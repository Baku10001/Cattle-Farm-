#!/usr/bin/env python3
"""
Dairy Farm Management System - Main Application
Comprehensive farm management with financial integration
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QAbstractItemView, QDialog, QFormLayout, 
                             QDateEdit, QSpinBox, QTextEdit, QMessageBox, QTabWidget, 
                             QFrame, QScrollArea, QGroupBox, QGridLayout, QDialogButtonBox,
                             QListWidget, QCheckBox, QDoubleSpinBox, QMenuBar, QAction,
                             QFileDialog, QProgressBar, QSplashScreen)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

from data_manager import DataManager
from financial_management import FinancialManagementWidget
from herd_management import HerdManagementWidget
from workers_payroll_management import WorkersPayrollWidget
from milk_management import MilkManagementWidget
from feed_management import FeedManagementWidget
from lactation_management_ui import LactationManagementWidget
from reporting_engine import ReportingEngine

class DashboardWidget(QWidget):
    """Enhanced dashboard with financial KPIs and farm analytics"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        self.update_dashboard()
        
        # Auto-refresh every 30 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(30000)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🏢 Dairy Farm Management Dashboard")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        header_layout.addWidget(title)
        
        # Quick actions
        quick_actions = QHBoxLayout()
        
        add_cattle_btn = QPushButton("🐄 Add Cattle")
        add_cattle_btn.setStyleSheet("QPushButton { padding: 8px 16px; font-weight: bold; }")
        add_cattle_btn.clicked.connect(self.open_add_cattle)
        quick_actions.addWidget(add_cattle_btn)
        
        record_milk_btn = QPushButton("🥛 Record Milk")
        record_milk_btn.setStyleSheet("QPushButton { padding: 8px 16px; font-weight: bold; }")
        record_milk_btn.clicked.connect(self.open_record_milk)
        quick_actions.addWidget(record_milk_btn)
        
        add_expense_btn = QPushButton("💸 Add Expense")
        add_expense_btn.setStyleSheet("QPushButton { padding: 8px 16px; font-weight: bold; }")
        add_expense_btn.clicked.connect(self.open_add_expense)
        quick_actions.addWidget(add_expense_btn)
        
        header_layout.addLayout(quick_actions)
        layout.addLayout(header_layout)
        
        # Main content in scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # All KPI Cards in one layout
        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(10)
        kpi_layout.setContentsMargins(10, 10, 10, 10)
        
        self.kpi_cards = {}
        all_kpis = [
            ('revenue', 'Monthly Revenue', 'Rs0', '💰', '#27ae60'),
            ('expenses', 'Monthly Expenses', 'Rs0', '💸', '#e74c3c'),
            ('profit', 'Net Profit', 'Rs0', '📈', '#3498db'),
            ('ar_balance', 'A/R Balance', 'Rs0', '💳', '#f39c12'),
            ('ap_balance', 'A/P Balance', 'Rs0', '📋', '#9b59b6'),
            ('cash_flow', 'Cash Flow', 'Rs0', '💵', '#1abc9c'),
            ('total_cattle', 'Total Cattle', '0', '🐄', '#34495e'),
            ('milk_production', 'Daily Milk', '0L', '🥛', '#3498db'),
            ('active_workers', 'Active Workers', '0', '👥', '#e67e22'),
            ('feed_inventory', 'Feed Items', '0', '🌾', '#f39c12'),
            ('health_alerts', 'Health Alerts', '0', '🚨', '#e74c3c'),
            ('breeding_due', 'Breeding Due', '0', '💕', '#8e44ad')
        ]
        
        for i, (key, title, value, icon, color) in enumerate(all_kpis):
            card = self.create_kpi_card(title, value, icon, color)
            self.kpi_cards[key] = card
            row, col = divmod(i, 3)
            kpi_layout.addWidget(card, row, col)
        
        # Add some stretch to prevent cramping
        kpi_layout.setRowStretch(kpi_layout.rowCount(), 1)
        scroll_layout.addLayout(kpi_layout)
        
        # Recent Activities
        activities_group = QGroupBox("📋 Recent Activities")
        activities_group.setFont(QFont("Arial", 14, QFont.Bold))
        activities_layout = QVBoxLayout()
        
        self.activities_list = QListWidget()
        self.activities_list.setMaximumHeight(200)
        activities_layout.addWidget(self.activities_list)
        
        activities_group.setLayout(activities_layout)
        scroll_layout.addWidget(activities_group)
        
        # Alerts and Notifications
        alerts_group = QGroupBox("🚨 Active Alerts")
        alerts_group.setFont(QFont("Arial", 14, QFont.Bold))
        alerts_layout = QVBoxLayout()
        
        self.alerts_list = QListWidget()
        self.alerts_list.setMaximumHeight(150)
        alerts_layout.addWidget(self.alerts_list)
        
        alerts_group.setLayout(alerts_layout)
        scroll_layout.addWidget(alerts_group)
        
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
    
    def create_kpi_card(self, title, value, icon, color):
        """Create smaller KPI card widget with muted colors"""
        # Convert vibrant colors to muted/pastel versions
        muted_colors = {
            '#27ae60': '#7fb3a3',  # Green → Muted teal-green
            '#e74c3c': '#d4a5a5',  # Red → Muted rose
            '#3498db': '#9bb8d3',  # Blue → Muted blue
            '#f39c12': '#e6c9a8',  # Orange → Muted peach
            '#9b59b6': '#c4b5d4',  # Purple → Muted lavender
            '#1abc9c': '#8ec9c8',  # Teal → Muted mint
            '#34495e': '#9ea7b0',  # Dark blue-gray → Muted gray-blue
            '#e67e22': '#dcbfa3',  # Dark orange → Muted tan
            '#8e44ad': '#b8a8c8',  # Dark purple → Muted purple
        }
        muted_color = muted_colors.get(color, '#b8c5d6')  # Default muted gray-blue
        
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {muted_color};
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin: 4px;
                padding: 0px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 12, 15, 12)
        
        # Smaller icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 28))
        icon_label.setStyleSheet("color: #5a6c7d; background: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setMinimumHeight(35)
        layout.addWidget(icon_label)
        
        # Smaller title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet("""
            color: #5a6c7d; 
            background: transparent;
            border: none;
        """)
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMinimumHeight(25)
        layout.addWidget(title_label)
        
        # Smaller value
        display_value = str(value) if value is not None and str(value).strip() else "0"
        value_label = QLabel(display_value)
        value_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        value_label.setStyleSheet("""
            color: #3d4f5f;
            background: transparent;
            border: none;
            padding: 5px;
        """)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setMinimumHeight(30)
        layout.addWidget(value_label)
        
        layout.addStretch()
        card.setLayout(layout)
        card.setMinimumHeight(140)
        card.setMinimumWidth(180)
        
        # Store references
        card.value_label = value_label
        card.title_label = title_label
        card.icon_label = icon_label
        card.original_color = muted_color
        
        # Subtle hover effects
        card.enterEvent = lambda event: self.card_hover_enter(card)
        card.leaveEvent = lambda event: self.card_hover_leave(card)
        
        return card
    
    def lighten_color(self, color):
        """Lighten a hex color slightly for hover effect"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * 1.1))
        g = min(255, int(g * 1.1))
        b = min(255, int(b * 1.1))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def card_hover_enter(self, card):
        """Handle card hover enter - subtle lightening"""
        color = card.original_color
        lighter_color = self.lighten_color(color)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {lighter_color};
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin: 4px;
                padding: 0px;
            }}
        """)
    
    def card_hover_leave(self, card):
        """Handle card hover leave - restore original color"""
        color = card.original_color
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin: 4px;
                padding: 0px;
            }}
        """)
    
    def update_dashboard(self):
        """Update dashboard with latest data"""
        try:
            # Get financial summary
            financial_summary = self.data_manager.get_financial_summary()
            
            # Update financial KPIs
            self.update_kpi_card('revenue', f"Rs{financial_summary.get('total_revenue', 0):,.2f}")
            self.update_kpi_card('expenses', f"Rs{financial_summary.get('total_expenses', 0):,.2f}")
            self.update_kpi_card('profit', f"Rs{financial_summary.get('net_profit', 0):,.2f}")
            
            # Get operational data
            cattle_count = len(self.data_manager.search_entities('cattle'))
            workers_count = len(self.data_manager.search_entities('workers', filters={'status': 'active'}))
            
            # Get milk production data
            milk_data = self.data_manager.load_data('milk')
            production_records = milk_data.get('production', [])
            today = datetime.now().strftime('%Y-%m-%d')
            today_production = sum(r.get('quantity', 0) for r in production_records if r.get('date') == today)
            
            # Get feed inventory data
            feed_items = self.data_manager.load_data('feed_inventory')
            feed_count = len(feed_items)
            
            # Get health alerts
            health_alerts = 0  # Placeholder - would integrate with health module
            
            # Get breeding due count
            breeding_due = 0  # Placeholder - would integrate with breeding module
            
            self.update_kpi_card('total_cattle', str(cattle_count))
            self.update_kpi_card('milk_production', f"{today_production:.1f}L")
            self.update_kpi_card('active_workers', str(workers_count))
            self.update_kpi_card('feed_inventory', str(feed_count))
            self.update_kpi_card('health_alerts', str(health_alerts))
            self.update_kpi_card('breeding_due', str(breeding_due))
            
            # Update recent activities
            self.update_recent_activities()
            
            # Update alerts
            self.update_alerts()
            
        except Exception as e:
            print(f"Error updating dashboard: {e}")
    
    def open_add_cattle(self):
        """Open add cattle dialog"""
        try:
            from herd_management import CattleDialog
            dialog = CattleDialog(self.data_manager, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.update_dashboard()  # Refresh after adding
        except Exception as e:
            print(f"Error opening add cattle dialog: {e}")
    
    def open_record_milk(self):
        """Open record milk dialog"""
        try:
            from milk_management import MilkProductionDialog
            dialog = MilkProductionDialog(parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.update_dashboard()  # Refresh after recording
        except Exception as e:
            print(f"Error opening record milk dialog: {e}")
    
    def open_add_expense(self):
        """Open add expense dialog"""
        try:
            from transaction_dialog import TransactionDialog
            dialog = TransactionDialog(self.data_manager, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.update_dashboard()  # Refresh after adding expense
        except Exception as e:
            print(f"Error opening add expense dialog: {e}")
    
    def update_kpi_card(self, key, value):
        """Update KPI card value"""
        if key in self.kpi_cards:
            card = self.kpi_cards[key]
            if hasattr(card, 'value_label'):
                # Ensure value is properly displayed
                display_value = str(value) if value is not None and str(value).strip() else "0"
                card.value_label.setText(display_value)
                card.value_label.repaint()  # Force repaint
    
    def update_recent_activities(self):
        """Update recent activities list"""
        self.activities_list.clear()
        
        # Add sample activities (would be populated from actual data)
        activities = [
            "🐄 New cattle COW-2412-0001 added to herd",
            "🥛 Daily milk production recorded: 450L",
            "💰 Invoice INV-2412-0001 generated for Rs1,250",
            "👥 Worker attendance marked for 8 employees",
            "🌾 Feed inventory updated - Low stock alert for corn"
        ]
        
        for activity in activities:
            self.activities_list.addItem(activity)
    
    def update_alerts(self):
        """Update alerts list"""
        self.alerts_list.clear()
        
        # Add sample alerts (would be populated from actual data)
        alerts = [
            "🚨 3 cattle due for vaccination this week",
            "⚠️ Feed inventory low: Corn silage (2 days remaining)",
            "💳 Overdue invoices: Rs2,500 (5 customers)",
            "🏥 Health check due for COW-2412-0005"
        ]
        
        for alert in alerts:
            self.alerts_list.addItem(alert)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏢 Dairy Farm Management System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Menu bar
        self.create_menu_bar()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 3px solid #3498db;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #d5dbdb);
            }
        """)
        
        # Add modules
        self.dashboard = DashboardWidget(self.data_manager)
        self.tab_widget.addTab(self.dashboard, "📊 Dashboard")
        
        # Financial Management
        self.financial_widget = FinancialManagementWidget(self.data_manager)
        self.tab_widget.addTab(self.financial_widget, "💰 Financial")
        
        # Herd Management
        self.herd_widget = HerdManagementWidget(self.data_manager)
        self.tab_widget.addTab(self.herd_widget, "🐄 Herd")
        
        # Workers & Payroll
        self.workers_widget = WorkersPayrollWidget(self.data_manager)
        self.tab_widget.addTab(self.workers_widget, "👥 Workers")
        
        # Milk Management
        self.milk_widget = MilkManagementWidget(self.data_manager)
        self.tab_widget.addTab(self.milk_widget, "🥛 Milk")
        
        # Lactation Cycle Management
        self.lactation_widget = LactationManagementWidget(self.data_manager)
        self.tab_widget.addTab(self.lactation_widget, "🔄 Lactation")
        
        # Feed Management
        self.feed_widget = FeedManagementWidget(self.data_manager)
        self.tab_widget.addTab(self.feed_widget, "🌾 Feed")
        
        # Reports & Analytics
        self.reports_widget = self.create_reports_widget()
        self.tab_widget.addTab(self.reports_widget, "📊 Reports")
        
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
    
    def create_reports_widget(self):
        """Create the reports and analytics widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("📊 Reports & Analytics")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Initialize reporting engine
        self.reporting_engine = ReportingEngine(self.data_manager)
        
        # Report generation buttons
        reports_group = QGroupBox("📋 Generate Reports")
        reports_layout = QGridLayout()
        
        # Financial Reports
        financial_reports = [
            ("💰 Profit & Loss Statement", self.generate_profit_loss),
            ("📊 Balance Sheet", self.generate_balance_sheet),
            ("💵 Cash Flow Statement", self.generate_cash_flow),
            ("📈 Comprehensive Farm Report", self.generate_farm_report)
        ]
        
        for i, (text, callback) in enumerate(financial_reports):
            btn = QPushButton(text)
            btn.setStyleSheet("QPushButton { padding: 10px; font-weight: bold; }")
            btn.clicked.connect(callback)
            row, col = divmod(i, 2)
            reports_layout.addWidget(btn, row, col)
        
        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)
        
        # Export options
        export_group = QGroupBox("📤 Export Data")
        export_layout = QGridLayout()
        
        export_options = [
            ("🐄 Export Cattle Data", lambda: self.export_entity_data('cattle')),
            ("👥 Export Workers Data", lambda: self.export_entity_data('workers')),
            ("🥛 Export Milk Records", lambda: self.export_entity_data('milk')),
            ("🌾 Export Feed Inventory", lambda: self.export_entity_data('feed_inventory'))
        ]
        
        for i, (text, callback) in enumerate(export_options):
            btn = QPushButton(text)
            btn.setStyleSheet("QPushButton { padding: 10px; font-weight: bold; }")
            btn.clicked.connect(callback)
            row, col = divmod(i, 2)
            export_layout.addWidget(btn, row, col)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Analytics dashboard placeholder
        analytics_group = QGroupBox("📈 Analytics Dashboard")
        analytics_layout = QVBoxLayout()
        
        analytics_info = QLabel("Real-time analytics and KPI tracking:\n\n"
                               "• Financial performance metrics\n"
                               "• Herd productivity analysis\n"
                               "• Feed efficiency tracking\n"
                               "• Milk production trends\n"
                               "• Cost analysis and profitability")
        analytics_info.setStyleSheet("color: #6c757d; padding: 20px;")
        analytics_layout.addWidget(analytics_info)
        
        analytics_group.setLayout(analytics_layout)
        layout.addWidget(analytics_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def generate_profit_loss(self):
        """Generate Profit & Loss Statement"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Profit & Loss Statement", 
            f"ProfitLoss_{self.get_timestamp()}.pdf",
            "PDF files (*.pdf)"
        )
        
        if filename:
            if self.reporting_engine.generate_financial_statement_pdf("Profit & Loss Statement", filename):
                QMessageBox.information(self, "Success", "Profit & Loss Statement generated successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate report!")
    
    def generate_balance_sheet(self):
        """Generate Balance Sheet"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Balance Sheet", 
            f"BalanceSheet_{self.get_timestamp()}.pdf",
            "PDF files (*.pdf)"
        )
        
        if filename:
            if self.reporting_engine.generate_financial_statement_pdf("Balance Sheet", filename):
                QMessageBox.information(self, "Success", "Balance Sheet generated successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate report!")
    
    def generate_cash_flow(self):
        """Generate Cash Flow Statement"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Cash Flow Statement", 
            f"CashFlow_{self.get_timestamp()}.pdf",
            "PDF files (*.pdf)"
        )
        
        if filename:
            if self.reporting_engine.generate_financial_statement_pdf("Cash Flow Statement", filename):
                QMessageBox.information(self, "Success", "Cash Flow Statement generated successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate report!")
    
    def generate_farm_report(self):
        """Generate Comprehensive Farm Report"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Farm Report", 
            f"FarmReport_{self.get_timestamp()}.pdf",
            "PDF files (*.pdf)"
        )
        
        if filename:
            if self.reporting_engine.generate_comprehensive_farm_report(filename, 'pdf'):
                QMessageBox.information(self, "Success", "Comprehensive Farm Report generated successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate report!")
    
    def export_entity_data(self, entity_type):
        """Export entity data in various formats"""
        format_dialog = QMessageBox()
        format_dialog.setWindowTitle("Select Export Format")
        format_dialog.setText(f"Choose export format for {entity_type} data:")
        
        pdf_btn = format_dialog.addButton("PDF", QMessageBox.ActionRole)
        excel_btn = format_dialog.addButton("Excel", QMessageBox.ActionRole)
        csv_btn = format_dialog.addButton("CSV", QMessageBox.ActionRole)
        format_dialog.addButton(QMessageBox.Cancel)
        
        format_dialog.exec_()
        
        if format_dialog.clickedButton() == pdf_btn:
            self._export_data(entity_type, 'pdf')
        elif format_dialog.clickedButton() == excel_btn:
            self._export_data(entity_type, 'excel')
        elif format_dialog.clickedButton() == csv_btn:
            self._export_data(entity_type, 'csv')
    
    def _export_data(self, entity_type, format_type):
        """Export data in specified format"""
        extensions = {'pdf': '*.pdf', 'excel': '*.xlsx', 'csv': '*.csv'}
        
        filename, _ = QFileDialog.getSaveFileName(
            self, f"Export {entity_type.title()} Data", 
            f"{entity_type}_{self.get_timestamp()}.{format_type if format_type != 'excel' else 'xlsx'}",
            f"{format_type.upper()} files ({extensions[format_type]})"
        )
        
        if filename:
            if self.reporting_engine.export_entity_data(entity_type, filename, format_type):
                QMessageBox.information(self, "Success", f"{entity_type.title()} data exported successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to export data!")

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('📁 File')
        
        backup_action = QAction('💾 Backup System', self)
        backup_action.triggered.connect(self.backup_system)
        file_menu.addAction(backup_action)
        
        restore_action = QAction('📥 Restore System', self)
        restore_action.triggered.connect(self.restore_system)
        file_menu.addAction(restore_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('❌ Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('🔧 Tools')
        
        search_action = QAction('🔍 Global Search', self)
        search_action.triggered.connect(self.open_global_search)
        tools_menu.addAction(search_action)
        
        # Help menu
        help_menu = menubar.addMenu('❓ Help')
        
        about_action = QAction('ℹ️ About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_theme(self):
        """Apply modern theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
                border-radius: 4px;
            }
            QMenu {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #ecf0f1;
            }
        """)
    
    def backup_system(self):
        """Create system backup"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save System Backup", 
            f"farm_backup_{self.get_timestamp()}.zip",
            "ZIP files (*.zip)"
        )
        
        if filename:
            if self.data_manager.backup_system(filename):
                QMessageBox.information(self, "Success", "System backup created successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to create backup!")
    
    def restore_system(self):
        """Restore system from backup"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", "", "ZIP files (*.zip)"
        )
        
        if filename:
            reply = QMessageBox.question(
                self, "Confirm Restore",
                "This will replace all current data. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.data_manager.restore_system(filename):
                    QMessageBox.information(self, "Success", "System restored successfully!")
                    self.dashboard.update_dashboard()
                else:
                    QMessageBox.warning(self, "Error", "Failed to restore system!")
    
    def open_global_search(self):
        """Open global search dialog"""
        dialog = GlobalSearchDialog(self.data_manager, self)
        dialog.exec_()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", 
            "Dairy Farm Management System\n"
            "Version 2.0\n\n"
            "Complete farm management solution with:\n"
            "• Financial Management (GL, A/R, A/P)\n"
            "• Herd Management with Breeding\n"
            "• Workers & Payroll\n"
            "• Professional Reporting\n"
            "• Unique coding system for all entities\n\n"
            "Built for professional dairy operations")
    
    def get_timestamp(self):
        """Get current timestamp for filenames"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

class GlobalSearchDialog(QDialog):
    """Global search dialog for searching across all entities"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("🔍 Global Search")
        self.setModal(True)
        self.resize(900, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🔍 Search Across All Farm Data")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(header)
        
        # Search controls
        search_layout = QHBoxLayout()
        
        # Search input
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term (code, name, phone, description...)")
        self.search_input.textChanged.connect(self.perform_search)
        self.search_input.setFont(QFont("Arial", 11))
        search_layout.addWidget(self.search_input)
        
        # Entity type filter
        search_layout.addWidget(QLabel("Filter:"))
        self.entity_filter = QComboBox()
        self.entity_filter.addItems([
            "All Entities",
            "🐄 Cattle",
            "👥 Workers",
            "🌾 Seasonal Workers",
            "🥛 Milk Records",
            "🌾 Feed Inventory",
            "💰 Expenses",
            "📋 Invoices",
            "💳 Customers"
        ])
        self.entity_filter.currentTextChanged.connect(self.perform_search)
        search_layout.addWidget(self.entity_filter)
        
        # Search button
        search_btn = QPushButton("🔍 Search")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Results count
        self.results_label = QLabel("Enter search term to begin")
        self.results_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        layout.addWidget(self.results_label)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Entity Type", "Code", "Name/Description", "Details", "Date", "Actions"
        ])
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.results_table)
        
        # Close button
        close_btn = QPushButton("✖️ Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def perform_search(self):
        """Perform global search across all entities"""
        search_term = self.search_input.text().strip()
        
        if not search_term:
            self.results_label.setText("Enter search term to begin")
            self.results_table.setRowCount(0)
            return
        
        entity_filter = self.entity_filter.currentText()
        
        # Define entity types to search
        entity_types = {
            "All Entities": ['cattle', 'workers', 'seasonal_workers', 'milk', 'feed_inventory', 'expenses', 'invoices'],
            "🐄 Cattle": ['cattle'],
            "👥 Workers": ['workers'],
            "🌾 Seasonal Workers": ['seasonal_workers'],
            "🥛 Milk Records": ['milk'],
            "🌾 Feed Inventory": ['feed_inventory'],
            "💰 Expenses": ['expenses'],
            "📋 Invoices": ['invoices'],
            "💳 Customers": ['customers']
        }
        
        entities_to_search = entity_types.get(entity_filter, entity_types["All Entities"])
        
        # Perform search
        all_results = []
        
        for entity_type in entities_to_search:
            try:
                results = self.data_manager.search_entities(entity_type, search_term)
                for result in results:
                    all_results.append((entity_type, result))
            except Exception as e:
                print(f"Error searching {entity_type}: {e}")
        
        # Display results
        self.display_results(all_results, search_term)
    
    def display_results(self, results, search_term):
        """Display search results in table"""
        self.results_table.setRowCount(len(results))
        
        if len(results) == 0:
            self.results_label.setText(f"No results found for '{search_term}'")
            return
        
        self.results_label.setText(f"Found {len(results)} result(s) for '{search_term}'")
        
        entity_icons = {
            'cattle': '🐄',
            'workers': '👥',
            'seasonal_workers': '🌾',
            'milk': '🥛',
            'feed_inventory': '🌾',
            'expenses': '💰',
            'invoices': '📋',
            'customers': '💳'
        }
        
        for row, (entity_type, data) in enumerate(results):
            # Entity type with icon
            icon = entity_icons.get(entity_type, '📄')
            type_text = f"{icon} {entity_type.replace('_', ' ').title()}"
            self.results_table.setItem(row, 0, QTableWidgetItem(type_text))
            
            # Code
            code = data.get('code', data.get('id', 'N/A'))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(code)))
            
            # Name/Description
            name = data.get('name', data.get('description', data.get('worker_name', 'N/A')))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(name)))
            
            # Details
            details = self.get_entity_details(entity_type, data)
            self.results_table.setItem(row, 3, QTableWidgetItem(details))
            
            # Date
            date = data.get('created_date', data.get('date', data.get('hire_date', 'N/A')))
            if isinstance(date, str) and len(date) > 10:
                date = date[:10]
            self.results_table.setItem(row, 4, QTableWidgetItem(str(date)))
            
            # Actions button
            actions_btn = QPushButton("👁️ View")
            actions_btn.clicked.connect(lambda checked, e=entity_type, d=data: self.view_entity(e, d))
            self.results_table.setCellWidget(row, 5, actions_btn)
        
        # Resize columns
        self.results_table.resizeColumnsToContents()
    
    def get_entity_details(self, entity_type, data):
        """Get relevant details for each entity type"""
        if entity_type == 'cattle':
            return f"Breed: {data.get('breed', 'N/A')}, Status: {data.get('status', 'N/A')}"
        elif entity_type == 'workers':
            return f"Role: {data.get('role', 'N/A')}, Phone: {data.get('phone', 'N/A')}"
        elif entity_type == 'seasonal_workers':
            return f"Daily Wage: Rs {data.get('daily_wage', 0)}, Status: {data.get('status', 'N/A')}"
        elif entity_type == 'milk':
            return f"Quantity: {data.get('quantity', 0)}L, Quality: {data.get('quality_grade', 'N/A')}"
        elif entity_type == 'feed_inventory':
            return f"Stock: {data.get('current_stock', 0)} {data.get('unit', '')}"
        elif entity_type == 'expenses':
            return f"Amount: Rs {data.get('amount', 0)}, Category: {data.get('category', 'N/A')}"
        elif entity_type == 'invoices':
            return f"Amount: Rs {data.get('total_amount', 0)}, Status: {data.get('status', 'N/A')}"
        else:
            return "Click View for details"
    
    def view_entity(self, entity_type, data):
        """View entity details"""
        details_text = f"Entity Type: {entity_type.replace('_', ' ').title()}\n\n"
        
        for key, value in data.items():
            details_text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        msg = QMessageBox(self)
        msg.setWindowTitle(f"View {entity_type.title()}")
        msg.setText(details_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Dairy Farm Management System")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Farm Management Solutions")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
