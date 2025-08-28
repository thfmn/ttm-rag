#!/usr/bin/env python3

import http.server
import socketserver
import os

# Change to the documentation build directory
os.chdir(os.path.join(os.path.dirname(__file__), 'docs', '_build', 'html'))

# Set up the server
PORT = 8080

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving documentation at http://localhost:{PORT}")
    httpd.serve_forever()