#!/usr/bin/env python3
"""
Webhook API Server for PyQt6 Theme Editor
REST API for remote theme operations and integration
"""

import json
import http.server
import socketserver
import urllib.parse
from typing import Dict, Any, Optional
from pathlib import Path
import threading
import subprocess
import sys

class ThemeAPIHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for theme API."""
    
    def __init__(self, *args, **kwargs):
        # Import here to avoid circular imports
        from cli_mode import ThemeCLI
        self.theme_cli = ThemeCLI()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        try:
            if path == '/':
                self.send_api_info()
            elif path == '/api/presets':
                self.get_presets()
            elif path == '/api/preset':
                preset_name = query_params.get('name', [None])[0]
                if preset_name:
                    self.get_preset(preset_name)
                else:
                    self.send_error_response(400, "Missing 'name' parameter")
            elif path == '/api/theme/current':
                self.get_current_theme()
            elif path == '/health':
                self.send_json_response({"status": "healthy", "service": "PyQt6 Theme Editor API"})
            else:
                self.send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body.decode('utf-8'))
                except json.JSONDecodeError:
                    self.send_error_response(400, "Invalid JSON in request body")
                    return
            else:
                data = {}
            
            if path == '/api/launch':
                self.launch_application(data)
            elif path == '/api/theme/modify':
                self.modify_theme(data)
            elif path == '/api/theme/export':
                self.export_theme(data)
            elif path == '/api/theme/import':
                self.import_theme(data)
            elif path == '/api/preset/load':
                self.load_preset(data)
            else:
                self.send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def send_api_info(self):
        """Send API information and available endpoints."""
        info = {
            "service": "PyQt6 Theme Editor API",
            "version": "1.0.0",
            "endpoints": {
                "GET": {
                    "/": "API information",
                    "/api/presets": "List available presets",
                    "/api/preset?name=<name>": "Get specific preset",
                    "/api/theme/current": "Get current theme",
                    "/health": "Health check"
                },
                "POST": {
                    "/api/launch": "Launch GUI or CLI mode",
                    "/api/theme/modify": "Modify current theme",
                    "/api/theme/export": "Export theme",
                    "/api/theme/import": "Import theme",
                    "/api/preset/load": "Load preset"
                }
            },
            "examples": {
                "launch_gui": {
                    "url": "/api/launch",
                    "method": "POST",
                    "body": {"mode": "gui", "preset": "Dark Sci-Fi"}
                },
                "modify_color": {
                    "url": "/api/theme/modify",
                    "method": "POST", 
                    "body": {"colors": {"Primary": "#FF6B35"}}
                },
                "export_theme": {
                    "url": "/api/theme/export",
                    "method": "POST",
                    "body": {"filename": "my_theme.qss", "format": "qss"}
                }
            }
        }
        self.send_json_response(info)
    
    def get_presets(self):
        """Get list of available presets."""
        presets = list(self.theme_cli.presets.keys())
        response = {
            "presets": presets,
            "count": len(presets)
        }
        self.send_json_response(response)
    
    def get_preset(self, preset_name: str):
        """Get specific preset theme."""
        if preset_name not in self.theme_cli.presets:
            self.send_error_response(404, f"Preset '{preset_name}' not found")
            return
            
        preset_data = self.theme_cli.presets[preset_name]
        response = {
            "name": preset_name,
            "theme": preset_data
        }
        self.send_json_response(response)
    
    def get_current_theme(self):
        """Get current theme configuration."""
        response = {
            "theme": self.theme_cli.current_theme,
            "preview_css": self.theme_cli.generate_css()
        }
        self.send_json_response(response)
    
    def launch_application(self, data: Dict[str, Any]):
        """Launch GUI or CLI application."""
        mode = data.get('mode', 'gui')
        preset = data.get('preset')
        
        try:
            if mode == 'gui':
                cmd = [sys.executable, 'main.py']
                if preset:
                    cmd.extend(['--preset', preset])
                subprocess.Popen(cmd)
                response = {"status": "success", "message": f"Launched GUI mode with preset: {preset}"}
                
            elif mode == 'cli':
                cmd = [sys.executable, 'main.py', '--cli']
                subprocess.Popen(cmd)
                response = {"status": "success", "message": "Launched CLI mode"}
                
            else:
                self.send_error_response(400, f"Invalid mode: {mode}")
                return
                
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error_response(500, f"Failed to launch application: {e}")
    
    def modify_theme(self, data: Dict[str, Any]):
        """Modify current theme."""
        modified = False
        
        # Handle color modifications
        if 'colors' in data:
            if 'colors' not in self.theme_cli.current_theme:
                self.theme_cli.current_theme['colors'] = {}
                
            for element, color in data['colors'].items():
                # Ensure color is in the right format
                if not color.startswith('background-color:'):
                    color = f"background-color: {color}; border: 1px solid #444;"
                self.theme_cli.current_theme['colors'][element] = color
                modified = True
        
        # Handle font modifications
        if 'fonts' in data:
            if 'fonts' not in self.theme_cli.current_theme:
                self.theme_cli.current_theme['fonts'] = {}
                
            for category, font in data['fonts'].items():
                self.theme_cli.current_theme['fonts'][category] = font
                modified = True
        
        # Handle numeric modifications (sizes, etc.)
        if 'numeric' in data:
            if 'numeric' not in self.theme_cli.current_theme:
                self.theme_cli.current_theme['numeric'] = {}
                
            for key, value in data['numeric'].items():
                self.theme_cli.current_theme['numeric'][key] = value
                modified = True
        
        if modified:
            response = {
                "status": "success",
                "message": "Theme modified successfully",
                "theme": self.theme_cli.current_theme,
                "preview_css": self.theme_cli.generate_css()
            }
        else:
            response = {
                "status": "warning",
                "message": "No modifications applied",
                "theme": self.theme_cli.current_theme
            }
        
        self.send_json_response(response)
    
    def export_theme(self, data: Dict[str, Any]):
        """Export current theme."""
        filename = data.get('filename', 'exported_theme.qss')
        format_type = data.get('format', 'qss')
        
        try:
            filepath = Path('./themes') / filename
            filepath.parent.mkdir(exist_ok=True)
            
            if format_type == 'json':
                self.theme_cli.export_json(filepath)
            elif format_type in ['qss', 'css']:
                self.theme_cli.export_qss(filepath)
            else:
                self.send_error_response(400, f"Unsupported format: {format_type}")
                return
            
            # Read the exported content to return in response
            with open(filepath, 'r') as f:
                content = f.read()
            
            response = {
                "status": "success",
                "message": f"Theme exported to {filepath}",
                "filename": str(filepath),
                "format": format_type,
                "content": content
            }
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error_response(500, f"Export failed: {e}")
    
    def import_theme(self, data: Dict[str, Any]):
        """Import theme from data or file."""
        if 'theme_data' in data:
            # Import from inline data
            try:
                self.theme_cli.current_theme = data['theme_data']
                response = {
                    "status": "success",
                    "message": "Theme imported from inline data",
                    "theme": self.theme_cli.current_theme
                }
                self.send_json_response(response)
            except Exception as e:
                self.send_error_response(400, f"Invalid theme data: {e}")
                
        elif 'filename' in data:
            # Import from file
            filename = data['filename']
            filepath = Path(filename)
            
            if not filepath.exists():
                self.send_error_response(404, f"File not found: {filename}")
                return
            
            try:
                with open(filepath, 'r') as f:
                    theme_data = json.load(f)
                    
                self.theme_cli.current_theme = theme_data
                response = {
                    "status": "success",
                    "message": f"Theme imported from {filename}",
                    "theme": self.theme_cli.current_theme
                }
                self.send_json_response(response)
                
            except Exception as e:
                self.send_error_response(500, f"Import failed: {e}")
        else:
            self.send_error_response(400, "Missing 'theme_data' or 'filename' in request")
    
    def load_preset(self, data: Dict[str, Any]):
        """Load a preset theme."""
        preset_name = data.get('name')
        if not preset_name:
            self.send_error_response(400, "Missing 'name' parameter")
            return
        
        if preset_name not in self.theme_cli.presets:
            self.send_error_response(404, f"Preset '{preset_name}' not found")
            return
        
        self.theme_cli.current_theme = self.theme_cli.presets[preset_name].copy()
        response = {
            "status": "success",
            "message": f"Loaded preset: {preset_name}",
            "preset_name": preset_name,
            "theme": self.theme_cli.current_theme,
            "preview_css": self.theme_cli.generate_css()
        }
        self.send_json_response(response)
    
    def send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response."""
        response_body = json.dumps(data, indent=2).encode('utf-8')
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_body)))
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(response_body)
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response."""
        error_data = {
            "error": {
                "code": status_code,
                "message": message
            }
        }
        self.send_json_response(error_data, status_code)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format."""
        print(f"🌐 API [{self.log_date_time_string()}] {format % args}")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Threaded HTTP server for handling multiple requests."""
    allow_reuse_address = True

def start_webhook_server(host: str = 'localhost', port: int = 8080):
    """Start the webhook API server."""
    try:
        server = ThreadedHTTPServer((host, port), ThemeAPIHandler)
        print(f"""
🌐 ═══════════════════════════════════════════════════════════════════
   PyQt6 Theme Editor - API Server Started
   
   🔗 Base URL: http://{host}:{port}
   📋 API Docs: http://{host}:{port}/
   💚 Health Check: http://{host}:{port}/health
═══════════════════════════════════════════════════════════════════

🚀 Ready to accept requests...
        """)
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
        server.shutdown()
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_webhook_server() 