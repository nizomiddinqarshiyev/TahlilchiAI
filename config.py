from dotenv import load_dotenv
import os


load_dotenv()

DB_URL = os.getenv("DB_URL")
SECRET = os.getenv("SECRET")
DB_USER = os.getenv("DB_USER")
DB_PORT = os.getenv("DB_PORT")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

STATIC_URL = os.getenv("STATIC_URL")
STATIC_ROOT = os.getenv("STATIC_ROOT")

MEDIA_URL = os.getenv("MEDIA_URL")
MEDIA_ROOT = os.getenv("MEDIA_ROOT")
DEBUG = os.getenv("DEBUG")
STAR_COST = os.getenv("STAR_COST")
TRAIN_COST = os.getenv("TRAIN_COST")
FORECAST_COST = os.getenv("FORECAST_COST")





