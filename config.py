import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = "healthcare-secret-key-change-this"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR,
        "healthcare.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False