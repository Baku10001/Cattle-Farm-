#!/usr/bin/env python3
"""
Reporting Engine
PDF/Excel/CSV export capabilities for all modules
"""

import os
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
# from reportlab.platypus.charts import LinePlot, BarChart, PieChart
# from reportlab.graphics.shapes import Drawing
import pandas as pd

class ReportingEngine:
    """Reporting engine with multiple export formats"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom report styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center
            textColor=colors.HexColor('#2c3e50')
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
    
    def generate_comprehensive_farm_report(self, output_path: str, format_type: str = 'pdf') -> bool:
        """Generate comprehensive farm management report"""
        try:
            if format_type.lower() == 'pdf':
                return self._generate_pdf_farm_report(output_path)
            elif format_type.lower() == 'excel':
                return self._generate_excel_farm_report(output_path)
            elif format_type.lower() == 'csv':
                return self._generate_csv_farm_report(output_path)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        except Exception as e:
            print(f"Error generating farm report: {e}")
            return False
    
    def _generate_pdf_farm_report(self, output_path: str) -> bool:
        """Generate comprehensive PDF farm report"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title page
        story.append(Paragraph("COMPREHENSIVE FARM MANAGEMENT REPORT", self.styles['CustomTitle']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", self.styles['CustomNormal']))
        story.append(Spacer(1, 0.5*inch))
        
        # Executive Summary
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['CustomHeading']))
        
        # Get summary data
        financial_summary = self.data_manager.get_financial_summary()
        cattle_count = len(self.data_manager.search_entities('cattle'))
        workers_count = len(self.data_manager.search_entities('workers', filters={'status': 'active'}))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Cattle', str(cattle_count)],
            ['Active Workers', str(workers_count)],
            ['Monthly Revenue', f"Rs{financial_summary.get('total_revenue', 0):,.2f}"],
            ['Monthly Expenses', f"Rs{financial_summary.get('total_expenses', 0):,.2f}"],
            ['Net Profit', f"Rs{financial_summary.get('net_profit', 0):,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(PageBreak())
        
        # Herd Management Section
        story.append(Paragraph("HERD MANAGEMENT", self.styles['CustomHeading']))
        
        cattle_data = self.data_manager.search_entities('cattle')
        if cattle_data:
            # Cattle summary by breed
            breed_summary = {}
            for cattle in cattle_data:
                breed = cattle.get('breed', 'Unknown')
                breed_summary[breed] = breed_summary.get(breed, 0) + 1
            
            breed_data = [['Breed', 'Count']]
            for breed, count in breed_summary.items():
                breed_data.append([breed, str(count)])
            
            breed_table = Table(breed_data, colWidths=[2.5*inch, 1.5*inch])
            breed_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(breed_table)
        
        story.append(PageBreak())
        
        # Financial Section
        story.append(Paragraph("FINANCIAL OVERVIEW", self.styles['CustomHeading']))
        
        # Chart of Accounts summary
        accounts = self.data_manager.load_data('chart_of_accounts')
        if accounts:
            account_types = {}
            for account in accounts:
                acc_type = account.get('type', 'Unknown')
                balance = float(account.get('balance', 0))
                account_types[acc_type] = account_types.get(acc_type, 0) + balance
            
            financial_data = [['Account Type', 'Balance']]
            for acc_type, balance in account_types.items():
                financial_data.append([acc_type.title(), f"Rs{balance:,.2f}"])
            
            financial_table = Table(financial_data, colWidths=[2.5*inch, 2*inch])
            financial_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(financial_table)
        
        story.append(PageBreak())
        
        # Workers Section
        story.append(Paragraph("WORKFORCE MANAGEMENT", self.styles['CustomHeading']))
        
        workers_data = self.data_manager.search_entities('workers')
        if workers_data:
            worker_summary = [['Worker Code', 'Name', 'Role', 'Type', 'Daily Rate']]
            for worker in workers_data[:10]:  # Limit to first 10
                worker_summary.append([
                    worker.get('code', ''),
                    worker.get('name', ''),
                    worker.get('role', ''),
                    worker.get('worker_type', ''),
                    f"Rs{worker.get('daily_rate', 0):.2f}"
                ])
            
            workers_table = Table(worker_summary, colWidths=[1.2*inch, 1.5*inch, 1.3*inch, 1*inch, 1*inch])
            workers_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(workers_table)
        
        # Build PDF
        doc.build(story)
        return True
    
    def _generate_excel_farm_report(self, output_path: str) -> bool:
        """Generate comprehensive Excel farm report"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            financial_summary = self.data_manager.get_financial_summary()
            summary_data = {
                'Metric': ['Total Cattle', 'Active Workers', 'Monthly Revenue', 'Monthly Expenses', 'Net Profit'],
                'Value': [
                    len(self.data_manager.search_entities('cattle')),
                    len(self.data_manager.search_entities('workers', filters={'status': 'active'})),
                    financial_summary.get('total_revenue', 0),
                    financial_summary.get('total_expenses', 0),
                    financial_summary.get('net_profit', 0)
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Cattle sheet
            cattle_data = self.data_manager.search_entities('cattle')
            if cattle_data:
                cattle_df = pd.DataFrame(cattle_data)
                cattle_df.to_excel(writer, sheet_name='Cattle', index=False)
            
            # Workers sheet
            workers_data = self.data_manager.search_entities('workers')
            if workers_data:
                workers_df = pd.DataFrame(workers_data)
                workers_df.to_excel(writer, sheet_name='Workers', index=False)
            
            # Financial accounts sheet
            accounts_data = self.data_manager.load_data('chart_of_accounts')
            if accounts_data:
                accounts_df = pd.DataFrame(accounts_data)
                accounts_df.to_excel(writer, sheet_name='Accounts', index=False)
        
        return True
    
    def _generate_csv_farm_report(self, output_path: str) -> bool:
        """Generate CSV export of farm data"""
        # Create directory for CSV files
        base_dir = os.path.splitext(output_path)[0]
        os.makedirs(base_dir, exist_ok=True)
        
        # Export cattle data
        cattle_data = self.data_manager.search_entities('cattle')
        if cattle_data:
            cattle_file = os.path.join(base_dir, 'cattle.csv')
            with open(cattle_file, 'w', newline='', encoding='utf-8') as f:
                if cattle_data:
                    writer = csv.DictWriter(f, fieldnames=cattle_data[0].keys())
                    writer.writeheader()
                    writer.writerows(cattle_data)
        
        # Export workers data
        workers_data = self.data_manager.search_entities('workers')
        if workers_data:
            workers_file = os.path.join(base_dir, 'workers.csv')
            with open(workers_file, 'w', newline='', encoding='utf-8') as f:
                if workers_data:
                    writer = csv.DictWriter(f, fieldnames=workers_data[0].keys())
                    writer.writeheader()
                    writer.writerows(workers_data)
        
        # Export financial accounts
        accounts_data = self.data_manager.load_data('chart_of_accounts')
        if accounts_data:
            accounts_file = os.path.join(base_dir, 'chart_of_accounts.csv')
            with open(accounts_file, 'w', newline='', encoding='utf-8') as f:
                if accounts_data:
                    writer = csv.DictWriter(f, fieldnames=accounts_data[0].keys())
                    writer.writeheader()
                    writer.writerows(accounts_data)
        
        return True
    
    def generate_financial_statement_pdf(self, statement_type: str, output_path: str, 
                                       start_date: str = None, end_date: str = None) -> bool:
        """Generate professional financial statement PDF"""
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create if there's a directory path
                os.makedirs(output_dir, exist_ok=True)
            
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # Header
            story.append(Paragraph("DAIRY FARM MANAGEMENT SYSTEM", self.styles['CustomTitle']))
            story.append(Paragraph(statement_type.upper(), self.styles['CustomHeading']))
            
            if start_date and end_date:
                story.append(Paragraph(f"Period: {start_date} to {end_date}", self.styles['CustomNormal']))
            else:
                story.append(Paragraph(f"As of: {datetime.now().strftime('%B %d, %Y')}", self.styles['CustomNormal']))
            
            story.append(Spacer(1, 0.3*inch))
            
            if statement_type == "Profit & Loss Statement":
                self._add_profit_loss_content(story, start_date, end_date)
            elif statement_type == "Balance Sheet":
                self._add_balance_sheet_content(story)
            elif statement_type == "Cash Flow Statement":
                self._add_cash_flow_content(story, start_date, end_date)
            
            # Build document with error handling
            doc.build(story)
            print(f"Financial statement PDF generated successfully: {output_path}")
            return True
        except Exception as e:
            print(f"Error generating financial statement PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _add_profit_loss_content(self, story, start_date, end_date):
        """Add Profit & Loss statement content with live data"""
        # Fetch financial data for the period
        financial_summary = self.data_manager.get_financial_summary(start_date, end_date)
        
        # Revenue Section
        story.append(Paragraph("REVENUE:", self.styles['CustomHeading']))
        revenue_data = [['Account', 'Amount']]
        total_revenue = financial_summary.get('total_revenue', 0)
        
        revenue_by_account = financial_summary.get('revenue_by_account', {})
        if not revenue_by_account:
            revenue_data.append(['No revenue recorded', 'Rs0.00'])
        else:
            for account, amount in revenue_by_account.items():
                revenue_data.append([account, f"Rs{amount:,.2f}"])
        
        revenue_data.append(['', ''])
        revenue_data.append(['Total Revenue', f"Rs{total_revenue:,.2f}"])
        
        revenue_table = Table(revenue_data, colWidths=[3*inch, 2*inch])
        revenue_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black)
        ]))
        story.append(revenue_table)
        story.append(Spacer(1, 0.2*inch))

        # Expenses Section
        story.append(Paragraph("EXPENSES:", self.styles['CustomHeading']))
        expense_data = [['Account', 'Amount']]
        total_expenses = financial_summary.get('total_expenses', 0)
        
        expenses_by_account = financial_summary.get('expenses_by_account', {})
        if not expenses_by_account:
            expense_data.append(['No expenses recorded', 'Rs0.00'])
        else:
            for account, amount in expenses_by_account.items():
                expense_data.append([account, f"Rs{amount:,.2f}"])

        expense_data.append(['', ''])
        expense_data.append(['Total Expenses', f"Rs{total_expenses:,.2f}"])

        expense_table = Table(expense_data, colWidths=[3*inch, 2*inch])
        expense_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black)
        ]))
        story.append(expense_table)
        story.append(Spacer(1, 0.2*inch))

        # Net Income Section
        net_income = financial_summary.get('net_profit', 0)
        net_income_data = [['NET INCOME', f"Rs{net_income:,.2f}"]]
        
        net_income_table = Table(net_income_data, colWidths=[3*inch, 2*inch])
        net_income_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('LINEABOVE', (0, 0), (-1, -1), 2, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.black)
        ]))
        
        story.append(net_income_table)
    
    def _add_balance_sheet_content(self, story):
        """Add Balance Sheet content with live data"""
        # Get account balances from chart of accounts
        accounts = self.data_manager.load_data('chart_of_accounts')
        
        # Organize accounts by type and category
        assets_by_category = {'current_assets': {}, 'fixed_assets': {}}
        liabilities_by_category = {'current_liabilities': {}, 'long_term_liabilities': {}}
        equity_accounts = {}
        
        for account in accounts:
            acc_type = account.get('type', '')
            category = account.get('category', '')
            name = account.get('name', '')
            balance = float(account.get('balance', 0))
            
            if acc_type == 'asset':
                if category in assets_by_category:
                    assets_by_category[category][name] = balance
            elif acc_type == 'liability':
                if category in liabilities_by_category:
                    liabilities_by_category[category][name] = balance
            elif acc_type == 'equity':
                equity_accounts[name] = balance
        
        # Assets section
        story.append(Paragraph("ASSETS:", self.styles['CustomHeading']))
        
        assets_data = []
        total_current_assets = 0
        total_fixed_assets = 0
        
        # Current Assets
        assets_data.append(['Current Assets:', ''])
        for name, balance in assets_by_category['current_assets'].items():
            assets_data.append([name, f'Rs{balance:,.2f}'])
            total_current_assets += balance
        assets_data.append(['Total Current Assets', f'Rs{total_current_assets:,.2f}'])
        assets_data.append(['', ''])
        
        # Fixed Assets
        assets_data.append(['Fixed Assets:', ''])
        for name, balance in assets_by_category['fixed_assets'].items():
            assets_data.append([name, f'Rs{balance:,.2f}'])
            total_fixed_assets += balance
        assets_data.append(['Total Fixed Assets', f'Rs{total_fixed_assets:,.2f}'])
        assets_data.append(['', ''])
        
        total_assets = total_current_assets + total_fixed_assets
        assets_data.append(['TOTAL ASSETS', f'Rs{total_assets:,.2f}'])
        
        assets_table = Table(assets_data, colWidths=[3*inch, 2*inch])
        assets_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 7), (0, 7), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black)
        ]))
        
        story.append(assets_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Liabilities and Equity section
        story.append(Paragraph("LIABILITIES & EQUITY:", self.styles['CustomHeading']))
        
        # Liabilities and Equity
        liabilities_data = []
        total_current_liabilities = 0
        total_long_term_liabilities = 0
        
        # Current Liabilities
        liabilities_data.append(['Current Liabilities:', ''])
        for name, balance in liabilities_by_category['current_liabilities'].items():
            liabilities_data.append([name, f'Rs{balance:,.2f}'])
            total_current_liabilities += balance
        liabilities_data.append(['Total Current Liabilities', f'Rs{total_current_liabilities:,.2f}'])
        liabilities_data.append(['', ''])
        
        # Long-term Liabilities
        liabilities_data.append(['Long-term Liabilities:', ''])
        for name, balance in liabilities_by_category['long_term_liabilities'].items():
            liabilities_data.append([name, f'Rs{balance:,.2f}'])
            total_long_term_liabilities += balance
        total_liabilities = total_current_liabilities + total_long_term_liabilities
        liabilities_data.append(['Total Liabilities', f'Rs{total_liabilities:,.2f}'])
        liabilities_data.append(['', ''])
        
        # Equity
        liabilities_data.append(['Equity:', ''])
        total_equity = 0
        for name, balance in equity_accounts.items():
            liabilities_data.append([name, f'Rs{balance:,.2f}'])
            total_equity += balance
        liabilities_data.append(['Total Equity', f'Rs{total_equity:,.2f}'])
        liabilities_data.append(['', ''])
        liabilities_data.append(['TOTAL LIABILITIES & EQUITY', f'Rs{total_liabilities + total_equity:,.2f}'])
        
        liabilities_table = Table(liabilities_data, colWidths=[3*inch, 2*inch])
        liabilities_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (0, 5), 'Helvetica-Bold'),
            ('FONTNAME', (0, 9), (0, 9), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black)
        ]))
        
        story.append(liabilities_table)
    
    def _add_cash_flow_content(self, story, start_date, end_date):
        """Add Cash Flow statement content with live data"""
        # Get financial summary
        financial_summary = self.data_manager.get_financial_summary(start_date, end_date)
        
        # Calculate cash flows (simplified - assumes all transactions are cash-based)
        total_revenue = financial_summary.get('total_revenue', 0)
        total_expenses = financial_summary.get('total_expenses', 0)
        expenses_by_account = financial_summary.get('expenses_by_account', {})
        
        # Operating Activities
        story.append(Paragraph("CASH FLOWS FROM OPERATING ACTIVITIES:", self.styles['CustomHeading']))
        
        operating_data = [
            ['Cash Receipts:', ''],
            ['Cash from milk sales', f'Rs{total_revenue:,.2f}'],
            ['Total Cash Receipts', f'Rs{total_revenue:,.2f}'],
            ['', ''],
            ['Cash Payments:', '']
        ]
        
        # Add expense categories
        total_cash_payments = 0
        for account, amount in expenses_by_account.items():
            operating_data.append([account, f'Rs{amount:,.2f}'])
            total_cash_payments += amount
        
        operating_data.extend([
            ['Total Cash Payments', f'Rs{total_cash_payments:,.2f}'],
            ['', ''],
            ['Net Cash from Operating Activities', f'Rs{total_revenue - total_cash_payments:,.2f}']
        ])
        
        operating_table = Table(operating_data, colWidths=[3*inch, 2*inch])
        operating_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (0, 5), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black)
        ]))
        
        story.append(operating_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Summary
        # Get cash account balances
        accounts = self.data_manager.load_data('chart_of_accounts')
        cash_balance = 0
        for account in accounts:
            if 'cash' in account.get('name', '').lower() or 'bank' in account.get('name', '').lower():
                cash_balance += float(account.get('balance', 0))
        
        net_change = total_revenue - total_cash_payments
        beginning_cash = cash_balance - net_change if cash_balance > 0 else 0
        
        summary_data = [
            ['NET CHANGE IN CASH', f'Rs{net_change:,.2f}'],
            ['Cash at Beginning of Period', f'Rs{beginning_cash:,.2f}'],
            ['CASH AT END OF PERIOD', f'Rs{cash_balance:,.2f}']
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black)
        ]))
        
        story.append(summary_table)
    
    def export_entity_data(self, entity_type: str, output_path: str, format_type: str = 'excel') -> bool:
        """Export specific entity data to various formats"""
        try:
            data = self.data_manager.search_entities(entity_type)
            
            if not data:
                return False
            
            if format_type.lower() == 'excel':
                df = pd.DataFrame(data)
                df.to_excel(output_path, index=False)
            elif format_type.lower() == 'csv':
                df = pd.DataFrame(data)
                df.to_csv(output_path, index=False)
            elif format_type.lower() == 'pdf':
                return self._export_entity_pdf(entity_type, data, output_path)
            
            return True
        except Exception as e:
            print(f"Error exporting {entity_type} data: {e}")
            return False
    
    def _export_entity_pdf(self, entity_type: str, data: List[Dict], output_path: str) -> bool:
        """Export entity data as PDF table"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph(f"{entity_type.upper()} REPORT", self.styles['CustomTitle']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", self.styles['CustomNormal']))
        story.append(Spacer(1, 0.3*inch))
        
        if data:
            # Create table with data
            headers = list(data[0].keys())
            table_data = [headers]
            
            for item in data:
                row = [str(item.get(header, '')) for header in headers]
                table_data.append(row)
            
            # Calculate column widths
            col_width = 7.5 / len(headers) * inch
            col_widths = [col_width] * len(headers)
            
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
        
        doc.build(story)
        return True
