"""
WiFi Tester Pro v6.0 - Windows WiFi Driver
Windows-specific WiFi implementation using netsh and WlanApi
"""

import subprocess
import re
import time
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from .abstract import WiFiDriverBase, InterfaceInfo, DriverCapability
from ..settings import NetworkInfo, IS_WINDOWS


class WindowsWiFiDriver(WiFiDriverBase):
    """
    Windows WiFi driver implementation.
    Uses netsh wlan commands for WiFi operations.
    """
    
    def __init__(self):
        super().__init__()
        self._capabilities = {DriverCapability.SCAN}
        # Windows doesn't support these without special hardware/drivers
        # DriverCapability.MONITOR_MODE, etc. are NOT available
    
    def initialize(self) -> bool:
        """Initialize Windows WiFi driver"""
        if not IS_WINDOWS:
            print("[WindowsDriver] Not running on Windows")
            return False
        
        try:
            # Test if netsh is available
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self._is_initialized = True
                # Get initial interface list
                self.get_interfaces()
                print("[WindowsDriver] Initialized successfully")
                return True
            else:
                print(f"[WindowsDriver] netsh failed: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("[WindowsDriver] netsh not found")
            return False
        except subprocess.TimeoutExpired:
            print("[WindowsDriver] netsh timeout")
            return False
        except Exception as e:
            print(f"[WindowsDriver] Initialization error: {e}")
            return False
    
    def get_interfaces(self) -> List[InterfaceInfo]:
        """Get list of WiFi interfaces on Windows"""
        interfaces = []
        
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return interfaces
            
            output = result.stdout
            
            # Parse interface blocks
            current_interface = {}
            
            for line in output.split('\n'):
                line = line.strip()
                if not line:
                    if current_interface.get('name'):
                        info = InterfaceInfo(
                            name=current_interface.get('name', ''),
                            mac_address=current_interface.get('mac', '00:00:00:00:00:00'),
                            driver=current_interface.get('driver', 'Unknown'),
                            mode='managed',
                            is_wireless=True,
                            supports_monitor=False,
                            supports_injection=False,
                        )
                        interfaces.append(info)
                        self._interfaces[info.name] = info
                    current_interface = {}
                    continue
                
                if ':' in line:
                    key, _, value = line.partition(':')
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'name' in key:
                        current_interface['name'] = value
                    elif 'physical address' in key or 'mac' in key:
                        current_interface['mac'] = value
                    elif 'description' in key or 'driver' in key:
                        current_interface['driver'] = value
                    elif 'state' in key:
                        current_interface['state'] = value
            
            # Handle last interface
            if current_interface.get('name'):
                info = InterfaceInfo(
                    name=current_interface.get('name', ''),
                    mac_address=current_interface.get('mac', '00:00:00:00:00:00'),
                    driver=current_interface.get('driver', 'Unknown'),
                    mode='managed',
                    is_wireless=True,
                    supports_monitor=False,
                    supports_injection=False,
                )
                interfaces.append(info)
                self._interfaces[info.name] = info
            
            # Select first interface if none selected
            if interfaces and not self._current_interface:
                self._current_interface = interfaces[0].name
            
        except Exception as e:
            print(f"[WindowsDriver] Error getting interfaces: {e}")
        
        return interfaces
    
    def scan_networks(
        self,
        interface: Optional[str] = None,
        timeout: float = 10.0
    ) -> List[NetworkInfo]:
        """Scan for WiFi networks on Windows"""
        networks = []
        
        try:
            # Run network scan
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                print(f"[WindowsDriver] Scan failed: {result.stderr}")
                return networks
            
            output = result.stdout
            current_network = {}
            
            for line in output.split('\n'):
                line = line.strip()
                
                if line.startswith('SSID') and ':' in line:
                    # Save previous network
                    if current_network.get('bssid'):
                        networks.append(self._create_network_info(current_network))
                    
                    # Start new network
                    ssid = line.split(':', 1)[1].strip()
                    current_network = {'ssid': ssid if ssid else '<Hidden>'}
                
                elif 'BSSID' in line and ':' in line:
                    # Extract BSSID (MAC address format)
                    bssid = line.split(':', 1)[1].strip()
                    current_network['bssid'] = bssid
                
                elif 'Signal' in line and ':' in line:
                    # Extract signal strength (percentage on Windows)
                    signal_str = line.split(':')[1].strip().replace('%', '')
                    try:
                        signal_percent = int(signal_str)
                        # Convert percentage to dBm approximation
                        signal_dbm = int((signal_percent / 2) - 100)
                        current_network['signal'] = signal_dbm
                    except:
                        current_network['signal'] = -80
                
                elif 'Channel' in line and ':' in line:
                    try:
                        channel = int(line.split(':')[1].strip())
                        current_network['channel'] = channel
                    except:
                        current_network['channel'] = 0
                
                elif 'Authentication' in line and ':' in line:
                    auth = line.split(':')[1].strip()
                    current_network['security'] = auth
                
                elif 'Encryption' in line and ':' in line:
                    enc = line.split(':')[1].strip()
                    current_network['encryption'] = enc
                
                elif 'Radio type' in line and ':' in line:
                    radio = line.split(':')[1].strip()
                    current_network['radio'] = radio
            
            # Save last network
            if current_network.get('bssid'):
                networks.append(self._create_network_info(current_network))
            
            print(f"[WindowsDriver] Scan complete: {len(networks)} networks found")
            
        except subprocess.TimeoutExpired:
            print(f"[WindowsDriver] Scan timeout")
        except Exception as e:
            print(f"[WindowsDriver] Scan error: {e}")
        
        return networks
    
    def _create_network_info(self, data: dict) -> NetworkInfo:
        """Create NetworkInfo from parsed data"""
        # Determine frequency from channel
        channel = data.get('channel', 0)
        if channel <= 14:
            frequency = 2412 + (channel - 1) * 5 if channel > 0 else 2437
        else:
            frequency = 5000 + channel * 5
        
        return NetworkInfo(
            ssid=data.get('ssid', '<Hidden>'),
            bssid=data.get('bssid', '00:00:00:00:00:00'),
            signal=data.get('signal', -80),
            channel=channel,
            frequency=frequency,
            security=data.get('security', 'Unknown'),
            encryption=data.get('encryption', ''),
            hidden=data.get('ssid', '') == '<Hidden>',
            first_seen=time.time(),
            last_seen=time.time(),
        )
    
    def get_current_connection(self) -> Optional[NetworkInfo]:
        """Get current WiFi connection info"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            output = result.stdout
            connection_data = {}
            
            for line in output.split('\n'):
                line = line.strip()
                if ':' not in line:
                    continue
                
                key, _, value = line.partition(':')
                key = key.strip().lower()
                value = value.strip()
                
                if 'ssid' in key and 'bssid' not in key:
                    connection_data['ssid'] = value
                elif 'bssid' in key:
                    connection_data['bssid'] = value
                elif 'signal' in key:
                    try:
                        signal_percent = int(value.replace('%', ''))
                        connection_data['signal'] = int((signal_percent / 2) - 100)
                    except:
                        connection_data['signal'] = -80
                elif 'channel' in key:
                    try:
                        connection_data['channel'] = int(value)
                    except:
                        connection_data['channel'] = 0
                elif 'authentication' in key:
                    connection_data['security'] = value
                elif 'state' in key:
                    connection_data['state'] = value
            
            # Only return if connected
            if connection_data.get('state', '').lower() == 'connected':
                return self._create_network_info(connection_data)
            
        except Exception as e:
            print(f"[WindowsDriver] Error getting connection: {e}")
        
        return None
    
    def disconnect(self) -> bool:
        """Disconnect from current WiFi network"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "disconnect"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def connect(self, ssid: str, password: Optional[str] = None) -> bool:
        """Connect to a WiFi network (requires saved profile)"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "connect", f"name={ssid}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except:
            return False
    
    def get_saved_profiles(self) -> List[str]:
        """Get list of saved WiFi profiles"""
        profiles = []
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'All User Profile' in line and ':' in line:
                        profile = line.split(':')[1].strip()
                        if profile:
                            profiles.append(profile)
        except Exception as e:
            print(f"[WindowsDriver] Error getting profiles: {e}")
        
        return profiles
    
    def get_profile_password(self, profile_name: str) -> Optional[str]:
        """
        Get the saved password for a WiFi profile.
        Requires admin privileges to retrieve passwords.
        
        Args:
            profile_name: Name of the WiFi profile
            
        Returns:
            Password string if found, None otherwise
        """
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "profile", f"name={profile_name}", "key=clear"],
                capture_output=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    # Look for "Key Content" line which contains the password
                    if 'Key Content' in line and ':' in line:
                        password = line.split(':', 1)[1].strip()
                        return password if password else None
            
        except Exception as e:
            print(f"[WindowsDriver] Error getting password for {profile_name}: {e}")
        
        return None
    
    def get_all_saved_passwords(self) -> Dict[str, Optional[str]]:
        """
        Get all saved WiFi passwords.
        Requires admin privileges.
        
        Returns:
            Dictionary mapping profile names to passwords
        """
        passwords = {}
        profiles = self.get_saved_profiles()
        
        for profile in profiles:
            passwords[profile] = self.get_profile_password(profile)
        
        return passwords
    
    def cleanup(self):
        """Cleanup Windows driver resources"""
        super().cleanup()
        print("[WindowsDriver] Cleanup complete")


__all__ = ['WindowsWiFiDriver']
