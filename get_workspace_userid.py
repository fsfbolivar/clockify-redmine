import requests

CLOCKIFY_API_KEY = "your_clockify_api_key"

headers = {
    "X-Api-Key": CLOCKIFY_API_KEY,
    "Content-Type": "application/json"
}

# Obtener workspaces
response = requests.get("https://api.clockify.me/api/v1/workspaces", headers=headers)
workspaces = response.json()
print("Workspaces:", workspaces)

# Obtener info del usuario actual
response = requests.get("https://api.clockify.me/api/v1/user", headers=headers)
user = response.json()
print("User ID:", user['id'])
print("Default Workspace:", user['defaultWorkspace'])
