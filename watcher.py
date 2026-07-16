import argparse
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import chromadb
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

def parse_args():
    parser = argparse.ArgumentParser(description="🧠 memex: The Obsidian Vault Synthesizer")
    parser.add_argument("--dir", type=str, required=True, help="Directory to watch and index")
    parser.add_argument("--model", type=str, default=None, help="Vertex AI model name (Default: env VERTEX_MODEL_NAME or gemini-3.1-pro-preview)")
    return parser.parse_args()

class MarkdownHandler(FileSystemEventHandler):
    def __init__(self, collection, model):
        self.collection = collection
        self.model = model
        self.processing = set()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            # Debounce to prevent infinite loops if we modify the file ourselves
            if event.src_path in self.processing:
                return
                
            print(f"📝 Detected modification: {event.src_path}")
            self.process_file(event.src_path)

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            print(f"📄 Detected new file: {event.src_path}")
            self.process_file(event.src_path)

    def process_file(self, filepath):
        self.processing.add(filepath)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Skip if we already synthesized this
            if "### 🤖 FDE Executive Summary" in content:
                print("Skipping - already synthesized.")
                return

            print("🔍 Generating embeddings and searching vault context...")
            
            # Upsert into ChromaDB
            file_id = os.path.basename(filepath)
            self.collection.upsert(
                documents=[content],
                metadatas=[{"source": filepath}],
                ids=[file_id]
            )
            
            # Retrieve past context (simulated RAG)
            results = self.collection.query(
                query_texts=[content],
                n_results=3
            )
            
            context = ""
            if results and results['documents']:
                for doc in results['documents'][0]:
                    if doc != content: # Don't include itself
                        context += doc[:500] + "...\n---\n"

            print("🧠 Asking Gemini to synthesize...")
            prompt = f"""
            You are an FDE Executive Assistant. Synthesize this new meeting note into a concise Executive Summary and Action Items.
            
            NEW NOTE:
            {content}
            
            PAST VAULT CONTEXT:
            {context}
            
            Return ONLY the markdown block starting with "### 🤖 FDE Executive Summary". Do not use code blocks (```).
            """
            
            response = self.model.generate_content(prompt, generation_config=GenerationConfig(temperature=0.2))
            summary = response.text.strip()
            
            # Write back to file
            new_content = f"{summary}\n\n---\n\n{content}"
            with open(filepath, 'w') as f:
                f.write(new_content)
                
            print("✅ Synthesis injected successfully!")
            
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
        finally:
            # Short sleep to let filesystem settle before removing from debounce set
            time.sleep(2)
            self.processing.remove(filepath)


def main():
    args = parse_args()
    watch_dir = os.path.abspath(args.dir)
    
    if not os.path.exists(watch_dir):
        print(f"Error: Directory {watch_dir} does not exist.")
        sys.exit(1)

    print("Initializing ChromaDB...")
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="fde_vault")

    print("Initializing Vertex AI Gemini...")
    project = os.environ.get("GOOGLE_VERTEX_PROJECT", "extreme-karma-gm")
    vertexai.init(project=project, location="global")
    
    selected_model = args.model or os.environ.get("VERTEX_MODEL_NAME", "gemini-3.1-pro-preview")
    model = GenerativeModel(selected_model)

    event_handler = MarkdownHandler(collection, model)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=True)
    
    print(f"👀 Watching directory: {watch_dir}")
    print("Press Ctrl+C to stop.")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
