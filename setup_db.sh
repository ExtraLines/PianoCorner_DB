#!/bin/bash

# Strict Mode
set -euo pipefail

# Configuration
DB_NAME="PianoCorner.db"
DUCKDB_BIN="./duckdb"
DATA_DIR="data"

echo "--- Starting Database Build: $DB_NAME ---"

if [[ ! -x "$DUCKDB_BIN" ]]; then
    echo "Error: $DUCKDB_BIN not found or not executable." >&2
    exit 1
fi

if [[ ! -d "$DATA_DIR" ]]; then
    echo "Error: Data directory '$DATA_DIR' missing." >&2
    exit 1
fi

# Clean up existing DB safely
rm -f "$DB_NAME"

echo "Creating schema and importing data..."

# Execute via Heredoc
$DUCKDB_BIN "$DB_NAME" <<EOF
BEGIN;

CREATE TABLE songs (song_id UUID, original_name VARCHAR, english_name VARCHAR, release_date DATE, duration INTERVAL, genre VARCHAR, youtube_link VARCHAR, progress TINYINT);
COPY songs FROM '$DATA_DIR/Piano Corner - Songs.csv' (HEADER);

CREATE TABLE artists (artist_id UUID, original_name VARCHAR, english_name VARCHAR, type VARCHAR);
COPY artists FROM '$DATA_DIR/Piano Corner - Artists.csv' (HEADER);

CREATE TABLE sources (source_id UUID, original_title VARCHAR, english_title VARCHAR, type VARCHAR, release_date DATE, creator VARCHAR);
COPY sources FROM '$DATA_DIR/Piano Corner - Sources.csv' (HEADER);

CREATE TABLE song_to_artist (song_id UUID, artist_id UUID, role VARCHAR, is_primary BOOLEAN);
COPY song_to_artist FROM '$DATA_DIR/Piano Corner - Song to Artist.csv' (HEADER);

CREATE TABLE song_to_source (song_id UUID, source_id UUID, relation VARCHAR);
COPY song_to_source FROM '$DATA_DIR/Piano Corner - Song to Source.csv' (HEADER);

COMMIT;
EOF

echo "Database build complete: $DB_NAME"