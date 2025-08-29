#!/usr/bin/env python3

import http.server
import socketserver
import os

# Change to the documentation build directory
docs_path = os.path.join(os.path.dirname(__file__), 'docs', '_build', 'html')
print(f"Changing to directory: {docs_path}")
os.chdir(docs_path)

# Verify we're in the right directory and can see index.html
if os.path.exists('index.html'):
    print("Found index.html")
else:
    print("ERROR: index.html not found")
    exit(1)

# Set up the server
PORT = 8081

Handler = http.server.SimpleHTTPRequestHandler

print(f"Serving documentation at http://localhost:{PORT}")
try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Server started successfully")
        httpd.serve_forever()
except Exception as e:
    print(f"Error starting server: {e}")