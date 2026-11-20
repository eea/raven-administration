-- Importing permission: lets a group import observations without the management permission
-- (which also allows editing stations, sampling points and other metadata).
-- Management still includes importing, so existing groups keep working unchanged.
ALTER TABLE "group" ADD COLUMN IF NOT EXISTS importing boolean NOT NULL DEFAULT false;
