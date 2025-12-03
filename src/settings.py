"""
WiFi Tester Pro v6.0 - Global Settings
Centralized configuration constants and paths
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum, auto

# =============================================================================
# APPLICATION METADATA
# =============================================================================
APP_NAME = "WiFi Tester Pro"
APP_VERSION = "6.0.0"
APP_AUTHOR = "WiFi Tester Pro Team"
APP_DESCRIPTION = "Professional WiFi Analysis & Security Auditing Tool"

# =============================================================================
# PATHS
# =============================================================================
def get_base_path() -> Path:
    """Get application base path, works for both dev and frozen (PyInstaller)"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent

BASE_PATH = get_base_path()
ASSETS_PATH = BASE_PATH / "assets"
LOGS_PATH = BASE_PATH / "logs"
CONFIG_PATH = BASE_PATH / "config"
THEME_FILE = ASSETS_PATH / "theme.json"

# Create directories if they don't exist
for path in [LOGS_PATH, CONFIG_PATH]:
    path.mkdir(parents=True, exist_ok=True)

# =============================================================================
# PLATFORM DETECTION
# =============================================================================
class Platform(Enum):
    WINDOWS = auto()
    LINUX = auto()
    KALI = auto()
    MACOS = auto()
    UNKNOWN = auto()

def detect_platform() -> Platform:
    """Detect current operating system platform"""
    if sys.platform == 'win32':
        return Platform.WINDOWS
    elif sys.platform == 'darwin':
        return Platform.MACOS
    elif sys.platform.startswith('linux'):
        # Check if running Kali Linux
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'kali' in content:
                    return Platform.KALI
        except:
            pass
        return Platform.LINUX
    return Platform.UNKNOWN

CURRENT_PLATFORM = detect_platform()
IS_WINDOWS = CURRENT_PLATFORM == Platform.WINDOWS
IS_LINUX = CURRENT_PLATFORM in (Platform.LINUX, Platform.KALI)
IS_KALI = CURRENT_PLATFORM == Platform.KALI
IS_MACOS = CURRENT_PLATFORM == Platform.MACOS

# =============================================================================
# THEME & COLORS
# =============================================================================
def load_theme() -> Dict[str, Any]:
    """Load theme configuration from JSON file"""
    default_theme = {
        "colors": {
            "primary": "#1E90FF",
            "primary_hover": "#4169E1",
            "secondary": "#2ECC71",
            "accent": "#9B59B6",
            "success": "#2ECC71",
            "warning": "#F39C12",
            "error": "#E74C3C",
            "info": "#3498DB",
            "background": {"dark": "#1a1a2e", "medium": "#16213e", "light": "#0f3460"},
            "surface": {"dark": "#0f0f23", "medium": "#1a1a2e", "light": "#252547"},
            "text": {"primary": "#FFFFFF", "secondary": "#B0B0B0", "muted": "#6C7A89"},
            "border": {"default": "#3a3a5c", "active": "#1E90FF"},
            "terminal": {"background": "#0a0a1a", "foreground": "#00FF00"},
            "signal": {"excellent": "#2ECC71", "good": "#27AE60", "fair": "#F39C12", "weak": "#E67E22", "poor": "#E74C3C"},
            "security": {"open": "#E74C3C", "wep": "#E67E22", "wpa": "#F39C12", "wpa2": "#2ECC71", "wpa3": "#1E90FF"}
        },
        "fonts": {"family": {"primary": "Segoe UI", "monospace": "Consolas"}, "sizes": {"sm": 12, "md": 14, "lg": 16}},
        "spacing": {"sm": 8, "md": 12, "lg": 16, "xl": 24},
        "components": {"sidebar": {"width": 220}, "terminal": {"max_lines": 1000}}
    }
    
    try:
        if THEME_FILE.exists():
            with open(THEME_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load theme: {e}")
    
    return default_theme

THEME = load_theme()

# Flattened color access for convenience
class Colors:
    """Easy access to theme colors"""
    PRIMARY = THEME["colors"]["primary"]
    PRIMARY_HOVER = THEME["colors"].get("primary_hover", "#4169E1")
    SECONDARY = THEME["colors"]["secondary"]
    ACCENT = THEME["colors"]["accent"]
    SUCCESS = THEME["colors"]["success"]
    WARNING = THEME["colors"]["warning"]
    ERROR = THEME["colors"]["error"]
    INFO = THEME["colors"].get("info", "#3498DB")
    
    # Backgrounds
    BG_DARK = THEME["colors"]["background"]["dark"]
    BG_MEDIUM = THEME["colors"]["background"]["medium"]
    BG_LIGHT = THEME["colors"]["background"]["light"]
    
    # Surfaces
    SURFACE_DARK = THEME["colors"]["surface"]["dark"]
    SURFACE_MEDIUM = THEME["colors"]["surface"]["medium"]
    SURFACE_LIGHT = THEME["colors"]["surface"]["light"]
    
    # Text
    TEXT_PRIMARY = THEME["colors"]["text"]["primary"]
    TEXT_SECONDARY = THEME["colors"]["text"]["secondary"]
    TEXT_MUTED = THEME["colors"]["text"]["muted"]
    
    # Border
    BORDER = THEME["colors"]["border"]["default"]
    BORDER_ACTIVE = THEME["colors"]["border"]["active"]
    
    # Terminal
    TERMINAL_BG = THEME["colors"]["terminal"]["background"]
    TERMINAL_FG = THEME["colors"]["terminal"]["foreground"]
    
    # Signal strength colors
    SIGNAL_EXCELLENT = THEME["colors"]["signal"]["excellent"]
    SIGNAL_GOOD = THEME["colors"]["signal"]["good"]
    SIGNAL_FAIR = THEME["colors"]["signal"]["fair"]
    SIGNAL_WEAK = THEME["colors"]["signal"]["weak"]
    SIGNAL_POOR = THEME["colors"]["signal"]["poor"]
    
    # Security colors
    SEC_OPEN = THEME["colors"]["security"]["open"]
    SEC_WEP = THEME["colors"]["security"]["wep"]
    SEC_WPA = THEME["colors"]["security"]["wpa"]
    SEC_WPA2 = THEME["colors"]["security"]["wpa2"]
    SEC_WPA3 = THEME["colors"]["security"]["wpa3"]

# =============================================================================
# FONTS
# =============================================================================
class Fonts:
    """Font configuration"""
    FAMILY = THEME["fonts"]["family"].get("primary", "Segoe UI")
    MONO = THEME["fonts"]["family"].get("monospace", "Consolas")
    SIZE_SM = THEME["fonts"]["sizes"].get("sm", 12)
    SIZE_MD = THEME["fonts"]["sizes"].get("md", 14)
    SIZE_LG = THEME["fonts"]["sizes"].get("lg", 16)
    SIZE_XL = THEME["fonts"]["sizes"].get("xl", 20)
    SIZE_TITLE = THEME["fonts"]["sizes"].get("title", 28)

# =============================================================================
# SPACING & LAYOUT
# =============================================================================
class Layout:
    """Layout constants"""
    PAD_XS = THEME["spacing"].get("xs", 4)
    PAD_SM = THEME["spacing"].get("sm", 8)
    PAD_MD = THEME["spacing"].get("md", 12)
    PAD_LG = THEME["spacing"].get("lg", 16)
    PAD_XL = THEME["spacing"].get("xl", 24)
    PAD_XXL = THEME["spacing"].get("xxl", 32)
    
    # Aliases for compatibility
    PADDING_SM = PAD_SM
    PADDING_MD = PAD_MD
    PADDING_LG = PAD_LG
    
    # Border radius
    BORDER_RADIUS = 12
    BORDER_RADIUS_SM = 8
    BORDER_RADIUS_LG = 16
    
    SIDEBAR_WIDTH = THEME["components"]["sidebar"].get("width", 220)
    TERMINAL_MAX_LINES = THEME["components"]["terminal"].get("max_lines", 1000)
    
    WINDOW_MIN_WIDTH = 1200
    WINDOW_MIN_HEIGHT = 800
    WINDOW_DEFAULT_WIDTH = 1400
    WINDOW_DEFAULT_HEIGHT = 900

# =============================================================================
# SCANNING CONFIGURATION
# =============================================================================
@dataclass
class ScanConfig:
    """WiFi scanning configuration"""
    scan_interval: float = 3.0  # seconds between scans
    channel_hop_interval: float = 0.3  # seconds per channel
    max_networks: int = 100
    timeout: float = 30.0
    channels_24ghz: list = field(default_factory=lambda: list(range(1, 15)))
    channels_5ghz: list = field(default_factory=lambda: list(range(36, 166, 4)))
    auto_refresh: bool = True
    show_hidden: bool = True
    min_signal: int = -100  # dBm

DEFAULT_SCAN_CONFIG = ScanConfig()

# =============================================================================
# EVENT TYPES
# =============================================================================
class EventType(Enum):
    """Application event types for pub/sub system"""
    # Scanning events
    SCAN_STARTED = auto()
    SCAN_COMPLETED = auto()
    SCAN_FAILED = auto()
    SCAN_PROGRESS = auto()
    NETWORK_FOUND = auto()
    NETWORK_UPDATED = auto()
    NETWORK_LOST = auto()
    
    # Interface events
    INTERFACE_CHANGED = auto()
    INTERFACE_ERROR = auto()
    MONITOR_MODE_ENABLED = auto()
    MONITOR_MODE_DISABLED = auto()
    
    # Security events
    AUDIT_STARTED = auto()
    AUDIT_COMPLETED = auto()
    AUDIT_PROGRESS = auto()
    VULNERABILITY_FOUND = auto()
    
    # Session events
    SESSION_STARTED = auto()
    SESSION_ENDED = auto()
    SESSION_ERROR = auto()
    
    # UI events
    PAGE_CHANGED = auto()
    THEME_CHANGED = auto()
    SETTINGS_CHANGED = auto()
    
    # Log events
    LOG_INFO = auto()
    LOG_WARNING = auto()
    LOG_ERROR = auto()
    LOG_DEBUG = auto()

# =============================================================================
# NETWORK DATA STRUCTURES
# =============================================================================
@dataclass
class NetworkInfo:
    """WiFi network information"""
    ssid: str
    bssid: str
    signal: int  # dBm
    channel: int
    frequency: float  # MHz
    security: str
    encryption: str = ""
    vendor: str = ""
    first_seen: float = 0.0
    last_seen: float = 0.0
    beacon_count: int = 0
    clients: list = field(default_factory=list)
    hidden: bool = False
    wps: bool = False
    
    @property
    def signal_quality(self) -> str:
        """Get signal quality category"""
        if self.signal >= -50:
            return "excellent"
        elif self.signal >= -60:
            return "good"
        elif self.signal >= -70:
            return "fair"
        elif self.signal >= -80:
            return "weak"
        return "poor"
    
    @property
    def signal_percent(self) -> int:
        """Convert dBm to percentage"""
        if self.signal >= -50:
            return 100
        elif self.signal <= -100:
            return 0
        return 2 * (self.signal + 100)

# =============================================================================
# SECURITY LEVELS
# =============================================================================
class SecurityLevel(Enum):
    """WiFi security levels"""
    OPEN = 0
    WEP = 1
    WPA = 2
    WPA2 = 3
    WPA3 = 4
    
    @classmethod
    def from_string(cls, security: str) -> 'SecurityLevel':
        """Parse security string to enum"""
        security = security.upper()
        if 'WPA3' in security:
            return cls.WPA3
        elif 'WPA2' in security:
            return cls.WPA2
        elif 'WPA' in security:
            return cls.WPA
        elif 'WEP' in security:
            return cls.WEP
        return cls.OPEN
    
    @property
    def color(self) -> str:
        """Get color for security level"""
        colors = {
            SecurityLevel.OPEN: Colors.SEC_OPEN,
            SecurityLevel.WEP: Colors.SEC_WEP,
            SecurityLevel.WPA: Colors.SEC_WPA,
            SecurityLevel.WPA2: Colors.SEC_WPA2,
            SecurityLevel.WPA3: Colors.SEC_WPA3,
        }
        return colors.get(self, Colors.SEC_OPEN)

# =============================================================================
# ADMIN / PRIVILEGES
# =============================================================================
def is_admin() -> bool:
    """Check if running with administrator/root privileges"""
    try:
        if IS_WINDOWS:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

RUNNING_AS_ADMIN = is_admin()

# =============================================================================
# LOGGING CONFIG
# =============================================================================
LOG_CONFIG = {
    "level": "DEBUG",
    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "file_enabled": True,
    "console_enabled": True,
    "max_file_size": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5,
}

# =============================================================================
# EXPORT ALL
# =============================================================================
__all__ = [
    # Metadata
    'APP_NAME', 'APP_VERSION', 'APP_AUTHOR', 'APP_DESCRIPTION',
    # Paths
    'BASE_PATH', 'ASSETS_PATH', 'LOGS_PATH', 'CONFIG_PATH', 'THEME_FILE',
    # Platform
    'Platform', 'CURRENT_PLATFORM', 'IS_WINDOWS', 'IS_LINUX', 'IS_KALI', 'IS_MACOS',
    # Theme
    'THEME', 'Colors', 'Fonts', 'Layout',
    # Config
    'ScanConfig', 'DEFAULT_SCAN_CONFIG',
    # Events
    'EventType',
    # Data structures
    'NetworkInfo', 'SecurityLevel',
    # Admin
    'is_admin', 'RUNNING_AS_ADMIN',
    # Logging
    'LOG_CONFIG',
]
