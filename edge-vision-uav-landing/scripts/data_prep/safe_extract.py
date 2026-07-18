import os
import zipfile
import sys

def safe_extract(zip_path, extract_dir):
    print(f"Extracting {zip_path} to {extract_dir}...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.infolist():
            # Prevent path traversal
            if member.filename.startswith('/') or '..' in member.filename:
                print(f"[ERROR] Path traversal detected: {member.filename}")
                sys.exit(1)
            zf.extract(member, extract_dir)
    print("Extraction complete.")

if __name__ == "__main__":
    zip_path = sys.argv[1]
    extract_dir = sys.argv[2]
    safe_extract(zip_path, extract_dir)
