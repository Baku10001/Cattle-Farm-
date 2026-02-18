from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
                             QFormLayout, QLineEdit, QDateEdit, QDoubleSpinBox,
                             QComboBox, QTextEdit, QMessageBox, QLabel, QGroupBox,
                             QTabWidget, QFileDialog, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor
from datetime import datetime, timedelta
from pdf_generator import PDFGenerator
from modern_widgets import (ModernCard, StatCard, ModernButton, ModernInput, 
                           ModernComboBox, ModernChart, NotificationWidget)

class MilkProductionDialog(QDialog):
    """Dialog for recording daily milk production."""
    
    def __init__(self, parent=None, production_data=None):
        super().__init__(parent)
        self.production_data = production_data
        self.setWindowTitle("Record Milk Production" if production_data is None else "Edit Milk Production")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
        
        if production_data:
            self.populate_fields()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        
        self.morning_quantity = QDoubleSpinBox()
        self.morning_quantity.setRange(0, 1000000000)
        self.morning_quantity.setSuffix(" L")
        self.morning_quantity.setDecimals(2)
        
        self.evening_quantity = QDoubleSpinBox()
        self.evening_quantity.setRange(0, 1000000000)
        self.evening_quantity.setSuffix(" L")
        self.evening_quantity.setDecimals(2)
        
        self.total_quantity = QDoubleSpinBox()
        self.total_quantity.setRange(0, 1000000000)
        self.total_quantity.setSuffix(" L")
        self.total_quantity.setDecimals(2)
        self.total_quantity.setReadOnly(True)
        
        self.quality_grade = QComboBox()
        self.quality_grade.addItems(["A", "B", "C"])
        
        self.fat_content = QDoubleSpinBox()
        self.fat_content.setRange(0, 10)
        self.fat_content.setSuffix(" %")
        self.fat_content.setDecimals(2)
        self.fat_content.setValue(3.5)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        
        # Connect quantity changes to update total
        self.morning_quantity.valueChanged.connect(self.update_total)
        self.evening_quantity.valueChanged.connect(self.update_total)
        
        layout.addRow("Date:", self.date_edit)
        layout.addRow("Morning Quantity:", self.morning_quantity)
        layout.addRow("Evening Quantity:", self.evening_quantity)
        layout.addRow("Total Quantity:", self.total_quantity)
        layout.addRow("Quality Grade:", self.quality_grade)
        layout.addRow("Fat Content:", self.fat_content)
        layout.addRow("Notes:", self.notes)
        
        # Quality bonus section
        bonus_group = QGroupBox("Quality Bonus Calculation")
        bonus_layout = QFormLayout()
        
        self.base_rate = QDoubleSpinBox()
        self.base_rate.setRange(0, 1000000000)
        self.base_rate.setPrefix("Rs ")
        self.base_rate.setDecimals(2)
        self.base_rate.setValue(0.50)  # Default base rate per liter
        
        self.bonus_rate = QDoubleSpinBox()
        self.bonus_rate.setRange(0, 1000000000)
        self.bonus_rate.setPrefix("Rs ")
        self.bonus_rate.setDecimals(3)
        self.bonus_rate.setReadOnly(True)
        
        self.final_rate = QDoubleSpinBox()
        self.final_rate.setRange(0, 1000000000)
        self.final_rate.setPrefix("Rs ")
        self.final_rate.setDecimals(3)
        self.final_rate.setReadOnly(True)
        
        self.estimated_value = QDoubleSpinBox()
        self.estimated_value.setRange(0, 1000000000)
        self.estimated_value.setPrefix("Rs ")
        self.estimated_value.setDecimals(2)
        self.estimated_value.setReadOnly(True)
        
        # Connect quality grade and quantity changes to update bonus
        self.quality_grade.currentTextChanged.connect(self.calculate_bonus)
        self.total_quantity.valueChanged.connect(self.calculate_bonus)
        self.base_rate.valueChanged.connect(self.calculate_bonus)
        
        bonus_layout.addRow("Base Rate (per L):", self.base_rate)
        bonus_layout.addRow("Quality Bonus:", self.bonus_rate)
        bonus_layout.addRow("Final Rate (per L):", self.final_rate)
        bonus_layout.addRow("Estimated Value:", self.estimated_value)
        
        bonus_group.setLayout(bonus_layout)
        layout.addRow(bonus_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("💾 Save Production", "#27ae60")
        save_btn.clicked.connect(self.accept)
        cancel_btn = ModernButton("❌ Cancel", "#95a5a6")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def update_total(self):
        """Update total quantity when morning or evening quantities change."""
        total = self.morning_quantity.value() + self.evening_quantity.value()
        self.total_quantity.setValue(total)
        self.calculate_bonus()
    
    def calculate_bonus(self):
        """Calculate quality bonus based on grade and update rates."""
        grade = self.quality_grade.currentText()
        base_rate = self.base_rate.value()
        quantity = self.total_quantity.value()
        
        # Quality bonus rates
        bonus_rates = {
            'A': 13.30,  # Rs 13.30 bonus per liter for Grade A
            'B': 6.65,   # Rs 6.65 bonus per liter for Grade B
            'C': 0.00    # No bonus for Grade C
        }
        
        bonus = bonus_rates.get(grade, 0.00)
        final_rate = base_rate + bonus
        estimated_value = quantity * final_rate
        
        self.bonus_rate.setValue(bonus)
        self.final_rate.setValue(final_rate)
        self.estimated_value.setValue(estimated_value)
    
    def populate_fields(self):
        """Populate fields with existing production data."""
        if not self.production_data:
            return
        
        if self.production_data.get('date'):
            date = QDate.fromString(self.production_data['date'], Qt.ISODate)
            if date.isValid():
                self.date_edit.setDate(date)
        
        self.morning_quantity.setValue(self.production_data.get('morning_quantity', 0))
        self.evening_quantity.setValue(self.production_data.get('evening_quantity', 0))
        self.fat_content.setValue(self.production_data.get('fat_content', 3.5))
        self.notes.setPlainText(self.production_data.get('notes', ''))
        
        quality = self.production_data.get('quality_grade', 'A')
        index = self.quality_grade.findText(quality)
        if index >= 0:
            self.quality_grade.setCurrentIndex(index)
    
    def get_production_data(self):
        """Get production data from form fields."""
        return {
            'date': self.date_edit.date().toString(Qt.ISODate),
            'morning_quantity': self.morning_quantity.value(),
            'evening_quantity': self.evening_quantity.value(),
            'quantity': self.total_quantity.value(),
            'quality_grade': self.quality_grade.currentText(),
            'fat_content': self.fat_content.value(),
            'base_rate': self.base_rate.value(),
            'bonus_rate': self.bonus_rate.value(),
            'final_rate': self.final_rate.value(),
            'estimated_value': self.estimated_value.value(),
            'notes': self.notes.toPlainText()
        }

class DeliveryDialog(QDialog):
    """Dialog for recording milk deliveries."""
    
    def __init__(self, parent=None, delivery_data=None):
        super().__init__(parent)
        self.delivery_data = delivery_data
        self.setWindowTitle("Record Delivery" if delivery_data is None else "Edit Delivery")
        self.setModal(True)
        self.resize(450, 400)
        self.init_ui()
        
        if delivery_data:
            self.populate_fields()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        
        self.buyer_name = QLineEdit()
        self.buyer_name.setPlaceholderText("Buyer/Company name")
        
        self.buyer_contact = QLineEdit()
        self.buyer_contact.setPlaceholderText("Phone number or email")
        
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0, 1000000000)
        self.quantity.setSuffix(" L")
        self.quantity.setDecimals(2)
        
        self.rate_per_liter = QDoubleSpinBox()
        self.rate_per_liter.setRange(0, 1000000000)
        self.rate_per_liter.setPrefix("Rs ")
        self.rate_per_liter.setDecimals(2)
        
        self.total_amount = QDoubleSpinBox()
        self.total_amount.setRange(0, 1000000000)
        self.total_amount.setPrefix("Rs ")
        self.total_amount.setDecimals(2)
        self.total_amount.setReadOnly(True)
        
        self.payment_status = QComboBox()
        self.payment_status.addItems(["Pending", "Paid", "Partial"])
        
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "Bank Transfer", "Check", "Credit"])
        
        self.delivery_notes = QTextEdit()
        self.delivery_notes.setMaximumHeight(80)
        
        # Connect quantity and rate changes to update total
        self.quantity.valueChanged.connect(self.update_total)
        self.rate_per_liter.valueChanged.connect(self.update_total)
        
        layout.addRow("Date:", self.date_edit)
        layout.addRow("Buyer Name:", self.buyer_name)
        layout.addRow("Buyer Contact:", self.buyer_contact)
        layout.addRow("Quantity:", self.quantity)
        layout.addRow("Rate per Liter:", self.rate_per_liter)
        layout.addRow("Total Amount:", self.total_amount)
        layout.addRow("Payment Status:", self.payment_status)
        layout.addRow("Payment Method:", self.payment_method)
        layout.addRow("Notes:", self.delivery_notes)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def update_total(self):
        """Update total amount when quantity or rate changes."""
        total = self.quantity.value() * self.rate_per_liter.value()
        self.total_amount.setValue(total)
    
    def populate_fields(self):
        """Populate fields with existing delivery data."""
        if not self.delivery_data:
            return
        
        if self.delivery_data.get('date'):
            date = QDate.fromString(self.delivery_data['date'], Qt.ISODate)
            if date.isValid():
                self.date_edit.setDate(date)
        
        self.buyer_name.setText(self.delivery_data.get('buyer', ''))
        self.buyer_contact.setText(self.delivery_data.get('buyer_contact', ''))
        self.quantity.setValue(self.delivery_data.get('quantity', 0))
        self.rate_per_liter.setValue(self.delivery_data.get('rate', 0))
        self.delivery_notes.setPlainText(self.delivery_data.get('notes', ''))
        
        # Payment status
        status = self.delivery_data.get('payment_status', 'Pending')
        index = self.payment_status.findText(status)
        if index >= 0:
            self.payment_status.setCurrentIndex(index)
        
        # Payment method
        method = self.delivery_data.get('payment_method', 'Cash')
        index = self.payment_method.findText(method)
        if index >= 0:
            self.payment_method.setCurrentIndex(index)
    
    def get_delivery_data(self):
        """Get delivery data from form fields."""
        return {
            'date': self.date_edit.date().toString(Qt.ISODate),
            'buyer': self.buyer_name.text(),
            'buyer_contact': self.buyer_contact.text(),
            'quantity': self.quantity.value(),
            'rate': self.rate_per_liter.value(),
            'total_amount': self.total_amount.value(),
            'payment_status': self.payment_status.currentText(),
            'payment_method': self.payment_method.currentText(),
            'notes': self.delivery_notes.toPlainText()
        }

class MilkManagementWidget(QWidget):
    """Widget for managing milk production and delivery records with quality bonuses."""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.pdf_generator = PDFGenerator()
        self.init_ui()
        self.refresh_tables()
        self.update_milk_stats()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Modern header with milk stats
        header_layout = QHBoxLayout()
        title = QLabel("🥛 Milk Production & Quality Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Milk stats cards
        stats_layout = QGridLayout()
        self.milk_stats = {}
        
        stats = [
            ('daily_production', 'Today\'s Production', '0 L', '#2ecc71'),
            ('monthly_income', 'Monthly Revenue', 'Rs 0', '#27ae60'),
            ('avg_quality', 'Average Quality', 'A', '#3498db'),
            ('pending_deliveries', 'Pending Deliveries', '0', '#f39c12')
        ]
        
        for i, (key, label, value, color) in enumerate(stats):
            card = StatCard(label, value, '', None, color)
            self.milk_stats[key] = card
            row, col = divmod(i, 4)
            stats_layout.addWidget(card, row, col)
        
        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        layout.addWidget(stats_widget)
        
        # Tab widget for production and deliveries
        self.tab_widget = QTabWidget()
        
        # Production Tab
        production_tab = self.create_production_tab()
        self.tab_widget.addTab(production_tab, "Milk Production")
        
        # Deliveries Tab
        deliveries_tab = self.create_deliveries_tab()
        self.tab_widget.addTab(deliveries_tab, "Deliveries")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def create_production_tab(self):
        """Create the milk production tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_production_btn = ModernButton("📝 Record Production", "#27ae60")
        add_production_btn.clicked.connect(self.add_production)
        
        edit_production_btn = ModernButton("✏️ Edit Production", "#f39c12")
        edit_production_btn.clicked.connect(self.edit_production)
        
        delete_production_btn = ModernButton("🗑️ Delete Production", "#e74c3c")
        delete_production_btn.clicked.connect(self.delete_production)
        
        export_production_btn = ModernButton("📊 Export Report", "#9b59b6")
        export_production_btn.clicked.connect(self.export_production_report)
        
        button_layout.addWidget(add_production_btn)
        button_layout.addWidget(edit_production_btn)
        button_layout.addWidget(delete_production_btn)
        button_layout.addWidget(export_production_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Production table
        self.production_table = QTableWidget()
        self.production_table.setColumnCount(7)
        self.production_table.setHorizontalHeaderLabels([
            "ID", "Date", "Morning (L)", "Evening (L)", "Total (L)", "Quality", "Fat %"
        ])
        
        header = self.production_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.production_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.production_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.production_table)
        tab.setLayout(layout)
        return tab
    
    def create_deliveries_tab(self):
        """Create the deliveries tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_delivery_btn = QPushButton("Record Delivery")
        add_delivery_btn.clicked.connect(self.add_delivery)
        
        edit_delivery_btn = QPushButton("Edit Delivery")
        edit_delivery_btn.clicked.connect(self.edit_delivery)
        
        delete_delivery_btn = QPushButton("Delete Delivery")
        delete_delivery_btn.clicked.connect(self.delete_delivery)
        
        export_delivery_btn = QPushButton("Export Delivery Report")
        export_delivery_btn.clicked.connect(self.export_delivery_report)
        
        button_layout.addWidget(add_delivery_btn)
        button_layout.addWidget(edit_delivery_btn)
        button_layout.addWidget(delete_delivery_btn)
        button_layout.addWidget(export_delivery_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Deliveries table with enhanced columns
        self.deliveries_table = QTableWidget()
        self.deliveries_table.setColumnCount(9)
        self.deliveries_table.setHorizontalHeaderLabels([
            "ID", "Date", "Buyer", "Quantity (L)", "Base Rate", "Quality Bonus", "Final Rate", "Total Amount", "Payment Status"
        ])
        
        header = self.deliveries_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.deliveries_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.deliveries_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.deliveries_table)
        tab.setLayout(layout)
        return tab
    
    def update_milk_stats(self):
        """Update milk production statistics cards."""
        try:
            milk_data = self.data_manager.load_data('milk')
            production_records = milk_data.get('production', [])
            delivery_records = milk_data.get('deliveries', [])
            
            # Calculate today's production
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            today_production = sum(r.get('quantity', 0) for r in production_records if r.get('date') == today)
            
            # Calculate monthly income
            current_month = datetime.now().strftime('%Y-%m')
            monthly_income = sum(r.get('total_amount', 0) for r in delivery_records 
                               if r.get('date', '').startswith(current_month))
            
            # Calculate average quality
            if production_records:
                quality_scores = {'A': 3, 'B': 2, 'C': 1}
                avg_score = sum(quality_scores.get(r.get('quality_grade', 'C'), 1) for r in production_records) / len(production_records)
                avg_quality = 'A' if avg_score >= 2.5 else 'B' if avg_score >= 1.5 else 'C'
            else:
                avg_quality = 'A'
            
            # Count pending deliveries
            pending_deliveries = len([r for r in delivery_records if r.get('payment_status') == 'pending'])
            
            # Update cards
            self.milk_stats['daily_production'].value_label.setText(f"{today_production:.1f} L")
            self.milk_stats['monthly_income'].value_label.setText(f"Rs {monthly_income:.0f}")
            self.milk_stats['avg_quality'].value_label.setText(avg_quality)
            self.milk_stats['pending_deliveries'].value_label.setText(str(pending_deliveries))
            
        except Exception as e:
            pass  # Silently handle stats update errors
    
    def refresh_tables(self):
        """Refresh both production and delivery tables."""
        self.refresh_production_table()
        self.refresh_delivery_table()
    
    def refresh_production_table(self):
        """Refresh the production table with current data."""
        milk_data = self.data_manager.load_data('milk')
        production_records = milk_data.get('production', [])
        
        self.production_table.setRowCount(len(production_records))
        
        for row, record in enumerate(production_records):
            self.production_table.setItem(row, 0, QTableWidgetItem(str(record.get('id', ''))))
            self.production_table.setItem(row, 1, QTableWidgetItem(record.get('date', '')))
            self.production_table.setItem(row, 2, QTableWidgetItem(f"{record.get('morning_quantity', 0):.2f}"))
            self.production_table.setItem(row, 3, QTableWidgetItem(f"{record.get('evening_quantity', 0):.2f}"))
            self.production_table.setItem(row, 4, QTableWidgetItem(f"{record.get('quantity', 0):.2f}"))
            self.production_table.setItem(row, 5, QTableWidgetItem(record.get('quality_grade', '')))
            self.production_table.setItem(row, 6, QTableWidgetItem(f"{record.get('fat_content', 0):.2f}"))
    
    def refresh_delivery_table(self):
        """Refresh the delivery table with enhanced quality bonus columns."""
        milk_data = self.data_manager.load_data('milk')
        delivery_records = milk_data.get('deliveries', [])
        
        self.deliveries_table.setRowCount(len(delivery_records))
        
        for row, record in enumerate(delivery_records):
            self.deliveries_table.setItem(row, 0, QTableWidgetItem(str(record.get('id', ''))))
            self.deliveries_table.setItem(row, 1, QTableWidgetItem(record.get('date', '')))
            self.deliveries_table.setItem(row, 2, QTableWidgetItem(record.get('buyer', '')))
            self.deliveries_table.setItem(row, 3, QTableWidgetItem(f"{record.get('quantity', 0):.2f}"))
            self.deliveries_table.setItem(row, 4, QTableWidgetItem(f"Rs {record.get('base_rate', 0):.2f}"))
            self.deliveries_table.setItem(row, 5, QTableWidgetItem(f"Rs {record.get('quality_bonus', 0):.2f}"))
            self.deliveries_table.setItem(row, 6, QTableWidgetItem(f"Rs {record.get('final_rate', 0):.2f}"))
            self.deliveries_table.setItem(row, 7, QTableWidgetItem(f"Rs {record.get('total_amount', 0):.0f}"))
            
            # Color-code payment status
            status_item = QTableWidgetItem(record.get('payment_status', ''))
            if record.get('payment_status') == 'paid':
                status_item.setBackground(QColor('#27ae60'))
                status_item.setForeground(QColor('white'))
            elif record.get('payment_status') == 'pending':
                status_item.setBackground(QColor('#f39c12'))
                status_item.setForeground(QColor('white'))
            else:
                status_item.setBackground(QColor('#e74c3c'))
                status_item.setForeground(QColor('white'))
            
            self.deliveries_table.setItem(row, 8, status_item)
    
    def get_selected_production_id(self):
        """Get the ID of the currently selected production record."""
        current_row = self.production_table.currentRow()
        if current_row >= 0:
            return self.production_table.item(current_row, 0).text()
        return None
    
    def get_selected_delivery_id(self):
        """Get the ID of the currently selected delivery record."""
        current_row = self.deliveries_table.currentRow()
        if current_row >= 0:
            return self.deliveries_table.item(current_row, 0).text()
        return None
    
    def add_production(self):
        """Add a new production record."""
        dialog = MilkProductionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            production_data = dialog.get_production_data()
            
            # Add to milk data
            milk_data = self.data_manager.load_data('milk')
            production_records = milk_data.get('production', [])
            
            # Generate ID
            production_data['id'] = self.generate_id(production_records)
            production_data['created_at'] = datetime.now().isoformat()
            
            production_records.append(production_data)
            milk_data['production'] = production_records
            
            if self.data_manager.save_data('milk', milk_data):
                self.refresh_production_table()
                QMessageBox.information(self, "Success", "Production record added successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to add production record!")
    
    def edit_production(self):
        """Edit the selected production record."""
        record_id = self.get_selected_production_id()
        if not record_id:
            QMessageBox.warning(self, "Warning", "Please select a production record to edit!")
            return
        
        milk_data = self.data_manager.load_data('milk')
        production_records = milk_data.get('production', [])
        
        # Find the record
        record_data = None
        for record in production_records:
            if str(record.get('id')) == record_id:
                record_data = record
                break
        
        if record_data:
            dialog = MilkProductionDialog(self, record_data)
            if dialog.exec_() == QDialog.Accepted:
                updated_data = dialog.get_production_data()
                updated_data['id'] = record_data['id']
                updated_data['updated_at'] = datetime.now().isoformat()
                
                # Update the record
                for i, record in enumerate(production_records):
                    if str(record.get('id')) == record_id:
                        production_records[i] = updated_data
                        break
                
                milk_data['production'] = production_records
                if self.data_manager.save_data('milk', milk_data):
                    self.refresh_production_table()
                    QMessageBox.information(self, "Success", "Production record updated successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update production record!")
    
    def delete_production(self):
        """Delete the selected production record."""
        record_id = self.get_selected_production_id()
        if not record_id:
            QMessageBox.warning(self, "Warning", "Please select a production record to delete!")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete production record ID {record_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            milk_data = self.data_manager.load_data('milk')
            production_records = milk_data.get('production', [])
            
            # Remove the record
            production_records = [r for r in production_records if str(r.get('id')) != record_id]
            milk_data['production'] = production_records
            
            if self.data_manager.save_data('milk', milk_data):
                self.refresh_production_table()
                QMessageBox.information(self, "Success", "Production record deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete production record!")
    
    def add_delivery(self):
        """Add a new delivery record with automatic invoice generation."""
        dialog = DeliveryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            delivery_data = dialog.get_delivery_data()
            
            # Add to milk data
            milk_data = self.data_manager.load_data('milk')
            delivery_records = milk_data.get('deliveries', [])
            
            # Generate ID and invoice number
            delivery_data['id'] = len(delivery_records) + 1
            delivery_data['invoice_number'] = f"INV-{delivery_data['id']:04d}"
            delivery_records.append(delivery_data)
            
            milk_data['deliveries'] = delivery_records
            self.data_manager.save_data('milk', milk_data)
            
            # Auto-generate PDF invoice
            self.generate_delivery_invoice(delivery_data)
            
            self.refresh_delivery_table()
            self.update_milk_stats()
            QMessageBox.information(self, "Success", "Delivery record added and invoice generated successfully!")
    
    def generate_delivery_invoice(self, delivery_data):
        """Generate PDF invoice for delivery with quality bonuses."""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            # Prepare invoice data
            invoice_data = {
                'invoice_number': delivery_data.get('invoice_number', 'INV-001'),
                'date': delivery_data.get('date', ''),
                'delivery_date': delivery_data.get('date', ''),
                'customer_name': delivery_data.get('buyer', ''),
                'customer_address': delivery_data.get('buyer_contact', ''),
                'payment_terms': 'Net 30 days',
                'items': [{
                    'description': 'Premium Fresh Milk',
                    'quantity': delivery_data.get('quantity', 0),
                    'quality_grade': delivery_data.get('quality_grade', 'A'),
                    'base_rate': delivery_data.get('base_rate', 0.50),
                    'quality_bonus': delivery_data.get('quality_bonus', 0.10)
                }]
            }
            
            # Generate filename
            filename = f"Invoice_{delivery_data.get('invoice_number', 'INV-001')}_{delivery_data.get('date', '')}.pdf"
            filepath = os.path.join(os.getcwd(), 'reports', filename)
            
            # Create reports directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Generate PDF
            if self.pdf_generator.create_milk_invoice_with_quality_bonus(invoice_data, filepath):
                QMessageBox.information(self, "Invoice Generated", f"Invoice saved as: {filename}")
            else:
                QMessageBox.warning(self, "Error", "Failed to generate invoice PDF")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", "Failed to generate invoice. Please check your data and try again.")
    
    def edit_delivery(self):
        """Edit the selected delivery record."""
        record_id = self.get_selected_delivery_id()
        if not record_id:
            QMessageBox.warning(self, "Warning", "Please select a delivery record to edit!")
            return
        
        milk_data = self.data_manager.load_data('milk')
        delivery_records = milk_data.get('deliveries', [])
        
        # Find the record
        record_data = None
        for record in delivery_records:
            if str(record.get('id')) == record_id:
                record_data = record
                break
        
        if record_data:
            dialog = DeliveryDialog(self, record_data)
            if dialog.exec_() == QDialog.Accepted:
                updated_data = dialog.get_delivery_data()
                updated_data['id'] = record_data['id']
                updated_data['updated_at'] = datetime.now().isoformat()
                
                # Update the record
                for i, record in enumerate(delivery_records):
                    if str(record.get('id')) == record_id:
                        delivery_records[i] = updated_data
                        break
                
                milk_data['deliveries'] = delivery_records
                if self.data_manager.save_data('milk', milk_data):
                    self.refresh_delivery_table()
                    QMessageBox.information(self, "Success", "Delivery record updated successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update delivery record!")
    
    def delete_delivery(self):
        """Delete the selected delivery record."""
        record_id = self.get_selected_delivery_id()
        if not record_id:
            QMessageBox.warning(self, "Warning", "Please select a delivery record to delete!")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete delivery record ID {record_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            milk_data = self.data_manager.load_data('milk')
            delivery_records = milk_data.get('deliveries', [])
            
            # Remove the record
            delivery_records = [r for r in delivery_records if str(r.get('id')) != record_id]
            milk_data['deliveries'] = delivery_records
            
            if self.data_manager.save_data('milk', milk_data):
                self.refresh_delivery_table()
                QMessageBox.information(self, "Success", "Delivery record deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete delivery record!")
    
    def generate_id(self, records):
        """Generate a unique ID for new records."""
        if not records:
            return "1"
        existing_ids = [int(record.get('id', 0)) for record in records if str(record.get('id', '')).isdigit()]
        return str(max(existing_ids, default=0) + 1)
    
    def export_production_report(self):
        """Export production report to PDF."""
        milk_data = self.data_manager.load_data('milk')
        production_records = milk_data.get('production', [])
        
        if not production_records:
            QMessageBox.warning(self, "Warning", "No production records found!")
            return
        
        # Get date range (last 30 days by default)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Filter records by date range
        filtered_records = [r for r in production_records if start_date <= r.get('date', '') <= end_date]
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Production Report", 
            f"milk_production_report_{start_date}_to_{end_date}.pdf", 
            "PDF files (*.pdf)"
        )
        
        if filename:
            if self.pdf_generator.create_milk_report(filtered_records, [], start_date, end_date, filename):
                QMessageBox.information(self, "Success", f"Production report exported to {filename}")
            else:
                QMessageBox.warning(self, "Error", "Failed to export production report!")
    
    def export_delivery_report(self):
        """Export delivery report to PDF."""
        milk_data = self.data_manager.load_data('milk')
        delivery_records = milk_data.get('deliveries', [])
        
        if not delivery_records:
            QMessageBox.warning(self, "Warning", "No delivery records found!")
            return
        
        # Get date range (last 30 days by default)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Filter records by date range
        filtered_records = [r for r in delivery_records if start_date <= r.get('date', '') <= end_date]
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Delivery Report", 
            f"milk_delivery_report_{start_date}_to_{end_date}.pdf", 
            "PDF files (*.pdf)"
        )
        
        if filename:
            if self.pdf_generator.create_milk_report([], filtered_records, start_date, end_date, filename):
                QMessageBox.information(self, "Success", f"Delivery report exported to {filename}")
            else:
                QMessageBox.warning(self, "Error", "Failed to export delivery report!")
