# 🚀 Professional Development Server

A lightweight, feature-rich development server designed for modern web applications with automatic live reload, anti-caching headers, and SPA (Single Page Application) routing support.

## ✨ Features

- 🔄 **Live Reload** - Automatic browser refresh when files change
- 🚫 **Anti-Caching** - Prevents browser caching during development
- 🎯 **SPA Support** - Handles client-side routing for single-page applications
- ⚡ **Fast & Lightweight** - Minimal overhead with efficient file watching
- 🎛️ **Configurable** - Customizable host, port, and directory settings
- 📁 **Smart Directory Detection** - Automatically detects `dist` and `build` folders
- 🔧 **Professional Logging** - Clean, informative console output

## 📋 Requirements

- Python 3.6+
- Required packages (install via `pip install -r requirements.txt`):
  - `watchdog` - File system monitoring
  - `websockets` - WebSocket support for live reload

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python Server.py
   ```

3. **Or specify a custom directory:**
   ```bash
   python Server.py /path/to/your/project/dist
   ```

## 🎛️ Usage

### Basic Usage
```bash
# Serve current directory on default port (3000)
python Server.py

# Serve specific directory
python Server.py ./dist

# Custom port
python Server.py --port 8080

# Custom host
python Server.py --host 0.0.0.0

# Combined options
python Server.py ./build --port 8080 --host 0.0.0.0
```

### Command Line Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `directory` | - | Current directory | Directory to serve |
| `--port` | `-p` | `3000` | HTTP server port |
| `--host` | `-H` | `localhost` | Server host address |

## 🏗️ Project Structure

This server is designed to work with modern web application builds:

```
your-project/
├── dist/                 # Built application files
│   ├── index.html       # Main HTML file
│   ├── assets/          # Static assets
│   │   ├── main.js      # JavaScript bundles
│   │   ├── style.css    # Stylesheets
│   │   └── ...
│   └── ...
├── Server.py            # This development server
├── requirements.txt     # Python dependencies
└── ...
```

## ⚙️ How It Works

### 🔄 Live Reload System
- **File Watcher**: Monitors your project directory for changes
- **WebSocket Connection**: Establishes real-time communication with the browser
- **Debounced Updates**: Prevents excessive reloads with 300ms delay
- **Smart Filtering**: Ignores Python files and directories

### 🚫 Anti-Caching Headers
The server automatically adds these headers to prevent browser caching:
```http
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Expires: 0
```

### 🎯 SPA Routing Support
- Serves `index.html` for all non-existent routes
- Perfect for React Router, Vue Router, Angular Router, etc.
- Maintains clean URLs without hash routing

## 🔧 Configuration

### Default Ports
- **HTTP Server**: `3000`
- **WebSocket Server**: `3001`

### Environment Detection
The server provides helpful warnings if:
- `index.html` is not found in the target directory
- You're not running from a `dist` or `build` folder

## 📊 Server Output

When running, you'll see a professional dashboard:

```
==================================================
  🚀 Professional Development Server is Running 🚀
  - HTTP Server: http://localhost:3000
  - Live Reload:  Enabled
  - Caching:      Disabled

  Watching for file changes...
  Press Ctrl+C to stop.
==================================================
```

## 🛠️ Development

### Dependencies

Download the `requirements.txt` file.


### Extending the Server

The server is built with modularity in mind:
- `DebouncedReloadHandler`: Custom file system event handler
- `SPAEnabledHandler`: HTTP request handler with SPA support
- WebSocket server for live reload communication

## 🚨 Troubleshooting

### Common Issues

**Port already in use:**
```bash
python Server.py --port 8080
```

**Permission denied:**
```bash
# Use a port > 1024 for non-root users
python Server.py --port 3000
```

**Live reload not working:**
- Check that WebSocket port (3001) is not blocked
- Ensure your browser supports WebSocket connections
- Verify that the `index.html` file contains the `</body>` tag for script injection

### Browser Compatibility

The live reload feature requires WebSocket support:
- ✅ Chrome 16+
- ✅ Firefox 11+
- ✅ Safari 7+
- ✅ Edge 12+

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Made with ❤️ for modern web development**
