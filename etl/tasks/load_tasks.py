from .app import app
import json
from openai import OpenAI
from tqdm import tqdm
from pinecone import Pinecone

@app.task(bind=True)
def index_datasets(self, openai_api_key, openai_config, pinecone_api_key, pinecone_config_dict, datasets, batch_size=100, previous_datasets=None):
    """Index dataset titles and resources to Pinecone"""
    try:
        # Validate API keys
        if not openai_api_key:
            raise ValueError("OpenAI API key is missing")
        if not pinecone_api_key:
            raise ValueError("Pinecone API key is missing")
        
        # Filter datasets with updated metadata_modified
        total_datasets = len(datasets)
        if previous_datasets:
            prev_metadata = {d["id"]: d.get("metadata_modified") for d in previous_datasets}
            datasets = [d for d in datasets if d["id"] not in prev_metadata or prev_metadata.get(d["id"]) != d.get("metadata_modified")]
        
        if not datasets:
            return {"total": total_datasets, "filtered": 0, "indexed": 0}
        
        openai_client = OpenAI(api_key=openai_api_key)
        embedding_model = openai_config["embedding_model"]

        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(pinecone_config_dict["index_name"])
        
        indexed_count = 0
        for i in tqdm(range(0, len(datasets), batch_size)):
            i_end = min(i + batch_size, len(datasets))
            batch = datasets[i:i_end]
            
            ids = [dataset["id"] for dataset in batch]
            texts = [dataset.get("title", dataset["id"]).replace("\n", " ") for dataset in batch]
            metadatas = [{"text": dataset.get("title", dataset["id"]), "metadata": json.dumps(dataset.get("resources", []))} for dataset in batch]
            
            try:
                embeddings = [emb.embedding for emb in openai_client.embeddings.create(input=texts, model=embedding_model).data]
                records = list(zip(ids, embeddings, metadatas))
                index.upsert(vectors=records)
                indexed_count += len(batch)
            except Exception as e:
                continue
        
        return {"total": total_datasets, "filtered": len(datasets), "indexed": indexed_count}
        
    except Exception as e:
        # Update task state with proper exception info
        self.update_state(state='FAILURE', meta={'error': str(e), 'exc_type': type(e).__name__})
        raise