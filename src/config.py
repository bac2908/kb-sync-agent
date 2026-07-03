from pathlib import Path


BASE_API_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
ARTICLE_API_URL_TEMPLATE = (
    "https://support.optisigns.com/api/v2/help_center/en-us/articles/{article_id}.json"
)
PINNED_ARTICLE_IDS = [
    "360051014713",  # How to use YouTube with OptiSigns
]

DATA_DIR = Path("data")
MARKDOWN_DIR = DATA_DIR / "markdown"
STATE_DIR = DATA_DIR / "state"
ARTICLES_MANIFEST_PATH = STATE_DIR / "articles_manifest.json"
GEMINI_UPLOAD_MANIFEST_PATH = STATE_DIR / "gemini_upload_manifest.json"
SCREENSHOTS_DIR = Path("docs") / "screenshots"

GEMINI_FILE_SEARCH_STORE_DISPLAY_NAME = "kb-sync-agent-knowledge-base"
GEMINI_DEFAULT_EMBEDDING_MODEL = "models/gemini-embedding-2"
GEMINI_CHUNK_SIZE = 512
GEMINI_CHUNK_OVERLAP = 100

SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.
- Tone: helpful, factual, concise.
- Only answer using the uploaded docs.
- Max 5 bullet points; else link to the doc.
- Cite up to 3 "Article URL:" lines per reply.
"""
