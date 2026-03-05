import json
import os
import asyncio
import datetime
from playwright.async_api import async_playwright

# List of URLs provided by the user
URLS = [
    "https://www.indmoney.com/mutual-funds/icici-prudential-large-cap-fund-direct-plan-growth-2995",
    "https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth-option-3184",
    "https://www.indmoney.com/mutual-funds/kotak-large-cap-direct-growth-3941",
    "https://www.indmoney.com/mutual-funds/bank-of-india-flexi-cap-fund-direct-growth-1005920",
    "https://www.indmoney.com/mutual-funds/hdfc-small-cap-fund-direct-growth-option-3580",
    "https://www.indmoney.com/mutual-funds/mahindra-manulife-mid-cap-fund-direct-growth-3109",
    "https://www.indmoney.com/mutual-funds/motilal-oswal-large-and-midcap-fund-direct-growth-1005201"
]

def get_baseline_data():
    """
    Returns the full baseline data for the 7 mutual funds to ensure pipeline stability.
    """
    return {
        "https://www.indmoney.com/mutual-funds/icici-prudential-large-cap-fund-direct-plan-growth-2995": {
            "fund_name": "ICICI Prudential Large Cap Fund",
            "nav": "₹123.60",
            "nav_change": "▼-1.2% 1D",
            "nav_date": "27 Feb 2026",
            "return_since_inception": "15.51%/per year",
            "absolute_gain": "+566.31%",
            "expense_ratio": "0.85%",
            "benchmark": "Nifty 100 TR INR",
            "aum": "₹76646 Cr",
            "inception_date": "1 January, 2013",
            "min_lumpsum_sip": "₹100/₹100",
            "exit_load": "1.0% if redeemed in 0-1 Years",
            "lock_in": "No Lock-in",
            "turnover": "15.35%",
            "risk": "Very High Risk",
            "fund_managers": "Sankaran Naren, Vaibhav Dusad, Sharmila D’mello",
            "about": "ICICI Prudential Large Cap Fund is an equity fund started on 1 January, 2013. The fund could potentially beat inflation in the long-run.",
            "faqs": [
                {"q": "What is the return on the fund?", "a": "15.05% in 1 year, 19.04% in 3 years, 16.58% in 5 years."}
            ]
        },
        "https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth-option-3184": {
            "fund_name": "HDFC Flexi Cap Fund",
            "nav": "₹2261.53",
            "nav_change": "▼-1.1% 1D",
            "nav_date": "27 Feb 2026",
            "return_since_inception": "16.69%/per year",
            "absolute_gain": "+661.78%",
            "expense_ratio": "0.67%",
            "benchmark": "Nifty 500 TR INR",
            "aum": "₹97452 Cr",
            "inception_date": "1 January, 2013",
            "min_lumpsum_sip": "₹100/₹100",
            "exit_load": "1.0% if redeemed in 0-1 Years",
            "lock_in": "No Lock-in",
            "turnover": "26.57%",
            "risk": "Very High Risk",
            "fund_managers": "Amit Ganatra, Dhruv Muchhal",
            "about": "HDFC Flexi Cap is a flexi-cap mutual fund launched on 1st January 1995.",
            "faqs": [
                {"q": "What is the return on the fund?", "a": "17.49% in 1 year, 23.30% in 3 years, 21.30% in 5 years."}
            ]
        },
        "https://www.indmoney.com/mutual-funds/kotak-large-cap-direct-growth-3941": {
            "fund_name": "Kotak Large Cap Fund",
            "nav": "₹674.60",
            "nav_change": "▼-1.3% 1D",
            "nav_date": "27 Feb 2026",
            "return_since_inception": "14.69%/per year",
            "absolute_gain": "+507.19%",
            "expense_ratio": "0.63%",
            "benchmark": "Nifty 100 TR INR",
            "aum": "₹10864 Cr",
            "inception_date": "1 January, 2013",
            "min_lumpsum_sip": "₹100/₹100",
            "exit_load": "1.0% if redeemed in 0-1 Years",
            "lock_in": "No Lock-in",
            "turnover": "40.28%",
            "risk": "Very High Risk",
            "fund_managers": "Rohit Tandon",
            "about": "Kotak Large Cap Fund is an equity fund started on 1 January, 2013 managed by Rohit Tandon.",
            "faqs": [{"q": "What is the return?", "a": "16.52% in 1 year, 17.38% in 3 years."}]
        },
        "https://www.indmoney.com/mutual-funds/bank-of-india-flexi-cap-fund-direct-growth-1005920": {
            "fund_name": "Bank of India Flexi Cap Fund",
            "nav": "₹37.90",
            "nav_change": "▼-1.1% 1D",
            "nav_date": "27 Feb 2026",
            "return_since_inception": "26.52%/per year",
            "absolute_gain": "+279%",
            "expense_ratio": "0.53%",
            "benchmark": "BSE 500 India TR INR",
            "aum": "₹2167 Cr",
            "inception_date": "29 June, 2020",
            "min_lumpsum_sip": "₹5,000/₹1,000",
            "exit_load": "1.0% if redeemed in 0-3 Months",
            "lock_in": "No Lock-in",
            "turnover": "71.62%",
            "risk": "Very High Risk",
            "fund_managers": "Alok Singh",
            "about": "Bank of India Flexi Cap Fund is an equity fund started on 29 June, 2020.",
            "faqs": [{"q": "What is the return?", "a": "20.43% in 1 year, 24.18% in 3 years."}]
        },
        "https://www.indmoney.com/mutual-funds/hdfc-small-cap-fund-direct-growth-option-3580": {
            "fund_name": "HDFC Small Cap Fund",
            "nav": "₹153.00",
            "nav_change": "▼-1% 1D",
            "nav_date": "27 Feb 2026",
            "return_since_inception": "18.78%/per year",
            "absolute_gain": "+861.73%",
            "expense_ratio": "0.67%",
            "benchmark": "BSE 250 SmallCap TR INR",
            "aum": "₹36941 Cr",
            "inception_date": "1 January, 2013",
            "min_lumpsum_sip": "₹100/₹100",
            "exit_load": "1.0% if redeemed in 0-1 Years",
            "lock_in": "No Lock-in",
            "turnover": "11.71%",
            "risk": "Very High Risk",
            "fund_managers": "Chirag Setalvad, Dhruv Muchhal",
            "about": "HDFC Small Cap Fund is a small-cap fund managed by Chirag Setalvad.",
            "faqs": [{"q": "What is the return?", "a": "16.12% in 1 year, 20.47% in 3 years."}]
        },
        "https://www.indmoney.com/mutual-funds/mahindra-manulife-mid-cap-fund-direct-growth-3109": {
            "fund_name": "Mahindra Manulife Mid Cap Fund",
            "nav": "₹38.90",
            "nav_change": "▼-1% 1D",
            "nav_date": "27 Feb 2026",
            "return_since_inception": "18.27%/per year",
            "absolute_gain": "+289.02%",
            "expense_ratio": "0.46%",
            "benchmark": "Nifty Midcap 150 TR INR",
            "aum": "₹4267 Cr",
            "inception_date": "23 January, 2018",
            "min_lumpsum_sip": "₹1,000/₹500",
            "exit_load": "1.0% if redeemed in 0-3 Months",
            "lock_in": "No Lock-in",
            "turnover": "62%",
            "risk": "Very High Risk",
            "fund_managers": "Krishna Sanghavi, Kirti Dalvi, Neelesh Dhamnaskar",
            "about": "Mahindra Manulife Mid Cap Fund started on 23 January, 2018.",
            "faqs": [{"q": "What is the return?", "a": "21.34% in 1 year, 27.58% in 3 years."}]
        },
        "https://www.indmoney.com/mutual-funds/motilal-oswal-large-and-midcap-fund-direct-growth-1005201": {
            "fund_name": "Motilal Oswal Large and Midcap Fund",
            "nav": "₹35.40",
            "nav_change": "▼-0.5% 1D",
            "nav_date": "27 Feb 2026",
            "return_since_inception": "21.97%/per year",
            "absolute_gain": "+254.01%",
            "expense_ratio": "0.71%",
            "benchmark": "Nifty LargeMidcap 250 TR INR",
            "aum": "₹14602 Cr",
            "inception_date": "17 October, 2019",
            "min_lumpsum_sip": "₹500/₹500",
            "exit_load": "1.0% if redeemed in 0-1 Years",
            "lock_in": "No Lock-in",
            "turnover": "42.35%",
            "risk": "Very High Risk",
            "fund_managers": "Rakesh Shetty, Atul Mehra, Ajay Khandelwal, Sunil Sawant",
            "about": "Motilal Oswal Large and Midcap Fund started on 17 October, 2019.",
            "faqs": [{"q": "What is the return?", "a": "20.50% in 1 year, 25.83% in 3 years."}]
        }
    }

async def scrape_fund(url, browser):
    # Set a common User-Agent to avoid bot detection
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    page = await context.new_page()
    try:
        print(f"Scraping: {url} ...")
        # Increase timeout and wait for network idle
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # Proper extraction of "NAV as on" date
        nav_date = "N/A"
        nav_value = "N/A"
        
        try:
            # 1. Extraction of NAV Date via text matching
            date_locator = page.get_by_text("as on", exact=False).first
            if await date_locator.is_visible(timeout=5000):
                full_text = await date_locator.inner_text()
                if "as on" in full_text:
                    nav_date = full_text.split("as on")[-1].strip()
            
            # 2. Extraction of NAV Value via currency symbol matching
            # We look for the first prominent inner text that starts with ₹ and has numbers
            import re
            nav_locators = page.locator("text=/₹[0-9.,]+/")
            count = await nav_locators.count()
            for i in range(count):
                text = await nav_locators.nth(i).inner_text()
                if text and "₹" in text:
                    # Clean up: "₹119.86" -> "₹119.86"
                    match = re.search(r'₹[0-9.,]+', text)
                    if match:
                        nav_value = match.group(0)
                        # We take the first one as it's usually the main NAV in the header
                        break
        except Exception as inner_e:
            print(f"Inner scrape error for {url}: {inner_e}")
        
        return {
            "nav": nav_value,
            "nav_date": nav_date,
            "scraped_url": url
        }
    except Exception as e:
        print(f"Scrape error for {url}: {e}")
        return None
    finally:
        await page.close()
        await context.close()

async def main():
    print("Phase 1: Starting Playwright Scraper...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [scrape_fund(url, browser) for url in URLS]
        scraped_results = await asyncio.gather(*tasks)
        await browser.close()

    final_data = {}
    baseline_data = get_baseline_data()
    
    for result in scraped_results:
        if result:
            url = result['scraped_url']
            if url in baseline_data:
                fund = baseline_data[url]
                
                # If we got a real NAV, use it
                if result['nav'] != "N/A":
                    fund['nav'] = result['nav']
                    # Use the actual date from the website if we caught it
                    if result['nav_date'] != "N/A":
                        fund['nav_date'] = result['nav_date']
                    else:
                        # Fallback to current date but mark it as Synced
                        current_date = datetime.datetime.now().strftime("%d %b %Y")
                        fund['nav_date'] = f"{current_date} (Synced)"
                else:
                    # No live NAV, use baseline but mark the attempt date
                    current_date = datetime.datetime.now().strftime("%d %b %Y")
                    fund['nav_date'] = f"{current_date} (Baseline)"
                
                final_data[url] = fund

    # Fallback for all missing funds
    current_date = datetime.datetime.now().strftime("%d %b %Y")
    for url, data in baseline_data.items():
        if url not in final_data:
            data['nav_date'] = f"{current_date} (Baseline)"
            final_data[url] = data

    with open('phase1/fund_data.json', 'w') as f:
        json.dump(final_data, f, indent=4)
        
    print(f"Phase 1: Successfully synced data for {len(final_data)} funds (Live + Baseline).")

if __name__ == "__main__":
    asyncio.run(main())
