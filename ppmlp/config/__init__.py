import os
from dotenv import load_dotenv

ENV_FILE_PATH = os.environ.get("ENV_FILE_PATH", ".env")

if os.path.exists(ENV_FILE_PATH):
    load_dotenv(ENV_FILE_PATH)

APP_TITLE = os.environ.get("APP_TITLE", "Preprocess Server")
APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")
APP_ORIGINS = os.environ.get("APP_ORIGINS", "http://localhost:4200").split(",")
APP_CREDENTIALS = os.environ.get("APP_CREDENTIALS", "true").lower() == "true"   
APP_METHODS = os.environ.get("APP_METHODS", "*").split(",")
APP_HEADERS = os.environ.get("APP_HEADERS", "*").split(",")
APP_RAW_DATA_PATH = os.environ.get("APP_RAW_DATA_PATH", "/home/nacho/Programming/external/ppmlp/data")
APP_SINK_DATA_PATH = os.environ.get("APP_SINK_DATA_PATH", "/sink")