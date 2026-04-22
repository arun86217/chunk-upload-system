import os
from flask import Flask, jsonify, request

app = Flask(__name__)

UPLOAD_DIRECTORY = "uploaded_chunks"
FINAL_DIRECTORY = "final_files"

os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(FINAL_DIRECTORY, exist_ok=True)

uploaded_chunks_tracker = {}
expected_chunks_tracker = {}


@app.route("/upload_chunk", methods=["POST"])
def upload_chunk():
    file_identifier = request.form["file_id"]
    chunk_index = int(request.form["chunk_index"])
    total_chunks = int(request.form.get("total_chunks", 0))
    chunk_file = request.files["chunk"]

    file_directory = os.path.join(UPLOAD_DIRECTORY, file_identifier)
    os.makedirs(file_directory, exist_ok=True)

    chunk_file_path = os.path.join(file_directory, f"chunk_{chunk_index}")
    chunk_file.save(chunk_file_path)

    if file_identifier not in uploaded_chunks_tracker:
        uploaded_chunks_tracker[file_identifier] = set()

    uploaded_chunks_tracker[file_identifier].add(chunk_index)

    if total_chunks > 0:
        expected_chunks_tracker[file_identifier] = total_chunks

    uploaded_count = len(uploaded_chunks_tracker[file_identifier])
    expected_count = expected_chunks_tracker.get(file_identifier)

    if expected_count is not None and uploaded_count == expected_count:
        final_file_path = merge_chunks(file_identifier)
        return jsonify({
            "status": "merged",
            "file_path": final_file_path
        })

    return jsonify({
        "status": "chunk_received",
        "chunk_index": chunk_index
    })


@app.route("/missing_chunks", methods=["GET"])
def missing_chunks():
    file_identifier = request.args.get("file_id")

    uploaded_chunks = uploaded_chunks_tracker.get(file_identifier, set())
    expected_total_chunks = expected_chunks_tracker.get(file_identifier)

    if expected_total_chunks is None:
        return jsonify({"missing_chunks": "unknown"})

    missing_chunks_list = [
        index for index in range(expected_total_chunks)
        if index not in uploaded_chunks
    ]

    return jsonify({"missing_chunks": missing_chunks_list})


def merge_chunks(file_identifier):
    file_directory = os.path.join(UPLOAD_DIRECTORY, file_identifier)
    output_file_path = os.path.join(FINAL_DIRECTORY, f"{file_identifier}")

    chunk_files = os.listdir(file_directory)

    chunk_files_sorted = sorted(
        chunk_files,
        key=lambda name: int(name.split("_")[1])
    )

    with open(output_file_path, "wb") as output_file:
        for chunk_file_name in chunk_files_sorted:
            chunk_file_path = os.path.join(file_directory, chunk_file_name)
            with open(chunk_file_path, "rb") as chunk_file:
                output_file.write(chunk_file.read())

    for chunk_file_name in chunk_files_sorted:
        os.remove(os.path.join(file_directory, chunk_file_name))

    os.rmdir(file_directory)

    return output_file_path


@app.route("/merge_file", methods=["POST"])
def merge_file():
    file_identifier = request.json.get("file_id")

    if file_identifier not in uploaded_chunks_tracker:
        return jsonify({"error": "no chunks uploaded"}), 404

    final_file_path = merge_chunks(file_identifier)

    return jsonify({
        "status": "file_merged_manual",
        "file_path": final_file_path
    })


if __name__ == "__main__":
    app.run(debug=True)