# Chunk Upload System (a.k.a. Stop Re-uploading 50GB Like a Maniac)

## Overview
This project implements a chunk-based file upload system with resume capability.
Translation: if your upload dies at 99%, you fix the missing piece instead of restarting your life choices.

## Problem Statement
Uploading large files (e.g., 50GB) over unstable networks results in:
- Upload failures at the worst possible moment
- Full restart requirements (junior-level suffering)
- Wasted bandwidth, time, and dignity

## Solution
Split the file into smaller chunks.
Upload them individually.
Track what is uploaded.
Resume only what is missing.

## Architecture

### Client (Uploader)
- Splits file into fixed-size chunks
- Generates hash for each chunk
- Uploads chunks individually
- Queries server for missing chunks
- Retries only failed chunks

### Server (API)
- Receives chunks
- Stores them reliably
- Tracks uploaded chunk indexes
- Returns missing chunks on request

## Setup Instructions

### Clone Repository
git clone https://github.com/arun86217/chunk-upload-system.git

### Install Dependencies
pip install flask requests

### Run Server
python server.py

### Run Uploader
python chunk_uploader.py

## Philosophy
If your system restarts a 50GB upload because 5MB failed,
you didn’t build a system.
You built a punishment mechanism.
