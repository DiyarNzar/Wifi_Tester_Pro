"""
WiFi Tester Pro v6.0 - Navigation Frame
Sidebar navigation with icon buttons
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict

from ..settings import Colors, Fonts, Layout, APP_NAME, APP_VERSION
from .settings_dialog import SettingsDialog


class NavButton(ctk.CTkButton):
    """Custom navigation button with active state"""
    
    def __init__(
        self,
        master,
        text: str,
        icon: str = "",
        command: Optional[Callable] = None,
        **kwargs
    ):
        self._is_active = False
        self._icon = icon
        self._text = text
        
        super().__init__(
            master,
            text=f"  {icon}  {text}" if icon else f"  {text}",
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            anchor="w",
            height=45,
            corner_radius=8,
            fg_color="transparent",
            hover_color=Colors.SURFACE_LIGHT,
            text_color=Colors.TEXT_SECONDARY,
            command=command,
            **kwargs
        )
    
    def set_active(self, active: bool):
        """Set active state"""
        self._is_active = active
        if active:
            self.configure(
                fg_color=Colors.PRIMARY,
                text_color=Colors.TEXT_PRIMARY,
                hover_color=Colors.PRIMARY_HOVER
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=Colors.TEXT_SECONDARY,
                hover_color=Colors.SURFACE_LIGHT
            )


class NavigationFrame(ctk.CTkFrame):
    """
    Sidebar navigation frame.
    Contains app logo and navigation buttons.
    """
    
    # Navigation items: (name, display_text, icon)
    NAV_ITEMS = [
        ("dashboard", "Dashboard", "📊"),
        ("scanner", "Scanner", "📡"),
        ("auditor", "Auditor", "🔒"),
    ]
    
    def __init__(
        self,
        master,
        on_navigate: Optional[Callable[[str], None]] = None,
        width: int = 220,
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=0,
            **kwargs
        )
        
        self._on_navigate = on_navigate
        self._buttons: Dict[str, NavButton] = {}
        self._active_button: Optional[str] = None
        
        # Don't let frame shrink
        self.grid_propagate(False)
        
        self._create_header()
        self._create_navigation()
        self._create_footer()
    
    def _create_header(self):
        """Create app header with logo"""
        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=80
        )
        header_frame.pack(fill="x", padx=15, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # App icon/logo
        logo_label = ctk.CTkLabel(
            header_frame,
            text="📶",
            font=(Fonts.FAMILY, 32)
        )
        logo_label.pack(side="left")
        
        # App name
        name_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        name_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(
            name_frame,
            text=APP_NAME.split()[0],  # "WiFi"
            font=(Fonts.FAMILY, Fonts.SIZE_LG, "bold"),
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            name_frame,
            text=APP_NAME.split()[-1],  # "Pro"
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.PRIMARY
        ).pack(anchor="w")
        
        # Separator
        separator = ctk.CTkFrame(
            self,
            height=1,
            fg_color=Colors.BORDER
        )
        separator.pack(fill="x", padx=15, pady=10)
    
    def _create_navigation(self):
        """Create navigation buttons"""
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for name, display_text, icon in self.NAV_ITEMS:
            button = NavButton(
                nav_frame,
                text=display_text,
                icon=icon,
                command=lambda n=name: self._navigate(n)
            )
            button.pack(fill="x", pady=3)
            self._buttons[name] = button
    
    def _create_footer(self):
        """Create footer with version info"""
        footer_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=50
        )
        footer_frame.pack(fill="x", side="bottom", padx=15, pady=15)
        footer_frame.pack_propagate(False)
        
        # Version label
        ctk.CTkLabel(
            footer_frame,
            text=f"v{APP_VERSION}",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED
        ).pack(side="left")
        
        # Settings button (placeholder)
        settings_btn = ctk.CTkButton(
            footer_frame,
            text="⚙",
            width=35,
            height=35,
            corner_radius=8,
            fg_color="transparent",
            hover_color=Colors.SURFACE_LIGHT,
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, 16),
            command=self._open_settings
        )
        settings_btn.pack(side="right")
    
    def _navigate(self, page_name: str):
        """Handle navigation button click"""
        self.set_active(page_name)
        
        if self._on_navigate:
            self._on_navigate(page_name)
    
    def _open_settings(self):
        """Open settings dialog"""
        # Get the main window (root)
        root = self.winfo_toplevel()
        
        # Get session if available
        session = None
        if hasattr(root, '_session'):
            session = root._session
        
        # Open settings dialog
        SettingsDialog(root, session=session)
    
    def set_active(self, page_name: str):
        """Set the active navigation button"""
        # Deactivate previous button
        if self._active_button and self._active_button in self._buttons:
            self._buttons[self._active_button].set_active(False)
        
        # Activate new button
        if page_name in self._buttons:
            self._buttons[page_name].set_active(True)
            self._active_button = page_name


__all__ = ['NavigationFrame', 'NavButton']
