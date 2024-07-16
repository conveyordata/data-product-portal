import os

from dotenv import load_dotenv


def add_additional_env_vars():  # improve naming
    load_dotenv(os.path.join(".env"))  # improve
