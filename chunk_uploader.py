import hashlib
import os
import time
import requests

CHUNK_SIZE_IN_BYTES = 500 * 1024 * 1024


def generate_chunk_hash(chunk_data):
    sha256_hash_object = hashlib.sha256()
    sha256_hash_object.update(chunk_data)
    return sha256_hash_object.hexdigest()


def upload_single_chunk(file_identifier, chunk_index, chunk_data, total_chunks):
    upload_api_endpoint = "http://localhost:5000/upload_chunk"

    payload_data = {
        "file_id": file_identifier,
        "chunk_index": chunk_index,
        "total_chunks": total_chunks,
        "chunk_hash": generate_chunk_hash(chunk_data),
    }

    files_data = {
        "chunk": ("chunk", chunk_data)
    }

    response = requests.post(upload_api_endpoint, data=payload_data, files=files_data)
    return response.json()


def get_missing_chunks(file_identifier):
    status_api_endpoint = f"http://localhost:5000/missing_chunks?file_id={file_identifier}"
    response = requests.get(status_api_endpoint)
    return response.json().get("missing_chunks", [])


def upload_file_with_resume(file_path):
    file_identifier = os.path.basename(file_path)
    total_file_size = os.path.getsize(file_path)
    total_chunks = (total_file_size + CHUNK_SIZE_IN_BYTES - 1) // CHUNK_SIZE_IN_BYTES

    missing_chunk_indexes = get_missing_chunks(file_identifier)

    if isinstance(missing_chunk_indexes, str):
        missing_chunk_indexes = list(range(total_chunks))

    uploaded_bytes = 0
    start_time = time.time()

    with open(file_path, "rb") as file_object:
        for current_chunk_index in range(total_chunks):
            chunk_data = file_object.read(CHUNK_SIZE_IN_BYTES)

            if current_chunk_index not in missing_chunk_indexes:
                uploaded_bytes += len(chunk_data)
                continue

            response = upload_single_chunk(
                file_identifier,
                current_chunk_index,
                chunk_data,
                total_chunks
            )

            uploaded_bytes += len(chunk_data)

            elapsed_time = time.time() - start_time
            upload_speed = uploaded_bytes / elapsed_time if elapsed_time > 0 else 0
            remaining_bytes = total_file_size - uploaded_bytes
            eta_seconds = remaining_bytes / upload_speed if upload_speed > 0 else 0

            print(
                f"[Chunk {current_chunk_index}] "
                f"{(uploaded_bytes / total_file_size) * 100:.2f}% | "
                f"{upload_speed / (1024 * 1024):.2f} MB/s | "
                f"ETA: {eta_seconds / 60:.2f} min | "
                f"{response}"
            )


if __name__ == "__main__":
    upload_file_with_resume(
        r"I:\Adobe Photoshop Masterclass From Beginner to Pro.zip"
    )