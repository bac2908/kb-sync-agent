import json
import os
import time
import hashlib
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from dotenv import load_dotenv
from google import genai


MARKDOWN_DIR = Path("data/markdown")
STATE_DIR = Path("data/state")
GEMINI_UPLOAD_MANIFEST_PATH = STATE_DIR / "gemini_upload_manifest.json"

FILE_SEARCH_STORE_DISPLAY_NAME = "kb-sync-agent-knowledge-base"
DEFAULT_EMBEDDING_MODEL = "models/gemini-embedding-2"


def load_upload_manifest() -> Dict:
    if not GEMINI_UPLOAD_MANIFEST_PATH.exists():
        return {}

    return json.loads(GEMINI_UPLOAD_MANIFEST_PATH.read_text(encoding="utf-8"))


def save_upload_manifest(manifest: Dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    GEMINI_UPLOAD_MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_markdown_files() -> List[Path]:
    files = sorted(MARKDOWN_DIR.glob("*.md"))
    if not files:
        raise FileNotFoundError(
            f"No Markdown files found in {MARKDOWN_DIR}. Run scraper first."
        )
    return files


def estimate_chunks(text: str, chunk_size: int = 512, overlap: int = 100) -> int:
    words = text.split()
    if not words:
        return 0

    if len(words) <= chunk_size:
        return 1

    step = max(chunk_size - overlap, 1)
    return 1 + max(0, (len(words) - chunk_size + step - 1) // step)


def calculate_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_api_key() -> str:
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("API_KEY")
    )
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Create one at https://aistudio.google.com/apikey "
            "and set GEMINI_API_KEY or API_KEY."
        )
    return api_key


def create_client() -> genai.Client:
    return genai.Client(api_key=get_api_key())


def create_file_search_store_if_needed(
    client: genai.Client,
    current_store_name: Optional[str],
    upload_manifest: Optional[Dict] = None,
) -> str:
    if current_store_name:
        print(f"Using existing Gemini file search store: {current_store_name}")
        return current_store_name

    manifest_store_name = (upload_manifest or {}).get("_file_search_store_name")
    if manifest_store_name:
        print(f"Using Gemini file search store from manifest: {manifest_store_name}")
        return manifest_store_name

    embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    file_search_store = client.file_search_stores.create(
        config={
            "display_name": FILE_SEARCH_STORE_DISPLAY_NAME,
            "embedding_model": embedding_model,
        }
    )
    print(f"Created Gemini file search store: {file_search_store.name}")
    return file_search_store.name


def wait_for_operation(client: genai.Client, operation, timeout_seconds: int = 300):
    start = time.time()

    while not operation.done:
        if time.time() - start > timeout_seconds:
            raise TimeoutError(f"Timed out waiting for Gemini operation: {operation.name}")

        print(f"Waiting for Gemini indexing operation: {operation.name}")
        time.sleep(5)
        operation = client.operations.get(operation)

    return operation


def upload_file_to_file_search_store(
    client: genai.Client,
    file_search_store_name: str,
    file_path: Path,
):
    operation = client.file_search_stores.upload_to_file_search_store(
        file=str(file_path),
        file_search_store_name=file_search_store_name,
        config={
            "display_name": file_path.name,
            "chunking_config": {
                "white_space_config": {
                    "max_tokens_per_chunk": 512,
                    "max_overlap_tokens": 100,
                }
            },
        },
    )

    return wait_for_operation(client, operation)


def upload_markdown_files_to_gemini(
    files_to_upload: Optional[Iterable[Path]] = None,
    file_hashes: Optional[Dict[str, str]] = None,
) -> Dict:
    load_dotenv()

    all_markdown_files = get_markdown_files()
    if files_to_upload is None:
        markdown_files = all_markdown_files
    else:
        markdown_files = [Path(file_path) for file_path in files_to_upload]

    upload_manifest = load_upload_manifest()

    if not markdown_files:
        print("No Markdown delta files to upload to Gemini.")
        return {
            "file_search_store_name": upload_manifest.get("_file_search_store_name", ""),
            "files_found": len(all_markdown_files),
            "files_considered": 0,
            "uploaded_files": 0,
            "skipped_files": 0,
            "estimated_chunks": 0,
        }

    file_search_store_name = os.getenv("GEMINI_FILE_SEARCH_STORE_NAME", "").strip()
    client = create_client()

    file_search_store_name = create_file_search_store_if_needed(
        client,
        file_search_store_name,
        upload_manifest,
    )

    uploaded_count = 0
    skipped_count = 0
    total_estimated_chunks = 0

    for file_path in markdown_files:
        content = file_path.read_text(encoding="utf-8")
        estimated_chunks = estimate_chunks(content)
        total_estimated_chunks += estimated_chunks

        file_key = str(file_path)
        content_hash = (file_hashes or {}).get(file_key, calculate_hash(content))
        manifest_item = upload_manifest.get(file_key)
        if manifest_item and manifest_item.get("hash") == content_hash:
            print(f"Skipped already uploaded to Gemini: {file_path.name}")
            skipped_count += 1
            continue

        if manifest_item and files_to_upload is None and "hash" not in manifest_item:
            print(f"Skipped already uploaded to Gemini: {file_path.name}")
            skipped_count += 1
            continue

        operation = upload_file_to_file_search_store(
            client=client,
            file_search_store_name=file_search_store_name,
            file_path=file_path,
        )

        upload_manifest[file_key] = {
            "file_name": file_path.name,
            "operation_name": operation.name,
            "estimated_chunks": estimated_chunks,
            "hash": content_hash,
        }
        uploaded_count += 1
        print(f"Uploaded to Gemini File Search: {file_path.name}")

    upload_manifest["_file_search_store_name"] = file_search_store_name
    save_upload_manifest(upload_manifest)

    print()
    print("Gemini upload completed.")
    print(f"File search store: {file_search_store_name}")
    print(f"Markdown files found: {len(all_markdown_files)}")
    print(f"Markdown delta files considered: {len(markdown_files)}")
    print(f"Uploaded files: {uploaded_count}")
    print(f"Skipped files: {skipped_count}")
    print(f"Estimated chunks embedded: {total_estimated_chunks}")
    print(f"Gemini upload manifest: {GEMINI_UPLOAD_MANIFEST_PATH}")

    return {
        "file_search_store_name": file_search_store_name,
        "files_found": len(all_markdown_files),
        "files_considered": len(markdown_files),
        "uploaded_files": uploaded_count,
        "skipped_files": skipped_count,
        "estimated_chunks": total_estimated_chunks,
    }


if __name__ == "__main__":
    upload_markdown_files_to_gemini()
