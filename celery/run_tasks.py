from celery import chord
from app import get_package_list, fetch_package_raw, process_package_raw, collect_results, index_packages
import time
import json
import os

def save_results(data, filename):
    """Save results to file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"💾 Results saved to {filepath}")

if __name__ == "__main__":
    print("🚀 Starting PNDA processing...")
    
    # Phase 1: Fetch raw data in parallel
    print("📦 Phase 1: Fetching raw package data...")
    package_list = get_package_list.delay().get()
    print(f"Found {len(package_list)} packages")
    
    start_time = time.time()
    raw_job = chord(fetch_package_raw.s(pkg_id) for pkg_id in package_list)(collect_results.s())
    raw_results = raw_job.get()
    
    save_results(raw_results, 'responses_results.json')
    phase1_time = time.time() - start_time
    print(f"⏱️  Phase 1 completed in {phase1_time:.2f}s")
    
    # Phase 2: Process raw data in parallel
    print("⚡ Phase 2: Processing raw data...")
    start_time = time.time()
    
    processed_job = chord(process_package_raw.s(pkg) for pkg in raw_results['packages'])(collect_results.s())
    final_results = processed_job.get()
    
    save_results(final_results, 'processing_results.json')
    phase2_time = time.time() - start_time
    
    # Phase 3: Index to Pinecone
    print("🔍 Phase 3: Indexing to Pinecone...")
    start_time = time.time()
    
    # Index to Pinecone
    index_result = index_packages.delay(final_results['packages'], 100).get()
    phase3_time = time.time() - start_time
    print(f"⏱️  Phase 3 completed in {phase3_time:.2f}s - Indexed {index_result['indexed']} packages")
    
    # Summary
    total_time = phase1_time + phase2_time + phase3_time
    avg_time = total_time / len(package_list) if package_list else 0
    
    print("✅ Processing complete!")
    print(f"📊 Total packages: {final_results['total']}")
    print(f"⏱️  Total time: {total_time:.2f}s | Avg per item: {avg_time:.3f}s")
    print("\n🔍 Sample results:")
    for i, package in enumerate(final_results['packages'][:5]):
        status = "❌" if 'error' in package else "✅"
        content = package.get('error', package.get('title', ''))
        print(f"  {status} {package['id']}: {content}")
    
    if len(final_results['packages']) > 5:
        print(f"  ... and {len(final_results['packages']) - 5} more packages")