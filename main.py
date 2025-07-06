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
def search_data(query: str, top_k: int = 10) -> dict:
    """Search for similar content in the Pinecone index"""
    embedding = client.embeddings.create(input=query, model="text-embedding-3-small").data[0].embedding
    results = index.query(top_k=top_k, vector=embedding, include_metadata=True, include_values=False)
    
    # Cache results
    for match in results["matches"]:
        cache[match["id"]] = match["metadata"]
    
    return {"query": query, "results": [{"id": match["id"], "score": match["score"], "text": match["metadata"]["text"]} for match in results["matches"]]}

@mcp.tool()
def get_item_by_id(id: str) -> dict:
    """Get a specific item from Pinecone by ID"""
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
