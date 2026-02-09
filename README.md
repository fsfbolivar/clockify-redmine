# Clockify to Redmine Time Import

Import time entries from Clockify into Redmine using the Redmine REST API.

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `get_workspace_userid.py` | Get your Clockify workspace and user IDs |
| `clockify_to_redmine.py` | Export Clockify time entries to CSV |
| `import_time.py` | Import CSV time entries into Redmine |

## Setup

### Prerequisites

```bash
pip install requests
```

### Step 1: Get Clockify Credentials

Run `get_workspace_userid.py` to retrieve your Clockify workspace and user IDs:

```bash
python get_workspace_userid.py
```

This will output your workspace ID and user ID. Update these values in `clockify_to_redmine.py`.

### Step 2: Configure Scripts

**`clockify_to_redmine.py`** - Update these variables:
```python
CLOCKIFY_API_KEY = "your_clockify_api_key"
CLOCKIFY_WORKSPACE_ID = "your_workspace_id"
CLOCKIFY_USER_ID = "your_user_id"
LOCAL_TZ_OFFSET = timezone(timedelta(hours=-5))  # Adjust to your timezone
DAYS_BACK = 1  # Number of days to fetch
```

**`import_time.py`** - Update these variables:
```python
REDMINE_URL = "https://your-redmine-instance.com"
API_KEY = "your_redmine_api_key"
DEFAULT_ACTIVITY_ID = 9  # Activity ID (see available activities below)
```

## Usage

### 1. Export from Clockify

```bash
python clockify_to_redmine.py
```

This generates a CSV file named `redmine_import_YYYYMMDD.csv`.

**Clockify description format:** Your Clockify entries should use this format:
```
#12345 project: description of work
```

Where `#12345` is the Redmine issue ID.

### 2. Import to Redmine

```bash
# Dry run first (validate without importing)
python import_time.py redmine_import_20260208.csv --dry-run

# Actual import
python import_time.py redmine_import_20260208.csv
```

## CSV Format

The generated CSV uses this format:

```csv
issue_id,spent_on,hours,comments
12345,2026-02-07,1.5,Code review
12346,2026-02-07,2.0,Bug fix implementation
```

| Column | Description |
|--------|-------------|
| `issue_id` | Redmine issue number |
| `spent_on` | Date in YYYY-MM-DD format |
| `hours` | Decimal hours (e.g., 1.5 for 1h 30m) |
| `comments` | Description of work performed |

## Available Redmine Activities

Query your Redmine instance for available activity IDs:

```bash
curl -H "X-Redmine-API-Key: YOUR_API_KEY" \
  "https://your-redmine.com/enumerations/time_entry_activities.json"
```

Common activities:
| ID | Name |
|----|------|
| 8 | Design |
| 9 | Development |
| 10 | System Administration |
| 11 | Technical Support |
| 12 | Requirements |
| 13 | Documentation |

## Timezone Handling

The `clockify_to_redmine.py` script converts Clockify UTC timestamps to your local timezone. Adjust `LOCAL_TZ_OFFSET` for your location:

```python
# Examples:
LOCAL_TZ_OFFSET = timezone(timedelta(hours=-5))   # GMT-5 (Colombia, EST)
LOCAL_TZ_OFFSET = timezone(timedelta(hours=-8))   # GMT-8 (PST)
LOCAL_TZ_OFFSET = timezone(timedelta(hours=1))    # GMT+1 (CET)
LOCAL_TZ_OFFSET = timezone(timedelta(hours=9))    # GMT+9 (Japan)
```

## Troubleshooting

### Error: "Activity cannot be blank"
Set `DEFAULT_ACTIVITY_ID` in `import_time.py` to a valid activity ID from your Redmine instance.

### Error: "KeyError: 'issue_id'"
Ensure your CSV has the correct column headers: `issue_id`, `spent_on`, `hours`, `comments`.

### Wrong dates in export
Adjust `LOCAL_TZ_OFFSET` in `clockify_to_redmine.py` to match your timezone.

### Entries not found
Increase `DAYS_BACK` in `clockify_to_redmine.py` to fetch more historical entries.

## API References

- [Clockify API](https://docs.clockify.me/)
- [Redmine Time Entries API](https://www.redmine.org/projects/redmine/wiki/Rest_TimeEntries)
