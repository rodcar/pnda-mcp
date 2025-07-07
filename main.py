from fastmcp import FastMCP
from pinecone import Pinecone
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("pnda-mcp")

# Initialize Pinecone and OpenAI
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("pnda-mcp-index")
client = OpenAI()

# Simple cache
cache = {}

@mcp.tool()
def search_datasets(query: str, top_k: int = 10) -> dict:
    """
    Search for relevant content (datasets) from the PNDA (Plataforma Nacional de Datos Abiertos) Peru.
    
    Find information from Peru's national open data platform (datosabiertos.gob.pe) that 
    semantically matches your search terms. Use this when you need to discover content 
    related to a topic, concept, or question. The search understands meaning and context, 
    not just exact word matches.
    
    Args:
        query (str): What you want to search for - can be keywords, phrases, or questions.
        top_k (int, optional): How many results to return. Defaults to 10.
    
    Returns:
        dict: Search results containing:
             - "query": Your original search query
             - "results": List of matching items with their ID, relevance score, and dataset name
    """
    embedding = client.embeddings.create(input=query, model="text-embedding-3-small").data[0].embedding
    results = index.query(top_k=top_k, vector=embedding, include_metadata=True, include_values=False)
    
    # Cache results
    for match in results["matches"]:
        cache[match["id"]] = match["metadata"]
    
    return {"query": query, "results": [{"id": match["id"], "score": match["score"], "text": match["metadata"]["text"]} for match in results["matches"]]}

@mcp.tool()
def get_dataset_by_id(id: str) -> dict:
    """
    Get detailed information about a specific dataset from the PNDA (Plataforma Nacional de Datos Abiertos) Peru.
    
    Use this when you have an dataset ID from search results and want to retrieve
    the full content and metadata for that specific dataset from Peru's national 
    open data platform (datosabiertos.gob.pe).
    
    Args:
        id (str): The unique ID of the dataset you want to retrieve.
    
    Returns:
        dict: Dataset details including:
             - "id": The dataset identifier
             - "text": The title of the dataset
             - "resources": List of resources (files) in the dataset, includes the file path, name, size, created, mimetype, format
             Returns error message if dataset not found.
    """
    # Check cache first
    if id in cache:
        metadata = cache[id]
        if metadata and "metadata" in metadata:
            try:
                parsed_metadata = json.loads(metadata["metadata"])
                return {"id": id, "text": metadata.get("text"), "resources": parsed_metadata}
            except:
                pass
        return {"id": id, "metadata": metadata, "text": metadata.get("text") if metadata else None}
    
    # Fallback to Pinecone
    result = index.fetch(ids=[id])
    if id in result.vectors:
        vector_data = result.vectors[id]
        metadata = vector_data.metadata
        cache[id] = metadata  # Cache for future use
        
        if metadata and "metadata" in metadata:
            try:
                parsed_metadata = json.loads(metadata["metadata"])
                return {"id": id, "text": metadata.get("text"), "resources": parsed_metadata}
            except:
                pass
        return {"id": id, "metadata": metadata, "text": metadata.get("text") if metadata else None}
    return {"error": f"Item with ID {id} not found"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
