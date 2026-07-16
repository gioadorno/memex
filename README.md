# fde-intel 🧠

**The Obsidian Vault Synthesizer & Local Vector DB**

## Overview
Forward Deployed Engineers are constantly in meetings, gathering chaotic requirements. `fde-intel` is a background daemon that turns a messy folder of Markdown notes (like an Obsidian vault) into a queryable, self-organizing "second brain."

## Features
*   **Directory Watching:** Automatically detects new or modified `.md` files in real-time.
*   **Local Vector Embeddings:** Uses ChromaDB to index every paragraph of your notes locally.
*   **Auto-Synthesis (RAG):** When a new note is added, it queries past notes and uses Vertex AI to generate an "Executive Summary & Action Items" block, safely prepending it to the file.
*   **Semantic Search:** Allows you to query your vault via CLI (e.g., "What did the client say about API rate limits last month?").

## Usage
```bash
# Run the watcher daemon in the background
python watcher.py --dir ~/fde-notes

# Query the vault
python query.py "What were the blockers for the authentication pipeline?"
```

## FDE Philosophy
**Never lose context.** Maintaining absolute clarity on shifting client requirements across hundreds of meetings is what separates top FDEs from standard engineers. Let the machine do the synthesis.
