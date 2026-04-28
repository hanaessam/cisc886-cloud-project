#!/usr/bin/env python3
"""
GlowBot proxy server
- Serves static files on port 3000
- Forwards /api/generate to Ollama on localhost:11434
"""

import http.server
import json
import urllib.request
import urllib.error
import os
import socketserver

PORT = 3000
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))


class GlowBotHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/generate":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)

                req = urllib.request.Request(
                    OLLAMA_URL,
                    data=body,
                    headers={
                        "Content-Type": "application/json",
                        "Connection": "keep-alive",
                    },
                    method="POST",
                )

                with urllib.request.urlopen(req, timeout=300) as resp:
                    response_body = resp.read()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                self.wfile.write(response_body)
                self.wfile.flush()
                print(f"[OK] /api/generate responded {len(response_body)} bytes")

            except Exception as e:
                print(f"[ERROR] {e}")
                error = json.dumps({"error": str(e)}).encode()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(error)))
                self.end_headers()
                self.wfile.write(error)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[GlowBot] {self.address_string()} - {format % args}")


socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), GlowBotHandler) as httpd:
    print(f"[GlowBot] Server running on port {PORT}")
    print(f"[GlowBot] Static files from: {STATIC_DIR}")
    print(f"[GlowBot] Proxying /api/generate → {OLLAMA_URL}")
    httpd.serve_forever()
