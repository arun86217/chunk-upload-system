import hashlib  # for hashing chunks (trust issues remain valid)
import os  # for file operations
import time  # for measuring time (finally some awareness)

import requests  # for HTTP calls

CHUNK_SIZE_IN_BYTES = 500 * 1024 * 1024  # 5MB chunks (chatty but precise)


def generate_chunk_hash(chunk_data):
    sha256_hash_object = hashlib.sha256()  # create hash object
    sha256_hash_object.update(chunk_data)  # feed data
    return sha256_hash_object.hexdigest()  # return fingerprint


def upload_single_chunk(file_identifier, chunk_index, chunk_data):

    upload_api_endpoint = "http://localhost:5000/upload_chunk"  # server endpoint

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

    uploaded_bytes = 0  # track total uploaded
    start_time = time.time()  # start stopwatch

    with open(file_path, "rb") as file_object:

        for current_chunk_index in range(total_chunks):

            # read chunk regardless (keeps file pointer aligned, unlike previous bug)
            chunk_data = file_object.read(CHUNK_SIZE_IN_BYTES)

            if current_chunk_index not in missing_chunk_indexes:
                uploaded_bytes += len(
                    chunk_data
                )  # count skipped chunks as already uploaded
                continue

            response = upload_single_chunk(
                file_identifier, current_chunk_index, chunk_data
            )

            uploaded_bytes += len(chunk_data)  # update progress

            # time calculations
            elapsed_time = time.time() - start_time

            upload_speed = (
                uploaded_bytes / elapsed_time if elapsed_time > 0 else 0
            )  # bytes/sec

            remaining_bytes = total_file_size - uploaded_bytes

            eta_seconds = remaining_bytes / upload_speed if upload_speed > 0 else 0

            # human readable
            speed_mb_per_sec = upload_speed / (1024 * 1024)
            eta_minutes = eta_seconds / 60
            progress_percent = (uploaded_bytes / total_file_size) * 100

            print(
                f"[Chunk {current_chunk_index}] "
                f"Progress: {progress_percent:.2f}% | "
                f"Speed: {speed_mb_per_sec:.2f} MB/s | "
                f"ETA: {eta_minutes:.2f} min | "
                f"Response: {response}"
            )


if __name__ == "__main__":

    upload_file_with_resume(r"I:\Adobe Photoshop Masterclass From Beginner to Pro.zip")
