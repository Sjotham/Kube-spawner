from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json
import sys

# Import KubeSpawner
sys.path.append("/home/kubespawner/")  # Add the correct path to KubeSpawner
from kubespawner import KubeSpawner



class JSONRPCHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Parse the content length and read the request body
        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length).decode('utf-8')

        # Parse JSON request
        try:
            request = json.loads(request_body)
            method = request.get('method')
            params = request.get('params', [])
            request_id = request.get('id')
        except json.JSONDecodeError:
            self.respond_with_error("Invalid JSON format", None)
            return

        # Dispatch the method
        response = self.dispatch_method(method, params, request_id)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def dispatch_method(self, method, params, request_id):
        """Handle the method dispatch."""
        methods = {
        
        
            "create_k8s_pod": self.create_k8s_pod,
        }

        if method not in methods:
            return self.create_error_response(f"Method {method} not found", request_id)

        try:
            # Call the method and return the result
            result = methods[method](*params)
            return self.create_response(result, request_id)
        except Exception as e:
            return self.create_error_response(str(e), request_id)

    def create_response(self, result, request_id):
        """Create a JSON-RPC success response."""
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }

    def create_error_response(self, error_message, request_id):
        """Create a JSON-RPC error response."""
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": error_message},
            "id": request_id
        }



    def create_k8s_pod(self, username, namespace="default"):
        """
        Create a Kubernetes pod using KubeSpawner for a given user.
        """
        spawner = KubeSpawner()
        # spawner.start()
            
       


def run_server():
    host, port = "127.0.0.1", 8000
    server = HTTPServer((host, port), JSONRPCHandler)
    print(f"JSON-RPC Server is running on {host}:{port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the server.")
        server.server_close()


if __name__ == "__main__":
    run_server()