-- Plugin registry table for Raven v4 plugin system.
-- Run once against the target database (ravendb4, raven-airquis, etc.)
CREATE TABLE IF NOT EXISTS plugin_registry (
    id               VARCHAR PRIMARY KEY,
    name             VARCHAR NOT NULL,
    version          VARCHAR,
    description      TEXT,
    enabled          BOOLEAN NOT NULL DEFAULT TRUE,
    config           JSONB NOT NULL DEFAULT '{}',
    restart_required BOOLEAN NOT NULL DEFAULT FALSE,
    installed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
