from .app import app
from pinecone import Pinecone, ServerlessSpec

@app.task
def init_index(api_key: str, config: dict):
    try:
        pc = Pinecone(api_key=api_key)
        if not pc.has_index(config["index_name"]):
            pc.create_index(
                name=config["index_name"],
                dimension=config["dimension"],
                metric=config["metric"],
                spec=ServerlessSpec(cloud=config["cloud"], region=config["region"])
            )
        return True
    except Exception as e:
        return {"error": str(e)}