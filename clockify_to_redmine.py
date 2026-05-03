import requests
from datetime import datetime, timedelta, timezone
import csv
import re

# ===== CONFIGURATION =====
CLOCKIFY_API_KEY = "your_clockify_api_key"
CLOCKIFY_WORKSPACE_ID = "your_workspace_id"  # Obtained from the previous script
CLOCKIFY_USER_ID = "your_user_id"  # Obtained from the previous script

# Timezone offset (GMT-5 for Bogota, Colombia)
LOCAL_TZ_OFFSET = timezone(timedelta(hours=-5))

# Date range (last week or custom)
DAYS_BACK = 1

# ===== FUNCTIONS =====
def parse_duration_to_hours(duration_str):
    """
    Converts ISO 8601 duration (PT2H30M15S) to decimal hours
    Example: PT2H30M -> 2.5
    """
    if not duration_str or duration_str == 'PT0S':
        return 0
    
    hours = 0
    minutes = 0
    seconds = 0
    
    # Extract hours
    h_match = re.search(r'(\d+)H', duration_str)
    if h_match:
        hours = int(h_match.group(1))

    # Extract minutes
    m_match = re.search(r'(\d+)M', duration_str)
    if m_match:
        minutes = int(m_match.group(1))

    # Extract seconds
    s_match = re.search(r'(\d+)S', duration_str)
    if s_match:
        seconds = int(s_match.group(1))

    # Convert everything to decimal hours
    total_hours = hours + (minutes / 60) + (seconds / 3600)
    return round(total_hours, 2)

def extract_issue_and_description(clockify_description):
    """
    Extracts issue ID and description from format: #123 project: description
    """
    if not clockify_description:
        return '', ''

    # Extract issue ID (#123)
    issue_match = re.search(r'#(\d+)', clockify_description)
    issue_id = issue_match.group(1) if issue_match else ''

    # Extract description (after the colon)
    desc_match = re.search(r':\s*(.+)', clockify_description)
    description = desc_match.group(1).strip() if desc_match else clockify_description
    
    return issue_id, description

# ===== FETCH TIME ENTRIES FROM CLOCKIFY =====
headers = {
    "X-Api-Key": CLOCKIFY_API_KEY,
    "Content-Type": "application/json"
}

end_date = datetime.now()
start_date = end_date - timedelta(days=DAYS_BACK)

url = f"https://api.clockify.me/api/v1/workspaces/{CLOCKIFY_WORKSPACE_ID}/user/{CLOCKIFY_USER_ID}/time-entries"

params = {
    "start": start_date.isoformat() + "Z",
    "end": end_date.isoformat() + "Z"
}

print(f"Fetching time entries from {start_date.date()} to {end_date.date()}...")
response = requests.get(url, headers=headers, params=params)

if response.status_code != 200:
    print(f"Error: {response.status_code} - {response.text}")
    exit(1)

time_entries = response.json()
print(f"Found {len(time_entries)} records")

# ===== GENERATE CSV FOR REDMINE =====
output_file = f'redmine_import_{datetime.now().strftime("%Y%m%d")}.csv'

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Header for Redmine (matching import_time.py expected columns)
    writer.writerow(['issue_id', 'spent_on', 'hours', 'comments'])
    
    for entry in time_entries:
        # Extract issue ID and description
        clockify_desc = entry.get('description', '')
        issue_id, description = extract_issue_and_description(clockify_desc)

        # Date in YYYY-MM-DD format (converted from UTC to local timezone)
        utc_timestamp = entry['timeInterval']['start']
        utc_dt = datetime.fromisoformat(utc_timestamp.replace('Z', '+00:00'))
        local_dt = utc_dt.astimezone(LOCAL_TZ_OFFSET)
        spent_on = local_dt.strftime('%Y-%m-%d')

        # Duration in hours
        duration = entry['timeInterval'].get('duration', 'PT0S')
        hours = parse_duration_to_hours(duration)

        writer.writerow([issue_id, spent_on, hours, description])
        
        print(f"  - Issue #{issue_id}: {hours}h en {spent_on} - {description[:50]}")

print(f"\n✓ File generated: {output_file}")
print(f"  You can now import it in Redmine")
