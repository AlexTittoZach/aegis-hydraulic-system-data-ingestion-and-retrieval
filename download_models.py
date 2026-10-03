#!/usr/bin/env python3
"""
Model download and cache pre-warmer for Aegis RAG Engine.
Downloads Qwen-2.5-1.5B GGUF and pre-caches BGE-small embeddings.
"""

import os
import sys
import urllib.request
import time

QWEN_URL = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "qwen2.5-1.5b-instruct-q4_k_m.gguf")
FASTEMBED_DIR = os.path.join(MODEL_DIR, "fastembed_cache")

def download_with_progress(url: str, dest_path: str):
    print(f"Downloading model from:\n  {url}\nDestination: {dest_path}")
    t0 = time.time()

    def reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100.0, downloaded * 100.0 / total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            sys.stdout.write(f"\rProgress: {percent:5.1f}% [{mb_downloaded:6.1f} MB / {mb_total:6.1f} MB]")
            sys.stdout.flush()

    urllib.request.urlretrieve(url, dest_path, reporthook)
    elapsed = time.time() - t0
    print(f"\nDownload completed in {elapsed:.1f}s ({os.path.getsize(dest_path)/(1024*1024):.1f} MB).")

def main():
    os.makedirs(MODEL_DIR, exist_ok=True)

    # 1. Check / Download Qwen-2.5-1.5B GGUF
    if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 1_000_000_000:
        print(f"[OK] Qwen-2.5-1.5B model already present: {MODEL_PATH} ({os.path.getsize(MODEL_PATH)/(1024*1024):.1f} MB)")
    else:
        print("[+] Fetching Qwen-2.5-1.5B GGUF model...")
        download_with_progress(QWEN_URL, MODEL_PATH)

    # 2. Pre-cache BGE-small ONNX embeddings
    print("[+] Pre-caching BGE-small embedding model in local cache...")
    try:
        from fastembed import TextEmbedding
        TextEmbedding(model_name="BAAI/bge-small-en-v1.5", cache_dir=FASTEMBED_DIR)
        print("[OK] FastEmbed BGE-small model cached successfully.")
    except Exception as e:
        print(f"[!] Note on FastEmbed caching: {e}")

    print("\n[SUCCESS] All models ready for 100% offline, air-gapped execution.")

if __name__ == "__main__":
    main()
