# Chunk Upload System – Usage Documentation

## Overview

A civilized method to upload absurdly large files without crying when the connection drops at 99%. Files are sliced, shipped, reassembled, and reborn as a complete ZIP like nothing ever happened.

---

## Components

* **server.py** → Receives chunks, tracks them, merges when complete
* **chunk_uploader.py** → Cuts file into chunks and uploads with resume capability

---

## Folder Behavior

```
uploaded_chunks/   → Temporary chunk storage (messy kitchen)
final_files/       → Final merged file (clean dining table)
```

---

## Step 1: Start Server

```
python server.py
```

Server runs on:

```
http://localhost:5000
```

If it crashes, it’s not emotional. It’s your fault.

---

## Step 2: Configure File Upload

Edit inside `chunk_uploader.py`:

```
upload_file_with_resume(r"YOUR_FILE_PATH")
```

Example:

```
upload_file_with_resume(r"I:\big_file.zip")
```

---

## Step 3: Run Uploader

```
python chunk_uploader.py
```

What happens:

1. File is split into chunks
2. Each chunk is uploaded
3. If interrupted → resumes from missing chunks
4. Server merges automatically when all chunks arrive

---

## Step 4: Monitor Output

Terminal shows:

```
[Chunk X] 45.32% | 12.44 MB/s | ETA: 3.21 min | {'status': 'chunk_received'}
```

Interpretation:

* Progress → how far you’ve gone in life
* Speed → how good your internet is
* ETA → how long you must suffer
* Status → server acknowledgment

---

## Step 5: Final Output

After last chunk:

```
final_files/<original_filename>
```

Example:

```
final_files/big_file.zip
```

File is fully reconstructed and identical to original.

No magic. Just deterministic suffering.

---

## Resume Logic

Uploader asks server:

```
/missing_chunks?file_id=<file_name>
```

Server responds:

* `[0, 3, 5]` → upload only these chunks
* `"unknown"` → upload everything

This prevents:

* Restarting uploads
* Wasting bandwidth
* Rage quitting

---

## Manual Merge (Emergency Button)

If auto-merge fails:

```
POST /merge_file
{
    "file_id": "your_file.zip"
}
```

Server forcibly merges chunks like a tired manager fixing interns’ work.

---

## Constraints

* File name = unique identifier
* Changing file name = new upload
* Server memory resets = tracking gone
* Disk storage = your responsibility

---

## Common Failures

| Problem                       | Cause                                 |
| ----------------------------- | ------------------------------------- |
| Upload restarts from 0%       | Server restarted                      |
| Missing chunks always unknown | total_chunks not sent                 |
| Corrupted file                | chunk order mismatch or missing chunk |
| Slow speed                    | reality                               |

---

## Optimization Knobs

Inside uploader:

```
CHUNK_SIZE_IN_BYTES = 100 * 1024 * 1024
```

Adjust:

* Larger → faster, riskier
* Smaller → slower, safer

---

## Final State

You now have:

* Resume-capable uploader
* Fault-tolerant chunk handling
* Automatic reconstruction

And zero excuses for failed uploads.
