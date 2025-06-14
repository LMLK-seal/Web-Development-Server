import http.server
import socketserver
import threading
import webbrowser
import os
import sys
import time
import logging
from pathlib import Path
import argparse
import asyncio
import websockets

# Third-party dependencies: watchdog, websockets
# Install using: pip install -r requirements.txt
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Error: Required libraries not found. Please install dependencies.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# --- Configuration (can be overridden by command-line args) ---
DEFAULT_HTTP_PORT = 3000
DEFAULT_WS_PORT = 3001
DEFAULT_HOST = "localhost"
# -------------------------------------------------------------

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# --- WebSocket Live Reload Logic ---
CONNECTED_CLIENTS = set()
ws_loop = None

async def register_client(websocket):
    CONNECTED_CLIENTS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CONNECTED_CLIENTS.remove(websocket)

async def start_ws_server(host, port):
    global ws_loop
    ws_loop = asyncio.get_running_loop()
    async with websockets.serve(register_client, host, port):
        await asyncio.Future() # run forever

def trigger_reload():
    if not ws_loop or not CONNECTED_CLIENTS:
        return
    
    logging.info("Change detected. Triggering browser reload...")
    asyncio.run_coroutine_threadsafe(
        asyncio.wait([client.send("reload") for client in CONNECTED_CLIENTS]),
        ws_loop
    )

# --- File Watcher with Debouncing ---
class DebouncedReloadHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.timer = None

    def on_any_event(self, event):
        if event.is_directory or ".py" in event.src_path:
            return
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        self.timer = threading.Timer(0.3, self.callback) # 300ms debounce
        self.timer.start()

# --- HTTP Server for SPA with Anti-Cache Headers ---
class SPAEnabledHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def end_headers(self):
        """
        [NEW] This is the key change to prevent browser caching.
        These headers are sent with every response to tell the browser
        not to store any files, ensuring you always get the latest version.
        """
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        # Handle SPA routing: if a file isn't found, serve index.html
        path_on_disk = self.translate_path(self.path)
        if not os.path.exists(path_on_disk):
            self.path = 'index.html'
            # Inject the live-reload WebSocket client script into index.html
            try:
                with open(self.translate_path(self.path), 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use the WebSocket port attached to the server instance
                ws_port = self.server.ws_port
                ws_script = f"""
                <script>
                  (function() {{
                    const ws = new WebSocket('ws://{self.server.server_address[0]}:{ws_port}');
                    ws.onmessage = (event) => {{ if (event.data === 'reload') window.location.reload(); }};
                    console.log('Live-reload enabled.');
                  }})();
                </script>
                </body>
                """
                content = content.replace('</body>', ws_script)
                encoded_content = content.encode('utf-8')
                
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded_content)))
                self.end_headers() # This will call our new anti-cache method
                self.wfile.write(encoded_content)
                return
            except Exception as e:
                logging.error(f"Could not inject WS script or serve index.html: {e}")
                
        # If the file exists, serve it normally (our end_headers will still apply)
        return super().do_GET()

    def log_message(self, format, *args):
        # Suppress noisy default logging
        return

def start_http_server(host, port, ws_port, directory):
    # We create a custom TCPServer that can hold a reference to the ws_port
    class CustomTCPServer(socketserver.TCPServer):
        def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
            super().__init__(server_address, RequestHandlerClass, bind_and_activate)
            self.ws_port = None # Will be set after initialization

    def handler_factory(*args, **kwargs):
        return SPAEnabledHandler(*args, directory=directory, **kwargs)

    httpd = CustomTCPServer((host, port), handler_factory)
    httpd.ws_port = ws_port # Attach the ws_port for the handler to access
    
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    logging.info(f"HTTP server started for directory '{directory}'")
    return httpd

def start_watcher(directory, callback):
    observer = Observer()
    observer.schedule(DebouncedReloadHandler(callback), directory, recursive=True)
    observer.daemon = True
    observer.start()
    logging.info("File watcher started.")
    return observer

def main():
    parser = argparse.ArgumentParser(description="A professional web app server with live reload and no caching.")
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help="Directory to serve (default: current).")
    parser.add_argument('--port', '-p', type=int, default=DEFAULT_HTTP_PORT, help=f"HTTP port (default: {DEFAULT_HTTP_PORT}).")
    parser.add_argument('--host', '-H', default=DEFAULT_HOST, help=f"Host (default: '{DEFAULT_HOST}').")
    args = parser.parse_args()

    serve_dir = Path(args.directory).resolve()
    if not (serve_dir / "index.html").exists():
        logging.warning(f"'index.html' not found in {serve_dir}.")
        if "dist" not in str(serve_dir).lower() and "build" not in str(serve_dir).lower():
             logging.warning("Warning: Are you running this from your project's 'dist' or 'build' folder?")
        time.sleep(3)

    # Start WebSocket server in its own thread
    ws_thread = threading.Thread(target=asyncio.run, args=(start_ws_server(args.host, DEFAULT_WS_PORT),))
    ws_thread.daemon = True
    ws_thread.start()

    # Start main services
    http_server = start_http_server(args.host, args.port, DEFAULT_WS_PORT, str(serve_dir))
    watcher = start_watcher(str(serve_dir), trigger_reload)

    url = f"http://{args.host}:{args.port}"
    webbrowser.open(url)
    
    print("\n" + "="*50)
    print("  🚀 Professional Development Server is Running 🚀")
    print(f"  - HTTP Server: {url}")
    print(f"  - Live Reload:  Enabled")
    print(f"  - Caching:      Disabled")
    print("\n  Watching for file changes...")
    print("  Press Ctrl+C to stop.")
    print("="*50 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        http_server.shutdown()
        watcher.stop()
        watcher.join()
    finally:
        logging.info("Shutdown complete. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()