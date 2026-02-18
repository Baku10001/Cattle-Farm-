from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame, QScrollArea, QGridLayout, QProgressBar,
                             QGraphicsDropShadowEffect, QSizePolicy, QSpacerItem,
                             QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
                             QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QRadioButton, QSlider, QTabWidget,
                             QGroupBox, QFormLayout, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, pyqtSignal
from PyQt5.QtGui import (QFont, QPalette, QColor, QPainter, QPen, QBrush, 
                         QLinearGradient, QPixmap, QIcon, QFontMetrics)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import os

class ModernCard(QFrame):
    """Modern card widget with shadow and hover effects."""
    
    def __init__(self, title="", content="", color="#3498db", parent=None):
        super().__init__(parent)
        self.title = title
        self.content = content
        self.color = color
        self.init_ui()
        self.add_shadow()
    
    def init_ui(self):
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                margin: 5px;
            }}
            ModernCard:hover {{
                border: 2px solid {self.color};
                background-color: #fafafa;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Title
        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            title_label.setStyleSheet(f"color: {self.color}; margin-bottom: 5px;")
            layout.addWidget(title_label)
        
        # Content
        if self.content:
            content_label = QLabel(self.content)
            content_label.setFont(QFont("Segoe UI", 10))
            content_label.setStyleSheet("color: #555; line-height: 1.4;")
            content_label.setWordWrap(True)
            layout.addWidget(content_label)
        
        self.setLayout(layout)
        self.setMinimumHeight(80)
    
    def add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

class StatCard(ModernCard):
    """Enhanced stat card with large numbers and trend indicators."""
    
    def __init__(self, title="", value="0", unit="", trend=None, color="#3498db", parent=None):
        self.value = value
        self.unit = unit
        self.trend = trend  # 'up', 'down', or None
        super().__init__(title, "", color, parent)
    
    def init_ui(self):
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet(f"""
            StatCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 white, stop:1 #f8f9fa);
                border-radius: 15px;
                border: 1px solid #e9ecef;
                margin: 8px;
                padding: 4px;
            }}
            StatCard:hover {{
                border: 2px solid {self.color};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f3f4);
            }}
            QLabel {{
                background: transparent;
            }}
        """)
        
        # Main layout with proper margins and spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(8)
        
        # Title with proper typography
        if self.title:
            title_label = QLabel(self.title, self)
            title_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
            title_label.setStyleSheet(f"color: #6c757d; margin: 0; padding: 0;")
            title_label.setWordWrap(True)
            title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            layout.addWidget(title_label, 0, Qt.AlignTop)
        
        # Value container with proper alignment
        value_container = QWidget(self)
        value_layout = QHBoxLayout(value_container)
        value_layout.setContentsMargins(0, 4, 0, 0)
        value_layout.setSpacing(8)
        
        # Main value with auto-sizing
        value_label = QLabel(str(self.value), self)
        value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Calculate optimal font size
        font = QFont("Segoe UI", 28, QFont.Bold)  # Start with smaller base size
        font_metrics = QFontMetrics(font)
        
        # Get text metrics with current font
        text = str(self.value)
        text_width = font_metrics.horizontalAdvance(text)
        text_height = font_metrics.height()
        
        # Calculate available space (accounting for margins and padding)
        max_width = 180
        max_height = 60
        
        # Adjust font size to fit
        while (text_width > max_width or text_height > max_height) and font.pointSize() > 14:
            font.setPointSize(font.pointSize() - 1)
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(text)
            text_height = font_metrics.height()
        
        value_label.setFont(font)
        value_label.setStyleSheet(f"color: {self.color}; margin: 0; padding: 0;")
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_layout.addWidget(value_label, 1)
        
        # Unit with proper alignment
        if self.unit:
            unit_label = QLabel(self.unit, self)
            unit_font = QFont("Segoe UI", 12, QFont.Medium)
            unit_label.setFont(unit_font)
            unit_label.setStyleSheet("color: #6c757d; margin: 0 0 0 4px; padding: 0;")
            unit_label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
            value_layout.addWidget(unit_label, 0, Qt.AlignBottom)
        
        # Add stretch to push content to the left
        value_layout.addStretch(1)
        
        # Trend indicator
        if self.trend:
            trend_color = "#28a745" if self.trend == 'up' else "#dc3545"
            trend_symbol = "↑" if self.trend == 'up' else "↓"
            trend_label = QLabel(trend_symbol, self)
            trend_font = QFont("Segoe UI", 16, QFont.Bold)
            trend_label.setFont(trend_font)
            trend_label.setStyleSheet(f"color: {trend_color}; margin: 0; padding: 0;")
            value_layout.addWidget(trend_label, 0, Qt.AlignBottom | Qt.AlignRight)
        
        layout.addWidget(value_container, 1)
        
        # Set size policies and minimum sizes
        self.setMinimumSize(200, 120)  # More compact minimum size
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # Store reference to value label for updates
        self.value_label = value_label
        
        # Store reference to value label for updates
        self.value_label = value_label
    
    def update_value(self, new_value, new_unit=None, new_trend=None):
        """Update the stat card value and optionally unit and trend."""
        self.value = new_value
        if new_unit is not None:
            self.unit = new_unit
        if new_trend is not None:
            self.trend = new_trend
        
        # Update the display
        self.value_label.setText(str(new_value))

class AlertCard(ModernCard):
    """Alert card with priority colors and dismiss functionality."""
    
    dismissed = pyqtSignal(int)
    
    def __init__(self, alert_data, index, parent=None):
        self.alert_data = alert_data
        self.index = index
        priority = alert_data.get('priority', 'medium')
        
        # Priority colors
        colors = {
            'high': '#dc3545',
            'medium': '#ffc107', 
            'low': '#17a2b8'
        }
        color = colors.get(priority, '#6c757d')
        
        super().__init__(
            alert_data.get('title', 'Alert'),
            alert_data.get('message', ''),
            color,
            parent
        )
    
    def init_ui(self):
        super().init_ui()
        
        # Add dismiss button
        dismiss_btn = QPushButton("×")
        dismiss_btn.setFixedSize(25, 25)
        dismiss_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c82333;
            }}
        """)
        dismiss_btn.clicked.connect(lambda: self.dismissed.emit(self.index))
        
        # Position dismiss button in top-right corner
        dismiss_btn.setParent(self)
        dismiss_btn.move(self.width() - 35, 10)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Reposition dismiss button when card is resized
        dismiss_btn = self.findChild(QPushButton)
        if dismiss_btn:
            dismiss_btn.move(self.width() - 35, 10)

class ModernChart(QWidget):
    """Modern chart widget using matplotlib with seaborn styling."""
    
    def __init__(self, chart_type='bar', title="Chart", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.title = title
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        # Set seaborn style
        sns.set_style("whitegrid")
        sns.set_palette("husl")
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_data(self, data, labels=None, colors=None):
        """Plot data based on chart type."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if self.chart_type == 'bar':
            bars = ax.bar(labels or range(len(data)), data, color=colors or sns.color_palette("husl", len(data)))
            ax.set_title(self.title, fontsize=14, fontweight='bold', pad=20)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom')
        
        elif self.chart_type == 'pie':
            wedges, texts, autotexts = ax.pie(data, labels=labels, autopct='%1.1f%%',
                                            colors=colors or sns.color_palette("husl", len(data)))
            ax.set_title(self.title, fontsize=14, fontweight='bold', pad=20)
            
            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        elif self.chart_type == 'line':
            ax.plot(labels or range(len(data)), data, marker='o', linewidth=3, markersize=8)
            ax.set_title(self.title, fontsize=14, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
        
        # Style improvements
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
        
        self.figure.tight_layout()
        self.canvas.draw()

class ModernProgressBar(QWidget):
    """Custom progress bar with modern styling."""
    
    def __init__(self, value=0, maximum=100, color="#3498db", parent=None):
        super().__init__(parent)
        self.value = value
        self.maximum = maximum
        self.color = color
        self.setMinimumHeight(25)
        self.setMaximumHeight(25)
    
    def setValue(self, value):
        self.value = max(0, min(value, self.maximum))
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.setBrush(QBrush(QColor("#e9ecef")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)
        
        # Progress
        if self.value > 0:
            progress_width = int((self.value / self.maximum) * self.width())
            progress_rect = QRect(0, 0, progress_width, self.height())
            
            gradient = QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, QColor(self.color))
            gradient.setColorAt(1, QColor(self.color).lighter(120))
            
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(progress_rect, 12, 12)
        
        # Text
        painter.setPen(QPen(QColor("#495057")))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        text = f"{self.value}/{self.maximum}"
        painter.drawText(self.rect(), Qt.AlignCenter, text)

class ModernButton(QPushButton):
    """Modern button with hover animations and different styles."""
    
    def __init__(self, text="", style="primary", icon=None, parent=None):
        super().__init__(text, parent)
        self.style_type = style
        self.setup_style()
        
        if icon:
            self.setIcon(QIcon(icon))
    
    def setup_style(self):
        styles = {
            'primary': {
                'bg': '#007bff',
                'hover': '#0056b3',
                'text': 'white'
            },
            'success': {
                'bg': '#28a745',
                'hover': '#1e7e34',
                'text': 'white'
            },
            'danger': {
                'bg': '#dc3545',
                'hover': '#c82333',
                'text': 'white'
            },
            'warning': {
                'bg': '#ffc107',
                'hover': '#e0a800',
                'text': '#212529'
            },
            'info': {
                'bg': '#17a2b8',
                'hover': '#138496',
                'text': 'white'
            },
            'secondary': {
                'bg': '#6c757d',
                'hover': '#545b62',
                'text': 'white'
            }
        }
        
        style = styles.get(self.style_type, styles['primary'])
        
        self.setStyleSheet(f"""
            ModernButton {{
                background-color: {style['bg']};
                color: {style['text']};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }}
            ModernButton:hover {{
                background-color: {style['hover']};
            }}
            ModernButton:pressed {{
                background-color: {style['hover']};
            }}
        """)
        
        self.setMinimumHeight(45)

class ModernInput(QLineEdit):
    """Modern input field with floating labels and validation."""
    
    def __init__(self, placeholder="", validation_type=None, parent=None):
        super().__init__(parent)
        self.placeholder_text = placeholder
        self.validation_type = validation_type
        self.setup_style()
    
    def setup_style(self):
        self.setStyleSheet("""
            ModernInput {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Segoe UI';
                background-color: white;
            }
            ModernInput:focus {
                border-color: #007bff;
                outline: none;
            }
            ModernInput:hover {
                border-color: #ced4da;
            }
        """)
        
        self.setPlaceholderText(self.placeholder_text)
        self.setMinimumHeight(45)

class ModernComboBox(QComboBox):
    """Modern combo box with enhanced styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
    
    def setup_style(self):
        self.setStyleSheet("""
            ModernComboBox {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Segoe UI';
                background-color: white;
                min-height: 21px;
            }
            ModernComboBox:focus {
                border-color: #007bff;
            }
            ModernComboBox:hover {
                border-color: #ced4da;
            }
            ModernComboBox::drop-down {
                border: none;
                width: 30px;
            }
            ModernComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6c757d;
                margin-right: 10px;
            }
        """)

class PhotoWidget(QWidget):
    """Widget for displaying and managing cow photos."""
    
    photo_changed = pyqtSignal(str)
    
    def __init__(self, photo_path=None, parent=None):
        super().__init__(parent)
        self.photo_path = photo_path
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Photo display area
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(200, 200)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ced4da;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setScaledContents(True)
        
        if self.photo_path and os.path.exists(self.photo_path):
            self.load_photo(self.photo_path)
        else:
            self.photo_label.setText("No Photo\nClick to add")
            self.photo_label.setStyleSheet(self.photo_label.styleSheet() + """
                QLabel {
                    color: #6c757d;
                    font-size: 14px;
                }
            """)
        
        # Make photo clickable
        self.photo_label.mousePressEvent = self.select_photo
        
        layout.addWidget(self.photo_label, alignment=Qt.AlignCenter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_btn = ModernButton("Select Photo", "primary")
        select_btn.clicked.connect(self.select_photo)
        
        remove_btn = ModernButton("Remove", "danger")
        remove_btn.clicked.connect(self.remove_photo)
        
        button_layout.addWidget(select_btn)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def select_photo(self, event=None):
        """Open file dialog to select photo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Cow Photo", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.load_photo(file_path)
            self.photo_changed.emit(file_path)
    
    def load_photo(self, photo_path):
        """Load and display photo."""
        if os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            scaled_pixmap = pixmap.scaled(
                self.photo_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.photo_label.setPixmap(scaled_pixmap)
            self.photo_path = photo_path
            
            # Update style for photo display
            self.photo_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #28a745;
                    border-radius: 10px;
                    background-color: white;
                }
            """)
    
    def remove_photo(self):
        """Remove current photo."""
        self.photo_label.clear()
        self.photo_label.setText("No Photo\nClick to add")
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ced4da;
                border-radius: 10px;
                background-color: #f8f9fa;
                color: #6c757d;
                font-size: 14px;
            }
        """)
        self.photo_path = None
        self.photo_changed.emit("")

class BodyConditionWidget(QWidget):
    """Widget for body condition scoring with visual indicators."""
    
    score_changed = pyqtSignal(float)
    
    def __init__(self, initial_score=3.0, parent=None):
        super().__init__(parent)
        self.score = initial_score
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Body Condition Score")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #495057; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Score slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(10, 50)  # 1.0 to 5.0 (multiplied by 10)
        self.slider.setValue(int(self.score * 10))
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(5)
        self.slider.valueChanged.connect(self.on_score_changed)
        
        # Custom slider styling
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dc3545, stop:0.25 #ffc107, 
                    stop:0.5 #28a745, stop:0.75 #ffc107, stop:1 #dc3545);
                height: 10px;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 2px solid #007bff;
                width: 20px;
                height: 20px;
                margin: -7px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #007bff;
            }
        """)
        
        layout.addWidget(self.slider)
        
        # Score display and description
        score_layout = QHBoxLayout()
        
        self.score_label = QLabel(f"{self.score:.1f}")
        self.score_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.score_label.setStyleSheet("color: #007bff;")
        
        self.description_label = QLabel(self.get_score_description(self.score))
        self.description_label.setFont(QFont("Segoe UI", 10))
        self.description_label.setStyleSheet("color: #6c757d;")
        
        score_layout.addWidget(self.score_label)
        score_layout.addWidget(self.description_label)
        score_layout.addStretch()
        
        layout.addLayout(score_layout)
        self.setLayout(layout)
    
    def on_score_changed(self, value):
        """Handle score change."""
        self.score = value / 10.0
        self.score_label.setText(f"{self.score:.1f}")
        self.description_label.setText(self.get_score_description(self.score))
        
        # Update score label color based on score
        if self.score < 2.5 or self.score > 4.0:
            color = "#dc3545"  # Red for poor condition
        elif self.score < 3.0 or self.score > 3.5:
            color = "#ffc107"  # Yellow for fair condition
        else:
            color = "#28a745"  # Green for good condition
        
        self.score_label.setStyleSheet(f"color: {color};")
        self.score_changed.emit(self.score)
    
    def get_score_description(self, score):
        """Get description for body condition score."""
        if score < 2.0:
            return "Very Thin - Immediate attention needed"
        elif score < 2.5:
            return "Thin - Needs improvement"
        elif score < 3.0:
            return "Moderate - Below optimal"
        elif score <= 3.5:
            return "Good - Optimal condition"
        elif score <= 4.0:
            return "Fat - Above optimal"
        else:
            return "Very Fat - Needs reduction"
    
    def set_score(self, score):
        """Set the body condition score."""
        self.score = max(1.0, min(5.0, score))
        self.slider.setValue(int(self.score * 10))
        self.on_score_changed(int(self.score * 10))

class NotificationWidget(QWidget):
    """Modern notification widget with auto-dismiss."""
    
    def __init__(self, message, notification_type="info", duration=5000, parent=None):
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.init_ui()
        
        # Auto-dismiss timer
        if duration > 0:
            QTimer.singleShot(duration, self.fade_out)
    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Type colors and icons
        type_config = {
            'success': {'color': '#28a745', 'icon': '✓'},
            'error': {'color': '#dc3545', 'icon': '✗'},
            'warning': {'color': '#ffc107', 'icon': '⚠'},
            'info': {'color': '#17a2b8', 'icon': 'ℹ'}
        }
        
        config = type_config.get(self.notification_type, type_config['info'])
        
        # Icon
        icon_label = QLabel(config['icon'])
        icon_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        icon_label.setStyleSheet(f"color: {config['color']};")
        icon_label.setFixedSize(30, 30)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setFont(QFont("Segoe UI", 11))
        message_label.setStyleSheet("color: #495057;")
        message_label.setWordWrap(True)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #6c757d;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #495057;
                background-color: #f8f9fa;
                border-radius: 12px;
            }
        """)
        close_btn.clicked.connect(self.fade_out)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Styling
        self.setStyleSheet(f"""
            NotificationWidget {{
                background-color: white;
                border-left: 4px solid {config['color']};
                border-radius: 8px;
                margin: 5px;
            }}
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
    
    def fade_out(self):
        """Fade out and remove notification."""
        self.setParent(None)
        self.deleteLater()
