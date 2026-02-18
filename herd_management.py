#!/usr/bin/env python3
"""
Herd Management Module
Complete cattle management with breeding cycles and parentage tracking
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QAbstractItemView, QDialog, QFormLayout, QDateEdit, 
                             QSpinBox, QTextEdit, QMessageBox, QMenu, QDialogButtonBox,
                             QFrame, QScrollArea, QGroupBox, QGridLayout, QListWidget)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QPixmap, QColor
from datetime import datetime, timedelta
from data_manager import DataManager
from lactation_management import LactationDataManager, LactationStageManager

class HerdManagementWidget(QWidget):
    """Herd management with breeding cycles and advanced tracking"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.lactation_manager = LactationDataManager(data_manager)
        self.init_ui()
        self.load_cattle_data()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header with search
        header_layout = QHBoxLayout()
        
        title = QLabel("🐄 Herd Management")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        # Search controls
        header_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by code, name, breed, or status...")
        self.search_input.textChanged.connect(self.filter_cattle)
        header_layout.addWidget(self.search_input)
        
        # Filter by status
        header_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Pregnant", "Dry", "Sick", "Sold"])
        self.status_filter.currentTextChanged.connect(self.filter_cattle)
        header_layout.addWidget(self.status_filter)
        
        layout.addLayout(header_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Cattle")
        add_btn.clicked.connect(self.add_cattle_dialog)
        button_layout.addWidget(add_btn)
        
        breeding_btn = QPushButton("💕 Breeding Management")
        breeding_btn.clicked.connect(self.open_breeding_management)
        button_layout.addWidget(breeding_btn)
        
        health_btn = QPushButton("🏥 Health Records")
        health_btn.clicked.connect(self.open_health_records)
        button_layout.addWidget(health_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Cattle table
        self.cattle_table = QTableWidget()
        self.cattle_table.setColumnCount(13)
        self.cattle_table.setHorizontalHeaderLabels([
            "Code", "Name", "Ear Tag", "Breed", "Age", "Sex", "Status", 
            "Lactation Stage", "DIM", "Mother's Tag", "Birth Date", "Body Condition", 
            "Actions"
        ])
        self.cattle_table.setAlternatingRowColors(True)
        self.cattle_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.cattle_table)
        
        self.setLayout(layout)
    
    def load_cattle_data(self):
        """Load and display cattle data"""
        cattle = self.data_manager.search_entities('cattle')
        self.populate_cattle_table(cattle)
    
    def populate_cattle_table(self, cattle_list):
        """Populate cattle table with data including lactation stage"""
        # Load lactation data
        self.lactation_manager.load_lactation_data()
        
        self.cattle_table.setRowCount(len(cattle_list))
        
        for row, cattle in enumerate(cattle_list):
            self.cattle_table.setItem(row, 0, QTableWidgetItem(cattle.get('code', '')))
            self.cattle_table.setItem(row, 1, QTableWidgetItem(cattle.get('name', '')))
            self.cattle_table.setItem(row, 2, QTableWidgetItem(cattle.get('ear_tag', '')))
            self.cattle_table.setItem(row, 3, QTableWidgetItem(cattle.get('breed', '')))
            
            # Calculate age
            birth_date = cattle.get('birth_date', '')
            age = self.calculate_age(birth_date) if birth_date else 'Unknown'
            self.cattle_table.setItem(row, 4, QTableWidgetItem(str(age)))
            
            self.cattle_table.setItem(row, 5, QTableWidgetItem(cattle.get('sex', '')))
            self.cattle_table.setItem(row, 6, QTableWidgetItem(cattle.get('status', '')))
            
            # Get lactation stage and DIM for female cattle
            cow_code = cattle.get('code', '')
            sex = cattle.get('sex', '')
            
            if sex == 'Female':
                # Get or create lactation record
                lactation_record = self.lactation_manager.get_or_create_lactation_record(cow_code)
                # Update DIM and stage
                self.lactation_manager.update_dim_and_stage(cow_code)
                
                # Lactation stage with color coding
                stage_item = QTableWidgetItem(lactation_record.stage.value)
                stage_color = QColor(LactationStageManager.get_stage_color(lactation_record.stage))
                stage_item.setBackground(stage_color)
                self.cattle_table.setItem(row, 7, stage_item)
                
                # DIM
                self.cattle_table.setItem(row, 8, QTableWidgetItem(str(lactation_record.dim)))
            else:
                # For male cattle, show N/A
                self.cattle_table.setItem(row, 7, QTableWidgetItem("N/A"))
                self.cattle_table.setItem(row, 8, QTableWidgetItem("N/A"))
            
            self.cattle_table.setItem(row, 9, QTableWidgetItem(cattle.get('mothers_tag', cattle.get('dam_code', ''))))
            self.cattle_table.setItem(row, 10, QTableWidgetItem(birth_date))
            self.cattle_table.setItem(row, 11, QTableWidgetItem(str(cattle.get('body_condition', ''))))
            
            # Actions button
            actions_btn = QPushButton("⚙️ Actions")
            actions_btn.clicked.connect(lambda checked, code=cattle.get('code'): self.show_cattle_actions(code))
            self.cattle_table.setCellWidget(row, 12, actions_btn)
    
    def calculate_age(self, birth_date_str):
        """Calculate age from birth date"""
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
            today = datetime.now()
            age = today - birth_date
            
            years = age.days // 365
            months = (age.days % 365) // 30
            
            if years > 0:
                return f"{years}y {months}m"
            else:
                return f"{months}m"
        except:
            return "Unknown"
    
    def filter_cattle(self):
        """Filter cattle based on search and status"""
        search_term = self.search_input.text()
        status_filter = self.status_filter.currentText()
        
        filters = {}
        if status_filter != "All":
            filters['status'] = status_filter.lower()
        
        cattle = self.data_manager.search_entities('cattle', search_term, filters)
        self.populate_cattle_table(cattle)
    
    def add_cattle_dialog(self):
        """Open dialog to add new cattle"""
        dialog = CattleDialog(self.data_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_cattle_data()
    
    def show_cattle_actions(self, cattle_code):
        """Show actions menu for cattle"""
        menu = QMenu(self)
        
        edit_action = menu.addAction("✏️ Edit Details")
        breeding_action = menu.addAction("💕 Breeding Record")
        health_action = menu.addAction("🏥 Health Record")
        photo_action = menu.addAction("📷 Add Photo")
        delete_action = menu.addAction("🗑️ Remove")
        
        action = menu.exec_(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
        
        if action == edit_action:
            self.edit_cattle(cattle_code)
        elif action == breeding_action:
            self.add_breeding_record(cattle_code)
        elif action == health_action:
            self.add_health_record(cattle_code)
        elif action == delete_action:
            self.delete_cattle(cattle_code)
    
    def edit_cattle(self, cattle_code):
        """Edit cattle details"""
        cattle = self.data_manager.get_entity_by_code('cattle', cattle_code)
        if cattle:
            dialog = CattleDialog(self.data_manager, cattle, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_cattle_data()
    
    def add_breeding_record(self, cattle_code):
        """Add breeding record"""
        dialog = BreedingDialog(self.data_manager, cattle_code, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_cattle_data()
    
    def add_health_record(self, cattle_code):
        """Add health record"""
        # Implementation for health record dialog
        pass
    
    def delete_cattle(self, cattle_code):
        """Delete cattle record"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to remove cattle {cattle_code}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.data_manager.delete_entity('cattle', cattle_code)
            self.load_cattle_data()
    
    def open_breeding_management(self):
        """Open breeding management interface"""
        dialog = BreedingManagementDialog(self.data_manager, parent=self)
        dialog.exec_()
    
    def open_health_records(self):
        """Open health records interface"""
        # Implementation for health records
        pass

class CattleDialog(QDialog):
    """Dialog for adding/editing cattle"""
    
    def __init__(self, data_manager, cattle_data=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.cattle_data = cattle_data
        self.setWindowTitle("Add Cattle" if not cattle_data else "Edit Cattle")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()
        
        if cattle_data:
            self.populate_fields()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Basic info
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)
        
        # Ear tag number
        self.ear_tag_input = QLineEdit()
        self.ear_tag_input.setPlaceholderText("e.g., ET-001, 12345")
        form_layout.addRow("Ear Tag Number:", self.ear_tag_input)
        
        self.breed_combo = QComboBox()
        self.breed_combo.addItems([
            "Holstein", "Jersey", "Guernsey", "Ayrshire", 
            "Brown Swiss", "Milking Shorthorn", "Crossbred"
        ])
        form_layout.addRow("Breed:", self.breed_combo)
        
        self.sex_combo = QComboBox()
        self.sex_combo.addItems(["Female", "Male"])
        form_layout.addRow("Sex:", self.sex_combo)
        
        self.birth_date = QDateEdit()
        self.birth_date.setDate(QDate.currentDate())
        form_layout.addRow("Birth Date:", self.birth_date)
        
        # Parentage
        self.sire_combo = QComboBox()
        self.load_parent_options(self.sire_combo, "Male")
        form_layout.addRow("Sire Code:", self.sire_combo)
        
        self.dam_combo = QComboBox()
        self.load_parent_options(self.dam_combo, "Female")
        form_layout.addRow("Dam Code:", self.dam_combo)
        
        # Status and condition
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Pregnant", "Dry", "Sick", "Sold", "Open", "Recheck"])
        form_layout.addRow("Status:", self.status_combo)
        
        # Breeding & Calving Information Group
        breeding_group = QGroupBox("🐄 Breeding & Calving Information")
        breeding_layout = QFormLayout()
        
        # Last calving info
        self.last_calving_date = QDateEdit()
        self.last_calving_date.setCalendarPopup(True)
        breeding_layout.addRow("Last Calving Date:", self.last_calving_date)
        
        self.lactation_number = QSpinBox()
        self.lactation_number.setRange(0, 20)
        self.lactation_number.setValue(0)
        breeding_layout.addRow("Lactation Number:", self.lactation_number)
        
        # Breeding info
        self.last_breeding_date = QDateEdit()
        self.last_breeding_date.setCalendarPopup(True)
        breeding_layout.addRow("Last Breeding Date:", self.last_breeding_date)
        
        self.expected_calving = QDateEdit()
        self.expected_calving.setCalendarPopup(True)
        breeding_layout.addRow("Expected Calving:", self.expected_calving)
        
        # Pregnancy status with edge cases
        self.pregnancy_status = QComboBox()
        self.pregnancy_status.addItems([
            "Not Bred",
            "Bred - Pending Check",
            "Confirmed Pregnant", 
            "Open - Failed AI",
            "Miscarriage/Pregnancy Loss",
            "Aborted"
        ])
        breeding_layout.addRow("Pregnancy Status:", self.pregnancy_status)
        
        # Pregnancy check history
        self.pregnancy_check_date = QDateEdit()
        self.pregnancy_check_date.setCalendarPopup(True)
        breeding_layout.addRow("Pregnancy Check Date:", self.pregnancy_check_date)
        
        self.pregnancy_check_method = QComboBox()
        self.pregnancy_check_method.addItems(["Not Checked", "Ultrasound", "Rectal Palpation", "Blood Test", "Visual"])
        breeding_layout.addRow("Check Method:", self.pregnancy_check_method)
        
        # Breeding method
        self.breeding_method = QComboBox()
        self.breeding_method.addItems(["Not Bred", "AI", "Natural Service", "ET (Embryo Transfer)"])
        breeding_layout.addRow("Breeding Method:", self.breeding_method)
        
        # Sire info
        self.sire_code = QLineEdit()
        self.sire_code.setPlaceholderText("Sire code or bull ID")
        breeding_layout.addRow("Sire Code:", self.sire_code)
        
        breeding_group.setLayout(breeding_layout)
        form_layout.addRow(breeding_group)
        
        # Milking Status (Pregnant cows can still be milking until dry-off)
        milking_group = QGroupBox("🥛 Milking Status")
        milking_layout = QFormLayout()
        
        self.milking_status = QComboBox()
        self.milking_status.addItems(["Not Milking", "Milking", "Dry", "Transitioning to Dry"])
        milking_layout.addRow("Current Milking Status:", self.milking_status)
        
        self.dry_off_date = QDateEdit()
        self.dry_off_date.setCalendarPopup(True)
        milking_layout.addRow("Dry-off Date:", self.dry_off_date)
        
        milking_group.setLayout(milking_layout)
        form_layout.addRow(milking_group)
        
        self.body_condition = QSpinBox()
        self.body_condition.setRange(1, 5)
        self.body_condition.setValue(3)
        form_layout.addRow("Body Condition (1-5):", self.body_condition)
        
        # Additional info
        self.registration_number = QLineEdit()
        form_layout.addRow("Registration Number:", self.registration_number)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_cattle)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_parent_options(self, combo, sex):
        """Load parent options into combo box"""
        combo.addItem("None", "")
        
        cattle = self.data_manager.search_entities('cattle', filters={'sex': sex})
        for animal in cattle:
            combo.addItem(f"{animal.get('code')} - {animal.get('name')}", animal.get('code'))
    
    def populate_fields(self):
        """Populate fields with existing cattle data"""
        if not self.cattle_data:
            return
        
        self.name_input.setText(self.cattle_data.get('name', ''))
        self.ear_tag_input.setText(self.cattle_data.get('ear_tag', ''))
        
        breed = self.cattle_data.get('breed', '')
        index = self.breed_combo.findText(breed)
        if index >= 0:
            self.breed_combo.setCurrentIndex(index)
        
        sex = self.cattle_data.get('sex', '')
        index = self.sex_combo.findText(sex)
        if index >= 0:
            self.sex_combo.setCurrentIndex(index)
        
        birth_date_str = self.cattle_data.get('birth_date', '')
        if birth_date_str:
            birth_date = QDate.fromString(birth_date_str, "yyyy-MM-dd")
            self.birth_date.setDate(birth_date)
        
        # Set parent codes
        sire_code = self.cattle_data.get('sire_code', '')
        if sire_code:
            index = self.sire_combo.findData(sire_code)
            if index >= 0:
                self.sire_combo.setCurrentIndex(index)
        
        dam_code = self.cattle_data.get('dam_code', '')
        if dam_code:
            index = self.dam_combo.findData(dam_code)
            if index >= 0:
                self.dam_combo.setCurrentIndex(index)
        
        status = self.cattle_data.get('status', '')
        index = self.status_combo.findText(status.title())
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        # Populate calving and breeding info
        last_calving = self.cattle_data.get('last_calving_date', '')
        if last_calving:
            self.last_calving_date.setDate(QDate.fromString(last_calving, "yyyy-MM-dd"))
        
        self.lactation_number.setValue(int(self.cattle_data.get('lactation_number', 0)))
        
        last_breeding = self.cattle_data.get('last_breeding_date', '')
        if last_breeding:
            self.last_breeding_date.setDate(QDate.fromString(last_breeding, "yyyy-MM-dd"))
        
        expected_calving = self.cattle_data.get('expected_calving_date', '')
        if expected_calving:
            self.expected_calving.setDate(QDate.fromString(expected_calving, "yyyy-MM-dd"))
        
        pregnancy_status = self.cattle_data.get('pregnancy_status', 'Not Bred')
        index = self.pregnancy_status.findText(pregnancy_status)
        if index >= 0:
            self.pregnancy_status.setCurrentIndex(index)
        
        pregnancy_check = self.cattle_data.get('pregnancy_check_date', '')
        if pregnancy_check:
            self.pregnancy_check_date.setDate(QDate.fromString(pregnancy_check, "yyyy-MM-dd"))
        
        check_method = self.cattle_data.get('pregnancy_check_method', 'Not Checked')
        index = self.pregnancy_check_method.findText(check_method)
        if index >= 0:
            self.pregnancy_check_method.setCurrentIndex(index)
        
        breeding_method = self.cattle_data.get('breeding_method', 'Not Bred')
        index = self.breeding_method.findText(breeding_method)
        if index >= 0:
            self.breeding_method.setCurrentIndex(index)
        
        self.sire_code.setText(self.cattle_data.get('sire_code', ''))
        
        # Populate milking status
        milking_status = self.cattle_data.get('milking_status', 'Not Milking')
        index = self.milking_status.findText(milking_status)
        if index >= 0:
            self.milking_status.setCurrentIndex(index)
        
        dry_off = self.cattle_data.get('dry_off_date', '')
        if dry_off:
            self.dry_off_date.setDate(QDate.fromString(dry_off, "yyyy-MM-dd"))
        
        self.body_condition.setValue(int(self.cattle_data.get('body_condition', 3)))
        self.registration_number.setText(self.cattle_data.get('registration_number', ''))
        self.notes.setPlainText(self.cattle_data.get('notes', ''))
    
    def save_cattle(self):
        """Save cattle data with all breeding and calving information"""
        data = {
            'name': self.name_input.text(),
            'ear_tag': self.ear_tag_input.text(),
            'breed': self.breed_combo.currentText(),
            'sex': self.sex_combo.currentText(),
            'birth_date': self.birth_date.date().toString("yyyy-MM-dd"),
            'sire_code': self.sire_combo.currentData(),
            'dam_code': self.dam_combo.currentData(),
            'status': self.status_combo.currentText().lower(),
            'body_condition': self.body_condition.value(),
            'registration_number': self.registration_number.text(),
            'notes': self.notes.toPlainText(),
            # Calving info
            'last_calving_date': self.last_calving_date.date().toString("yyyy-MM-dd") if self.last_calving_date.date() else '',
            'lactation_number': self.lactation_number.value(),
            # Breeding info
            'last_breeding_date': self.last_breeding_date.date().toString("yyyy-MM-dd") if self.last_breeding_date.date() else '',
            'expected_calving_date': self.expected_calving.date().toString("yyyy-MM-dd") if self.expected_calving.date() else '',
            'pregnancy_status': self.pregnancy_status.currentText(),
            'pregnancy_check_date': self.pregnancy_check_date.date().toString("yyyy-MM-dd") if self.pregnancy_check_date.date() else '',
            'pregnancy_check_method': self.pregnancy_check_method.currentText(),
            'breeding_method': self.breeding_method.currentText(),
            'sire_code': self.sire_code.text(),
            # Milking status
            'milking_status': self.milking_status.currentText(),
            'dry_off_date': self.dry_off_date.date().toString("yyyy-MM-dd") if self.dry_off_date.date() else ''
        }
        
        if self.cattle_data:
            # Update existing
            self.data_manager.update_entity('cattle', self.cattle_data['code'], data)
        else:
            # Create new
            self.data_manager.create_entity('cattle', data)
        
        self.accept()

class BreedingDialog(QDialog):
    """Dialog for breeding records"""
    
    def __init__(self, data_manager, cattle_code, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.cattle_code = cattle_code
        self.setWindowTitle("Breeding Record")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Cattle info
        cattle = self.data_manager.get_entity_by_code('cattle', self.cattle_code)
        cattle_info = QLabel(f"Cattle: {cattle.get('code')} - {cattle.get('name')}")
        cattle_info.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(cattle_info)
        
        # Breeding details
        self.breeding_date = QDateEdit()
        self.breeding_date.setDate(QDate.currentDate())
        form_layout.addRow("Breeding Date:", self.breeding_date)
        
        self.breeding_method = QComboBox()
        self.breeding_method.addItems(["Artificial Insemination", "Natural Service"])
        form_layout.addRow("Method:", self.breeding_method)
        
        self.sire_code = QLineEdit()
        form_layout.addRow("Sire Code:", self.sire_code)
        
        self.expected_calving = QDateEdit()
        # Set expected calving date (approximately 280 days from breeding)
        expected_date = QDate.currentDate().addDays(280)
        self.expected_calving.setDate(expected_date)
        form_layout.addRow("Expected Calving:", self.expected_calving)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        form_layout.addRow("Notes:", self.notes)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_breeding_record)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def save_breeding_record(self):
        """Save breeding record with proper error handling"""
        try:
            # Validate required fields
            sire_code = self.sire_code.text().strip()
            if not sire_code:
                QMessageBox.warning(self, "Validation Error", "Sire code is required.")
                return
                
            # Validate sire exists
            sire = self.data_manager.get_entity_by_code('cattle', sire_code)
            if not sire:
                reply = QMessageBox.question(
                    self, 
                    "Sire Not Found", 
                    f"No cattle found with code: {sire_code}\nDo you want to continue anyway?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # Prepare breeding record data
            data = {
                'cattle_code': self.cattle_code,
                'breeding_date': self.breeding_date.date().toString("yyyy-MM-dd"),
                'method': self.breeding_method.currentText(),
                'sire_code': sire_code,
                'expected_calving_date': self.expected_calving.date().toString("yyyy-MM-dd"),
                'notes': self.notes.toPlainText().strip(),
                'status': 'bred',
                'pregnancy_status': 'pending'  # pending/confirmed/failed
            }
            
            # Create breeding record
            try:
                breeding_code = self.data_manager.create_entity('breeding', data)
                if not breeding_code:
                    raise Exception("Failed to create breeding record")
                
                # Update cattle status to pregnant
                update_success = self.data_manager.update_entity('cattle', self.cattle_code, {
                    'status': 'pregnant',
                    'last_breeding_date': data['breeding_date'],
                    'pregnancy_status': 'pending',
                    'sire_code': sire_code,
                    'last_breeding_method': data['method']
                })
                
                if not update_success:
                    # Rollback breeding record if cattle update fails
                    self.data_manager.delete_entity('breeding', breeding_code)
                    raise Exception("Failed to update cattle record")
                
                QMessageBox.information(self, "Success", "Breeding record saved successfully!")
                self.accept()
                
            except Exception as e:
                self.logger.error(f"Error saving breeding record: {str(e)}")
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to save breeding record: {str(e)}\nPlease check the logs for details."
                )
                
        except Exception as e:
            self.logger.error(f"Unexpected error in save_breeding_record: {str(e)}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"An unexpected error occurred: {str(e)}\nPlease check the logs for details."
            )
        self.accept()

class BreedingManagementDialog(QDialog):
    """Breeding management interface"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("🐄 Breeding Management")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()
        self.load_breeding_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("💕 Breeding Management & Reminders")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # Breeding records table
        self.breeding_table = QTableWidget()
        self.breeding_table.setColumnCount(8)
        self.breeding_table.setHorizontalHeaderLabels([
            "Code", "Cattle Code", "Cattle Name", "Breeding Date", 
            "Method", "Sire Code", "Expected Calving", "Status"
        ])
        layout.addWidget(self.breeding_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Breeding Record")
        add_btn.clicked.connect(self.add_breeding_record)
        button_layout.addWidget(add_btn)
        
        calving_btn = QPushButton("🐄 Record Calving")
        calving_btn.clicked.connect(self.record_calving)
        button_layout.addWidget(calving_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_breeding_data(self):
        """Load breeding records"""
        breeding_records = self.data_manager.search_entities('breeding')
        self.breeding_table.setRowCount(len(breeding_records))
        
        for row, record in enumerate(breeding_records):
            self.breeding_table.setItem(row, 0, QTableWidgetItem(record.get('code', '')))
            self.breeding_table.setItem(row, 1, QTableWidgetItem(record.get('cattle_code', '')))
            
            # Get cattle name
            cattle = self.data_manager.get_entity_by_code('cattle', record.get('cattle_code', ''))
            cattle_name = cattle.get('name', '') if cattle else 'Unknown'
            self.breeding_table.setItem(row, 2, QTableWidgetItem(cattle_name))
            
            self.breeding_table.setItem(row, 3, QTableWidgetItem(record.get('breeding_date', '')))
            self.breeding_table.setItem(row, 4, QTableWidgetItem(record.get('method', '')))
            self.breeding_table.setItem(row, 5, QTableWidgetItem(record.get('sire_code', '')))
            self.breeding_table.setItem(row, 6, QTableWidgetItem(record.get('expected_calving_date', '')))
            self.breeding_table.setItem(row, 7, QTableWidgetItem(record.get('status', '')))
    
    def add_breeding_record(self):
        """Add new breeding record"""
        # Show cattle selection dialog first
        cattle_list = self.data_manager.search_entities('cattle', filters={'sex': 'Female'})
        if not cattle_list:
            QMessageBox.information(self, "Info", "No female cattle available for breeding.")
            return
        
        cattle_codes = [f"{c.get('code')} - {c.get('name')}" for c in cattle_list]
        cattle_code, ok = QInputDialog.getItem(
            self, "Select Cattle", "Choose cattle for breeding:", cattle_codes, 0, False
        )
        
        if ok and cattle_code:
            actual_code = cattle_code.split(' - ')[0]
            dialog = BreedingDialog(self.data_manager, actual_code, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_breeding_data()
    
    def record_calving(self):
        """Record calving event"""
        # Implementation for calving record
        QMessageBox.information(self, "Info", "Calving record feature coming soon!")
