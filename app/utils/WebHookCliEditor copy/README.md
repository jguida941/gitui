# PyQt6 Theme Editor 🎨

A **complete no-code solution** for creating, editing, and deploying themes for PyQt6 applications. Features multiple operation modes, real-time preview, and comprehensive export capabilities.

![PyQt6 Theme Editor](https://img.shields.io/badge/PyQt6-Theme%20Editor-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## 🚀 Features

### 🎯 **Multi-Mode Operation**
- **GUI Mode**: Full-featured visual editor with live preview
- **CLI Mode**: Interactive command-line interface for automation
- **API Mode**: REST API for remote operations and integration
- **Batch Mode**: Mass export and conversion of themes

### 🎨 **Comprehensive Theme Editing**
- **8+ Built-in Presets**: Dark Sci-Fi, Material Design, Cyberpunk, and more
- **Real-time Preview**: See changes instantly across all widget types
- **Complete Coverage**: Buttons, inputs, tables, trees, sliders, progress bars
- **Advanced Effects**: Shadows, transitions, transforms, and filters
- **Typography Control**: Fonts, sizes, weights, spacing, and text effects

### 📤 **Export & Integration**
- **Multiple Formats**: JSON, QSS (Qt Stylesheet), CSS
- **Batch Operations**: Export all presets simultaneously
- **Theme Library Generation**: Complete documented theme collections
- **API Integration**: Use themes via REST endpoints

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd pyqt6-theme-editor

# Install dependencies
pip install PyQt6

# Run the application
python main.py
```

## 🎮 Usage

### 1. GUI Mode (Default)

```bash
# Launch the visual editor
python main.py

# Launch with a specific preset
python main.py --preset "Dark Sci-Fi"
```

**Features:**
- Tabbed interface for all theme properties
- Live preview with comprehensive widget examples
- Color pickers, font selectors, and numeric controls
- Real-time CSS generation and export
- Undo/redo functionality

### 2. CLI Mode

```bash
# Enter interactive CLI
python main.py --cli
```

**Available Commands:**
```bash
🎨 theme> list-presets              # Show all available themes
🎨 theme> load-preset "Dark Sci-Fi" # Load a preset theme
🎨 theme> set-color Primary #FF6B35 # Modify colors
🎨 theme> set-font Heading "Arial"  # Change fonts
🎨 theme> set-size H1 24            # Adjust font sizes
🎨 theme> show-colors               # Display current colors
🎨 theme> preview                   # Generate CSS preview
🎨 theme> export my_theme.qss       # Export theme
🎨 theme> help                      # Show all commands
```

### 3. REST API Mode

```bash
# Start the API server
python main.py --webhook --port 8080
```

**API Endpoints:**

```bash
# Get API information
curl http://localhost:8080/

# List available presets
curl http://localhost:8080/api/presets

# Load a preset
curl -X POST http://localhost:8080/api/preset/load \
  -H "Content-Type: application/json" \
  -d '{"name": "Dark Sci-Fi"}'

# Modify theme colors
curl -X POST http://localhost:8080/api/theme/modify \
  -H "Content-Type: application/json" \
  -d '{"colors": {"Primary": "#FF6B35"}}'

# Export current theme
curl -X POST http://localhost:8080/api/theme/export \
  -H "Content-Type: application/json" \
  -d '{"filename": "my_theme.qss", "format": "qss"}'
```

### 4. Batch Operations

```bash
# Export all presets as QSS files
python main.py --batch-export --format qss --output ./themes

# Export all presets as JSON
python main.py --batch-export --format json --output ./themes

# Convert a single theme file
python main.py --convert my_theme.json --format qss
```

## 🎨 Available Themes

| Theme | Description | Best For |
|-------|-------------|----------|
| **Dark Sci-Fi** | Futuristic dark theme with neon accents | Tech/Gaming applications |
| **Light Modern** | Clean, modern light theme | Professional software |
| **Material Dark** | Google Material Design dark | Android-style apps |
| **Material Light** | Google Material Design light | Web-like interfaces |
| **Cyberpunk** | High-contrast neon theme | Creative/Entertainment |
| **Minimalist** | Ultra-clean minimal design | Focus-driven apps |
| **Corporate Blue** | Professional blue theme | Business applications |
| **Nature Green** | Calm green organic theme | Health/Environment apps |

## 📁 Project Structure

```
pyqt6-theme-editor/
├── main.py              # Multi-mode entry point
├── UI_Editor.py         # Main GUI theme editor
├── cli_mode.py          # Interactive CLI interface
├── webhook_api.py       # REST API server
├── batch_operations.py  # Mass export/conversion
├── test_cli.py         # CLI functionality tests
├── demo_themes/        # Generated theme files
│   ├── dark_sci_fi.qss
│   ├── material_dark.qss
│   └── ...
└── README.md           # This file
```

## 🔧 Integration Examples

### Using in PyQt6 Applications

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themed Application")
        
    def load_theme(self, theme_file):
        with open(theme_file, 'r') as f:
            self.setStyleSheet(f.read())

# Apply a theme
app = QApplication(sys.argv)
window = MyApp()
window.load_theme('demo_themes/dark_sci_fi.qss')
window.show()
```

### Programmatic Theme Generation

```python
from cli_mode import ThemeCLI

# Create and customize a theme
cli = ThemeCLI()
cli.load_preset("Dark Sci-Fi")
cli.current_theme['colors']['Primary'] = "background-color: #FF6B35; border: 1px solid #444;"

# Export the customized theme
cli.export_qss(Path("./my_custom_theme.qss"))
```

### Web Integration

```javascript
// Fetch themes via API
fetch('http://localhost:8080/api/presets')
  .then(response => response.json())
  .then(data => {
    console.log('Available themes:', data.presets);
  });

// Apply a theme
fetch('http://localhost:8080/api/preset/load', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({name: 'Dark Sci-Fi'})
});
```

## 🎯 Use Cases

### For Developers
- **Rapid Prototyping**: Create professional themes in minutes
- **Consistent Branding**: Maintain visual consistency across applications
- **Theme Libraries**: Build and maintain collections of reusable themes

### For Teams
- **Collaboration**: Share themes via JSON files or API
- **Automation**: Integrate theme generation into CI/CD pipelines
- **Version Control**: Track theme changes with JSON exports

### For Businesses
- **White Labeling**: Customize applications for different clients
- **Brand Compliance**: Ensure applications match corporate guidelines
- **User Preferences**: Offer multiple theme options to users

## 🛠️ Advanced Features

### Real-time CSS Generation
The editor generates optimized CSS that includes:
- Widget-specific styles for all PyQt6 components
- State-based styling (hover, pressed, disabled)
- Advanced effects (shadows, transitions, transforms)
- Responsive design considerations

### Comprehensive Widget Support
Supports styling for:
- Basic widgets (buttons, labels, inputs)
- Complex widgets (tables, trees, tabs)
- Container widgets (group boxes, frames)
- Specialty widgets (progress bars, sliders)

### Export Options
- **QSS Files**: Ready-to-use Qt stylesheets
- **JSON Files**: Complete theme configurations
- **CSS Files**: Web-compatible stylesheets
- **Documentation**: Auto-generated usage guides

## 🌐 API Reference

### GET Endpoints
- `GET /` - API documentation
- `GET /api/presets` - List available presets
- `GET /api/preset?name=<name>` - Get specific preset
- `GET /api/theme/current` - Get current theme
- `GET /health` - Health check

### POST Endpoints
- `POST /api/launch` - Launch GUI/CLI mode
- `POST /api/theme/modify` - Modify current theme
- `POST /api/theme/export` - Export theme
- `POST /api/theme/import` - Import theme
- `POST /api/preset/load` - Load preset

## 🔮 Future Enhancements

- [ ] Visual theme inheritance and composition
- [ ] Animation timeline editor
- [ ] Theme marketplace integration
- [ ] Real-time collaborative editing
- [ ] Mobile app companion
- [ ] Plugin system for custom widgets
- [ ] Advanced color theory tools
- [ ] Accessibility compliance checking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PyQt6 team for the excellent GUI framework
- Material Design team for design inspiration
- Open source community for various theme concepts

---

**Made with ❤️ for the PyQt6 community**

*Turn your applications from functional to phenomenal with professional themes!* 