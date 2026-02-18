#!/usr/bin/env python3
"""
Financial Management Module - Sage 50 Style
Complete accounting system with General Ledger, A/R, A/P, and Financial Statements
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QAbstractItemView, QDialog, QFormLayout, QDateEdit, 
                             QSpinBox, QTextEdit, QMessageBox, QTabWidget, QFrame,
                             QScrollArea, QGroupBox, QGridLayout, QDialogButtonBox,
                             QFileDialog, QMenu, QHeaderView, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QFont, QColor
from datetime import datetime, timedelta
from data_manager import DataManager
import json
from transaction_dialog import TransactionDialog

class FinancialManagementWidget(QWidget):
    """Main financial management interface"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("💰 Financial Management")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin: 10px; padding: 10px;")
        layout.addWidget(header)
        
        # Tab widget for different financial modules
        self.tab_widget = QTabWidget()
        
        # General Ledger
        self.tab_widget.addTab(self.create_general_ledger_tab(), "📊 General Ledger")
        
        # Accounts Receivable
        self.tab_widget.addTab(self.create_accounts_receivable_tab(), "💳 A/R")
        
        # Accounts Payable  
        self.tab_widget.addTab(self.create_accounts_payable_tab(), "💸 A/P")
        
        # Financial Statements
        self.tab_widget.addTab(self.create_financial_statements_tab(), "📈 Statements")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def create_general_ledger_tab(self):
        """Create enhanced General Ledger interface with transaction management"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Filter controls
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout()
        
        # Date range
        filter_layout.addWidget(QLabel("Date Range:"))
        self.gl_start_date = QDateEdit(calendarPopup=True)
        self.gl_start_date.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.gl_start_date)
        
        filter_layout.addWidget(QLabel("to"))
        self.gl_end_date = QDateEdit(calendarPopup=True)
        self.gl_end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.gl_end_date)
        
        # Account filter
        filter_layout.addWidget(QLabel("Account:"))
        self.gl_account_filter = QComboBox()
        self.gl_account_filter.addItem("All Accounts", "")
        self.load_accounts_combo(self.gl_account_filter)
        filter_layout.addWidget(self.gl_account_filter)
        
        # Transaction type filter
        filter_layout.addWidget(QLabel("Type:"))
        self.gl_type_filter = QComboBox()
        self.gl_type_filter.addItems(["All Types", "Income", "Expense", "Asset", "Liability", "Equity"])
        filter_layout.addWidget(self.gl_type_filter)
        
        # Search box
        filter_layout.addWidget(QLabel("Search:"))
        self.gl_search = QLineEdit()
        self.gl_search.setPlaceholderText("Search by description or reference...")
        filter_layout.addWidget(self.gl_search)
        
        # Action buttons
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self.refresh_general_ledger)
        filter_layout.addWidget(btn_refresh)
        
        btn_export = QPushButton("📤 Export")
        btn_export.clicked.connect(self.export_general_ledger)
        filter_layout.addWidget(btn_export)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        self.gl_summary_cards = {}
        self.gl_summary_labels = {}

        debit_card, debit_label = self.create_summary_card("Total Debit", "Rs0.00", "#3498db")
        self.gl_summary_cards['debit'] = debit_card
        self.gl_summary_labels['debit'] = debit_label

        credit_card, credit_label = self.create_summary_card("Total Credit", "Rs0.00", "#2ecc71")
        self.gl_summary_cards['credit'] = credit_card
        self.gl_summary_labels['credit'] = credit_label

        balance_card, balance_label = self.create_summary_card("Balance", "Rs0.00", "#9b59b6")
        self.gl_summary_cards['balance'] = balance_card
        self.gl_summary_labels['balance'] = balance_label
        
        for card in self.gl_summary_cards.values():
            summary_layout.addWidget(card)
        
        layout.addLayout(summary_layout)
        
        # General Ledger table with context menu
        self.gl_table = QTableWidget()
        self.gl_table.setColumnCount(9)
        self.gl_table.setHorizontalHeaderLabels([
            "Date", "Trans. ID", "Account Code", "Account Name", "Description", 
            "Reference", "Debit", "Credit", "Balance"
        ])
        self.gl_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.gl_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.gl_table.customContextMenuRequested.connect(self.show_gl_context_menu)
        
        # Enable sorting
        self.gl_table.setSortingEnabled(True)
        
        layout.addWidget(self.gl_table)
        
        # Add transaction button
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Add Transaction")
        btn_add.clicked.connect(self.show_add_transaction_dialog)
        btn_layout.addWidget(btn_add)
        
        btn_reverse = QPushButton("↩️ Reverse Transaction")
        btn_reverse.clicked.connect(self.reverse_transaction)
        btn_reverse.setEnabled(False)
        btn_layout.addWidget(btn_reverse)
        
        layout.addLayout(btn_layout)
        
        # Connect signals
        self.gl_table.itemSelectionChanged.connect(
            lambda: btn_reverse.setEnabled(len(self.gl_table.selectedItems()) > 0)
        )
        
        widget.setLayout(layout)
        self.refresh_general_ledger()  # Initial load
        return widget
    
    def create_accounts_receivable_tab(self):
        """Create Accounts Receivable interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # A/R Summary cards
        summary_layout = QHBoxLayout()
        
        # Create summary cards for A/R
        total_ar = self.calculate_total_ar()
        overdue_ar = self.calculate_overdue_ar()
        
        total_ar_card, _ = self.create_summary_card("Total A/R", f"Rs{total_ar:,.2f}", "#3498db")
        summary_layout.addWidget(total_ar_card)

        overdue_ar_card, _ = self.create_summary_card("Overdue", f"Rs{overdue_ar:,.2f}", "#e74c3c")
        summary_layout.addWidget(overdue_ar_card)

        current_ar_card, _ = self.create_summary_card("Current", f"Rs{total_ar - overdue_ar:,.2f}", "#27ae60")
        summary_layout.addWidget(current_ar_card)
        
        layout.addLayout(summary_layout)
        
        # A/R table
        self.ar_table = QTableWidget()
        self.ar_table.setColumnCount(8)
        self.ar_table.setHorizontalHeaderLabels([
            "Customer Code", "Customer Name", "Invoice Code", "Date", 
            "Due Date", "Amount", "Paid", "Balance"
        ])
        layout.addWidget(self.ar_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_accounts_payable_tab(self):
        """Create Accounts Payable interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # A/P Summary cards
        summary_layout = QHBoxLayout()
        
        total_ap = self.calculate_total_ap()
        overdue_ap = self.calculate_overdue_ap()
        
        total_ap_card, _ = self.create_summary_card("Total A/P", f"Rs{total_ap:,.2f}", "#f39c12")
        summary_layout.addWidget(total_ap_card)

        overdue_ap_card, _ = self.create_summary_card("Overdue", f"Rs{overdue_ap:,.2f}", "#e74c3c")
        summary_layout.addWidget(overdue_ap_card)

        current_ap_card, _ = self.create_summary_card("Current", f"Rs{total_ap - overdue_ap:,.2f}", "#27ae60")
        summary_layout.addWidget(current_ap_card)
        
        layout.addLayout(summary_layout)
        
        # A/P table
        self.ap_table = QTableWidget()
        self.ap_table.setColumnCount(8)
        self.ap_table.setHorizontalHeaderLabels([
            "Supplier Code", "Supplier Name", "Bill Code", "Date", 
            "Due Date", "Amount", "Paid", "Balance"
        ])
        layout.addWidget(self.ap_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_financial_statements_tab(self):
        """Create Financial Statements interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Statement selection
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Statement Type:"))
        self.statement_type = QComboBox()
        self.statement_type.addItems([
            "Profit & Loss Statement",
            "Balance Sheet", 
            "Cash Flow Statement"
        ])
        controls_layout.addWidget(self.statement_type)
        
        controls_layout.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Daily", "Weekly", "Monthly", "Quarterly", "Yearly", "Custom"])
        controls_layout.addWidget(self.period_combo)
        
        generate_btn = QPushButton("📊 Generate Statement")
        generate_btn.clicked.connect(self.generate_financial_statement)
        controls_layout.addWidget(generate_btn)
        
        export_btn = QPushButton("📄 Export PDF")
        export_btn.clicked.connect(self.export_statement)
        controls_layout.addWidget(export_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Statement display area
        self.statement_display = QTextEdit()
        self.statement_display.setReadOnly(True)
        self.statement_display.setFont(QFont("Courier", 10))
        layout.addWidget(self.statement_display)
        
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
        return card, value_label
    
    def load_accounts_combo(self, combo):
        """Load chart of accounts into combo box"""
        combo.clear()
        combo.addItem("All Accounts", "")
        
        accounts = self.data_manager.load_data('chart_of_accounts')
        for account in accounts:
            combo.addItem(f"{account['code']} - {account['name']}", account['code'])
    
    def calculate_total_ar(self):
        """Calculate total accounts receivable"""
        invoices = self.data_manager.search_entities('invoices')
        total = 0.0
        for invoice in invoices:
            if invoice.get('status') != 'paid':
                total += float(invoice.get('total_amount', 0))
        return total
    
    def calculate_overdue_ar(self):
        """Calculate overdue accounts receivable"""
        invoices = self.data_manager.search_entities('invoices')
        total = 0.0
        today = datetime.now().date()
        
        for invoice in invoices:
            if invoice.get('status') != 'paid':
                due_date_str = invoice.get('due_date', '')
                if due_date_str:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                    if due_date < today:
                        total += float(invoice.get('total_amount', 0))
        return total
    
    def calculate_total_ap(self):
        """Calculate total accounts payable"""
        expenses = self.data_manager.search_entities('expenses')
        total = 0.0
        for expense in expenses:
            if expense.get('status') != 'paid':
                total += float(expense.get('amount', 0))
        return total
    
    def calculate_overdue_ap(self):
        """Calculate overdue accounts payable"""
        expenses = self.data_manager.search_entities('expenses')
        total = 0.0
        today = datetime.now().date()
        
        for expense in expenses:
            if expense.get('status') != 'paid':
                due_date_str = expense.get('due_date', '')
                if due_date_str:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                    if due_date < today:
                        total += float(expense.get('amount', 0))
        return total
    
    def refresh_general_ledger(self):
        """Refresh the general ledger view with current filters"""
        try:
            # Clear existing data
            self.gl_table.setRowCount(0)
            
            # Get filter values
            start_date = self.gl_start_date.date().toString('yyyy-MM-dd')
            end_date = self.gl_end_date.date().toString('yyyy-MM-dd')
            account_filter = self.gl_account_filter.currentData()
            transaction_type = self.gl_type_filter.currentText()
            search_term = self.gl_search.text().lower()
            
            # Load transactions from data manager
            transactions = self.data_manager.load_data('transactions')
            accounts = self.data_manager.load_data('chart_of_accounts')
            
            if not transactions:
                transactions = []
                
            if not accounts:
                accounts = []
                
            # Create account code to name mapping
            account_map = {acc['code']: acc['name'] for acc in accounts}
            
            # Filter transactions
            filtered_transactions = []
            total_debit = 0.0
            total_credit = 0.0
            
            for trans in transactions:
                # Apply date filter
                if not (start_date <= trans.get('date', '') <= end_date):
                    continue
                    
                # Apply account filter
                if account_filter and trans.get('account_code') != account_filter:
                    continue
                    
                # Apply type filter
                if transaction_type != 'All Types':
                    account = next((a for a in accounts if a['code'] == trans.get('account_code')), {})
                    if account.get('type', '') != transaction_type.upper():
                        continue
                        
                # Apply search term
                if search_term and (search_term not in trans.get('description', '').lower() and 
                                  search_term not in trans.get('reference', '').lower()):
                    continue
                    
                filtered_transactions.append(trans)
                
                # Update totals
                amount = float(trans.get('amount', 0))
                if trans.get('transaction_type') == 'debit':
                    total_debit += amount
                else:
                    total_credit += amount
            
            # Sort transactions by date (newest first)
            filtered_transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # Populate table
            self.gl_table.setRowCount(len(filtered_transactions))
            for row, trans in enumerate(filtered_transactions):
                account_code = trans.get('account_code', '')
                account_name = account_map.get(account_code, 'Unknown Account')
                
                self.gl_table.setItem(row, 0, QTableWidgetItem(trans.get('date', '')))
                self.gl_table.setItem(row, 1, QTableWidgetItem(trans.get('id', '')))
                self.gl_table.setItem(row, 2, QTableWidgetItem(account_code))
                self.gl_table.setItem(row, 3, QTableWidgetItem(account_name))
                self.gl_table.setItem(row, 4, QTableWidgetItem(trans.get('description', '')))
                self.gl_table.setItem(row, 5, QTableWidgetItem(trans.get('reference', '')))
                
                if trans.get('transaction_type') == 'debit':
                    self.gl_table.setItem(row, 6, QTableWidgetItem(f"Rs{float(trans.get('amount', 0)):,.2f}"))
                    self.gl_table.setItem(row, 7, QTableWidgetItem("Rs0.00"))
                else:
                    self.gl_table.setItem(row, 6, QTableWidgetItem("Rs0.00"))
                    self.gl_table.setItem(row, 7, QTableWidgetItem(f"Rs{float(trans.get('amount', 0)):,.2f}"))
                
                # Calculate running balance (simplified)
                balance = float(trans.get('amount', 0))
                if trans.get('transaction_type') == 'credit':
                    balance = -balance
                
                self.gl_table.setItem(row, 8, QTableWidgetItem(f"Rs{balance:,.2f}"))
            
            # Update summary cards
            self.gl_summary_labels['debit'].setText(f"Rs{total_debit:,.2f}")
            self.gl_summary_labels['credit'].setText(f"Rs{total_credit:,.2f}")
            self.gl_summary_labels['balance'].setText(f"Rs{(total_debit - total_credit):,.2f}")
            
            # Resize columns to fit content
            self.gl_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh general ledger: {str(e)}")
            print(f"Error refreshing general ledger: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def generate_financial_statement(self):
        """Generate selected financial statement"""
        statement_type = self.statement_type.currentText()
        
        if statement_type == "Profit & Loss Statement":
            self.generate_profit_loss_statement()
        elif statement_type == "Balance Sheet":
            self.generate_balance_sheet()
        elif statement_type == "Cash Flow Statement":
            self.generate_cash_flow_statement()
    
    def generate_profit_loss_statement(self):
        """Generate Profit & Loss Statement"""
        # Get date range based on period selection
        start_date, end_date = self.get_period_dates()
        
        # Get revenue and expense data
        revenue_accounts = self.data_manager.search_entities('chart_of_accounts', 
                                                           filters={'type': 'revenue'})
        expense_accounts = self.data_manager.search_entities('chart_of_accounts', 
                                                           filters={'type': 'expense'})
        
        # Calculate totals (simplified - would need actual transaction data)
        total_revenue = sum(float(acc.get('balance', 0)) for acc in revenue_accounts)
        total_expenses = sum(float(acc.get('balance', 0)) for acc in expense_accounts)
        net_income = total_revenue - total_expenses
        
        # Format statement
        statement = f"""
DAIRY FARM MANAGEMENT SYSTEM
PROFIT & LOSS STATEMENT
Period: {start_date} to {end_date}

REVENUE:
Milk Sales Revenue                    Rs{total_revenue:>12,.2f}
Other Revenue                         Rs{0:>12,.2f}
                                     ________________
Total Revenue                         Rs{total_revenue:>12,.2f}

EXPENSES:
Direct Costs:
  Feed Expenses                       Rs{0:>12,.2f}
  Veterinary Expenses                 Rs{0:>12,.2f}
  Breeding Expenses                   Rs{0:>12,.2f}
                                     ________________
Total Direct Costs                    Rs{0:>12,.2f}

Operating Expenses:
  Salaries & Wages                    Rs{0:>12,.2f}
  Utilities                           Rs{0:>12,.2f}
  Equipment Maintenance               Rs{0:>12,.2f}
  Insurance                           Rs{0:>12,.2f}
                                     ________________
Total Operating Expenses              Rs{0:>12,.2f}

                                     ________________
Total Expenses                        Rs{total_expenses:>12,.2f}

                                     ________________
NET INCOME                            Rs{net_income:>12,.2f}
                                     ================
"""
        
        self.statement_display.setPlainText(statement)
    
    def generate_balance_sheet(self):
        """Generate Balance Sheet"""
        # Get account balances
        asset_accounts = self.data_manager.search_entities('chart_of_accounts', 
                                                         filters={'type': 'asset'})
        liability_accounts = self.data_manager.search_entities('chart_of_accounts', 
                                                             filters={'type': 'liability'})
        equity_accounts = self.data_manager.search_entities('chart_of_accounts', 
                                                          filters={'type': 'equity'})
        
        total_assets = sum(float(acc.get('balance', 0)) for acc in asset_accounts)
        total_liabilities = sum(float(acc.get('balance', 0)) for acc in liability_accounts)
        total_equity = sum(float(acc.get('balance', 0)) for acc in equity_accounts)
        
        statement = f"""
DAIRY FARM MANAGEMENT SYSTEM
BALANCE SHEET
As of {datetime.now().strftime('%Y-%m-%d')}

ASSETS:
Current Assets:
  Cash in Hand                        Rs{0:>12,.2f}
  Bank Account                        Rs{0:>12,.2f}
  Accounts Receivable                 Rs{self.calculate_total_ar():>12,.2f}
  Feed Inventory                      Rs{0:>12,.2f}
  Medicine Inventory                  Rs{0:>12,.2f}
                                     ________________
Total Current Assets                  Rs{0:>12,.2f}

Fixed Assets:
  Cattle - Dairy Cows                 Rs{0:>12,.2f}
  Farm Equipment                      Rs{0:>12,.2f}
  Buildings                           Rs{0:>12,.2f}
                                     ________________
Total Fixed Assets                    Rs{0:>12,.2f}

                                     ________________
TOTAL ASSETS                          Rs{total_assets:>12,.2f}

LIABILITIES & EQUITY:
Current Liabilities:
  Accounts Payable                    Rs{self.calculate_total_ap():>12,.2f}
  Wages Payable                       Rs{0:>12,.2f}
                                     ________________
Total Current Liabilities             Rs{0:>12,.2f}

Long-term Liabilities:
  Long-term Loans                     Rs{0:>12,.2f}
                                     ________________
Total Liabilities                     Rs{total_liabilities:>12,.2f}

Equity:
  Owner Equity                        Rs{0:>12,.2f}
  Retained Earnings                   Rs{0:>12,.2f}
                                     ________________
Total Equity                          Rs{total_equity:>12,.2f}

                                     ________________
TOTAL LIABILITIES & EQUITY            Rs{total_liabilities + total_equity:>12,.2f}
                                     ================
"""
        
        self.statement_display.setPlainText(statement)
    
    def generate_cash_flow_statement(self):
        """Generate Cash Flow Statement"""
        start_date, end_date = self.get_period_dates()
        
        # Get cash transactions (simplified)
        cash_inflows = 0.0  # From sales, receivables collection
        cash_outflows = 0.0  # From expenses, payables payment
        
        net_cash_flow = cash_inflows - cash_outflows
        
        statement = f"""
DAIRY FARM MANAGEMENT SYSTEM
CASH FLOW STATEMENT
Period: {start_date} to {end_date}

CASH FLOWS FROM OPERATING ACTIVITIES:
Cash Receipts:
  Cash from milk sales                Rs{0:>12,.2f}
  Collection of receivables           Rs{0:>12,.2f}
                                     ________________
Total Cash Receipts                   Rs{cash_inflows:>12,.2f}

Cash Payments:
  Feed purchases                      Rs{0:>12,.2f}
  Veterinary payments                 Rs{0:>12,.2f}
  Salary payments                     Rs{0:>12,.2f}
  Other operating expenses            Rs{0:>12,.2f}
                                     ________________
Total Cash Payments                   Rs{cash_outflows:>12,.2f}

                                     ________________
Net Cash from Operating Activities    Rs{net_cash_flow:>12,.2f}

CASH FLOWS FROM INVESTING ACTIVITIES:
  Equipment purchases                 Rs{0:>12,.2f}
  Cattle purchases                    Rs{0:>12,.2f}
                                     ________________
Net Cash from Investing Activities    Rs{0:>12,.2f}

CASH FLOWS FROM FINANCING ACTIVITIES:
  Loan proceeds                       Rs{0:>12,.2f}
  Loan payments                       Rs{0:>12,.2f}
  Owner withdrawals                   Rs{0:>12,.2f}
                                     ________________
Net Cash from Financing Activities    Rs{0:>12,.2f}

                                     ________________
NET CHANGE IN CASH                    Rs{net_cash_flow:>12,.2f}
Cash at Beginning of Period           Rs{0:>12,.2f}
                                     ________________
CASH AT END OF PERIOD                 Rs{net_cash_flow:>12,.2f}
                                     ================
"""
        
        self.statement_display.setPlainText(statement)
    
    def get_period_dates(self):
        """Get start and end dates based on period selection"""
        period = self.period_combo.currentText()
        today = datetime.now()
        
        if period == "Daily":
            return today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        elif period == "Weekly":
            start = today - timedelta(days=7)
            return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        elif period == "Monthly":
            start = today.replace(day=1)
            return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        elif period == "Yearly":
            start = today.replace(month=1, day=1)
            return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        else:
            return today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    
    def export_statement(self):
        """Export financial statement to PDF"""
        from pdf_generator import PDFGenerator
        
        statement_text = self.statement_display.toPlainText()
        if not statement_text.strip():
            QMessageBox.warning(self, "Warning", "Please generate a statement first.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Statement", 
            f"financial_statement_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF files (*.pdf)"
        )
        
        if filename:
            pdf_gen = PDFGenerator()
            # Create PDF with statement content
            QMessageBox.information(self, "Success", f"Statement exported to {filename}")

    # ===== General Ledger Methods =====
    
    def show_gl_context_menu(self, position):
        """Show context menu for GL table"""
        menu = QMenu()
        view_details = menu.addAction("🔍 View Details")
        reverse_action = menu.addAction("↩️ Reverse Transaction")
        export_action = menu.addAction("📤 Export Selected")
        
        action = menu.exec_(self.gl_table.viewport().mapToGlobal(position))
        
        if action == view_details:
            self.view_transaction_details()
        elif action == reverse_action:
            self.reverse_transaction()
        elif action == export_action:
            self.export_selected_transactions()

    
    def is_account_of_type(self, account_code, account_type):
        """Check if an account is of a specific type"""
        account = self.get_account_by_code(account_code)
        if not account:
            return False
        return account.get('type', '').lower() == account_type.lower()
    
    def get_account_by_code(self, account_code):
        """Get account details by code"""
        accounts = self.data_manager.search_entities('chart_of_accounts')
        for account in accounts:
            if account.get('code') == account_code:
                return account
        return None
    
    def show_add_transaction_dialog(self):
        """Show dialog to add a new transaction"""
        dialog = TransactionDialog(self.data_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            transaction_data = dialog.get_transaction_data()
            self.add_transaction(transaction_data)
    
    def add_transaction(self, transaction_data):
        """Add a new transaction to the general ledger"""
        try:
            # Validate transaction
            if not transaction_data or 'lines' not in transaction_data:
                raise ValueError("Invalid transaction data")
            
            # Calculate totals
            total_debit = sum(float(line.get('debit', 0)) for line in transaction_data['lines'])
            total_credit = sum(float(line.get('credit', 0)) for line in transaction_data['lines'])
            
            # Check if transaction is balanced
            if abs(total_debit - total_credit) > 0.01:  # Allow for floating point rounding
                raise ValueError(f"Transaction is not balanced. Debits ({total_debit:,.2f}) must equal credits ({total_credit:,.2f})")
            
            # Generate transaction ID
            trans_id = f"TRX-{QDateTime.currentDateTime().toString('yyyyMMdd-hhmmss')}"
            
            # Prepare transaction
            transaction = {
                'id': trans_id,
                'date': transaction_data.get('date', QDate.currentDate().toString("yyyy-MM-dd")),
                'description': transaction_data.get('description', '').strip(),
                'reference': transaction_data.get('reference', '').strip(),
                'created_at': QDateTime.currentDateTime().toString(Qt.ISODate),
                'lines': []
            }
            
            # Add transaction lines
            for line in transaction_data['lines']:
                if not line.get('account_code'):
                    continue
                    
                transaction['lines'].append({
                    'account_code': line['account_code'],
                    'description': line.get('description', '').strip(),
                    'debit': float(line.get('debit', 0)),
                    'credit': float(line.get('credit', 0))
                })
            
            # Save transaction
            transactions = self.data_manager.load_data('transactions', [])
            transactions.append(transaction)
            self.data_manager.save_data('transactions', transactions)
            
            # Update account balances
            for line in transaction['lines']:
                self.update_account_balance(
                    line['account_code'],
                    line.get('debit', 0) - line.get('credit', 0)
                )
            
            # Refresh the view
            self.refresh_general_ledger()
            QMessageBox.information(self, "Success", "Transaction recorded successfully!")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record transaction: {str(e)}")
            return False
    
    def update_account_balance(self, account_code, amount):
        """Update an account's balance by the specified amount"""
        accounts = self.data_manager.load_data('chart_of_accounts')
        for acc in accounts:
            if acc['code'] == account_code:
                acc['balance'] = float(acc.get('balance', 0)) + float(amount)
                break
        self.data_manager.save_data('chart_of_accounts', accounts)
    
    def reverse_transaction(self):
        """Reverse the selected transaction"""
        selected = self.gl_table.selectedItems()
        if not selected:
            return
            
        trans_id = self.gl_table.item(selected[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, 
            "Confirm Reversal", 
            f"Are you sure you want to reverse transaction {trans_id}?\nThis will create a reversing entry.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                transactions = self.data_manager.load_data('transactions', [])
                transaction = next((t for t in transactions if t.get('id') == trans_id), None)
                
                if not transaction:
                    raise ValueError("Transaction not found")
                
                # Create reversal transaction
                reversal = {
                    'id': f"REV-{trans_id}-{QDateTime.currentDateTime().toString('hhmmss')}",
                    'date': QDate.currentDate().toString("yyyy-MM-dd"),
                    'description': f"Reversal of {trans_id}",
                    'reference': f"Reversal of {trans_id}",
                    'created_at': QDateTime.currentDateTime().toString(Qt.ISODate),
                    'lines': []
                }
                
                # Reverse all lines
                for line in transaction.get('lines', []):
                    reversal['lines'].append({
                        'account_code': line.get('account_code', ''),
                        'description': f"Reversal: {line.get('description', '')}",
                        'debit': line.get('credit', 0),
                        'credit': line.get('debit', 0)
                    })
                
                # Save reversal
                transactions.append(reversal)
                self.data_manager.save_data('transactions', transactions)
                
                # Update account balances
                for line in reversal['lines']:
                    self.update_account_balance(
                        line['account_code'],
                        line.get('debit', 0) - line.get('credit', 0)
                    )
                
                # Refresh the view
                self.refresh_general_ledger()
                QMessageBox.information(self, "Success", f"Transaction {trans_id} has been reversed.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reverse transaction: {str(e)}")
    
    def view_transaction_details(self):
        """Show details of the selected transaction"""
        selected = self.gl_table.selectedItems()
        if not selected:
            return
            
        trans_id = self.gl_table.item(selected[0].row(), 1).text()
        transactions = self.data_manager.load_data('transactions', [])
        transaction = next((t for t in transactions if t.get('id') == trans_id), None)
        
        if not transaction:
            QMessageBox.warning(self, "Not Found", "Transaction details not found.")
            return
        
        # Create and show details dialog
        dialog = TransactionDetailsDialog(transaction, self)
        dialog.exec_()
    
    def export_general_ledger(self):
        """Export general ledger to CSV"""
        try:
            # Get save file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export General Ledger",
                f"general_ledger_{QDate.currentDate().toString('yyyyMMdd')}.csv",
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Write CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                # Write header
                f.write("Date,Transaction ID,Account Code,Account Name,Description,Reference,Debit,Credit,Balance\n")
                
                # Write data
                for row in range(self.gl_table.rowCount()):
                    line = []
                    for col in range(self.gl_table.columnCount()):
                        item = self.gl_table.item(row, col)
                        cell_value = item.text() if item else ""
                        # Handle special characters in CSV
                        if ',' in cell_value or '"' in cell_value:
                            cell_value = f'"{cell_value.replace("\"", "\"\"")}"'
                        line.append(cell_value)
                    f.write(','.join(line) + '\n')
            
            QMessageBox.information(self, "Export Successful", 
                                 f"General ledger exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", 
                              f"Failed to export general ledger: {str(e)}")
    
    def export_selected_transactions(self):
        """Export selected transactions to CSV"""
        selected = self.gl_table.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select transactions to export.")
            return
        
        try:
            # Get save file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Selected Transactions",
                f"transactions_{QDate.currentDate().toString('yyyyMMdd')}.csv",
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Get unique transaction IDs from selected rows
            selected_rows = set(item.row() for item in selected)
            transactions = {}
            
            for row in selected_rows:
                trans_id = self.gl_table.item(row, 1).text()
                if trans_id not in transactions:
                    transactions[trans_id] = []
                
                # Get all data for this row
                row_data = []
                for col in range(self.gl_table.columnCount()):
                    item = self.gl_table.item(row, col)
                    row_data.append(item.text() if item else "")
                transactions[trans_id].append(row_data)
            
            # Write CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                # Write header
                f.write("Date,Transaction ID,Account Code,Account Name,Description,Reference,Debit,Credit,Balance\n")
                
                # Write data for each transaction
                for trans_id, lines in transactions.items():
                    for line in lines:
                        # Handle special characters in CSV
                        line = [f'"{item.replace("\"", "\"\"")}"' if ',' in item or '"' in item else item 
                              for item in line]
                        f.write(','.join(line) + '\n')
            
            QMessageBox.information(self, "Export Successful", 
                                 f"Selected transactions exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", 
                              f"Failed to export transactions: {str(e)}")
