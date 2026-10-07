"""
Tiny local server: serves index.html and proxies /api/countries to
REST Countries with your API key (server-to-server, so no CORS problem).

Run:   python server.py
Open:  http://localhost:8000
"""
import json, os, urllib.error, urllib.parse, urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

FILE_KEY = "rc_live_173dd064cbcc4856825701ace94cab5c"
ENV_KEY = os.environ.get("RESTCOUNTRIES_KEY")

# Strip stray spaces / quotes / line breaks that often sneak into env vars
API_KEY = (ENV_KEY or FILE_KEY).strip().strip("\"'").strip()
KEY_SOURCE = "environment variable RESTCOUNTRIES_KEY" if ENV_KEY else "server.py"
UPSTREAM = "https://api.restcountries.com/countries/v5"
PORT = int(os.environ.get("PORT", "8000"))

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path == "/api/countries":
            return self.proxy(parsed.query)
        return super().do_GET()

    def proxy(self, query):
        url = UPSTREAM + ("?" + query if query else "")
        req = urllib.request.Request(url, headers={
            "Authorization": "Bearer " + API_KEY,
            "Accept": "application/json",
            "User-Agent": "WorldCountriesApp/1.0",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                status, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            status, body = e.code, e.read()
        except Exception as e:
            status = 502
            body = json.dumps({"errors": [{"message": "Server could not reach REST Countries: %s" % e}]}).encode()

        print("-> REST Countries answered HTTP %d  (key from %s: %s...%s)"
              % (status, KEY_SOURCE, API_KEY[:8], API_KEY[-4:]))

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("Using key from %s: %s...%s (length %d, should be 40)"
          % (KEY_SOURCE, API_KEY[:8], API_KEY[-4:], len(API_KEY)))
    print("Open http://localhost:%d" % PORT)
    ThreadingHTTPServer(("", PORT), Handler).serve_forever()
