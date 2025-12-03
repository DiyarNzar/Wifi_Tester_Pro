"""
WiFi Tester Pro v6.0 - Linux WiFi Driver
Linux-specific WiFi implementation using iw, iwconfig, and optional Scapy
"""

import subprocess
import re
import os
import time
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from .abstract import WiFiDriverBase, InterfaceInfo, DriverCapability
from ..settings import NetworkInfo, IS_LINUX, IS_KALI


class LinuxWiFiDriver(WiFiDriverBase):
    """
    Linux WiFi driver implementation.
    Uses iw/iwconfig commands, with enhanced features on Kali Linux.
    """
    
    def __init__(self):
        super().__init__()
        self._original_mode: Dict[str, str] = {}  # Store original modes for cleanup
        self._monitor_interface: Optional[str] = None
        
        # Set capabilities based on platform
        self._capabilities = {DriverCapability.SCAN}
        
        if IS_KALI:
            self._capabilities.update({
                DriverCapability.MONITOR_MODE,
                DriverCapability.CHANNEL_HOP,
            })
            # Check for injection support separately
            self._check_injection_support()
    
    def _check_injection_support(self):
        """Check if packet injection is supported"""
        try:
            # Check for aircrack-ng suite
            result = subprocess.run(
                ["which", "aireplay-ng"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self._capabilities.add(DriverCapability.PACKET_INJECTION)
                self._capabilities.add(DriverCapability.DEAUTH)
        except:
            pass
    
    def initialize(self) -> bool:
        """Initialize Linux WiFi driver"""
        if not IS_LINUX:
            print("[LinuxDriver] Not running on Linux")
            return False
        
        try:
            # Check for required tools
            tools_available = True
            
            for tool in ["iw", "ip"]:
                result = subprocess.run(
                    ["which", tool],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"[LinuxDriver] Missing tool: {tool}")
                    tools_available = False
            
            if not tools_available:
                print("[LinuxDriver] Some tools missing, limited functionality")
            
            # Check for root/sudo
            if os.geteuid() != 0:
                print("[LinuxDriver] Warning: Not running as root, some features disabled")
            
            self._is_initialized = True
            self.get_interfaces()
            print(f"[LinuxDriver] Initialized {'(Kali mode)' if IS_KALI else ''}")
            return True
            
        except Exception as e:
            print(f"[LinuxDriver] Initialization error: {e}")
            return False
    
    def get_interfaces(self) -> List[InterfaceInfo]:
        """Get list of WiFi interfaces on Linux"""
        interfaces = []
        
        try:
            # Use iw dev to list wireless interfaces
            result = subprocess.run(
                ["iw", "dev"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # Fallback to /sys/class/net
                return self._get_interfaces_fallback()
            
            output = result.stdout
            current_phy = ""
            current_interface = {}
            
            for line in output.split('\n'):
                line = line.strip()
                
                if line.startswith('phy#'):
                    current_phy = line
                
                elif line.startswith('Interface'):
                    # Save previous interface
                    if current_interface.get('name'):
                        interfaces.append(self._create_interface_info(current_interface))
                    current_interface = {'name': line.split()[1], 'phy': current_phy}
                
                elif line.startswith('addr'):
                    current_interface['mac'] = line.split()[1]
                
                elif line.startswith('type'):
                    current_interface['mode'] = line.split()[1]
                
                elif line.startswith('channel'):
                    try:
                        parts = line.split()
                        current_interface['channel'] = int(parts[1])
                        # Extract frequency if available
                        for part in parts:
                            if 'MHz' in part or part.replace('.', '').isdigit():
                                freq_match = re.search(r'(\d+)', part)
                                if freq_match:
                                    current_interface['frequency'] = float(freq_match.group(1))
                    except:
                        pass
                
                elif line.startswith('txpower'):
                    try:
                        current_interface['txpower'] = int(float(line.split()[1]))
                    except:
                        pass
            
            # Save last interface
            if current_interface.get('name'):
                interfaces.append(self._create_interface_info(current_interface))
            
            # Update internal cache
            for iface in interfaces:
                self._interfaces[iface.name] = iface
            
            # Select first interface if none selected
            if interfaces and not self._current_interface:
                self._current_interface = interfaces[0].name
            
        except Exception as e:
            print(f"[LinuxDriver] Error getting interfaces: {e}")
        
        return interfaces
    
    def _get_interfaces_fallback(self) -> List[InterfaceInfo]:
        """Fallback method using /sys/class/net"""
        interfaces = []
        
        try:
            net_path = "/sys/class/net"
            for iface_name in os.listdir(net_path):
                wireless_path = os.path.join(net_path, iface_name, "wireless")
                if os.path.exists(wireless_path):
                    # Read MAC address
                    mac = "00:00:00:00:00:00"
                    try:
                        with open(os.path.join(net_path, iface_name, "address")) as f:
                            mac = f.read().strip()
                    except:
                        pass
                    
                    info = InterfaceInfo(
                        name=iface_name,
                        mac_address=mac,
                        mode='managed',
                        is_wireless=True,
                        supports_monitor=IS_KALI,
                        supports_injection=IS_KALI,
                    )
                    interfaces.append(info)
                    self._interfaces[iface_name] = info
        except:
            pass
        
        return interfaces
    
    def _create_interface_info(self, data: dict) -> InterfaceInfo:
        """Create InterfaceInfo from parsed data"""
        return InterfaceInfo(
            name=data.get('name', ''),
            mac_address=data.get('mac', '00:00:00:00:00:00'),
            mode=data.get('mode', 'managed'),
            channel=data.get('channel', 0),
            frequency=data.get('frequency', 0.0),
            tx_power=data.get('txpower', 0),
            is_wireless=True,
            supports_monitor=IS_KALI,
            supports_injection=IS_KALI,
        )
    
    def scan_networks(
        self,
        interface: Optional[str] = None,
        timeout: float = 10.0
    ) -> List[NetworkInfo]:
        """Scan for WiFi networks on Linux"""
        networks = []
        iface = interface or self._current_interface
        
        if not iface:
            print("[LinuxDriver] No interface selected")
            return networks
        
        try:
            # Use iw scan
            result = subprocess.run(
                ["sudo", "iw", "dev", iface, "scan"],
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            
            if result.returncode != 0:
                # Try alternative: iwlist
                return self._scan_with_iwlist(iface, timeout)
            
            output = result.stdout
            current_network = {}
            
            for line in output.split('\n'):
                line = line.strip()
                
                if line.startswith('BSS') and '(' in line:
                    # Save previous network
                    if current_network.get('bssid'):
                        networks.append(self._create_network_info(current_network))
                    
                    # Extract BSSID
                    bssid_match = re.search(r'BSS ([0-9a-fA-F:]{17})', line)
                    current_network = {
                        'bssid': bssid_match.group(1) if bssid_match else '',
                        'hidden': False
                    }
                
                elif line.startswith('SSID:'):
                    ssid = line.split(':', 1)[1].strip()
                    current_network['ssid'] = ssid if ssid else '<Hidden>'
                    current_network['hidden'] = not bool(ssid)
                
                elif line.startswith('signal:'):
                    signal_match = re.search(r'(-?\d+\.?\d*)\s*dBm', line)
                    if signal_match:
                        current_network['signal'] = int(float(signal_match.group(1)))
                
                elif line.startswith('freq:'):
                    freq_match = re.search(r'(\d+)', line)
                    if freq_match:
                        freq = int(freq_match.group(1))
                        current_network['frequency'] = freq
                        # Calculate channel from frequency
                        if freq < 3000:
                            current_network['channel'] = (freq - 2407) // 5
                        else:
                            current_network['channel'] = (freq - 5000) // 5
                
                elif 'WPA' in line or 'RSN' in line:
                    if 'WPA2' in line or 'RSN' in line:
                        current_network['security'] = 'WPA2'
                    elif 'WPA' in line:
                        current_network['security'] = 'WPA'
                
                elif 'WEP' in line:
                    current_network['security'] = 'WEP'
                
                elif 'Privacy' in line and 'capability' in line.lower():
                    if 'security' not in current_network:
                        current_network['security'] = 'WEP/Unknown'
                
                elif 'WPS' in line:
                    current_network['wps'] = True
            
            # Save last network
            if current_network.get('bssid'):
                networks.append(self._create_network_info(current_network))
            
            print(f"[LinuxDriver] Scan complete: {len(networks)} networks found")
            
        except subprocess.TimeoutExpired:
            print(f"[LinuxDriver] Scan timeout")
        except Exception as e:
            print(f"[LinuxDriver] Scan error: {e}")
        
        return networks
    
    def _scan_with_iwlist(self, interface: str, timeout: float) -> List[NetworkInfo]:
        """Fallback scan using iwlist"""
        networks = []
        
        try:
            result = subprocess.run(
                ["sudo", "iwlist", interface, "scan"],
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            
            if result.returncode != 0:
                return networks
            
            output = result.stdout
            current_network = {}
            
            for line in output.split('\n'):
                line = line.strip()
                
                if 'Cell' in line and 'Address:' in line:
                    if current_network.get('bssid'):
                        networks.append(self._create_network_info(current_network))
                    
                    bssid_match = re.search(r'([0-9A-Fa-f:]{17})', line)
                    current_network = {
                        'bssid': bssid_match.group(1) if bssid_match else ''
                    }
                
                elif 'ESSID:' in line:
                    ssid_match = re.search(r'ESSID:"([^"]*)"', line)
                    ssid = ssid_match.group(1) if ssid_match else ''
                    current_network['ssid'] = ssid if ssid else '<Hidden>'
                
                elif 'Signal level' in line:
                    signal_match = re.search(r'(-?\d+)\s*dBm', line)
                    if signal_match:
                        current_network['signal'] = int(signal_match.group(1))
                
                elif 'Channel:' in line:
                    channel_match = re.search(r'Channel:(\d+)', line)
                    if channel_match:
                        current_network['channel'] = int(channel_match.group(1))
                
                elif 'Encryption key:' in line:
                    if 'on' in line.lower():
                        current_network.setdefault('security', 'WEP/Unknown')
                    else:
                        current_network['security'] = 'Open'
            
            if current_network.get('bssid'):
                networks.append(self._create_network_info(current_network))
                
        except Exception as e:
            print(f"[LinuxDriver] iwlist scan error: {e}")
        
        return networks
    
    def _create_network_info(self, data: dict) -> NetworkInfo:
        """Create NetworkInfo from parsed data"""
        channel = data.get('channel', 0)
        frequency = data.get('frequency', 0)
        
        if not frequency and channel:
            if channel <= 14:
                frequency = 2412 + (channel - 1) * 5
            else:
                frequency = 5000 + channel * 5
        
        return NetworkInfo(
            ssid=data.get('ssid', '<Hidden>'),
            bssid=data.get('bssid', '00:00:00:00:00:00'),
            signal=data.get('signal', -80),
            channel=channel,
            frequency=frequency,
            security=data.get('security', 'Open'),
            encryption=data.get('encryption', ''),
            hidden=data.get('hidden', False),
            wps=data.get('wps', False),
            first_seen=time.time(),
            last_seen=time.time(),
        )
    
    def get_current_connection(self) -> Optional[NetworkInfo]:
        """Get current WiFi connection info on Linux"""
        # Try nmcli first (more reliable on modern systems)
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "ACTIVE,SSID,BSSID,CHAN,FREQ,SIGNAL,SECURITY", "dev", "wifi"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('yes:'):
                        # Format: yes:SSID:BSSID:CHAN:FREQ:SIGNAL:SECURITY
                        # BSSID has escaped colons like 4E\:7B\:35\:18\:87\:F0
                        # First unescape the line
                        line = line.replace('\\:', '##COLON##')
                        parts = line.split(':')
                        
                        if len(parts) >= 7:
                            # Restore colons in BSSID
                            bssid = parts[2].replace('##COLON##', ':')
                            
                            # Parse frequency (e.g., "2412 MHz" or "5240 MHz")
                            freq_str = parts[4].replace(' MHz', '').replace('##COLON##', ':')
                            try:
                                freq = float(freq_str) if freq_str else 0
                            except:
                                freq = 0
                            
                            # Parse signal (percentage, convert to approximate dBm)
                            try:
                                signal_pct = int(parts[5]) if parts[5] else 50
                                signal_dbm = int((signal_pct / 2) - 100)  # Rough conversion
                            except:
                                signal_dbm = -70
                            
                            # Calculate channel from frequency
                            channel = int(parts[3]) if parts[3].isdigit() else 0
                            
                            connection_data = {
                                'ssid': parts[1].replace('##COLON##', ':') if parts[1] else '<Hidden>',
                                'bssid': bssid,
                                'channel': channel,
                                'frequency': freq,
                                'signal': signal_dbm,
                                'security': parts[6].replace('##COLON##', ':') if len(parts) > 6 else 'Open'
                            }
                            return self._create_network_info(connection_data)
        except Exception as e:
            print(f"[LinuxDriver] nmcli method failed: {e}")
        
        # Fallback to iwconfig
        iface = self._current_interface
        if not iface:
            # Try to find a wireless interface
            interfaces = self.get_interfaces()
            if interfaces:
                iface = interfaces[0].name
            else:
                return None
        
        try:
            result = subprocess.run(
                ["iwconfig", iface],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            output = result.stdout
            connection_data = {}
            
            # Parse iwconfig output
            ssid_match = re.search(r'ESSID:"([^"]*)"', output)
            if ssid_match:
                connection_data['ssid'] = ssid_match.group(1)
            
            ap_match = re.search(r'Access Point:\s*([0-9A-Fa-f:]{17})', output)
            if ap_match:
                connection_data['bssid'] = ap_match.group(1)
            
            freq_match = re.search(r'Frequency[:\s]*(\d+\.?\d*)\s*(GHz|MHz)', output)
            if freq_match:
                freq = float(freq_match.group(1))
                if freq_match.group(2) == 'GHz':
                    freq *= 1000
                connection_data['frequency'] = freq
            
            signal_match = re.search(r'Signal level[=:]\s*(-?\d+)\s*dBm', output)
            if signal_match:
                connection_data['signal'] = int(signal_match.group(1))
            
            # Only return if connected (has BSSID)
            if connection_data.get('bssid') and connection_data['bssid'] != 'Not-Associated':
                return self._create_network_info(connection_data)
            
        except Exception as e:
            print(f"[LinuxDriver] Error getting connection: {e}")
        
        return None
    
    # ==========================================================================
    # Monitor Mode (Kali Linux only)
    # ==========================================================================
    
    def enable_monitor_mode(self, interface: Optional[str] = None) -> Tuple[bool, str]:
        """Enable monitor mode on interface"""
        if DriverCapability.MONITOR_MODE not in self._capabilities:
            return False, "Monitor mode not supported"
        
        iface = interface or self._current_interface
        if not iface:
            return False, "No interface selected"
        
        try:
            # Save original mode
            self._original_mode[iface] = self._interfaces.get(iface, InterfaceInfo(iface, "")).mode
            
            # Method 1: Try airmon-ng (Kali)
            result = subprocess.run(
                ["sudo", "airmon-ng", "start", iface],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Find new monitor interface name
                new_iface = f"{iface}mon"
                self._monitor_interface = new_iface
                self._current_interface = new_iface
                
                # Refresh interfaces
                self.get_interfaces()
                
                print(f"[LinuxDriver] Monitor mode enabled: {new_iface}")
                return True, new_iface
            
            # Method 2: Manual using iw
            subprocess.run(["sudo", "ip", "link", "set", iface, "down"], timeout=10)
            subprocess.run(["sudo", "iw", iface, "set", "type", "monitor"], timeout=10)
            subprocess.run(["sudo", "ip", "link", "set", iface, "up"], timeout=10)
            
            self._monitor_interface = iface
            print(f"[LinuxDriver] Monitor mode enabled: {iface}")
            return True, iface
            
        except Exception as e:
            return False, str(e)
    
    def disable_monitor_mode(self, interface: Optional[str] = None) -> Tuple[bool, str]:
        """Disable monitor mode and return to managed mode"""
        iface = interface or self._monitor_interface or self._current_interface
        if not iface:
            return False, "No interface specified"
        
        try:
            # Method 1: Try airmon-ng
            result = subprocess.run(
                ["sudo", "airmon-ng", "stop", iface],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Method 2: Manual
                subprocess.run(["sudo", "ip", "link", "set", iface, "down"], timeout=10)
                subprocess.run(["sudo", "iw", iface, "set", "type", "managed"], timeout=10)
                subprocess.run(["sudo", "ip", "link", "set", iface, "up"], timeout=10)
            
            # Restore original interface name
            original = iface.replace("mon", "")
            self._current_interface = original
            self._monitor_interface = None
            
            self.get_interfaces()
            
            print(f"[LinuxDriver] Monitor mode disabled: {original}")
            return True, original
            
        except Exception as e:
            return False, str(e)
    
    def set_channel(self, channel: int, interface: Optional[str] = None) -> bool:
        """Set interface channel"""
        iface = interface or self._current_interface
        if not iface:
            return False
        
        try:
            result = subprocess.run(
                ["sudo", "iw", "dev", iface, "set", "channel", str(channel)],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def cleanup(self):
        """Cleanup Linux driver resources"""
        # Disable monitor mode if enabled
        if self._monitor_interface:
            self.disable_monitor_mode()
        super().cleanup()
        print("[LinuxDriver] Cleanup complete")


__all__ = ['LinuxWiFiDriver']
