# 🏢 Enhanced Dairy Farm Management System - Sage 50 Style

A professional-grade desktop application for comprehensive dairy farm management with Sage 50-style accounting and financial management capabilities. Perfect for small to large-scale dairy operations requiring professional financial visibility and operational control.

## ✨ Key Features

### 💰 **Financial Management (Sage 50 Style)**
- **General Ledger**: Complete chart of accounts with automated posting
- **Accounts Receivable**: Customer invoicing and payment tracking
- **Accounts Payable**: Supplier bills and payment management
- **Financial Statements**: Professional P&L, Balance Sheet, Cash Flow reports
- **Real-time KPIs**: Financial dashboards with live updates
- **Multi-format Export**: PDF, Excel, CSV report generation

### 🐄 **Enhanced Herd Management**
- **Unique Coding System**: COW-YYMM-XXXX format for all cattle
- **Complete Profiles**: Individual records with photos and parentage
- **Breeding Cycles**: Track breeding history and offspring
- **Body Condition Scoring**: Visual health indicators (1-5 scale)
- **Advanced Search**: Filter by breed, age, status, and more

### 👥 **Workers & Payroll**
- **Employee Management**: Complete worker profiles with unique codes
- **Attendance Tracking**: Daily attendance and work hours
- **Payroll System**: Automated salary calculations
- **Salary Slips**: Professional PDF payslip generation
- **Performance Tracking**: Worker productivity metrics

### 🥛 **Milk Production & Billing**
- **Daily Production**: Track yield by cow and quality grade
- **Quality Bonuses**: Grade A (Rs 13.30), Grade B (Rs 6.65), Grade C (base rate)
- **Customer Management**: Unique customer codes and profiles
- **Automated Billing**: Invoice generation with quality premiums
- **Payment Tracking**: Monitor receivables and collections

### 🌾 **Feed & Nutrition Management**
- **Inventory Control**: Real-time stock levels with supplier codes
- **Cost Analysis**: Track feed expenses and efficiency
- **Reorder Alerts**: Automated low-stock notifications
- **Supplier Management**: Complete vendor database
- **Usage Tracking**: Monitor consumption patterns

### 📊 **Professional Reporting Engine**
- **Financial Reports**: Profit & Loss, Balance Sheet, Cash Flow (PDF/Excel/CSV)
- **Comprehensive Farm Reports**: Multi-page PDF with all farm data
- **Entity Exports**: Export cattle, workers, milk, feed data
- **Custom Date Ranges**: Filter reports by any time period
- **Professional Formatting**: Publication-ready documents

### 🔍 **Advanced Search & Filtering**
- **Global Search**: Find any entity by code, name, or description
- **Date Range Filters**: Query data by custom periods
- **Multi-criteria Filters**: Combine multiple search parameters
- **Real-time Results**: Instant search as you type

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python enhanced_main.py
```

### First Time Setup
1. **Launch Application**: Run `python enhanced_main.py`
2. **Data Initialization**: System creates default chart of accounts automatically
3. **Backup Location**: All data stored in `data/` folder with automatic backups
4. **Start Using**: Begin adding cattle, workers, and recording transactions

## 📁 System Architecture

### Core Modules
- `enhanced_main.py` - Main application with dashboard
- `enhanced_data_manager.py` - Sage 50-style data management with unique codes
- `financial_management.py` - Complete accounting system (GL, A/R, A/P)
- `enhanced_herd_management.py` - Advanced cattle management
- `workers_payroll_management.py` - Workforce and payroll system
- `enhanced_reporting_engine.py` - Professional PDF/Excel/CSV reports
- `milk_management.py` - Production tracking and billing
- `feed_management.py` - Inventory and supplier management

### Data Storage
```
data/
├── cattle.json              # Herd records with unique codes
├── workers.json             # Employee database
├── invoices.json            # Customer invoices (A/R)
├── expenses.json            # Expense records
├── chart_of_accounts.json   # Financial accounts
├── milk.json                # Production and delivery data
├── feed_inventory.json      # Feed stock levels
├── sequences.json           # Auto-increment counters
└── backups/                 # Automated ZIP backups
```

## 💡 Unique Features

### Sage 50-Style Coding System
- **Cattle**: COW-2412-0001, COW-2412-0002...
- **Customers**: CUST-2412-0001, CUST-2412-0002...
- **Workers**: WORK-2412-0001, WORK-2412-0002...
- **Invoices**: INV-2412-0001, INV-2412-0002...
- **Accounts**: ACC-1000-0001, ACC-2000-0001...

### Professional Financial Statements
All financial statements use **live data** from your transactions:
- **Profit & Loss**: Revenue and expenses by account with net income
- **Balance Sheet**: Assets, liabilities, and equity with proper categorization
- **Cash Flow**: Operating, investing, and financing activities

### Backup & Restore
- **Automated Backups**: ZIP compression with metadata
- **One-Click Restore**: Complete system recovery
- **Data Integrity**: Backup before restore with rollback capability

## 🎯 Target Users

- **Small to Medium Dairy Farms**: 10-500 cattle operations
- **Commercial Dairy Operations**: Professional financial management needs
- **Farm Managers**: Requiring detailed operational and financial reports
- **Agricultural Consultants**: Multi-farm management capabilities
- **Accounting Professionals**: Sage 50-style financial integration

## 📋 System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, Linux
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Display**: 1400x900 minimum resolution for optimal experience

## 🆕 Version Information

**Current Version**: 2.0 (Enhanced - Sage 50 Style)  
**Release Date**: December 2024  
**Compatibility**: Windows 10/11, macOS 10.14+, Linux  
**Currency**: Nepali Rupees (Rs) - No conversion  
**Status**: ✅ Production Ready for Organizational Use
