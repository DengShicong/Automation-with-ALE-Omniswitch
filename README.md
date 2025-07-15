# ALE Network Device Inspection System

## 🎯 Overview

This is an automated network device inspection system specifically designed for **ALE (Alcatel-Lucent Enterprise)** network devices. The system provides comprehensive device health monitoring, configuration backup, and automated reporting capabilities.

### 🔧 What This Program Does

The ALE Network Device Inspection System automates the following tasks:

1. **Device Connectivity Testing** - Automatically connects to multiple ALE devices via SSH
2. **Tech-Support Execution** - Runs `show tech-support` command on ALE devices
3. **Log File Collection** - Downloads critical log files from device root directory:
   - `tech_support_layer3.log`
   - `tech_support_layer2.log`
   - `tech_support.log`
4. **Configuration Backup** - Executes predefined CLI commands to collect device configurations
5. **Data Organization** - Organizes collected data with device IP prefixes and timestamps
6. **Result Compression** - Automatically compresses all inspection results into ZIP files
7. **Email Notifications** - Sends automated email reports with inspection results as attachments

### 🎯 Purpose & Benefits

- **Automated Network Auditing**: Eliminate manual device inspection tasks
- **Centralized Log Collection**: Gather critical system logs from multiple devices
- **Scheduled Health Checks**: Regular monitoring of network infrastructure
- **Compliance Reporting**: Generate comprehensive reports for network compliance
- **Troubleshooting Support**: Collect diagnostic information for technical support
- **Time Efficiency**: Reduce hours of manual work to minutes of automated execution

### 📸 System Demonstration

![ALE Inspection System](IMG/image.png)

*The system interface showing automated inspection process and results*

### 🔄 Workflow Overview

```
Excel Configuration → Device Connection → Tech-Support Execution → Log Download → Result Compression → Email Report
       ↓                    ↓                     ↓                    ↓                ↓               ↓
   template.xlsx      SSH to devices      show tech-support      TFTP/SCP files    ZIP creation    SMTP delivery
```

**Typical Execution Flow:**
1. 📋 Read device list from Excel
2. 🔌 Establish SSH connections
3. ⚡ Execute tech-support commands
4. 📥 Download log files via TFTP/SCP
5. 📝 Run additional CLI commands
6. 🗜️ Compress all results
7. 📧 Email compressed results to administrators

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Device List
```
1. Open template.xlsx
2. Fill in device information
3. Save the file
```

### Step 3: Configure Email Settings (Optional)
```
1. Edit .env file
2. Set SMTP server and credentials
3. Configure sender/receiver emails
```

### Step 4: Run Inspection Program
```bash
python ale_inspection.py
```

## 📋 Prerequisites

### ⚠️ Important: Configure Device List First
Before running the inspection program, **you must configure the device list in the Excel file**:

1. **Open Configuration File**: `template.xlsx`
2. **Configure Device Information**: Fill in device details in the "Device Information" worksheet
3. **Check Command Configuration**: Verify the command worksheet for corresponding device types
4. **Save File**: Ensure the configuration is saved

## 📋 Inspection Process

1. **Read Excel Device List** - Load device configuration from template.xlsx
2. **ALE Device Special Processing** - Execute `show tech-support` command
3. **TFTP File Transfer** - Download three log files from root directory
4. **File Naming Convention** - Save log files with device IP prefix
5. **Post-processing** - Compress LOG folder and send email

## 📁 Core Files

```
├── ale_inspection.py          # Main program (interactive startup)
├── connect.py                 # Device connection module
├── send_email.py              # Email sending module
├── zip_file.py                # File compression module
├── env_loader.py              # Environment variable loader
├── tftp_downloader.py         # TFTP download tool
├── template.xlsx              # Device configuration file
├── .env                       # Email configuration file
└── LOG/                       # Inspection results directory
```

## ⚙️ Excel Configuration

Configure device information in `template.xlsx`:

| No. | Status | Device IP | Protocol | Port | Username | Password | Enable Password | Device Type |
|-----|--------|-----------|----------|------|----------|----------|-----------------|-------------|
| 1 | Enable | 10.10.10.226 | ssh | 22 | admin | switch | | alcatel_aos |

**Important Notes:**
- Use `alcatel_aos` for ALE device type
- Fill `#` in Status column to skip the device

## 📧 Email Configuration

Email parameters are configured in `.env` file:
- Sender: (configure in .env)
- Receiver: (configure in .env)
- SMTP Server: (configure in .env)

## 🔧 Usage

### Interactive Mode
```bash
python ale_inspection.py
```
The program will automatically:
1. Read Excel configuration
2. Connect to ALE devices
3. Execute tech-support command
4. Attempt to download log files
5. Execute other inspection commands
6. Compress result files
7. Send email notification

## 📊 Output Results

```
LOG/
├── 10.10.10.226_2025-07-15_20-49-28/
│   ├── 10.10.10.226_show_system.txt
│   ├── 10.10.10.226_show_health.txt
│   ├── 10.10.10.226_tech_support.log
│   └── ...
└── inspection_results_20250715_204928.zip
```

## ⚠️ Important Notes

1. **TFTP Download**: If TFTP download fails, the program will create record files
2. **Network Connection**: Ensure SSH connection to ALE devices is available
3. **Email Sending**: Email configuration completed, will send results automatically

## 🆘 Troubleshooting

### Connection Failed
- Check device IP and authentication information
- Verify network connectivity

### File Download Failed
- Check device TFTP/SCP service
- Verify file permissions

### Email Sending Failed
- Check email configuration in .env file
- Verify network connection

## 🛠️ Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Dependencies
- netmiko>=4.0.0
- paramiko>=2.7.0
- openpyxl>=3.0.0
- pandas>=1.3.0

## 📚 Documentation

- [中文文档](README_CN.md) - Chinese Documentation
- [English Documentation](README.md) - This file

## 🔧 Features

- ✅ **Multi-vendor Support**: Supports ALE/Alcatel-Lucent devices
- ✅ **Excel Configuration**: Easy device management through Excel templates
- ✅ **Tech-support Processing**: Automatic execution and log file download
- ✅ **Email Notifications**: Automatic email sending with results
- ✅ **File Compression**: Automatic compression of inspection results
- ✅ **Error Handling**: Comprehensive error handling and logging

## 📝 License

This project is licensed under the MIT License.

---

**Quick Start**: Configure `template.xlsx` first, then run `python ale_inspection.py`!
