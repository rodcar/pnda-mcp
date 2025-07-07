from .app import app
import requests

PNDA_API_BASE_URL = "https://datosabiertos.gob.pe/api/3/action"

@app.task
def get_dataset_list():
    """Fetch the list of all datasets"""
    # Packages are datasets
    response = requests.get(f"{PNDA_API_BASE_URL}/package_list")
    return response.json()["result"][:3]

@app.task
def fetch_dataset(dataset_name):
    """Fetch dataset data"""
    try:
        response = requests.get(f"{PNDA_API_BASE_URL}/package_show?id={dataset_name}")
        result = response.json()["result"][0]
        # Use the id from the result
        return {"id": result["id"], "response": result}
    except Exception as e:
        return {"id": dataset_name, "error": str(e)}