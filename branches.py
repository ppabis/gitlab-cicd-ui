import requests, os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

PROJECT_ID = 47513328 # Bring your own project ID
API_URL = "https://gitlab.com/api/v4/" # For self-hosted, change this
GITLAB_TOKEN = os.environ["GITLAB_TOKEN"] # Will fail if not set

def get_branches():
  url = f"{API_URL}/projects/{PROJECT_ID}/repository/branches"
  headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
  response = requests.get(url, headers=headers)

  branches = response.json()
  iterations = 0
  # Loop at most 10 times
  while "next" in response.links and iterations < 10:
    response = requests.get(response.links["next"]["url"], headers=headers)
    branches += response.json()
    iterations += 1
  return branches

def get_pipelines():
    url = f"{API_URL}/projects/{PROJECT_ID}/pipelines?per_page=50"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    return requests.get(url, headers=headers).json()

def trigger_pipeline(branch, build_type):
    url = f"{API_URL}/projects/{PROJECT_ID}/trigger/pipeline"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    body = {
        "ref": branch,
        "variables": [
            { "key": 'BUILD_TYPE', "value": build_type }
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    return (response.status_code, response.json())
