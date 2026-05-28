import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

FILES = {
    "meteo-weather.csv": ("meteo_weather", "meteo-weather"),
}

S3_BUCKET = "sentinel-kunle"
