-- Migration: add plugin_permissions JSONB column to group table
-- This is a generic extension point allowing installed plugins to store per-group
-- permission flags without requiring changes to the core eea-raven codebase.
-- Each plugin declares its own keys, e.g. {"adacs": true, "my-plugin": true}

ALTER TABLE "group"
    ADD COLUMN IF NOT EXISTS plugin_permissions JSONB NOT NULL DEFAULT '{}';
