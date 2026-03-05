import chromadb
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from Phase 3's .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

class INDmoneyBot:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in .env file.")
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')

        # Update path to look into Phase 2's isolated storage
        path = os.path.join(os.getcwd(), "phase2", "chroma_db")
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection("fund_data")
        self.known_funds = ["icici", "prudential", "hdfc", "kotak", "bank of india", "mahindra", "manulife", "motilal", "oswal"]
        
    def is_relevant(self, query):
        """
        Check if the query is about mutual funds or our specific funds,
        and filter out advice-seeking or subjective questions.
        """
        query_l = query.lower()
        
        # 1. Block explicit advice-seeking or subjective triggers
        advice_keywords = ["best", "should", "advice", "recommend", "suggest", "me", "my", "better", "top", "good", "noob", "student", "grandfather", "elder", "parent"]
        # If any advice keyword is present AND no specific fund name is mentioned, it's likely out of scope
        has_advice_keyword = any(k in query_l for k in advice_keywords)
        has_fund_name = any(f in query_l for f in self.known_funds)
        
        # If they ask "best fund" or "should I invest", it's advice.
        if has_advice_keyword and not has_fund_name:
             return False
        
        # Check for non-advice relevance
        fund_keywords = [
            "fund", "nav", "ratio", "aum", "inception", "sip", "lumpsum", 
            "exit", "load", "risk", "investment", "manager", "return", "gain", 
            "about", "faq", "question", "turnover", "invest", "history", "start",
            "absolute", "benchmark", "lock-in", "minimum", "buy", "how"
        ]

        
        if has_fund_name:
            return True
        if any(k in query_l for k in fund_keywords):
            return True
            
        return False


    def generate_fallback_answer(self, query, metadata, url):
        """
        Pinpoints specific answers from metadata even without LLM.
        Directly addresses user requests for 'About', 'FAQs', 'Turnover' etc.
        """
        query_l = query.lower()
        # 0. Block advice/persona even in fallback
        advice_keywords = ["best", "should", "advice", "recommend", "suggest", "better", "top", "good", "noob", "student", "grandfather", "elder", "parent"]
        if any(k in query_l for k in advice_keywords):
            return "I cannot provide investment advice or fund recommendations. I can only share factual data like NAV, AUM, and Expense Ratios for specific funds."

        if not self.is_relevant(query):
            return "I am a factual mutual fund assistant and can only help with data provided in my knowledge base. Your query appears to be out of scope."

        name = metadata.get('fund_name', 'The fund')
        
        # 1. About / History
        if "about" in query_l or "history" in query_l or "tell me about" in query_l:
            return f"About {name}: {metadata.get('about', 'N/A')}\nSource: {url}"
            
        # 2. Invest / Minimums / Lumpsum / SIP / Buy (High Priority)
        invest_keywords = ["lumpsum", "sip", "minimum", "buy", "method", "process"]
        is_invest_query = any(w in query_l for w in invest_keywords) or ("how" in query_l and ("invest" in query_l or "buy" in query_l or "start" in query_l))
        
        if is_invest_query:
            min_data = metadata.get('min_lumpsum_sip', 'N/A')
            lumpsum = min_data.split('/')[0] if '/' in min_data else min_data
            sip = min_data.split('/')[-1] if '/' in min_data else min_data
            return f"To invest in {name}, the minimum lumpsum required is {lumpsum} and the minimum SIP is {sip}.\nSource: {url}"

        # 3. FAQs / Specific Questions
        if "faq" in query_l or "question" in query_l:
            faqs = metadata.get('faqs', '[]')
            try:
                faq_list = json.loads(faqs)
                if faq_list:
                    # If specific word from query matches an FAQ question, prioritize it
                    for f in faq_list:
                        if any(word in query_l for word in f['q'].lower().split() if len(word) > 3):
                            return f"Question: {f['q']}\nAnswer: {f['a']}\nSource: {url}"
                    
                    formatted_faqs = "\n".join([f"Q: {f['q']}\nA: {f['a']}" for f in faq_list])
                    return f"Frequently Asked Questions for {name}:\n{formatted_faqs}\nSource: {url}"
            except:
                pass
            return f"I don't have specific FAQs for {name} right now.\nSource: {url}"

        # 3. Absolute Gain
        if "gain" in query_l or "absolute" in query_l:
            return f"The absolute gain for {name} is {metadata.get('absolute_gain', 'N/A')}.\nSource: {url}"

        # 4. Turnover
        if "turnover" in query_l:
            return f"The portfolio turnover for {name} is {metadata.get('turnover', 'N/A')}.\nSource: {url}"

        # 5. Return since inception
        if "return" in query_l and ("inception" in query_l or "since" in query_l or "start" in query_l):
            return f"The return since inception for {name} is {metadata.get('return_since_inception', 'N/A')}.\nSource: {url}"

        # 6. AUM
        if "aum" in query_l:
            return f"The AUM of {name} is {metadata.get('aum', 'N/A')}.\nSource: {url}"

        # 7. NAV
        if "nav" in query_l:
            return f"The current NAV of {name} is {metadata.get('nav', 'N/A')} as of {metadata.get('nav_date', 'N/A')}.\nSource: {url}"

        # 8. Inception Date
        if "inception" in query_l or "start" in query_l:
            return f"The inception date for {name} is {metadata.get('inception_date', 'N/A')}.\nSource: {url}"

        # 9. Expense Ratio
        if "expense" in query_l or "ratio" in query_l:
            return f"The expense ratio of {name} is {metadata.get('expense_ratio', 'N/A')}.\nSource: {url}"

        # 10. Benchmark
        if "benchmark" in query_l:
            return f"The benchmark for {name} is {metadata.get('benchmark', 'N/A')}.\nSource: {url}"

        # 11. Lock In
        if "lock" in query_l:
            return f"The lock-in period for {name} is {metadata.get('lock_in', 'N/A')}.\nSource: {url}"

        # 12. Exit Load
        if "exit" in query_l or "load" in query_l:
            return f"The exit load for {name} is {metadata.get('exit_load', 'N/A')}.\nSource: {url}"

        # 11. Risk
        if "risk" in query_l:
            return f"The risk category for {name} is {metadata.get('risk', 'N/A')}.\nSource: {url}"

        # 12. Manager
        if "manager" in query_l:
            return f"The fund managers for {name} are {metadata.get('fund_managers', 'N/A')}.\nSource: {url}"

        # Default Summary Block (clean and single)
        res = f"{name} Summary:\n- NAV: {metadata.get('nav', 'N/A')}\n- AUM: {metadata.get('aum', 'N/A')}\n- Exit Load: {metadata.get('exit_load', 'N/A')}\n- Risk: {metadata.get('risk', 'N/A')}"
        return f"{res}\n\nSource: {url}"

    def handle_query(self, query):
        """
        Handles the entire query lifecycle in ONE Gemini API call.
        """
        try:
            # 1. First Pass Health/Relevance Check
            if not self.is_relevant(query):
                return "I am a factual mutual fund assistant and can only help with data provided in my knowledge base. For investment advice or general questions, please consult a financial advisor."

            # 2. Ambiguity Check: Ensure a fund is mentioned for specific data queries
            query_l = query.lower().strip()
            has_fund_name = any(f in query_l for f in self.known_funds)
            
            # Expanded list of generic keywords that require a specific fund context
            generic_keywords = [
                "nav", "aum", "ratio", "benchmark", "sip", "lumpsum", "exit", "load", "risk", 
                "manager", "turnover", "gain", "return", "inception", "lock-in", "about", 
                "faq", "fund", "performance", "history", "details", "summary", "information",
                "inspection", "invest", "buy", "how", "to", "process", "method", "minimum",
                "investment", "investing"
            ]


            
            # Logic: If the query contains generic words but NO fund name, and is short/simple
            words = [w.strip('?') for w in query_l.split()]
            # Catch standalone keywords or short phrases like "return since inception" or "how to invest"
            is_mostly_generic = all(w in generic_keywords or w in ["of", "the", "for", "since", "in", "what", "is", "a", "inspection", "inception"] for w in words)
            contains_generic = any(k in query_l for k in generic_keywords)

            if contains_generic and not has_fund_name and (is_mostly_generic or len(words) <= 4):
                return "Which mutual fund are you asking about? Please specify the fund name (e.g., 'NAV of HDFC Flexi Cap' or 'About ICICI Large Cap') so I can give you the exact data."



            # 3. Retrieve context from Vector DB (Local, no API cost)
            results = self.collection.query(
                query_texts=[query],
                n_results=1
            )
            
            context = "No specific data found."
            url = "https://www.indmoney.com"
            metadata = {}
            
            if results and results['documents'] and results['documents'][0]:
                context = results['documents'][0][0]
                metadata = results['metadatas'][0][0]
                url = metadata.get('source_url', url)

            # 3. Construct unified prompt for Intent + Synthesis
            prompt = f"""
            SYSTEM ROLE:
            You are a strict factual mutual fund assistant for INDmoney.
            
            GUARDRAILS:
            1. If the query is unrelated to mutual funds, INDmoney, or financial data provided explicitly in the context, refuse to answer. Say: "I am a factual mutual fund assistant and can only help with data provided in my knowledge base."
            2. Do NOT provide investment advice or recommendations. 
               - If asked "Which fund is best?", "Should I invest?", "Best for students/parents", etc., refuse. 
               - Say: "I cannot provide investment advice or fund recommendations. I can only share factual data like NAV, AUM, and Expense Ratios for specific funds."
            3. Answer precisely. If a specific data point (like AUM, Turnover, Absolute Gain, Benchmark, Lock-in, Lumpsum/SIP, or FAQ) is asked, provide that specific value/section at the very beginning of your response.
            4. If the query asks "How to invest", "How to buy", or mentions "Minimum investment", provide the specific Min Lumpsum and SIP details for the fund.
            5. If the query is subjective (e.g., "Am I a good investor?"), refuse.
            6. CRITICAL: If the user does NOT specify a fund name in the query (e.g., just "NAV", "Expense Ratio"), do NOT guess or provide data for a default fund. Instead, politely ask the user to specify which mutual fund they are asking about.
            7. Use ONLY the provided context. If the query asks for a comparison or ranking not explicitly in the context, refuse.
            8. Do NOT repeat your answer or provide duplicate information. Be concise.
            
            CONTEXT:
            {context}
            
            QUERY: {query}
            """

            # 4. Single Gemini API Call
            if hasattr(self, 'model'):
                try:
                    response = self.model.generate_content(prompt)
                    answer = response.text.strip()
                    # Prevent potential empty response from Gemini
                    if not answer:
                        return self.generate_fallback_answer(query, metadata, url)
                    return f"{answer}\n\nSource: {url}"
                except Exception as api_error:
                    print(f"Gemini API Error: {api_error}")
                    # Fallback if API fails
                    return self.generate_fallback_answer(query, metadata, url)
            else:
                return self.generate_fallback_answer(query, metadata, url)

        except Exception as e:
            return f"I encountered an error while processing your request: {e}"

if __name__ == "__main__":
    bot = INDmoneyBot()
    # Test specific extraction
    print("Test About:", bot.handle_query("About Motilal Oswal"))
    print("\nTest Absolute Gain:", bot.handle_query("absolute gain of motilal"))
    print("\nTest Turnover:", bot.handle_query("turnover of Motilal oswal"))
    print("\nTest Return Since Inception:", bot.handle_query("Return since inception of Motilal oswal"))
    print("\nTest FAQ:", bot.handle_query("Frequently Asked Questions for Motilal Oswal"))
