from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from datetime import datetime
import os
from typing import List, Dict, Any

class PDFGenerator:
    """Handles PDF generation for reports and invoices."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
    def create_health_report(self, cow_data: Dict, health_records: List[Dict], filename: str) -> bool:
        """Generate health report PDF for a specific cow."""
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Title
            title = Paragraph(f"Health Report - Cow ID: {cow_data.get('id', 'N/A')}", self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Cow basic info
            cow_info = [
                ['Cow ID:', cow_data.get('id', 'N/A')],
                ['Breed:', cow_data.get('breed', 'N/A')],
                ['Age:', f"{cow_data.get('age', 'N/A')} years"],
                ['Weight:', f"{cow_data.get('weight', 'N/A')} kg"],
                ['Purchase Date:', cow_data.get('purchase_date', 'N/A')]
            ]
            
            cow_table = Table(cow_info, colWidths=[2*inch, 3*inch])
            cow_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(cow_table)
            story.append(Spacer(1, 20))
            
            # Health records
            if health_records:
                health_title = Paragraph("Health Records", self.styles['Heading2'])
                story.append(health_title)
                story.append(Spacer(1, 12))
                
                health_data = [['Date', 'Status', 'Condition', 'Medication', 'Notes']]
                for record in health_records:
                    health_data.append([
                        record.get('date', ''),
                        record.get('status', ''),
                        record.get('condition', ''),
                        record.get('medication', ''),
                        record.get('notes', '')[:50] + '...' if len(record.get('notes', '')) > 50 else record.get('notes', '')
                    ])
                
                health_table = Table(health_data, colWidths=[1*inch, 1*inch, 1.5*inch, 1.5*inch, 2*inch])
                health_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(health_table)
            
            doc.build(story)
            return True
        except Exception as e:
            return False
    
    def create_milk_report(self, production_data: List[Dict], delivery_data: List[Dict], 
                          start_date: str, end_date: str, filename: str) -> bool:
        """Generate detailed milk production and delivery report with complete data tables."""
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Title
            title = Paragraph(f"Detailed Milk Production Report ({start_date} to {end_date})", self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Production summary
            total_production = sum([p.get('quantity', 0) for p in production_data])
            avg_daily = total_production / max(len(production_data), 1)
            
            summary_data = [
                ['Total Production:', f"{total_production:.2f} liters"],
                ['Average Daily:', f"{avg_daily:.2f} liters"],
                ['Total Days:', str(len(production_data))],
                ['Date Range:', f"{start_date} to {end_date}"]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold')
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Detailed Production Records
            if production_data:
                prod_title = Paragraph("Complete Daily Production Records", self.styles['Heading2'])
                story.append(prod_title)
                story.append(Spacer(1, 12))
                
                prod_table_data = [['Date', 'Morning (L)', 'Evening (L)', 'Total (L)', 'Quality Grade', 'Fat %', 'Notes']]
                for prod in production_data:
                    prod_table_data.append([
                        prod.get('date', ''),
                        f"{prod.get('morning_quantity', 0):.2f}",
                        f"{prod.get('evening_quantity', 0):.2f}",
                        f"{prod.get('quantity', 0):.2f}",
                        prod.get('quality_grade', 'N/A'),
                        f"{prod.get('fat_content', 0):.1f}%",
                        prod.get('notes', '')[:25] + '...' if len(prod.get('notes', '')) > 25 else prod.get('notes', '')
                    ])
                
                prod_table = Table(prod_table_data, colWidths=[1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.6*inch, 2.3*inch])
                prod_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(prod_table)
                story.append(Spacer(1, 20))
            
            # Complete Delivery Records
            if delivery_data:
                del_title = Paragraph("Complete Delivery Records", self.styles['Heading2'])
                story.append(del_title)
                story.append(Spacer(1, 12))
                
                del_table_data = [['Date', 'Buyer', 'Contact', 'Quantity (L)', 'Base Rate', 'Quality Bonus', 'Final Rate', 'Total Amount']]
                total_delivered = 0
                total_amount = 0
                total_bonus = 0
                
                for delivery in delivery_data:
                    quantity = delivery.get('quantity', 0)
                    base_rate = delivery.get('base_rate', delivery.get('rate', 0))
                    quality_bonus = delivery.get('quality_bonus', 0)
                    final_rate = delivery.get('final_rate', base_rate + quality_bonus)
                    amount = delivery.get('total_amount', quantity * final_rate)
                    
                    total_delivered += quantity
                    total_amount += amount
                    total_bonus += quantity * quality_bonus
                    
                    del_table_data.append([
                        delivery.get('date', ''),
                        delivery.get('buyer', ''),
                        delivery.get('buyer_contact', '')[:15] + '...' if len(delivery.get('buyer_contact', '')) > 15 else delivery.get('buyer_contact', ''),
                        f"{quantity:.2f}",
                        f"Rs {base_rate:.2f}",
                        f"Rs {quality_bonus:.2f}",
                        f"Rs {final_rate:.2f}",
                        f"Rs {amount:.0f}"
                    ])
                
                # Add totals row
                del_table_data.append([
                    'TOTALS', '', '', f"{total_delivered:.2f}", '', f"Rs {total_bonus:.0f}", '', f"Rs {total_amount:.0f}"
                ])
                
                del_table = Table(del_table_data, colWidths=[0.9*inch, 1.2*inch, 0.9*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.9*inch])
                del_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(del_table)
            
            doc.build(story)
            return True
        except Exception as e:
            return False
    
    def create_expense_report(self, expenses: List[Dict], start_date: str, end_date: str, filename: str) -> bool:
        """Generate expense report."""
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Title
            title = Paragraph(f"Expense Report ({start_date} to {end_date})", self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Category summary
            categories = {}
            total_expenses = 0
            
            for expense in expenses:
                category = expense.get('category', 'Other')
                amount = expense.get('amount', 0)
                categories[category] = categories.get(category, 0) + amount
                total_expenses += amount
            
            # Category breakdown table
            cat_data = [['Category', 'Amount', 'Percentage']]
            for category, amount in categories.items():
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                cat_data.append([category, f"{amount:.2f}", f"{percentage:.1f}%"])
            
            cat_data.append(['TOTAL', f"{total_expenses:.2f}", "100.0%"])
            
            cat_table = Table(cat_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(cat_table)
            story.append(Spacer(1, 20))
            
            # Detailed expenses
            if expenses:
                detail_title = Paragraph("Detailed Expenses", self.styles['Heading2'])
                story.append(detail_title)
                story.append(Spacer(1, 12))
                
                detail_data = [['Date', 'Category', 'Description', 'Amount']]
                for expense in expenses:
                    detail_data.append([
                        expense.get('date', ''),
                        expense.get('category', ''),
                        expense.get('description', '')[:40] + '...' if len(expense.get('description', '')) > 40 else expense.get('description', ''),
                        f"{expense.get('amount', 0):.2f}"
                    ])
                
                detail_table = Table(detail_data, colWidths=[1.5*inch, 1.5*inch, 3*inch, 1*inch])
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(detail_table)
            
            doc.build(story)
            return True
        except Exception as e:
            return False
    
    def create_invoice(self, invoice_data: Dict, filename: str) -> bool:
        """Generate invoice PDF."""
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Header
            title = Paragraph("INVOICE", self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Invoice details
            invoice_info = [
                ['Invoice #:', invoice_data.get('invoice_number', '')],
                ['Date:', invoice_data.get('date', '')],
                ['Customer:', invoice_data.get('customer_name', '')],
                ['Address:', invoice_data.get('customer_address', '')]
            ]
            
            info_table = Table(invoice_info, colWidths=[1.5*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica')
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Items
            items_data = [['Description', 'Quantity', 'Rate', 'Amount']]
            total_amount = 0
            
            for item in invoice_data.get('items', []):
                quantity = item.get('quantity', 0)
                rate = item.get('rate', 0)
                amount = quantity * rate
                total_amount += amount
                
                items_data.append([
                    item.get('description', ''),
                    str(quantity),
                    f"{rate:.2f}",
                    f"{amount:.2f}"
                ])
            
            # Add total row
            items_data.append(['', '', 'TOTAL:', f"{total_amount:.2f}"])
            
            items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1.5*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 20))
            
            # Footer
            footer = Paragraph("Thank you for your business!", self.styles['Normal'])
            story.append(footer)
            
            doc.build(story)
            return True
        except Exception as e:
            return False
    
    def create_milk_invoice_with_quality_bonus(self, invoice_data: Dict, filename: str) -> bool:
        """Generate professional milk delivery invoice with quality bonuses."""
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Professional header
            header_table = Table([
                ['🥛 PREMIUM DAIRY FARM', 'INVOICE'],
                ['Fresh Quality Milk Products', f"#{invoice_data.get('invoice_number', 'INV-001')}"]
            ], colWidths=[4*inch, 2*inch])
            
            header_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, 0), 16),
                ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (1, 0), (1, 0), 20),
                ('TEXTCOLOR', (1, 0), (1, 0), colors.darkblue),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(header_table)
            story.append(Spacer(1, 20))
            
            # Invoice details
            invoice_details = Table([
                ['Invoice Date:', invoice_data.get('date', datetime.now().strftime('%Y-%m-%d'))],
                ['Delivery Date:', invoice_data.get('delivery_date', '')],
                ['Customer:', invoice_data.get('customer_name', '')],
                ['Address:', invoice_data.get('customer_address', '')],
                ['Payment Terms:', invoice_data.get('payment_terms', 'Net 30 days')]
            ], colWidths=[1.5*inch, 4*inch])
            
            invoice_details.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(invoice_details)
            story.append(Spacer(1, 20))
            
            # Delivery items with quality bonus breakdown
            items_header = Paragraph("Milk Delivery Details", self.styles['Heading2'])
            story.append(items_header)
            story.append(Spacer(1, 12))
            
            items_data = [['Description', 'Quantity (L)', 'Quality Grade', 'Base Rate', 'Quality Bonus', 'Final Rate', 'Amount']]
            
            total_amount = 0
            total_quantity = 0
            total_bonus = 0
            
            for item in invoice_data.get('items', []):
                quantity = item.get('quantity', 0)
                base_rate = item.get('base_rate', 0)
                quality_bonus = item.get('quality_bonus', 0)
                final_rate = base_rate + quality_bonus
                amount = quantity * final_rate
                
                total_quantity += quantity
                total_amount += amount
                total_bonus += quantity * quality_bonus
                
                items_data.append([
                    item.get('description', 'Fresh Milk'),
                    f"{quantity:.2f}",
                    item.get('quality_grade', 'A'),
                    f"Rs {base_rate:.2f}",
                    f"Rs {quality_bonus:.2f}",
                    f"Rs {final_rate:.2f}",
                    f"Rs {amount:.0f}"
                ])
            
            # Summary rows
            items_data.append(['', '', '', '', '', '', ''])
            items_data.append(['TOTALS:', f"{total_quantity:.2f} L", '', '', f"Rs {total_bonus:.0f}", '', f"Rs {total_amount:.0f}"])
            
            items_table = Table(items_data, colWidths=[1.5*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.7*inch, 0.8*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -2), 1, colors.black),
                ('LINEBELOW', (0, -2), (-1, -2), 2, colors.black)
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 20))
            
            # Payment information
            payment_info = Paragraph(
                f"<b>Total Amount Due: Rs {total_amount:.0f}</b><br/>"
                f"Quality Bonus Earned: Rs {total_bonus:.0f}<br/>"
                f"Thank you for choosing our premium dairy products!<br/>"
                f"Payment due within {invoice_data.get('payment_terms', '30 days')}",
                self.styles['Normal']
            )
            story.append(payment_info)
            
            doc.build(story)
            return True
        except Exception as e:
            return False
    
    def create_vaccination_schedule_report(self, vaccination_data: List[Dict], filename: str) -> bool:
        """Generate vaccination schedule and reminder report."""
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Title
            title = Paragraph("💉 VACCINATION SCHEDULE REPORT", self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Summary statistics
            total_scheduled = len(vaccination_data)
            overdue = len([v for v in vaccination_data if v.get('status') == 'overdue'])
            due_soon = len([v for v in vaccination_data if v.get('status') == 'due_soon'])
            completed = len([v for v in vaccination_data if v.get('status') == 'completed'])
            
            summary_data = [
                ['Total Scheduled:', str(total_scheduled)],
                ['Overdue:', str(overdue)],
                ['Due Soon (7 days):', str(due_soon)],
                ['Completed:', str(completed)]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 1*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.orange),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT')
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Detailed schedule
            if vaccination_data:
                detail_title = Paragraph("Detailed Vaccination Schedule", self.styles['Heading2'])
                story.append(detail_title)
                story.append(Spacer(1, 12))
                
                detail_data = [['Cow ID', 'Vaccine Type', 'Due Date', 'Status', 'Notes']]
                
                for vaccination in vaccination_data:
                    status = vaccination.get('status', 'scheduled')
                    detail_data.append([
                        vaccination.get('cow_id', ''),
                        vaccination.get('vaccine_type', ''),
                        vaccination.get('due_date', ''),
                        status.upper(),
                        vaccination.get('notes', '')[:30] + '...' if len(vaccination.get('notes', '')) > 30 else vaccination.get('notes', '')
                    ])
                
                detail_table = Table(detail_data, colWidths=[1*inch, 2*inch, 1.2*inch, 1*inch, 2.3*inch])
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(detail_table)
            
            doc.build(story)
            return True
        except Exception as e:
            return False
    
    def create_feed_inventory_report(self, feed_data: List[Dict], filename: str) -> bool:
        """Generate feed inventory and usage report."""
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Title
            title = Paragraph("🌾 FEED INVENTORY REPORT", self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Inventory summary
            total_value = sum(item.get('total_cost', 0) for item in feed_data)
            low_stock_items = len([item for item in feed_data if item.get('current_stock', 0) <= item.get('low_stock_threshold', 0)])
            
            summary_data = [
                ['Total Inventory Items:', str(len(feed_data))],
                ['Total Inventory Value:', f"Rs {total_value:.0f}"],
                ['Low Stock Items:', str(low_stock_items)],
                ['Report Date:', datetime.now().strftime('%Y-%m-%d')]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.green),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT')
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Detailed inventory
            if feed_data:
                detail_title = Paragraph("Detailed Feed Inventory", self.styles['Heading2'])
                story.append(detail_title)
                story.append(Spacer(1, 12))
                
                detail_data = [['Feed Type', 'Current Stock', 'Low Stock Alert', 'Unit Cost', 'Total Value', 'Supplier']]
                
                for item in feed_data:
                    current_stock = item.get('current_stock', 0)
                    threshold = item.get('low_stock_threshold', 0)
                    status = "⚠️ LOW" if current_stock <= threshold else "✅ OK"
                    
                    detail_data.append([
                        item.get('feed_type', ''),
                        f"{current_stock:.1f} {item.get('unit', 'kg')}",
                        status,
                        f"Rs {item.get('unit_cost', 0):.0f}",
                        f"Rs {item.get('total_cost', 0):.0f}",
                        item.get('supplier_name', '')[:20] + '...' if len(item.get('supplier_name', '')) > 20 else item.get('supplier_name', '')
                    ])
                
                detail_table = Table(detail_data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 1.4*inch])
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(detail_table)
            
            doc.build(story)
            return True
        except Exception as e:
            return False
