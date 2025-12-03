"""
WiFi Tester Pro v6.0 - Saved Passwords Dialog
View and manage saved WiFi passwords (Windows only)
"""

import customtkinter as ctk
from typing import Optional, Dict
import threading

from ..settings import Colors, Fonts, Layout, IS_WINDOWS, RUNNING_AS_ADMIN
from .utils import create_button, create_label, show_message


class PasswordRow(ctk.CTkFrame):
    """Single row displaying a saved WiFi profile and password"""
    
    def __init__(
        self,
        parent,
        profile_name: str,
        password: Optional[str] = None,
        driver=None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=8,
            height=50,
            **kwargs
        )
        
        self._profile_name = profile_name
        self._password = password
        self._password_visible = False
        self._driver = driver
        
        self.pack_propagate(False)
        self._create_ui()
    
    def _create_ui(self):
        """Create row UI"""
        # WiFi icon
        ctk.CTkLabel(
            self,
            text="📶",
            font=(Fonts.FAMILY, 16),
            width=40
        ).pack(side="left", padx=(10, 5))
        
        # Profile name
        ctk.CTkLabel(
            self,
            text=self._profile_name,
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.TEXT_PRIMARY,
            width=200,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Password display
        self._password_label = ctk.CTkLabel(
            self,
            text=self._get_password_display(),
            font=(Fonts.MONO, Fonts.SIZE_MD),
            text_color=Colors.TEXT_SECONDARY,
            width=200,
            anchor="w"
        )
        self._password_label.pack(side="left", padx=10)
        
        # Show/Hide button
        self._toggle_btn = ctk.CTkButton(
            self,
            text="👁",
            width=35,
            height=30,
            corner_radius=6,
            fg_color=Colors.SURFACE_LIGHT,
            hover_color=Colors.PRIMARY,
            text_color=Colors.TEXT_SECONDARY,
            command=self._toggle_password
        )
        self._toggle_btn.pack(side="right", padx=5)
        
        # Copy button
        self._copy_btn = ctk.CTkButton(
            self,
            text="📋",
            width=35,
            height=30,
            corner_radius=6,
            fg_color=Colors.SURFACE_LIGHT,
            hover_color=Colors.PRIMARY,
            text_color=Colors.TEXT_SECONDARY,
            command=self._copy_password
        )
        self._copy_btn.pack(side="right", padx=5)
        
        # Test Connection button
        self._test_btn = ctk.CTkButton(
            self,
            text="🔗",
            width=35,
            height=30,
            corner_radius=6,
            fg_color=Colors.SURFACE_LIGHT,
            hover_color=Colors.SUCCESS,
            text_color=Colors.TEXT_SECONDARY,
            command=self._test_connection
        )
        self._test_btn.pack(side="right", padx=5)
    
    def _get_password_display(self) -> str:
        """Get password display text"""
        if self._password is None:
            return "No password / Open network"
        elif self._password_visible:
            return self._password
        else:
            return "•" * min(len(self._password), 12)
    
    def _toggle_password(self):
        """Toggle password visibility"""
        self._password_visible = not self._password_visible
        self._password_label.configure(text=self._get_password_display())
        
        # Update button icon
        if self._password_visible:
            self._toggle_btn.configure(text="🔒")
        else:
            self._toggle_btn.configure(text="👁")
    
    def _copy_password(self):
        """Copy password to clipboard"""
        if self._password:
            try:
                self.clipboard_clear()
                self.clipboard_append(self._password)
                # Show brief feedback
                original_text = self._copy_btn.cget("text")
                self._copy_btn.configure(text="✓")
                self.after(1000, lambda: self._copy_btn.configure(text=original_text))
            except Exception as e:
                show_message("Error", f"Could not copy to clipboard: {e}", "error")
        else:
            show_message("Info", "No password to copy", "info")
    
    def _test_connection(self):
        """Test connection to this WiFi network"""
        # Show testing state
        self._test_btn.configure(text="⏳", state="disabled")
        self.update()
        
        def do_test():
            success = False
            message = ""
            
            try:
                if self._driver and hasattr(self._driver, 'connect'):
                    # Try to connect to the network
                    success = self._driver.connect(self._profile_name)
                    
                    if success:
                        # Verify connection
                        import time
                        time.sleep(2)  # Wait for connection to establish
                        
                        if hasattr(self._driver, 'get_current_connection'):
                            current = self._driver.get_current_connection()
                            if current and current.ssid == self._profile_name:
                                message = f"✅ Successfully connected to '{self._profile_name}'"
                            else:
                                message = f"⚠️ Connection initiated but not verified"
                        else:
                            message = f"✅ Connection command sent to '{self._profile_name}'"
                    else:
                        message = f"❌ Could not connect to '{self._profile_name}'"
                else:
                    message = "❌ Driver not available for connection test"
                    
            except Exception as e:
                message = f"❌ Error: {str(e)}"
            
            # Update UI on main thread
            self.after(0, lambda: self._show_test_result(success, message))
        
        # Run test in background thread
        thread = threading.Thread(target=do_test, daemon=True)
        thread.start()
    
    def _show_test_result(self, success: bool, message: str):
        """Show test result and restore button"""
        # Restore button
        self._test_btn.configure(
            text="✅" if success else "❌",
            state="normal"
        )
        
        # Show message
        msg_type = "info" if success else "warning"
        show_message("Connection Test", message, msg_type)
        
        # Restore original icon after delay
        self.after(2000, lambda: self._test_btn.configure(text="🔗"))


class SavedPasswordsDialog(ctk.CTkToplevel):
    """
    Dialog showing all saved WiFi passwords.
    Windows only - requires admin privileges for passwords.
    """
    
    def __init__(self, parent, driver=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self._driver = driver
        self._passwords: Dict[str, Optional[str]] = {}
        
        # Configure dialog
        self.title("Saved WiFi Passwords")
        self.geometry("600x500")
        self.resizable(False, True)
        self.configure(fg_color=Colors.BG_DARK)
        
        # Make modal
        self.transient(parent)
        
        # Center on parent
        self._center_on_parent(parent)
        
        self._create_ui()
        
        # Load passwords
        self.after(100, self._load_passwords)
        
        # Set up modal
        self.after(100, self._setup_modal)
    
    def _setup_modal(self):
        """Set up modal behavior"""
        try:
            self.grab_set()
            self.focus_force()
        except Exception:
            pass
    
    def _center_on_parent(self, parent):
        """Center dialog on parent window"""
        self.update_idletasks()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        dialog_w = 600
        dialog_h = 500
        
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        
        self.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")
    
    def _create_ui(self):
        """Create dialog UI"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header,
            text="🔑 Saved WiFi Passwords",
            font=(Fonts.FAMILY, 20, "bold"),
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left")
        
        # Refresh button
        create_button(
            header,
            text="Refresh",
            icon="🔄",
            style="ghost",
            width=100,
            command=self._load_passwords
        ).pack(side="right")
        
        # Warning/info banner
        if not IS_WINDOWS:
            self._create_banner(
                main_frame,
                "⚠️ This feature is only available on Windows",
                Colors.WARNING
            )
        elif not RUNNING_AS_ADMIN:
            self._create_banner(
                main_frame,
                "⚠️ Run as Administrator to view passwords",
                Colors.WARNING
            )
        
        # Scrollable list
        self._scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=12
        )
        self._scroll_frame.pack(fill="both", expand=True, pady=(10, 15))
        
        # Loading indicator
        self._loading_label = ctk.CTkLabel(
            self._scroll_frame,
            text="Loading saved networks...",
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.TEXT_MUTED
        )
        self._loading_label.pack(pady=50)
        
        # Footer
        footer = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer.pack(fill="x")
        
        # Close button
        create_button(
            footer,
            text="Close",
            style="primary",
            width=100,
            command=self.destroy
        ).pack(side="right")
        
        # Export button
        create_button(
            footer,
            text="Export All",
            icon="📄",
            style="secondary",
            width=120,
            command=self._export_passwords
        ).pack(side="left")
    
    def _create_banner(self, parent, text: str, color: str):
        """Create a warning/info banner"""
        banner = ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=8,
            height=40
        )
        banner.pack(fill="x", pady=(0, 10))
        banner.pack_propagate(False)
        
        ctk.CTkLabel(
            banner,
            text=text,
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_PRIMARY
        ).pack(pady=10)
    
    def _load_passwords(self):
        """Load saved passwords from driver"""
        # Clear existing
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        
        # Show loading
        self._loading_label = ctk.CTkLabel(
            self._scroll_frame,
            text="Loading saved networks...",
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            text_color=Colors.TEXT_MUTED
        )
        self._loading_label.pack(pady=50)
        
        # Load in background
        def load():
            if self._driver and hasattr(self._driver, 'get_all_saved_passwords'):
                self._passwords = self._driver.get_all_saved_passwords()
            elif self._driver and hasattr(self._driver, 'get_saved_profiles'):
                # Fallback: just get profile names
                profiles = self._driver.get_saved_profiles()
                self._passwords = {p: None for p in profiles}
            else:
                self._passwords = {}
            
            # Update UI on main thread
            self.after(0, self._display_passwords)
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def _display_passwords(self):
        """Display loaded passwords"""
        # Clear loading
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        
        if not self._passwords:
            ctk.CTkLabel(
                self._scroll_frame,
                text="No saved WiFi networks found",
                font=(Fonts.FAMILY, Fonts.SIZE_MD),
                text_color=Colors.TEXT_MUTED
            ).pack(pady=50)
            return
        
        # Sort by profile name
        sorted_profiles = sorted(self._passwords.keys())
        
        # Create rows
        for profile in sorted_profiles:
            password = self._passwords[profile]
            row = PasswordRow(
                self._scroll_frame,
                profile_name=profile,
                password=password,
                driver=self._driver
            )
            row.pack(fill="x", padx=5, pady=3)
    
    def _export_passwords(self):
        """Export all passwords to a file"""
        if not self._passwords:
            show_message("Info", "No passwords to export", "info")
            return
        
        try:
            from tkinter import filedialog
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export WiFi Passwords"
            )
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("WiFi Tester Pro - Saved Passwords Export\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for profile, password in sorted(self._passwords.items()):
                        f.write(f"Network: {profile}\n")
                        f.write(f"Password: {password or '(no password)'}\n")
                        f.write("-" * 30 + "\n")
                
                show_message("Success", f"Passwords exported to:\n{filepath}", "info")
        
        except Exception as e:
            show_message("Error", f"Export failed: {e}", "error")


__all__ = ['SavedPasswordsDialog', 'PasswordRow']
