from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QDialogButtonBox, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PyQt5.QtCore import QDate

class TransactionDialog(QDialog):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("Add New Transaction")
        self.setMinimumWidth(600)

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.date_edit = QDateEdit(QDate.currentDate())
        self.description_edit = QLineEdit()
        self.reference_edit = QLineEdit()

        self.form_layout.addRow("Date:", self.date_edit)
        self.form_layout.addRow("Description:", self.description_edit)
        self.form_layout.addRow("Reference:", self.reference_edit)

        self.layout.addLayout(self.form_layout)

        self.lines_table = QTableWidget()
        self.lines_table.setColumnCount(4)
        self.lines_table.setHorizontalHeaderLabels(["Account", "Description", "Debit", "Credit"])
        self.lines_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.lines_table)

        self.add_line_button = QPushButton("Add Line")
        self.add_line_button.clicked.connect(self.add_table_row)
        self.layout.addWidget(self.add_line_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.add_table_row() # Start with one empty row

    def add_table_row(self):
        row_position = self.lines_table.rowCount()
        self.lines_table.insertRow(row_position)

        account_combo = QComboBox()
        accounts = self.data_manager.load_data('chart_of_accounts')
        for account in accounts:
            account_combo.addItem(f"{account['code']} - {account['name']}", account['code'])

        self.lines_table.setCellWidget(row_position, 0, account_combo)
        self.lines_table.setItem(row_position, 1, QTableWidgetItem())
        self.lines_table.setItem(row_position, 2, QTableWidgetItem("0.00"))
        self.lines_table.setItem(row_position, 3, QTableWidgetItem("0.00"))

    def get_transaction_data(self):
        lines = []
        for row in range(self.lines_table.rowCount()):
            account_combo = self.lines_table.cellWidget(row, 0)
            lines.append({
                'account_code': account_combo.currentData(),
                'description': self.lines_table.item(row, 1).text(),
                'debit': self.lines_table.item(row, 2).text(),
                'credit': self.lines_table.item(row, 3).text(),
            })

        return {
            'date': self.date_edit.date().toString('yyyy-MM-dd'),
            'description': self.description_edit.text(),
            'reference': self.reference_edit.text(),
            'lines': lines
        }
