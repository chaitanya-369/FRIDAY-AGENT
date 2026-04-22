import sys
import os
import requests
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RAGFLOW_API_URL = os.environ.get("RAGFLOW_API_URL", "http://localhost:9380/v1")
RAGFLOW_API_KEY = os.environ.get("RAGFLOW_API_KEY")


def ingest_directory(dir_path: str, glob_pattern: str = "**/*.md"):
    if not RAGFLOW_API_KEY:
        print("[Antigravity] RAGFLOW_API_KEY not found in .env. Skipping ingestion.")
        return

    search_path = os.path.join(dir_path, glob_pattern)
    files_to_ingest = glob.glob(search_path, recursive=True)

    if not files_to_ingest:
        print(f"[Antigravity] No files found matching {search_path}")
        return

    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}",
    }

    # Note: This uses standard multipart form uploading,
    # specific Ragflow endpoint syntax may vary based on exact setup.
    endpoint = f"{RAGFLOW_API_URL}/document/upload"

    print(
        f"[Antigravity] Found {len(files_to_ingest)} files. Beginning ingestion into Ragflow..."
    )
    for file_path in files_to_ingest:
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                response = requests.post(endpoint, headers=headers, files=files)

            if response.status_code == 200:
                print(f"[Antigravity] ✓ Ingested: {file_path}")
            else:
                print(
                    f"[Antigravity] ✗ Failed: {file_path} - Status {response.status_code}"
                )

        except Exception as e:
            print(f"[Antigravity] Error reading or uploading {file_path}: {e}")


if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "Project Idea And Details"

    # Ensure relative paths resolve from project root
    if not os.path.isabs(target_dir):
        project_root = os.path.dirname(os.path.dirname(__file__))
        target_dir = os.path.join(project_root, target_dir)

    ingest_directory(target_dir)
