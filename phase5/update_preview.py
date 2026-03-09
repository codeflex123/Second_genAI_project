import json
import os

def update_preview():
    json_path = os.path.join(os.getcwd(), "phase1", "fund_data.json")
    preview_path = os.path.join(os.getcwd(), "data_preview.md")
    
    if not os.path.exists(json_path):
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Get the latest date from the first fund
    latest_date = "N/A"
    if data:
        latest_date = next(iter(data.values())).get('nav_date', 'N/A')

    header = f"""# Mutual Fund Data Preview

This file provides a factual summary of the data extracted from INDmoney for the 7 supported mutual funds. 
**Last Sync: {latest_date}**

| Fund Name | NAV | Expense Ratio | AUM | Risk Category | Source Link |
|---|---|---|---|---|---|
"""
    
    rows = []
    for url, fund in data.items():
        name = fund.get('fund_name', 'N/A')
        nav = fund.get('nav', 'N/A')
        er = fund.get('expense_ratio', 'N/A')
        aum = fund.get('aum', 'N/A')
        risk = fund.get('risk', 'N/A')
        rows.append(f"| {name} | {nav} | {er} | {aum} | {risk} | [Link]({url}) |")

    footer = "\n---\n*Note: Data is synchronized daily via GitHub Actions at 10:00 AM IST.*"
    
    content = header + "\n".join(rows) + footer
    
    with open(preview_path, 'w') as f:
        f.write(content)
    print(f"Successfully updated {preview_path}")

if __name__ == "__main__":
    update_preview()
