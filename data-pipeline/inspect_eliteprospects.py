import requests
from bs4 import BeautifulSoup

def inspect_page(url, page_name):
    """Download and explore the HTML structure of a page"""
    
    print(f"\n{'='*60}")
    print(f"Inspecting: {page_name}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")
    
    # Add headers to appear like a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML to a file so you can inspect it
        filename = f"{page_name.replace(' ', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f" Downloaded successfully!")
        print(f" Saved HTML to: {filename}")
        print(f" Page title: {soup.title.text if soup.title else 'No title'}")
        
        # Try to find common elements
        print("\n Looking for common patterns...")
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"   - Found {len(tables)} table(s)")
        
        # Look for player links
        player_links = soup.find_all('a', href=lambda x: x and '/player/' in x)
        print(f"   - Found {len(player_links)} player link(s)")
        
        # Show first few player names if found
        if player_links:
            print("\n   First 5 players found:")
            for i, link in enumerate(player_links[:5]):
                print(f"      {i+1}. {link.text.strip()}")
        
        return soup
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Inspect both pages

nhl_stats_url = "https://www.eliteprospects.com/team/75/tampa-bay-lightning?tab=stats"



soup_stats = inspect_page(nhl_stats_url, "NHL Stats")


print("\n" + "="*60)
print(" Inspection complete!")
print("="*60)
print("\nNext steps:")
print("1. Open the saved .html files in a text editor")
print("2. Search for player names to find the HTML structure")
print("3. Look for patterns in table rows or divs")