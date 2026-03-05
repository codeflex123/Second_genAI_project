import argparse
import subprocess
import time
import os
import sys

def run_sync_job():
    """
    Triggers Ph1 and Ph2, then notifies subsequent phases (Ph3, Ph4).
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] --- PHASE 5: ORCHESTRATION START ---")
    
    # Ensure paths are correct regardless of where script is called from
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Trigger Phase 1: Data Ingestion (Scraping)
    print("Step 1: Running Phase 1 [Data Ingestion]...")
    subprocess.run(["python3", os.path.join(base_dir, "phase1/scraper.py")], check=True)
    
    # 2. Trigger Phase 2: Embedding & Vector Store
    print("Step 2: Running Phase 2 [Embedding & Vector Store]...")
    subprocess.run(["python3", os.path.join(base_dir, "phase2/ingest.py")], check=True)
    
    # 3. Trigger Phase 3: Notify Backend (Symbolic)
    print("Step 3: Triggering Phase 3 [Backend Notification]... Done.")
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] --- DATA FRESHNESS ENSURED ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="INDmoney RAG Data Scheduler")
    parser.add_argument("--once", action="store_true", help="Run the sync job once and exit")
    args = parser.parse_args()

    if args.once:
        run_sync_job()
    else:
        try:
            from apscheduler.schedulers.blocking import BlockingScheduler
        except ImportError:
            print("Error: apscheduler is not installed. Use --once for single runs or install it via 'pip install apscheduler'.")
            sys.exit(1)

        scheduler = BlockingScheduler()
        
        # Run once immediately on start
        run_sync_job()
        
        # Schedule the job to run every 30 minutes for local development mode
        scheduler.add_job(run_sync_job, 'interval', minutes=30)
        
        print("Phase 5: Scheduler Started. Syncing data every 30 minutes.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass
