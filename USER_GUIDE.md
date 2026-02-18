# 🐄 Cattle Farm Management System - User Guide

## Table of Contents
1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Main Features](#main-features)
4. [Module Guides](#module-guides)
5. [Data Management](#data-management)
6. [Troubleshooting](#troubleshooting)
7. [Support](#support)

---

## Installation

### System Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.7 or higher
- **RAM**: Minimum 4GB recommended
- **Storage**: 500MB free space
- **Display**: 1024x768 minimum resolution

### Quick Installation
1. **Download** the application files to a folder
2. **Run Setup**: Double-click `setup.py` or run `python setup.py`
3. **Launch**: Use `app_launcher.py` or run `python main.py`

### Manual Installation
```bash
# Install required packages
pip install PyQt5>=5.15.0 matplotlib>=3.5.0 reportlab>=3.6.0 Pillow>=8.0.0

# Run the application
python main.py
```

---

## Getting Started

### First Launch
1. **Start the Application**
   - Use the desktop shortcut (if created)
   - Or run `python app_launcher.py`
   - Or directly run `python main.py`

2. **Initial Setup**
   - The application creates a `data` folder automatically
   - All your farm data is stored locally
   - No internet connection required

3. **Navigation**
   - Use the tabs at the top to switch between modules
   - Dashboard shows overview of your farm operations
   - Each module has its own set of features

---

## Main Features

### 📊 Dashboard
- **Real-time Statistics**: View key metrics at a glance
- **Quick Alerts**: See important notifications
- **Charts & Graphs**: Visual representation of farm data
- **KPI Cards**: Track performance indicators

### 🐄 Cow Management
- **Individual Profiles**: Detailed records for each animal
- **Photo Support**: Add pictures to cow profiles
- **Breeding Records**: Track parentage and breeding history
- **Body Condition Scoring**: Monitor animal health (1-5 scale)

### 🏥 Health Management
- **Health Records**: Track treatments and medications
- **Vaccination Schedules**: Automated reminders
- **Treatment History**: Complete medical records
- **Veterinarian Contacts**: Manage vet information

### 🥛 Milk Management
- **Production Tracking**: Daily milk production records
- **Quality Grading**: A, B, C grade system with bonuses
- **Delivery Management**: Track sales and payments
- **Revenue Calculation**: Automatic pricing with quality bonuses

### 🌾 Feed Management
- **Inventory Tracking**: Monitor feed stock levels
- **Supplier Management**: Track feed suppliers and contacts
- **Cost Analysis**: Monitor feed expenses
- **Low Stock Alerts**: Automatic reorder notifications

### 💰 Expense Management
- **Expense Tracking**: Record all farm expenses
- **Category Management**: Organize expenses by type
- **Worker Management**: Track employee information
- **Payroll System**: Manage salary payments

### 📋 Reports & Billing
- **Financial Reports**: Income, expenses, and profit analysis
- **Production Reports**: Milk production summaries
- **Health Reports**: Animal health statistics
- **PDF Generation**: Professional invoices and reports

---

## Module Guides

### Cow Management Module

#### Adding a New Cow
1. Click **"Add Cow"** button
2. Fill in required information:
   - **Tag ID**: Unique identifier
   - **Name**: Cow's name
   - **Breed**: Select or enter breed
   - **Birth Date**: Date of birth
   - **Sire/Dam**: Parent information (optional)
3. Add photo if available
4. Set body condition score (1-5)
5. Click **"Save"**

#### Managing Cow Records
- **Edit**: Double-click any cow in the table
- **Delete**: Select cow and click "Delete"
- **Search**: Use the search box to find specific cows
- **Photos**: Click "Add Photo" to upload images

### Health Management Module

#### Recording Health Events
1. Click **"Add Health Record"**
2. Select the cow from dropdown
3. Choose record type:
   - **Vaccination**: Preventive care
   - **Treatment**: Medical treatment
   - **Checkup**: Routine examination
4. Fill in details and save

#### Vaccination Reminders
- System automatically calculates due dates
- Overdue vaccinations show in red
- Click "Mark as Done" when completed
- Set custom reminder intervals

### Milk Management Module

#### Recording Production
1. Click **"Add Production"**
2. Select cow and enter quantity
3. Choose quality grade (A, B, or C)
4. System calculates bonus automatically:
   - **Grade A**: Rs 13.30 bonus per liter
   - **Grade B**: Rs 6.65 bonus per liter
   - **Grade C**: No bonus

#### Managing Deliveries
1. Click **"Add Delivery"**
2. Enter buyer information
3. Specify quantity and rate
4. Track payment status
5. Generate invoices as needed

### Feed Management Module

#### Adding Feed Items
1. Click **"Add Feed Item"**
2. Enter feed details:
   - **Type**: Hay, Grain, Pellets, etc.
   - **Quantity**: Amount in stock
   - **Unit Cost**: Price per unit
   - **Supplier**: Vendor information
3. Set low stock threshold
4. Save the record

#### Inventory Monitoring
- **Green Status**: Adequate stock
- **Red Status**: Low stock (below threshold)
- **Automatic Alerts**: System notifies when reorder needed
- **Cost Tracking**: Monitor total inventory value

### Expense Management Module

#### Recording Expenses
1. Click **"Add Expense"**
2. Select category (Feed, Veterinary, Equipment, etc.)
3. Enter amount in Nepali Rupees (Rs)
4. Add description and vendor information
5. Choose payment method
6. Save the record

#### Worker Management
1. Go to **"Workers"** tab
2. Click **"Add Worker"**
3. Enter employee details and salary
4. Track hire dates and contact information
5. Record salary payments in **"Salaries"** tab

---

## Data Management

### Data Storage
- All data stored in `data` folder as JSON files
- **Automatic Backups**: System creates periodic backups
- **Data Security**: All data remains on your computer
- **No Cloud Dependency**: Works completely offline

### Backup & Restore
```
data/
├── cows.json          # Cow records
├── health.json        # Health records
├── milk.json          # Production & delivery data
├── feed.json          # Feed inventory
├── expenses.json      # Expense records
├── alerts.json        # System alerts
└── backups/           # Automatic backups
```

### Data Export
- **CSV Export**: Export data to spreadsheets
- **PDF Reports**: Generate professional reports
- **Backup Creation**: Manual backup functionality
- **Data Import**: Import existing data (JSON format)

---

## Troubleshooting

### Common Issues

#### Application Won't Start
1. **Check Python Version**: Ensure Python 3.7+ is installed
2. **Run Setup**: Execute `python setup.py`
3. **Check Dependencies**: Verify all packages are installed
4. **Restart as Administrator**: Try running with elevated privileges

#### Missing Data
1. **Check Data Folder**: Ensure `data` folder exists
2. **File Permissions**: Verify read/write access
3. **Restore Backup**: Use backup files if available
4. **Recreate Files**: Delete and restart application

#### Performance Issues
1. **Close Other Applications**: Free up system memory
2. **Reduce Data Size**: Archive old records
3. **Update Graphics Drivers**: For chart display issues
4. **Restart Application**: Close and reopen the program

#### Display Problems
1. **Screen Resolution**: Ensure minimum 1024x768
2. **DPI Settings**: Check Windows display scaling
3. **Graphics Drivers**: Update to latest version
4. **Font Issues**: Install required system fonts

### Error Messages

| Error | Solution |
|-------|----------|
| "Module not found" | Run `python setup.py` to install dependencies |
| "Permission denied" | Run as administrator or check file permissions |
| "Data file corrupted" | Restore from backup in `data/backups/` folder |
| "Memory error" | Close other applications and restart |

---

## Support

### Getting Help
1. **Check This Guide**: Most issues covered here
2. **Error Messages**: Note exact error text for troubleshooting
3. **System Information**: Note your OS and Python version
4. **Data Backup**: Always backup data before major changes

### Best Practices
- **Regular Backups**: Export data weekly
- **Data Entry**: Enter information consistently
- **System Updates**: Keep Python and packages updated
- **File Organization**: Don't move application files

### Advanced Features
- **Custom Reports**: Modify report templates
- **Data Integration**: Import from other farm software
- **Multi-User Setup**: Share data folder on network
- **Automation**: Schedule automatic backups

---

## Quick Reference

### Keyboard Shortcuts
- **Ctrl+N**: New record (context-dependent)
- **Ctrl+S**: Save current form
- **Ctrl+F**: Search/Find
- **F5**: Refresh current view
- **Ctrl+P**: Print/Generate PDF

### Currency Format
- All monetary values in **Nepali Rupees (Rs)**
- Format: Rs 1,234.56
- No automatic currency conversion

### Date Format
- Standard format: YYYY-MM-DD
- Calendar picker available for date selection
- Automatic date validation

---

**🎉 Congratulations!** You're now ready to manage your cattle farm efficiently with this comprehensive system. For additional support or feature requests, refer to the application's built-in help system.

---
*Cattle Farm Management System v1.0 - September 2025 - Production Ready*
