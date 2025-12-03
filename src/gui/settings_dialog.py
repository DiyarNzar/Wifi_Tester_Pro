"""
WiFi Tester Pro v6.0 - Settings Dialog
Application settings configuration dialog
"""

import customtkinter as ctk
from typing import Optional, Callable
import json
from pathlib import Path

from ..settings import (
    Colors, Fonts, Layout, CONFIG_PATH, 
    IS_KALI, IS_WINDOWS, APP_VERSION
)
from .utils import create_button, create_label, create_entry


class SettingsDialog(ctk.CTkToplevel):
    """
    Settings dialog for application configuration.
    """
    
    def __init__(
        self,
        parent,
        session=None,
        on_save: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self._session = session
        self._on_save = on_save
        self._settings = self._load_settings()
        
        # Configure dialog
        self.title("Settings")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG_DARK)
        
        # Make modal
        self.transient(parent)
        
        # Center on parent
        self._center_on_parent(parent)
        
        self._create_ui()
        
        # Wait for window to be ready, then grab focus
        self.after(100, self._setup_modal)
    
    def _setup_modal(self):
        """Set up modal behavior after window is visible"""
        try:
            self.grab_set()
            self.focus_force()
        except Exception:
            pass  # Window might have been closed
    
    def _center_on_parent(self, parent):
        """Center dialog on parent window"""
        self.update_idletasks()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        dialog_w = 500
        dialog_h = 600
        
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        
        self.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")
    
    def _load_settings(self) -> dict:
        """Load settings from config file"""
        config_file = CONFIG_PATH / "settings.json"
        default_settings = {
            "scan_timeout": 15,
            "auto_refresh": True,
            "refresh_interval": 30,
            "show_hidden_networks": True,
            "sound_enabled": False,
            "log_level": "INFO",
            "theme": "dark",
            "default_interface": "",
        }
        
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
        except Exception as e:
            print(f"[Settings] Error loading config: {e}")
        
        return default_settings
    
    def _save_settings(self):
        """Save settings to config file"""
        config_file = CONFIG_PATH / "settings.json"
        
        try:
            CONFIG_PATH.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
            print("[Settings] Configuration saved")
        except Exception as e:
            print(f"[Settings] Error saving config: {e}")
    
    def _create_ui(self):
        """Create dialog UI"""
        # Main container with padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text="⚙ Settings",
            font=(Fonts.FAMILY, 24, "bold"),
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=f"v{APP_VERSION}",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED
        ).pack(side="right")
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True)
        
        # ===== Scanning Settings =====
        self._create_section(scroll_frame, "📡 Scanning")
        
        # Scan timeout
        timeout_frame = self._create_setting_row(scroll_frame, "Scan Timeout (seconds)")
        self._timeout_var = ctk.StringVar(value=str(self._settings.get("scan_timeout", 15)))
        ctk.CTkEntry(
            timeout_frame,
            textvariable=self._timeout_var,
            width=80,
            fg_color=Colors.SURFACE_DARK,
            border_color=Colors.BORDER
        ).pack(side="right")
        
        # Show hidden networks
        hidden_frame = self._create_setting_row(scroll_frame, "Show Hidden Networks")
        self._hidden_var = ctk.BooleanVar(value=self._settings.get("show_hidden_networks", True))
        ctk.CTkSwitch(
            hidden_frame,
            text="",
            variable=self._hidden_var,
            onvalue=True,
            offvalue=False,
            fg_color=Colors.SURFACE_LIGHT,
            progress_color=Colors.PRIMARY
        ).pack(side="right")
        
        # Auto refresh
        refresh_frame = self._create_setting_row(scroll_frame, "Auto Refresh")
        self._refresh_var = ctk.BooleanVar(value=self._settings.get("auto_refresh", True))
        ctk.CTkSwitch(
            refresh_frame,
            text="",
            variable=self._refresh_var,
            onvalue=True,
            offvalue=False,
            fg_color=Colors.SURFACE_LIGHT,
            progress_color=Colors.PRIMARY
        ).pack(side="right")
        
        # Refresh interval
        interval_frame = self._create_setting_row(scroll_frame, "Refresh Interval (seconds)")
        self._interval_var = ctk.StringVar(value=str(self._settings.get("refresh_interval", 30)))
        ctk.CTkEntry(
            interval_frame,
            textvariable=self._interval_var,
            width=80,
            fg_color=Colors.SURFACE_DARK,
            border_color=Colors.BORDER
        ).pack(side="right")
        
        # ===== Interface Settings =====
        self._create_section(scroll_frame, "🔌 Interface")
        
        # Default interface
        iface_frame = self._create_setting_row(scroll_frame, "Default Interface")
        self._iface_var = ctk.StringVar(value=self._settings.get("default_interface", ""))
        
        # Get available interfaces
        interfaces = ["Auto"]
        if self._session and hasattr(self._session, 'interfaces'):
            interfaces.extend(self._session.interfaces)
        
        ctk.CTkOptionMenu(
            iface_frame,
            values=interfaces,
            variable=self._iface_var,
            width=150,
            fg_color=Colors.SURFACE_DARK,
            button_color=Colors.SURFACE_MEDIUM,
            button_hover_color=Colors.PRIMARY,
            dropdown_fg_color=Colors.SURFACE_DARK
        ).pack(side="right")
        
        # ===== Application Settings =====
        self._create_section(scroll_frame, "🎨 Application")
        
        # Theme
        theme_frame = self._create_setting_row(scroll_frame, "Theme")
        self._theme_var = ctk.StringVar(value=self._settings.get("theme", "dark"))
        ctk.CTkOptionMenu(
            theme_frame,
            values=["dark", "light", "system"],
            variable=self._theme_var,
            width=150,
            fg_color=Colors.SURFACE_DARK,
            button_color=Colors.SURFACE_MEDIUM,
            button_hover_color=Colors.PRIMARY,
            dropdown_fg_color=Colors.SURFACE_DARK
        ).pack(side="right")
        
        # Log level
        log_frame = self._create_setting_row(scroll_frame, "Log Level")
        self._log_var = ctk.StringVar(value=self._settings.get("log_level", "INFO"))
        ctk.CTkOptionMenu(
            log_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            variable=self._log_var,
            width=150,
            fg_color=Colors.SURFACE_DARK,
            button_color=Colors.SURFACE_MEDIUM,
            button_hover_color=Colors.PRIMARY,
            dropdown_fg_color=Colors.SURFACE_DARK
        ).pack(side="right")
        
        # Sound enabled
        sound_frame = self._create_setting_row(scroll_frame, "Sound Notifications")
        self._sound_var = ctk.BooleanVar(value=self._settings.get("sound_enabled", False))
        ctk.CTkSwitch(
            sound_frame,
            text="",
            variable=self._sound_var,
            onvalue=True,
            offvalue=False,
            fg_color=Colors.SURFACE_LIGHT,
            progress_color=Colors.PRIMARY
        ).pack(side="right")
        
        # ===== System Info =====
        self._create_section(scroll_frame, "ℹ️ System Info")
        
        info_frame = ctk.CTkFrame(scroll_frame, fg_color=Colors.SURFACE_DARK, corner_radius=8)
        info_frame.pack(fill="x", pady=5)
        
        platform_text = "Kali Linux" if IS_KALI else ("Windows" if IS_WINDOWS else "Linux")
        info_items = [
            ("Platform", platform_text),
            ("Version", APP_VERSION),
            ("Config Path", str(CONFIG_PATH)),
        ]
        
        for label, value in info_items:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=8)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=(Fonts.FAMILY, Fonts.SIZE_SM),
                text_color=Colors.TEXT_SECONDARY
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=(Fonts.MONO, Fonts.SIZE_SM),
                text_color=Colors.TEXT_PRIMARY
            ).pack(side="right")
        
        # ===== Buttons =====
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Cancel button
        create_button(
            button_frame,
            text="Cancel",
            style="ghost",
            width=100,
            command=self.destroy
        ).pack(side="left")
        
        # Reset button
        create_button(
            button_frame,
            text="Reset",
            style="secondary",
            width=100,
            command=self._reset_settings
        ).pack(side="left", padx=10)
        
        # Save button
        create_button(
            button_frame,
            text="Save",
            style="primary",
            width=100,
            command=self._apply_settings
        ).pack(side="right")
    
    def _create_section(self, parent, title: str):
        """Create a section header"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=(Fonts.FAMILY, Fonts.SIZE_MD, "bold"),
            text_color=Colors.PRIMARY
        ).pack(side="left")
        
        # Separator line
        ctk.CTkFrame(
            frame,
            height=1,
            fg_color=Colors.BORDER
        ).pack(side="left", fill="x", expand=True, padx=(15, 0))
    
    def _create_setting_row(self, parent, label: str) -> ctk.CTkFrame:
        """Create a setting row with label"""
        frame = ctk.CTkFrame(parent, fg_color="transparent", height=45)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left", pady=8)
        
        return frame
    
    def _apply_settings(self):
        """Apply and save settings"""
        try:
            # Update settings dict
            self._settings["scan_timeout"] = int(self._timeout_var.get())
            self._settings["show_hidden_networks"] = self._hidden_var.get()
            self._settings["auto_refresh"] = self._refresh_var.get()
            self._settings["refresh_interval"] = int(self._interval_var.get())
            self._settings["default_interface"] = self._iface_var.get()
            self._settings["theme"] = self._theme_var.get()
            self._settings["log_level"] = self._log_var.get()
            self._settings["sound_enabled"] = self._sound_var.get()
            
            # Save to file
            self._save_settings()
            
            # Apply theme change
            if self._theme_var.get() != "system":
                ctk.set_appearance_mode(self._theme_var.get())
            
            # Callback
            if self._on_save:
                self._on_save(self._settings)
            
            # Show confirmation
            from .utils import show_message
            show_message("Settings", "Settings saved successfully!", "info")
            
            self.destroy()
            
        except ValueError as e:
            from .utils import show_message
            show_message("Error", f"Invalid value: {e}", "error")
    
    def _reset_settings(self):
        """Reset to default settings"""
        from .utils import ask_confirmation
        
        if ask_confirmation("Reset Settings", "Reset all settings to default?"):
            # Reset to defaults
            self._timeout_var.set("15")
            self._hidden_var.set(True)
            self._refresh_var.set(True)
            self._interval_var.set("30")
            self._iface_var.set("Auto")
            self._theme_var.set("dark")
            self._log_var.set("INFO")
            self._sound_var.set(False)


__all__ = ['SettingsDialog']
