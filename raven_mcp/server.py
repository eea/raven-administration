"""Read-only MCP server for Raven.

Served over Streamable HTTP behind Raven's nginx at /mcp. Every request carries the
user's Raven login, either as the headers X-Raven-Username / X-Raven-Password or as
HTTP Basic auth; the server signs in to the Raven API as that user, so the API's
network access and claims apply unchanged. Only GET routes and
POST routes that read are called; there is no tool that writes.

Environment:
    MCP_ENABLED    true to serve; anything else exits at start
    RAVEN_API_URL  the API as seen from this container, e.g. http://api:5000 (no trailing /api)
    MCP_PORT       port to listen on, default 8000
"""
import base64
import binascii
import hashlib
import os
import sys
from typing import Literal, Optional

import requests
from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

API_URL = os.environ.get("RAVEN_API_URL", "http://api:5000").rstrip("/")
PORT = int(os.environ.get("MCP_PORT", "8000"))

# ponytail: fixed cap so one call can't flood the model's context; narrow the query instead of raising it
MAX_ROWS = 500

READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True)

# Mirrors core.data.mean.MeanType in the API. Copied, not imported: this server only talks HTTP.
MEAN_TYPES = {
    "Original": 0, "Hour": 1, "Day": 2, "MovingEightHour": 3, "Year": 4, "MovingDay": 5,
    "MovingEightHourMax": 6, "Month": 7, "WinterYear": 8, "Aot40Vegetation": 9,
    "Aot40ForestProtection": 10, "WinterSeason": 11, "SummerYear": 12,
}

mcp = MCPServer("raven")

# Raven JWT per login, keyed by a hash of username:password so the password itself is never kept.
# ponytail: in-process dict, fine for one container; move to a shared cache if the service is ever scaled out
_tokens: dict[str, str] = {}


def _error_text(r: requests.Response) -> str:
    try:
        body = r.json()
        msg = body.get("msg") or body.get("message") or body.get("description") if isinstance(body, dict) else None
    except ValueError:
        msg = None
    return f"Raven API returned {r.status_code}: {msg or r.text[:300]}"


def _credentials(ctx: Context) -> tuple[str, str]:
    headers = ctx.headers or {}
    # Plain headers, so users can write their username and password into the client config as is.
    if headers.get("x-raven-username"):
        return headers["x-raven-username"], headers.get("x-raven-password", "")
    scheme, _, encoded = headers.get("authorization", "").partition(" ")
    if scheme.lower() != "basic" or not encoded:
        raise ToolError("Not signed in: configure this MCP server with the headers 'X-Raven-Username' and "
                        "'X-Raven-Password' (or an 'Authorization: Basic ...' header).")
    try:
        username, sep, password = base64.b64decode(encoded).decode("utf-8").partition(":")
    except (binascii.Error, UnicodeDecodeError):
        sep = ""
    if not sep or not username:
        raise ToolError("Malformed Basic auth header: expected base64 of 'username:password'.")
    return username, password


def _sign_in(username: str, password: str) -> str:
    try:
        r = requests.post(f"{API_URL}/api/auth/signin", json={"username": username, "password": password}, timeout=30)
    except requests.RequestException:
        raise ToolError("Cannot reach the Raven API.")
    if not r.ok:
        raise ToolError(f"Sign-in failed for user {username}: {_error_text(r)}")
    return r.json()["token"]


def _call(ctx: Context, method: str, path: str, params: dict = None, body: dict = None):
    username, password = _credentials(ctx)
    key = hashlib.sha256(f"{username}:{password}".encode()).hexdigest()
    for attempt in (1, 2):
        token = _tokens.get(key)
        if token is None:
            token = _tokens[key] = _sign_in(username, password)
        try:
            r = requests.request(method, f"{API_URL}{path}", params=params, json=body,
                                 headers={"Authorization": f"Bearer {token}"}, timeout=120)
        except requests.RequestException:
            raise ToolError("Cannot reach the Raven API.")
        # Tokens expire (1 h by default): sign in again once, then give up.
        if r.status_code == 401 and attempt == 1:
            _tokens.pop(key, None)
            continue
        if not r.ok:
            raise ToolError(_error_text(r))
        return r.json()


def _capped(rows: list) -> dict:
    return {"total": len(rows), "truncated": len(rows) > MAX_ROWS, "rows": rows[:MAX_ROWS]}


def _filter(rows: list, station: Optional[str], pollutant: Optional[str]) -> list:
    if station:
        rows = [r for r in rows if station.lower() in (r.get("station") or "").lower()]
    if pollutant:
        rows = [r for r in rows if (r.get("pollutant") or "").lower() == pollutant.lower()]
    return rows


@mcp.tool(annotations=READ_ONLY)
def list_series(ctx: Context, station: Optional[str] = None, pollutant: Optional[str] = None) -> dict:
    """List the measurement series (sampling points) you have access to, with station, pollutant,
    timestep, unit and the period covered. Use the returned sampling_point_id with get_measurements
    and get_observation_log.

    station: part of the station name, case-insensitive.
    pollutant: exact pollutant notation, e.g. NO2, PM10, O3.
    """
    return _capped(_filter(_call(ctx, "GET", "/api/data/historical/timeseries"), station, pollutant))


@mcp.tool(annotations=READ_ONLY)
def latest_values(ctx: Context, station: Optional[str] = None, pollutant: Optional[str] = None) -> dict:
    """Newest observation per series: value, unit, time, validity/verification flags,
    status (0 = updated in the last 3 hours, 1 = within 6 months, 2 = older) and AQI levels.

    station: part of the station name, case-insensitive.
    pollutant: exact pollutant notation, e.g. NO2, PM10, O3.
    """
    return _capped(_filter(_call(ctx, "GET", "/api/data/latest"), station, pollutant))


@mcp.tool(annotations=READ_ONLY)
def statistics_options(ctx: Context) -> dict:
    """Years with data, and for each pollutant the aggregation processes (statistics) available,
    with whether each applies to directive 2008/50 and 2024/2881. Call this before get_statistics."""
    return {
        "years": _call(ctx, "GET", "/api/data/statistics/years"),
        "pollutants": _call(ctx, "GET", "/api/data/statistics/pollutants_and_aggregationprocess"),
    }


@mcp.tool(annotations=READ_ONLY)
def get_statistics(ctx: Context, pollutant: str, aggregation_process: str, years: list[int]) -> dict:
    """Annual statistics per sampling point (e.g. annual mean, number of exceedance hours),
    as shown on Raven's Statistics page.

    pollutant: pollutant notation, e.g. NO2.
    aggregation_process: an aggregation process id from statistics_options.
    years: one or more years.
    """
    body = {"pollutant": pollutant, "aggregation_process": aggregation_process, "years": years}
    return _capped(_call(ctx, "POST", "/api/data/statistics/values", body=body))


Directive = Literal["2008/50", "2024/2881", "WHO"]


@mcp.tool(annotations=READ_ONLY)
def exceedance_options(ctx: Context, directive: Optional[Directive] = None) -> dict:
    """Directives, years with observations, and pollutants that have thresholds
    (optionally only those with a threshold in the given directive). Call this before
    evaluate_exceedances."""
    params = {"directive": directive} if directive else None
    return {
        "directives": _call(ctx, "GET", "/api/data/exceedances/directives"),
        "years": _call(ctx, "GET", "/api/data/exceedances/years"),
        "pollutants": _call(ctx, "GET", "/api/data/exceedances/pollutants", params=params),
    }


@mcp.tool(annotations=READ_ONLY)
def evaluate_exceedances(ctx: Context, year: int, pollutant: str, directive: Directive,
                         aggregation_process: Optional[str] = None, exceeded_only: bool = False) -> dict:
    """Compare each sampling point's statistics for a year with the directive's thresholds
    (limit values, target values, alert/information thresholds, ...). One row per sampling point
    and objective, with measured value, threshold, coverage and whether it was exceeded.

    pollutant: pollutant notation, e.g. NO2.
    aggregation_process: only evaluate this statistic, e.g. P1Y.
    exceeded_only: return only rows where the threshold was exceeded.
    """
    body = {"year": year, "pollutant": pollutant, "directive": directive}
    if aggregation_process:
        body["aggregation_process"] = aggregation_process
    rows = _call(ctx, "POST", "/api/data/exceedances/evaluate", body=body)
    if exceeded_only:
        rows = [r for r in rows if r.get("exceeded")]
    return _capped(rows)


@mcp.tool(annotations=READ_ONLY)
def list_zones(ctx: Context) -> dict:
    """Air quality zones: id, national code, name, area, type and category.
    Needs the management and all-networks permissions."""
    zones = _call(ctx, "GET", "/api/management/zones")
    # The zone polygons are large and useless to the model.
    return _capped([{k: v for k, v in z.items() if k != "geojson"} for z in zones])


@mcp.tool(annotations=READ_ONLY)
def list_assessment_regimes(ctx: Context, zone_id: str, pollutant: Optional[str] = None) -> dict:
    """Assessment regimes of a zone (which pollutant/objective is assessed and how).
    Use a regime id with evaluate_assessment_regime.

    zone_id: zone id from list_zones.
    pollutant: optional pollutant notation, e.g. NO2.
    """
    params = {"zone_id": zone_id}
    if pollutant:
        params["pollutant"] = pollutant
    return _capped(_call(ctx, "GET", "/api/data/exceedances/regimes", params=params))


@mcp.tool(annotations=READ_ONLY)
def evaluate_assessment_regime(ctx: Context, regime_id: str, year: int, directive: Directive) -> dict:
    """Evaluate one assessment regime for a year: whether the zone exceeds the objective,
    based on the regime's sampling points."""
    return _call(ctx, "POST", "/api/data/exceedances/evaluate/regime",
                 body={"regime_id": regime_id, "year": year, "directive": directive})


@mcp.tool(annotations=READ_ONLY)
def get_measurements(ctx: Context, sampling_point_ids: list[str], from_dt: str, to_dt: str,
                     mean_type: Literal[tuple(MEAN_TYPES)] = "Day", coverage: int = 75) -> dict:
    """Measured values for one or more series over a period, aggregated to mean_type.
    Prefer Day, Month or Year for long periods; Hour or Original returns many rows.

    sampling_point_ids: ids from list_series.
    from_dt, to_dt: ISO date/time, e.g. 2025-01-01 or 2025-01-01T00:00:00.
    coverage: minimum data coverage in percent for an aggregated value.
    """
    body = {"sampling_point_ids": sampling_point_ids, "from_dt": from_dt, "to_dt": to_dt,
            "meantype": MEAN_TYPES[mean_type], "coverage": coverage}
    return _capped(_call(ctx, "POST", "/api/data/historical", body=body))


@mcp.tool(annotations=READ_ONLY)
def get_observation_log(ctx: Context, sampling_point_id: str, from_dt: Optional[str] = None, to_dt: Optional[str] = None,
                        limit: int = 100) -> dict:
    """Change history of a series' observations (who changed values or validity/verification
    flags, when, and from what to what), newest first. Needs the quality control permission.

    from_dt, to_dt: optional period, both or neither, e.g. 2025-01-01.
    limit: up to 500 rows.
    """
    params = {"sampling_point_id": sampling_point_id, "limit": max(1, min(limit, MAX_ROWS))}
    if from_dt and to_dt:
        params.update(from_dt=from_dt, to_dt=to_dt)
    result = _call(ctx, "GET", "/api/qualitycontrol/log", params=params)
    return {"rows": result["rows"], "has_more": result["has_more"]}


if __name__ == "__main__":
    if os.environ.get("MCP_ENABLED", "false").strip().lower() not in ("true", "1", "yes", "on"):
        print("MCP server is disabled (set MCP_ENABLED=true in .env to enable it). Exiting.", file=sys.stderr)
        sys.exit(0)
    # Stateless JSON: no sessions to lose on restart, and every request is self-contained.
    # DNS-rebinding protection is off because nginx in front decides which Host reaches us.
    mcp.run("streamable-http", host="0.0.0.0", port=PORT, stateless_http=True, json_response=True,
            transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False))
