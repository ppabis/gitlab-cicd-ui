import requests, os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json

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

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>GitLab Project CI</title>
  <!-- Bootstrap CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" crossorigin="anonymous">
</head>
<body>
  <h2>Run Pipeline</h2>
  <form action="/" method="POST">
    Branch: <select name="branch">
      {}
    </select>
    <br>
    Build type:<select name="build_type">
      <option value="debug">Debug</option>
      <option value="release">Release</option>
    </select>
    <br>
    <input type="submit" value="Submit">
  </form>
  <h2>Recent pipelines</h2>
  <table>
    {}
  </table>
</body>
</html>
"""

def format_index():
    branches = [f"<option value=\"{b['name']}\">{b['name']}</option>" for b in get_branches()]
    html_branches = "\n".join(branches)

    pipelines = [
        f"<tr><td><a href=\"{p['web_url']}\">{p['id']}</a></td><td>{p['ref']}</td><td>{p['status']}</td></tr>"
        for p in get_pipelines()
    ]
    html_pipelines = "\n".join(pipelines)
    
    return INDEX_HTML.format(html_branches, html_pipelines)

class GitLabHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(format_index().encode("utf-8"))
        self.wfile.close()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")
        parsed_data = parse_qs(post_data)
        branch = parsed_data["branch"][0]
        build_type = parsed_data["build_type"][0]
        print(f"Triggering pipeline for branch {branch} with build type {build_type}")
        code, data = trigger_pipeline(branch, build_type)
        if code >= 400:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))
        else:
            self.send_response(302)
            self.send_header("Content-type", "text/html")
            self.send_header("Location", "/")
            self.end_headers()
            self.wfile.write("Redirecting".encode("utf-8"))
        self.wfile.close()

def main():
    server_address = ("", 8000)
    server = HTTPServer(server_address, GitLabHandler)
    print("Starting server")
    server.serve_forever()

if __name__ == "__main__":
    main()