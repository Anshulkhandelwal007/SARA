-- Create import tracking table for incremental imports
-- This table tracks the last import time for each data source
-- to support incremental imports where only new/modified records are processed

CREATE TABLE IF NOT EXISTS import_tracking (
  id SERIAL PRIMARY KEY,
  source VARCHAR(100) NOT NULL UNIQUE,
  last_import_at TIMESTAMP NOT NULL,
  imported_count INTEGER NOT NULL DEFAULT 0,
  updated_count INTEGER NOT NULL DEFAULT 0,
  failed_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on source for faster lookups
CREATE INDEX IF NOT EXISTS idx_import_tracking_source ON import_tracking(source);

-- Create index on last_import_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_import_tracking_last_import_at ON import_tracking(last_import_at);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_import_tracking_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_import_tracking_updated_at
  BEFORE UPDATE ON import_tracking
  FOR EACH ROW
  EXECUTE FUNCTION update_import_tracking_updated_at();

-- Insert initial tracking entry for Google Sheets
INSERT INTO import_tracking (source, last_import_at, imported_count)
VALUES ('google_sheets', CURRENT_TIMESTAMP - INTERVAL '1 year', 0)
ON CONFLICT (source) DO NOTHING;

COMMENT ON TABLE import_tracking IS 'Tracks import history for incremental data imports from various sources';
COMMENT ON COLUMN import_tracking.source IS 'Data source identifier (e.g., google_sheets, api, manual)';
COMMENT ON COLUMN import_tracking.last_import_at IS 'Timestamp of the last successful import';
COMMENT ON COLUMN import_tracking.imported_count IS 'Number of records imported in the last run';
COMMENT ON COLUMN import_tracking.updated_count IS 'Number of records updated in the last run';
COMMENT ON COLUMN import_tracking.failed_count IS 'Number of records that failed in the last run';
