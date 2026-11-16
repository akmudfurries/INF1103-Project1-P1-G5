# AI Inventory & Procurement Advisor

## 1. Project Overview

The AI Inventory & Procurement Advisor is a Python-based application that helps users manage inventory, assess stock conditions and generate procurement recommendations.

It combines Google Gemini AI for qualitative inventory assessment with deterministic Python business logic for procurement calculations. Users retain control over procurement decisions through an approval workflow.

### Key Features

- Inventory record management (add, view and remove).
- AI-powered inventory assessment using Google Gemini.
- Automated stock analysis and procurement recommendations.
- Procurement approval, rejection and defer workflow.
- Procurement history and audit tracking.
- What-if procurement simulation.
- SQLite database persistence.
- JSON-to-SQLite data migration.

## 2. System Requirements

- Python 3.11
- Docker Desktop (optional, for containerised execution).
- Google Gemini API key.

## 3. Installation and Configuration

### 3.1 Clone the Repository

git clone https://github.com/akmudfurries/INF1103-Project1-P1-G5.git
cd INF1103-Project1-P1-G5

### 3.2 Configure Gemini API Key

The application requires a valid Google Gemini API key.

Windows PowerShell:

$env:GEMINI_API_KEY="your-api-key"

To save the key permanently for future terminal sessions:

setx GEMINI_API_KEY "your-api-key"

Open a new terminal after using `setx`.

Linux / macOS Bash:

export GEMINI_API_KEY="your-api-key"

Do not commit or share your API key.

## 4. Running Locally

### 4.1 Install Dependencies

python -m pip install -r requirements.txt

### 4.2 Launch the Application

python main.py

## 5. Running with Docker

Docker provides a containerised environment for running the application.

### 5.1 Build the Docker Image

Run this command from the project root:

docker build -t ai-inventory-advisor .

Rebuild the image whenever application code or the Dockerfile changes.

### 5.2 Launch the Container

Windows PowerShell:

docker run --rm -it -e GEMINI_API_KEY -v inventory-data:/app/data ai-inventory-advisor

Linux / macOS Bash:

docker run --rm -it -e GEMINI_API_KEY -v inventory-data:/app/data ai-inventory-advisor

The named Docker volume `inventory-data` stores the SQLite database outside the container.

This allows inventory and procurement records to persist between container executions.

Use the same volume name when restarting the application. Do not remove the volume if you want to retain its data.

## 6. Database and Data Migration

### 6.1 SQLite Persistence

The application uses SQLite to store inventory records, procurement decisions and procurement history.

The database is stored under the application's `data/` directory.

When using Docker, `/app/data` is mounted to the persistent `inventory-data` volume.

### 6.2 JSON-to-SQLite Migration

To import existing JSON records into SQLite, execute:

python migrate_json_to_sqlite.py

The migration script imports inventory and procurement records while preserving existing identifiers and procurement statuses.

The migration is designed to be idempotent, preventing duplicate records when executed repeatedly.

Migration is only required when importing existing JSON data. It is not required during normal application startup.

## 7. Running Automated Tests

The project uses pytest for automated testing.

Run the complete test suite:

python -m pytest -v

The tests cover:

- AI assessment and error handling.
- Application controller workflows.
- Inventory and procurement data management.
- User input and CLI display functions.
- Procurement calculations and safety stock.
- What-if simulation logic.

## 8. Project Dependencies

Dependencies are listed in `requirements.txt`.

| Package | Purpose |

| `google-genai`    | Google Gemini API integration |
| `pytest`          | Automated testing             |
| `tzdata`          | Timezone database support     |

Install all dependencies using:

python -m pip install -r requirements.txt

## 9. Important Notes

- A valid Gemini API key is required for AI-powered assessment and simulation.
- Keep API keys private. Never commit them to the repository.
- SQLite database files and runtime data are not required to be committed.
- Preserve the Docker volume to retain database records between container executions.
- Install dependencies before running the application locally.