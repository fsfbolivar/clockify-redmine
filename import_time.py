import csv
import requests

REDMINE_URL = "https://your-redmine-instance.com"
API_KEY = "your_redmine_api_key"
DEFAULT_ACTIVITY_ID = 9  # Development


def log_time(issue_id, hours, spent_on, comments="", activity_id=DEFAULT_ACTIVITY_ID):
    """Log a time entry to Redmine."""
    url = f"{REDMINE_URL}/time_entries.json"
    data = {
        "time_entry": {
            "issue_id": issue_id,
            "hours": hours,
            "spent_on": spent_on,
            "comments": comments
        }
    }
    if activity_id:
        data["time_entry"]["activity_id"] = activity_id

    response = requests.post(url, json=data, headers={"X-Redmine-API-Key": API_KEY})
    if response.status_code != 201:
        print(f"    Error {response.status_code}: {response.text}")
    return response.status_code == 201


def import_from_csv(csv_path, dry_run=False):
    """Import time entries from a CSV file."""
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            issue_id = row["issue_id"]
            hours = float(row["hours"])
            spent_on = row["spent_on"]
            comments = row.get("comments", "")

            if dry_run:
                print(f"[DRY RUN] Would log {hours}h to issue #{issue_id} on {spent_on}")
            else:
                success = log_time(issue_id, hours, spent_on, comments)
                status = "OK" if success else "FAILED"
                print(f"[{status}] Logged {hours}h to issue #{issue_id} on {spent_on}")


if __name__ == "__main__":
    import sys
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "time_entries.csv"
    dry_run = "--dry-run" in sys.argv
    import_from_csv(csv_path, dry_run)
