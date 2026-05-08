import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
# It's standard to use .env, but api.env works as long as it's in .gitignore
load_dotenv("api.env")

# =========================
#  API Keys (Secure)
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("[WARNING] GROQ_API_KEY not found. Ensure it is set in api.env")

# =========================
#  Model Configuration
# =========================
LLM_MODEL = "llama-3.3-70b-versatile"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# =========================
#  Data Configuration
# =========================
# Using Path ensures this works across different Operating Systems
BASE_DIR = Path(__file__).resolve().parent
PRODUCTS_FILE = BASE_DIR / "products.json"

def get_catalog_info():
    """
    Load product catalog and return (total_count, dataset)
    """
    if PRODUCTS_FILE.exists():
        try:
            with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return len(data), data
        except (json.JSONDecodeError, Exception) as e:
            print(f"[ERROR] Failed to load {PRODUCTS_FILE.name}: {e}")
    
    return 0, []

# =========================
#  Runtime Catalog Stats
# =========================
TOTAL_LAPTOPS, ALL_PRODUCTS = get_catalog_info()

# =========================
# RAG / System Settings
# =========================
# Default to 5 if catalog is empty, otherwise show all
TOP_K_RESULTS = TOTAL_LAPTOPS if TOTAL_LAPTOPS > 0 else 5
SCRAPE_DELAY = 3
MAX_PRODUCTS = 50