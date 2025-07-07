from .app import app

@app.task
def process_dataset(dataset):
    """Process dataset data"""
    # In case of error, return the response, it will be saved on the results folder
    if "error" in dataset:
        return dataset
    
    try:
        data = dataset["response"]
        resource_keys_to_keep = ["id", "url", "name", "size", "created", "mimetype", "state", "format", "description"]

        # Check if dataset is active, if not, skip
        if data.get("state", "").lower() != "active": 
            return None
        
        # Keep only the keys that are in the resource_keys_to_keep list
        resources = [{key: resource.get(key, "") for key in resource_keys_to_keep} for resource in data.get("resources", [])]
        return {"id": dataset["id"], 
                "title": data.get("title", ""), 
                "resources": resources, 
                "metadata_modified": data.get("metadata_modified", "")}
    except Exception as e:
        return {"id": dataset["id"], "error": str(e)}