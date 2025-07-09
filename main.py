from fastmcp import FastMCP
from pinecone import Pinecone
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import requests

PNDA_API_BASE_URL = "https://www.datosabiertos.gob.pe/api/3/action"

load_dotenv()

mcp = FastMCP("pnda-mcp")

# Initialize Pinecone and OpenAI
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("pnda-mcp-index")
client = OpenAI()

# Simple cache
cache = {}

@mcp.tool()
def dataset_search(query: str, top_k: int = 10) -> dict:
    """
    Search for relevant content (datasets) from the PNDA (Plataforma Nacional de Datos Abiertos) Peru.
    
    Find information from Peru's national open data platform (datosabiertos.gob.pe) that 
    semantically matches your search terms. Use this when you need to discover content 
    related to a topic, concept, or question. The search understands meaning and context, 
    not just exact word matches.
    
    Args:
        query (str): What you want to search for - can be keywords, phrases, or questions.
        top_k (int, optional): How many results to return. Defaults to 10, max 25.
    
    Returns:
        dict: Search results containing:
             - "query": Your original search query
             - "results": List of matching items with their ID, relevance score, and dataset name
    """
    top_k = min(top_k, 25)
    embedding = client.embeddings.create(input=query, model="text-embedding-3-small").data[0].embedding
    results = index.query(top_k=top_k, vector=embedding, include_metadata=True, include_values=False)
    
    # Cache results
    for match in results["matches"]:
        cache[match["id"]] = match["metadata"]
    
    return {"query": query, "results": [{"id": match["id"], "score": match["score"], "text": match["metadata"]["text"]} for match in results["matches"]]}

@mcp.tool()
def dataset_details(id: str) -> dict:
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
    
    # Fallback to PNDA
    try:
        result = requests.get(f"{PNDA_API_BASE_URL}/package_show?id={id}").json().get("result", {})
        return {"id": id, "text": result.get("title", "").strip(), "resources": result.get("resources", [])}
    except: pass

    # Secondary fallback to Pinecone
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

@mcp.prompt()
def question_generation(topic: str) -> str:
    return f"""Topic: {topic}
    Follow these steps to complete the task:
    1. Based on the topic, search for datasets in the PNDA (Plataforma Nacional de Datos Abiertos) Peru.
    2. If no relevant datasets are found, retry the search with a different query.
    3. Based on the search results, get the detailed information of one or more datasets.
    4. Create a temporary jupyter notebook to explore the datasets (Only focus on that objective not others). In particular, explore the data dictionary of the datasets to get the data columns and their descriptions. If it fails to open the data dictionary, skip this step and explore the data headers directly.
    5. Only continue after you explore the datasets.
    6. Think hard based on your exploration, generate a list of 5 questions that would be possible to answer with the datasets and columns and it is related to the topic. Justify using the data columns why it would be possible to answer the question (do this for each question).
    7. You questions should be based on the datasets and the topic. Do not make up questions.
    8. Show the questions in a list format do not add extra text or comments.
    9. Delete the temporary jupyter notebook.
    """

@mcp.prompt()
def analysis_quick(question: str) -> str:
    return f"""Provide a quick analysis of the following question: {question}
    Rules:
    - Do not include or generate synthetic data. All conclusions should be grounded in the data.
    - Minimal code implementation but you can use Markdwon cells for each section for comments.
    Objective: Provide a quick analysis of the question but still with a high quality.
    Use emoticons appropiately to make the analysis more engaging.
    Follow these steps to complete the task:
    1. Based on the question, search for datasets in the PNDA (Plataforma Nacional de Datos Abiertos) Peru that help you answer the question.
    2. If no relevant datasets are found, retry the search with a different query.
    3. Based on the search results, get the detailed information of one or more datasets.
    4. Think hard how to answer the question using the dataset or datasets.
    5. Create a jupyter notebook, start with the following structure: title, description, imports, code cells.
    6. Start with the installations.
    7. Explore the data dictionary of the datasets to get the data columns and their descriptions. If it fails to open the data dictionary, skip this step.
    8. If not data dictionary is available or not possible to open, explore the dataset to get the data columns.
    9. Think hard how to answer the question using the dataset or datasets taking into account the data dictionary.
    10. The code should be in python. Implement the code to answer the question using the datasets in the code cell. You can create temporal cells to explore the data, but you should delete them at the end.
    11. You could include a graph, and a brief analysis.
    11. Run the code cell to answer the question. Check for error, if error then fix, and execute again the same cell, do until the whole notebook runs correctly and the answer is addressed.
    12. Refine the notebook to make simple sections but high-quality. Title, description, imports, main code cell, graphs, answer.
    """

# Execute the notebook. Check for error, if error then fix, and execute again, do until the whole notebook runs correctly
# Claude Sonnet 4 is the best model for this task.
# GPT 4.1 produces more straight forward answers.
@mcp.prompt()
def analysis_full(question: str) -> str:
    return f"""Provide a full analysis of the following question: {question}
    Rules:
    - Do not include or generate synthetic data. All conclusions should be grounded in the data.
    Use emoticons appropiately to make the analysis more engaging.
    Follow these steps to complete the task:
    1. Based on the question, search for datasets in the PNDA (Plataforma Nacional de Datos Abiertos) Peru that help you answer the question.
    2. If no relevant datasets are found, retry the search with a different query.
    3. Based on the search results, get the detailed information of one or more datasets.
    4. Think hard how to answer the question using the dataset or datasets.
    5. Create a jupyter notebook with the code to answer the question using the datasets. The implementation should be in python. The notebook should be in a way that is easy to understand and follow.
    6. After the notebook is created, execute it. Check for error, if error then fix, and execute again, do until the whole notebook runs correctly.
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)