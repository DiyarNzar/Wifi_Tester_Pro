#!/bin/bash

#######################################
# WiFi Tester Pro - Driver Installer
# Installs required drivers and tools
#######################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║     WiFi Tester Pro - Driver Installer    ║"
echo "║              Version 6.0                  ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Please run as root (use sudo)${NC}"
    echo "Usage: sudo ./install-driver.sh"
    exit 1
fi

# Detect distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        echo -e "${GREEN}[INFO] Detected distribution: $DISTRO${NC}"
    else
        DISTRO="unknown"
        echo -e "${YELLOW}[WARN] Could not detect distribution${NC}"
    fi
}

# Update package lists
update_packages() {
    echo -e "${BLUE}[*] Updating package lists...${NC}"
    apt update -y
}

# Install basic network tools
install_basic_tools() {
    echo -e "${BLUE}[*] Installing basic network tools...${NC}"
    apt install -y \
        iw \
        wireless-tools \
        net-tools \
        network-manager \
        wpasupplicant \
        rfkill
}

# Install aircrack-ng suite (for Kali/security testing)
install_aircrack() {
    echo -e "${BLUE}[*] Installing aircrack-ng suite...${NC}"
    apt install -y aircrack-ng
}

# Install Python dependencies
install_python_deps() {
    echo -e "${BLUE}[*] Installing Python dependencies...${NC}"
    apt install -y \
        python3 \
        python3-pip \
        python3-tk \
        python3-dev
}

# Install common WiFi adapter drivers
install_wifi_drivers() {
    echo -e "${BLUE}[*] Installing WiFi adapter drivers...${NC}"
    
    # Install firmware and drivers
    apt install -y \
        firmware-linux \
        firmware-linux-nonfree \
        firmware-atheros \
        firmware-realtek \
        firmware-iwlwifi \
        firmware-brcm80211 \
        2>/dev/null || true
    
    # Install DKMS for driver compilation
    apt install -y dkms build-essential linux-headers-$(uname -r) 2>/dev/null || true
}

# Install Realtek RTL8812AU driver (common for monitor mode)
install_rtl8812au() {
    echo -e "${BLUE}[*] Installing RTL8812AU driver (common USB adapter)...${NC}"
    
    # Check if already installed
    if modinfo 88XXau &>/dev/null || modinfo rtl8812au &>/dev/null; then
        echo -e "${GREEN}[✓] RTL8812AU driver already installed${NC}"
        return
    fi
    
    # Try to install from repository first
    if apt install -y realtek-rtl88xxau-dkms 2>/dev/null; then
        echo -e "${GREEN}[✓] RTL8812AU driver installed from repository${NC}"
        return
    fi
    
    # Otherwise, build from source
    echo -e "${YELLOW}[*] Building RTL8812AU from source...${NC}"
    
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    if command -v git &>/dev/null; then
        git clone https://github.com/aircrack-ng/rtl8812au.git
        cd rtl8812au
        make && make install
        echo -e "${GREEN}[✓] RTL8812AU driver built and installed${NC}"
    else
        echo -e "${YELLOW}[WARN] Git not found, skipping source build${NC}"
        apt install -y git
    fi
    
    cd /
    rm -rf "$TEMP_DIR"
}

# Install additional security tools for Kali
install_security_tools() {
    echo -e "${BLUE}[*] Installing security tools...${NC}"
    
    apt install -y \
        reaver \
        pixiewps \
        bully \
        wifite \
        hcxtools \
        hcxdumptool \
        hashcat \
        2>/dev/null || true
}

# Configure NetworkManager for monitor mode
configure_nm() {
    echo -e "${BLUE}[*] Configuring NetworkManager...${NC}"
    
    # Create unmanaged devices config for monitor interfaces
    mkdir -p /etc/NetworkManager/conf.d/
    cat > /etc/NetworkManager/conf.d/wifi-tester.conf << 'EOF'
[keyfile]
unmanaged-devices=interface-name:wlan*mon;interface-name:mon*
EOF
    
    # Restart NetworkManager
    systemctl restart NetworkManager 2>/dev/null || true
    echo -e "${GREEN}[✓] NetworkManager configured${NC}"
}

# Install Python packages from requirements.txt
install_pip_packages() {
    echo -e "${BLUE}[*] Installing Python packages...${NC}"
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        pip3 install -r "$SCRIPT_DIR/requirements.txt" --break-system-packages 2>/dev/null || \
        pip3 install -r "$SCRIPT_DIR/requirements.txt"
        echo -e "${GREEN}[✓] Python packages installed${NC}"
    else
        echo -e "${YELLOW}[WARN] requirements.txt not found${NC}"
    fi
}

# Main installation
main() {
    detect_distro
    
    echo ""
    echo -e "${YELLOW}This script will install:${NC}"
    echo "  • Basic network tools (iw, wireless-tools, etc.)"
    echo "  • Aircrack-ng suite"
    echo "  • WiFi adapter drivers/firmware"
    echo "  • Python dependencies"
    echo "  • Security tools (on Kali)"
    echo ""
    
    read -p "Continue with installation? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
        echo -e "${YELLOW}Installation cancelled${NC}"
        exit 0
    fi
    
    update_packages
    install_basic_tools
    install_python_deps
    install_aircrack
    install_wifi_drivers
    
    # Install RTL8812AU driver (popular for pen testing)
    read -p "Install RTL8812AU USB adapter driver? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_rtl8812au
    fi
    
    # Install extra security tools on Kali
    if [ "$DISTRO" = "kali" ]; then
        echo -e "${BLUE}[*] Kali Linux detected - installing extra security tools${NC}"
        install_security_tools
    fi
    
    configure_nm
    install_pip_packages
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║      Installation Complete! ✓             ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}To run WiFi Tester Pro:${NC}"
    echo "  sudo python3 main.py"
    echo ""
    echo -e "${YELLOW}Note: A reboot may be required for driver changes${NC}"
}

# Run main function
main "$@"
