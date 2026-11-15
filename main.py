# Application entry point for the AI Inventory & Procurement Advisor

import os

from ai_manager import AIManager
from ai_provider import GeminiAIProvider
from application_controller import ApplicationController
from data_manager import DataManager
from database_repo import DatabaseRepository
from io_manager import IOManager
from logic_manager import LogicManager


DATABASE_PATH = os.path.join("data", "inventory.db")


def main():
    # Construct application dependencies and start the CLI

    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    repository = DatabaseRepository(DATABASE_PATH)

    try:
        # Initialise SQLite before starting the application.
        repository.initialize()

        # Construct the managers and their dependencies.
        data_manager = DataManager(repository)

        ai_provider = GeminiAIProvider()
        ai_manager = AIManager(ai_provider)

        logic_manager = LogicManager()
        io_manager = IOManager()

        # Inject dependencies into the application controller.
        controller = ApplicationController(
            io_manager=io_manager,
            ai_manager=ai_manager,
            logic_manager=logic_manager,
            data_manager=data_manager,
        )

        controller.run()

    finally:
        # Close the database connection when the application exits.
        repository.close()


if __name__ == "__main__":
    main()
