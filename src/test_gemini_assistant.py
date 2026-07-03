import json
import os
import sys

from dotenv import load_dotenv
from google import genai

from src.config import GEMINI_UPLOAD_MANIFEST_PATH, SYSTEM_PROMPT


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


def get_file_search_store_name() -> str:
    store_name = os.getenv("GEMINI_FILE_SEARCH_STORE_NAME", "").strip()
    if store_name:
        return store_name

    if GEMINI_UPLOAD_MANIFEST_PATH.exists():
        manifest = json.loads(GEMINI_UPLOAD_MANIFEST_PATH.read_text(encoding="utf-8"))
        store_name = manifest.get("_file_search_store_name", "")
        if store_name:
            return store_name

    raise ValueError(
        "GEMINI_FILE_SEARCH_STORE_NAME is missing. Run src/gemini_uploader.py first."
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    load_dotenv()

    client = genai.Client(api_key=get_api_key())
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    file_search_store_name = get_file_search_store_name()

    question = "How do I add a YouTube video?"
    prompt = f"""{SYSTEM_PROMPT}

Question:
{question}
"""

    interaction = client.interactions.create(
        model=model,
        input=prompt,
        tools=[
            {
                "type": "file_search",
                "file_search_store_names": [file_search_store_name],
            }
        ],
    )

    print()
    print("Question:")
    print(question)
    print()
    print("Assistant answer:")
    cited_files = []

    for step in interaction.steps:
        if step.type != "model_output":
            continue

        for content_block in step.content:
            if content_block.type != "text":
                continue

            print(content_block.text)

            annotations = getattr(content_block, "annotations", None)
            if annotations:
                for annotation in annotations:
                    if getattr(annotation, "type", "") == "file_citation":
                        file_name = annotation.file_name
                        if file_name not in cited_files:
                            cited_files.append(file_name)

    if cited_files:
        print()
        print("Gemini file citations:")
        for file_name in cited_files[:3]:
            print(f"- {file_name}")


if __name__ == "__main__":
    main()
