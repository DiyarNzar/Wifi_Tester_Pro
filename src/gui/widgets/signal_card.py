"""
WiFi Tester Pro v6.0 - Signal Card Widgets
Visual cards for displaying WiFi signal and network information
"""

import customtkinter as ctk
from typing import Optional, Dict, Any, Callable

from ...settings import Colors, Fonts, Layout, NetworkInfo


class SignalCard(ctk.CTkFrame):
    """
    Widget displaying WiFi signal strength with visual indicator.
    Shows signal bars and dBm value.
    """
    
    def __init__(
        self,
        parent,
        title: str = "Signal Strength",
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Layout.BORDER_RADIUS,
            **kwargs
        )
        
        self._title = title
        self._signal_dbm = -100
        self._create_ui()
    
    def _create_ui(self):
        """Create signal card UI"""
        # Title
        ctk.CTkLabel(
            self,
            text=self._title,
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_SECONDARY
        ).pack(padx=Layout.PADDING_SM, pady=(Layout.PADDING_SM, 0), anchor="w")
        
        # Signal display frame
        signal_frame = ctk.CTkFrame(self, fg_color="transparent")
        signal_frame.pack(fill="x", padx=Layout.PADDING_SM, pady=Layout.PADDING_SM)
        
        # Signal bars container
        self._bars_frame = ctk.CTkFrame(signal_frame, fg_color="transparent")
        self._bars_frame.pack(side="left")
        
        # Create signal bars
        self._bars = []
        bar_heights = [8, 14, 20, 26, 32]
        for i, height in enumerate(bar_heights):
            bar = ctk.CTkFrame(
                self._bars_frame,
                width=8,
                height=height,
                fg_color=Colors.SURFACE_LIGHT,
                corner_radius=2
            )
            bar.pack(side="left", padx=2, anchor="s")
            bar.pack_propagate(False)
            self._bars.append(bar)
        
        # dBm label
        self._dbm_label = ctk.CTkLabel(
            signal_frame,
            text="-100 dBm",
            font=(Fonts.MONO, Fonts.SIZE_XL, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        self._dbm_label.pack(side="right", padx=Layout.PADDING_SM)
        
        # Quality label
        self._quality_label = ctk.CTkLabel(
            self,
            text="No Signal",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED
        )
        self._quality_label.pack(padx=Layout.PADDING_SM, pady=(0, Layout.PADDING_SM))
    
    def set_signal(self, dbm: int):
        """
        Update signal strength display.
        
        Args:
            dbm: Signal strength in dBm (typically -30 to -100)
        """
        self._signal_dbm = dbm
        
        # Determine bars to light up
        if dbm >= -50:
            active_bars = 5
            color = Colors.SUCCESS
            quality = "Excellent"
        elif dbm >= -60:
            active_bars = 4
            color = Colors.SUCCESS
            quality = "Good"
        elif dbm >= -70:
            active_bars = 3
            color = Colors.WARNING
            quality = "Fair"
        elif dbm >= -80:
            active_bars = 2
            color = Colors.WARNING
            quality = "Weak"
        elif dbm >= -90:
            active_bars = 1
            color = Colors.ERROR
            quality = "Very Weak"
        else:
            active_bars = 0
            color = Colors.ERROR
            quality = "No Signal"
        
        # Update bars
        for i, bar in enumerate(self._bars):
            if i < active_bars:
                bar.configure(fg_color=color)
            else:
                bar.configure(fg_color=Colors.SURFACE_LIGHT)
        
        # Update labels
        self._dbm_label.configure(text=f"{dbm} dBm", text_color=color)
        self._quality_label.configure(text=quality, text_color=color)


class NetworkCard(ctk.CTkFrame):
    """
    Card widget displaying detailed network information.
    Shows SSID, signal, security type, channel, etc.
    """
    
    def __init__(
        self,
        parent,
        network: Optional[NetworkInfo] = None,
        on_connect: Optional[Callable[[NetworkInfo], None]] = None,
        on_analyze: Optional[Callable[[NetworkInfo], None]] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Layout.BORDER_RADIUS,
            border_width=1,
            border_color=Colors.BORDER,
            **kwargs
        )
        
        self._network = network
        self._on_connect = on_connect
        self._on_analyze = on_analyze
        self._selected = False
        
        self._create_ui()
        
        if network:
            self.update_network(network)
        
        # Bind hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _create_ui(self):
        """Create network card UI"""
        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=Layout.PADDING_MD, pady=Layout.PADDING_MD)
        
        # Top row: SSID and Signal
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")
        
        # SSID
        self._ssid_label = ctk.CTkLabel(
            top_row,
            text="Unknown Network",
            font=(Fonts.FAMILY, Fonts.SIZE_LG, "bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        self._ssid_label.pack(side="left", fill="x", expand=True)
        
        # Signal indicator (small bars)
        self._signal_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        self._signal_frame.pack(side="right")
        
        self._mini_bars = []
        for i, height in enumerate([6, 9, 12, 15]):
            bar = ctk.CTkFrame(
                self._signal_frame,
                width=4,
                height=height,
                fg_color=Colors.SURFACE_LIGHT,
                corner_radius=1
            )
            bar.pack(side="left", padx=1, anchor="s")
            bar.pack_propagate(False)
            self._mini_bars.append(bar)
        
        # Middle row: Details
        details_row = ctk.CTkFrame(content, fg_color="transparent")
        details_row.pack(fill="x", pady=(Layout.PADDING_SM, 0))
        
        # Security badge
        self._security_badge = ctk.CTkLabel(
            details_row,
            text="🔒 WPA2",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.TEXT_SECONDARY,
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=4,
            padx=8,
            pady=2
        )
        self._security_badge.pack(side="left")
        
        # Channel
        self._channel_label = ctk.CTkLabel(
            details_row,
            text="CH: --",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.TEXT_MUTED
        )
        self._channel_label.pack(side="left", padx=(Layout.PADDING_SM, 0))
        
        # Frequency
        self._freq_label = ctk.CTkLabel(
            details_row,
            text="2.4 GHz",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.TEXT_MUTED
        )
        self._freq_label.pack(side="left", padx=(Layout.PADDING_SM, 0))
        
        # dBm
        self._dbm_label = ctk.CTkLabel(
            details_row,
            text="-100 dBm",
            font=(Fonts.MONO, Fonts.SIZE_XS),
            text_color=Colors.TEXT_MUTED
        )
        self._dbm_label.pack(side="right")
        
        # Bottom row: BSSID and Actions
        bottom_row = ctk.CTkFrame(content, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(Layout.PADDING_SM, 0))
        
        # BSSID
        self._bssid_label = ctk.CTkLabel(
            bottom_row,
            text="BSSID: --:--:--:--:--:--",
            font=(Fonts.MONO, Fonts.SIZE_XS),
            text_color=Colors.TEXT_MUTED,
            anchor="w"
        )
        self._bssid_label.pack(side="left")
        
        # Action buttons frame
        actions = ctk.CTkFrame(bottom_row, fg_color="transparent")
        actions.pack(side="right")
        
        # Analyze button
        self._analyze_btn = ctk.CTkButton(
            actions,
            text="Analyze",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            width=60,
            height=24,
            fg_color="transparent",
            hover_color=Colors.SURFACE_LIGHT,
            text_color=Colors.PRIMARY,
            command=self._handle_analyze
        )
        self._analyze_btn.pack(side="left", padx=(0, 5))
        
        # Connect button
        self._connect_btn = ctk.CTkButton(
            actions,
            text="Connect",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            width=70,
            height=24,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            command=self._handle_connect
        )
        self._connect_btn.pack(side="left")
    
    def update_network(self, network: NetworkInfo):
        """Update card with network information"""
        self._network = network
        
        # Update SSID
        ssid_display = network.ssid if network.ssid else "<Hidden Network>"
        if network.is_connected:
            ssid_display = f"✓ {ssid_display}"
        self._ssid_label.configure(text=ssid_display)
        
        # Update signal bars
        signal = network.signal_strength
        if signal >= -50:
            active = 4
            color = Colors.SUCCESS
        elif signal >= -60:
            active = 3
            color = Colors.SUCCESS
        elif signal >= -70:
            active = 2
            color = Colors.WARNING
        elif signal >= -80:
            active = 1
            color = Colors.WARNING
        else:
            active = 0
            color = Colors.ERROR
        
        for i, bar in enumerate(self._mini_bars):
            bar.configure(fg_color=color if i < active else Colors.SURFACE_LIGHT)
        
        # Update security badge
        security_icons = {
            "WPA3": "🔐",
            "WPA2": "🔒",
            "WPA": "🔓",
            "WEP": "⚠️",
            "Open": "⚪",
        }
        icon = security_icons.get(network.security.split("-")[0] if "-" in network.security else network.security, "🔒")
        self._security_badge.configure(text=f"{icon} {network.security}")
        
        # Update other fields
        self._channel_label.configure(text=f"CH: {network.channel}")
        self._freq_label.configure(text=network.frequency)
        self._dbm_label.configure(text=f"{network.signal_strength} dBm", text_color=color)
        self._bssid_label.configure(text=f"BSSID: {network.bssid}")
        
        # Update connect button
        if network.is_connected:
            self._connect_btn.configure(
                text="Disconnect",
                fg_color=Colors.SURFACE_LIGHT,
                hover_color=Colors.ERROR
            )
            self.configure(border_color=Colors.SUCCESS)
        else:
            self._connect_btn.configure(
                text="Connect",
                fg_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY_HOVER
            )
            self.configure(border_color=Colors.BORDER)
    
    def _handle_connect(self):
        """Handle connect button click"""
        if self._on_connect and self._network:
            self._on_connect(self._network)
    
    def _handle_analyze(self):
        """Handle analyze button click"""
        if self._on_analyze and self._network:
            self._on_analyze(self._network)
    
    def _on_enter(self, event):
        """Mouse enter hover effect"""
        if not self._selected:
            self.configure(border_color=Colors.PRIMARY)
    
    def _on_leave(self, event):
        """Mouse leave hover effect"""
        if not self._selected:
            if self._network and self._network.is_connected:
                self.configure(border_color=Colors.SUCCESS)
            else:
                self.configure(border_color=Colors.BORDER)
    
    def set_selected(self, selected: bool):
        """Set card selection state"""
        self._selected = selected
        if selected:
            self.configure(border_color=Colors.PRIMARY, border_width=2)
        else:
            self.configure(border_color=Colors.BORDER, border_width=1)
    
    def get_network(self) -> Optional[NetworkInfo]:
        """Get the network info"""
        return self._network


class NetworkList(ctk.CTkScrollableFrame):
    """
    Scrollable list of NetworkCard widgets.
    Manages selection and filtering.
    """
    
    def __init__(
        self,
        parent,
        on_select: Optional[Callable[[NetworkInfo], None]] = None,
        on_connect: Optional[Callable[[NetworkInfo], None]] = None,
        on_analyze: Optional[Callable[[NetworkInfo], None]] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs
        )
        
        self._on_select = on_select
        self._on_connect = on_connect
        self._on_analyze = on_analyze
        self._cards: Dict[str, NetworkCard] = {}
        self._selected_bssid: Optional[str] = None
    
    def add_network(self, network: NetworkInfo):
        """Add a network to the list"""
        if network.bssid in self._cards:
            # Update existing card
            self._cards[network.bssid].update_network(network)
        else:
            # Create new card
            card = NetworkCard(
                self,
                network=network,
                on_connect=self._on_connect,
                on_analyze=self._on_analyze
            )
            card.pack(fill="x", pady=(0, Layout.PADDING_SM))
            card.bind("<Button-1>", lambda e, n=network: self._handle_select(n))
            self._cards[network.bssid] = card
    
    def update_networks(self, networks: list):
        """Update the entire network list"""
        # Get current BSSIDs
        current_bssids = set(self._cards.keys())
        new_bssids = {n.bssid for n in networks}
        
        # Remove old cards
        for bssid in current_bssids - new_bssids:
            self._cards[bssid].destroy()
            del self._cards[bssid]
        
        # Add/update networks
        for network in networks:
            self.add_network(network)
    
    def _handle_select(self, network: NetworkInfo):
        """Handle card selection"""
        # Deselect previous
        if self._selected_bssid and self._selected_bssid in self._cards:
            self._cards[self._selected_bssid].set_selected(False)
        
        # Select new
        self._selected_bssid = network.bssid
        self._cards[network.bssid].set_selected(True)
        
        if self._on_select:
            self._on_select(network)
    
    def clear(self):
        """Clear all networks"""
        for card in self._cards.values():
            card.destroy()
        self._cards.clear()
        self._selected_bssid = None
    
    def get_selected(self) -> Optional[NetworkInfo]:
        """Get currently selected network"""
        if self._selected_bssid and self._selected_bssid in self._cards:
            return self._cards[self._selected_bssid].get_network()
        return None


__all__ = ['SignalCard', 'NetworkCard', 'NetworkInfo', 'NetworkList']
