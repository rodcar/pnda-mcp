from celery import group
from etl.tasks.extract_tasks import get_dataset_list, fetch_dataset
from etl.tasks.transform_tasks import process_dataset
from etl.tasks.load_tasks import index_datasets
from etl.tasks.pinecone_tasks import init_index
import time, json, os
from dotenv import load_dotenv
from etl.logger_config import get_logger

load_dotenv()

logger = get_logger(__name__)

RESULTS_DIR = 'etl/results'

def save_results(data, filename):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(f'{RESULTS_DIR}/{filename}', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    start_time = time.time()
    logger.info("Starting ETL pipeline")
    
    # Phase 1: Extraction
    logger.info("Phase 1: Starting data extraction")
    package_list = get_dataset_list.delay().get()
    extraction_results = group(fetch_dataset.s(pkg_id) for pkg_id in package_list)().get()
    save_results(extraction_results, 'responses_results.json')
    logger.info(f"Extraction completed: {len(extraction_results)} datasets fetched")
    
    # Load previous results for comparison before transformation
    try:
        with open(f'{RESULTS_DIR}/processing_results.json', 'r') as f:
            previous_datasets = json.load(f)
    except:
        previous_datasets = None
    
    # Phase 2: Transformation
    logger.info("Phase 2: Starting data transformation")
    transformation_results = [r for r in group(process_dataset.s(pkg) for pkg in extraction_results)().get() if r and "error" not in r]
    save_results(transformation_results, 'processing_results.json')
    logger.info(f"Transformation completed: {len(transformation_results)} datasets processed")
    
    # Phase 3: Load
    logger.info("Phase 3: Starting data loading")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    openai_config = {
        'embedding_model': os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small'),
    }
    
    pinecone_key = os.getenv('PINECONE_API_KEY')
    pinecone_config = {
        'index_name': os.getenv('PINECONE_INDEX_NAME', 'pnda-mcp-index'),
        'dimension': int(os.getenv('PINECONE_DIMENSION', '1536')),
        'metric': os.getenv('PINECONE_METRIC', 'cosine'),
        'cloud': os.getenv('PINECONE_CLOUD', 'aws'),
        'region': os.getenv('PINECONE_REGION', 'us-east-1'),    
    }
    
    try:
        # Check if index exists, if not, create it
        logger.info("Initializing Pinecone index")
        init_index.delay(pinecone_key, pinecone_config).get()
        
        task = index_datasets.delay(openai_key, openai_config, pinecone_key, pinecone_config, transformation_results, 100, previous_datasets)
        # Timeout is 30 minutes
        result = task.get(timeout=1800)
        end_time = time.time()
        logger.info(f'Successfully indexed {result["indexed"]}/{result["filtered"]} (total: {result["total"]}) packages in {end_time-start_time:.2f}s')
    except Exception as e:
        end_time = time.time()
        logger.error(f'ETL pipeline failed after {end_time-start_time:.2f}s: {e}')
        if 'task' in locals():
            try:
                logger.error(f'Task status: {task.status}')
                if task.status == 'FAILURE':
                    logger.error(f'Task info: {task.info}')
            except: pass
        return
                                
if __name__ == '__main__':
    main() 