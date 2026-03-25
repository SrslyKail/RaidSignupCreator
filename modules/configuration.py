import os
from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path
from dotenv import load_dotenv
from typing import ClassVar
from dataclasses import dataclass


# Read-only dataclass that contains the required config :)
@dataclass(frozen=True)
class Config:
    API_KEY: str
    SERVER_ID: str
    CHANNEL_ID: str
    DISCORD_ID: str
    WEEKLY: bool


class ConfigFactory:
    REQUIRED_ENV_VARIABLES: ClassVar[list[str]] = [
        "API_KEY",
        "SERVER_ID",
        "CHANNEL_ID",
        "DISCORD_ID",
    ]

    def __init__(self) -> None:

        self.namespace = Namespace()
        self.__validateEnvVariables()
        self.__load_configuration()

    def __createConfig(self) -> Config:
        return Config(
            API_KEY=os.environ["API_KEY"],
            SERVER_ID=os.environ["SERVER_ID"],
            CHANNEL_ID=os.environ["CHANNEL_ID"],
            DISCORD_ID=os.environ["DISCORD_ID"],
            WEEKLY=self.namespace.weekly,
        )

    @classmethod
    def createConfig(cls) -> Config:
        return cls().__createConfig()

    def __load_configuration(self) -> None:
        """Loads the required environment variables from a .env file and checks that they loaded correctly.

        Raises:
            Exception: If the .env file is not located
            Exception: If a environment variable is missing
        """

        parser: ArgumentParser = self.__setup_parser()
        parser.parse_args(namespace=self.namespace)

        return

    def __setup_parser(self) -> ArgumentParser:
        parser: ArgumentParser = ArgumentParser()
        parser.add_argument(
            "-w",
            "--weekly",
            help="If you want to post all the raids for a single week at once",
            action=BooleanOptionalAction,
            dest="weekly",
            default=False,
        )

        return parser

    @classmethod
    def __validateEnvVariables(cls):
        missing_vars: list[str] = []

        # Get the current directory
        current_dir = Path(__file__).parent
        # Check the .env file exists
        if Path(current_dir / ".." / ".env").exists is False:
            raise Exception(
                f"Missing .env file. Check for a .env file at {current_dir}"
            )

        # If it does, load the file
        load_dotenv()

        # Check the variables were loaded
        missing_vars = [
            variable
            for variable in cls.REQUIRED_ENV_VARIABLES
            if os.getenv(variable) is None
        ]

        # if something is missing, raise an exception so the user can add it
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
