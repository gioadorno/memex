# Build Plan: fde-intel

## Step 1: Directory Watcher
*   Implement `watchdog` in Python to monitor a specified directory for file creation and modification events.

## Step 2: Local Vector Database (ChromaDB)
*   Integrate `chromadb`.
*   Build a text splitter to chunk Markdown files effectively (e.g., by headers or paragraphs).
*   Generate embeddings and store them locally.

## Step 3: Retrieval-Augmented Generation (RAG)
*   When a new file is detected, use the file's content as a query against ChromaDB to find related past notes.
*   Pass the new note + retrieved context to Vertex AI (Gemini) to generate an actionable summary.

## Step 4: File Injection
*   Safely write the generated "Executive Summary" block to the top of the modified Markdown file without overwriting the original content.
