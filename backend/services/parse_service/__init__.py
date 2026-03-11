from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")
