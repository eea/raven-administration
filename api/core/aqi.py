
# AQI legend: index, description, color
aqi_legend = [
    {"index": 1, "description": "Good", "color": "#007687"},
    {"index": 2, "description": "Fair", "color": "#009344"},
    {"index": 3, "description": "Moderate", "color": "#554f00"},
    {"index": 4, "description": "Poor", "color": "#ff4040"},
    {"index": 5, "description": "Very poor", "color": "#ff9999"},
    {"index": 6, "description": "Extremely poor", "color": "#e1a6ff"}
]

aqi_ranges = [
    {
        "pollutant_uri": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001",
        "pollutant": "PM2.5",
        "ranges": [
            dict(**aqi_legend[0], from_=0, to=5),
            dict(**aqi_legend[1], from_=6, to=15),
            dict(**aqi_legend[2], from_=16, to=50),
            dict(**aqi_legend[3], from_=51, to=90),
            dict(**aqi_legend[4], from_=91, to=140),
            dict(**aqi_legend[5], from_=141, to=999999)
        ]
    },
    {
        "pollutant_uri": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5",
        "pollutant": "PM10",
        "ranges": [
            dict(**aqi_legend[0], from_=0, to=15),
            dict(**aqi_legend[1], from_=16, to=45),
            dict(**aqi_legend[2], from_=46, to=120),
            dict(**aqi_legend[3], from_=121, to=195),
            dict(**aqi_legend[4], from_=196, to=270),
            dict(**aqi_legend[5], from_=271, to=999999)
        ]
    },
    {
        "pollutant_uri": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7",
        "pollutant": "O3",
        "ranges": [
            dict(**aqi_legend[0], from_=0, to=60),
            dict(**aqi_legend[1], from_=61, to=100),
            dict(**aqi_legend[2], from_=101, to=120),
            dict(**aqi_legend[3], from_=121, to=160),
            dict(**aqi_legend[4], from_=161, to=180),
            dict(**aqi_legend[5], from_=181, to=999999)
        ]
    },
    {
        "pollutant_uri": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8",
        "pollutant": "NO2",
        "ranges": [
            dict(**aqi_legend[0], from_=0, to=10),
            dict(**aqi_legend[1], from_=11, to=25),
            dict(**aqi_legend[2], from_=26, to=60),
            dict(**aqi_legend[3], from_=61, to=100),
            dict(**aqi_legend[4], from_=101, to=150),
            dict(**aqi_legend[5], from_=151, to=999999)
        ]
    },
    {
        "pollutant_uri": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1",
        "pollutant": "SO2",
        "ranges": [
            dict(**aqi_legend[0], from_=0, to=20),
            dict(**aqi_legend[1], from_=21, to=40),
            dict(**aqi_legend[2], from_=41, to=125),
            dict(**aqi_legend[3], from_=126, to=190),
            dict(**aqi_legend[4], from_=191, to=275),
            dict(**aqi_legend[5], from_=276, to=999999)
        ]
    }
]


def get_pollutant_uris():
    """Return a list of all pollutant_uris in aqi_ranges."""
    return [item["pollutant_uri"] for item in aqi_ranges]


def get_aqi(pollutant, value, timestep="Hour"):
    default_value = {"index": 0, "description": "No data", "color": "#cccccc"}
    if timestep != "Hour":
        return default_value

    rounded_value = int(round(value))
    for item in aqi_ranges:
        if item["pollutant"].lower() == pollutant.lower():
            for r in item["ranges"]:
                if r["from_"] <= rounded_value <= r["to"]:
                    return {"index": r["index"], "description": r["description"], "color": r["color"]}
    return default_value


def map_aqi_ranges_to_flat(pollutant: str = None):
    """
    Map aqi_ranges to a flat list of dicts with pollutant, meantype, aqi, range_from, range_to, meantype_name.
    meantype and meantype_name are hardcoded to 1 and 'Hour'.
    If pollutant is provided, only include entries for that pollutant (case-insensitive).
    Results are ordered by index for each pollutant.
    """
    result = []
    for item in aqi_ranges:
        if pollutant and item["pollutant"].lower() != pollutant.lower():
            continue
        # Sort the ranges by index before adding
        sorted_ranges = sorted(item["ranges"], key=lambda x: x["index"])
        for r in sorted_ranges:
            result.append({
                "pollutant": item["pollutant"],
                "meantype": 1,
                "aqi": r["index"],
                "description": r["description"],
                "color": r["color"],
                "range_from": r["from_"],
                "range_to": r["to"],
                "meantype_name": "Hour"
            })
    return result


def get_aqi_legend():
    """
    Returns the AQI legend as a list of dictionaries with index, description, and color.
    """
    return aqi_legend
