# WiFi Tester Pro v6.0 🛡️

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-orange.svg)](https://github.com/yourusername/wifi-tester-pro)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Professional WiFi Network Security Auditor** - A cross-platform tool for network analysis, security assessment, and penetration testing.

<div align="center">
  <img src="assets/screenshot.png" alt="WiFi Tester Pro Screenshot" width="800"/>
</div>

## ✨ Features

### 🌐 Cross-Platform Support
- **Windows** - Network scanning, signal monitoring, security analysis
- **Linux (Kali)** - Full penetration testing suite with monitor mode support

### 📊 Network Analysis
- 📡 Real-time WiFi network discovery
- 📈 Live signal strength monitoring with graphs
- 🖥️ Connected device enumeration
- 🏥 Network health diagnostics
- 📊 Channel utilization analysis

### 🔒 Security Assessment
- 🔐 WPA/WPA2/WPA3 protocol analysis
- 🚨 Weak password detection
- 🔑 Encryption strength evaluation
- ✅ Security recommendations
- 📋 Compliance reporting

### 💀 Advanced Features (Kali Linux)
- 🎯 Monitor mode management (airmon-ng)
- 💉 Packet injection testing
- 🔌 Deauthentication attacks
- 📦 Deep packet analysis
- 🕵️ WPS vulnerability scanning

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.10 or higher
python --version

# pip package manager
pip --version
```

### Installation

#### Windows
```bash
# Clone the repository
git clone https://github.com/DiyarNzar/Wifi_tester_pro.git
cd wifi-tester-pro

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

#### Kali Linux
```bash
# Clone the repository
git clone https://github.com/yourusername/wifi-tester-pro.git
cd wifi-tester-pro

# Install system dependencies
sudo apt update
sudo apt install -y aircrack-ng network-manager

# Install Python dependencies
pip install -r requirements.txt

# Run with root privileges (required for monitor mode)
sudo python main.py
```

## 📖 Usage Guide

### Basic Network Scanning
1. Launch the application: `python main.py`
2. Navigate to the **Scanner** tab
3. Click "Scan Networks" to discover nearby WiFi
4. Select a network to view detailed information

### Security Auditing (Windows/Linux)
1. Go to the **Auditor** tab
2. Select a target network from the list
3. Run security analysis to identify vulnerabilities
4. Review recommendations in the report

### Advanced Testing (Kali Linux Only)
1. Launch with root: `sudo python main.py`
2. Navigate to **Auditor** → **Advanced Tools**
3. Enable Monitor Mode on your wireless adapter
4. Use penetration testing features responsibly

## 🏗️ Architecture

### Design Patterns
- **Factory Pattern** - OS-specific driver loading
- **Strategy Pattern** - Cross-platform abstraction
- **Observer Pattern** - Real-time GUI updates
- **Thread Pool** - Non-blocking operations

### Project Structure
```
wifi_tester_pro/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
├── .gitignore             # Git exclusions
├── assets/                # Resources
│   ├── app_icon.ico       # Windows icon
│   ├── app_icon.png       # Linux icon
│   └── theme.json         # UI theme
└── src/
    ├── settings.py         # Configuration
    ├── app_factory.py      # OS detection & loading
    ├── core/               # Business logic
    │   ├── engine.py       # Threading engine
    │   ├── session.py      # State management
    │   └── logger.py       # Logging system
    ├── drivers/            # OS abstraction
    │   ├── abstract.py     # Base interface
    │   ├── win_driver.py   # Windows impl
    │   └── lin_driver.py   # Linux impl
    ├── security/           # Security modules
    │   ├── common.py       # Cross-platform
    │   └── kali/           # Linux-specific
    │       ├── adapter_mgr.py
    │       ├── injector.py
    │       └── deauther.py
    └── gui/                # User interface
        ├── main_window.py  # Main window
        ├── navigation.py   # Tab navigation
        ├── tabs/
        │   ├── dashboard.py
        │   ├── scanner.py
        │   └── auditor.py
        └── widgets/
            ├── terminal.py
            └── signal_card.py
```

## 🛠️ Development

### Setting Up Development Environment
```bash
# Clone the repository
git clone https://github.com/yourusername/wifi-tester-pro.git
cd wifi-tester-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

### Running Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Coverage report
pytest --cov=src tests/
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## ⚠️ Legal Disclaimer

**IMPORTANT**: This tool is designed for legitimate purposes only:

✅ **Authorized Use:**
- Testing networks you own
- Authorized penetration testing with written permission
- Educational purposes in controlled environments
- Security research with proper authorization

❌ **Prohibited Use:**
- Unauthorized access to networks
- Disrupting network services without permission
- Any illegal activities

**You are responsible for compliance with all applicable laws.** Unauthorized access to computer networks is illegal in most jurisdictions. The developers assume no liability for misuse of this software.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **aircrack-ng** - Wireless security auditing tools
- **CustomTkinter** - Modern UI framework
- **Scapy** - Packet manipulation library
- The open-source security community

## 📞 Support

- 🐛 **Bug Reports**: [Open an issue](https://github.com/yourusername/wifi-tester-pro/issues)
- 💡 **Feature Requests**: [Start a discussion](https://github.com/yourusername/wifi-tester-pro/discussions)
- 📧 **Contact**: your.email@example.com

## 🗺️ Roadmap

- [ ] Web-based dashboard
- [ ] Export reports to PDF/CSV
- [ ] WPA3 vulnerability scanning
- [ ] Multi-adapter support
- [ ] Plugin system for extensions
- [ ] Mobile app companion

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/wifi-tester-pro&type=Date)](https://star-history.com/#yourusername/wifi-tester-pro&Date)

---

<div align="center">
  <strong>WiFi Tester Pro v6.0</strong> - Built with ❤️ for the security community
  <br>
  <sub>If you find this tool useful, please consider giving it a ⭐</sub>
</div>