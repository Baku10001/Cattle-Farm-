#!/usr/bin/env python3
"""
Lactation Management UI Widget
Interactive dashboard for cow milking cycle management
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QAbstractItemView, QDialog, QFormLayout, QDateEdit, 
                             QSpinBox, QTextEdit, QMessageBox, QTabWidget, QFrame,
                             QGroupBox, QGridLayout, QScrollArea, QSplitter,
                             QHeaderView, QDoubleSpinBox, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QPen, QBrush
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Optional

from lactation_management import (
    LactationDataManager, LactationRecord, BreedingEvent, HeatEvent,
    WoodsLactationCurve, LactationStageManager, FertilityAlertManager,
    LactationAnalytics, LactationStage, FertilityStatus
)
from modern_widgets import (ModernCard, StatCard, ModernButton, ModernInput, 
                           ModernComboBox, ModernChart, NotificationWidget)


class LactationCurveChart(QWidget):
    """Custom widget for displaying Wood's lactation curve"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.curve_data = []
        self.actual_data = []
        self.setMinimumHeight(250)
        self.setMinimumWidth(400)
    
    def set_data(self, curve_data: List[Dict], actual_data: List[Dict] = None):
        """Set curve data for visualization"""
        self.curve_data = curve_data
        self.actual_data = actual_data or []
        self.update()
    
    def paintEvent(self, event):
        """Paint the lactation curve"""
        if not self.curve_data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get dimensions
        width = self.width()
        height = self.height()
        margin = 50
        
        chart_width = width - 2 * margin
        chart_height = height - 2 * margin
        
        # Draw axes
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(margin, height - margin, width - margin, height - margin)  # X-axis
        painter.drawLine(margin, margin, margin, height - margin)  # Y-axis
        
        # Get max values
        max_yield = max(d['yield'] for d in self.curve_data) if self.curve_data else 30
        max_dim = max(d['dim'] for d in self.curve_data) if self.curve_data else 305
        
        # Draw grid lines
        painter.setPen(QPen(Qt.lightGray, 1, Qt.DotLine))
        
        # Horizontal grid lines
        for i in range(6):
            y = height - margin - (i * chart_height / 5)
            painter.drawLine(margin, y, width - margin, y)
            # Y-axis labels
            painter.setPen(Qt.black)
            label = f"{max_yield * i / 5:.1f}L"
            painter.drawText(5, y + 4, label)
            painter.setPen(QPen(Qt.lightGray, 1, Qt.DotLine))
        
        # Vertical grid lines (every 50 DIM)
        for i in range(7):
            x = margin + (i * chart_width / 6)
            painter.drawLine(x, margin, x, height - margin)
            # X-axis labels
            painter.setPen(Qt.black)
            label = f"{max_dim * i / 6:.0f}"
            painter.drawText(x - 10, height - margin + 20, label)
            painter.setPen(QPen(Qt.lightGray, 1, Qt.DotLine))
        
        # Draw lactation curve
        if self.curve_data:
            painter.setPen(QPen(QColor(33, 150, 243), 3))  # Blue
            points = []
            
            for data in self.curve_data:
                x = margin + (data['dim'] / max_dim) * chart_width
                y = height - margin - (data['yield'] / max_yield) * chart_height
                points.append((x, y))
            
            # Draw curve line
            for i in range(len(points) - 1):
                painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        
        # Draw actual data points
        if self.actual_data:
            painter.setBrush(QBrush(QColor(255, 87, 34)))  # Orange
            painter.setPen(QPen(QColor(255, 87, 34), 2))
            
            for data in self.actual_data:
                if 'dim' in data and 'yield' in data:
                    x = margin + (data['dim'] / max_dim) * chart_width
                    y = height - margin - (data['yield'] / max_yield) * chart_height
                    painter.drawEllipse(int(x) - 3, int(y) - 3, 6, 6)
        
        # Draw labels
        painter.setPen(Qt.black)
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(width // 2 - 50, 20, "Wood's Lactation Curve")
        
        font = QFont("Arial", 8)
        painter.setFont(font)
        painter.drawText(width // 2 - 30, height - 10, "Days In Milk (DIM)")
        
        painter.rotate(-90)
        painter.drawText(-height // 2 - 30, 15, "Milk Yield (L/day)")
        painter.rotate(90)
        
        painter.end()


class LactationStageIndicator(QWidget):
    """Visual indicator for lactation stage"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_stage = LactationStage.FRESH
        self.dim = 0
        self.setMinimumHeight(60)
    
    def set_stage(self, stage: LactationStage, dim: int):
        """Update the stage indicator"""
        self.current_stage = stage
        self.dim = dim
        self.update()
    
    def paintEvent(self, event):
        """Paint the stage indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        stages = [
            ("Pre-calving", LactationStage.PRE_CALVING, 0),
            ("Fresh", LactationStage.FRESH, 10),
            ("Early", LactationStage.EARLY_LACTATION, 60),
            ("Mid", LactationStage.MID_LACTATION, 150),
            ("Late", LactationStage.LATE_LACTATION, 250),
            ("Dry", LactationStage.DRY, 305)
        ]
        
        box_width = self.width() // 6
        height = self.height() - 10
        
        for i, (name, stage, _) in enumerate(stages):
            x = i * box_width
            
            # Determine color
            if stage == self.current_stage:
                color = QColor(LactationStageManager.get_stage_color(stage))
                border_width = 3
            else:
                color = QColor(200, 200, 200)
                border_width = 1
            
            # Draw box
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.black, border_width))
            painter.drawRoundedRect(x + 2, 5, box_width - 4, height, 5, 5)
            
            # Draw text
            painter.setPen(Qt.black)
            font = QFont("Arial", 8, QFont.Bold)
            painter.setFont(font)
            text_rect = painter.boundingRect(x + 5, 10, box_width - 10, 20, Qt.AlignCenter, name)
            painter.drawText(text_rect, Qt.AlignCenter, name)
        
        # Draw current position indicator
        if 0 <= self.dim <= 350:
            indicator_x = (self.dim / 350) * self.width()
            painter.setBrush(QBrush(QColor(244, 67, 54)))  # Red
            painter.setPen(QPen(Qt.black, 1))
            painter.drawTriangle(
                int(indicator_x), height + 5,
                int(indicator_x - 5), height + 15,
                int(indicator_x + 5), height + 15
            )
        
        painter.end()


class CowLactationDialog(QDialog):
    """Dialog for managing individual cow lactation data"""
    
    def __init__(self, cow_code: str, lactation_manager: LactationDataManager, parent=None):
        super().__init__(parent)
        self.cow_code = cow_code
        self.lactation_manager = lactation_manager
        self.setWindowTitle(f"Lactation Management - {cow_code}")
        self.setModal(True)
        self.resize(900, 700)
        self.init_ui()
        self.load_cow_data()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"🐄 Lactation Profile: {self.cow_code}")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # Lactation Stage Indicator
        self.stage_indicator = LactationStageIndicator()
        layout.addWidget(self.stage_indicator)
        
        # Splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Cow information
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Basic info group
        info_group = QGroupBox("Lactation Information")
        info_layout = QFormLayout()
        
        self.calving_date_edit = QDateEdit()
        self.calving_date_edit.setCalendarPopup(True)
        info_layout.addRow("Calving Date:", self.calving_date_edit)
        
        self.lactation_num_spin = QSpinBox()
        self.lactation_num_spin.setRange(1, 20)
        info_layout.addRow("Lactation Number:", self.lactation_num_spin)
        
        self.dim_label = QLabel("0 days")
        self.dim_label.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout.addRow("Days In Milk (DIM):", self.dim_label)
        
        self.stage_label = QLabel("Fresh")
        self.stage_label.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout.addRow("Current Stage:", self.stage_label)
        
        self.daily_yield_spin = QDoubleSpinBox()
        self.daily_yield_spin.setRange(0, 100)
        self.daily_yield_spin.setSuffix(" L")
        info_layout.addRow("Daily Yield:", self.daily_yield_spin)
        
        info_group.setLayout(info_layout)
        left_layout.addWidget(info_group)
        
        # Breeding info group
        breeding_group = QGroupBox("Breeding & Fertility")
        breeding_layout = QFormLayout()
        
        self.breeding_status_combo = QComboBox()
        self.breeding_status_combo.addItems([s.value for s in FertilityStatus])
        breeding_layout.addRow("Breeding Status:", self.breeding_status_combo)
        
        self.last_breeding_date = QDateEdit()
        self.last_breeding_date.setCalendarPopup(True)
        breeding_layout.addRow("Last Breeding:", self.last_breeding_date)
        
        self.expected_calving_label = QLabel("Not pregnant")
        breeding_layout.addRow("Expected Calving:", self.expected_calving_label)
        
        self.dry_off_date_edit = QDateEdit()
        self.dry_off_date_edit.setCalendarPopup(True)
        breeding_layout.addRow("Dry-off Date:", self.dry_off_date_edit)
        
        breeding_group.setLayout(breeding_layout)
        left_layout.addWidget(breeding_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        save_btn = ModernButton("💾 Save Changes")
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)
        
        record_milk_btn = ModernButton("🥛 Record Milk")
        record_milk_btn.clicked.connect(self.record_milk_dialog)
        button_layout.addWidget(record_milk_btn)
        
        record_breeding_btn = ModernButton("💕 Record Breeding")
        record_breeding_btn.clicked.connect(self.record_breeding_dialog)
        button_layout.addWidget(record_breeding_btn)
        
        dry_off_btn = ModernButton("🛑 Dry Off")
        dry_off_btn.clicked.connect(self.perform_dry_off)
        button_layout.addWidget(dry_off_btn)
        
        left_layout.addLayout(button_layout)
        left_layout.addStretch()
        
        left_panel.setLayout(left_layout)
        splitter.addWidget(left_panel)
        
        # Right panel - Lactation curve and history
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Lactation curve chart
        curve_group = QGroupBox("Wood's Lactation Curve")
        curve_layout = QVBoxLayout()
        
        self.curve_chart = LactationCurveChart()
        curve_layout.addWidget(self.curve_chart)
        
        # Wood's curve parameters
        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel("a (scaling):"))
        self.param_a_label = QLabel("30.0")
        params_layout.addWidget(self.param_a_label)
        params_layout.addWidget(QLabel("b (ascending):"))
        self.param_b_label = QLabel("0.15")
        params_layout.addWidget(self.param_b_label)
        params_layout.addWidget(QLabel("c (descending):"))
        self.param_c_label = QLabel("0.0025")
        params_layout.addWidget(self.param_c_label)
        params_layout.addWidget(QLabel("R²:"))
        self.r_squared_label = QLabel("0.00")
        params_layout.addWidget(self.r_squared_label)
        params_layout.addStretch()
        
        curve_layout.addLayout(params_layout)
        curve_group.setLayout(curve_layout)
        right_layout.addWidget(curve_group)
        
        # Yield history table
        history_group = QGroupBox("Yield History")
        history_layout = QVBoxLayout()
        
        self.yield_table = QTableWidget()
        self.yield_table.setColumnCount(5)
        self.yield_table.setHorizontalHeaderLabels(["Date", "DIM", "Yield (L)", "Cumulative", "Notes"])
        self.yield_table.setAlternatingRowColors(True)
        self.yield_table.horizontalHeader().setStretchLastSection(True)
        history_layout.addWidget(self.yield_table)
        
        history_group.setLayout(history_layout)
        right_layout.addWidget(history_group)
        
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)
        
        splitter.setSizes([350, 550])
        layout.addWidget(splitter)
        
        # Close button
        close_btn = ModernButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_cow_data(self):
        """Load cow lactation data"""
        record = self.lactation_manager.get_or_create_lactation_record(self.cow_code)
        
        # Update DIM and stage
        self.lactation_manager.update_dim_and_stage(self.cow_code)
        
        # Set basic info
        if record.calving_date:
            self.calving_date_edit.setDate(QDate(record.calving_date.year, 
                                                record.calving_date.month, 
                                                record.calving_date.day))
        
        self.lactation_num_spin.setValue(record.lactation_number)
        self.dim_label.setText(f"{record.dim} days")
        self.stage_label.setText(record.stage.value)
        self.daily_yield_spin.setValue(record.daily_yield)
        
        # Set breeding info
        self.breeding_status_combo.setCurrentText(record.breeding_status.value)
        
        if record.last_breeding_date:
            self.last_breeding_date.setDate(QDate(record.last_breeding_date.year,
                                                 record.last_breeding_date.month,
                                                 record.last_breeding_date.day))
        
        if record.expected_calving_date:
            self.expected_calving_label.setText(record.expected_calving_date.strftime("%Y-%m-%d"))
        
        if record.dry_off_date:
            self.dry_off_date_edit.setDate(QDate(record.dry_off_date.year,
                                                record.dry_off_date.month,
                                                record.dry_off_date.day))
        
        # Update stage indicator
        self.stage_indicator.set_stage(record.stage, record.dim)
        
        # Update curve chart
        self.update_curve_chart(record)
        
        # Load yield history
        self.load_yield_history(record)
    
    def update_curve_chart(self, record: LactationRecord):
        """Update the lactation curve chart"""
        if record.wood_params:
            # Use fitted parameters
            curve = WoodsLactationCurve(
                a=record.wood_params.get('a', 30.0),
                b=record.wood_params.get('b', 0.15),
                c=record.wood_params.get('c', 0.0025)
            )
            
            # Update parameter labels
            self.param_a_label.setText(f"{record.wood_params.get('a', 30.0):.2f}")
            self.param_b_label.setText(f"{record.wood_params.get('b', 0.15):.4f}")
            self.param_c_label.setText(f"{record.wood_params.get('c', 0.0025):.5f}")
            self.r_squared_label.setText(f"{record.wood_params.get('r_squared', 0.0):.3f}")
        else:
            # Use default curve
            curve = WoodsLactationCurve()
        
        # Generate curve data
        curve_data = curve.get_curve_data(305)
        
        # Get actual yield data
        actual_data = record.yield_history
        
        # Update chart
        self.curve_chart.set_data(curve_data, actual_data)
    
    def load_yield_history(self, record: LactationRecord):
        """Load yield history into table"""
        self.yield_table.setRowCount(len(record.yield_history))
        
        for row, entry in enumerate(record.yield_history):
            date_str = entry.get('date', '')[:10]
            dim = entry.get('dim', 0)
            yield_val = entry.get('yield', 0.0)
            cumulative = sum(e.get('yield', 0.0) for e in record.yield_history[:row+1])
            notes = entry.get('notes', '')
            
            self.yield_table.setItem(row, 0, QTableWidgetItem(date_str))
            self.yield_table.setItem(row, 1, QTableWidgetItem(str(dim)))
            self.yield_table.setItem(row, 2, QTableWidgetItem(f"{yield_val:.1f}"))
            self.yield_table.setItem(row, 3, QTableWidgetItem(f"{cumulative:.1f}"))
            self.yield_table.setItem(row, 4, QTableWidgetItem(notes))
    
    def save_changes(self):
        """Save changes to cow data"""
        record = self.lactation_manager.get_or_create_lactation_record(self.cow_code)
        
        # Update record
        calving_date = self.calving_date_edit.date()
        record.calving_date = datetime(calving_date.year(), calving_date.month(), calving_date.day())
        record.lactation_number = self.lactation_num_spin.value()
        record.daily_yield = self.daily_yield_spin.value()
        
        # Update breeding info
        breeding_status_text = self.breeding_status_combo.currentText()
        for status in FertilityStatus:
            if status.value == breeding_status_text:
                record.breeding_status = status
                break
        
        # Update dates
        last_breeding = self.last_breeding_date.date()
        record.last_breeding_date = datetime(last_breeding.year(), last_breeding.month(), last_breeding.day())
        
        dry_off = self.dry_off_date_edit.date()
        record.dry_off_date = datetime(dry_off.year(), dry_off.month(), dry_off.day())
        
        # Update DIM and stage
        self.lactation_manager.update_dim_and_stage(self.cow_code)
        
        # Save data
        self.lactation_manager.save_lactation_data()
        
        # Reload display
        self.load_cow_data()
        
        QMessageBox.information(self, "Success", "Changes saved successfully!")
    
    def record_milk_dialog(self):
        """Open dialog to record milk yield"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Record Milk Yield")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QFormLayout()
        
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        layout.addRow("Date:", date_edit)
        
        yield_spin = QDoubleSpinBox()
        yield_spin.setRange(0, 100)
        yield_spin.setSuffix(" L")
        yield_spin.setDecimals(1)
        layout.addRow("Yield (L):", yield_spin)
        
        notes_edit = QTextEdit()
        notes_edit.setMaximumHeight(80)
        layout.addRow("Notes:", notes_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_milk_yield(
            date_edit.date(), yield_spin.value(), notes_edit.toPlainText(), dialog
        ))
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def save_milk_yield(self, date, yield_amount, notes, dialog):
        """Save milk yield record"""
        py_date = datetime(date.year(), date.month(), date.day())
        
        self.lactation_manager.record_milk_yield(self.cow_code, py_date, yield_amount)
        
        # Add notes to last entry
        record = self.lactation_manager.get_or_create_lactation_record(self.cow_code)
        if record.yield_history:
            record.yield_history[-1]['notes'] = notes
        
        self.lactation_manager.save_lactation_data()
        
        dialog.accept()
        self.load_cow_data()
        
        QMessageBox.information(self, "Success", "Milk yield recorded!")
    
    def record_breeding_dialog(self):
        """Open dialog to record breeding event"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Record Breeding/AI")
        dialog.setModal(True)
        dialog.resize(450, 350)
        
        layout = QFormLayout()
        
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        layout.addRow("Breeding Date:", date_edit)
        
        sire_edit = QLineEdit()
        sire_edit.setPlaceholderText("Sire code or registration number")
        layout.addRow("Sire Code:", sire_edit)
        
        method_combo = QComboBox()
        method_combo.addItems(["AI (Artificial Insemination)", "Natural", "Embryo Transfer"])
        layout.addRow("Method:", method_combo)
        
        technician_edit = QLineEdit()
        layout.addRow("Technician:", technician_edit)
        
        notes_edit = QTextEdit()
        notes_edit.setMaximumHeight(80)
        layout.addRow("Notes:", notes_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_breeding(
            date_edit.date(), sire_edit.text(), method_combo.currentText(),
            technician_edit.text(), notes_edit.toPlainText(), dialog
        ))
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def save_breeding(self, date, sire_code, method, technician, notes, dialog):
        """Save breeding event"""
        breeding_event = BreedingEvent(
            cow_code=self.cow_code,
            breeding_date=datetime(date.year(), date.month(), date.day()),
            sire_code=sire_code,
            method=method.split("(")[0].strip(),
            technician=technician,
            notes=notes
        )
        
        self.lactation_manager.record_breeding(breeding_event)
        self.lactation_manager.save_lactation_data()
        
        dialog.accept()
        self.load_cow_data()
        
        QMessageBox.information(self, "Success", "Breeding event recorded!")
    
    def perform_dry_off(self):
        """Perform dry-off for the cow"""
        reply = QMessageBox.question(
            self, "Confirm Dry-off",
            f"Are you sure you want to dry off cow {self.cow_code}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.lactation_manager.perform_dry_off(
                self.cow_code,
                datetime.now(),
                method='Gradual',
                notes='Manual dry-off initiated'
            )
            self.lactation_manager.save_lactation_data()
            self.load_cow_data()
            
            QMessageBox.information(self, "Success", "Cow has been dried off!")


class LactationManagementWidget(QWidget):
    """Main widget for lactation cycle management"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.lactation_manager = LactationDataManager(data_manager)
        self.alert_manager = FertilityAlertManager(data_manager)
        self.analytics = LactationAnalytics()
        
        self.init_ui()
        self.load_data()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes
    
    def init_ui(self):
        """Initialize the main UI"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🥛 Lactation Cycle Management")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = ModernButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # KPI Cards
        kpi_layout = QHBoxLayout()
        
        self.total_cows_card = StatCard("Total Cows", "0", "👥")
        kpi_layout.addWidget(self.total_cows_card)
        
        self.avg_dim_card = StatCard("Avg DIM", "0 days", "📅")
        kpi_layout.addWidget(self.avg_dim_card)
        
        self.avg_yield_card = StatCard("Avg Yield", "0.0 L", "🥛")
        kpi_layout.addWidget(self.avg_yield_card)
        
        self.pregnant_card = StatCard("Pregnant", "0", "🤰")
        kpi_layout.addWidget(self.pregnant_card)
        
        self.breeding_window_card = StatCard("In Breeding Window", "0", "💕")
        kpi_layout.addWidget(self.breeding_window_card)
        
        layout.addLayout(kpi_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Lactation Overview
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📊 Overview")
        
        # Tab 2: Alerts & Notifications
        self.alerts_tab = self.create_alerts_tab()
        self.tab_widget.addTab(self.alerts_tab, "🔔 Alerts")
        
        # Tab 3: Lactation Curves
        self.curves_tab = self.create_curves_tab()
        self.tab_widget.addTab(self.curves_tab, "📈 Lactation Curves")
        
        # Tab 4: Fertility Management
        self.fertility_tab = self.create_fertility_tab()
        self.tab_widget.addTab(self.fertility_tab, "💕 Fertility")
        
        # Tab 5: Stage Distribution
        self.distribution_tab = self.create_distribution_tab()
        self.tab_widget.addTab(self.distribution_tab, "🎨 Stage Distribution")
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
    
    def create_overview_tab(self) -> QWidget:
        """Create the lactation overview tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Search and filter
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by cow code or name...")
        self.search_input.textChanged.connect(self.filter_cows)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("Stage:"))
        self.stage_filter = QComboBox()
        self.stage_filter.addItem("All Stages")
        for stage in LactationStage:
            self.stage_filter.addItem(stage.value)
        self.stage_filter.currentTextChanged.connect(self.filter_cows)
        filter_layout.addWidget(self.stage_filter)
        
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Status")
        for status in FertilityStatus:
            self.status_filter.addItem(status.value)
        self.status_filter.currentTextChanged.connect(self.filter_cows)
        filter_layout.addWidget(self.status_filter)
        
        layout.addLayout(filter_layout)
        
        # Cows table
        self.cows_table = QTableWidget()
        self.cows_table.setColumnCount(12)
        self.cows_table.setHorizontalHeaderLabels([
            "Cow Code", "Lactation #", "DIM", "Stage", "Daily Yield (L)", 
            "Total Yield (L)", "Breeding Status", "Last Breeding", 
            "Expected Calving", "Feed Efficiency", "Wood's Curve", "Actions"
        ])
        self.cows_table.setAlternatingRowColors(True)
        self.cows_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.cows_table.horizontalHeader().setStretchLastSection(True)
        
        # Make columns resize to content
        self.cows_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        layout.addWidget(self.cows_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        add_cow_btn = ModernButton("➕ Add Cow Record")
        add_cow_btn.clicked.connect(self.add_cow_record_dialog)
        button_layout.addWidget(add_cow_btn)
        
        record_heat_btn = ModernButton("🔥 Record Heat Detection")
        record_heat_btn.clicked.connect(self.record_heat_dialog)
        button_layout.addWidget(record_heat_btn)
        
        pregnancy_check_btn = ModernButton("🩺 Record Pregnancy Check")
        pregnancy_check_btn.clicked.connect(self.pregnancy_check_dialog)
        button_layout.addWidget(pregnancy_check_btn)
        
        export_btn = ModernButton("📤 Export Data")
        export_btn.clicked.connect(self.export_lactation_data)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_alerts_tab(self) -> QWidget:
        """Create the alerts and notifications tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Alert summary cards
        summary_layout = QHBoxLayout()
        
        self.urgent_alerts_card = StatCard("Urgent", "0", "🔴")
        self.urgent_alerts_card.setStyleSheet("background-color: #FFEBEE;")
        summary_layout.addWidget(self.urgent_alerts_card)
        
        self.high_alerts_card = StatCard("High Priority", "0", "🟠")
        self.high_alerts_card.setStyleSheet("background-color: #FFF3E0;")
        summary_layout.addWidget(self.high_alerts_card)
        
        self.medium_alerts_card = StatCard("Medium", "0", "🟡")
        self.medium_alerts_card.setStyleSheet("background-color: #FFFDE7;")
        summary_layout.addWidget(self.medium_alerts_card)
        
        layout.addLayout(summary_layout)
        
        # Alerts table
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels([
            "Priority", "Type", "Message", "Action Required", "Cow Code"
        ])
        self.alerts_table.setAlternatingRowColors(True)
        self.alerts_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.alerts_table)
        
        tab.setLayout(layout)
        return tab
    
    def create_curves_tab(self) -> QWidget:
        """Create the lactation curves visualization tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Cow selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Cow:"))
        
        self.curve_cow_selector = QComboBox()
        self.curve_cow_selector.currentTextChanged.connect(self.update_curve_display)
        selector_layout.addWidget(self.curve_cow_selector)
        
        selector_layout.addWidget(QLabel("Compare with:"))
        self.compare_cow_selector = QComboBox()
        self.compare_cow_selector.addItem("None")
        selector_layout.addWidget(self.compare_cow_selector)
        
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Curve chart
        self.main_curve_chart = LactationCurveChart()
        self.main_curve_chart.setMinimumHeight(400)
        layout.addWidget(self.main_curve_chart)
        
        # Curve statistics
        stats_layout = QHBoxLayout()
        
        self.peak_yield_label = QLabel("Peak Yield: -- L")
        stats_layout.addWidget(self.peak_yield_label)
        
        self.peak_dim_label = QLabel("Peak DIM: -- days")
        stats_layout.addWidget(self.peak_dim_label)
        
        self.total_yield_label = QLabel("305-day ME: -- L")
        stats_layout.addWidget(self.total_yield_label)
        
        self.persistence_label = QLabel("Persistence: --")
        stats_layout.addWidget(self.persistence_label)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_fertility_tab(self) -> QWidget:
        """Create the fertility management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Fertility KPIs
        kpi_layout = QHBoxLayout()
        
        self.conception_rate_card = StatCard("Conception Rate", "0%", "🎯")
        kpi_layout.addWidget(self.conception_rate_card)
        
        self.pregnancy_rate_card = StatCard("Pregnancy Rate", "0%", "🤰")
        kpi_layout.addWidget(self.pregnancy_rate_card)
        
        self.days_open_card = StatCard("Avg Days Open", "0", "📅")
        kpi_layout.addWidget(self.days_open_card)
        
        self.services_per_conception_card = StatCard("Services/Conception", "0.0", "🔄")
        kpi_layout.addWidget(self.services_per_conception_card)
        
        layout.addLayout(kpi_layout)
        
        # Breeding calendar/schedule
        calendar_group = QGroupBox("Upcoming Breeding & Check Schedule")
        calendar_layout = QVBoxLayout()
        
        self.breeding_table = QTableWidget()
        self.breeding_table.setColumnCount(6)
        self.breeding_table.setHorizontalHeaderLabels([
            "Date", "Cow Code", "Event Type", "Status", "Technician", "Notes"
        ])
        self.breeding_table.setAlternatingRowColors(True)
        calendar_layout.addWidget(self.breeding_table)
        
        calendar_group.setLayout(calendar_layout)
        layout.addWidget(calendar_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_distribution_tab(self) -> QWidget:
        """Create the stage distribution visualization tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Stage distribution table
        self.distribution_table = QTableWidget()
        self.distribution_table.setColumnCount(5)
        self.distribution_table.setHorizontalHeaderLabels([
            "Stage", "Number of Cows", "Percentage", "Avg Yield (L)", "Feed Requirement"
        ])
        self.distribution_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.distribution_table)
        
        tab.setLayout(layout)
        return tab
    
    def load_data(self):
        """Load all lactation data"""
        self.lactation_manager.load_lactation_data()
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh all displays"""
        # Update KPIs
        self.update_kpi_cards()
        
        # Update cows table
        self.populate_cows_table()
        
        # Update alerts
        self.update_alerts()
        
        # Update curve selectors
        self.update_curve_selectors()
        
        # Update fertility tab
        self.update_fertility_tab()
        
        # Update distribution
        self.update_distribution_tab()
    
    def update_kpi_cards(self):
        """Update KPI summary cards"""
        summary = self.lactation_manager.get_herd_lactation_summary()
        
        self.total_cows_card.value_label.setText(str(summary['total_cows']))
        self.avg_dim_card.value_label.setText(f"{summary['avg_dim']:.0f} days")
        self.avg_yield_card.value_label.setText(f"{summary['avg_daily_yield']:.1f} L")
        
        fertility = summary.get('fertility_summary', {})
        self.pregnant_card.value_label.setText(str(fertility.get('pregnant', 0)))
        self.breeding_window_card.value_label.setText(str(fertility.get('in_breeding_window', 0)))
    
    def populate_cows_table(self):
        """Populate the cows table with lactation data"""
        records = list(self.lactation_manager.lactation_records.values())
        
        self.cows_table.setRowCount(len(records))
        
        for row, record in enumerate(records):
            # Update DIM and stage
            self.lactation_manager.update_dim_and_stage(record.cow_code)
            
            # Cow code
            self.cows_table.setItem(row, 0, QTableWidgetItem(record.cow_code))
            
            # Lactation number
            self.cows_table.setItem(row, 1, QTableWidgetItem(str(record.lactation_number)))
            
            # DIM
            self.cows_table.setItem(row, 2, QTableWidgetItem(str(record.dim)))
            
            # Stage
            stage_item = QTableWidgetItem(record.stage.value)
            stage_color = QColor(LactationStageManager.get_stage_color(record.stage))
            stage_item.setBackground(stage_color)
            self.cows_table.setItem(row, 3, stage_item)
            
            # Daily yield
            self.cows_table.setItem(row, 4, QTableWidgetItem(f"{record.daily_yield:.1f}"))
            
            # Total yield
            self.cows_table.setItem(row, 5, QTableWidgetItem(f"{record.total_yield:.1f}"))
            
            # Breeding status
            status_item = QTableWidgetItem(record.breeding_status.value)
            self.cows_table.setItem(row, 6, status_item)
            
            # Last breeding
            last_breeding = record.last_breeding_date.strftime("%Y-%m-%d") if record.last_breeding_date else "--"
            self.cows_table.setItem(row, 7, QTableWidgetItem(last_breeding))
            
            # Expected calving
            expected = record.expected_calving_date.strftime("%Y-%m-%d") if record.expected_calving_date else "--"
            self.cows_table.setItem(row, 8, QTableWidgetItem(expected))
            
            # Feed efficiency
            self.cows_table.setItem(row, 9, QTableWidgetItem(f"{record.feed_efficiency:.2f}"))
            
            # Wood's curve fitted?
            wood_status = "✓ Fitted" if record.wood_params else "✗ Not fitted"
            self.cows_table.setItem(row, 10, QTableWidgetItem(wood_status))
            
            # Actions button
            actions_btn = QPushButton("Manage")
            actions_btn.clicked.connect(lambda checked, code=record.cow_code: self.open_cow_dialog(code))
            self.cows_table.setCellWidget(row, 11, actions_btn)
    
    def filter_cows(self):
        """Filter cows table based on search and filters"""
        search_term = self.search_input.text().lower()
        stage_filter = self.stage_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        for row in range(self.cows_table.rowCount()):
            show_row = True
            
            # Search filter
            if search_term:
                cow_code = self.cows_table.item(row, 0).text().lower()
                if search_term not in cow_code:
                    show_row = False
            
            # Stage filter
            if stage_filter != "All Stages":
                stage = self.cows_table.item(row, 3).text()
                if stage != stage_filter:
                    show_row = False
            
            # Status filter
            if status_filter != "All Status":
                status = self.cows_table.item(row, 6).text()
                if status != status_filter:
                    show_row = False
            
            self.cows_table.setRowHidden(row, not show_row)
    
    def update_alerts(self):
        """Update alerts table"""
        records = list(self.lactation_manager.lactation_records.values())
        alerts = self.alert_manager.generate_all_alerts(records, self.lactation_manager.heat_records)
        
        # Update summary cards
        urgent = len([a for a in alerts if a['priority'] == 'urgent'])
        high = len([a for a in alerts if a['priority'] == 'high'])
        medium = len([a for a in alerts if a['priority'] == 'medium'])
        
        self.urgent_alerts_card.value_label.setText(str(urgent))
        self.high_alerts_card.value_label.setText(str(high))
        self.medium_alerts_card.value_label.setText(str(medium))
        
        # Update alerts table
        self.alerts_table.setRowCount(len(alerts))
        
        for row, alert in enumerate(alerts):
            # Priority
            priority_item = QTableWidgetItem(alert['priority'].upper())
            if alert['priority'] == 'urgent':
                priority_item.setBackground(QColor(255, 200, 200))
            elif alert['priority'] == 'high':
                priority_item.setBackground(QColor(255, 230, 200))
            elif alert['priority'] == 'medium':
                priority_item.setBackground(QColor(255, 255, 200))
            
            self.alerts_table.setItem(row, 0, priority_item)
            self.alerts_table.setItem(row, 1, QTableWidgetItem(alert['type']))
            self.alerts_table.setItem(row, 2, QTableWidgetItem(alert['message']))
            self.alerts_table.setItem(row, 3, QTableWidgetItem(alert['action_required']))
            
            # Extract cow code from message
            cow_code = ""
            for word in alert['message'].split():
                if word.startswith("COW-"):
                    cow_code = word
                    break
            self.alerts_table.setItem(row, 4, QTableWidgetItem(cow_code))
    
    def update_curve_selectors(self):
        """Update cow selectors for curve display"""
        current_selection = self.curve_cow_selector.currentText()
        
        self.curve_cow_selector.clear()
        self.compare_cow_selector.clear()
        self.compare_cow_selector.addItem("None")
        
        cow_codes = sorted(self.lactation_manager.lactation_records.keys())
        
        for code in cow_codes:
            self.curve_cow_selector.addItem(code)
            self.compare_cow_selector.addItem(code)
        
        # Restore selection if possible
        if current_selection and current_selection in cow_codes:
            self.curve_cow_selector.setCurrentText(current_selection)
        elif cow_codes:
            self.curve_cow_selector.setCurrentIndex(0)
            self.update_curve_display()
    
    def update_curve_display(self):
        """Update the lactation curve display"""
        cow_code = self.curve_cow_selector.currentText()
        if not cow_code:
            return
        
        record = self.lactation_manager.get_or_create_lactation_record(cow_code)
        
        if record.wood_params:
            curve = WoodsLactationCurve(
                a=record.wood_params.get('a', 30.0),
                b=record.wood_params.get('b', 0.15),
                c=record.wood_params.get('c', 0.0025)
            )
            
            # Update statistics
            self.peak_yield_label.setText(f"Peak Yield: {curve.get_peak_yield():.1f} L")
            self.peak_dim_label.setText(f"Peak DIM: {curve.get_peak_dim()} days")
            self.total_yield_label.setText(f"305-day ME: {curve.get_total_yield(305):.1f} L")
            self.persistence_label.setText(f"Persistence: {curve.get_persistence():.3f}")
        else:
            curve = WoodsLactationCurve()
            self.peak_yield_label.setText("Peak Yield: -- L")
            self.peak_dim_label.setText("Peak DIM: -- days")
            self.total_yield_label.setText("305-day ME: -- L")
            self.persistence_label.setText("Persistence: --")
        
        # Generate curve data
        curve_data = curve.get_curve_data(305)
        actual_data = record.yield_history
        
        self.main_curve_chart.set_data(curve_data, actual_data)
    
    def update_fertility_tab(self):
        """Update fertility management tab"""
        # Calculate KPIs
        breeding_list = [b.to_dict() for b in self.lactation_manager.breeding_records]
        lactation_list = list(self.lactation_manager.lactation_records.values())
        
        kpis = self.analytics.calculate_fertility_kpis(breeding_list, lactation_list)
        
        self.conception_rate_card.value_label.setText(f"{kpis['conception_rate']:.1f}%")
        self.pregnancy_rate_card.value_label.setText(f"{kpis['pregnancy_rate']:.1f}%")
        self.days_open_card.value_label.setText(f"{kpis['days_open']}")
        self.services_per_conception_card.value_label.setText(f"{kpis['services_per_conception']:.1f}")
        
        # Update breeding table (future events)
        future_events = []
        
        for record in lactation_list:
            # Pregnancy checks
            if record.last_breeding_date and record.breeding_status == FertilityStatus.OPEN:
                days_since_ai = (datetime.now() - record.last_breeding_date).days
                
                # Check 1: 32 days
                if days_since_ai < 32:
                    check_date = record.last_breeding_date + timedelta(days=32)
                    if check_date >= datetime.now():
                        future_events.append({
                            'date': check_date,
                            'cow_code': record.cow_code,
                            'event': 'Pregnancy Check 1',
                            'status': 'Scheduled',
                            'technician': 'TBD',
                            'notes': f'{32 - days_since_ai} days from now'
                        })
                
                # Check 2: 60 days
                if days_since_ai < 60:
                    check_date = record.last_breeding_date + timedelta(days=60)
                    if check_date >= datetime.now():
                        future_events.append({
                            'date': check_date,
                            'cow_code': record.cow_code,
                            'event': 'Pregnancy Check 2',
                            'status': 'Scheduled',
                            'technician': 'TBD',
                            'notes': f'{60 - days_since_ai} days from now'
                        })
            
            # Dry-off events
            if record.expected_calving_date:
                dry_off_date = record.expected_calving_date - timedelta(days=60)
                if dry_off_date >= datetime.now():
                    future_events.append({
                        'date': dry_off_date,
                        'cow_code': record.cow_code,
                        'event': 'Dry-off',
                        'status': 'Planned',
                        'technician': 'TBD',
                        'notes': 'Prepare transition diet'
                    })
        
        # Sort by date
        future_events.sort(key=lambda x: x['date'])
        
        # Update table
        self.breeding_table.setRowCount(len(future_events))
        
        for row, event in enumerate(future_events):
            self.breeding_table.setItem(row, 0, QTableWidgetItem(event['date'].strftime("%Y-%m-%d")))
            self.breeding_table.setItem(row, 1, QTableWidgetItem(event['cow_code']))
            self.breeding_table.setItem(row, 2, QTableWidgetItem(event['event']))
            self.breeding_table.setItem(row, 3, QTableWidgetItem(event['status']))
            self.breeding_table.setItem(row, 4, QTableWidgetItem(event['technician']))
            self.breeding_table.setItem(row, 5, QTableWidgetItem(event['notes']))
    
    def update_distribution_tab(self):
        """Update stage distribution tab"""
        records = list(self.lactation_manager.lactation_records.values())
        
        distribution = self.analytics.calculate_stage_distribution(records)
        avg_yields = self.analytics.calculate_average_yield_by_stage(records)
        
        total_cows = sum(distribution.values())
        
        self.distribution_table.setRowCount(len(distribution))
        
        for row, (stage, count) in enumerate(distribution.items()):
            percentage = (count / total_cows * 100) if total_cows > 0 else 0
            avg_yield = avg_yields.get(stage, 0)
            
            # Get feed requirement example (for 500kg cow)
            for ls in LactationStage:
                if ls.value == stage:
                    feed_req = LactationStageManager.get_feed_requirements(ls, 500)
                    feed_text = f"{feed_req['dm_intake_kg']:.1f}kg DM/day"
                    break
            else:
                feed_text = "--"
            
            self.distribution_table.setItem(row, 0, QTableWidgetItem(stage))
            self.distribution_table.setItem(row, 1, QTableWidgetItem(str(count)))
            self.distribution_table.setItem(row, 2, QTableWidgetItem(f"{percentage:.1f}%"))
            self.distribution_table.setItem(row, 3, QTableWidgetItem(f"{avg_yield:.1f}"))
            self.distribution_table.setItem(row, 4, QTableWidgetItem(feed_text))
    
    def open_cow_dialog(self, cow_code: str):
        """Open cow lactation management dialog"""
        dialog = CowLactationDialog(cow_code, self.lactation_manager, self)
        dialog.exec_()
        self.refresh_data()
    
    def add_cow_record_dialog(self):
        """Add new cow lactation record"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Cow Lactation Record")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QFormLayout()
        
        cow_code_edit = QLineEdit()
        cow_code_edit.setPlaceholderText("Enter cow code (e.g., COW-2401-0001)")
        layout.addRow("Cow Code:", cow_code_edit)
        
        calving_date = QDateEdit()
        calving_date.setDate(QDate.currentDate())
        calving_date.setCalendarPopup(True)
        layout.addRow("Calving Date:", calving_date)
        
        lactation_num = QSpinBox()
        lactation_num.setRange(1, 20)
        lactation_num.setValue(1)
        layout.addRow("Lactation Number:", lactation_num)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_new_cow_record(
            cow_code_edit.text(), calving_date.date(), lactation_num.value(), dialog
        ))
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def save_new_cow_record(self, cow_code, calving_date, lactation_num, dialog):
        """Save new cow lactation record"""
        if not cow_code:
            QMessageBox.warning(self, "Error", "Please enter a cow code!")
            return
        
        record = self.lactation_manager.get_or_create_lactation_record(cow_code)
        record.calving_date = datetime(calving_date.year(), calving_date.month(), calving_date.day())
        record.lactation_number = lactation_num
        
        # Update DIM
        self.lactation_manager.update_dim_and_stage(cow_code)
        
        self.lactation_manager.save_lactation_data()
        
        dialog.accept()
        self.refresh_data()
        
        QMessageBox.information(self, "Success", f"Lactation record added for {cow_code}!")
    
    def record_heat_dialog(self):
        """Record heat detection event"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Record Heat Detection")
        dialog.setModal(True)
        dialog.resize(450, 350)
        
        layout = QFormLayout()
        
        cow_combo = QComboBox()
        for code in sorted(self.lactation_manager.lactation_records.keys()):
            cow_combo.addItem(code)
        layout.addRow("Cow Code:", cow_combo)
        
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        layout.addRow("Detection Date:", date_edit)
        
        method_combo = QComboBox()
        method_combo.addItems(["Visual Observation", "Activity Monitor", "Teaser Bull", "Heat Mount Detector"])
        layout.addRow("Detection Method:", method_combo)
        
        intensity_combo = QComboBox()
        intensity_combo.addItems(["Strong", "Moderate", "Weak"])
        layout.addRow("Heat Intensity:", intensity_combo)
        
        duration_spin = QSpinBox()
        duration_spin.setRange(0, 48)
        duration_spin.setSuffix(" hours")
        layout.addRow("Duration:", duration_spin)
        
        notes_edit = QTextEdit()
        notes_edit.setMaximumHeight(80)
        layout.addRow("Notes:", notes_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_heat_event(
            cow_combo.currentText(), date_edit.date(), method_combo.currentText(),
            intensity_combo.currentText(), duration_spin.value(), notes_edit.toPlainText(), dialog
        ))
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def save_heat_event(self, cow_code, date, method, intensity, duration, notes, dialog):
        """Save heat detection event"""
        heat_event = HeatEvent(
            cow_code=cow_code,
            detection_date=datetime(date.year(), date.month(), date.day()),
            detection_method=method,
            intensity=intensity,
            duration_hours=duration,
            notes=notes
        )
        
        self.lactation_manager.record_heat_event(heat_event)
        self.lactation_manager.save_lactation_data()
        
        dialog.accept()
        self.refresh_data()
        
        QMessageBox.information(self, "Success", "Heat detection recorded!")
    
    def pregnancy_check_dialog(self):
        """Record pregnancy check"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Record Pregnancy Check")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QFormLayout()
        
        cow_combo = QComboBox()
        for code, record in self.lactation_manager.lactation_records.items():
            if record.last_breeding_date:
                cow_combo.addItem(code)
        layout.addRow("Cow Code:", cow_combo)
        
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        layout.addRow("Check Date:", date_edit)
        
        result_combo = QComboBox()
        result_combo.addItems(["Pregnant", "Open", "Doubtful", "Early Pregnancy"])
        layout.addRow("Result:", result_combo)
        
        method_combo = QComboBox()
        method_combo.addItems(["Ultrasound", "Rectal Palpation", "Blood Test (PAG)", "Milk Test"])
        layout.addRow("Method:", method_combo)
        
        vet_edit = QLineEdit()
        layout.addRow("Veterinarian:", vet_edit)
        
        notes_edit = QTextEdit()
        notes_edit.setMaximumHeight(80)
        layout.addRow("Notes:", notes_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_pregnancy_check(
            cow_combo.currentText(), date_edit.date(), result_combo.currentText(),
            method_combo.currentText(), vet_edit.text(), notes_edit.toPlainText(), dialog
        ))
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def save_pregnancy_check(self, cow_code, date, result, method, vet_name, notes, dialog):
        """Save pregnancy check result"""
        self.lactation_manager.record_pregnancy_check(
            cow_code,
            datetime(date.year(), date.month(), date.day()),
            result,
            method,
            vet_name
        )
        
        self.lactation_manager.save_lactation_data()
        
        dialog.accept()
        self.refresh_data()
        
        QMessageBox.information(self, "Success", f"Pregnancy check recorded: {result}!")
    
    def export_lactation_data(self):
        """Export lactation data to CSV"""
        from PyQt5.QtWidgets import QFileDialog
        import csv
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Lactation Data", "lactation_data.csv", "CSV Files (*.csv)"
        )
        
        if not file_name:
            return
        
        try:
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'cow_code', 'lactation_number', 'calving_date', 'dim', 'stage',
                    'daily_yield', 'total_yield', 'breeding_status', 'last_breeding_date',
                    'expected_calving_date', 'dry_off_date', 'feed_efficiency'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in self.lactation_manager.lactation_records.values():
                    writer.writerow({
                        'cow_code': record.cow_code,
                        'lactation_number': record.lactation_number,
                        'calving_date': record.calving_date.strftime("%Y-%m-%d") if record.calving_date else "",
                        'dim': record.dim,
                        'stage': record.stage.value,
                        'daily_yield': record.daily_yield,
                        'total_yield': record.total_yield,
                        'breeding_status': record.breeding_status.value,
                        'last_breeding_date': record.last_breeding_date.strftime("%Y-%m-%d") if record.last_breeding_date else "",
                        'expected_calving_date': record.expected_calving_date.strftime("%Y-%m-%d") if record.expected_calving_date else "",
                        'dry_off_date': record.dry_off_date.strftime("%Y-%m-%d") if record.dry_off_date else "",
                        'feed_efficiency': record.feed_efficiency
                    })
            
            QMessageBox.information(self, "Success", f"Data exported to {file_name}!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    # Test the module
    app = QApplication(sys.argv)
    
    print("Lactation Management UI Module loaded successfully!")
    print("\nFeatures:")
    print("- Lactation Stage Tracker with visual indicators")
    print("- Wood's Lactation Curve visualization")
    print("- Breeding alerts and fertility management")
    print("- Heat detection recording")
    print("- Pregnancy check scheduling")
    print("- Comprehensive dashboard and reporting")
    
    sys.exit(0)
