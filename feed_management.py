from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
                             QFormLayout, QLineEdit, QDateEdit, QDoubleSpinBox,
                             QComboBox, QTextEdit, QMessageBox, QLabel, QGroupBox,
                             QTabWidget, QFileDialog, QSpinBox)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta
from modern_widgets import (ModernCard, StatCard, ModernButton, ModernInput, 
                           ModernComboBox, ModernChart, NotificationWidget)

class FeedItemDialog(QDialog):
    """Dialog for adding/editing feed inventory items."""
    
    def __init__(self, parent=None, feed_data=None):
        super().__init__(parent)
        self.feed_data = feed_data
        self.setWindowTitle("Add Feed Item" if feed_data is None else "Edit Feed Item")
        self.setModal(True)
        self.resize(500, 600)
        self.init_ui()
        
        if feed_data:
            self.populate_fields()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Basic Info Tab
        basic_tab = QWidget()
        basic_layout = QFormLayout()
        
        self.feed_name = ModernInput("Feed Name")
        self.feed_type = ModernComboBox()
        self.feed_type.addItems([
            "Hay", "Silage", "Grain", "Pellets", "Concentrate", 
            "Mineral Supplement", "Vitamin Supplement", "Other"
        ])
        self.feed_type.setEditable(True)
        
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0, 1000000000)
        self.quantity.setSuffix(" kg")
        self.quantity.setDecimals(2)
        
        self.unit_cost = QDoubleSpinBox()
        self.unit_cost.setRange(0, 1000000000)
        self.unit_cost.setPrefix("Rs ")
        self.unit_cost.setDecimals(2)
        
        self.total_cost = QDoubleSpinBox()
        self.total_cost.setRange(0, 1000000000)
        self.total_cost.setPrefix("Rs ")
        self.total_cost.setDecimals(2)
        self.total_cost.setReadOnly(True)
        
        self.low_stock_threshold = QDoubleSpinBox()
        self.low_stock_threshold.setRange(0, 1000000000)
        self.low_stock_threshold.setSuffix(" kg")
        self.low_stock_threshold.setDecimals(2)
        self.low_stock_threshold.setValue(100)
        
        # Connect quantity and cost changes
        self.quantity.valueChanged.connect(self.update_total_cost)
        self.unit_cost.valueChanged.connect(self.update_total_cost)
        
        basic_layout.addRow("Feed Name:", self.feed_name)
        basic_layout.addRow("Feed Type:", self.feed_type)
        basic_layout.addRow("Quantity:", self.quantity)
        basic_layout.addRow("Unit Cost:", self.unit_cost)
        basic_layout.addRow("Total Cost:", self.total_cost)
        basic_layout.addRow("Low Stock Alert:", self.low_stock_threshold)
        
        basic_tab.setLayout(basic_layout)
        tab_widget.addTab(basic_tab, "Basic Info")
        
        # Supplier Tab
        supplier_tab = QWidget()
        supplier_layout = QFormLayout()
        
        self.supplier_name = ModernInput("Supplier Name")
        self.supplier_contact = ModernInput("Contact Person")
        self.supplier_phone = ModernInput("Phone Number")
        self.supplier_email = ModernInput("Email Address")
        self.supplier_address = QTextEdit()
        self.supplier_address.setMaximumHeight(80)
        
        supplier_layout.addRow("Supplier Name:", self.supplier_name)
        supplier_layout.addRow("Contact Person:", self.supplier_contact)
        supplier_layout.addRow("Phone:", self.supplier_phone)
        supplier_layout.addRow("Email:", self.supplier_email)
        supplier_layout.addRow("Address:", self.supplier_address)
        
        supplier_tab.setLayout(supplier_layout)
        tab_widget.addTab(supplier_tab, "Supplier Info")
        
        # Purchase Info Tab
        purchase_tab = QWidget()
        purchase_layout = QFormLayout()
        
        self.purchase_date = QDateEdit()
        self.purchase_date.setDate(QDate.currentDate())
        self.purchase_date.setCalendarPopup(True)
        
        self.expiry_date = QDateEdit()
        self.expiry_date.setDate(QDate.currentDate().addMonths(6))
        self.expiry_date.setCalendarPopup(True)
        
        self.batch_number = ModernInput("Batch/Lot Number")
        self.storage_location = ModernInput("Storage Location")
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        
        purchase_layout.addRow("Purchase Date:", self.purchase_date)
        purchase_layout.addRow("Expiry Date:", self.expiry_date)
        purchase_layout.addRow("Batch Number:", self.batch_number)
        purchase_layout.addRow("Storage Location:", self.storage_location)
        purchase_layout.addRow("Notes:", self.notes)
        
        purchase_tab.setLayout(purchase_layout)
        tab_widget.addTab(purchase_tab, "Purchase Info")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = ModernButton("Save", "success")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = ModernButton("Cancel", "secondary")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_total_cost(self):
        """Update total cost when quantity or unit cost changes."""
        total = self.quantity.value() * self.unit_cost.value()
        self.total_cost.setValue(total)
    
    def populate_fields(self):
        """Populate fields with existing feed data."""
        if not self.feed_data:
            return
        
        self.feed_name.setText(self.feed_data.get('name', ''))
        
        feed_type = self.feed_data.get('type', '')
        index = self.feed_type.findText(feed_type)
        if index >= 0:
            self.feed_type.setCurrentIndex(index)
        else:
            self.feed_type.setCurrentText(feed_type)
        
        self.quantity.setValue(self.feed_data.get('quantity', 0))
        self.unit_cost.setValue(self.feed_data.get('unit_cost', 0))
        self.low_stock_threshold.setValue(self.feed_data.get('low_stock_threshold', 100))
        
        # Supplier info
        self.supplier_name.setText(self.feed_data.get('supplier_name', ''))
        self.supplier_contact.setText(self.feed_data.get('supplier_contact', ''))
        self.supplier_phone.setText(self.feed_data.get('supplier_phone', ''))
        self.supplier_email.setText(self.feed_data.get('supplier_email', ''))
        self.supplier_address.setPlainText(self.feed_data.get('supplier_address', ''))
        
        # Purchase info
        self.batch_number.setText(self.feed_data.get('batch_number', ''))
        self.storage_location.setText(self.feed_data.get('storage_location', ''))
        self.notes.setPlainText(self.feed_data.get('notes', ''))
        
        # Dates
        if self.feed_data.get('purchase_date'):
            date = QDate.fromString(self.feed_data['purchase_date'], Qt.ISODate)
            if date.isValid():
                self.purchase_date.setDate(date)
        
        if self.feed_data.get('expiry_date'):
            date = QDate.fromString(self.feed_data['expiry_date'], Qt.ISODate)
            if date.isValid():
                self.expiry_date.setDate(date)
    
    def get_feed_data(self):
        """Get feed data from form fields."""
        return {
            'name': self.feed_name.text(),
            'type': self.feed_type.currentText(),
            'quantity': self.quantity.value(),
            'unit_cost': self.unit_cost.value(),
            'total_cost': self.total_cost.value(),
            'low_stock_threshold': self.low_stock_threshold.value(),
            'supplier_name': self.supplier_name.text(),
            'supplier_contact': self.supplier_contact.text(),
            'supplier_phone': self.supplier_phone.text(),
            'supplier_email': self.supplier_email.text(),
            'supplier_address': self.supplier_address.toPlainText(),
            'purchase_date': self.purchase_date.date().toString(Qt.ISODate),
            'expiry_date': self.expiry_date.date().toString(Qt.ISODate),
            'batch_number': self.batch_number.text(),
            'storage_location': self.storage_location.text(),
            'notes': self.notes.toPlainText()
        }

class FeedUsageDialog(QDialog):
    """Dialog for recording feed usage."""
    
    def __init__(self, parent=None, feed_items=None):
        super().__init__(parent)
        self.feed_items = feed_items or []
        self.setWindowTitle("Record Feed Usage")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.feed_combo = QComboBox()
        for item in self.feed_items:
            self.feed_combo.addItem(f"{item.get('name', '')} ({item.get('quantity', 0):.1f} kg available)", 
                                  item.get('id'))
        
        self.usage_date = QDateEdit()
        self.usage_date.setDate(QDate.currentDate())
        self.usage_date.setCalendarPopup(True)
        
        self.quantity_used = QDoubleSpinBox()
        self.quantity_used.setRange(0, 1000000000)
        self.quantity_used.setSuffix(" kg")
        self.quantity_used.setDecimals(2)
        
        self.purpose = QComboBox()
        self.purpose.addItems(["Daily Feeding", "Supplemental", "Medical", "Other"])
        self.purpose.setEditable(True)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        
        layout.addRow("Feed Item:", self.feed_combo)
        layout.addRow("Date:", self.usage_date)
        layout.addRow("Quantity Used:", self.quantity_used)
        layout.addRow("Purpose:", self.purpose)
        layout.addRow("Notes:", self.notes)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Record Usage", "success")
        save_btn.clicked.connect(self.accept)
        cancel_btn = ModernButton("Cancel", "secondary")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def get_usage_data(self):
        """Get usage data from form."""
        return {
            'feed_id': self.feed_combo.currentData(),
            'date': self.usage_date.date().toString(Qt.ISODate),
            'quantity_used': self.quantity_used.value(),
            'purpose': self.purpose.currentText(),
            'notes': self.notes.toPlainText()
        }

class FeedManagementWidget(QWidget):
    """Widget for managing feed inventory."""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        self.refresh_table()
        
        # Setup timer for periodic alerts check
        self.alert_timer = QTimer()
        self.alert_timer.timeout.connect(self.check_low_stock_alerts)
        self.alert_timer.start(60000)  # Check every minute
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Modern header with stats
        header_layout = QHBoxLayout()
        
        title = QLabel("🌾 Feed Inventory Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Quick stats cards
        stats_layout = QHBoxLayout()
        self.total_items_card = StatCard("Total Items", "0", "", None, "#3498db")
        self.total_value_card = StatCard("Total Value", "Rs0", "", None, "#27ae60")
        self.low_stock_card = StatCard("Low Stock", "0", "", "down", "#e74c3c")
        
        stats_layout.addWidget(self.total_items_card)
        stats_layout.addWidget(self.total_value_card)
        stats_layout.addWidget(self.low_stock_card)
        
        header_layout.addLayout(stats_layout)
        layout.addLayout(header_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        add_btn = ModernButton("➕ Add Feed Item", "success")
        add_btn.clicked.connect(self.add_feed_item)
        
        edit_btn = ModernButton("✏️ Edit Item", "primary")
        edit_btn.clicked.connect(self.edit_feed_item)
        
        delete_btn = ModernButton("🗑️ Delete Item", "danger")
        delete_btn.clicked.connect(self.delete_feed_item)
        
        usage_btn = ModernButton("📝 Record Usage", "info")
        usage_btn.clicked.connect(self.record_usage)
        
        reorder_btn = ModernButton("📦 Reorder Alert", "warning")
        reorder_btn.clicked.connect(self.create_reorder_alert)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(usage_btn)
        button_layout.addWidget(reorder_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "Quantity", "Unit Cost", "Total Value", 
            "Supplier", "Expiry Date", "Storage", "Status"
        ])
        
        # Modern table styling
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #007bff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #007bff;
                font-weight: bold;
                color: #495057;
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def refresh_table(self):
        """Refresh the feed inventory table."""
        feed_items = self.data_manager.load_data('feed_inventory')
        self.table.setRowCount(len(feed_items))
        
        # Update stats
        total_items = len(feed_items)
        total_value = sum([item.get('total_cost', 0) for item in feed_items])
        low_stock_count = len([item for item in feed_items 
                              if item.get('quantity', 0) <= item.get('low_stock_threshold', 100)])
        
        self.total_items_card.value_label.setText(str(total_items))
        self.total_value_card.value_label.setText(f"Rs{total_value:.2f}")
        self.low_stock_card.value_label.setText(str(low_stock_count))
        
        for row, item in enumerate(feed_items):
            self.table.setItem(row, 0, QTableWidgetItem(str(item.get('id', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(item.get('name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(item.get('type', '')))
            self.table.setItem(row, 3, QTableWidgetItem(f"{item.get('quantity', 0):.1f} kg"))
            self.table.setItem(row, 4, QTableWidgetItem(f"Rs{item.get('unit_cost', 0):.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"Rs{item.get('total_cost', 0):.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(item.get('supplier_name', '')))
            self.table.setItem(row, 7, QTableWidgetItem(item.get('expiry_date', '')))
            self.table.setItem(row, 8, QTableWidgetItem(item.get('storage_location', '')))
            
            # Status with color coding
            status = self.get_item_status(item)
            status_item = QTableWidgetItem(status)
            
            if status == "Low Stock":
                status_item.setBackground(Qt.red)
            elif status == "Expiring Soon":
                status_item.setBackground(Qt.yellow)
            elif status == "Good":
                status_item.setBackground(Qt.green)
            
            self.table.setItem(row, 9, status_item)
    
    def get_item_status(self, item):
        """Determine feed item status."""
        quantity = item.get('quantity', 0)
        threshold = item.get('low_stock_threshold', 100)
        
        if quantity <= threshold:
            return "Low Stock"
        
        # Check expiry date
        expiry_str = item.get('expiry_date', '')
        if expiry_str:
            try:
                expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
                days_to_expiry = (expiry_date - datetime.now().date()).days
                if days_to_expiry <= 30:
                    return "Expiring Soon"
            except:
                pass
        
        return "Good"
    
    def check_low_stock_alerts(self):
        """Check for low stock items and create alerts."""
        feed_items = self.data_manager.load_data('feed_inventory')
        
        for item in feed_items:
            if item.get('quantity', 0) <= item.get('low_stock_threshold', 100):
                # Create alert if not already exists
                self.data_manager.create_alert(
                    'low_stock',
                    f"Low Stock: {item.get('name', 'Unknown Item')}",
                    f"Only {item.get('quantity', 0):.1f} kg remaining. Threshold: {item.get('low_stock_threshold', 100):.1f} kg",
                    priority='high'
                )
    
    def get_selected_item_id(self):
        """Get the ID of the currently selected feed item."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            return self.table.item(current_row, 0).text()
        return None
    
    def add_feed_item(self):
        """Add a new feed item."""
        dialog = FeedItemDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            feed_data = dialog.get_feed_data()
            if self.data_manager.add_record('feed_inventory', feed_data):
                self.refresh_table()
                QMessageBox.information(self, "Success", "Feed item added successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to add feed item!")
    
    def edit_feed_item(self):
        """Edit the selected feed item."""
        item_id = self.get_selected_item_id()
        if not item_id:
            QMessageBox.warning(self, "Warning", "Please select a feed item to edit!")
            return
        
        item_data = self.data_manager.get_record('feed_inventory', item_id)
        if item_data:
            dialog = FeedItemDialog(self, item_data)
            if dialog.exec_() == QDialog.Accepted:
                updated_data = dialog.get_feed_data()
                if self.data_manager.update_record('feed_inventory', item_id, updated_data):
                    self.refresh_table()
                    QMessageBox.information(self, "Success", "Feed item updated successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update feed item!")
    
    def delete_feed_item(self):
        """Delete the selected feed item."""
        item_id = self.get_selected_item_id()
        if not item_id:
            QMessageBox.warning(self, "Warning", "Please select a feed item to delete!")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete feed item ID {item_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.data_manager.delete_record('feed_inventory', item_id):
                self.refresh_table()
                QMessageBox.information(self, "Success", "Feed item deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete feed item!")
    
    def record_usage(self):
        """Record feed usage."""
        feed_items = self.data_manager.load_data('feed_inventory')
        if not feed_items:
            QMessageBox.warning(self, "Warning", "No feed items available!")
            return
        
        dialog = FeedUsageDialog(self, feed_items)
        if dialog.exec_() == QDialog.Accepted:
            usage_data = dialog.get_usage_data()
            
            # Update feed quantity
            feed_id = usage_data['feed_id']
            quantity_used = usage_data['quantity_used']
            
            feed_item = self.data_manager.get_record('feed_inventory', feed_id)
            if feed_item:
                new_quantity = max(0, feed_item.get('quantity', 0) - quantity_used)
                feed_item['quantity'] = new_quantity
                
                if self.data_manager.update_record('feed_inventory', feed_id, feed_item):
                    # Log the usage
                    self.data_manager.log_event('FEED_USAGE', 
                                              f"Used {quantity_used} kg of {feed_item.get('name', 'Unknown')}")
                    self.refresh_table()
                    QMessageBox.information(self, "Success", "Feed usage recorded successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to record feed usage!")
    
    def create_reorder_alert(self):
        """Create reorder alerts for low stock items."""
        feed_items = self.data_manager.load_data('feed_inventory')
        low_stock_items = [item for item in feed_items 
                          if item.get('quantity', 0) <= item.get('low_stock_threshold', 100)]
        
        if not low_stock_items:
            QMessageBox.information(self, "Info", "No items are currently low in stock!")
            return
        
        message = "Low Stock Items:\n\n"
        for item in low_stock_items:
            message += f"• {item.get('name', 'Unknown')}: {item.get('quantity', 0):.1f} kg remaining\n"
            message += f"  Supplier: {item.get('supplier_name', 'Unknown')}\n"
            message += f"  Phone: {item.get('supplier_phone', 'N/A')}\n\n"
        
        QMessageBox.warning(self, "Reorder Alert", message)
