import sys
import os

# Add project root to path to allow imports from phases
sys.path.append(os.getcwd())

from phase3.bot import INDmoneyBot
import json

def run_integration_tests():
    print("--- INDmoney RAG Integration Tests ---")
    bot = INDmoneyBot()
    
    test_cases = [
        {
            "query": "What is the exit load of the ICICI Prudential Large Cap Fund?",
            "check": ["1.0%", "0-1 Years", "https://www.indmoney.com/mutual-funds/icici-prudential-large-cap-fund-direct-plan-growth-2995"]
        },
        {
            "query": "Tell me about HDFC Flexi Cap Fund and its fund managers.",
            "check": ["HDFC Flexi Cap", "Amit Ganatra", "Dhruv Muchhal"]
        },
        {
            "query": "What are the common questions for Motilal Oswal Large and Midcap?",
            "check": ["Motilal Oswal", "20.50% in 1 year", "25.83% in 3 years"]
        },
        {
            "query": "Should I invest in Bank of India Flexi Cap Fund?",
            "check": ["cannot provide investment advice", "facts-only assistant"]
        },
        {
            "query": "What is the exit load of hdfc small cap Fund?",
            "check": ["1.0%", "0-1 Years", "https://www.indmoney.com/mutual-funds/hdfc-small-cap-fund-direct-growth-option-3580"]
        }
    ]
    
    passed = 0
    for i, test in enumerate(test_cases):
        print(f"\nTest {i+1}: Query: {test['query']}")
        response = bot.handle_query(test['query'])
        print(f"Response: {response}")
        
        # Simple verification
        success = all(item.lower() in response.lower() for item in test['check'])
        if success:
            print("Status: PASSED")
            passed += 1
        else:
            missing = [item for item in test['check'] if item.lower() not in response.lower()]
            print(f"Status: FAILED (Missing: {missing})")
            
    print(f"\nSummary: {passed}/{len(test_cases)} tests passed.")

if __name__ == "__main__":
    # Ensure data is fresh before testing integration
    print("Pre-test: Refreshing data pipeline...")
    os.system("python3 phase1/scraper.py")
    os.system("python3 phase2/ingest.py")
    
    run_integration_tests()
