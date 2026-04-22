import hashlib
import os

import requests

CHUNK_SIZE_IN_BYTES = 5 * 1024 * 1024


def generate_chunk_hash(chunk_data):
    sha256_hash_object = hashlib.sha256()
    sha256_hash_object.update(chunk_data)
    return sha256_hash_object.hexdigest()


def upload_single_chunk(file_identifier, chunk_index, chunk_data):

    upload_api_endpoint = "http://localhost:5000/upload_chunk"

    payload_data = {
        "file_id": file_identifier,
        "chunk_index": chunk_index,
        "chunk_hash": generate_chunk_hash(chunk_data),
    }

    files_data = {"chunk": chunk_data}

    response = requests.post(upload_api_endpoint, data=payload_data, files=files_data)

    return response.json()


def get_missing_chunks(file_identifier):

    status_api_endpoint = (
        f"http://localhost:5000/missing_chunks?file_id={file_identifier}"
    )

    response = requests.get(status_api_endpoint)

    return response.json().get("missing_chunks", [])


def upload_file_with_resume(file_path):

    file_identifier = os.path.basename(file_path)

    total_file_size = os.path.getsize(file_path)

    total_chunks = (total_file_size // CHUNK_SIZE_IN_BYTES) + 1

    missing_chunk_indexes = get_missing_chunks(file_identifier)

    with open(file_path, "rb") as file_object:

        for current_chunk_index in range(total_chunks):

            if current_chunk_index not in missing_chunk_indexes:
                continue

            chunk_data = file_object.read(CHUNK_SIZE_IN_BYTES)

            response = upload_single_chunk(
                file_identifier, current_chunk_index, chunk_data
            )

            print(f"Chunk {current_chunk_index} upload response:", response)


if __name__ == "__main__":

    upload_file_with_resume("large_file.zip")
