#!/usr/bin/env python3
"""
Batch Operations for PyQt6 Theme Editor
Mass conversion, export, and processing of themes
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import concurrent.futures
from datetime import datetime

def export_all_presets(output_dir: str = "./themes", format_type: str = "qss"):
    """Export all preset themes to files."""
    print(f"🚀 Starting batch export of all presets to {output_dir}")
    
    # Import CLI module to access presets
    from cli_mode import ThemeCLI
    cli = ThemeCLI()
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    exported_files = []
    errors = []
    
    for preset_name, theme_data in cli.presets.items():
        try:
            # Generate filename
            safe_name = preset_name.lower().replace(' ', '_').replace('-', '_')
            filename = f"{safe_name}.{format_type}"
            filepath = output_path / filename
            
            # Set current theme and export
            cli.current_theme = theme_data.copy()
            
            if format_type == 'json':
                cli.export_json(filepath)
            elif format_type in ['qss', 'css']:
                cli.export_qss(filepath)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            exported_files.append(str(filepath))
            print(f"✅ Exported: {preset_name} → {filepath}")
            
        except Exception as e:
            error_msg = f"Failed to export {preset_name}: {e}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    # Generate summary report
    generate_export_summary(output_path, exported_files, errors, format_type)
    
    print(f"\n📊 Export Summary:")
    print(f"   ✅ Successfully exported: {len(exported_files)} themes")
    print(f"   ❌ Errors: {len(errors)}")
    print(f"   📁 Output directory: {output_path.absolute()}")

def convert_theme_file(input_file: str, output_format: str, output_dir: str = "./themes"):
    """Convert a single theme file to different format."""
    input_path = Path(input_file)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    if not input_path.exists():
        print(f"❌ Input file not found: {input_file}")
        return False
    
    try:
        print(f"🔄 Converting {input_path} to {output_format}")
        
        # Load theme data
        if input_path.suffix.lower() == '.json':
            with open(input_path, 'r') as f:
                theme_data = json.load(f)
        else:
            print(f"❌ Only JSON input files are supported for conversion")
            return False
        
        # Generate output filename
        output_filename = input_path.stem + f".{output_format}"
        output_filepath = output_path / output_filename
        
        # Convert and save
        from cli_mode import ThemeCLI
        cli = ThemeCLI()
        cli.current_theme = theme_data
        
        if output_format == 'json':
            cli.export_json(output_filepath)
        elif output_format in ['qss', 'css']:
            cli.export_qss(output_filepath)
        else:
            print(f"❌ Unsupported output format: {output_format}")
            return False
        
        print(f"✅ Converted to: {output_filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return False

def batch_convert_directory(input_dir: str, output_format: str, output_dir: str = "./themes"):
    """Convert all theme files in a directory."""
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return
    
    # Find all JSON files
    json_files = list(input_path.glob("*.json"))
    if not json_files:
        print(f"⚠️  No JSON theme files found in {input_dir}")
        return
    
    print(f"🚀 Starting batch conversion of {len(json_files)} files")
    
    success_count = 0
    error_count = 0
    
    # Use concurrent processing for better performance
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(convert_theme_file, str(file), output_format, output_dir): file
            for file in json_files
        }
        
        for future in concurrent.futures.as_completed(futures):
            file = futures[future]
            try:
                if future.result():
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"❌ Error processing {file}: {e}")
                error_count += 1
    
    print(f"\n📊 Batch Conversion Summary:")
    print(f"   ✅ Successfully converted: {success_count} files")
    print(f"   ❌ Errors: {error_count}")

def generate_theme_library(output_dir: str = "./theme_library"):
    """Generate a comprehensive theme library with all formats."""
    print(f"📚 Generating comprehensive theme library in {output_dir}")
    
    library_path = Path(output_dir)
    library_path.mkdir(exist_ok=True)
    
    # Create subdirectories for different formats
    formats = {
        'json': library_path / 'json',
        'qss': library_path / 'qss',
        'css': library_path / 'css'
    }
    
    for format_dir in formats.values():
        format_dir.mkdir(exist_ok=True)
    
    # Export all presets in all formats
    for format_name, format_dir in formats.items():
        print(f"🎨 Exporting all themes as {format_name.upper()}")
        export_all_presets(str(format_dir), format_name)
    
    # Generate documentation
    generate_library_documentation(library_path)
    
    print(f"✅ Theme library generated at: {library_path.absolute()}")

def generate_export_summary(output_path: Path, exported_files: List[str], 
                           errors: List[str], format_type: str):
    """Generate a summary report for exports."""
    summary = {
        "export_info": {
            "timestamp": datetime.now().isoformat(),
            "format": format_type,
            "output_directory": str(output_path.absolute()),
            "total_themes": len(exported_files) + len(errors),
            "successful_exports": len(exported_files),
            "failed_exports": len(errors)
        },
        "exported_files": exported_files,
        "errors": errors
    }
    
    summary_file = output_path / f"export_summary_{format_type}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📄 Export summary saved to: {summary_file}")

def generate_library_documentation(library_path: Path):
    """Generate documentation for the theme library."""
    
    # Import CLI to get preset information
    from cli_mode import ThemeCLI
    cli = ThemeCLI()
    
    # Generate README
    readme_content = f"""# PyQt6 Theme Library

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This library contains all available themes for PyQt6 applications in multiple formats.

## 📁 Directory Structure

```
theme_library/
├── json/          # JSON theme configuration files
├── qss/           # Qt Stylesheet files
├── css/           # CSS files (for reference)
├── examples/      # Usage examples
└── README.md      # This file
```

## 🎨 Available Themes

{generate_theme_descriptions(cli.presets)}

## 🚀 Usage

### In PyQt6 Applications

```python
# Method 1: Load QSS file
app = QApplication(sys.argv)
with open('theme_library/qss/dark_sci_fi.qss', 'r') as f:
    app.setStyleSheet(f.read())

# Method 2: Use theme editor programmatically
from UI_Editor import StyleEditor
editor = StyleEditor()
editor.load_json_theme('theme_library/json/dark_sci_fi.json')
app.setStyleSheet(editor.generate_stylesheet())
```

### Using the CLI

```bash
# Apply a theme
python main.py --cli
> load-preset "Dark Sci-Fi"
> export my_custom.qss

# Batch operations
python main.py --batch-export --format qss --output ./my_themes/
```

### Using the API

```bash
# Get available themes
curl http://localhost:8080/api/presets

# Load a theme
curl -X POST http://localhost:8080/api/preset/load \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "Dark Sci-Fi"}}'

# Export current theme
curl -X POST http://localhost:8080/api/theme/export \\
  -H "Content-Type: application/json" \\
  -d '{{"filename": "my_theme.qss", "format": "qss"}}'
```

## 🎯 Integration Examples

### Web Dashboard
```javascript
// Fetch and apply theme via API
fetch('http://localhost:8080/api/preset?name=Dark%20Sci-Fi')
  .then(response => response.json())
  .then(data => {{
    console.log('Theme loaded:', data.theme);
  }});
```

### Python Scripts
```python
# Programmatic theme application
from main import ThemeEditorMainWindow
import sys
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
theme_editor = ThemeEditorMainWindow()
theme_editor.style_editor.load_preset_theme("Dark Sci-Fi")
app.setStyleSheet(theme_editor.style_editor.generate_stylesheet())
```

## 📝 Theme Format Reference

### JSON Format
JSON files contain the complete theme configuration including colors, fonts, and numeric values.

### QSS Format
Qt Stylesheet files ready to use with `setStyleSheet()` method.

### CSS Format
Standard CSS files for reference and web applications.

## 🔧 Customization

All themes can be customized using:
- The GUI editor: `python main.py`
- The CLI: `python main.py --cli`
- The REST API: `python main.py --webhook`

Generated by PyQt6 Theme Editor v1.0.0
"""
    
    readme_file = library_path / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    # Generate usage examples
    examples_dir = library_path / "examples"
    examples_dir.mkdir(exist_ok=True)
    
    # Basic usage example
    basic_example = """#!/usr/bin/env python3
'''
Basic PyQt6 Theme Application Example
Shows how to use themes from the theme library
'''

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel

class ThemedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Themed Application")
        self.setGeometry(100, 100, 600, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Sample widgets
        layout.addWidget(QLabel("Welcome to the Themed Application!"))
        layout.addWidget(QPushButton("Primary Button"))
        layout.addWidget(QPushButton("Secondary Button"))
        
    def load_theme(self, theme_file):
        '''Load a theme from the library'''
        try:
            with open(theme_file, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Failed to load theme: {e}")

def main():
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = ThemedApp()
    
    # Load a theme (change this path to test different themes)
    window.load_theme('../qss/dark_sci_fi.qss')
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
"""
    
    with open(examples_dir / "basic_usage.py", 'w') as f:
        f.write(basic_example)
    
    print(f"📚 Documentation generated at: {readme_file}")

def generate_theme_descriptions(presets: Dict[str, Any]) -> str:
    """Generate descriptions for all themes."""
    descriptions = []
    
    theme_info = {
        "Dark Sci-Fi": "Futuristic dark theme with neon accents. Perfect for tech applications.",
        "Light Modern": "Clean, modern light theme with subtle shadows and crisp typography.",
        "Material Dark": "Google Material Design dark theme with purple accents.",
        "Material Light": "Google Material Design light theme with clean aesthetics.",
        "Cyberpunk": "High-contrast neon theme inspired by cyberpunk aesthetics.",
        "Minimalist": "Ultra-clean minimal theme focusing on typography and whitespace.",
        "Corporate Blue": "Professional blue theme suitable for business applications.",
        "Nature Green": "Calm green theme inspired by nature and organic forms."
    }
    
    for preset_name in presets.keys():
        desc = theme_info.get(preset_name, "Custom theme with unique styling.")
        safe_name = preset_name.lower().replace(' ', '_').replace('-', '_')
        descriptions.append(f"- **{preset_name}** (`{safe_name}.*`): {desc}")
    
    return "\\n".join(descriptions)

def validate_theme_files(directory: str) -> Dict[str, Any]:
    """Validate theme files in a directory."""
    print(f"🔍 Validating theme files in {directory}")
    
    dir_path = Path(directory)
    if not dir_path.exists():
        return {"error": f"Directory not found: {directory}"}
    
    results = {
        "valid_files": [],
        "invalid_files": [],
        "missing_fields": [],
        "total_files": 0
    }
    
    # Check JSON files
    json_files = list(dir_path.glob("*.json"))
    results["total_files"] = len(json_files)
    
    required_fields = ["colors", "fonts", "numeric"]
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                theme_data = json.load(f)
            
            missing = [field for field in required_fields if field not in theme_data]
            
            if missing:
                results["missing_fields"].append({
                    "file": str(json_file),
                    "missing": missing
                })
            else:
                results["valid_files"].append(str(json_file))
                
        except Exception as e:
            results["invalid_files"].append({
                "file": str(json_file),
                "error": str(e)
            })
    
    # Print summary
    print(f"✅ Valid files: {len(results['valid_files'])}")
    print(f"⚠️  Files with missing fields: {len(results['missing_fields'])}")
    print(f"❌ Invalid files: {len(results['invalid_files'])}")
    
    return results

if __name__ == "__main__":
    # Example usage
    print("🎨 PyQt6 Theme Editor - Batch Operations")
    print("Available operations:")
    print("1. Export all presets")
    print("2. Generate theme library")
    print("3. Validate themes")
    
    choice = input("Select operation (1-3): ").strip()
    
    if choice == "1":
        format_type = input("Format (json/qss/css) [qss]: ").strip() or "qss"
        output_dir = input("Output directory [./themes]: ").strip() or "./themes"
        export_all_presets(output_dir, format_type)
        
    elif choice == "2":
        output_dir = input("Library directory [./theme_library]: ").strip() or "./theme_library"
        generate_theme_library(output_dir)
        
    elif choice == "3":
        directory = input("Directory to validate [./themes]: ").strip() or "./themes"
        validate_theme_files(directory)
        
    else:
        print("Invalid choice") 