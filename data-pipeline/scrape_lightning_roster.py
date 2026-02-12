import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import time
import re
import os
from dotenv import load_dotenv


load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")


def scrape_player_profile(player_url, player_id):
    """
    Scrape detailed player information from their individual Elite Prospects page
    
    Args:
        player_url: Full URL to player's profile
        player_id: Elite Prospects player ID
    
    Returns:
        Dictionary with player details or None if scraping fails
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(player_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        player_data = {}
        
        # Extract name and position from header
        header = soup.find('h1', class_='ep-entity-header_name')
        if header:
            header_text = header.get_text(strip=True)
            # Format: "Name #Number" or just "Name"
            player_data['name'] = re.sub(r'\s*#\d+\s*$', '', header_text).strip()
        
        # Extract position
        position_tag = soup.find('div', class_='ep-entity-header_position')
        if position_tag:
            player_data['position'] = position_tag.get_text(strip=True)
        
        # Find the player facts section
        facts_section = soup.find('div', class_='player-facts')
        
        if facts_section:
            # Extract all fact items
            fact_items = facts_section.find_all('div', class_='player-facts_fact')
            
            for fact in fact_items:
                label_div = fact.find('div', class_='player-facts_label')
                value_div = fact.find('div', class_='player-facts_value')
                
                if not label_div or not value_div:
                    continue
                
                label = label_div.get_text(strip=True).lower()
                value = value_div.get_text(strip=True)
                
                # Map labels to our fields
                if 'date of birth' in label:
                    # Format: "Jan 02, 2000" or similar
                    try:
                        date_obj = datetime.strptime(value, "%b %d, %Y")
                        player_data['birth_date'] = value
                        player_data['birth_year'] = str(date_obj.year)
                        
                        # Calculate age
                        today = datetime.now()
                        age = today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))
                        player_data['age'] = age
                    except:
                        # Sometimes just the year is shown
                        if value.isdigit() and len(value) == 4:
                            player_data['birth_year'] = value
                            player_data['age'] = datetime.now().year - int(value)
                
                elif 'age' in label:
                    # Direct age field
                    age_match = re.search(r'\d+', value)
                    if age_match:
                        player_data['age'] = int(age_match.group())
                
                elif 'place of birth' in label or 'birthplace' in label:
                    player_data['birthplace'] = value
                
                elif 'nation' in label or 'nationality' in label:
                    player_data['nationality'] = value
                
                elif 'height' in label:
                    player_data['height'] = value
                
                elif 'weight' in label:
                    # Extract just the number
                    weight_match = re.search(r'(\d+)', value)
                    if weight_match:
                        player_data['weight'] = int(weight_match.group(1))
                
                elif 'shoots' in label or 'catches' in label:
                    player_data['shoots_catches'] = value
                
                elif 'youth team' in label:
                    player_data['youth_team'] = value
                
                elif 'drafted' in label:
                    player_data['draft_info'] = value
        
        return player_data
        
    except Exception as e:
        print(f"      Error scraping player profile: {e}")
        return None

def scrape_roster_page(url, roster_type):
    """
    Scrape a Lightning roster page and return list of players
    
    Args:
        url: The Elite Prospects URL
        roster_type: "NHL" or "System" for categorization
    
    Returns:
        List of player dictionaries
    """
    
    print(f"\n Scraping {roster_type} roster from Elite Prospects...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        players = []
        
        # Find all player rows
        player_rows = soup.find_all('tr', class_='SortTable_tr__L9yVC')
        
        print(f"   Found {len(player_rows)} rows to process...")
        
        for idx, row in enumerate(player_rows, 1):
            try:
                # Find the player link in the specific div
                player_div = row.find('div', class_='Roster_player__e6EbP')
                
                if not player_div:
                    continue  # Skip rows without player data
                
                player_link = player_div.find('a', class_='TextLink_link__RhSiC')
                
                if not player_link:
                    continue
                
                # Extract player URL and ID
                player_url = player_link.get('href', '')
                if not player_url.startswith('/player/'):
                    continue
                
                # Get player ID from URL: /player/70424/andrei-vasilevsky -> 70424
                player_id = player_url.split('/')[2]
                full_player_url = f"https://www.eliteprospects.com{player_url}"
                
                # Get full text and extract name and position
                full_text = player_link.get_text(strip=True)
                
                # Extract position (last part in parentheses)
                position_match = re.search(r'\(([A-Z]+)\)', full_text)
                position = position_match.group(1) if position_match else 'Unknown'
                
                # Extract name (everything before the position)
                name = re.sub(r'\s*\([A-Z]+\)\s*$', '', full_text).strip()
                
                print(f"   [{idx}/{len(player_rows)}] Processing: {name} ({position})...")
                
                # Get all table cells for this row (basic roster data)
                cells = row.find_all('td', class_='SortTable_trow__T6wLH')
                
                # Extract jersey number from roster
                jersey_number = None
                if len(cells) > 1:
                    jersey_text = cells[1].get_text(strip=True).replace('#', '')
                    if jersey_text and jersey_text.isdigit():
                        jersey_number = jersey_text
                
                # NOW SCRAPE THE INDIVIDUAL PLAYER PAGE FOR COMPLETE DATA
                print(f"      → Fetching detailed profile...")
                time.sleep(1)  # Be respectful to their servers
                
                player_profile_data = scrape_player_profile(full_player_url, player_id)
                
                # Build the player document
                player = {
                    '_id': f"ep_{player_id}",
                    'name': player_profile_data.get('name', name) if player_profile_data else name,
                    'position': player_profile_data.get('position', position) if player_profile_data else position,
                    'elite_prospects_id': player_id,
                    'elite_prospects_url': full_player_url,
                    'jersey_number': jersey_number,
                    'current_status': {
                        'team': 'Tampa Bay Lightning',
                        'league': 'NHL' if roster_type == 'NHL' else 'System',
                        'roster_status': 'active',
                        'rights_holder': 'Tampa Bay Lightning'
                    },
                    'organizational_history': [{
                        'team': 'Tampa Bay Lightning',
                        'league': 'NHL' if roster_type == 'NHL' else 'System',
                        'start_date': datetime.now(),
                        'end_date': None,
                        'reason': 'initial_scrape'
                    }],
                    'injury_history': [],
                    'scraped_at': datetime.now(),
                    'last_updated': datetime.now(),
                    'source': 'eliteprospects'
                }
                
                # Add all the profile data we scraped
                if player_profile_data:
                    if 'age' in player_profile_data:
                        player['age'] = player_profile_data['age']
                    if 'birth_year' in player_profile_data:
                        player['birth_year'] = player_profile_data['birth_year']
                    if 'birth_date' in player_profile_data:
                        player['birth_date'] = player_profile_data['birth_date']
                    if 'birthplace' in player_profile_data:
                        player['birthplace'] = player_profile_data['birthplace']
                    if 'nationality' in player_profile_data:
                        player['nationality'] = player_profile_data['nationality']
                    if 'height' in player_profile_data:
                        player['height'] = player_profile_data['height']
                    if 'weight' in player_profile_data:
                        player['weight'] = player_profile_data['weight']
                    if 'shoots_catches' in player_profile_data:
                        player['shoots_catches'] = player_profile_data['shoots_catches']
                    if 'youth_team' in player_profile_data:
                        player['youth_team'] = player_profile_data['youth_team']
                    if 'draft_info' in player_profile_data:
                        player['draft_info'] = player_profile_data['draft_info']
                
                players.append(player)
                
                # Show what we got
                age_str = f"{player.get('age')}yo" if player.get('age') else "age:?"
                height_str = player.get('height', '?')
                print(f"      ✓ {name} - {age_str}, {height_str}, #{jersey_number if jersey_number else 'N/A'}")
                
            except Exception as e:
                print(f"      ✗ Error parsing row: {e}")
                continue
        
        print(f"\n Successfully scraped {len(players)} players from {roster_type} roster")
        return players
        
    except requests.exceptions.RequestException as e:
        print(f" Error fetching {url}: {e}")
        return []

def save_players_to_db(players):
    """Save scraped players to MongoDB"""
    
    if not players:
        print("\n  No players to save")
        return
    
    print(f"\n Saving {len(players)} players to MongoDB...")
    
    client = MongoClient(MONGO_URI)
    db = client.lightning_tracker
    
    saved_count = 0
    updated_count = 0
    
    for player in players:
        result = db.player_profiles.update_one(
            {'_id': player['_id']},
            {'$set': player},
            upsert=True
        )
        
        if result.upserted_id:
            saved_count += 1
        else:
            updated_count += 1
    
    print(f"\n Database Update Complete:")
    print(f"     New players added: {saved_count}")
    print(f"     Existing players updated: {updated_count}")
    print(f"     Total players: {saved_count + updated_count}")

def scrape_all_lightning_players():
    """Main function to scrape entire Lightning organization"""
    
    print("\n" + "="*70)
    print(" TAMPA BAY LIGHTNING ORGANIZATION SCRAPER (ENHANCED)")
    print("="*70)
    
    all_players = []
    
    # Scrape NHL roster
    print("\n STEP 1: NHL Roster")
    nhl_url = "https://www.eliteprospects.com/team/75/tampa-bay-lightning"
    nhl_players = scrape_roster_page(nhl_url, "NHL")
    all_players.extend(nhl_players)
    
    # Be nice to their servers
    print("\n Waiting 5 seconds before next request...")
    time.sleep(5)
    
    # Scrape system players (prospects, AHL, etc.)
    print("\n STEP 2: System Players (Prospects/AHL/Juniors)")
    system_url = "https://www.eliteprospects.com/team/75/tampa-bay-lightning/in-the-system"
    system_players = scrape_roster_page(system_url, "System")
    all_players.extend(system_players)
    
    # Save to database
    save_players_to_db(all_players)
    
    print("\n" + "="*70)
    print(f" SCRAPING COMPLETE!")
    print(f" Total players scraped: {len(all_players)}")
    print("="*70)
    
    return all_players

def show_summary(players):
    """Display a summary of scraped players"""
    
    print("\n" + "="*70)
    print(" PLAYER SUMMARY")
    print("="*70)
    
    # Count by position
    from collections import Counter
    positions = Counter(p['position'] for p in players)
    
    print("\n By Position:")
    for pos, count in sorted(positions.items()):
        print(f"   {pos}: {count} player(s)")
    
    # Count by roster type
    nhl_count = sum(1 for p in players if p['current_status']['league'] == 'NHL')
    system_count = sum(1 for p in players if p['current_status']['league'] == 'System')
    
    print(f"\n By Roster:")
    print(f"   NHL Roster: {nhl_count} player(s)")
    print(f"   System/Prospects: {system_count} player(s)")
    
    # Count completeness
    complete_count = sum(1 for p in players if p.get('age') and p.get('height'))
    incomplete_count = len(players) - complete_count
    
    print(f"\n Data Quality:")
    print(f"   Complete profiles: {complete_count}/{len(players)}")
    if incomplete_count > 0:
        print(f"     Incomplete profiles: {incomplete_count}")
    
    # Show first 15 players
    print(f"\n First 15 Players:")
    for i, player in enumerate(players[:15], 1):
        league = player['current_status']['league']
        jersey = f"#{player['jersey_number']}" if player.get('jersey_number') else "N/A"
        age = f"{player['age']}yo" if player.get('age') else "?"
        height = player.get('height', '?')
        print(f"   {i:2d}. {player['name']:25s} ({player['position']:2s}) {jersey:4s} - {age:4s}, {height:7s} [{league}]")
    
    if len(players) > 15:
        print(f"   ... and {len(players) - 15} more")

if __name__ == "__main__":
    # Run the scraper
    players = scrape_all_lightning_players()
    
    # Show summary
    if players:
        show_summary(players)
        
        print("\n" + "="*70)
        print(" Next steps:")
        print("   1. Check MongoDB Atlas to see your complete data")
        print("   2. All players should now have age and height!")
        print("   3. Ready to add stats scraping next")
        print("="*70)