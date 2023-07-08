import requests, os
PROJECT_ID = 47513328 # Bring your own project ID
API_URL = "https://gitlab.com/api/v4/" # For self-hosted, change this
GITLAB_TOKEN = os.environ["GITLAB_TOKEN"] # Will fail if not set

def get_branches():
  url = f"{API_URL}/projects/{PROJECT_ID}/repository/branches"
  headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
  response = requests.get(url, headers=headers)
  return response.json()