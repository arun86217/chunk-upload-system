import os

from flask import Flask, jsonify, request

app = Flask(__name__)


UPLOAD_DIRECTORY = "uploaded_chunks"


os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


uploaded_chunks_tracker = {}


@app.route("/upload_chunk", methods=["POST"])
def upload_chunk():

    file_id = request.form["file_id"]
    chunk_index = int(request.form["chunk_index"])

    chunk_file = request.files["chunk"]

    file_directory = os.path.join(UPLOAD_DIRECTORY, file_id)
    os.makedirs(file_directory, exist_ok=True)

    chunk_file_path = os.path.join(file_directory, f"chunk_{chunk_index}")

    chunk_file.save(chunk_file_path)

    if file_id not in uploaded_chunks_tracker:
        uploaded_chunks_tracker[file_id] = set()

    uploaded_chunks_tracker[file_id].add(chunk_index)

    return jsonify({"status": "chunk_received", "chunk_index": chunk_index})


@app.route("/missing_chunks", methods=["GET"])
def missing_chunks():

    file_id = request.args.get("file_id")

    expected_total_chunks = 1000

    uploaded_chunks = uploaded_chunks_tracker.get(file_id, set())

    missing_chunks_list = [
        chunk_index
        for chunk_index in range(expected_total_chunks)
        if chunk_index not in uploaded_chunks
    ]

    return jsonify({"missing_chunks": missing_chunks_list})


if __name__ == "__main__":
    app.run(debug=True)
