import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key (use environment variable in production)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")

    # SQLite database inside project folder
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, "app.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI API Key from environment
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
