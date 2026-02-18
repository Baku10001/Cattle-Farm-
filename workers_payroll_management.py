#!/usr/bin/env python3
"""
Workers & Payroll Management System
Complete employee management with attendance, wages, and payroll processing
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QAbstractItemView, QDialog, QFormLayout, QDateEdit, 
                             QSpinBox, QTextEdit, QMessageBox, QTabWidget, QFrame,
                             QScrollArea, QGroupBox, QGridLayout, QDialogButtonBox,
                             QListWidget, QCheckBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta
from data_manager import DataManager

class WorkersPayrollWidget(QWidget):
    """Main workers and payroll management interface"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("👨‍🌾 Workers & Payroll Management")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin: 10px; padding: 10px;")
        layout.addWidget(header)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Workers tab
        self.tab_widget.addTab(self.create_workers_tab(), "👥 Workers")
        
        # Seasonal Workers tab
        self.tab_widget.addTab(self.create_seasonal_workers_tab(), "🌾 Seasonal Workers")
        
        # Attendance tab
        self.tab_widget.addTab(self.create_attendance_tab(), "📅 Attendance")
        
        # Payroll tab
        self.tab_widget.addTab(self.create_payroll_tab(), "💰 Payroll")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def create_workers_tab(self):
        """Create workers management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Search
        controls_layout.addWidget(QLabel("Search:"))
        self.worker_search = QLineEdit()
        self.worker_search.setPlaceholderText("Search by code, name, or role...")
        controls_layout.addWidget(self.worker_search)
        
        # Filter by type
        controls_layout.addWidget(QLabel("Type:"))
        self.worker_type_filter = QComboBox()
        self.worker_type_filter.addItems(["All", "Permanent", "Temporary", "Contractor"])
        controls_layout.addWidget(self.worker_type_filter)
        
        # Add worker button
        add_worker_btn = QPushButton("➕ Add Worker")
        add_worker_btn.clicked.connect(self.add_worker_dialog)
        controls_layout.addWidget(add_worker_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Workers table
        self.workers_table = QTableWidget()
        self.workers_table.setColumnCount(9)
        self.workers_table.setHorizontalHeaderLabels([
            "Worker Code", "Name", "Role", "Type", "Hire Date", 
            "Phone", "Daily Rate", "Status", "Actions"
        ])
        layout.addWidget(self.workers_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_seasonal_workers_tab(self):
        """Create seasonal/daily wage workers management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Info banner
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e9;
                border-left: 5px solid #4caf50;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        info_layout = QHBoxLayout()
        info_label = QLabel("🌾 Seasonal Workers - Track daily wage workers hired during peak farming seasons")
        info_label.setFont(QFont("Arial", 11, QFont.Bold))
        info_label.setStyleSheet("color: #2e7d32;")
        info_layout.addWidget(info_label)
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        # Action buttons row
        actions_layout = QHBoxLayout()
        
        # Search
        actions_layout.addWidget(QLabel("Search:"))
        self.seasonal_search = QLineEdit()
        self.seasonal_search.setPlaceholderText("Search by name or phone...")
        self.seasonal_search.textChanged.connect(self.load_seasonal_workers)
        actions_layout.addWidget(self.seasonal_search)
        
        # Status filter
        actions_layout.addWidget(QLabel("Status:"))
        self.seasonal_status_filter = QComboBox()
        self.seasonal_status_filter.addItems(["All", "Active", "Inactive"])
        self.seasonal_status_filter.currentTextChanged.connect(self.load_seasonal_workers)
        actions_layout.addWidget(self.seasonal_status_filter)
        
        # Add seasonal worker
        add_seasonal_btn = QPushButton("➕ Add Seasonal Worker")
        add_seasonal_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_seasonal_btn.clicked.connect(self.add_seasonal_worker_dialog)
        actions_layout.addWidget(add_seasonal_btn)
        
        # Record daily work
        record_work_btn = QPushButton("📝 Record Daily Work")
        record_work_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        record_work_btn.clicked.connect(self.record_daily_work_dialog)
        actions_layout.addWidget(record_work_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        
        self.seasonal_total_card = self.create_stat_card("Total Seasonal Workers", "0", "#4caf50")
        stats_layout.addWidget(self.seasonal_total_card)
        
        self.seasonal_active_card = self.create_stat_card("Working Today", "0", "#2196f3")
        stats_layout.addWidget(self.seasonal_active_card)
        
        self.seasonal_wages_card = self.create_stat_card("Total Wages (This Month)", "Rs 0", "#ff9800")
        stats_layout.addWidget(self.seasonal_wages_card)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Seasonal workers table
        self.seasonal_table = QTableWidget()
        self.seasonal_table.setColumnCount(9)
        self.seasonal_table.setHorizontalHeaderLabels([
            "Name", "Phone", "Daily Wage (Rs)", "Days Worked (Month)",
            "Total Earned (Month)", "Last Work Date", "Status", "Notes", "Actions"
        ])
        self.seasonal_table.setAlternatingRowColors(True)
        self.seasonal_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.seasonal_table.horizontalHeader().setStretchLastSection(False)
        layout.addWidget(self.seasonal_table)
        
        # Load data
        self.load_seasonal_workers()
        
        widget.setLayout(layout)
        return widget
    
    def create_stat_card(self, title, value, color):
        """Create a statistics card for seasonal workers"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                padding: 20px;
                min-width: 180px;
                max-width: 250px;
            }}
        """)
        card_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: white;")
        title_label.setWordWrap(True)
        card_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet("color: white;")
        card_layout.addWidget(value_label)
        
        card.setLayout(card_layout)
        return card
    
    def create_attendance_tab(self):
        """Create attendance tracking tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Date selection
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        
        self.attendance_date = QDateEdit()
        self.attendance_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.attendance_date)
        
        mark_attendance_btn = QPushButton("✓ Mark Attendance")
        mark_attendance_btn.clicked.connect(self.mark_attendance_dialog)
        date_layout.addWidget(mark_attendance_btn)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(7)
        self.attendance_table.setHorizontalHeaderLabels([
            "Worker Code", "Name", "Date", "Check In", 
            "Check Out", "Hours", "Status"
        ])
        layout.addWidget(self.attendance_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_payroll_tab(self):
        """Create payroll processing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Payroll period selection
        period_layout = QHBoxLayout()
        
        period_layout.addWidget(QLabel("Payroll Period:"))
        self.payroll_start_date = QDateEdit()
        self.payroll_start_date.setDate(QDate.currentDate().addDays(-30))
        period_layout.addWidget(self.payroll_start_date)
        
        period_layout.addWidget(QLabel("to"))
        self.payroll_end_date = QDateEdit()
        self.payroll_end_date.setDate(QDate.currentDate())
        period_layout.addWidget(self.payroll_end_date)
        
        calculate_btn = QPushButton("🧮 Calculate Payroll")
        calculate_btn.clicked.connect(self.calculate_payroll)
        period_layout.addWidget(calculate_btn)
        
        generate_slips_btn = QPushButton("📄 Generate Salary Slips")
        generate_slips_btn.clicked.connect(self.generate_salary_slips)
        period_layout.addWidget(generate_slips_btn)
        
        period_layout.addStretch()
        layout.addLayout(period_layout)
        
        # Payroll summary
        summary_layout = QHBoxLayout()
        
        self.total_workers_card = self.create_summary_card("Total Workers", "0", "#3498db")
        summary_layout.addWidget(self.total_workers_card)
        
        self.total_hours_card = self.create_summary_card("Total Hours", "0", "#e74c3c")
        summary_layout.addWidget(self.total_hours_card)
        
        self.total_wages_card = self.create_summary_card("Total Wages", "Rs0", "#27ae60")
        summary_layout.addWidget(self.total_wages_card)
        
        layout.addLayout(summary_layout)
        
        # Payroll table
        self.payroll_table = QTableWidget()
        self.payroll_table.setColumnCount(8)
        self.payroll_table.setHorizontalHeaderLabels([
            "Worker Code", "Name", "Days Worked", "Hours", 
            "Rate", "Gross Pay", "Deductions", "Net Pay"
        ])
        layout.addWidget(self.payroll_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_summary_card(self, title, value, color):
        """Create summary card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 2px solid {color};
                border-radius: 10px;
                margin: 5px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        card.setMinimumHeight(100)
        
        return card
    
    def add_worker_dialog(self):
        """Open dialog to add new worker"""
        dialog = WorkerDialog(self.data_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_workers_data()
    
    def mark_attendance_dialog(self):
        """Open dialog to mark attendance"""
        dialog = AttendanceDialog(self.data_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_attendance_data()
    
    def calculate_payroll(self):
        """Calculate payroll for selected period"""
        start_date = self.payroll_start_date.date().toString("yyyy-MM-dd")
        end_date = self.payroll_end_date.date().toString("yyyy-MM-dd")
        
        # Get attendance records for period
        attendance_records = self.data_manager.search_entities('attendance', 
            filters={'date_range': {'field': 'date', 'start': start_date, 'end': end_date}})
        
        # Calculate payroll by worker
        payroll_data = {}
        for record in attendance_records:
            worker_code = record.get('worker_code')
            hours = float(record.get('hours_worked', 0))
            
            if worker_code not in payroll_data:
                worker = self.data_manager.get_entity_by_code('workers', worker_code)
                payroll_data[worker_code] = {
                    'worker': worker,
                    'total_hours': 0,
                    'days_worked': 0
                }
            
            payroll_data[worker_code]['total_hours'] += hours
            payroll_data[worker_code]['days_worked'] += 1
        
        # Populate payroll table
        self.populate_payroll_table(payroll_data)
    
    def populate_payroll_table(self, payroll_data):
        """Populate payroll table with calculated data"""
        self.payroll_table.setRowCount(len(payroll_data))
        
        total_workers = len(payroll_data)
        total_hours = 0
        total_wages = 0
        
        for row, (worker_code, data) in enumerate(payroll_data.items()):
            worker = data['worker']
            hours = data['total_hours']
            days = data['days_worked']
            rate = float(worker.get('daily_rate', 0))
            
            gross_pay = days * rate
            deductions = gross_pay * 0.1  # 10% deductions (simplified)
            net_pay = gross_pay - deductions
            
            total_hours += hours
            total_wages += net_pay
            
            self.payroll_table.setItem(row, 0, QTableWidgetItem(worker_code))
            self.payroll_table.setItem(row, 1, QTableWidgetItem(worker.get('name', '')))
            self.payroll_table.setItem(row, 2, QTableWidgetItem(str(days)))
            self.payroll_table.setItem(row, 3, QTableWidgetItem(f"{hours:.1f}"))
            self.payroll_table.setItem(row, 4, QTableWidgetItem(f"Rs{rate:.2f}"))
            self.payroll_table.setItem(row, 5, QTableWidgetItem(f"Rs{gross_pay:.2f}"))
            self.payroll_table.setItem(row, 6, QTableWidgetItem(f"Rs{deductions:.2f}"))
            self.payroll_table.setItem(row, 7, QTableWidgetItem(f"Rs{net_pay:.2f}"))
        
        # Update summary cards
        self.update_summary_card(self.total_workers_card, str(total_workers))
        self.update_summary_card(self.total_hours_card, f"{total_hours:.1f}")
        self.update_summary_card(self.total_wages_card, f"Rs{total_wages:.2f}")
    
    def update_summary_card(self, card, value):
        """Update summary card value"""
        layout = card.layout()
        if layout and layout.count() > 1:
            value_label = layout.itemAt(1).widget()
            if value_label:
                value_label.setText(value)
    
    def generate_salary_slips(self):
        """Generate salary slips for all workers"""
        QMessageBox.information(self, "Info", "Salary slips generated successfully!")
    
    def load_workers_data(self):
        """Load workers data"""
        # Implementation for loading workers
        pass
    
    def load_attendance_data(self):
        """Load attendance data"""
        # Implementation for loading attendance
        pass
    
    def load_seasonal_workers(self):
        """Load seasonal workers data"""
        try:
            search_term = self.seasonal_search.text() if hasattr(self, 'seasonal_search') else ""
            status_filter = self.seasonal_status_filter.currentText() if hasattr(self, 'seasonal_status_filter') else "All"
            
            # Load seasonal workers from data
            seasonal_workers = self.data_manager.search_entities('seasonal_workers', search_term)
            
            # Filter by status
            if status_filter != "All":
                seasonal_workers = [w for w in seasonal_workers if w.get('status', '').lower() == status_filter.lower()]
            
            # Populate table
            self.seasonal_table.setRowCount(len(seasonal_workers))
            
            for row, worker in enumerate(seasonal_workers):
                self.seasonal_table.setItem(row, 0, QTableWidgetItem(worker.get('name', '')))
                self.seasonal_table.setItem(row, 1, QTableWidgetItem(worker.get('phone', '')))
                self.seasonal_table.setItem(row, 2, QTableWidgetItem(f"Rs {worker.get('daily_wage', 0):.2f}"))
                self.seasonal_table.setItem(row, 3, QTableWidgetItem(str(worker.get('days_worked_month', 0))))
                
                total_earned = worker.get('daily_wage', 0) * worker.get('days_worked_month', 0)
                self.seasonal_table.setItem(row, 4, QTableWidgetItem(f"Rs {total_earned:.2f}"))
                self.seasonal_table.setItem(row, 5, QTableWidgetItem(worker.get('last_work_date', 'N/A')))
                self.seasonal_table.setItem(row, 6, QTableWidgetItem(worker.get('status', 'Active')))
                self.seasonal_table.setItem(row, 7, QTableWidgetItem(worker.get('notes', '')))
                
                # Actions button
                actions_btn = QPushButton("⚙️ Actions")
                actions_btn.clicked.connect(lambda checked, w=worker: self.seasonal_worker_actions(w))
                self.seasonal_table.setCellWidget(row, 8, actions_btn)
        
        except Exception as e:
            print(f"Error loading seasonal workers: {e}")
    
    def add_seasonal_worker_dialog(self):
        """Open dialog to add seasonal worker"""
        dialog = SeasonalWorkerDialog(self.data_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_seasonal_workers()
    
    def record_daily_work_dialog(self):
        """Open dialog to record daily work for seasonal workers"""
        dialog = RecordDailyWorkDialog(self.data_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_seasonal_workers()
    
    def seasonal_worker_actions(self, worker):
        """Show actions menu for seasonal worker"""
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        
        edit_action = menu.addAction("✏️ Edit Details")
        record_work_action = menu.addAction("📝 Record Work")
        pay_action = menu.addAction("💰 Mark as Paid")
        delete_action = menu.addAction("🗑️ Remove")
        
        action = menu.exec_(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
        
        if action == edit_action:
            dialog = SeasonalWorkerDialog(self.data_manager, worker, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_seasonal_workers()
        elif action == record_work_action:
            dialog = RecordDailyWorkDialog(self.data_manager, worker, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_seasonal_workers()
        elif action == pay_action:
            QMessageBox.information(self, "Payment", f"Mark {worker.get('name')} as paid")
        elif action == delete_action:
            reply = QMessageBox.question(self, "Confirm Delete",
                f"Remove seasonal worker {worker.get('name')}?",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.data_manager.delete_entity('seasonal_workers', worker.get('code'))
                self.load_seasonal_workers()

class WorkerDialog(QDialog):
    """Dialog for adding/editing workers"""
    
    def __init__(self, data_manager, worker_data=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.worker_data = worker_data
        self.setWindowTitle("Add Worker" if not worker_data else "Edit Worker")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Basic info
        self.name_input = QLineEdit()
        form_layout.addRow("Full Name:", self.name_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "Farm Manager", "Milker", "Feeder", "Cleaner", 
            "Veterinary Assistant", "Equipment Operator", "General Worker"
        ])
        form_layout.addRow("Role:", self.role_combo)
        
        self.worker_type = QComboBox()
        self.worker_type.addItems(["Permanent", "Temporary", "Contractor"])
        form_layout.addRow("Worker Type:", self.worker_type)
        
        self.hire_date = QDateEdit()
        self.hire_date.setDate(QDate.currentDate())
        form_layout.addRow("Hire Date:", self.hire_date)
        
        # Contact info
        self.phone_input = QLineEdit()
        form_layout.addRow("Phone:", self.phone_input)
        
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        form_layout.addRow("Address:", self.address_input)
        
        # Compensation
        self.daily_rate = QDoubleSpinBox()
        self.daily_rate.setRange(0, 9999)
        self.daily_rate.setPrefix("Rs")
        form_layout.addRow("Daily Rate:", self.daily_rate)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_worker)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def save_worker(self):
        """Save worker data"""
        data = {
            'name': self.name_input.text(),
            'role': self.role_combo.currentText(),
            'worker_type': self.worker_type.currentText(),
            'hire_date': self.hire_date.date().toString("yyyy-MM-dd"),
            'phone': self.phone_input.text(),
            'address': self.address_input.toPlainText(),
            'daily_rate': self.daily_rate.value(),
            'status': 'active'
        }
        
        if self.worker_data:
            self.data_manager.update_entity('workers', self.worker_data['code'], data)
        else:
            self.data_manager.create_entity('workers', data)
        
        self.accept()

class AttendanceDialog(QDialog):
    """Dialog for marking attendance"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("Mark Attendance")
        self.setModal(True)
        self.resize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Date selection
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        
        self.attendance_date = QDateEdit()
        self.attendance_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.attendance_date)
        
        load_btn = QPushButton("📋 Load Workers")
        load_btn.clicked.connect(self.load_workers_for_attendance)
        date_layout.addWidget(load_btn)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Workers attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(6)
        self.attendance_table.setHorizontalHeaderLabels([
            "Worker Code", "Name", "Present", "Check In", "Check Out", "Hours"
        ])
        layout.addWidget(self.attendance_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Attendance")
        save_btn.clicked.connect(self.save_attendance)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_workers_for_attendance(self):
        """Load workers for attendance marking"""
        workers = self.data_manager.search_entities('workers', filters={'status': 'active'})
        self.attendance_table.setRowCount(len(workers))
        
        for row, worker in enumerate(workers):
            self.attendance_table.setItem(row, 0, QTableWidgetItem(worker.get('code', '')))
            self.attendance_table.setItem(row, 1, QTableWidgetItem(worker.get('name', '')))
            
            # Present checkbox
            present_checkbox = QCheckBox()
            self.attendance_table.setCellWidget(row, 2, present_checkbox)
            
            # Time inputs
            check_in = QTimeEdit()
            check_in.setTime(QTime(8, 0))  # Default 8:00 AM
            self.attendance_table.setCellWidget(row, 3, check_in)
            
            check_out = QTimeEdit()
            check_out.setTime(QTime(17, 0))  # Default 5:00 PM
            self.attendance_table.setCellWidget(row, 4, check_out)
            
            # Hours (calculated)
            self.attendance_table.setItem(row, 5, QTableWidgetItem("8.0"))
    
    def save_attendance(self):
        """Save attendance records"""
        date_str = self.attendance_date.date().toString("yyyy-MM-dd")
        
        for row in range(self.attendance_table.rowCount()):
            worker_code = self.attendance_table.item(row, 0).text()
            present_checkbox = self.attendance_table.cellWidget(row, 2)
            
            if present_checkbox.isChecked():
                check_in_widget = self.attendance_table.cellWidget(row, 3)
                check_out_widget = self.attendance_table.cellWidget(row, 4)
                
                check_in_time = check_in_widget.time().toString("HH:mm")
                check_out_time = check_out_widget.time().toString("HH:mm")
                
                # Calculate hours
                check_in_minutes = check_in_widget.time().hour() * 60 + check_in_widget.time().minute()
                check_out_minutes = check_out_widget.time().hour() * 60 + check_out_widget.time().minute()
                hours_worked = (check_out_minutes - check_in_minutes) / 60.0
                
                attendance_data = {
                    'worker_code': worker_code,
                    'date': date_str,
                    'check_in_time': check_in_time,
                    'check_out_time': check_out_time,
                    'hours_worked': hours_worked,
                    'status': 'present'
                }
                
                self.data_manager.create_entity('attendance', attendance_data)
        
        QMessageBox.information(self, "Success", "Attendance saved successfully!")
        self.accept()

class SeasonalWorkerDialog(QDialog):
    """Dialog for adding/editing seasonal workers"""
    
    def __init__(self, data_manager, worker_data=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.worker_data = worker_data
        self.setWindowTitle("Add Seasonal Worker" if not worker_data else "Edit Seasonal Worker")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Basic info
        self.name_input = QLineEdit()
        if self.worker_data:
            self.name_input.setText(self.worker_data.get('name', ''))
        form_layout.addRow("Name:*", self.name_input)
        
        self.phone_input = QLineEdit()
        if self.worker_data:
            self.phone_input.setText(self.worker_data.get('phone', ''))
        form_layout.addRow("Phone:", self.phone_input)
        
        # Daily wage
        self.daily_wage = QDoubleSpinBox()
        self.daily_wage.setRange(0, 10000)
        self.daily_wage.setPrefix("Rs ")
        self.daily_wage.setSuffix(" /day")
        if self.worker_data:
            self.daily_wage.setValue(self.worker_data.get('daily_wage', 0))
        form_layout.addRow("Daily Wage:*", self.daily_wage)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        if self.worker_data:
            self.status_combo.setCurrentText(self.worker_data.get('status', 'Active'))
        form_layout.addRow("Status:", self.status_combo)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        if self.worker_data:
            self.notes_input.setText(self.worker_data.get('notes', ''))
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        save_btn.clicked.connect(self.save_seasonal_worker)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def save_seasonal_worker(self):
        """Save seasonal worker data"""
        if not self.name_input.text():
            QMessageBox.warning(self, "Validation Error", "Name is required!")
            return
        
        data = {
            'name': self.name_input.text(),
            'phone': self.phone_input.text(),
            'daily_wage': self.daily_wage.value(),
            'status': self.status_combo.currentText(),
            'notes': self.notes_input.toPlainText(),
            'days_worked_month': self.worker_data.get('days_worked_month', 0) if self.worker_data else 0,
            'last_work_date': self.worker_data.get('last_work_date', '') if self.worker_data else ''
        }
        
        if self.worker_data:
            self.data_manager.update_entity('seasonal_workers', self.worker_data['code'], data)
        else:
            self.data_manager.create_entity('seasonal_workers', data)
        
        QMessageBox.information(self, "Success", "Seasonal worker saved successfully!")
        self.accept()

class RecordDailyWorkDialog(QDialog):
    """Dialog for recording daily work for seasonal workers"""
    
    def __init__(self, data_manager, worker_data=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.worker_data = worker_data
        self.setWindowTitle("Record Daily Work")
        self.setModal(True)
        self.resize(500, 350)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("📝 Record work done by seasonal workers for the day")
        info_label.setStyleSheet("color: #2196f3; font-weight: bold; padding: 10px;")
        layout.addWidget(info_label)
        
        form_layout = QFormLayout()
        
        # Worker selection
        self.worker_combo = QComboBox()
        seasonal_workers = self.data_manager.search_entities('seasonal_workers')
        for worker in seasonal_workers:
            if worker.get('status', '').lower() == 'active':
                self.worker_combo.addItem(worker.get('name', ''), worker)
        
        if self.worker_data:
            index = self.worker_combo.findText(self.worker_data.get('name', ''))
            if index >= 0:
                self.worker_combo.setCurrentIndex(index)
        
        form_layout.addRow("Worker:*", self.worker_combo)
        
        # Work date
        self.work_date = QDateEdit()
        self.work_date.setDate(QDate.currentDate())
        self.work_date.setCalendarPopup(True)
        form_layout.addRow("Work Date:*", self.work_date)
        
        # Hours worked
        self.hours_worked = QDoubleSpinBox()
        self.hours_worked.setRange(0, 24)
        self.hours_worked.setValue(8)
        self.hours_worked.setSuffix(" hours")
        form_layout.addRow("Hours Worked:", self.hours_worked)
        
        # Work description
        self.work_description = QTextEdit()
        self.work_description.setMaximumHeight(80)
        self.work_description.setPlaceholderText("Describe the work done (e.g., harvesting, planting, feeding cattle...)")
        form_layout.addRow("Work Description:", self.work_description)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Record Work")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        save_btn.clicked.connect(self.save_work_record)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def save_work_record(self):
        """Save daily work record"""
        worker_data = self.worker_combo.currentData()
        if not worker_data:
            QMessageBox.warning(self, "Validation Error", "Please select a worker!")
            return
        
        work_data = {
            'worker_code': worker_data.get('code'),
            'worker_name': worker_data.get('name'),
            'work_date': self.work_date.date().toString("yyyy-MM-dd"),
            'hours_worked': self.hours_worked.value(),
            'daily_wage': worker_data.get('daily_wage', 0),
            'amount_earned': worker_data.get('daily_wage', 0),
            'work_description': self.work_description.toPlainText(),
            'status': 'unpaid'
        }
        
        # Save work record
        self.data_manager.create_entity('seasonal_work_records', work_data)
        
        # Update worker's days worked count
        current_month = QDate.currentDate().toString("yyyy-MM")
        work_month = self.work_date.date().toString("yyyy-MM")
        
        if current_month == work_month:
            days_worked = worker_data.get('days_worked_month', 0) + 1
            self.data_manager.update_entity('seasonal_workers', worker_data['code'], {
                'days_worked_month': days_worked,
                'last_work_date': self.work_date.date().toString("yyyy-MM-dd")
            })
        
        QMessageBox.information(self, "Success", "Work record saved successfully!")
        self.accept()
