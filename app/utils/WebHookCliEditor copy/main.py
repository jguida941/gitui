#!/usr/bin/env python3
"""
PyQt6 Theme Editor - Multi-Mode Application
Supports GUI mode, CLI mode, and webhook API mode
"""

import sys
import argparse
from PyQt6.QtWidgets import QApplication
from UI_Editor import ThemeEditorMainWindow
from cli_mode import ThemeCLI
from webhook_api import start_webhook_server

def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="PyQt6 Theme Editor - Create and export themes for Qt applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Launch GUI mode
  python main.py --cli                     # Launch interactive CLI
  python main.py --preset "Dark Sci-Fi"   # Load preset in GUI
  python main.py --batch-export            # Export all presets
  python main.py --webhook                 # Start webhook API server
  python main.py --convert theme.json     # Convert theme to QSS
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--cli', action='store_true',
                           help='Launch interactive CLI mode')
    mode_group.add_argument('--webhook', action='store_true',
                           help='Start webhook API server')
    mode_group.add_argument('--batch-export', action='store_true',
                           help='Export all preset themes')
    
    # Theme operations
    parser.add_argument('--preset', type=str,
                       help='Load specific preset theme')
    parser.add_argument('--convert', type=str,
                       help='Convert theme file to different format')
    parser.add_argument('--format', choices=['json', 'qss', 'css'], default='qss',
                       help='Output format for conversion')
    parser.add_argument('--output', type=str, default='./themes/',
                       help='Output directory for exports')
    
    # Server options
    parser.add_argument('--host', default='localhost',
                       help='Webhook server host')
    parser.add_argument('--port', type=int, default=8080,
                       help='Webhook server port')
    
    return parser

def main():
    """Main application entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        if args.cli:
            # Launch CLI mode
            cli = ThemeCLI()
            cli.run()
            
        elif args.webhook:
            # Start webhook API server
            print(f"Starting webhook server on {args.host}:{args.port}")
            start_webhook_server(args.host, args.port)
            
        elif args.batch_export:
            # Batch export all presets
            from batch_operations import export_all_presets
            export_all_presets(args.output, args.format)
            
        elif args.convert:
            # Convert single theme file
            from batch_operations import convert_theme_file
            convert_theme_file(args.convert, args.format, args.output)
            
        else:
            # Launch GUI mode (default)
            app = QApplication(sys.argv)
            app.setApplicationName("PyQt6 Theme Editor")
            app.setApplicationVersion("1.0.0")
            
            window = ThemeEditorMainWindow()
            
            # Load preset if specified
            if args.preset:
                window.style_editor.load_preset_theme(args.preset)
                
            window.show()
            sys.exit(app.exec())
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 