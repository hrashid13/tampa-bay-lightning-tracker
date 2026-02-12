import requests
from bs4 import BeautifulSoup

def save_page(url, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"✅ Saved {filename}")

# Save both stats pages
save_page("https://www.eliteprospects.com/team/75/tampa-bay-lightning?tab=stats", "NHL_Stats.html")
