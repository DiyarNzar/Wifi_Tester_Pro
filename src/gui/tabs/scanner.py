"""
WiFi Tester Pro v6.0 - Scanner Tab
Network scanning and discovery page
"""

import customtkinter as ctk
from typing import Optional, List, Dict
import time

from ...settings import Colors, Fonts, Layout, NetworkInfo, EventType
from ..utils import (
    create_button, create_label, format_signal,
    get_signal_color, get_security_color
)


class NetworkRow(ctk.CTkFrame):
    """Single row displaying network information"""
    
    def __init__(
        self,
        parent,
        network: NetworkInfo,
        on_select=None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=8,
            height=50,
            **kwargs
        )
        
        self._network = network
        self._on_select = on_select
        self._selected = False
        
        self.pack_propagate(False)
        self._create_ui()
        
        # Bind click
        self.bind("<Button-1>", self._on_click)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._on_click)
    
    def _create_ui(self):
        """Create row UI"""
        # Signal indicator
        signal_color = get_signal_color(self._network.signal)
        signal_frame = ctk.CTkFrame(
            self,
            width=8,
            fg_color=signal_color,
            corner_radius=4
        )
        signal_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # SSID
        ssid_text = self._network.ssid if self._network.ssid else "<Hidden>"
        ctk.CTkLabel(
            self,
            text=ssid_text,
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.TEXT_PRIMARY,
            width=200,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # BSSID
        ctk.CTkLabel(
            self,
            text=self._network.bssid,
            font=(Fonts.MONO, Fonts.SIZE_SM),
            text_color=Colors.TEXT_SECONDARY,
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Channel
        ctk.CTkLabel(
            self,
            text=f"CH {self._network.channel}",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_SECONDARY,
            width=60,
            anchor="center"
        ).pack(side="left", padx=5)
        
        # Signal
        ctk.CTkLabel(
            self,
            text=f"{self._network.signal} dBm",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=signal_color,
            width=80,
            anchor="center"
        ).pack(side="left", padx=5)
        
        # Security
        security_color = get_security_color(self._network.security)
        ctk.CTkLabel(
            self,
            text=self._network.security[:10],
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=security_color,
            width=80,
            anchor="center"
        ).pack(side="left", padx=5)
    
    def _on_click(self, event):
        """Handle row click"""
        if self._on_select:
            self._on_select(self._network)
    
    def set_selected(self, selected: bool):
        """Set selection state"""
        self._selected = selected
        if selected:
            self.configure(fg_color=Colors.PRIMARY)
        else:
            self.configure(fg_color=Colors.SURFACE_DARK)


class ScannerTab(ctk.CTkFrame):
    """
    Scanner page for network discovery.
    """
    
    def __init__(
        self,
        parent,
        driver=None,
        session=None,
        engine=None,
        logger=None,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self._driver = driver
        self._session = session
        self._engine = engine
        self._logger = logger
        
        self._network_rows: Dict[str, NetworkRow] = {}
        self._selected_network: Optional[NetworkInfo] = None
        self._is_scanning = False
        
        self._create_ui()
        self._bind_events()
    
    def _create_ui(self):
        """Create scanner UI"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self._create_header()
        
        # Network list
        self._create_network_list()
        
        # Details panel
        self._create_details_panel()
    
    def _create_header(self):
        """Create page header with controls"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Title
        create_label(header, text="Network Scanner", style="heading").pack(side="left")
        
        # Controls
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side="right")
        
        # Interface selector
        ctk.CTkLabel(
            controls,
            text="Interface:",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_SECONDARY
        ).pack(side="left", padx=(0, 5))
        
        interfaces = self._session.interfaces if self._session else []
        self._interface_var = ctk.StringVar(
            value=self._session.interface if self._session else ""
        )
        
        self._interface_menu = ctk.CTkOptionMenu(
            controls,
            values=interfaces if interfaces else ["No interfaces"],
            variable=self._interface_var,
            width=150,
            fg_color=Colors.SURFACE_LIGHT,
            button_color=Colors.SURFACE_MEDIUM,
            button_hover_color=Colors.PRIMARY,
            dropdown_fg_color=Colors.SURFACE_DARK,
            command=self._on_interface_change
        )
        self._interface_menu.pack(side="left", padx=10)
        
        # Scan button
        self._scan_button = create_button(
            controls,
            text="Start Scan",
            icon="📡",
            style="primary",
            width=130,
            command=self._toggle_scan
        )
        self._scan_button.pack(side="left", padx=5)
        
        # Clear button
        create_button(
            controls,
            text="Clear",
            icon="🗑",
            style="ghost",
            width=80,
            command=self._clear_results
        ).pack(side="left", padx=5)
    
    def _create_network_list(self):
        """Create scrollable network list"""
        # Container
        list_container = ctk.CTkFrame(self, fg_color=Colors.SURFACE_MEDIUM, corner_radius=12)
        list_container.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(1, weight=1)
        
        # Header row
        header_row = ctk.CTkFrame(list_container, fg_color="transparent", height=40)
        header_row.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_row.pack_propagate(False)
        
        columns = [
            ("", 18),
            ("SSID", 200),
            ("BSSID", 150),
            ("Channel", 60),
            ("Signal", 80),
            ("Security", 80),
        ]
        
        for text, width in columns:
            ctk.CTkLabel(
                header_row,
                text=text,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, "bold"),
                text_color=Colors.TEXT_MUTED,
                width=width,
                anchor="w" if text else "center"
            ).pack(side="left", padx=10 if text else 0)
        
        # Separator
        ctk.CTkFrame(
            list_container,
            height=1,
            fg_color=Colors.BORDER
        ).grid(row=0, column=0, sticky="ew", padx=10, pady=(45, 0))
        
        # Scrollable list
        self._network_scroll = ctk.CTkScrollableFrame(
            list_container,
            fg_color="transparent"
        )
        self._network_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Status label (placed in scroll frame initially, will be managed separately)
        self._status_frame = ctk.CTkFrame(self._network_scroll, fg_color="transparent")
        self._status_frame.pack(fill="x", pady=50)
        
        self._status_label = ctk.CTkLabel(
            self._status_frame,
            text="Click 'Start Scan' to discover networks",
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.TEXT_MUTED
        )
        self._status_label.pack()
    
    def _create_details_panel(self):
        """Create selected network details panel"""
        self._details_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=12,
            height=120
        )
        self._details_frame.grid(row=2, column=0, sticky="ew")
        self._details_frame.pack_propagate(False)
        
        # Details content
        self._details_content = ctk.CTkFrame(self._details_frame, fg_color="transparent")
        self._details_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        ctk.CTkLabel(
            self._details_content,
            text="Select a network to view details",
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.TEXT_MUTED
        ).pack(pady=30)
    
    def _bind_events(self):
        """Bind session events"""
        if self._session:
            self._session.subscribe(EventType.SCAN_COMPLETED, self._on_scan_complete)
            self._session.subscribe(EventType.NETWORK_FOUND, self._on_network_found)
    
    # ==========================================================================
    # Actions
    # ==========================================================================
    
    def _toggle_scan(self):
        """Start or stop scanning"""
        if self._is_scanning:
            self._stop_scan()
        else:
            self._start_scan()
    
    def _start_scan(self):
        """Start network scan"""
        if not self._driver:
            if self._logger:
                self._logger.error("No driver available", "Scanner")
            return
        
        self._is_scanning = True
        self._scan_button.configure(text="⏹ Stop")
        
        # Show scanning status
        self._show_status("Scanning...")
        
        if self._session:
            self._session.is_scanning = True
        
        # Run scan in background
        if self._engine:
            self._engine.submit(
                self._perform_scan,
                name="network_scan",
                callback=self._on_scan_done,
                error_callback=self._on_scan_error
            )
        else:
            # Fallback: run directly (may freeze UI)
            self._perform_scan()
            self._on_scan_done([])
    
    def _perform_scan(self) -> List[NetworkInfo]:
        """Perform the actual scan (runs in background thread)"""
        if self._driver:
            return self._driver.scan_networks(timeout=15.0)
        return []
    
    def _on_scan_done(self, networks: List[NetworkInfo]):
        """Handle scan completion"""
        self._is_scanning = False
        self._scan_button.configure(text="📡 Start Scan")
        
        if self._session:
            self._session.is_scanning = False
            # Update session with results
            for network in networks:
                self._session.add_network(network)
        
        self._update_network_list(networks)
        
        if self._logger:
            self._logger.info(f"Scan complete: {len(networks)} networks", "Scanner")
    
    def _on_scan_error(self, error: Exception):
        """Handle scan error"""
        self._is_scanning = False
        self._scan_button.configure(text="📡 Start Scan")
        
        if self._session:
            self._session.is_scanning = False
        
        # Show error status
        self._show_status(f"Scan error: {error}")
        
        if self._logger:
            self._logger.error(f"Scan error: {error}", "Scanner")
    
    def _stop_scan(self):
        """Stop scanning"""
        self._is_scanning = False
        self._scan_button.configure(text="📡 Start Scan")
        
        if self._session:
            self._session.is_scanning = False
    
    def _show_status(self, text: str):
        """Show status message in the network list area"""
        # Clear existing content
        for widget in self._network_scroll.winfo_children():
            widget.destroy()
        self._network_rows.clear()
        
        # Create new status frame and label
        self._status_frame = ctk.CTkFrame(self._network_scroll, fg_color="transparent")
        self._status_frame.pack(fill="x", pady=50)
        
        self._status_label = ctk.CTkLabel(
            self._status_frame,
            text=text,
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.TEXT_MUTED
        )
        self._status_label.pack()
    
    def _update_network_list(self, networks: List[NetworkInfo]):
        """Update the network list display"""
        # Clear existing rows
        for widget in self._network_scroll.winfo_children():
            widget.destroy()
        self._network_rows.clear()
        
        if not networks:
            self._show_status("No networks found")
            return
        
        # Sort by signal strength
        networks = sorted(networks, key=lambda n: n.signal, reverse=True)
        
        # Add rows
        for network in networks:
            row = NetworkRow(
                self._network_scroll,
                network,
                on_select=self._on_network_select
            )
            row.pack(fill="x", pady=2)
            self._network_rows[network.bssid] = row
    
    def _on_network_select(self, network: NetworkInfo):
        """Handle network selection"""
        # Update selection
        if self._selected_network:
            old_bssid = self._selected_network.bssid
            if old_bssid in self._network_rows:
                self._network_rows[old_bssid].set_selected(False)
        
        self._selected_network = network
        
        if network.bssid in self._network_rows:
            self._network_rows[network.bssid].set_selected(True)
        
        if self._session:
            self._session.selected_network = network.bssid
        
        # Update details panel
        self._show_network_details(network)
    
    def _show_network_details(self, network: NetworkInfo):
        """Show selected network details"""
        # Clear details
        for widget in self._details_content.winfo_children():
            widget.destroy()
        
        # Create details grid
        details = [
            ("SSID", network.ssid or "<Hidden>"),
            ("BSSID", network.bssid),
            ("Signal", f"{network.signal} dBm ({network.signal_quality})"),
            ("Channel", str(network.channel)),
            ("Frequency", f"{network.frequency} MHz"),
            ("Security", network.security),
            ("WPS", "Yes" if network.wps else "No"),
        ]
        
        row_frame = ctk.CTkFrame(self._details_content, fg_color="transparent")
        row_frame.pack(fill="x")
        
        for i, (label, value) in enumerate(details):
            col = i % 4
            
            item = ctk.CTkFrame(row_frame, fg_color="transparent")
            item.pack(side="left", padx=15)
            
            ctk.CTkLabel(
                item,
                text=label,
                font=(Fonts.FAMILY, Fonts.SIZE_SM),
                text_color=Colors.TEXT_MUTED
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                item,
                text=value,
                font=(Fonts.FAMILY, Fonts.SIZE_MD),
                text_color=Colors.TEXT_PRIMARY
            ).pack(anchor="w")
    
    def _clear_results(self):
        """Clear scan results"""
        for widget in self._network_scroll.winfo_children():
            widget.destroy()
        self._network_rows.clear()
        self._selected_network = None
        
        self._status_label = ctk.CTkLabel(
            self._network_scroll,
            text="Click 'Start Scan' to discover networks",
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.TEXT_MUTED
        )
        self._status_label.pack(pady=50)
        
        # Clear details
        for widget in self._details_content.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(
            self._details_content,
            text="Select a network to view details",
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.TEXT_MUTED
        ).pack(pady=30)
        
        if self._session:
            self._session.clear_networks()
    
    def _on_interface_change(self, interface: str):
        """Handle interface change"""
        if self._session:
            self._session.interface = interface
        
        if self._driver:
            self._driver.select_interface(interface)
    
    def _on_scan_complete(self, event_type, data):
        """Handle scan complete event"""
        pass  # Already handled by callback
    
    def _on_network_found(self, event_type, data):
        """Handle network found event"""
        pass  # Will refresh on next scan
    
    def on_show(self):
        """Called when page is shown"""
        # Update interface list
        if self._session:
            interfaces = self._session.interfaces
            if interfaces:
                self._interface_menu.configure(values=interfaces)
                if self._session.interface:
                    self._interface_var.set(self._session.interface)


__all__ = ['ScannerTab']
