"""
WiFi Tester Pro v6.0 - Dashboard Tab
Main overview page with system status and quick actions
"""

import customtkinter as ctk
from typing import Optional
import time

from ...settings import Colors, Fonts, Layout, IS_WINDOWS, IS_KALI, RUNNING_AS_ADMIN
from ..utils import create_button, create_label, create_card
from ..passwords_dialog import SavedPasswordsDialog


class StatCard(ctk.CTkFrame):
    """Card displaying a single statistic"""
    
    def __init__(
        self,
        parent,
        title: str,
        value: str,
        icon: str = "",
        color: str = Colors.PRIMARY,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=12,
            **kwargs
        )
        
        self._title = title
        self._value_var = ctk.StringVar(value=value)
        
        # Icon
        if icon:
            icon_label = ctk.CTkLabel(
                self,
                text=icon,
                font=(Fonts.FAMILY, 28),
                text_color=color
            )
            icon_label.pack(pady=(20, 5))
        
        # Value
        self._value_label = ctk.CTkLabel(
            self,
            textvariable=self._value_var,
            font=(Fonts.FAMILY, 32, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        self._value_label.pack(pady=5)
        
        # Title
        ctk.CTkLabel(
            self,
            text=title,
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_SECONDARY
        ).pack(pady=(0, 20))
    
    def set_value(self, value: str):
        """Update the displayed value"""
        self._value_var.set(value)


class DashboardTab(ctk.CTkFrame):
    """
    Dashboard page showing system overview.
    """
    
    def __init__(self, parent, driver=None, session=None, logger=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self._driver = driver
        self._session = session
        self._logger = logger
        
        self._create_ui()
    
    def _create_ui(self):
        """Create dashboard UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        self._create_header()
        
        # Stats row
        self._create_stats()
        
        # Main content
        self._create_content()
    
    def _create_header(self):
        """Create page header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        create_label(
            header,
            text="Dashboard",
            style="heading"
        ).pack(side="left")
        
        # Refresh button
        create_button(
            header,
            text="Refresh",
            icon="🔄",
            style="ghost",
            width=100,
            command=self._refresh
        ).pack(side="right")
    
    def _create_stats(self):
        """Create statistics cards row"""
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Configure columns
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Network count
        self._stat_networks = StatCard(
            stats_frame,
            title="Networks Found",
            value="0",
            icon="📡",
            color=Colors.PRIMARY
        )
        self._stat_networks.grid(row=0, column=0, padx=5, sticky="ew")
        
        # Interface
        interface_text = self._session.interface if self._session else "None"
        self._stat_interface = StatCard(
            stats_frame,
            title="Active Interface",
            value=interface_text or "None",
            icon="📶",
            color=Colors.SUCCESS
        )
        self._stat_interface.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Security status
        self._stat_security = StatCard(
            stats_frame,
            title="Security Mode",
            value="Normal",
            icon="🔒",
            color=Colors.WARNING
        )
        self._stat_security.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Status
        status = "Admin" if RUNNING_AS_ADMIN else "User"
        self._stat_status = StatCard(
            stats_frame,
            title="Privileges",
            value=status,
            icon="👤",
            color=Colors.SUCCESS if RUNNING_AS_ADMIN else Colors.WARNING
        )
        self._stat_status.grid(row=0, column=3, padx=5, sticky="ew")
    
    def _create_content(self):
        """Create main content area"""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        
        # Left: Quick actions
        self._create_quick_actions(content)
        
        # Right: System info
        self._create_system_info(content)
    
    def _create_quick_actions(self, parent):
        """Create quick actions panel"""
        card, content = create_card(parent, title="Quick Actions")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Actions grid
        actions_grid = ctk.CTkFrame(content, fg_color="transparent")
        actions_grid.pack(fill="both", expand=True)
        
        actions = [
            ("Start Scan", "📡", Colors.PRIMARY, self._start_scan),
            ("Current Network", "🌐", Colors.SUCCESS, self._show_current),
            ("Security Audit", "🔒", Colors.WARNING, self._start_audit),
            ("View Passwords", "🔑", Colors.ACCENT, self._view_passwords),
            ("Refresh All", "🔄", Colors.INFO, self._refresh),
        ]
        
        for i, (text, icon, color, cmd) in enumerate(actions):
            row = i // 3
            col = i % 3
            
            btn = ctk.CTkButton(
                actions_grid,
                text=f"{icon}\n{text}",
                font=(Fonts.FAMILY, Fonts.SIZE_MD),
                width=120,
                height=90,
                corner_radius=12,
                fg_color=Colors.SURFACE_LIGHT,
                hover_color=color,
                text_color=Colors.TEXT_PRIMARY,
                command=cmd
            )
            btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            actions_grid.grid_columnconfigure(col, weight=1)
        
        actions_grid.grid_rowconfigure(0, weight=1)
        actions_grid.grid_rowconfigure(1, weight=1)
    
    def _create_system_info(self, parent):
        """Create system info panel"""
        card, content = create_card(parent, title="System Information")
        card.grid(row=0, column=1, sticky="nsew")
        
        # Info items
        info_items = [
            ("Platform", "Windows" if IS_WINDOWS else ("Kali Linux" if IS_KALI else "Linux")),
            ("Privileges", "Administrator" if RUNNING_AS_ADMIN else "Standard User"),
            ("Driver", "Windows WiFi" if IS_WINDOWS else "Linux WiFi"),
            ("Monitor Mode", "Not Available" if IS_WINDOWS else ("Available" if IS_KALI else "Limited")),
            ("Security Features", "Basic" if IS_WINDOWS else ("Full" if IS_KALI else "Basic")),
        ]
        
        for label, value in info_items:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=(Fonts.FAMILY, Fonts.SIZE_SM),
                text_color=Colors.TEXT_MUTED,
                width=120,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=(Fonts.FAMILY, Fonts.SIZE_SM),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
    
    # ==========================================================================
    # Actions
    # ==========================================================================
    
    def _start_scan(self):
        """Navigate to scanner page"""
        # Find root window and navigate
        root = self.winfo_toplevel()
        if hasattr(root, 'show_page'):
            root.show_page("scanner")
    
    def _show_current(self):
        """Show current network info"""
        from ..utils import show_message
        
        if not self._driver:
            show_message("Current Network", "Driver not initialized", "warning")
            return
        
        try:
            current = self._driver.get_current_connection()
            if current:
                show_message(
                    "Current Network",
                    f"SSID: {current.ssid}\n"
                    f"BSSID: {current.bssid}\n"
                    f"Signal: {current.signal} dBm\n"
                    f"Channel: {current.channel}\n"
                    f"Security: {current.security}",
                    "info"
                )
            else:
                show_message("Current Network", "Not connected to any network", "info")
        except Exception as e:
            show_message("Current Network", f"Error getting connection: {e}", "error")
    
    def _start_audit(self):
        """Navigate to auditor page"""
        root = self.winfo_toplevel()
        if hasattr(root, 'show_page'):
            root.show_page("auditor")
    
    def _view_passwords(self):
        """Open the saved passwords dialog"""
        root = self.winfo_toplevel()
        SavedPasswordsDialog(root, driver=self._driver)
    
    def _refresh(self):
        """Refresh dashboard data"""
        if self._session:
            network_count = len(self._session.networks)
            self._stat_networks.set_value(str(network_count))
            
            interface = self._session.interface or "None"
            self._stat_interface.set_value(interface)
        
        if self._logger:
            self._logger.info("Dashboard refreshed", "Dashboard")
    
    def on_show(self):
        """Called when page is shown"""
        self._refresh()


__all__ = ['DashboardTab']
