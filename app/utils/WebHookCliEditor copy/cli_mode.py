#!/usr/bin/env python3
"""
CLI Mode for PyQt6 Theme Editor
Interactive command-line interface for theme creation and modification
"""

import json
import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

class ThemeCLI:
    """Interactive CLI for theme editing."""
    
    def __init__(self):
        self.current_theme = self.get_default_theme()
        self.presets = {
            "Dark Sci-Fi": self.get_dark_scifi_preset(),
            "Light Modern": self.get_light_modern_preset(),
            "Material Dark": self.get_material_dark_preset(),
            "Material Light": self.get_material_light_preset(),
            "Cyberpunk": self.get_cyberpunk_preset(),
            "Minimalist": self.get_minimalist_preset(),
            "Corporate Blue": self.get_corporate_blue_preset(),
            "Nature Green": self.get_nature_green_preset(),
        }
        self.output_dir = Path("./themes")
        self.output_dir.mkdir(exist_ok=True)
        
    def run(self):
        """Start the interactive CLI session."""
        self.print_welcome()
        
        while True:
            try:
                command = input("\n🎨 theme> ").strip().lower()
                if not command:
                    continue
                    
                if command in ['exit', 'quit', 'q']:
                    print("👋 Thanks for using PyQt6 Theme Editor!")
                    break
                elif command in ['help', 'h', '?']:
                    self.print_help()
                elif command == 'list-presets':
                    self.list_presets()
                elif command.startswith('load-preset '):
                    preset_name = command[12:].strip('"\'')
                    self.load_preset(preset_name)
                elif command.startswith('set-color '):
                    self.handle_set_color(command)
                elif command.startswith('set-font '):
                    self.handle_set_font(command)
                elif command.startswith('set-size '):
                    self.handle_set_size(command)
                elif command == 'show-colors':
                    self.show_current_colors()
                elif command == 'show-fonts':
                    self.show_current_fonts()
                elif command == 'show-theme':
                    self.show_current_theme()
                elif command.startswith('export '):
                    self.handle_export(command)
                elif command.startswith('import '):
                    self.handle_import(command)
                elif command == 'preview':
                    self.generate_preview()
                elif command == 'reset':
                    self.reset_theme()
                else:
                    print(f"❌ Unknown command: {command}")
                    print("💡 Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def print_welcome(self):
        """Print welcome message and basic info."""
        print("""
🎨 ═══════════════════════════════════════════════════════════════════
   PyQt6 Theme Editor - Interactive CLI Mode
   Create, modify, and export themes for Qt applications
═══════════════════════════════════════════════════════════════════

💡 Type 'help' to see available commands
🚀 Current theme: Default
        """)
    
    def print_help(self):
        """Print available commands."""
        print("""
📋 Available Commands:

🏷️  Theme Management:
   list-presets                    List all available preset themes
   load-preset "Theme Name"        Load a preset theme
   show-theme                      Show current theme configuration
   reset                          Reset to default theme
   
🎨 Color Modification:
   set-color <element> <#color>    Set color for theme element
   show-colors                     Show all current colors
   
   Elements: Background, Foreground, Primary, Secondary, Accent,
            Error, Warning, Success, Info, Link, Selection_Bg, etc.
   
🔤 Font Modification:
   set-font <category> <font>      Set font family
   set-size <category> <size>      Set font size
   show-fonts                      Show current font settings
   
   Categories: Default, Heading, Body, Monospace, Display, H1-H6
   
💾 Import/Export:
   export <filename> [format]      Export theme (json/qss/css)
   import <filename>               Import theme from file
   preview                         Generate CSS preview
   
🔧 Utility:
   help, h, ?                      Show this help
   exit, quit, q                   Exit CLI mode

📝 Examples:
   set-color Primary #00FFAA
   set-font Heading "Arial"
   set-size H1 24
   load-preset "Dark Sci-Fi"
   export my_theme.qss
        """)
    
    def list_presets(self):
        """List all available preset themes."""
        print("\n🎭 Available Preset Themes:")
        for i, name in enumerate(self.presets.keys(), 1):
            print(f"   {i:2}. {name}")
        print(f"\n💡 Use: load-preset \"Theme Name\" to load a preset")
    
    def load_preset(self, preset_name: str):
        """Load a preset theme."""
        # Try exact match first
        if preset_name in self.presets:
            self.current_theme = self.presets[preset_name].copy()
            print(f"✅ Loaded preset: {preset_name}")
            return
            
        # Try case-insensitive match
        for name, theme in self.presets.items():
            if name.lower() == preset_name.lower():
                self.current_theme = theme.copy()
                print(f"✅ Loaded preset: {name}")
                return
                
        print(f"❌ Preset '{preset_name}' not found")
        print(f"💡 Available presets: {', '.join(self.presets.keys())}")
    
    def handle_set_color(self, command: str):
        """Handle set-color command."""
        parts = command.split()
        if len(parts) != 3:
            print("❌ Usage: set-color <element> <#color>")
            print("📝 Example: set-color Primary #00FFAA")
            return
            
        _, element, color = parts
        
        # Validate color format
        if not (color.startswith('#') and len(color) in [4, 7]):
            print("❌ Color must be in format #RGB or #RRGGBB")
            return
            
        # Convert element name to match internal format
        element_key = element.replace('_', ' ').title()
        
        if 'colors' not in self.current_theme:
            self.current_theme['colors'] = {}
            
        self.current_theme['colors'][element_key] = f"background-color: {color}; border: 1px solid #444;"
        print(f"✅ Set {element_key} color to {color}")
    
    def handle_set_font(self, command: str):
        """Handle set-font command."""
        parts = command.split(maxsplit=2)
        if len(parts) != 3:
            print("❌ Usage: set-font <category> <font_name>")
            print("📝 Example: set-font Heading \"Arial\"")
            return
            
        _, category, font_name = parts
        font_name = font_name.strip('"\'')
        
        if 'fonts' not in self.current_theme:
            self.current_theme['fonts'] = {}
            
        self.current_theme['fonts'][category] = font_name
        print(f"✅ Set {category} font to {font_name}")
    
    def handle_set_size(self, command: str):
        """Handle set-size command."""
        parts = command.split()
        if len(parts) != 3:
            print("❌ Usage: set-size <category> <size>")
            print("📝 Example: set-size H1 24")
            return
            
        _, category, size_str = parts
        
        try:
            size = int(size_str)
            if size < 6 or size > 72:
                print("❌ Size must be between 6 and 72")
                return
        except ValueError:
            print("❌ Size must be a number")
            return
            
        if 'numeric' not in self.current_theme:
            self.current_theme['numeric'] = {}
            
        self.current_theme['numeric'][f'font_size_{category}'] = size
        print(f"✅ Set {category} font size to {size}px")
    
    def show_current_colors(self):
        """Show current color configuration."""
        colors = self.current_theme.get('colors', {})
        if not colors:
            print("🎨 No custom colors set")
            return
            
        print("\n🎨 Current Colors:")
        for element, style in colors.items():
            # Extract color from style string
            color = style.split('background-color:')[1].split(';')[0].strip()
            print(f"   {element:15} {color}")
    
    def show_current_fonts(self):
        """Show current font configuration."""
        fonts = self.current_theme.get('fonts', {})
        sizes = self.current_theme.get('numeric', {})
        
        print("\n🔤 Current Fonts:")
        if fonts:
            print("   Font Families:")
            for category, font in fonts.items():
                print(f"     {category:15} {font}")
                
        size_entries = {k: v for k, v in sizes.items() if k.startswith('font_size_')}
        if size_entries:
            print("   Font Sizes:")
            for key, size in size_entries.items():
                category = key.replace('font_size_', '')
                print(f"     {category:15} {size}px")
    
    def show_current_theme(self):
        """Show complete current theme."""
        print("\n🎭 Current Theme Configuration:")
        print(json.dumps(self.current_theme, indent=2))
    
    def handle_export(self, command: str):
        """Handle export command."""
        parts = command.split()
        if len(parts) < 2:
            print("❌ Usage: export <filename> [format]")
            print("📝 Example: export my_theme.qss")
            return
            
        filename = parts[1]
        format_type = parts[2] if len(parts) > 2 else self.get_format_from_extension(filename)
        
        filepath = self.output_dir / filename
        
        try:
            if format_type == 'json':
                self.export_json(filepath)
            elif format_type in ['qss', 'css']:
                self.export_qss(filepath)
            else:
                print(f"❌ Unsupported format: {format_type}")
                return
                
            print(f"✅ Exported theme to {filepath}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def handle_import(self, command: str):
        """Handle import command."""
        parts = command.split()
        if len(parts) != 2:
            print("❌ Usage: import <filename>")
            return
            
        filename = parts[1]
        filepath = Path(filename)
        
        if not filepath.exists():
            print(f"❌ File not found: {filename}")
            return
            
        try:
            with open(filepath, 'r') as f:
                if filename.endswith('.json'):
                    self.current_theme = json.load(f)
                    print(f"✅ Imported theme from {filename}")
                else:
                    print("❌ Only JSON import is currently supported")
                    
        except Exception as e:
            print(f"❌ Import failed: {e}")
    
    def generate_preview(self):
        """Generate and display CSS preview."""
        css = self.generate_css()
        print("\n🔍 Generated CSS Preview:")
        print("─" * 50)
        print(css)
        print("─" * 50)
    
    def reset_theme(self):
        """Reset to default theme."""
        self.current_theme = self.get_default_theme()
        print("✅ Reset to default theme")
    
    def export_json(self, filepath: Path):
        """Export theme as JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.current_theme, f, indent=2)
    
    def export_qss(self, filepath: Path):
        """Export theme as QSS/CSS."""
        css = self.generate_css()
        with open(filepath, 'w') as f:
            f.write(css)
    
    def generate_css(self) -> str:
        """Generate CSS from current theme."""
        # This is a simplified version - in practice, you'd use the same
        # generation logic as the GUI version
        colors = self.current_theme.get('colors', {})
        fonts = self.current_theme.get('fonts', {})
        
        css_parts = []
        
        # Basic widget styles
        bg_color = self.extract_color(colors.get('Background', '#121212'))
        fg_color = self.extract_color(colors.get('Foreground', '#EEEEEE'))
        primary_color = self.extract_color(colors.get('Primary', '#00FFAA'))
        
        css_parts.append(f"""QWidget {{
    background-color: {bg_color};
    color: {fg_color};
}}

QPushButton {{
    background-color: {primary_color};
    border: 2px solid #444;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {self.lighten_color(primary_color)};
}}""")
        
        return "\n\n".join(css_parts)
    
    def extract_color(self, style_or_color: str) -> str:
        """Extract color value from style string or return as-is."""
        if 'background-color:' in style_or_color:
            return style_or_color.split('background-color:')[1].split(';')[0].strip()
        return style_or_color
    
    def lighten_color(self, color: str) -> str:
        """Simple color lightening (placeholder)."""
        # This is a simplified version - you'd implement proper color manipulation
        return color
    
    def get_format_from_extension(self, filename: str) -> str:
        """Get format from file extension."""
        ext = Path(filename).suffix.lower()
        if ext == '.json':
            return 'json'
        elif ext in ['.qss', '.css']:
            return 'qss'
        return 'qss'  # default
    
    # Preset theme definitions (simplified versions)
    def get_default_theme(self) -> Dict[str, Any]:
        return {
            'colors': {
                'Background': 'background-color: #FFFFFF; border: 1px solid #444;',
                'Foreground': 'background-color: #000000; border: 1px solid #444;',
                'Primary': 'background-color: #007ACC; border: 1px solid #444;',
            },
            'fonts': {
                'Default': 'System Default'
            },
            'numeric': {
                'font_size_Base Size': 12
            }
        }
    
    def get_dark_scifi_preset(self) -> Dict[str, Any]:
        return {
            'colors': {
                'Background': 'background-color: #121212; border: 1px solid #444;',
                'Foreground': 'background-color: #EEEEEE; border: 1px solid #444;',
                'Primary': 'background-color: #00FFAA; border: 1px solid #444;',
                'Secondary': 'background-color: #FF4500; border: 1px solid #444;',
                'Accent': 'background-color: #FFD700; border: 1px solid #444;',
            }
        }
    
    def get_light_modern_preset(self) -> Dict[str, Any]:
        return {
            'colors': {
                'Background': 'background-color: #FFFFFF; border: 1px solid #444;',
                'Foreground': 'background-color: #333333; border: 1px solid #444;',
                'Primary': 'background-color: #2196F3; border: 1px solid #444;',
            }
        }
    
    def get_material_dark_preset(self) -> Dict[str, Any]:
        return {
            'colors': {
                'Background': 'background-color: #212121; border: 1px solid #444;',
                'Foreground': 'background-color: #FFFFFF; border: 1px solid #444;',
                'Primary': 'background-color: #BB86FC; border: 1px solid #444;',
            }
        }
    
    def get_material_light_preset(self) -> Dict[str, Any]:
        return {
            'colors': {
                'Background': 'background-color: #FAFAFA; border: 1px solid #444;',
                'Primary': 'background-color: #6200EE; border: 1px solid #444;',
            }
        }
    
    def get_cyberpunk_preset(self) -> Dict[str, Any]:
        return {
            'colors': {
                'Background': 'background-color: #0A0A0A; border: 1px solid #444;',
                'Primary': 'background-color: #00FFFF; border: 1px solid #444;',
            }
        }
    
    def get_minimalist_preset(self) -> Dict[str, Any]:
        return {
            'colors': {
                'Background': 'background-color: #F5F5F5; border: 1px solid #444;',
                'Primary': 'background-color: #000000; border: 1px solid #444;',
            }
        }
    
    def get_corporate_blue_preset(self) -> Dict[str, Any]:
        return {
            'colors': {
                'Background': 'background-color: #F0F4F8; border: 1px solid #444;',
                'Primary': 'background-color: #2B6CB0; border: 1px solid #444;',
            }
        }
    
    def get_nature_green_preset(self) -> Dict[str, Any]:
        return {
            'colors': {
                'Background': 'background-color: #F7FAFC; border: 1px solid #444;',
                'Primary': 'background-color: #48BB78; border: 1px solid #444;',
            }
        } 