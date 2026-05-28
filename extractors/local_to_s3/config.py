import os

# Absolute path to the local data folder
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

# Files to ingest: { local_filename: (source_partition, s3_file_name) }
FILES = {
    "meteo-weather.csv": ("meteo_weather", "meteo-weather"),
}

S3_BUCKET = "sentinel-kunle"
