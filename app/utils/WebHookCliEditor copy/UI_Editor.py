import sys
import json
from typing import Dict, List, Tuple, Optional, Any
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QBrush, QPen,
    QLinearGradient, QRadialGradient, QConicalGradient, QGradient
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QGroupBox, QPushButton, QLabel, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QLineEdit, QTextEdit, QListWidget,
    QColorDialog, QFontComboBox, QSlider, QScrollArea, QFrame,
    QFileDialog, QMessageBox, QInputDialog, QListWidgetItem,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy, QButtonGroup,
    QRadioButton, QMenu, QToolBar, QDockWidget, QMainWindow,
    QProgressBar
)
from PyQt6.QtCore import (
    Qt, QSettings, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QPoint, QSize, QRect, pyqtProperty, QDateTime
)


class StyleEditor(QWidget):
    """Complete PyQt6 Theme Editor - A no-code solution for creating and editing PyQt6 themes."""

    style_changed = pyqtSignal(str)  # Emits the CSS when style changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Initialize theme components
        self.theme_components = {
            'colors': {},
            'gradients': {},
            'fonts': {},
            'borders': {},
            'spacing': {},
            'effects': {},
            'animations': {},
            'states': {},
            'custom_properties': {}
        }

        # Widget-specific styles
        self.widget_styles = {}

        # Initialize UI elements storage
        self.color_pickers = {}
        self.gradient_editors = {}
        self.font_selectors = {}
        self.numeric_inputs = {}
        self.checkboxes = {}
        self.combo_boxes = {}

        # Live preview widget
        self.preview_widget = None
        self.live_preview = True

        # Undo/Redo stack
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_levels = 50

        # Initialize settings
        self.settings = QSettings("ThemeEditor", "StyleEditor")

        # Set up the UI
        self.setup_ui()

        # Load default theme
        self.load_default_theme()

        # Apply initial dark sci-fi theme
        self.apply_dark_scifi_theme()

    def setup_ui(self):
        """Set up the complete user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create toolbar
        toolbar_layout = self.create_toolbar()
        main_layout.addLayout(toolbar_layout)

        # Create main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)

        # Create main tabs
        self.main_tabs = QTabWidget()
        self.main_tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Add all editor tabs
        self.create_global_styles_tab()
        self.create_widget_styles_tab()
        self.create_colors_tab()
        self.create_typography_tab()
        self.create_spacing_tab()
        self.create_borders_tab()
        self.create_effects_tab()
        self.create_animations_tab()
        self.create_advanced_tab()
        self.create_import_export_tab()

        editor_layout.addWidget(self.main_tabs)
        splitter.addWidget(editor_widget)

        # Right side - Live Preview
        preview_widget = self.create_preview_panel()
        splitter.addWidget(preview_widget)

        # Set splitter sizes (60% editor, 40% preview)
        splitter.setSizes([600, 400])

        main_layout.addWidget(splitter)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background: #1a1a1a; color: #00ff88;")
        main_layout.addWidget(self.status_label)

    def create_toolbar(self) -> QHBoxLayout:
        """Create the main toolbar."""
        toolbar = QHBoxLayout()

        # File operations
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new_theme)

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_theme)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_theme)

        save_as_btn = QPushButton("Save As")
        save_as_btn.clicked.connect(self.save_theme_as)

        # Edit operations
        undo_btn = QPushButton("↶ Undo")
        undo_btn.clicked.connect(self.undo)

        redo_btn = QPushButton("↷ Redo")
        redo_btn.clicked.connect(self.redo)

        # Preview toggle
        self.preview_toggle = QCheckBox("Live Preview")
        self.preview_toggle.setChecked(True)
        self.preview_toggle.toggled.connect(self.toggle_preview)

        # Theme presets
        preset_combo = QComboBox()
        preset_combo.addItems([
            "Dark Sci-Fi", "Light Modern", "Material Dark",
            "Material Light", "Cyberpunk", "Minimalist",
            "Corporate Blue", "Nature Green", "Custom"
        ])
        preset_combo.currentTextChanged.connect(self.load_preset_theme)

        # Add to toolbar
        toolbar.addWidget(new_btn)
        toolbar.addWidget(open_btn)
        toolbar.addWidget(save_btn)
        toolbar.addWidget(save_as_btn)
        toolbar.addWidget(QLabel(" | "))
        toolbar.addWidget(undo_btn)
        toolbar.addWidget(redo_btn)
        toolbar.addWidget(QLabel(" | "))
        toolbar.addWidget(self.preview_toggle)
        toolbar.addWidget(QLabel(" | "))
        toolbar.addWidget(QLabel("Preset:"))
        toolbar.addWidget(preset_combo)
        toolbar.addStretch()
        
        # Store preset combo for later access
        self.preset_combo = preset_combo

        return toolbar

    def create_global_styles_tab(self):
        """Create the global styles configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Application-wide settings
        app_group = QGroupBox("Application Settings")
        app_layout = QGridLayout()

        # Window properties
        app_layout.addWidget(QLabel("Window Opacity:"), 0, 0)
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(50, 100)
        opacity_slider.setValue(100)
        opacity_slider.valueChanged.connect(self.update_preview)
        app_layout.addWidget(opacity_slider, 0, 1)

        # Default margins
        app_layout.addWidget(QLabel("Default Margin:"), 1, 0)
        margin_spin = QSpinBox()
        margin_spin.setRange(0, 50)
        margin_spin.setValue(8)
        margin_spin.valueChanged.connect(self.update_preview)
        self.numeric_inputs['default_margin'] = margin_spin
        app_layout.addWidget(margin_spin, 1, 1)

        # Default spacing
        app_layout.addWidget(QLabel("Default Spacing:"), 2, 0)
        spacing_spin = QSpinBox()
        spacing_spin.setRange(0, 50)
        spacing_spin.setValue(6)
        spacing_spin.valueChanged.connect(self.update_preview)
        self.numeric_inputs['default_spacing'] = spacing_spin
        app_layout.addWidget(spacing_spin, 2, 1)

        app_group.setLayout(app_layout)
        scroll_layout.addWidget(app_group)

        # Inheritance settings
        inherit_group = QGroupBox("Style Inheritance")
        inherit_layout = QVBoxLayout()

        self.inherit_colors = QCheckBox("Inherit parent colors")
        self.inherit_colors.setChecked(True)
        self.inherit_fonts = QCheckBox("Inherit parent fonts")
        self.inherit_fonts.setChecked(True)
        self.inherit_spacing = QCheckBox("Inherit parent spacing")
        self.inherit_spacing.setChecked(True)

        inherit_layout.addWidget(self.inherit_colors)
        inherit_layout.addWidget(self.inherit_fonts)
        inherit_layout.addWidget(self.inherit_spacing)

        inherit_group.setLayout(inherit_layout)
        scroll_layout.addWidget(inherit_group)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.main_tabs.addTab(tab, "Global Styles")

    def create_widget_styles_tab(self):
        """Create widget-specific styles tab."""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Widget selector
        widget_list = QListWidget()
        widget_list.setMaximumWidth(200)
        widgets = [
            "QWidget", "QPushButton", "QLabel", "QLineEdit", "QTextEdit",
            "QComboBox", "QSpinBox", "QSlider", "QCheckBox", "QRadioButton",
            "QGroupBox", "QTabWidget", "QListWidget", "QTreeWidget", "QTableWidget",
            "QScrollBar", "QProgressBar", "QToolBar", "QMenuBar", "QMenu",
            "QStatusBar", "QDockWidget", "QDialog", "QMessageBox", "QFrame"
        ]
        widget_list.addItems(widgets)
        widget_list.currentTextChanged.connect(self.load_widget_style)
        layout.addWidget(widget_list)

        # Widget style editor
        editor_widget = QWidget()
        self.widget_editor_layout = QVBoxLayout(editor_widget)

        # States for current widget
        states_group = QGroupBox("Widget States")
        states_layout = QVBoxLayout()

        self.state_checkboxes = {
            'normal': QCheckBox('Normal'),
            'hover': QCheckBox('Hover'),
            'pressed': QCheckBox('Pressed'),
            'disabled': QCheckBox('Disabled'),
            'selected': QCheckBox('Selected'),
            'focus': QCheckBox('Focus')
        }

        for state, checkbox in self.state_checkboxes.items():
            checkbox.setChecked(state == 'normal')
            checkbox.toggled.connect(self.update_preview)
            states_layout.addWidget(checkbox)

        states_group.setLayout(states_layout)
        self.widget_editor_layout.addWidget(states_group)

        # Properties for current state
        props_group = QGroupBox("State Properties")
        self.state_props_layout = QVBoxLayout()
        props_group.setLayout(self.state_props_layout)

        scroll = QScrollArea()
        scroll.setWidget(props_group)
        scroll.setWidgetResizable(True)
        self.widget_editor_layout.addWidget(scroll)

        layout.addWidget(editor_widget)

        self.main_tabs.addTab(tab, "Widget Styles")

    def create_colors_tab(self):
        """Create comprehensive color configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Color schemes
        scheme_group = QGroupBox("Color Schemes")
        scheme_layout = QVBoxLayout()

        scheme_selector = QComboBox()
        scheme_selector.addItems(["Default", "High Contrast", "Colorblind Safe", "Custom"])
        scheme_layout.addWidget(scheme_selector)

        scheme_group.setLayout(scheme_layout)
        scroll_layout.addWidget(scheme_group)

        # Primary colors
        primary_group = QGroupBox("Primary Colors")
        primary_layout = QGridLayout()

        primary_colors = {
            "Background": "#121212",
            "Foreground": "#EEEEEE",
            "Primary": "#00FFAA",
            "Secondary": "#FF4500",
            "Accent": "#FFD700",
            "Error": "#FF5252",
            "Warning": "#FFC107",
            "Success": "#4CAF50",
            "Info": "#2196F3"
        }

        row = 0
        for name, default in primary_colors.items():
            label = QLabel(name)
            picker = QPushButton()
            picker.setObjectName(f"color_{name}")
            picker.setStyleSheet(f"background-color: {default}; border: 1px solid #444;")
            picker.setFixedSize(50, 25)
            picker.clicked.connect(lambda checked, p=picker, n=name: self.pick_color(p, n))
            self.color_pickers[name] = picker

            # Add hex input
            hex_input = QLineEdit(default)
            hex_input.setMaximumWidth(80)
            hex_input.textChanged.connect(lambda text, p=picker: self.update_color_from_hex(p, text))

            primary_layout.addWidget(label, row, 0)
            primary_layout.addWidget(picker, row, 1)
            primary_layout.addWidget(hex_input, row, 2)
            row += 1

        primary_group.setLayout(primary_layout)
        scroll_layout.addWidget(primary_group)

        # Semantic colors
        semantic_group = QGroupBox("Semantic Colors")
        semantic_layout = QGridLayout()

        semantic_colors = {
            "Link": "#00FFFF",
            "Link Visited": "#FF00FF",
            "Selection Bg": "#00FFAA",
            "Selection Fg": "#000000",
            "Tooltip Bg": "#333333",
            "Tooltip Fg": "#FFFFFF"
        }

        row = 0
        for name, default in semantic_colors.items():
            label = QLabel(name)
            picker = QPushButton()
            picker.setObjectName(f"color_{name}")
            picker.setStyleSheet(f"background-color: {default}; border: 1px solid #444;")
            picker.setFixedSize(50, 25)
            picker.clicked.connect(lambda checked, p=picker, n=name: self.pick_color(p, n))
            self.color_pickers[name] = picker

            semantic_layout.addWidget(label, row, 0)
            semantic_layout.addWidget(picker, row, 1)
            row += 1

        semantic_group.setLayout(semantic_layout)
        scroll_layout.addWidget(semantic_group)

        # Gradient editor
        gradient_group = QGroupBox("Gradients")
        gradient_layout = QVBoxLayout()

        # Gradient list
        self.gradient_list = QListWidget()
        self.gradient_list.setMaximumHeight(100)
        gradient_layout.addWidget(self.gradient_list)

        # Add gradient button
        add_gradient_btn = QPushButton("Add New Gradient")
        add_gradient_btn.clicked.connect(self.add_new_gradient)
        gradient_layout.addWidget(add_gradient_btn)

        # Gradient editor area
        self.gradient_editor = QWidget()
        self.gradient_editor_layout = QVBoxLayout(self.gradient_editor)
        gradient_layout.addWidget(self.gradient_editor)

        gradient_group.setLayout(gradient_layout)
        scroll_layout.addWidget(gradient_group)

        # Color palette generator
        palette_group = QGroupBox("Color Palette Generator")
        palette_layout = QVBoxLayout()

        gen_layout = QHBoxLayout()
        gen_layout.addWidget(QLabel("Base Color:"))
        self.palette_base = QPushButton()
        self.palette_base.setStyleSheet("background-color: #00FFAA; border: 1px solid #444;")
        self.palette_base.setFixedSize(50, 25)
        self.palette_base.clicked.connect(lambda: self.pick_color(self.palette_base, "Palette Base"))
        gen_layout.addWidget(self.palette_base)

        gen_btn = QPushButton("Generate Palette")
        gen_btn.clicked.connect(self.generate_color_palette)
        gen_layout.addWidget(gen_btn)
        palette_layout.addLayout(gen_layout)

        # Palette display
        self.palette_display = QWidget()
        self.palette_display.setMinimumHeight(50)
        palette_layout.addWidget(self.palette_display)

        palette_group.setLayout(palette_layout)
        scroll_layout.addWidget(palette_group)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.main_tabs.addTab(tab, "Colors")

    def create_typography_tab(self):
        """Create comprehensive typography configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Font families
        families_group = QGroupBox("Font Families")
        families_layout = QGridLayout()

        font_categories = {
            "Default": "System Default",
            "Heading": "System Default",
            "Body": "System Default",
            "Monospace": "Consolas",
            "Display": "System Default"
        }

        row = 0
        for category, default in font_categories.items():
            label = QLabel(f"{category}:")
            font_combo = QFontComboBox()
            font_combo.setCurrentText(default)
            font_combo.currentFontChanged.connect(self.update_preview)
            self.font_selectors[category] = font_combo

            families_layout.addWidget(label, row, 0)
            families_layout.addWidget(font_combo, row, 1)
            row += 1

        families_group.setLayout(families_layout)
        scroll_layout.addWidget(families_group)

        # Font sizes
        sizes_group = QGroupBox("Font Sizes")
        sizes_layout = QGridLayout()

        size_categories = {
            "Base Size": 12,
            "H1": 32,
            "H2": 24,
            "H3": 20,
            "H4": 16,
            "H5": 14,
            "H6": 12,
            "Small": 10,
            "Large": 16
        }

        row = 0
        for category, default in size_categories.items():
            label = QLabel(f"{category}:")
            size_spin = QSpinBox()
            size_spin.setRange(6, 72)
            size_spin.setValue(default)
            size_spin.valueChanged.connect(self.update_preview)
            self.numeric_inputs[f"font_size_{category}"] = size_spin

            sizes_layout.addWidget(label, row, 0)
            sizes_layout.addWidget(size_spin, row, 1)
            row += 1

        sizes_group.setLayout(sizes_layout)
        scroll_layout.addWidget(sizes_group)

        # Font weights
        weights_group = QGroupBox("Font Weights")
        weights_layout = QGridLayout()

        weight_categories = {
            "Thin": 100,
            "Light": 300,
            "Regular": 400,
            "Medium": 500,
            "Bold": 700,
            "Black": 900
        }

        row = 0
        for category, default in weight_categories.items():
            label = QLabel(f"{category}:")
            weight_spin = QSpinBox()
            weight_spin.setRange(100, 900)
            weight_spin.setSingleStep(100)
            weight_spin.setValue(default)
            weight_spin.valueChanged.connect(self.update_preview)
            self.numeric_inputs[f"font_weight_{category}"] = weight_spin

            weights_layout.addWidget(label, row, 0)
            weights_layout.addWidget(weight_spin, row, 1)
            row += 1

        weights_group.setLayout(weights_layout)
        scroll_layout.addWidget(weights_group)

        # Text properties
        text_props_group = QGroupBox("Text Properties")
        text_props_layout = QGridLayout()

        # Line height
        text_props_layout.addWidget(QLabel("Line Height:"), 0, 0)
        line_height = QDoubleSpinBox()
        line_height.setRange(0.5, 3.0)
        line_height.setSingleStep(0.1)
        line_height.setValue(1.5)
        line_height.valueChanged.connect(self.update_preview)
        self.numeric_inputs['line_height'] = line_height
        text_props_layout.addWidget(line_height, 0, 1)

        # Letter spacing
        text_props_layout.addWidget(QLabel("Letter Spacing:"), 1, 0)
        letter_spacing = QDoubleSpinBox()
        letter_spacing.setRange(-5.0, 10.0)
        letter_spacing.setSingleStep(0.1)
        letter_spacing.setValue(0.0)
        letter_spacing.valueChanged.connect(self.update_preview)
        self.numeric_inputs['letter_spacing'] = letter_spacing
        text_props_layout.addWidget(letter_spacing, 1, 1)

        # Word spacing
        text_props_layout.addWidget(QLabel("Word Spacing:"), 2, 0)
        word_spacing = QDoubleSpinBox()
        word_spacing.setRange(-5.0, 20.0)
        word_spacing.setSingleStep(0.5)
        word_spacing.setValue(0.0)
        word_spacing.valueChanged.connect(self.update_preview)
        self.numeric_inputs['word_spacing'] = word_spacing
        text_props_layout.addWidget(word_spacing, 2, 1)

        # Text transform
        text_props_layout.addWidget(QLabel("Text Transform:"), 3, 0)
        text_transform = QComboBox()
        text_transform.addItems(["none", "capitalize", "uppercase", "lowercase"])
        text_transform.currentTextChanged.connect(self.update_preview)
        self.combo_boxes['text_transform'] = text_transform
        text_props_layout.addWidget(text_transform, 3, 1)

        # Text decoration
        self.text_underline = QCheckBox("Underline")
        self.text_overline = QCheckBox("Overline")
        self.text_strikethrough = QCheckBox("Strike-through")

        text_props_layout.addWidget(self.text_underline, 4, 0)
        text_props_layout.addWidget(self.text_overline, 4, 1)
        text_props_layout.addWidget(self.text_strikethrough, 5, 0)

        for checkbox in [self.text_underline, self.text_overline, self.text_strikethrough]:
            checkbox.toggled.connect(self.update_preview)

        text_props_group.setLayout(text_props_layout)
        scroll_layout.addWidget(text_props_group)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.main_tabs.addTab(tab, "Typography")

    def create_spacing_tab(self):
        """Create spacing and layout configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Margins
        margins_group = QGroupBox("Margins")
        margins_layout = QGridLayout()

        margin_types = ["Top", "Right", "Bottom", "Left"]
        for i, margin_type in enumerate(margin_types):
            label = QLabel(f"{margin_type}:")
            spin = QSpinBox()
            spin.setRange(0, 100)
            spin.setValue(8)
            spin.valueChanged.connect(self.update_preview)
            self.numeric_inputs[f"margin_{margin_type.lower()}"] = spin

            margins_layout.addWidget(label, i // 2, (i % 2) * 2)
            margins_layout.addWidget(spin, i // 2, (i % 2) * 2 + 1)

        # Link margins
        self.link_margins = QCheckBox("Link all margins")
        self.link_margins.toggled.connect(self.toggle_linked_margins)
        margins_layout.addWidget(self.link_margins, 2, 0, 1, 4)

        margins_group.setLayout(margins_layout)
        scroll_layout.addWidget(margins_group)

        # Padding
        padding_group = QGroupBox("Padding")
        padding_layout = QGridLayout()

        for i, padding_type in enumerate(margin_types):
            label = QLabel(f"{padding_type}:")
            spin = QSpinBox()
            spin.setRange(0, 100)
            spin.setValue(8)
            spin.valueChanged.connect(self.update_preview)
            self.numeric_inputs[f"padding_{padding_type.lower()}"] = spin

            padding_layout.addWidget(label, i // 2, (i % 2) * 2)
            padding_layout.addWidget(spin, i // 2, (i % 2) * 2 + 1)

        # Link padding
        self.link_padding = QCheckBox("Link all padding")
        self.link_padding.toggled.connect(self.toggle_linked_padding)
        padding_layout.addWidget(self.link_padding, 2, 0, 1, 4)

        padding_group.setLayout(padding_layout)
        scroll_layout.addWidget(padding_group)

        # Grid and flexbox
        layout_group = QGroupBox("Layout System")
        layout_layout = QVBoxLayout()

        # Layout type
        layout_type_layout = QHBoxLayout()
        layout_type_layout.addWidget(QLabel("Layout Type:"))
        self.layout_type = QComboBox()
        self.layout_type.addItems(["Block", "Flex", "Grid", "Inline", "Inline-Block"])
        self.layout_type.currentTextChanged.connect(self.update_preview)
        layout_type_layout.addWidget(self.layout_type)
        layout_layout.addLayout(layout_type_layout)

        # Flex properties
        self.flex_group = QGroupBox("Flex Properties")
        flex_layout = QGridLayout()

        flex_layout.addWidget(QLabel("Direction:"), 0, 0)
        self.flex_direction = QComboBox()
        self.flex_direction.addItems(["row", "row-reverse", "column", "column-reverse"])
        flex_layout.addWidget(self.flex_direction, 0, 1)

        flex_layout.addWidget(QLabel("Justify:"), 1, 0)
        self.flex_justify = QComboBox()
        self.flex_justify.addItems(["flex-start", "flex-end", "center", "space-between", "space-around"])
        flex_layout.addWidget(self.flex_justify, 1, 1)

        flex_layout.addWidget(QLabel("Align:"), 2, 0)
        self.flex_align = QComboBox()
        self.flex_align.addItems(["flex-start", "flex-end", "center", "stretch", "baseline"])
        flex_layout.addWidget(self.flex_align, 2, 1)

        self.flex_group.setLayout(flex_layout)
        layout_layout.addWidget(self.flex_group)

        # Grid properties
        self.grid_group = QGroupBox("Grid Properties")
        grid_layout = QGridLayout()

        grid_layout.addWidget(QLabel("Columns:"), 0, 0)
        self.grid_columns = QSpinBox()
        self.grid_columns.setRange(1, 12)
        self.grid_columns.setValue(3)
        grid_layout.addWidget(self.grid_columns, 0, 1)

        grid_layout.addWidget(QLabel("Rows:"), 1, 0)
        self.grid_rows = QSpinBox()
        self.grid_rows.setRange(1, 12)
        self.grid_rows.setValue(3)
        grid_layout.addWidget(self.grid_rows, 1, 1)

        grid_layout.addWidget(QLabel("Gap:"), 2, 0)
        self.grid_gap = QSpinBox()
        self.grid_gap.setRange(0, 50)
        self.grid_gap.setValue(10)
        grid_layout.addWidget(self.grid_gap, 2, 1)

        self.grid_group.setLayout(grid_layout)
        layout_layout.addWidget(self.grid_group)

        layout_group.setLayout(layout_layout)
        scroll_layout.addWidget(layout_group)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)




        # THIS IS SECOND PASTE IT MIGHT HAVE ERRORS OR DUPLICATES

        # Continuing from grid properties...
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.main_tabs.addTab(tab, "Spacing & Layout")

    def create_borders_tab(self):
        """Create borders and outlines configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Border styles
        border_group = QGroupBox("Border Styles")
        border_layout = QGridLayout()

        # Border width
        border_layout.addWidget(QLabel("Width:"), 0, 0)
        self.border_width = QSpinBox()
        self.border_width.setRange(0, 20)
        self.border_width.setValue(1)
        self.border_width.valueChanged.connect(self.update_preview)
        border_layout.addWidget(self.border_width, 0, 1)

        # Border style
        border_layout.addWidget(QLabel("Style:"), 1, 0)
        self.border_style = QComboBox()
        self.border_style.addItems([
            "none", "solid", "dashed", "dotted", "double",
            "groove", "ridge", "inset", "outset"
        ])
        self.border_style.setCurrentText("solid")
        self.border_style.currentTextChanged.connect(self.update_preview)
        border_layout.addWidget(self.border_style, 1, 1)

        # Border color
        border_layout.addWidget(QLabel("Color:"), 2, 0)
        self.border_color = QPushButton()
        self.border_color.setStyleSheet("background-color: #2D2D2D; border: 1px solid #444;")
        self.border_color.setFixedSize(50, 25)
        self.border_color.clicked.connect(lambda: self.pick_color(self.border_color, "Border"))
        border_layout.addWidget(self.border_color, 2, 1)
        
        # Connect border controls to update preview
        self.border_width.valueChanged.connect(self.update_preview)
        self.border_style.currentTextChanged.connect(self.update_preview)

        # Individual borders
        self.individual_borders = QCheckBox("Configure individual borders")
        self.individual_borders.toggled.connect(self.toggle_individual_borders)
        border_layout.addWidget(self.individual_borders, 3, 0, 1, 2)

        # Individual border controls (initially hidden)
        self.individual_border_widget = QWidget()
        individual_layout = QGridLayout(self.individual_border_widget)

        sides = ["Top", "Right", "Bottom", "Left"]
        for i, side in enumerate(sides):
            label = QLabel(f"{side}:")
            width_spin = QSpinBox()
            width_spin.setRange(0, 20)
            width_spin.setValue(1)
            style_combo = QComboBox()
            style_combo.addItems(["solid", "dashed", "dotted", "none"])
            color_btn = QPushButton()
            color_btn.setStyleSheet("background-color: #2D2D2D;")
            color_btn.setFixedSize(30, 20)

            individual_layout.addWidget(label, i, 0)
            individual_layout.addWidget(width_spin, i, 1)
            individual_layout.addWidget(style_combo, i, 2)
            individual_layout.addWidget(color_btn, i, 3)

        self.individual_border_widget.setVisible(False)
        border_layout.addWidget(self.individual_border_widget, 4, 0, 1, 4)

        border_group.setLayout(border_layout)
        scroll_layout.addWidget(border_group)

        # Border radius
        radius_group = QGroupBox("Border Radius")
        radius_layout = QGridLayout()

        # Uniform radius
        radius_layout.addWidget(QLabel("All corners:"), 0, 0)
        self.border_radius = QSpinBox()
        self.border_radius.setRange(0, 50)
        self.border_radius.setValue(4)
        self.border_radius.valueChanged.connect(self.update_preview)
        radius_layout.addWidget(self.border_radius, 0, 1)

        # Individual corners
        self.individual_corners = QCheckBox("Configure individual corners")
        self.individual_corners.toggled.connect(self.toggle_individual_corners)
        radius_layout.addWidget(self.individual_corners, 1, 0, 1, 2)

        # Individual corner controls
        self.corner_widget = QWidget()
        corner_layout = QGridLayout(self.corner_widget)

        corners = ["Top-Left", "Top-Right", "Bottom-Right", "Bottom-Left"]
        for i, corner in enumerate(corners):
            label = QLabel(f"{corner}:")
            spin = QSpinBox()
            spin.setRange(0, 50)
            spin.setValue(4)
            corner_layout.addWidget(label, i // 2, (i % 2) * 2)
            corner_layout.addWidget(spin, i // 2, (i % 2) * 2 + 1)

        self.corner_widget.setVisible(False)
        radius_layout.addWidget(self.corner_widget, 2, 0, 1, 4)

        radius_group.setLayout(radius_layout)
        scroll_layout.addWidget(radius_group)

        # Outline
        outline_group = QGroupBox("Outline")
        outline_layout = QGridLayout()

        outline_layout.addWidget(QLabel("Width:"), 0, 0)
        self.outline_width = QSpinBox()
        self.outline_width.setRange(0, 20)
        self.outline_width.setValue(0)
        outline_layout.addWidget(self.outline_width, 0, 1)

        outline_layout.addWidget(QLabel("Style:"), 1, 0)
        self.outline_style = QComboBox()
        self.outline_style.addItems(["none", "solid", "dashed", "dotted", "double"])
        outline_layout.addWidget(self.outline_style, 1, 1)

        outline_layout.addWidget(QLabel("Color:"), 2, 0)
        self.outline_color = QPushButton()
        self.outline_color.setStyleSheet("background-color: #00FFAA; border: 1px solid #444;")
        self.outline_color.setFixedSize(50, 25)
        self.outline_color.clicked.connect(lambda: self.pick_color(self.outline_color, "Outline"))
        outline_layout.addWidget(self.outline_color, 2, 1)

        outline_layout.addWidget(QLabel("Offset:"), 3, 0)
        self.outline_offset = QSpinBox()
        self.outline_offset.setRange(0, 20)
        self.outline_offset.setValue(0)
        outline_layout.addWidget(self.outline_offset, 3, 1)

        outline_group.setLayout(outline_layout)
        scroll_layout.addWidget(outline_group)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.main_tabs.addTab(tab, "Borders")

    def create_effects_tab(self):
        """Create visual effects configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Shadows
        shadow_group = QGroupBox("Box Shadow")
        shadow_layout = QGridLayout()

        # Enable shadow
        self.shadow_enabled = QCheckBox("Enable shadow")
        self.shadow_enabled.toggled.connect(self.update_preview)
        shadow_layout.addWidget(self.shadow_enabled, 0, 0, 1, 2)

        # Shadow properties
        shadow_layout.addWidget(QLabel("X Offset:"), 1, 0)
        self.shadow_x = QSpinBox()
        self.shadow_x.setRange(-50, 50)
        self.shadow_x.setValue(0)
        shadow_layout.addWidget(self.shadow_x, 1, 1)

        shadow_layout.addWidget(QLabel("Y Offset:"), 2, 0)
        self.shadow_y = QSpinBox()
        self.shadow_y.setRange(-50, 50)
        self.shadow_y.setValue(5)
        shadow_layout.addWidget(self.shadow_y, 2, 1)

        shadow_layout.addWidget(QLabel("Blur:"), 3, 0)
        self.shadow_blur = QSpinBox()
        self.shadow_blur.setRange(0, 50)
        self.shadow_blur.setValue(10)
        shadow_layout.addWidget(self.shadow_blur, 3, 1)

        shadow_layout.addWidget(QLabel("Spread:"), 4, 0)
        self.shadow_spread = QSpinBox()
        self.shadow_spread.setRange(-50, 50)
        self.shadow_spread.setValue(0)
        shadow_layout.addWidget(self.shadow_spread, 4, 1)

        shadow_layout.addWidget(QLabel("Color:"), 5, 0)
        self.shadow_color = QPushButton()
        self.shadow_color.setStyleSheet("background-color: rgba(0,0,0,0.5); border: 1px solid #444;")
        self.shadow_color.setFixedSize(50, 25)
        self.shadow_color.clicked.connect(lambda: self.pick_color(self.shadow_color, "Shadow"))
        shadow_layout.addWidget(self.shadow_color, 5, 1)

        # Inset shadow
        self.shadow_inset = QCheckBox("Inset shadow")
        shadow_layout.addWidget(self.shadow_inset, 6, 0, 1, 2)
        
        # Connect shadow controls to update preview
        for control in [self.shadow_x, self.shadow_y, self.shadow_blur, self.shadow_spread]:
            control.valueChanged.connect(self.update_preview)
        for checkbox in [self.shadow_enabled, self.shadow_inset]:
            checkbox.toggled.connect(self.update_preview)

        # Multiple shadows
        self.multiple_shadows = QCheckBox("Add multiple shadows")
        self.multiple_shadows.toggled.connect(self.toggle_multiple_shadows)
        shadow_layout.addWidget(self.multiple_shadows, 7, 0, 1, 2)

        shadow_group.setLayout(shadow_layout)
        scroll_layout.addWidget(shadow_group)

        # Text shadow
        text_shadow_group = QGroupBox("Text Shadow")
        text_shadow_layout = QGridLayout()

        self.text_shadow_enabled = QCheckBox("Enable text shadow")
        text_shadow_layout.addWidget(self.text_shadow_enabled, 0, 0, 1, 2)

        text_shadow_layout.addWidget(QLabel("X Offset:"), 1, 0)
        self.text_shadow_x = QSpinBox()
        self.text_shadow_x.setRange(-20, 20)
        self.text_shadow_x.setValue(1)
        text_shadow_layout.addWidget(self.text_shadow_x, 1, 1)

        text_shadow_layout.addWidget(QLabel("Y Offset:"), 2, 0)
        self.text_shadow_y = QSpinBox()
        self.text_shadow_y.setRange(-20, 20)
        self.text_shadow_y.setValue(1)
        text_shadow_layout.addWidget(self.text_shadow_y, 2, 1)

        text_shadow_layout.addWidget(QLabel("Blur:"), 3, 0)
        self.text_shadow_blur = QSpinBox()
        self.text_shadow_blur.setRange(0, 20)
        self.text_shadow_blur.setValue(2)
        text_shadow_layout.addWidget(self.text_shadow_blur, 3, 1)

        text_shadow_layout.addWidget(QLabel("Color:"), 4, 0)
        self.text_shadow_color = QPushButton()
        self.text_shadow_color.setStyleSheet("background-color: rgba(0,0,0,0.8); border: 1px solid #444;")
        self.text_shadow_color.setFixedSize(50, 25)
        self.text_shadow_color.clicked.connect(lambda: self.pick_color(self.text_shadow_color, "Text Shadow"))
        text_shadow_layout.addWidget(self.text_shadow_color, 4, 1)
        
        # Connect text shadow controls to update preview
        for control in [self.text_shadow_x, self.text_shadow_y, self.text_shadow_blur]:
            control.valueChanged.connect(self.update_preview)
        self.text_shadow_enabled.toggled.connect(self.update_preview)

        text_shadow_group.setLayout(text_shadow_layout)
        scroll_layout.addWidget(text_shadow_group)

        # Filters
        filters_group = QGroupBox("CSS Filters")
        filters_layout = QGridLayout()

        # Blur
        filters_layout.addWidget(QLabel("Blur:"), 0, 0)
        self.filter_blur = QDoubleSpinBox()
        self.filter_blur.setRange(0, 20)
        self.filter_blur.setSuffix("px")
        self.filter_blur.setValue(0)
        filters_layout.addWidget(self.filter_blur, 0, 1)

        # Brightness
        filters_layout.addWidget(QLabel("Brightness:"), 1, 0)
        self.filter_brightness = QSpinBox()
        self.filter_brightness.setRange(0, 200)
        self.filter_brightness.setSuffix("%")
        self.filter_brightness.setValue(100)
        filters_layout.addWidget(self.filter_brightness, 1, 1)

        # Contrast
        filters_layout.addWidget(QLabel("Contrast:"), 2, 0)
        self.filter_contrast = QSpinBox()
        self.filter_contrast.setRange(0, 200)
        self.filter_contrast.setSuffix("%")
        self.filter_contrast.setValue(100)
        filters_layout.addWidget(self.filter_contrast, 2, 1)

        # Grayscale
        filters_layout.addWidget(QLabel("Grayscale:"), 3, 0)
        self.filter_grayscale = QSpinBox()
        self.filter_grayscale.setRange(0, 100)
        self.filter_grayscale.setSuffix("%")
        self.filter_grayscale.setValue(0)
        filters_layout.addWidget(self.filter_grayscale, 3, 1)

        # Hue rotate
        filters_layout.addWidget(QLabel("Hue Rotate:"), 4, 0)
        self.filter_hue = QSpinBox()
        self.filter_hue.setRange(0, 360)
        self.filter_hue.setSuffix("°")
        self.filter_hue.setValue(0)
        filters_layout.addWidget(self.filter_hue, 4, 1)

        # Invert
        filters_layout.addWidget(QLabel("Invert:"), 5, 0)
        self.filter_invert = QSpinBox()
        self.filter_invert.setRange(0, 100)
        self.filter_invert.setSuffix("%")
        self.filter_invert.setValue(0)
        filters_layout.addWidget(self.filter_invert, 5, 1)

        # Opacity
        filters_layout.addWidget(QLabel("Opacity:"), 6, 0)
        self.filter_opacity = QSpinBox()
        self.filter_opacity.setRange(0, 100)
        self.filter_opacity.setSuffix("%")
        self.filter_opacity.setValue(100)
        filters_layout.addWidget(self.filter_opacity, 6, 1)

        # Saturate
        filters_layout.addWidget(QLabel("Saturate:"), 7, 0)
        self.filter_saturate = QSpinBox()
        self.filter_saturate.setRange(0, 200)
        self.filter_saturate.setSuffix("%")
        self.filter_saturate.setValue(100)
        filters_layout.addWidget(self.filter_saturate, 7, 1)

        # Sepia
        filters_layout.addWidget(QLabel("Sepia:"), 8, 0)
        self.filter_sepia = QSpinBox()
        self.filter_sepia.setRange(0, 100)
        self.filter_sepia.setSuffix("%")
        self.filter_sepia.setValue(0)
        filters_layout.addWidget(self.filter_sepia, 8, 1)

        # Connect all filter controls to update preview
        for control in [self.filter_blur, self.filter_brightness, self.filter_contrast, 
                       self.filter_grayscale, self.filter_hue, self.filter_invert,
                       self.filter_opacity, self.filter_saturate, self.filter_sepia]:
            if hasattr(control, 'valueChanged'):
                control.valueChanged.connect(self.update_preview)

        filters_group.setLayout(filters_layout)
        scroll_layout.addWidget(filters_group)

        # Transform
        transform_group = QGroupBox("Transform")
        transform_layout = QGridLayout()

        # Scale
        transform_layout.addWidget(QLabel("Scale X:"), 0, 0)
        self.transform_scale_x = QDoubleSpinBox()
        self.transform_scale_x.setRange(0.1, 3.0)
        self.transform_scale_x.setSingleStep(0.1)
        self.transform_scale_x.setValue(1.0)
        transform_layout.addWidget(self.transform_scale_x, 0, 1)

        transform_layout.addWidget(QLabel("Scale Y:"), 1, 0)
        self.transform_scale_y = QDoubleSpinBox()
        self.transform_scale_y.setRange(0.1, 3.0)
        self.transform_scale_y.setSingleStep(0.1)
        self.transform_scale_y.setValue(1.0)
        transform_layout.addWidget(self.transform_scale_y, 1, 1)

        # Rotate
        transform_layout.addWidget(QLabel("Rotate:"), 2, 0)
        self.transform_rotate = QSpinBox()
        self.transform_rotate.setRange(-360, 360)
        self.transform_rotate.setSuffix("°")
        self.transform_rotate.setValue(0)
        transform_layout.addWidget(self.transform_rotate, 2, 1)

        # Skew
        transform_layout.addWidget(QLabel("Skew X:"), 3, 0)
        self.transform_skew_x = QSpinBox()
        self.transform_skew_x.setRange(-90, 90)
        self.transform_skew_x.setSuffix("°")
        self.transform_skew_x.setValue(0)
        transform_layout.addWidget(self.transform_skew_x, 3, 1)

        transform_layout.addWidget(QLabel("Skew Y:"), 4, 0)
        self.transform_skew_y = QSpinBox()
        self.transform_skew_y.setRange(-90, 90)
        self.transform_skew_y.setSuffix("°")
        self.transform_skew_y.setValue(0)
        transform_layout.addWidget(self.transform_skew_y, 4, 1)

        # Connect transform controls to update preview
        for control in [self.transform_scale_x, self.transform_scale_y, self.transform_rotate,
                       self.transform_skew_x, self.transform_skew_y]:
            control.valueChanged.connect(self.update_preview)

        transform_group.setLayout(transform_layout)
        scroll_layout.addWidget(transform_group)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.main_tabs.addTab(tab, "Effects")

    def create_animations_tab(self):
        """Create animations and transitions configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Transitions
        transitions_group = QGroupBox("Transitions")
        transitions_layout = QGridLayout()

        # Transition property
        transitions_layout.addWidget(QLabel("Property:"), 0, 0)
        self.transition_property = QComboBox()
        self.transition_property.addItems([
            "all", "none", "background-color", "color", "opacity",
            "transform", "border", "width", "height", "margin", "padding"
        ])
        transitions_layout.addWidget(self.transition_property, 0, 1)

        # Duration
        transitions_layout.addWidget(QLabel("Duration:"), 1, 0)
        self.transition_duration = QSpinBox()
        self.transition_duration.setRange(0, 5000)
        self.transition_duration.setSuffix(" ms")
        self.transition_duration.setValue(300)
        transitions_layout.addWidget(self.transition_duration, 1, 1)

        # Timing function
        transitions_layout.addWidget(QLabel("Timing:"), 2, 0)
        self.transition_timing = QComboBox()
        self.transition_timing.addItems([
            "ease", "linear", "ease-in", "ease-out", "ease-in-out",
            "cubic-bezier(0.4, 0, 0.2, 1)", "cubic-bezier(0, 0, 0.2, 1)",
            "cubic-bezier(0.4, 0, 1, 1)", "cubic-bezier(0, 0, 0.6, 1)"
        ])
        transitions_layout.addWidget(self.transition_timing, 2, 1)

        # Delay
        transitions_layout.addWidget(QLabel("Delay:"), 3, 0)
        self.transition_delay = QSpinBox()
        self.transition_delay.setRange(0, 2000)
        self.transition_delay.setSuffix(" ms")
        self.transition_delay.setValue(0)
        transitions_layout.addWidget(self.transition_delay, 3, 1)
        
        # Connect transition controls to update preview
        for combo in [self.transition_property, self.transition_timing]:
            combo.currentTextChanged.connect(self.update_preview)
        for spinbox in [self.transition_duration, self.transition_delay]:
            spinbox.valueChanged.connect(self.update_preview)

        transitions_group.setLayout(transitions_layout)
        scroll_layout.addWidget(transitions_group)

        # Keyframe animations
        animations_group = QGroupBox("Keyframe Animations")
        animations_layout = QVBoxLayout()

        # Animation list
        self.animation_list = QListWidget()
        self.animation_list.setMaximumHeight(100)
        animations_layout.addWidget(self.animation_list)

        # Add animation button
        add_anim_btn = QPushButton("Add New Animation")
        add_anim_btn.clicked.connect(self.add_new_animation)
        animations_layout.addWidget(add_anim_btn)

        # Animation editor
        self.animation_editor = QWidget()
        anim_editor_layout = QVBoxLayout(self.animation_editor)

        # Animation properties
        anim_props_layout = QGridLayout()

        anim_props_layout.addWidget(QLabel("Name:"), 0, 0)
        self.anim_name = QLineEdit()
        anim_props_layout.addWidget(self.anim_name, 0, 1)

        anim_props_layout.addWidget(QLabel("Duration:"), 1, 0)
        self.anim_duration = QSpinBox()
        self.anim_duration.setRange(100, 10000)
        self.anim_duration.setSuffix(" ms")
        self.anim_duration.setValue(1000)
        anim_props_layout.addWidget(self.anim_duration, 1, 1)

        anim_props_layout.addWidget(QLabel("Timing:"), 2, 0)
        self.anim_timing = QComboBox()
        self.anim_timing.addItems([
            "ease", "linear", "ease-in", "ease-out", "ease-in-out"
        ])
        anim_props_layout.addWidget(self.anim_timing, 2, 1)

        anim_props_layout.addWidget(QLabel("Delay:"), 3, 0)
        self.anim_delay = QSpinBox()
        self.anim_delay.setRange(0, 5000)
        self.anim_delay.setSuffix(" ms")
        self.anim_delay.setValue(0)
        anim_props_layout.addWidget(self.anim_delay, 3, 1)

        anim_props_layout.addWidget(QLabel("Iterations:"), 4, 0)
        self.anim_iterations = QComboBox()
        self.anim_iterations.addItems(["1", "2", "3", "5", "10", "infinite"])
        anim_props_layout.addWidget(self.anim_iterations, 4, 1)

        anim_props_layout.addWidget(QLabel("Direction:"), 5, 0)
        self.anim_direction = QComboBox()
        self.anim_direction.addItems([
            "normal", "reverse", "alternate", "alternate-reverse"
        ])
        anim_props_layout.addWidget(self.anim_direction, 5, 1)

        anim_editor_layout.addLayout(anim_props_layout)

        # Keyframes
        keyframes_group = QGroupBox("Keyframes")
        self.keyframes_layout = QVBoxLayout()

        add_keyframe_btn = QPushButton("Add Keyframe")
        add_keyframe_btn.clicked.connect(self.add_keyframe)
        self.keyframes_layout.addWidget(add_keyframe_btn)

        keyframes_group.setLayout(self.keyframes_layout)
        anim_editor_layout.addWidget(keyframes_group)

        animations_layout.addWidget(self.animation_editor)

        animations_group.setLayout(animations_layout)
        scroll_layout.addWidget(animations_group)

        # Hover effects
        hover_group = QGroupBox("Hover Effects")
        hover_layout = QVBoxLayout()

        self.hover_scale = QCheckBox("Scale on hover")
        self.hover_rotate = QCheckBox("Rotate on hover")
        self.hover_shadow = QCheckBox("Shadow on hover")
        self.hover_color = QCheckBox("Color change on hover")

        hover_layout.addWidget(self.hover_scale)
        hover_layout.addWidget(self.hover_rotate)
        hover_layout.addWidget(self.hover_shadow)
        hover_layout.addWidget(self.hover_color)
        
        # Connect hover effects to update preview
        for checkbox in [self.hover_scale, self.hover_rotate, self.hover_shadow, self.hover_color]:
            checkbox.toggled.connect(self.update_preview)

        hover_group.setLayout(hover_layout)
        scroll_layout.addWidget(hover_group)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.main_tabs.addTab(tab, "Animations")

    def create_advanced_tab(self):
        """Create advanced configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Custom CSS
        css_group = QGroupBox("Custom CSS")
        css_layout = QVBoxLayout()

        self.custom_css = QTextEdit()
        self.custom_css.setPlaceholderText("/* Enter custom CSS here */")
        self.custom_css.textChanged.connect(self.update_preview)
        css_layout.addWidget(self.custom_css)

        css_group.setLayout(css_layout)
        scroll_layout.addWidget(css_group)

        # CSS Variables
        vars_group = QGroupBox("CSS Variables")
        vars_layout = QVBoxLayout()

        self.css_vars_list = QListWidget()
        self.css_vars_list.setMaximumHeight(100)
        vars_layout.addWidget(self.css_vars_list)

        add_var_btn = QPushButton("Add CSS Variable")
        add_var_btn.clicked.connect(self.add_css_variable)
        vars_layout.addWidget(add_var_btn)

        vars_group.setLayout(vars_layout)
        scroll_layout.addWidget(vars_group)

        # Pseudo-elements
        pseudo_group = QGroupBox("Pseudo-elements")
        pseudo_layout = QVBoxLayout()

        self.before_enabled = QCheckBox("::before")
        self.after_enabled = QCheckBox("::after")
        self.selection_enabled = QCheckBox("::selection")
        self.placeholder_enabled = QCheckBox("::placeholder")

        pseudo_layout.addWidget(self.before_enabled)
        pseudo_layout.addWidget(self.after_enabled)
        pseudo_layout.addWidget(self.selection_enabled)
        pseudo_layout.addWidget(self.placeholder_enabled)

        pseudo_group.setLayout(pseudo_layout)
        scroll_layout.addWidget(pseudo_group)

        # Media queries
        media_group = QGroupBox("Media Queries")
        media_layout = QVBoxLayout()

        self.media_list = QListWidget()
        self.media_list.setMaximumHeight(100)
        media_layout.addWidget(self.media_list)

        add_media_btn = QPushButton("Add Media Query")
        add_media_btn.clicked.connect(self.add_media_query)
        media_layout.addWidget(add_media_btn)

        media_group.setLayout(media_layout)
        scroll_layout.addWidget(media_group)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.main_tabs.addTab(tab, "Advanced")

    def create_import_export_tab(self):
        """Create import/export configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Import section
        import_group = QGroupBox("Import")
        import_layout = QVBoxLayout()

        import_btns_layout = QHBoxLayout()

        import_css_btn = QPushButton("Import CSS File")
        import_css_btn.clicked.connect(self.import_css_file)
        import_btns_layout.addWidget(import_css_btn)

        import_json_btn = QPushButton("Import JSON Theme")
        import_json_btn.clicked.connect(self.import_json_theme)
        import_btns_layout.addWidget(import_json_btn)

        import_qt_btn = QPushButton("Import Qt Stylesheet")
        import_qt_btn.clicked.connect(self.import_qt_stylesheet)
        import_btns_layout.addWidget(import_qt_btn)

        import_layout.addLayout(import_btns_layout)

        # Import preview
        self.import_preview = QTextEdit()
        self.import_preview.setReadOnly(True)
        self.import_preview.setMaximumHeight(150)
        self.import_preview.setPlaceholderText("Imported content will appear here...")
        import_layout.addWidget(self.import_preview)

        import_group.setLayout(import_layout)
        layout.addWidget(import_group)

        # Export section
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout()

        export_btns_layout = QHBoxLayout()

        export_css_btn = QPushButton("Export as CSS")
        export_css_btn.clicked.connect(self.export_css_file)
        export_btns_layout.addWidget(export_css_btn)

        export_json_btn = QPushButton("Export as JSON")
        export_json_btn.clicked.connect(self.export_json_theme)
        export_btns_layout.addWidget(export_json_btn)

        export_qt_btn = QPushButton("Export as Qt Stylesheet")
        export_qt_btn.clicked.connect(self.export_qt_stylesheet)
        export_btns_layout.addWidget(export_qt_btn)

        export_layout.addLayout(export_btns_layout)

        # Export options
        options_layout = QHBoxLayout()
        self.minify_export = QCheckBox("Minify output")
        self.include_comments = QCheckBox("Include comments")
        self.include_comments.setChecked(True)
        options_layout.addWidget(self.minify_export)
        options_layout.addWidget(self.include_comments)
        export_layout.addLayout(options_layout)

        # Export preview
        self.export_preview = QTextEdit()
        self.export_preview.setReadOnly(True)
        self.export_preview.setPlaceholderText("Generated stylesheet will appear here...")
        export_layout.addWidget(self.export_preview)

        # Copy button
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_export_to_clipboard)
        export_layout.addWidget(copy_btn)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        self.main_tabs.addTab(tab, "Import/Export")

    def create_preview_panel(self) -> QWidget:
        """Create the live preview panel."""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)

        # Preview header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Live Preview"))

        # Device selector
        device_combo = QComboBox()
        device_combo.addItems(["Desktop", "Tablet", "Mobile"])
        device_combo.currentTextChanged.connect(self.change_preview_device)
        header_layout.addWidget(device_combo)

        # Theme selector for preview
        theme_combo = QComboBox()
        theme_combo.addItems(["Light", "Dark", "Auto"])
        header_layout.addWidget(theme_combo)

        layout.addLayout(header_layout)

        # Preview area
        preview_scroll = QScrollArea()
        self.preview_content = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_content)

        # Create sample widgets
        self.create_preview_widgets()

        preview_scroll.setWidget(self.preview_content)
        preview_scroll.setWidgetResizable(True)
        layout.addWidget(preview_scroll)

        return preview_widget

    def create_preview_widgets(self):
        """Create sample widgets for preview."""
        # Buttons section
        buttons_group = QGroupBox("Buttons")
        buttons_layout = QHBoxLayout()

        primary_btn = QPushButton("Primary")
        primary_btn.setObjectName("primaryButton")
        secondary_btn = QPushButton("Secondary")
        secondary_btn.setObjectName("secondaryButton")
        danger_btn = QPushButton("Danger")
        danger_btn.setObjectName("dangerButton")
        disabled_btn = QPushButton("Disabled")
        disabled_btn.setEnabled(False)

        buttons_layout.addWidget(primary_btn)
        buttons_layout.addWidget(secondary_btn)
        buttons_layout.addWidget(danger_btn)
        buttons_layout.addWidget(disabled_btn)
        buttons_group.setLayout(buttons_layout)
        self.preview_layout.addWidget(buttons_group)

        # Input section
        inputs_group = QGroupBox("Input Elements")
        inputs_layout = QGridLayout()

        inputs_layout.addWidget(QLabel("Text Input:"), 0, 0)
        text_input = QLineEdit("Sample text")
        inputs_layout.addWidget(text_input, 0, 1)

        inputs_layout.addWidget(QLabel("Combo Box:"), 1, 0)
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        inputs_layout.addWidget(combo, 1, 1)

        inputs_layout.addWidget(QLabel("Spin Box:"), 2, 0)
        spin = QSpinBox()
        spin.setValue(42)
        inputs_layout.addWidget(spin, 2, 1)

        inputs_layout.addWidget(QLabel("Check Box:"), 3, 0)
        check = QCheckBox("Check me")
        check.setChecked(True)
        inputs_layout.addWidget(check, 3, 1)

        inputs_group.setLayout(inputs_layout)
        self.preview_layout.addWidget(inputs_group)

        # Text section
        text_group = QGroupBox("Text Elements")
        text_layout = QVBoxLayout()

        h1 = QLabel("Heading 1")
        h1.setObjectName("h1")
        h2 = QLabel("Heading 2")
        h2.setObjectName("h2")
        h3 = QLabel("Heading 3")
        h3.setObjectName("h3")

        paragraph = QLabel("This is a paragraph of text to demonstrate the typography settings. "
                           "It includes multiple sentences to show line height and spacing.")
        paragraph.setWordWrap(True)

        text_layout.addWidget(h1)
        text_layout.addWidget(h2)
        text_layout.addWidget(h3)
        text_layout.addWidget(paragraph)

        text_group.setLayout(text_layout)
        self.preview_layout.addWidget(text_group)

        # Lists section
        lists_group = QGroupBox("Lists")
        lists_layout = QHBoxLayout()

        list_widget = QListWidget()
        list_widget.addItems(["Item 1", "Item 2", "Item 3", "Item 4"])
        lists_layout.addWidget(list_widget)

        tree_widget = QTreeWidget()
        tree_widget.setHeaderLabel("Tree View")
        root = QTreeWidgetItem(tree_widget, ["Root"])
        child1 = QTreeWidgetItem(root, ["Child 1"])
        child2 = QTreeWidgetItem(root, ["Child 2"])
        QTreeWidgetItem(child1, ["Subchild 1"])
        QTreeWidgetItem(child1, ["Subchild 2"])
        tree_widget.expandAll()
        lists_layout.addWidget(tree_widget)

        lists_group.setLayout(lists_layout)
        self.preview_layout.addWidget(lists_group)

        # Progress section
        progress_group = QGroupBox("Progress Indicators")
        progress_layout = QVBoxLayout()

        progress = QProgressBar()
        progress.setValue(75)
        progress_layout.addWidget(progress)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setValue(50)
        progress_layout.addWidget(slider)

        progress_group.setLayout(progress_layout)
        self.preview_layout.addWidget(progress_group)

        # Tab widget with content
        tabs = QTabWidget()
        
        # Tab 1 - More Controls
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        
        # Advanced sliders
        sliders_group = QGroupBox("Sliders & Ranges")
        sliders_layout = QGridLayout()
        
        sliders_layout.addWidget(QLabel("Horizontal Slider:"), 0, 0)
        h_slider = QSlider(Qt.Orientation.Horizontal)
        h_slider.setRange(0, 100)
        h_slider.setValue(75)
        sliders_layout.addWidget(h_slider, 0, 1)
        
        sliders_layout.addWidget(QLabel("Vertical Slider:"), 1, 0)
        v_slider = QSlider(Qt.Orientation.Vertical)
        v_slider.setRange(0, 100)
        v_slider.setValue(50)
        v_slider.setMaximumHeight(100)
        sliders_layout.addWidget(v_slider, 1, 1)
        
        sliders_layout.addWidget(QLabel("Progress Bar:"), 2, 0)
        progress2 = QProgressBar()
        progress2.setValue(85)
        progress2.setFormat("Loading... %p%")
        sliders_layout.addWidget(progress2, 2, 1)
        
        sliders_group.setLayout(sliders_layout)
        tab1_layout.addWidget(sliders_group)
        
        # Advanced inputs
        advanced_inputs_group = QGroupBox("Advanced Inputs")
        advanced_layout = QGridLayout()
        
        advanced_layout.addWidget(QLabel("Double Spin:"), 0, 0)
        double_spin = QDoubleSpinBox()
        double_spin.setRange(0.0, 100.0)
        double_spin.setValue(3.14159)
        double_spin.setDecimals(5)
        advanced_layout.addWidget(double_spin, 0, 1)
        
        advanced_layout.addWidget(QLabel("Font Combo:"), 1, 0)
        font_combo = QFontComboBox()
        advanced_layout.addWidget(font_combo, 1, 1)
        
        advanced_layout.addWidget(QLabel("Color Dialog:"), 2, 0)
        color_btn = QPushButton("Choose Color")
        color_btn.setStyleSheet("background-color: #ff6b35; color: white;")
        advanced_layout.addWidget(color_btn, 2, 1)
        
        advanced_inputs_group.setLayout(advanced_layout)
        tab1_layout.addWidget(advanced_inputs_group)
        tab1_layout.addStretch()
        
        # Tab 2 - Tables & Trees
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        
        # Table widget
        table_group = QGroupBox("Table Widget")
        table_layout = QVBoxLayout()
        
        table = QTableWidget(3, 4)
        table.setHorizontalHeaderLabels(["Name", "Value", "Type", "Status"])
        table.setVerticalHeaderLabels(["Row 1", "Row 2", "Row 3"])
        
        # Add sample data
        table.setItem(0, 0, QTableWidgetItem("Sample"))
        table.setItem(0, 1, QTableWidgetItem("123.45"))
        table.setItem(0, 2, QTableWidgetItem("Number"))
        table.setItem(0, 3, QTableWidgetItem("Active"))
        
        table.setItem(1, 0, QTableWidgetItem("Test"))
        table.setItem(1, 1, QTableWidgetItem("67.89"))
        table.setItem(1, 2, QTableWidgetItem("Float"))
        table.setItem(1, 3, QTableWidgetItem("Pending"))
        
        table.setItem(2, 0, QTableWidgetItem("Demo"))
        table.setItem(2, 1, QTableWidgetItem("999"))
        table.setItem(2, 2, QTableWidgetItem("Integer"))
        table.setItem(2, 3, QTableWidgetItem("Complete"))
        
        table.resizeColumnsToContents()
        table_layout.addWidget(table)
        table_group.setLayout(table_layout)
        tab2_layout.addWidget(table_group)
        
        # Tab 3 - Frames & Layouts
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        
        # Different frame styles
        frames_group = QGroupBox("Frame Styles")
        frames_layout = QGridLayout()
        
        # Raised frame
        raised_frame = QFrame()
        raised_frame.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        raised_frame.setLineWidth(2)
        raised_frame_label = QLabel("Raised Panel")
        raised_frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        raised_layout = QVBoxLayout(raised_frame)
        raised_layout.addWidget(raised_frame_label)
        frames_layout.addWidget(raised_frame, 0, 0)
        
        # Sunken frame
        sunken_frame = QFrame()
        sunken_frame.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        sunken_frame.setLineWidth(2)
        sunken_frame_label = QLabel("Sunken Panel")
        sunken_frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sunken_layout = QVBoxLayout(sunken_frame)
        sunken_layout.addWidget(sunken_frame_label)
        frames_layout.addWidget(sunken_frame, 0, 1)
        
        # Box frame
        box_frame = QFrame()
        box_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        box_frame.setLineWidth(3)
        box_frame_label = QLabel("Box Frame")
        box_frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box_layout = QVBoxLayout(box_frame)
        box_layout.addWidget(box_frame_label)
        frames_layout.addWidget(box_frame, 1, 0)
        
        # Styled frame
        styled_frame = QFrame()
        styled_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        styled_frame_label = QLabel("Styled Panel")
        styled_frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        styled_layout = QVBoxLayout(styled_frame)
        styled_layout.addWidget(styled_frame_label)
        frames_layout.addWidget(styled_frame, 1, 1)
        
        frames_group.setLayout(frames_layout)
        tab3_layout.addWidget(frames_group)
        tab3_layout.addStretch()
        
        tabs.addTab(tab1, "Advanced Controls")
        tabs.addTab(tab2, "Tables & Data")
        tabs.addTab(tab3, "Frames & Panels")
        self.preview_layout.addWidget(tabs)

        # Status indicators
        status_group = QGroupBox("Status & Indicators")
        status_layout = QHBoxLayout()
        
        # Different progress bars
        progress_indeterminate = QProgressBar()
        progress_indeterminate.setRange(0, 0)  # Indeterminate
        status_layout.addWidget(progress_indeterminate)
        
        # Status labels
        status_ok = QLabel("● Online")
        status_ok.setStyleSheet("color: #4CAF50; font-weight: bold;")
        status_layout.addWidget(status_ok)
        
        status_warning = QLabel("● Warning")
        status_warning.setStyleSheet("color: #FF9800; font-weight: bold;")
        status_layout.addWidget(status_warning)
        
        status_error = QLabel("● Error")
        status_error.setStyleSheet("color: #F44336; font-weight: bold;")
        status_layout.addWidget(status_error)
        
        status_group.setLayout(status_layout)
        self.preview_layout.addWidget(status_group)

        self.preview_layout.addStretch()

        # Helper methods

    def pick_color(self, button: QPushButton, name: str):
        """Open color picker dialog."""
        current_color = button.styleSheet().split("background-color:")[1].split(";")[0].strip()
        color = QColorDialog.getColor(QColor(current_color), self, f"Select {name} Color")
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #444;")
            self.update_preview()
            self.add_to_undo_stack()

    def update_color_from_hex(self, button: QPushButton, hex_value: str):
        """Update color button from hex input."""
        if QColor(hex_value).isValid():
            button.setStyleSheet(f"background-color: {hex_value}; border: 1px solid #444;")
            self.update_preview()

    def toggle_preview(self, enabled: bool):
        """Toggle live preview."""
        self.live_preview = enabled
        if enabled:
            self.update_preview()

    def update_preview(self):
        """Update the live preview with current settings."""
        if not self.live_preview:
            return

        css = self.generate_stylesheet()
        self.preview_content.setStyleSheet(css)
        self.export_preview.setPlainText(css)
        self.style_changed.emit(css)

    def generate_stylesheet(self) -> str:
        """Generate complete stylesheet from current settings."""
        css_parts = []

        # Global styles
        css_parts.append(self.generate_global_styles())

        # Widget-specific styles
        css_parts.append(self.generate_widget_styles())

        # Custom CSS
        if self.custom_css.toPlainText():
            css_parts.append(self.custom_css.toPlainText())

        return "\n\n".join(filter(None, css_parts))

    def generate_global_styles(self) -> str:
        """Generate global CSS styles."""
        styles = []

        # Base QWidget styles
        widget_style = f"""QWidget {{
        background-color: {self.color_pickers.get('Background', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()};
        color: {self.color_pickers.get('Foreground', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()};
        font-family: '{self.font_selectors.get('Default', QFontComboBox()).currentFont().family()}';
        font-size: {self.numeric_inputs.get('font_size_Base Size', QSpinBox()).value()}px;
    }}"""
        styles.append(widget_style)

        # Selection colors
        selection_style = f"""QWidget::selection {{
        background-color: {self.color_pickers.get('Selection Bg', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()};
        color: {self.color_pickers.get('Selection Fg', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()};
    }}"""
        styles.append(selection_style)

        return "\n\n".join(styles)

    def generate_widget_styles(self) -> str:
        """Generate widget-specific styles."""
        styles = []

        # Button styles
        button_style = self.generate_button_styles()
        if button_style:
            styles.append(button_style)

        # Input styles
        input_style = self.generate_input_styles()
        if input_style:
            styles.append(input_style)

        # Slider styles
        slider_styles = self.generate_slider_styles()
        if slider_styles:
            styles.append(slider_styles)

        # Progress bar styles
        progress_styles = self.generate_progress_styles()
        if progress_styles:
            styles.append(progress_styles)

        # Tab widget styles
        tab_styles = self.generate_tab_styles()
        if tab_styles:
            styles.append(tab_styles)

        # Table styles
        table_styles = self.generate_table_styles()
        if table_styles:
            styles.append(table_styles)

        # Frame styles
        frame_styles = self.generate_frame_styles()
        if frame_styles:
            styles.append(frame_styles)

        return "\n\n".join(styles)

    def generate_slider_styles(self) -> str:
        """Generate slider-specific styles."""
        primary_color = self.color_pickers.get('Primary', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()
        secondary_color = self.color_pickers.get('Secondary', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()
        
        return f"""QSlider::groove:horizontal {{
        border: 1px solid #999999;
        height: 8px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
        margin: 2px 0;
        border-radius: 4px;
    }}

    QSlider::handle:horizontal {{
        background: {primary_color};
        border: 1px solid #5c5c5c;
        width: 18px;
        margin: -2px 0;
        border-radius: 9px;
    }}

    QSlider::handle:horizontal:hover {{
        background: {secondary_color};
    }}

    QSlider::sub-page:horizontal {{
        background: {primary_color};
        border: 1px solid #777;
        height: 8px;
        border-radius: 4px;
    }}"""

    def generate_progress_styles(self) -> str:
        """Generate progress bar styles."""
        primary_color = self.color_pickers.get('Primary', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()
        background_color = self.color_pickers.get('Background', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()
        
        return f"""QProgressBar {{
        border: 2px solid grey;
        border-radius: 5px;
        text-align: center;
        background-color: {background_color};
    }}

    QProgressBar::chunk {{
        background-color: {primary_color};
        border-radius: 3px;
    }}"""

    def generate_tab_styles(self) -> str:
        """Generate tab widget styles."""
        primary_color = self.color_pickers.get('Primary', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()
        background_color = self.color_pickers.get('Background', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()
        
        return f"""QTabWidget::pane {{
        border: 1px solid #C0C0C0;
        top: -1px;
        background-color: {background_color};
    }}

    QTabBar::tab {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E1E1E1, stop: 0.4 #DDDDDD, stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
        border: 1px solid #C4C4C3;
        border-bottom-color: #C2C7CB;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 8ex;
        padding: 4px 8px;
    }}

    QTabBar::tab:selected {{
        background-color: {primary_color};
        color: white;
    }}

    QTabBar::tab:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #fafafa, stop: 0.4 #f4f4f4, stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
    }}"""

    def generate_table_styles(self) -> str:
        """Generate table widget styles."""
        background_color = self.color_pickers.get('Background', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()
        primary_color = self.color_pickers.get('Primary', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()
        
        return f"""QTableWidget {{
        gridline-color: #d0d0d0;
        background-color: {background_color};
        alternate-background-color: #f0f0f0;
        selection-background-color: {primary_color};
    }}

    QHeaderView::section {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #616161, stop: 0.5 #505050, stop: 0.6 #434343, stop:1 #656565);
        color: white;
        padding-left: 4px;
        border: 1px solid #6c6c6c;
    }}"""

    def generate_frame_styles(self) -> str:
        """Generate frame styles."""
        border_color = self.border_color.styleSheet().split('background-color:')[1].split(';')[0].strip()
        
        return f"""QFrame[frameShape="1"] {{ /* Panel */
        border: 2px solid {border_color};
        border-radius: {self.border_radius.value()}px;
    }}

    QFrame[frameShape="2"] {{ /* StyledPanel */
        border: 2px groove {border_color};
        border-radius: {self.border_radius.value()}px;
    }}

    QFrame[frameShape="3"] {{ /* HLine */
        border: none;
        border-top: 1px solid {border_color};
    }}

    QFrame[frameShape="4"] {{ /* VLine */
        border: none;
        border-left: 1px solid {border_color};
    }}"""

    def generate_button_styles(self) -> str:
        """Generate button-specific styles."""
        primary_color = \
        self.color_pickers.get('Primary', QPushButton()).styleSheet().split('background-color:')[1].split(';')[
            0].strip()

        # Generate box shadow if enabled
        box_shadow = ""
        if hasattr(self, 'shadow_enabled') and self.shadow_enabled.isChecked():
            shadow_type = "inset " if hasattr(self, 'shadow_inset') and self.shadow_inset.isChecked() else ""
            box_shadow = f"box-shadow: {shadow_type}{self.shadow_x.value()}px {self.shadow_y.value()}px {self.shadow_blur.value()}px {self.shadow_spread.value()}px {self.shadow_color.styleSheet().split('background-color:')[1].split(';')[0].strip()};"

        # Generate transition
        transition = ""
        if hasattr(self, 'transition_duration'):
            transition = f"transition: {self.transition_property.currentText()} {self.transition_duration.value()}ms {self.transition_timing.currentText()} {self.transition_delay.value()}ms;"

        styles = f"""QPushButton {{
        background-color: {primary_color};
        border: {self.border_width.value()}px {self.border_style.currentText()} {self.border_color.styleSheet().split('background-color:')[1].split(';')[0].strip()};
        border-radius: {self.border_radius.value()}px;
        padding: {self.numeric_inputs.get('padding_top', QSpinBox()).value()}px {self.numeric_inputs.get('padding_right', QSpinBox()).value()}px;
        font-weight: {self.numeric_inputs.get('font_weight_Medium', QSpinBox()).value()};
        {box_shadow}
        {transition}
    }}

    QPushButton:hover {{
        background-color: {self.color_pickers.get('Secondary', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()};
        {self.generate_hover_effects()}
    }}

    QPushButton:pressed {{
        background-color: {self.color_pickers.get('Accent', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()};
    }}

    QPushButton:disabled {{
        background-color: #cccccc;
        color: #666666;
    }}"""

        return styles

    def generate_input_styles(self) -> str:
        """Generate input element styles."""
        styles = f"""QLineEdit, QTextEdit, QSpinBox, QComboBox {{
        background-color: {self.color_pickers.get('Background', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()};
        border: {self.border_width.value()}px {self.border_style.currentText()} {self.border_color.styleSheet().split('background-color:')[1].split(';')[0].strip()};
        border-radius: {self.border_radius.value()}px;
        padding: {self.numeric_inputs.get('padding_top', QSpinBox()).value()}px;
    }}

    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border-color: {self.color_pickers.get('Primary', QPushButton()).styleSheet().split('background-color:')[1].split(';')[0].strip()};
        outline: none;
    }}"""

        return styles

    def generate_hover_effects(self) -> str:
        """Generate hover effect styles."""
        effects = []

        if hasattr(self, 'hover_scale') and self.hover_scale.isChecked():
            effects.append("transform: scale(1.05);")

        if hasattr(self, 'hover_rotate') and self.hover_rotate.isChecked():
            effects.append("transform: rotate(2deg);")

        if hasattr(self, 'hover_shadow') and self.hover_shadow.isChecked():
            effects.append(f"box-shadow: 0 5px 15px rgba(0,0,0,0.3);")

        return "\n    ".join(effects)

    # Event handlers and utility methods

    def new_theme(self):
        """Create a new theme."""
        reply = QMessageBox.question(self, "New Theme",
                                     "Create a new theme? Unsaved changes will be lost.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.reset_all_values()
            self.update_preview()
            self.status_label.setText("New theme created")

    def open_theme(self):
        """Open an existing theme file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Theme", "",
            "Theme Files (*.json *.css *.qss);;All Files (*.*)"
        )

        if filename:
            try:
                if filename.endswith('.json'):
                    self.load_json_theme(filename)
                elif filename.endswith(('.css', '.qss')):
                    self.load_css_file(filename)

                self.status_label.setText(f"Loaded: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load theme: {str(e)}")

    def save_theme(self):
        """Save the current theme."""
        if not hasattr(self, 'current_filename'):
            self.save_theme_as()
        else:
            self.save_to_file(self.current_filename)

    def save_theme_as(self):
        """Save the current theme with a new name."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Theme", "",
            "JSON Theme (*.json);;CSS File (*.css);;Qt Stylesheet (*.qss)"
        )

        if filename:
            self.save_to_file(filename)
            self.current_filename = filename

    def save_to_file(self, filename: str):
        """Save theme to the specified file."""
        try:
            if filename.endswith('.json'):
                self.export_json_theme_to_file(filename)
            elif filename.endswith(('.css', '.qss')):
                self.export_css_to_file(filename)

            self.status_label.setText(f"Saved: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save theme: {str(e)}")

    def undo(self):
        """Undo the last change."""
        if self.undo_stack:
            state = self.undo_stack.pop()
            self.redo_stack.append(self.get_current_state())
            self.restore_state(state)
            self.update_preview()
            self.status_label.setText("Undo performed")

    def redo(self):
        """Redo the last undone change."""
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(self.get_current_state())
            self.restore_state(state)
            self.update_preview()
            self.status_label.setText("Redo performed")

    def add_to_undo_stack(self):
        """Add current state to undo stack."""
        if len(self.undo_stack) >= self.max_undo_levels:
            self.undo_stack.pop(0)

        self.undo_stack.append(self.get_current_state())
        self.redo_stack.clear()

    def get_current_state(self) -> dict:
        """Get the current state of all controls."""
        state = {
            'colors': {},
            'fonts': {},
            'numeric': {},
            'combos': {},
            'checks': {},
            'text': {}
        }

        # Save color states
        for name, picker in self.color_pickers.items():
            state['colors'][name] = picker.styleSheet()

        # Save font states
        for name, selector in self.font_selectors.items():
            state['fonts'][name] = selector.currentFont().family()

        # Save numeric states
        for name, spin in self.numeric_inputs.items():
            state['numeric'][name] = spin.value()

        # Save combo states
        for name, combo in self.combo_boxes.items():
            state['combos'][name] = combo.currentText()

        # Save checkbox states
        for name, check in self.checkboxes.items():
            state['checks'][name] = check.isChecked()

        # Save text content
        state['text']['custom_css'] = self.custom_css.toPlainText()

        return state

    def restore_state(self, state: dict):
        """Restore controls to a previous state."""
        # Restore colors
        for name, style in state.get('colors', {}).items():
            if name in self.color_pickers:
                self.color_pickers[name].setStyleSheet(style)

        # Restore fonts
        for name, family in state.get('fonts', {}).items():
            if name in self.font_selectors:
                self.font_selectors[name].setCurrentFont(QFont(family))

        # Restore numeric values
        for name, value in state.get('numeric', {}).items():
            if name in self.numeric_inputs:
                self.numeric_inputs[name].setValue(value)

        # Restore combo selections
        for name, text in state.get('combos', {}).items():
            if name in self.combo_boxes:
                self.combo_boxes[name].setCurrentText(text)

        # Restore checkbox states
        for name, checked in state.get('checks', {}).items():
            if name in self.checkboxes:
                self.checkboxes[name].setChecked(checked)

        # Restore text content
        if 'custom_css' in state.get('text', {}):
            self.custom_css.setPlainText(state['text']['custom_css'])

    def load_preset_theme(self, preset_name: str):
        """Load a preset theme."""
        if preset_name == "Dark Sci-Fi":
            self.apply_dark_scifi_theme()
        elif preset_name == "Light Modern":
            self.apply_light_modern_theme()
        elif preset_name == "Material Dark":
            self.apply_material_dark_theme()
        elif preset_name == "Material Light":
            self.apply_material_light_theme()
        elif preset_name == "Cyberpunk":
            self.apply_cyberpunk_theme()
        elif preset_name == "Minimalist":
            self.apply_minimalist_theme()
        elif preset_name == "Corporate Blue":
            self.apply_corporate_blue_theme()
        elif preset_name == "Nature Green":
            self.apply_nature_green_theme()

        self.update_preview()
        self.status_label.setText(f"Loaded preset: {preset_name}")

    def apply_dark_scifi_theme(self):
        """Apply the dark sci-fi theme."""
        # Colors
        self.color_pickers['Background'].setStyleSheet("background-color: #121212; border: 1px solid #444;")
        self.color_pickers['Foreground'].setStyleSheet("background-color: #EEEEEE; border: 1px solid #444;")
        self.color_pickers['Primary'].setStyleSheet("background-color: #00FFAA; border: 1px solid #444;")
        self.color_pickers['Secondary'].setStyleSheet("background-color: #FF4500; border: 1px solid #444;")
        self.color_pickers['Accent'].setStyleSheet("background-color: #FFD700; border: 1px solid #444;")

        # Borders
        self.border_width.setValue(2)
        self.border_style.setCurrentText("solid")
        self.border_color.setStyleSheet("background-color: #2D2D2D; border: 1px solid #444;")
        self.border_radius.setValue(8)

        # Effects
        if hasattr(self, 'shadow_enabled'):
            self.shadow_enabled.setChecked(True)
            self.shadow_blur.setValue(15)
            self.shadow_color.setStyleSheet("background-color: rgba(0,255,170,0.3); border: 1px solid #444;")

    def apply_light_modern_theme(self):
        """Apply a light modern theme."""
        self.color_pickers['Background'].setStyleSheet("background-color: #FFFFFF; border: 1px solid #444;")
        self.color_pickers['Foreground'].setStyleSheet("background-color: #333333; border: 1px solid #444;")
        self.color_pickers['Primary'].setStyleSheet("background-color: #2196F3; border: 1px solid #444;")
        self.color_pickers['Secondary'].setStyleSheet("background-color: #FFC107; border: 1px solid #444;")
        self.color_pickers['Accent'].setStyleSheet("background-color: #4CAF50; border: 1px solid #444;")

    def apply_material_dark_theme(self):
        """Apply Material Design dark theme."""
        self.color_pickers['Background'].setStyleSheet("background-color: #212121; border: 1px solid #444;")
        self.color_pickers['Foreground'].setStyleSheet("background-color: #FFFFFF; border: 1px solid #444;")
        self.color_pickers['Primary'].setStyleSheet("background-color: #BB86FC; border: 1px solid #444;")
        self.color_pickers['Secondary'].setStyleSheet("background-color: #03DAC6; border: 1px solid #444;")
        self.color_pickers['Accent'].setStyleSheet("background-color: #CF6679; border: 1px solid #444;")

    def apply_material_light_theme(self):
        """Apply Material Design light theme."""
        self.color_pickers['Background'].setStyleSheet("background-color: #FAFAFA; border: 1px solid #444;")
        self.color_pickers['Foreground'].setStyleSheet("background-color: #212121; border: 1px solid #444;")
        self.color_pickers['Primary'].setStyleSheet("background-color: #6200EE; border: 1px solid #444;")
        self.color_pickers['Secondary'].setStyleSheet("background-color: #03DAC6; border: 1px solid #444;")
        self.color_pickers['Accent'].setStyleSheet("background-color: #B00020; border: 1px solid #444;")

    def apply_cyberpunk_theme(self):
        """Apply cyberpunk theme."""
        self.color_pickers['Background'].setStyleSheet("background-color: #0A0A0A; border: 1px solid #444;")
        self.color_pickers['Foreground'].setStyleSheet("background-color: #FF00FF; border: 1px solid #444;")
        self.color_pickers['Primary'].setStyleSheet("background-color: #00FFFF; border: 1px solid #444;")
        self.color_pickers['Secondary'].setStyleSheet("background-color: #FF1493; border: 1px solid #444;")
        self.color_pickers['Accent'].setStyleSheet("background-color: #FFFF00; border: 1px solid #444;")

    def apply_minimalist_theme(self):
        """Apply minimalist theme."""
        self.color_pickers['Background'].setStyleSheet("background-color: #F5F5F5; border: 1px solid #444;")
        self.color_pickers['Foreground'].setStyleSheet("background-color: #333333; border: 1px solid #444;")
        self.color_pickers['Primary'].setStyleSheet("background-color: #000000; border: 1px solid #444;")
        self.color_pickers['Secondary'].setStyleSheet("background-color: #666666; border: 1px solid #444;")
        self.color_pickers['Accent'].setStyleSheet("background-color: #E0E0E0; border: 1px solid #444;")

    def apply_corporate_blue_theme(self):
        """Apply corporate blue theme."""
        self.color_pickers['Background'].setStyleSheet("background-color: #F0F4F8; border: 1px solid #444;")
        self.color_pickers['Foreground'].setStyleSheet("background-color: #1A365D; border: 1px solid #444;")
        self.color_pickers['Primary'].setStyleSheet("background-color: #2B6CB0; border: 1px solid #444;")
        self.color_pickers['Secondary'].setStyleSheet("background-color: #4299E1; border: 1px solid #444;")
        self.color_pickers['Accent'].setStyleSheet("background-color: #ED8936; border: 1px solid #444;")

    def apply_nature_green_theme(self):
        """Apply nature green theme."""
        self.color_pickers['Background'].setStyleSheet("background-color: #F7FAFC; border: 1px solid #444;")
        self.color_pickers['Foreground'].setStyleSheet("background-color: #22543D; border: 1px solid #444;")
        self.color_pickers['Primary'].setStyleSheet("background-color: #48BB78; border: 1px solid #444;")
        self.color_pickers['Secondary'].setStyleSheet("background-color: #38A169; border: 1px solid #444;")
        self.color_pickers['Accent'].setStyleSheet("background-color: #F6E05E; border: 1px solid #444;")

    def reset_all_values(self):
        """Reset all values to defaults."""
        # Reset colors
        for picker in self.color_pickers.values():
            picker.setStyleSheet("background-color: #FFFFFF; border: 1px solid #444;")

        # Reset numeric values
        for spin in self.numeric_inputs.values():
            if isinstance(spin, QSpinBox):
                spin.setValue(spin.minimum())
            elif isinstance(spin, QDoubleSpinBox):
                spin.setValue(spin.minimum())

        # Reset combos
        for combo in self.combo_boxes.values():
            combo.setCurrentIndex(0)

        # Reset checkboxes
        for check in self.checkboxes.values():
            check.setChecked(False)

        # Clear custom CSS
        self.custom_css.clear()

    def change_preview_device(self, device: str):
        """Change the preview device size."""
        if device == "Desktop":
            self.preview_content.setMaximumWidth(1200)
        elif device == "Tablet":
            self.preview_content.setMaximumWidth(768)
        elif device == "Mobile":
            self.preview_content.setMaximumWidth(375)

    def toggle_linked_margins(self, linked: bool):
        """Toggle linked margin controls."""
        if linked:
            # Link all margins to top margin value
            value = self.numeric_inputs['margin_top'].value()
            for side in ['right', 'bottom', 'left']:
                self.numeric_inputs[f'margin_{side}'].setValue(value)
                self.numeric_inputs[f'margin_{side}'].setEnabled(False)
        else:
            # Unlink margins
            for side in ['right', 'bottom', 'left']:
                self.numeric_inputs[f'margin_{side}'].setEnabled(True)

    def toggle_linked_padding(self, linked: bool):
        """Toggle linked padding controls."""
        if linked:
            # Link all padding to top padding value
            value = self.numeric_inputs['padding_top'].value()
            for side in ['right', 'bottom', 'left']:
                self.numeric_inputs[f'padding_{side}'].setValue(value)
                self.numeric_inputs[f'padding_{side}'].setEnabled(False)
        else:
            # Unlink padding
            for side in ['right', 'bottom', 'left']:
                self.numeric_inputs[f'padding_{side}'].setEnabled(True)

    def toggle_individual_borders(self, enabled: bool):
        """Toggle individual border controls."""
        self.individual_border_widget.setVisible(enabled)

    def toggle_individual_corners(self, enabled: bool):
        """Toggle individual corner controls."""
        self.corner_widget.setVisible(enabled)

    def toggle_multiple_shadows(self, enabled: bool):
        """Toggle multiple shadows."""
        # Placeholder for multiple shadow functionality
        pass

    def add_new_gradient(self):
        """Add a new gradient."""
        name, ok = QInputDialog.getText(self, "New Gradient", "Gradient name:")
        if ok and name:
            self.gradient_list.addItem(name)

    def add_new_animation(self):
        """Add a new animation."""
        name, ok = QInputDialog.getText(self, "New Animation", "Animation name:")
        if ok and name:
            self.animation_list.addItem(name)

    def add_keyframe(self):
        """Add a new keyframe."""
        # Placeholder for keyframe functionality
        pass

    def add_css_variable(self):
        """Add a CSS variable."""
        name, ok = QInputDialog.getText(self, "CSS Variable", "Variable name (without --):")
        if ok and name:
            value, ok = QInputDialog.getText(self, "CSS Variable", f"Value for --{name}:")
            if ok:
                self.css_vars_list.addItem(f"--{name}: {value}")

    def add_media_query(self):
        """Add a media query."""
        query, ok = QInputDialog.getText(self, "Media Query", "Media query condition:")
        if ok and query:
            self.media_list.addItem(f"@media {query}")

    def generate_color_palette(self):
        """Generate a color palette from base color."""
        # Placeholder for palette generation
        pass

    def load_widget_style(self, widget_name: str):
        """Load styles for a specific widget."""
        # Clear current state properties
        for widget in self.state_props_layout.children():
            if hasattr(widget, 'deleteLater'):
                widget.deleteLater()

    def load_json_theme(self, filename: str):
        """Load theme from JSON file."""
        try:
            with open(filename, 'r') as f:
                theme_data = json.load(f)
                
                # Show import preview
                self.import_preview.setPlainText(f"Loaded theme: {theme_data.get('metadata', {}).get('description', 'Unknown theme')}")
                
                # Apply loaded theme data
                self.apply_theme_data(theme_data)
                self.update_preview()
                
                self.status_label.setText(f"Loaded JSON theme: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON theme: {str(e)}")

    def load_css_file(self, filename: str):
        """Load CSS file."""
        try:
            with open(filename, 'r') as f:
                css_content = f.read()
                
                # Show import preview  
                self.import_preview.setPlainText(css_content[:500] + "..." if len(css_content) > 500 else css_content)
                
                # Clear current settings and apply CSS
                self.custom_css.setPlainText(css_content)
                self.update_preview()
                
                self.status_label.setText(f"Loaded CSS file: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSS file: {str(e)}")

    def apply_theme_data(self, theme_data: dict):
        """Apply theme data to controls."""
        # Apply colors
        if 'colors' in theme_data:
            for name, style in theme_data['colors'].items():
                if name in self.color_pickers:
                    self.color_pickers[name].setStyleSheet(style)
        
        # Apply fonts
        if 'fonts' in theme_data:
            for name, family in theme_data['fonts'].items():
                if name in self.font_selectors:
                    self.font_selectors[name].setCurrentFont(QFont(family))
        
        # Apply numeric values
        if 'numeric' in theme_data:
            for name, value in theme_data['numeric'].items():
                if name in self.numeric_inputs:
                    self.numeric_inputs[name].setValue(value)
        
        # Apply combo selections
        if 'combos' in theme_data:
            for name, text in theme_data['combos'].items():
                if name in self.combo_boxes:
                    self.combo_boxes[name].setCurrentText(text)
        
        # Apply checkbox states
        if 'checks' in theme_data:
            for name, checked in theme_data['checks'].items():
                if name in self.checkboxes:
                    self.checkboxes[name].setChecked(checked)
        
        # Apply custom CSS
        if 'text' in theme_data and 'custom_css' in theme_data['text']:
            self.custom_css.setPlainText(theme_data['text']['custom_css'])

    def import_css_file(self):
        """Import CSS file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import CSS File", "", "CSS Files (*.css);;All Files (*.*)"
        )
        if filename:
            self.load_css_file(filename)

    def import_json_theme(self):
        """Import JSON theme."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import JSON Theme", "", "JSON Files (*.json);;All Files (*.*)"
        )
        if filename:
            self.load_json_theme(filename)

    def import_qt_stylesheet(self):
        """Import Qt stylesheet."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Qt Stylesheet", "", "Qt Stylesheets (*.qss);;All Files (*.*)"
        )
        if filename:
            self.load_css_file(filename)

    def export_css_file(self):
        """Export as CSS file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export CSS", "", "CSS Files (*.css);;All Files (*.*)"
        )
        if filename:
            self.export_css_to_file(filename)

    def export_json_theme(self):
        """Export as JSON theme."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export JSON Theme", "", "JSON Files (*.json);;All Files (*.*)"
        )
        if filename:
            self.export_json_theme_to_file(filename)

    def export_qt_stylesheet(self):
        """Export as Qt stylesheet."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Qt Stylesheet", "", "Qt Stylesheets (*.qss);;All Files (*.*)"
        )
        if filename:
            self.export_css_to_file(filename)

    def export_css_to_file(self, filename: str):
        """Export CSS to file."""
        try:
            css = self.generate_stylesheet()
            
            # Add header comment if requested
            if self.include_comments.isChecked():
                header = f"""/*
 * PyQt6 Theme Generated by Theme Editor
 * Generated: {QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate)}
 * 
 * This theme can be applied to any PyQt6 application using:
 * app.setStyleSheet(open('theme.qss').read())
 */

"""
                css = header + css
            
            # Minify if requested
            if self.minify_export.isChecked():
                css = self.minify_css(css)
            
            with open(filename, 'w') as f:
                f.write(css)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSS: {str(e)}")

    def export_json_theme_to_file(self, filename: str):
        """Export theme as JSON to file."""
        try:
            theme_data = self.get_current_state()
            
            # Add metadata
            theme_data['metadata'] = {
                'version': '1.0.0',
                'created': QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate),
                'generator': 'PyQt6 Theme Editor',
                'description': 'Theme configuration for PyQt6 applications'
            }
            
            # Include generated CSS for reference
            theme_data['generated_css'] = self.generate_stylesheet()
            
            with open(filename, 'w') as f:
                json.dump(theme_data, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export JSON: {str(e)}")

    def minify_css(self, css: str) -> str:
        """Minify CSS by removing unnecessary whitespace and comments."""
        import re
        
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        
        # Remove extra whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r';\s*}', '}', css)
        css = re.sub(r'{\s*', '{', css)
        css = re.sub(r'}\s*', '}', css)
        css = re.sub(r':\s*', ':', css)
        css = re.sub(r';\s*', ';', css)
        
        return css.strip()

    def copy_export_to_clipboard(self):
        """Copy export content to clipboard."""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.export_preview.toPlainText())
        self.status_label.setText("Copied to clipboard")

    def load_default_theme(self):
        """Load default theme values."""
        self.apply_dark_scifi_theme()


class ThemeEditorMainWindow(QMainWindow):
    """Main window for the theme editor application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Theme Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create the style editor as central widget
        self.style_editor = StyleEditor(self)
        self.setCentralWidget(self.style_editor)
        
        # Apply initial theme to the main window
        self.style_editor.style_changed.connect(self.apply_theme)
    
    def apply_theme(self, css: str):
        """Apply the generated theme to the main window."""
        self.setStyleSheet(css)


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("PyQt6 Theme Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Theme Editor")
    
    # Create and show main window
    window = ThemeEditorMainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()