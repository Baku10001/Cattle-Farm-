#!/usr/bin/env python3
"""
Data Manager for Dairy Farm Management System
Data management with unique codes for all entities
"""

import os
import json
import logging
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import uuid
import re

class CodeGenerator:
    """Generates unique codes for all entities"""
    
    def __init__(self):
        self.prefixes = {
            'cattle': 'COW',
            'customer': 'CUST',
            'supplier': 'SUPP',
            'worker': 'WORK',
            'product': 'PROD',
            'expense': 'EXP',
            'invoice': 'INV',
            'receipt': 'REC',
            'feed': 'FEED',
            'medicine': 'MED',
            'treatment': 'TREAT',
            'vaccination': 'VAC',
            'breeding': 'BREED',
            'account': 'ACC'
        }
    
    def generate_code(self, entity_type: str, sequence_num: int = None) -> str:
        """Generate unique code for entity type"""
        prefix = self.prefixes.get(entity_type, 'GEN')
        timestamp = datetime.now().strftime('%y%m')
        
        if sequence_num:
            return f"{prefix}-{timestamp}-{sequence_num:04d}"
        else:
            # Use current timestamp for uniqueness
            unique_id = datetime.now().strftime('%d%H%M%S')
            return f"{prefix}-{timestamp}-{unique_id}"
    
    def validate_code(self, code: str) -> bool:
        """Validate code format"""
        pattern = r'^[A-Z]+-\d{4}-\d{4,6}$'
        return bool(re.match(pattern, code))

class SearchFilter:
    """Advanced search and filter capabilities"""
    
    @staticmethod
    def search_entities(data: List[Dict], search_term: str, search_fields: List[str]) -> List[Dict]:
        """Search entities by term in specified fields"""
        if not search_term:
            return data
        
        search_term = search_term.lower()
        results = []
        
        for item in data:
            for field in search_fields:
                field_value = str(item.get(field, '')).lower()
                if search_term in field_value:
                    results.append(item)
                    break
        
        return results
    
    @staticmethod
    def filter_by_date_range(data: List[Dict], date_field: str, start_date: str, end_date: str) -> List[Dict]:
        """Filter entities by date range"""
        if not start_date or not end_date:
            return data
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            results = []
            for item in data:
                item_date_str = item.get(date_field, '')
                if item_date_str:
                    item_date = datetime.strptime(item_date_str.split('T')[0], '%Y-%m-%d')
                    if start <= item_date <= end:
                        results.append(item)
            
            return results
        except ValueError:
            return data
    
    @staticmethod
    def filter_by_field(data: List[Dict], field: str, value: Any) -> List[Dict]:
        """Filter entities by specific field value"""
        if not value:
            return data
        
        return [item for item in data if item.get(field) == value]

class DataManager:
    """Data manager with unique coding and search features"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.code_generator = CodeGenerator()
        self.search_filter = SearchFilter()
        self.ensure_data_directory()
        self.setup_logging()
        self.initialize_chart_of_accounts()
    
    def setup_logging(self):
        """Setup logging system"""
        log_file = os.path.join(self.data_dir, 'system.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_data_directory(self):
        """Create data directory structure"""
        directories = [
            self.data_dir,
            os.path.join(self.data_dir, 'backups'),
            os.path.join(self.data_dir, 'exports'),
            os.path.join(self.data_dir, 'photos'),
            os.path.join(self.data_dir, 'reports')
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def initialize_chart_of_accounts(self):
        """Initialize chart of accounts for financial management"""
        accounts = self.load_data('chart_of_accounts')
        if not accounts:
            default_accounts = [
                # Assets
                {'code': 'ACC-1000-0001', 'name': 'Cash in Hand', 'type': 'asset', 'category': 'current_assets', 'balance': 0.0},
                {'code': 'ACC-1000-0002', 'name': 'Bank Account', 'type': 'asset', 'category': 'current_assets', 'balance': 0.0},
                {'code': 'ACC-1100-0001', 'name': 'Accounts Receivable', 'type': 'asset', 'category': 'current_assets', 'balance': 0.0},
                {'code': 'ACC-1200-0001', 'name': 'Feed Inventory', 'type': 'asset', 'category': 'current_assets', 'balance': 0.0},
                {'code': 'ACC-1200-0002', 'name': 'Medicine Inventory', 'type': 'asset', 'category': 'current_assets', 'balance': 0.0},
                {'code': 'ACC-1500-0001', 'name': 'Cattle - Dairy Cows', 'type': 'asset', 'category': 'fixed_assets', 'balance': 0.0},
                {'code': 'ACC-1600-0001', 'name': 'Farm Equipment', 'type': 'asset', 'category': 'fixed_assets', 'balance': 0.0},
                {'code': 'ACC-1700-0001', 'name': 'Buildings', 'type': 'asset', 'category': 'fixed_assets', 'balance': 0.0},
                
                # Liabilities
                {'code': 'ACC-2000-0001', 'name': 'Accounts Payable', 'type': 'liability', 'category': 'current_liabilities', 'balance': 0.0},
                {'code': 'ACC-2100-0001', 'name': 'Wages Payable', 'type': 'liability', 'category': 'current_liabilities', 'balance': 0.0},
                {'code': 'ACC-2500-0001', 'name': 'Long-term Loans', 'type': 'liability', 'category': 'long_term_liabilities', 'balance': 0.0},
                
                # Equity
                {'code': 'ACC-3000-0001', 'name': 'Owner Equity', 'type': 'equity', 'category': 'equity', 'balance': 0.0},
                {'code': 'ACC-3100-0001', 'name': 'Retained Earnings', 'type': 'equity', 'category': 'equity', 'balance': 0.0},
                
                # Revenue
                {'code': 'ACC-4000-0001', 'name': 'Milk Sales Revenue', 'type': 'revenue', 'category': 'operating_revenue', 'balance': 0.0},
                {'code': 'ACC-4100-0001', 'name': 'Cattle Sales Revenue', 'type': 'revenue', 'category': 'operating_revenue', 'balance': 0.0},
                {'code': 'ACC-4900-0001', 'name': 'Other Revenue', 'type': 'revenue', 'category': 'other_revenue', 'balance': 0.0},
                
                # Expenses
                {'code': 'ACC-5000-0001', 'name': 'Feed Expenses', 'type': 'expense', 'category': 'direct_costs', 'balance': 0.0},
                {'code': 'ACC-5100-0001', 'name': 'Veterinary Expenses', 'type': 'expense', 'category': 'direct_costs', 'balance': 0.0},
                {'code': 'ACC-5200-0001', 'name': 'Breeding Expenses', 'type': 'expense', 'category': 'direct_costs', 'balance': 0.0},
                {'code': 'ACC-6000-0001', 'name': 'Salaries & Wages', 'type': 'expense', 'category': 'operating_expenses', 'balance': 0.0},
                {'code': 'ACC-6100-0001', 'name': 'Utilities', 'type': 'expense', 'category': 'operating_expenses', 'balance': 0.0},
                {'code': 'ACC-6200-0001', 'name': 'Equipment Maintenance', 'type': 'expense', 'category': 'operating_expenses', 'balance': 0.0},
                {'code': 'ACC-6300-0001', 'name': 'Insurance', 'type': 'expense', 'category': 'operating_expenses', 'balance': 0.0},
                {'code': 'ACC-7000-0001', 'name': 'Depreciation Expense', 'type': 'expense', 'category': 'non_operating_expenses', 'balance': 0.0}
            ]
            self.save_data('chart_of_accounts', default_accounts)
    
    def load_data(self, filename: str) -> Union[Dict, List]:
        """Load data from JSON file"""
        file_path = os.path.join(self.data_dir, f"{filename}.json")
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {} if filename in ['settings', 'dashboard_stats'] else []
        except Exception as e:
            self.logger.error(f"Error loading {filename}: {str(e)}")
            return {} if filename in ['settings', 'dashboard_stats'] else []
    
    def save_data(self, filename: str, data: Union[Dict, List]) -> bool:
        """Save data to JSON file"""
        file_path = os.path.join(self.data_dir, f"{filename}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {filename}: {str(e)}")
            return False
    
    def generate_next_sequence(self, entity_type: str) -> int:
        """Generate next sequence number for entity type"""
        sequences = self.load_data('sequences')
        if not isinstance(sequences, dict):
            sequences = {}
        
        current = sequences.get(entity_type, 0)
        next_seq = current + 1
        sequences[entity_type] = next_seq
        self.save_data('sequences', sequences)
        return next_seq
    
    def create_entity(self, entity_type: str, data: Dict) -> str:
        """Create new entity with unique code"""
        # Generate unique code
        sequence = self.generate_next_sequence(entity_type)
        code = self.code_generator.generate_code(entity_type, sequence)
        
        # Add metadata
        data.update({
            'code': code,
            'created_date': datetime.now().isoformat(),
            'modified_date': datetime.now().isoformat(),
            'created_by': 'system',
            'status': 'active'
        })
        
        # Save to appropriate data file
        entities = self.load_data(entity_type)
        entities.append(data)
        self.save_data(entity_type, entities)
        
        self.logger.info(f"Created {entity_type} with code: {code}")
        return code
    
    def update_entity(self, entity_type: str, code: str, data: Dict) -> bool:
        """Update entity by code"""
        entities = self.load_data(entity_type)
        
        for i, entity in enumerate(entities):
            if entity.get('code') == code:
                data['modified_date'] = datetime.now().isoformat()
                entities[i].update(data)
                self.save_data(entity_type, entities)
                self.logger.info(f"Updated {entity_type} with code: {code}")
                return True
        
        return False
    
    def delete_entity(self, entity_type: str, code: str) -> bool:
        """Soft delete entity by code"""
        return self.update_entity(entity_type, code, {'status': 'deleted'})
    
    def get_entity_by_code(self, entity_type: str, code: str) -> Optional[Dict]:
        """Get entity by code"""
        entities = self.load_data(entity_type)
        for entity in entities:
            if entity.get('code') == code and entity.get('status') != 'deleted':
                return entity
        return None
    
    def search_entities(self, entity_type: str, search_term: str = '', filters: Dict = None) -> List[Dict]:
        """Search entities with advanced filtering"""
        entities = self.load_data(entity_type)
        
        # Filter out deleted entities
        active_entities = [e for e in entities if e.get('status') != 'deleted']
        
        # Apply search term
        if search_term:
            search_fields = ['code', 'name', 'description', 'notes']
            active_entities = self.search_filter.search_entities(active_entities, search_term, search_fields)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if field == 'date_range' and isinstance(value, dict):
                    date_field = value.get('field', 'created_date')
                    start_date = value.get('start')
                    end_date = value.get('end')
                    active_entities = self.search_filter.filter_by_date_range(
                        active_entities, date_field, start_date, end_date
                    )
                else:
                    active_entities = self.search_filter.filter_by_field(active_entities, field, value)
        
        return active_entities
    
    def get_financial_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get financial summary for dashboard with account breakdown"""
        # Get all transactions within date range
        filters = {}
        if start_date and end_date:
            filters['date_range'] = {'field': 'date', 'start': start_date, 'end': end_date}

        invoices = self.search_entities('invoices', filters=filters.copy())
        expenses = self.search_entities('expenses', filters=filters.copy())
        
        # Calculate totals and group by account
        total_revenue = 0
        revenue_by_account = {}
        for inv in invoices:
            amount = float(inv.get('total_amount', 0))
            total_revenue += amount
            # This is a simplification; real system would have line items linked to revenue accounts
            account_name = "Milk Sales Revenue"
            revenue_by_account[account_name] = revenue_by_account.get(account_name, 0) + amount

        total_expenses = 0
        expenses_by_account = {}
        for exp in expenses:
            amount = float(exp.get('amount', 0))
            total_expenses += amount
            account_name = exp.get('category', 'Uncategorized') # Assuming expense has a category
            expenses_by_account[account_name] = expenses_by_account.get(account_name, 0) + amount

        net_profit = total_revenue - total_expenses
        
        return {
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'invoice_count': len(invoices),
            'expense_count': len(expenses),
            'revenue_by_account': revenue_by_account,
            'expenses_by_account': expenses_by_account
        }
    
    def backup_system(self, backup_path: str) -> bool:
        """Create comprehensive system backup"""
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                # Backup all JSON data files
                for filename in os.listdir(self.data_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(self.data_dir, filename)
                        zipf.write(file_path, f"data/{filename}")
                
                # Backup photos and reports
                for subdir in ['photos', 'reports']:
                    subdir_path = os.path.join(self.data_dir, subdir)
                    if os.path.exists(subdir_path):
                        for root, dirs, files in os.walk(subdir_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_path = os.path.relpath(file_path, self.data_dir)
                                zipf.write(file_path, arc_path)
                
                # Add backup metadata
                metadata = {
                    'backup_date': datetime.now().isoformat(),
                    'version': '2.0',
                    'system': 'Dairy Farm Management System'
                }
                zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2))
            
            self.logger.info(f"System backup created: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            return False
    
    def restore_system(self, backup_path: str) -> bool:
        """Restore system from backup"""
        try:
            # Create backup of current data first
            current_backup = f"backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            self.backup_system(os.path.join(self.data_dir, 'backups', current_backup))
            
            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.data_dir)
            
            self.logger.info(f"System restored from: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            return False
