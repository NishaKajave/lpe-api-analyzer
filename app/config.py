import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./looplens.db")
AI_MODE = os.getenv("AI_MODE", "mock").lower()

MAX_RETRIES = min(max(int(os.getenv("MAX_RETRIES", "5")), 1), 5)
MIN_CONFIDENCE = int(os.getenv("MIN_CONFIDENCE", "80"))
MIN_VALIDATION_SCORE = int(os.getenv("MIN_VALIDATION_SCORE", "80"))
MAX_CONCURRENT_RECORDS = int(os.getenv("MAX_CONCURRENT_RECORDS", "3"))
RECORD_TIME_LIMIT_SECONDS = int(os.getenv("RECORD_TIME_LIMIT_SECONDS", "120"))

PROMPT_VERSION = "1.3"
VALIDATOR_VERSION = "1.2"
DEFAULT_MODEL_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT", "API-Analyzer-Production" if AI_MODE == "azure" else "Deterministic-Optimizer-Engine-v2")

# Token and cost metrics simulation
INPUT_TOKEN_COST_PER_1K = float(os.getenv("INPUT_TOKEN_COST_PER_1K", "0.0015"))
OUTPUT_TOKEN_COST_PER_1K = float(os.getenv("OUTPUT_TOKEN_COST_PER_1K", "0.0020"))
