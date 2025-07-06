from celery import Celery, chord
import requests
from tqdm import tqdm
import json
import hashlib
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

app = Celery(
    'pnda_processor',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

app.conf.update(
    worker_concurrency=14,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

PNDA_API_BASE_URL = "https://datosabiertos.gob.pe/api/3/action"

@app.task
def get_package_list():
    """Fetch the list of all packages"""
    response = requests.get(f"{PNDA_API_BASE_URL}/package_list")
    return response.json()["result"][:10]

@app.task
def fetch_package_raw(package_id):
    """Fetch raw package data"""
    try:
        response = requests.get(f"{PNDA_API_BASE_URL}/package_show?id={package_id}")
        return {"id": package_id, "raw_data": response.json()["result"]}
    except Exception as e:
        return {"id": package_id, "error": str(e)}

@app.task
def process_package_raw(raw_package):
    """Process raw package data"""
    if "error" in raw_package:
        return raw_package
    
    try:
        data = raw_package["raw_data"]
        # Handle both dict and list cases
        data = data if isinstance(data, dict) else (data[0] if data else {})
        resources = [{k: r.get(k, "") for k in ["id", "url", "name", "size", "created", "mimetype", "state", "format", "description"]} 
                    for r in data.get("resources", [])]
        return {"id": raw_package["id"], "title": data.get("title", "") if isinstance(data, dict) else "", "resources": resources}
    except Exception as e:
        return {"id": raw_package["id"], "error": str(e)}

@app.task
def index_packages(packages, batch_size=100):
    """Index package titles and resources to Pinecone"""
    
    # Initialize Pinecone inside the task
    from pinecone import Pinecone
    import os
    
    load_dotenv()  # Load environment variables in worker context
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("pnda-mcp-index")
    
    for i in tqdm(range(0, len(packages), batch_size)):
        i_end = min(i + batch_size, len(packages))
        batch = packages[i:i_end]
        
        ids = [hashlib.md5(pkg["id"].encode()).hexdigest() for pkg in batch]
        texts = [pkg["title"].replace("\n", " ") for pkg in batch]
        metadatas = [{"text": pkg["title"], "metadata": json.dumps(pkg["resources"])} for pkg in batch]
        
        embeddings = [emb.embedding for emb in client.embeddings.create(input=texts, model="text-embedding-3-small").data]
        records = zip(ids, embeddings, metadatas)
        index.upsert(vectors=records)
    
    return {"indexed": len(packages)}

@app.task
def collect_results(results):
    """Collect all results"""
    return {"total": len(results), "packages": results}