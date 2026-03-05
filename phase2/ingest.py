import json
import os
import chromadb

def ingest_to_vector_db(json_path):
    print("Phase 2: Starting Vector DB Ingestion...")
    
    # Load scraped data
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return
        
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Initialize ChromaDB in phase2 folder (Isolated Architecture)
    path = os.path.join(os.getcwd(), "phase2", "chroma_db")
    client = chromadb.PersistentClient(path=path)
    collection = client.get_or_create_collection("fund_data")

    for url, fund in data.items():
        # Cleanly stringify FAQs for indexing
        faqs = fund.get('faqs', [])
        faq_str = "\n".join([f"Q: {item['q']} A: {item['a']}" for item in faqs])
        
        # Create context string for vector search
        doc = f"Fund Name: {fund.get('fund_name', 'N/A')}. " \
              f"About: {fund.get('about', 'N/A')}. " \
              f"Frequently Asked Questions: {faq_str}. " \
              f"Current NAV: {fund.get('nav', 'N/A')} as of {fund.get('nav_date', 'N/A')}. " \
              f"Return Since Inception: {fund.get('return_since_inception', 'N/A')}. " \
              f"Absolute Gain: {fund.get('absolute_gain', 'N/A')}. " \
              f"Expense Ratio: {fund.get('expense_ratio', 'N/A')}. " \
              f"Benchmark: {fund.get('benchmark', 'N/A')}. " \
              f"AUM: {fund.get('aum', 'N/A')}. " \
              f"Inception Date: {fund.get('inception_date', 'N/A')}. " \
              f"Min Lumpsum/SIP: {fund.get('min_lumpsum_sip', 'N/A')}. " \
              f"Exit Load: {fund.get('exit_load', 'N/A')}. " \
              f"Turnover: {fund.get('turnover', 'N/A')}. " \
              f"Risk: {fund.get('risk', 'N/A')}. " \
              f"Fund Managers: {fund.get('fund_managers', 'N/A')}."

        # Upsert into collection with ALL metadata fields for direct fallback extraction
        collection.upsert(
            documents=[doc],
            metadatas=[{
                "fund_name": fund.get('fund_name', 'N/A'),
                "nav": fund.get('nav', 'N/A'),
                "nav_date": fund.get('nav_date', 'N/A'),
                "nav_change": fund.get('nav_change', 'N/A'),
                "aum": fund.get('aum', 'N/A'),
                "inception_date": fund.get('inception_date', 'N/A'),
                "expense_ratio": fund.get('expense_ratio', 'N/A'),
                "exit_load": fund.get('exit_load', 'N/A'),
                "turnover": fund.get('turnover', 'N/A'),
                "absolute_gain": fund.get('absolute_gain', 'N/A'),
                "return_since_inception": fund.get('return_since_inception', 'N/A'),
                "benchmark": fund.get('benchmark', 'N/A'),
                "lock_in": fund.get('lock_in', 'N/A'),
                "risk": fund.get('risk', 'N/A'),
                "about": fund.get('about', 'N/A'),
                "fund_managers": fund.get('fund_managers', 'N/A'),
                "min_lumpsum_sip": fund.get('min_lumpsum_sip', 'N/A'),
                "faqs": json.dumps(faqs),
                "source_url": url
            }],
            ids=[url]
        )

    print(f"Phase 2: Ingested {len(data)} funds into Vector DB with full metadata.")

if __name__ == "__main__":
    json_path = os.path.join(os.getcwd(), "phase1", "fund_data.json")
    ingest_to_vector_db(json_path)
