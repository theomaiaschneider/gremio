import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import os

# ESPN Grêmio schedule URL
URL = "https://www.espn.com.br/futebol/time/calendario/_/id/6273/gremio"

# Function to scrape match data
def scrape_matches():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    matches = []
    for row in soup.select(".Table__TR"):  # Adjust selector if needed
        cols = row.find_all("td")
        if len(cols) < 3:
            continue  # Skip invalid rows
        
        date_text = cols[0].text.strip()
        time_text = cols[1].text.strip()
        teams = cols[2].text.strip()
        competition = cols[3].text.strip() if len(cols) > 3 else ""
        
        if "Definir" in time_text:
            continue  # Skip games without set time
        
        match_datetime = datetime.strptime(f"{date_text} {time_text}", "%d/%m/%Y %H:%M")
        matches.append({
            "summary": teams,
            "start": match_datetime,
            "end": match_datetime.replace(hour=match_datetime.hour+2),  # Assume 2-hour duration
            "description": competition
        })
    
    return matches

# Function to generate ICS file
def generate_ics(matches):
    calendar = Calendar()
    for match in matches:
        event = Event()
        event.name = match["summary"]
        event.begin = match["start"].isoformat()
        event.end = match["end"].isoformat()
        event.description = match["description"]
        calendar.events.add(event)
    
    with open("gremio_schedule.ics", "w") as f:
        f.writelines(calendar)

# Function to push the updated ICS file to GitHub
def push_to_github():
    os.system("git -C gremio add gremio_schedule.ics")
    os.system('git -C gremio commit -m "Auto-update Grêmio schedule"')
    os.system("git -C gremio push origin main")  # Change 'main' if your default branch is different

# Run the functions
matches = scrape_matches()
generate_ics(matches)
push_to_github()

print("ICS file generated and pushed to GitHub: gremio_schedule.ics")
