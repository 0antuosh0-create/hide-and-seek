#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           🔐 Hide and Seek v1.0                                 ║
║                     Image Steganography Application                           ║
║                                                                               ║
║    Hide secret messages inside images using LSB (Least Significant Bit)       ║
║    technique with optional AES-256 encryption for maximum security.           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import math
import base64
import subprocess
import json
import threading
import time
from pathlib import Path
from tkinter import filedialog
import tkinter as tk

# ═══════════════════════════════════════════════════════════════════════════════
#  AUTO-INSTALL DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════════
def ensure_package(name, pip_name=None):
    try:
        return __import__(name)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pip_name or name], check=False)
        return __import__(name)

ctk = ensure_package("customtkinter")
np = ensure_package("numpy")
ensure_package("PIL", "Pillow")
ensure_package("cryptography")



from PIL import Image, ImageTk
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import customtkinter as ctk

SETTINGS_DIR = Path.home() / ".hide_and_seek"


# ═══════════════════════════════════════════════════════════════════════════════
#  DESIGN TOKENS - Premium Dark Theme
# ═══════════════════════════════════════════════════════════════════════════════
class Theme:
    """Modern dark theme with green and purple accents"""
    
    # ── Backgrounds ──
    BG_DARK = "#0a0e14"          # Deepest background
    BG_PRIMARY = "#0d1117"        # Main background  
    BG_SECONDARY = "#151b23"      # Cards, elevated
    BG_TERTIARY = "#1c2430"       # Hover, inputs
    BG_ELEVATED = "#212a36"       # Active states
    
    # ── Borders ──
    BORDER = "#2a3441"            # Default borders
    BORDER_SUBTLE = "#1e2631"     # Subtle borders
    BORDER_HOVER = "#3d4a5c"      # Hover borders
    
    # ── Text ──
    TEXT_PRIMARY = "#f0f4f8"      # Primary text
    TEXT_SECONDARY = "#8b99a8"    # Secondary text  
    TEXT_MUTED = "#5c6b7a"        # Muted text
    TEXT_DISABLED = "#3d4a5c"     # Disabled text
    
    # ── Accents ──
    ACCENT_GREEN = "#22c55e"      # Primary action, success
    ACCENT_GREEN_HOVER = "#16a34a"
    ACCENT_GREEN_GLOW = "#22c55e30"
    
    ACCENT_PURPLE = "#a855f7"     # Secondary action
    ACCENT_PURPLE_HOVER = "#9333ea"
    ACCENT_PURPLE_GLOW = "#a855f720"
    
    ACCENT_BLUE = "#3b82f6"       # Links, info
    ACCENT_BLUE_HOVER = "#2563eb"
    
    ACCENT_YELLOW = "#eab308"     # Warning
    ACCENT_RED = "#ef4444"        # Error, danger
    
    # ── Sidebar ──
    SIDEBAR_BG = "#0a0d12"
    SIDEBAR_ITEM_HOVER = "#151b23"
    SIDEBAR_ITEM_ACTIVE = "#1c2430"
    
    # ── Gradients (for special elements) ──
    GRADIENT_START = "#22c55e"
    GRADIENT_END = "#a855f7"



# ═══════════════════════════════════════════════════════════════════════════════
#  ANIMATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
class Animate:
    """Smooth animation utilities with easing"""
    
    @staticmethod
    def ease_out_expo(t):
        return 1 if t == 1 else 1 - pow(2, -10 * t)
    
    @staticmethod
    def ease_out_cubic(t):
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_out_back(t):
        c1, c3 = 1.70158, 2.70158
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    @staticmethod
    def ease_in_out_cubic(t):
        return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def lerp(a, b, t):
        return a + (b - a) * t
    
    @staticmethod
    def animate(root, duration_ms, on_update, on_complete=None, easing=None):
        """Generic animation with callbacks"""
        if easing is None:
            easing = Animate.ease_out_cubic
        
        fps, start_time = 60, [None]
        step_ms = 1000 // fps
        
        def step():
            if start_time[0] is None:
                start_time[0] = time.time() * 1000
            
            elapsed = time.time() * 1000 - start_time[0]
            t = min(elapsed / duration_ms, 1.0)
            eased = easing(t)
            
            try:
                on_update(eased)
            except Exception:
                return
            
            if t < 1.0:
                root.after(step_ms, step)
            elif on_complete:
                on_complete()
        
        step()
    
    @staticmethod
    def progress(root, bar, target, duration=400):
        """Animate progress bar"""
        try:
            start = bar.get()
        except Exception:
            start = 0
        
        def update(t):
            try:
                bar.set(Animate.lerp(start, target, t))
            except Exception:
                pass
        
        Animate.animate(root, duration, update)
    
    @staticmethod
    def pulse_border(root, widget, color1, color2, duration=1000, cycles=2):
        """Pulse border color"""
        def hex_to_rgb(h):
            h = h.lstrip("#")
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"
        
        c1, c2 = hex_to_rgb(color1), hex_to_rgb(color2)

        step_count = [0]
        total = 40 * cycles
        
        def smooth_step():
            t = step_count[0] / total
            phase = t * cycles * 2 * 3.14159
            blend = (math.sin(phase) + 1) / 2
            
            rgb = tuple(Animate.lerp(c1[i], c2[i], blend) for i in range(3))
            try:
                widget.configure(border_color=rgb_to_hex(rgb))
            except Exception:
                return
            
            step_count[0] += 1
            if step_count[0] <= total:
                root.after(duration // total, smooth_step)
            else:
                try:
                    widget.configure(border_color=color1)
                except Exception:
                    pass
        
        smooth_step()
    
    @staticmethod  
    def typewriter(root, label, text, delay=25):
        """Typewriter text effect"""
        idx = [0]
        def step():
            if idx[0] <= len(text):
                try:
                    label.configure(text=text[:idx[0]])
                except Exception:
                    return
                idx[0] += 1
                root.after(delay, step)
        step()


# ═══════════════════════════════════════════════════════════════════════════════
#  STEGANOGRAPHY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
MAGIC = b"STEG"
SALT_LEN = 16

class Stego:
    """LSB Steganography with AES encryption"""

    @staticmethod
    def _key(password, salt):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def _encrypt(msg, pwd):
        salt = os.urandom(SALT_LEN)
        token = Fernet(Stego._key(pwd, salt)).encrypt(msg.encode())
        return salt, token

    @staticmethod
    def _decrypt(data, pwd, salt):
        return Fernet(Stego._key(pwd, salt)).decrypt(data).decode()
    
    @staticmethod
    def _to_bits(data):
        return "".join(f"{b:08b}" for b in data)
    
    @staticmethod
    def _from_bits(bits):
        return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    
    @staticmethod
    def capacity(w, h):
        return max(0, (w * h * 3 - 200) // 8)
    
    @staticmethod
    def encode(path, msg, pwd=None, progress=None):
        if progress: progress(0.05)
        
        img = Image.open(path).convert("RGB")
        px = np.array(img, dtype=np.uint8)
        h, w = px.shape[:2]
        
        if progress: progress(0.15)
        
        if pwd:
            salt, payload = Stego._encrypt(msg, pwd)
            flag = 0xFF
        else:
            salt = b"\x00" * SALT_LEN
            payload = msg.encode()
            flag = 0x00

        bits = (
            Stego._to_bits(MAGIC)
            + f"{flag:08b}"
            + Stego._to_bits(salt)
            + f"{len(payload):032b}"
            + Stego._to_bits(payload)
        )
        
        if len(bits) > w * h * 3:
            raise ValueError(f"Message too large! Max: {Stego.capacity(w, h):,} bytes")
        
        if progress: progress(0.35)
        
        flat = px.reshape(-1)
        bit_arr = np.array([int(b) for b in bits], dtype=np.uint8)
        flat[:len(bit_arr)] = (flat[:len(bit_arr)] & 0xFE) | bit_arr
        
        if progress: progress(0.85)
        
        result = Image.fromarray(flat.reshape(h, w, 3), "RGB")
        if progress: progress(1.0)
        return result
    
    @staticmethod
    def decode(path, pwd=None, progress=None):
        if progress: progress(0.1)
        
        img = Image.open(path).convert("RGB")
        flat = np.array(img, dtype=np.uint8).reshape(-1)
        
        def extract(n):
            return "".join(str(b & 1) for b in flat[:n])
        
        if progress: progress(0.25)
        
        if Stego._from_bits(extract(32)) != MAGIC:
            raise ValueError("No hidden data found")

        if progress: progress(0.4)

        header = extract(200)
        encrypted = int(header[32:40], 2) == 0xFF
        salt = Stego._from_bits(header[40:168])
        length = int(header[168:200], 2)

        if length <= 0 or length > (len(flat) - 200) // 8:
            raise ValueError("No hidden data found")

        if progress: progress(0.6)

        data = Stego._from_bits(extract(200 + length * 8)[200:])
        
        if progress: progress(0.8)
        
        if encrypted:
            if not pwd:
                raise ValueError("ENCRYPTED")
            try:
                result = Stego._decrypt(data, pwd, salt)
            except Exception:
                raise ValueError("Wrong password")
        else:
            result = data.decode()
        
        if progress: progress(1.0)
        return result
    
    @staticmethod
    def compare(path, encoded):
        orig = np.array(Image.open(path).convert("RGB"), dtype=np.float64)
        enc = np.array(encoded.convert("RGB"), dtype=np.float64)
        diff = np.abs(orig - enc)
        amp = np.clip(diff * 50, 0, 255).astype(np.uint8)
        mse = np.mean(diff ** 2)
        psnr = float("inf") if mse == 0 else 10 * math.log10(255**2 / mse)
        return Image.fromarray(amp, "RGB"), psnr
    
    @staticmethod
    def risk(msg_len, w, h):
        return (msg_len * 8 + 72) / (w * h * 3) * 100 if w * h > 0 else 100


# ═══════════════════════════════════════════════════════════════════════════════
#  ICON SYSTEM (Unicode-based)
# ═══════════════════════════════════════════════════════════════════════════════
class Icons:
    # Navigation
    ENCODE = "🔒"
    DECODE = "🔓"
    SETTINGS = "⚙️"
    
    # Actions
    UPLOAD = "📁"
    SAVE = "💾"
    COPY = "📋"
    COMPARE = "🔍"
    
    # Status
    SUCCESS = "✓"
    # ERROR = "✗"
    # WARNING = "⚠"
    INFO = "ℹ"
    
    # UI
    # LOCK = "🔐"
    KEY = "🔑"
    IMAGE = "🖼"
    MESSAGE = "✉"
    SHIELD = "🛡"
    EYE = "👁"
    EYE_OFF = "🙈"
    # MOON = "🌙"
    # SUN = "☀"
    # CHECK = "✓"
    # ARROW = "→"


# ═══════════════════════════════════════════════════════════════════════════════
#  CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════
class GlowButton(ctk.CTkButton):
    """Button with subtle glow effect on hover"""
    
    def __init__(self, master, glow_color=None, **kwargs):
        self.glow_color = glow_color or Theme.ACCENT_GREEN_GLOW
        super().__init__(master, **kwargs)


class Card(ctk.CTkFrame):
    """Styled card component with header"""
    
    def __init__(self, master, title="", icon="", subtitle="", **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=16,
            border_width=1,
            border_color=Theme.BORDER,
            **kwargs
        )
        
        if title:
            header = ctk.CTkFrame(self, fg_color="transparent")
            header.pack(fill="x", padx=24, pady=(20, 16))
            
            title_frame = ctk.CTkFrame(header, fg_color="transparent")
            title_frame.pack(side="left")
            
            if icon:
                ctk.CTkLabel(
                    title_frame,
                    text=icon,
                    font=ctk.CTkFont(size=20),
                    text_color=Theme.TEXT_PRIMARY,
                ).pack(side="left", padx=(0, 10))
            
            ctk.CTkLabel(
                title_frame,
                text=title,
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                text_color=Theme.TEXT_PRIMARY,
            ).pack(side="left")
            
            if subtitle:
                ctk.CTkLabel(
                    title_frame,
                    text=f"  •  {subtitle}",
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color=Theme.TEXT_MUTED,
                ).pack(side="left")


class InfoRow(ctk.CTkFrame):
    """Info row with label and value"""
    
    def __init__(self, master, label, value, badge=None, badge_color=None):
        super().__init__(master, fg_color=Theme.BG_TERTIARY, corner_radius=10, height=40)
        self.pack_propagate(False)
        
        ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Theme.TEXT_SECONDARY,
        ).pack(side="left", padx=14, pady=10)
        
        if badge:
            ctk.CTkLabel(
                self,
                text=badge,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=badge_color or Theme.ACCENT_GREEN,
            ).pack(side="right", padx=(0, 10))
        
        ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
        ).pack(side="right", padx=14, pady=10)


class DropZone(ctk.CTkFrame):
    """Drag & drop style file selector"""

    def __init__(self, master, icon="📁", text="Click to select", subtext="", command=None, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_PRIMARY,
            corner_radius=12,
            border_width=2,
            border_color=Theme.BORDER,
            **kwargs
        )

        self.command = command
        self.default_border = Theme.BORDER
        self.hover_border = Theme.BORDER_HOVER
        self._icon = icon
        self._text = text
        self._subtext = subtext
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.place(relx=0.5, rely=0.5, anchor="center")
        
        self.icon_label = ctk.CTkLabel(
            self.content,
            text=icon,
            font=ctk.CTkFont(size=42),
            text_color=Theme.TEXT_MUTED,
        )
        self.icon_label.pack()
        
        self.text_label = ctk.CTkLabel(
            self.content,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=Theme.TEXT_SECONDARY,
        )
        self.text_label.pack(pady=(10, 4))
        
        if subtext:
            self.sub_label = ctk.CTkLabel(
                self.content,
                text=subtext,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=Theme.TEXT_MUTED,
            )
            self.sub_label.pack()
        
        # Bindings
        for w in [self, self.content, self.icon_label, self.text_label]:
            w.bind("<Button-1>", lambda e: self._click())
            w.bind("<Enter>", lambda e: self._hover(True))
            w.bind("<Leave>", lambda e: self._hover(False))



class SteganoHide(ctk.CTk):
    """Hide and Seek - Modern Image Steganography Application"""
    
    def __init__(self):
        super().__init__()
        # Window
        self.title("Hide and Seek")
        self.geometry("1100x780")
        self.minsize(1000, 700)
        self.configure(fg_color=Theme.BG_DARK)
        
        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1100) // 2
        y = (self.winfo_screenheight() - 780) // 2
        self.geometry(f"1100x780+{x}+{y}")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Fonts
        self.fonts = {
            "h1": ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            "h2": ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            "h3": ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            "body": ctk.CTkFont(family="Segoe UI", size=13),
            "small": ctk.CTkFont(family="Segoe UI", size=11),
            "tiny": ctk.CTkFont(family="Segoe UI", size=10),
            "mono": ctk.CTkFont(family="Consolas", size=12),
        }
        
        # State
        self.current_view = "encode"
        self.image_path = None
        self.image_info = None
        self.encoded_img = None
        self.decode_path = None
        self.preview_photo = None
        self.decode_photo = None
        self.export_format = "PNG"
        
        # Settings
        settings = self._load_settings()
        if settings.get("export_format"):
            self.export_format = settings["export_format"]
        
        # Build UI
        self._build_layout()
        
        # Restore settings
        if settings.get("export_format") and hasattr(self, "format_menu"):
            self.format_menu.set(self.export_format)
            if hasattr(self, "save_btn"):
                self.save_btn.configure(text=f"{Icons.SAVE}  Save as {self.export_format}")
        
        # Keyboard Shortcuts
        self.bind("<Control-o>", lambda e: (self._select_image(), "break")[-1])
        self.bind("<Control-s>", lambda e: (self._save_current(), "break")[-1])
        self.bind("<Control-e>", lambda e: (self._encode(), "break")[-1])
        self.bind("<Control-d>", lambda e: (self._decode(), "break")[-1])
        self.bind("<Escape>", lambda e: (self._clear_current(), "break")[-1])
        self.bind("<Control-v>", lambda e: (self._paste_image(), "break")[-1])
        
        # Save settings on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)


    #  LAYOUT
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ── Sidebar ──
        self._build_sidebar()
        
        # ── Main Content ──
        self.main_frame = ctk.CTkFrame(self, fg_color=Theme.BG_PRIMARY, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        self._build_header()
        
        # Content area
        self.content = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color=Theme.BG_PRIMARY,
            scrollbar_button_color=Theme.BORDER,
            scrollbar_button_hover_color=Theme.BORDER_HOVER,
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.content.grid_columnconfigure(0, weight=1)
        
        # Build views
        self.encode_view = self._build_encode_view()
        self.decode_view = self._build_decode_view()
        self.settings_view = self._build_settings_view()
        
        # Show default
        self._show_view("encode")
        
        # Footer
        self._build_footer()
        
        # Save settings on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color=Theme.SIDEBAR_BG,
            corner_radius=0,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(4, weight=1)
        
        # Logo
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(28, 32))
        
        ctk.CTkLabel(
            logo_frame,
            text="🔐",
            font=ctk.CTkFont(size=32),
            text_color=Theme.ACCENT_GREEN,
        ).pack(side="left", padx=(0, 12))
        
        title_box = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_box.pack(side="left")
        
        ctk.CTkLabel(
            title_box,
            text="Hide and Seek",
            font=self.fonts["h2"],
            text_color=Theme.TEXT_PRIMARY,
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_box,
            text="Image Steganography",
            font=self.fonts["tiny"],
            text_color=Theme.TEXT_MUTED,
        ).pack(anchor="w")
        
        # Section label
        ctk.CTkLabel(
            sidebar,
            text="NAVIGATION",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=Theme.TEXT_DISABLED,
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 12))
        
        # Nav items
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.grid(row=2, column=0, sticky="ew", padx=12)
        
        self.nav_buttons = {}
        
        for idx, (key, icon, label) in enumerate([
            ("encode", Icons.ENCODE, "Hide"),
            ("decode", Icons.DECODE, "Seek"),
            ("settings", Icons.SETTINGS, "About"),
        ]):
            btn = ctk.CTkButton(
                nav_frame,
                text=f"  {icon}   {label}",
                font=self.fonts["body"],
                height=44,
                corner_radius=10,
                anchor="w",
                fg_color="transparent",
                hover_color=Theme.SIDEBAR_ITEM_HOVER,
                text_color=Theme.TEXT_SECONDARY,
                command=lambda k=key: self._show_view(k),
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn
        
        # Recent section
        ctk.CTkLabel(
            sidebar,
            text="RECENT",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=Theme.TEXT_DISABLED,
        ).grid(row=3, column=0, sticky="w", padx=24, pady=(12, 4))

        self.recent_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.recent_frame.grid(row=4, column=0, sticky="ew", padx=12)
        self._build_recent_list()

        # Bottom section
        bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom.grid(row=5, column=0, sticky="sew", padx=12, pady=12)



        # Clear history
        ctk.CTkButton(
            bottom,
            text="Clear History",
            font=self.fonts["tiny"],
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color=Theme.SIDEBAR_ITEM_HOVER,
            text_color=Theme.TEXT_DISABLED,
            command=self._clear_history,
        ).pack(pady=(4, 4))

        # Version
        ctk.CTkLabel(
            bottom,
            text="v1.0.0",
            font=self.fonts["tiny"],
            text_color=Theme.TEXT_DISABLED,
        ).pack(pady=(0, 8))
        
        # Exit button
        ctk.CTkButton(
            bottom,
            text="Exit",
            font=self.fonts["small"],
            height=32,
            corner_radius=8,
            fg_color=Theme.ACCENT_RED,
            hover_color="#dc2626",
            text_color="#ffffff",
            command=self._on_close,
        ).pack(fill="x")
    
    def _build_header(self):
        header = ctk.CTkFrame(self.main_frame, fg_color=Theme.BG_PRIMARY, height=72)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        
        # Title (will be updated based on view)
        self.header_title = ctk.CTkLabel(
            header,
            text="",
            font=self.fonts["h1"],
            text_color=Theme.TEXT_PRIMARY,
        )
        self.header_title.grid(row=0, column=0, sticky="w", padx=40, pady=20)
        
        # Separator
        sep = ctk.CTkFrame(header, fg_color=Theme.BORDER, height=1)
        sep.place(x=0, rely=1, relwidth=1, anchor="sw")
    
    def _build_footer(self):
        footer = ctk.CTkFrame(self.main_frame, fg_color=Theme.BG_SECONDARY, height=44, corner_radius=0)
        footer.grid(row=2, column=0, sticky="sew")
        footer.grid_propagate(False)
        
        ctk.CTkLabel(
            footer,
            text="🔒  All processing happens locally • Your data never leaves your computer",
            font=self.fonts["small"],
            text_color=Theme.TEXT_MUTED,
        ).place(relx=0.5, rely=0.5, anchor="center")
    
    def _menu_cut(self):
        try:
            sel = self.msg_textbox.tag_ranges("sel")
            if sel:
                text = self.msg_textbox.get("sel.first", "sel.last")
                self.clipboard_clear()
                self.clipboard_append(text)
                self.msg_textbox.delete("sel.first", "sel.last")
        except Exception:
            pass

    def _menu_copy(self):
        try:
            sel = self.msg_textbox.tag_ranges("sel")
            if sel:
                text = self.msg_textbox.get("sel.first", "sel.last")
                self.clipboard_clear()
                self.clipboard_append(text)
        except Exception:
            pass

    def _menu_paste(self):
        try:
            text = self.clipboard_get()
            if text:
                self.msg_textbox.insert("insert", text)
        except Exception:
            pass

    def _menu_select_all(self):
        self.msg_textbox.tag_add("sel", "1.0", "end")

    # ═══════════════════════════════════════════════════════════════════════════
    #  ENCODE VIEW
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_encode_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        
        # Two columns
        cols = ctk.CTkFrame(view, fg_color="transparent")
        cols.pack(fill="x", padx=40, pady=(24, 0))
        cols.grid_columnconfigure((0, 1), weight=1, uniform="col")
        
        # ── Left: Image ──
        left = Card(cols, title="Select Image", icon=Icons.IMAGE)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 20))
        
        self.enc_dropzone = DropZone(
            left,
            icon=Icons.UPLOAD,
            text="Click to select an image",
            subtext="PNG, BMP, TIFF, WebP supported",
            command=self._select_image,
            height=180,
        )
        self.enc_dropzone.pack(fill="x", padx=24, pady=(0, 16))
        
        self.enc_browse = ctk.CTkButton(
            left,
            text="Browse Files",
            font=self.fonts["body"],
            height=42,
            corner_radius=10,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BORDER,
            command=self._select_image,
        )
        self.enc_browse.pack(fill="x", padx=24, pady=(0, 24))
        
        # ── Right: Info ──
        right = Card(cols, title="Image Details", icon=Icons.INFO)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=(0, 20))
        
        self.info_container = ctk.CTkFrame(right, fg_color="transparent")
        self.info_container.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        
        self.info_placeholder = ctk.CTkLabel(
            self.info_container,
            text="No image selected",
            font=self.fonts["body"],
            text_color=Theme.TEXT_MUTED,
        )
        self.info_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
        self.info_rows_frame = ctk.CTkFrame(self.info_container, fg_color="transparent")
        
        # ── Message ──
        msg_card = Card(view, title="Secret Message", icon=Icons.MESSAGE)
        msg_card.pack(fill="x", padx=40, pady=(0, 20))
        
        msg_header = ctk.CTkFrame(msg_card, fg_color="transparent")
        msg_header.pack(fill="x", padx=24, pady=(0, 8))
        
        ctk.CTkLabel(
            msg_header,
            text="Enter the text you want to hide:",
            font=self.fonts["small"],
            text_color=Theme.TEXT_SECONDARY,
        ).pack(side="left")
        
        self.char_counter = ctk.CTkLabel(
            msg_header,
            text="0 bytes",
            font=self.fonts["small"],
            text_color=Theme.TEXT_MUTED,
        )
        self.char_counter.pack(side="right")
        
        self.msg_textbox = ctk.CTkTextbox(
            msg_card,
            height=120,
            corner_radius=12,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BORDER,
            font=self.fonts["body"],
            wrap="word",
        )
        self.msg_textbox.pack(fill="x", padx=24, pady=(0, 24))
        self.msg_textbox.bind("<KeyRelease>", self._on_msg_change)
        
        # Right-click context menu
        self.msg_menu = tk.Menu(self.msg_textbox, tearoff=0, bg=Theme.BG_ELEVATED, fg=Theme.TEXT_PRIMARY,
                                activebackground=Theme.BG_TERTIARY, activeforeground=Theme.TEXT_PRIMARY,
                                font=("Segoe UI", 11))
        self.msg_menu.add_command(label="Cut", command=self._menu_cut)
        self.msg_menu.add_command(label="Copy", command=self._menu_copy)
        self.msg_menu.add_command(label="Paste", command=self._menu_paste)
        self.msg_menu.add_separator()
        self.msg_menu.add_command(label="Select All", command=self._menu_select_all)
        self.msg_textbox.bind("<Button-3>", lambda e: self.msg_menu.tk_popup(e.x_root, e.y_root))
        
        # ── Password ──
        pwd_card = Card(view, title="Encryption", icon=Icons.KEY, subtitle="Optional")
        pwd_card.pack(fill="x", padx=40, pady=(0, 20))
        
        pwd_frame = ctk.CTkFrame(pwd_card, fg_color="transparent")
        pwd_frame.pack(fill="x", padx=24, pady=(0, 24))
        
        self.enc_pwd_entry = ctk.CTkEntry(
            pwd_frame,
            height=46,
            corner_radius=12,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BORDER,
            font=self.fonts["body"],
            placeholder_text="Enter password (leave empty for no encryption)",
            show="●",
        )
        self.enc_pwd_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.enc_pwd_btn = ctk.CTkButton(
            pwd_frame,
            text=Icons.EYE,
            width=46,
            height=46,
            corner_radius=12,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=16),
            command=self._toggle_enc_pwd,
        )
        self.enc_pwd_btn.pack(side="right", padx=(10, 0))
        
        self.save_pwd_btn = ctk.CTkButton(
            pwd_frame,
            text=Icons.SAVE,
            width=46,
            height=46,
            corner_radius=12,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=16),
            command=self._save_pwd_dialog,
        )
        self.save_pwd_btn.pack(side="right", padx=(0, 0))
        self.enc_pwd_visible = False
        
        # ── Risk Meter ──
        risk_card = Card(view, title="Detection Risk", icon=Icons.SHIELD)
        risk_card.pack(fill="x", padx=40, pady=(0, 20))
        
        risk_inner = ctk.CTkFrame(risk_card, fg_color="transparent")
        risk_inner.pack(fill="x", padx=24, pady=(0, 24))
        
        risk_header = ctk.CTkFrame(risk_inner, fg_color="transparent")
        risk_header.pack(fill="x", pady=(0, 10))
        
        self.risk_pct = ctk.CTkLabel(
            risk_header,
            text="—",
            font=self.fonts["h3"],
            text_color=Theme.TEXT_MUTED,
        )
        self.risk_pct.pack(side="left")
        
        self.risk_level = ctk.CTkLabel(
            risk_header,
            text="",
            font=self.fonts["small"],
            text_color=Theme.TEXT_MUTED,
        )
        self.risk_level.pack(side="right")
        
        self.risk_bar = ctk.CTkProgressBar(
            risk_inner,
            height=10,
            corner_radius=5,
            fg_color=Theme.BG_PRIMARY,
            progress_color=Theme.ACCENT_GREEN,
        )
        self.risk_bar.pack(fill="x")
        self.risk_bar.set(0)
        
        # ── Action Buttons ──
        enc_btns = ctk.CTkFrame(view, fg_color="transparent")
        enc_btns.pack(fill="x", padx=40, pady=(0, 16))
        enc_btns.grid_columnconfigure(0, weight=3)
        enc_btns.grid_columnconfigure(1, weight=1)
        enc_btns.grid_columnconfigure(2, weight=1)

        self.encode_btn = ctk.CTkButton(
            enc_btns,
            text=f"{Icons.ENCODE}   Hide",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            height=56,
            corner_radius=14,
            fg_color=Theme.ACCENT_GREEN,
            hover_color=Theme.ACCENT_GREEN_HOVER,
            text_color="#ffffff",
            command=self._encode,
        )
        self.encode_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.batch_encode_btn = ctk.CTkButton(
            enc_btns,
            text="Batch...",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            height=56,
            corner_radius=14,
            fg_color=Theme.ACCENT_BLUE,
            hover_color=Theme.ACCENT_BLUE_HOVER,
            text_color="#ffffff",
            command=self._batch_encode,
        )
        self.batch_encode_btn.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        self.clear_encode_btn = ctk.CTkButton(
            enc_btns,
            text="Clear",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            height=56,
            corner_radius=14,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_SECONDARY,
            border_width=1,
            border_color=Theme.BORDER,
            command=self._clear_encode,
        )
        self.clear_encode_btn.grid(row=0, column=2, sticky="ew")
        
        # Progress
        self.enc_progress = ctk.CTkProgressBar(
            view,
            height=6,
            corner_radius=3,
            fg_color=Theme.BG_SECONDARY,
            progress_color=Theme.ACCENT_GREEN,
        )
        self.enc_progress.pack(fill="x", padx=40, pady=(0, 8))
        self.enc_progress.set(0)
        
        self.enc_status = ctk.CTkLabel(
            view,
            text="",
            font=self.fonts["small"],
            text_color=Theme.TEXT_SECONDARY,
        )
        self.enc_status.pack(anchor="w", padx=40)
        
        # ── Result Card ──
        self.enc_result = ctk.CTkFrame(
            view,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=16,
            border_width=2,
            border_color=Theme.ACCENT_GREEN,
        )
        
        res_header = ctk.CTkFrame(self.enc_result, fg_color="transparent")
        res_header.pack(fill="x", padx=24, pady=(20, 16))
        
        ctk.CTkLabel(
            res_header,
            text=f"{Icons.SUCCESS}  Success!",
            font=self.fonts["h3"],
            text_color=Theme.ACCENT_GREEN,
        ).pack(side="left")
        
        res_btns = ctk.CTkFrame(self.enc_result, fg_color="transparent")
        res_btns.pack(fill="x", padx=24, pady=(0, 24))
        res_btns.grid_columnconfigure(1, weight=1)
        res_btns.grid_columnconfigure(2, weight=1)

        self.format_menu = ctk.CTkOptionMenu(
            res_btns,
            values=["PNG", "BMP", "TIFF"],
            font=self.fonts["body"],
            height=46,
            corner_radius=12,
            fg_color=Theme.BG_TERTIARY,
            button_color=Theme.BORDER,
            button_hover_color=Theme.BORDER_HOVER,
            dropdown_fg_color=Theme.BG_SECONDARY,
            command=self._on_format_change,
        )
        self.format_menu.grid(row=0, column=0, padx=(0, 8))
        self.format_menu.set("PNG")

        self.save_btn = ctk.CTkButton(
            res_btns,
            text=f"{Icons.SAVE}  Save as PNG",
            font=self.fonts["body"],
            height=46,
            corner_radius=12,
            fg_color=Theme.ACCENT_BLUE,
            hover_color=Theme.ACCENT_BLUE_HOVER,
            text_color="#ffffff",
            command=self._save_encoded,
        )
        self.save_btn.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            res_btns,
            text=f"{Icons.COMPARE}  Compare",
            font=self.fonts["body"],
            height=46,
            corner_radius=12,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BORDER,
            command=self._show_compare,
        ).grid(row=0, column=2, sticky="ew")
        
        return view
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  DECODE VIEW
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_decode_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")
        
        # ── Image ──
        img_card = Card(view, title="Select Encoded Image", icon=Icons.DECODE)
        img_card.pack(fill="x", padx=40, pady=(24, 20))
        
        self.dec_dropzone = DropZone(
            img_card,
            icon="🔍",
            text="Click to select encoded image",
            subtext="Select an image with hidden data",
            command=self._select_decode_image,
            height=180,
        )
        self.dec_dropzone.pack(fill="x", padx=24, pady=(0, 16))
        
        self.dec_info_container = ctk.CTkFrame(img_card, fg_color="transparent")
        
        self.dec_info_placeholder = ctk.CTkLabel(
            self.dec_info_container,
            text="No image selected",
            font=self.fonts["body"],
            text_color=Theme.TEXT_MUTED,
        )
        self.dec_info_placeholder.pack(pady=(0, 8))
        
        self.dec_info_rows = ctk.CTkFrame(self.dec_info_container, fg_color="transparent")
        
        btn_frame = ctk.CTkFrame(img_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 24))
        
        ctk.CTkButton(
            btn_frame,
            text="Browse Files",
            font=self.fonts["body"],
            height=42,
            corner_radius=10,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BORDER,
            command=self._select_decode_image,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        ctk.CTkButton(
            btn_frame,
            text="Paste Image",
            font=self.fonts["body"],
            height=42,
            corner_radius=10,
            fg_color=Theme.ACCENT_PURPLE,
            hover_color=Theme.ACCENT_PURPLE_HOVER,
            text_color="#ffffff",
            command=self._paste_image,
        ).pack(side="right", fill="x", expand=True)
        
        # ── Password ──
        pwd_card = Card(view, title="Password", icon=Icons.KEY, subtitle="If encrypted")
        pwd_card.pack(fill="x", padx=40, pady=(0, 20))
        
        pwd_frame = ctk.CTkFrame(pwd_card, fg_color="transparent")
        pwd_frame.pack(fill="x", padx=24, pady=(0, 24))
        
        self.dec_pwd_entry = ctk.CTkEntry(
            pwd_frame,
            height=46,
            corner_radius=12,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BORDER,
            font=self.fonts["body"],
            placeholder_text="Enter password if message was encrypted",
            show="●",
        )
        self.dec_pwd_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.dec_pwd_btn = ctk.CTkButton(
            pwd_frame,
            text=Icons.EYE,
            width=46,
            height=46,
            corner_radius=12,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=16),
            command=self._toggle_dec_pwd,
        )
        self.dec_pwd_btn.pack(side="right", padx=(10, 0))
        
        self.load_pwd_btn = ctk.CTkButton(
            pwd_frame,
            text="Load",
            width=60,
            height=46,
            corner_radius=12,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_PRIMARY,
            font=self.fonts["small"],
            command=self._load_pwd_dialog,
        )
        self.load_pwd_btn.pack(side="right")
        self.dec_pwd_visible = False
        
        # ── Action Buttons ──
        dec_btns = ctk.CTkFrame(view, fg_color="transparent")
        dec_btns.pack(fill="x", padx=40, pady=(0, 16))
        dec_btns.grid_columnconfigure(0, weight=3)
        dec_btns.grid_columnconfigure(1, weight=1)
        dec_btns.grid_columnconfigure(2, weight=1)

        self.decode_btn = ctk.CTkButton(
            dec_btns,
            text=f"{Icons.DECODE}   Seek",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            height=56,
            corner_radius=14,
            fg_color=Theme.ACCENT_PURPLE,
            hover_color=Theme.ACCENT_PURPLE_HOVER,
            text_color="#ffffff",
            command=self._decode,
        )
        self.decode_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.batch_decode_btn = ctk.CTkButton(
            dec_btns,
            text="Batch...",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            height=56,
            corner_radius=14,
            fg_color=Theme.ACCENT_BLUE,
            hover_color=Theme.ACCENT_BLUE_HOVER,
            text_color="#ffffff",
            command=self._batch_decode,
        )
        self.batch_decode_btn.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        self.clear_decode_btn = ctk.CTkButton(
            dec_btns,
            text="Clear",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            height=56,
            corner_radius=14,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_SECONDARY,
            border_width=1,
            border_color=Theme.BORDER,
            command=self._clear_decode,
        )
        self.clear_decode_btn.grid(row=0, column=2, sticky="ew")
        
        # Progress
        self.dec_progress = ctk.CTkProgressBar(
            view,
            height=6,
            corner_radius=3,
            fg_color=Theme.BG_SECONDARY,
            progress_color=Theme.ACCENT_PURPLE,
        )
        self.dec_progress.pack(fill="x", padx=40, pady=(0, 8))
        self.dec_progress.set(0)
        
        self.dec_status = ctk.CTkLabel(
            view,
            text="",
            font=self.fonts["small"],
            text_color=Theme.TEXT_SECONDARY,
        )
        self.dec_status.pack(anchor="w", padx=40)
        
        # ── Result ──
        self.dec_result = ctk.CTkFrame(
            view,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=16,
            border_width=2,
            border_color=Theme.ACCENT_GREEN,
        )
        
        res_header = ctk.CTkFrame(self.dec_result, fg_color="transparent")
        res_header.pack(fill="x", padx=24, pady=(20, 12))
        
        ctk.CTkLabel(
            res_header,
            text=f"{Icons.SUCCESS}  Message Found!",
            font=self.fonts["h3"],
            text_color=Theme.ACCENT_GREEN,
        ).pack(side="left")

        self.save_decoded_btn = ctk.CTkButton(
            res_header,
            text=f"{Icons.SAVE} Save",
            font=self.fonts["small"],
            width=80,
            height=32,
            corner_radius=8,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_PRIMARY,
            command=self._save_decoded,
        )
        self.save_decoded_btn.pack(side="right", padx=(0, 6))

        self.copy_btn = ctk.CTkButton(
            res_header,
            text=f"{Icons.COPY} Copy",
            font=self.fonts["small"],
            width=80,
            height=32,
            corner_radius=8,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_ELEVATED,
            text_color=Theme.TEXT_PRIMARY,
            command=self._copy_decoded,
        )
        self.copy_btn.pack(side="right")
        
        self.decoded_textbox = ctk.CTkTextbox(
            self.dec_result,
            height=150,
            corner_radius=12,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BORDER,
            font=self.fonts["body"],
            state="disabled",
            wrap="word",
        )
        self.decoded_textbox.pack(fill="x", padx=24, pady=(0, 16))
        
        self.decoded_info = ctk.CTkLabel(
            self.dec_result,
            text="",
            font=self.fonts["small"],
            text_color=Theme.TEXT_MUTED,
        )
        self.decoded_info.pack(padx=24, pady=(0, 24), anchor="w")
        
        return view
    
    def _on_close(self):
        self._save_settings()
        self.destroy()

    def _save_current(self):
        if self.current_view == "encode":
            self._save_encoded()
        elif self.current_view == "decode":
            self._save_decoded()

    def _clear_current(self):
        if self.current_view == "encode":
            self._clear_encode()
        elif self.current_view == "decode":
            self._clear_decode()


    # ═══════════════════════════════════════════════════════════════════════════
    #  SETTINGS PERSISTENCE
    # ═══════════════════════════════════════════════════════════════════════════
    def _settings_path(self):
        SETTINGS_DIR.mkdir(exist_ok=True)
        return SETTINGS_DIR / "settings.json"

    def _recent_path(self):
        SETTINGS_DIR.mkdir(exist_ok=True)
        return SETTINGS_DIR / "recent.json"

    def _load_settings(self):
        path = self._settings_path()
        if path.exists():
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_settings(self):
        settings = {
            "export_format": self.export_format,
            "geometry": self.geometry(),
        }
        try:
            with open(self._settings_path(), "w") as f:
                json.dump(settings, f)
        except Exception:
            pass

    def _passwords_path(self):
        SETTINGS_DIR.mkdir(exist_ok=True)
        return SETTINGS_DIR / "passwords.json"

    def _load_passwords(self):
        path = self._passwords_path()
        if path.exists():
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_password(self, name, password):
        passwords = self._load_passwords()
        # Remove if name already exists
        passwords = [p for p in passwords if p.get("name") != name]
        passwords.insert(0, {"name": name, "password": password})
        passwords = passwords[:10]  # Keep max 10
        try:
            with open(self._passwords_path(), "w") as f:
                json.dump(passwords, f)
        except Exception:
            pass

    def _delete_password(self, name):
        passwords = self._load_passwords()
        passwords = [p for p in passwords if p.get("name") != name]
        try:
            with open(self._passwords_path(), "w") as f:
                json.dump(passwords, f)
        except Exception:
            pass

    def _load_recent(self):
        path = self._recent_path()
        if path.exists():
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"encode": [], "decode": []}

    def _save_recent(self, recent):
        try:
            with open(self._recent_path(), "w") as f:
                json.dump(recent, f)
        except Exception:
            pass

    def _add_to_recent(self, filepath, mode):
        recent = self._load_recent()
        # Remove if already exists
        recent[mode] = [item for item in recent[mode] if item.get("path") != filepath]
        # Add new entry with timestamp
        recent[mode].insert(0, {
            "path": filepath,
            "time": time.time(),
            "size": os.path.getsize(filepath) if os.path.exists(filepath) else 0
        })
        recent[mode] = recent[mode][:10]
        self._save_recent(recent)
        self._build_recent_list()

    def _build_recent_list(self):
        for w in self.recent_frame.winfo_children():
            w.destroy()

        recent = self._load_recent()
        all_files = []
        for item in recent.get("encode", [])[:4]:
            if isinstance(item, dict):
                all_files.append(("encode", item))
            else:
                all_files.append(("encode", {"path": item, "time": 0, "size": 0}))
        for item in recent.get("decode", [])[:4]:
            if isinstance(item, dict):
                all_files.append(("decode", item))
            else:
                all_files.append(("decode", {"path": item, "time": 0, "size": 0}))

        if not all_files:
            ctk.CTkLabel(
                self.recent_frame,
                text="No recent files",
                font=self.fonts["tiny"],
                text_color=Theme.TEXT_DISABLED,
            ).pack(pady=4)
            return

        for mode, item in all_files[:8]:
            filepath = item.get("path", "")
            timestamp = item.get("time", 0)
            size = item.get("size", 0)

            if not Path(filepath).exists():
                continue

            name = Path(filepath).name
            icon = Icons.ENCODE if mode == "encode" else Icons.DECODE

            # Format time
            if timestamp > 0:
                elapsed = time.time() - timestamp
                if elapsed < 60:
                    time_str = "Just now"
                elif elapsed < 3600:
                    time_str = f"{int(elapsed/60)}m ago"
                elif elapsed < 86400:
                    time_str = f"{int(elapsed/3600)}h ago"
                else:
                    time_str = f"{int(elapsed/86400)}d ago"
            else:
                time_str = ""

            # Format size
            if size > 1024*1024:
                size_str = f"{size/1024/1024:.1f} MB"
            elif size > 1024:
                size_str = f"{size/1024:.0f} KB"
            else:
                size_str = f"{size} B"

            # Create entry frame
            entry = ctk.CTkFrame(self.recent_frame, fg_color="transparent", height=32)
            entry.pack(fill="x", pady=1)
            entry.pack_propagate(False)

            # Icon and filename
            btn = ctk.CTkButton(
                entry,
                text=f"  {icon} {name}",
                font=self.fonts["tiny"],
                height=28,
                anchor="w",
                fg_color="transparent",
                hover_color=Theme.SIDEBAR_ITEM_HOVER,
                text_color=Theme.TEXT_MUTED,
                command=lambda p=filepath, m=mode: self._open_recent(p, m),
            )
            btn.pack(side="left", fill="x", expand=True)

            # Time label
            if time_str:
                ctk.CTkLabel(
                    entry,
                    text=time_str,
                    font=self.fonts["tiny"],
                    text_color=Theme.TEXT_DISABLED,
                    width=50,
                ).pack(side="right", padx=(0, 4))

    def _open_recent(self, filepath, mode):
        if not Path(filepath).exists():
            return
        if mode == "encode":
            self._show_view("encode")
            self._select_image(filepath)
        else:
            self._show_view("decode")
            self._select_decode_image(filepath)

    def _clear_history(self):
        recent = {"encode": [], "decode": []}
        self._save_recent(recent)
        self._build_recent_list()

    def _show_help(self):
        win = ctk.CTkToplevel(self)
        win.title("Keyboard Shortcuts")
        win.geometry("400x380")
        win.grab_set()
        win.configure(fg_color=Theme.BG_PRIMARY)
        win.resizable(False, False)

        win.update_idletasks()
        x = (win.winfo_screenwidth() - 400) // 2
        y = (win.winfo_screenheight() - 380) // 2
        win.geometry(f"400x380+{x}+{y}")

        ctk.CTkLabel(win, text="Keyboard Shortcuts", font=self.fonts["h2"], text_color=Theme.TEXT_PRIMARY).pack(pady=(20, 12))

        shortcuts = [
            ("Ctrl+O", "Open image"),
            ("Ctrl+S", "Save result"),
            ("Ctrl+E", "Encode message"),
            ("Ctrl+D", "Decode message"),
            ("Escape", "Clear current view"),
        ]

        for key, desc in shortcuts:
            row = ctk.CTkFrame(win, fg_color=Theme.BG_SECONDARY, corner_radius=8, height=36)
            row.pack(fill="x", padx=20, pady=2)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=key, font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color=Theme.ACCENT_GREEN, width=100).pack(side="left", padx=12)
            ctk.CTkLabel(row, text=desc, font=self.fonts["body"], text_color=Theme.TEXT_SECONDARY).pack(side="left")

        ctk.CTkLabel(win, text="Tips: Drag images onto the app, use Batch for multiple files", font=self.fonts["tiny"], text_color=Theme.TEXT_MUTED).pack(pady=(16, 8))

        ctk.CTkButton(win, text="Close", font=self.fonts["body"], height=36, corner_radius=8, fg_color=Theme.BG_TERTIARY, hover_color=Theme.BG_ELEVATED, text_color=Theme.TEXT_PRIMARY, border_width=1, border_color=Theme.BORDER, command=win.destroy).pack(pady=(8, 20))

    # ═══════════════════════════════════════════════════════════════════════════
    #  VIEW SWITCHING
    # ═══════════════════════════════════════════════════════════════════════════
    def _show_view(self, name):
        self.current_view = name
        
        # Update nav buttons
        for key, btn in self.nav_buttons.items():
            if key == name:
                btn.configure(
                    fg_color=Theme.SIDEBAR_ITEM_ACTIVE,
                    text_color=Theme.TEXT_PRIMARY,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Theme.TEXT_SECONDARY,
                )
        
        # Update header
        titles = {
            "encode": "Hide",
            "decode": "Seek",
            "settings": "About",
        }
        self.header_title.configure(text=titles.get(name, ""))
        
        # Show view
        self.encode_view.pack_forget()
        self.decode_view.pack_forget()
        self.settings_view.pack_forget()
        
        if name == "encode":
            self.encode_view.pack(fill="both", expand=True)
        elif name == "decode":
            self.decode_view.pack(fill="both", expand=True)
        else:
            self.settings_view.pack(fill="both", expand=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  IMAGE HANDLING
    # ═══════════════════════════════════════════════════════════════════════════
    def _select_image(self, dropped_path=None):
        path = dropped_path or filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Images", "*.png *.bmp *.tiff *.tif *.webp"), ("All", "*.*")]
        )
        if not path:
            return
        
        self.image_path = path
        self.encoded_img = None
        self.enc_result.pack_forget()
        self.enc_progress.set(0)
        self.enc_status.configure(text="")
        
        try:
            img = Image.open(path)
            self.image_info = {
                "width": img.width,
                "height": img.height,
                "format": img.format or Path(path).suffix[1:].upper(),
                "size": os.path.getsize(path),
                "capacity": Stego.capacity(img.width, img.height),
            }
            
            # Preview
            thumb = img.copy()
            thumb.thumbnail((280, 140), Image.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(thumb)
            self.enc_dropzone.set_preview(self.preview_photo, Path(path).name)
            
            # Info
            self._update_info()
            self._on_msg_change()
            
        except Exception as e:
            self.enc_status.configure(text=f"❌ {e}", text_color=Theme.ACCENT_RED)
    
    def _update_info(self):
        if not self.image_info:
            return
        
        self.info_placeholder.place_forget()
        
        for w in self.info_rows_frame.winfo_children():
            w.destroy()
        
        self.info_rows_frame.pack(fill="both", expand=True)
        
        info = self.image_info
        is_png = info["format"].upper() == "PNG"
        
        rows = [
            ("Resolution", f"{info['width']} × {info['height']}", None, None),
            ("Format", info["format"], "✓ Lossless" if is_png else "⚠ Convert", Theme.ACCENT_GREEN if is_png else Theme.ACCENT_YELLOW),
            ("File Size", f"{info['size']/1024/1024:.2f} MB", None, None),
            ("Capacity", f"{info['capacity']:,} bytes", None, None),
        ]
        
        for label, value, badge, color in rows:
            row = InfoRow(self.info_rows_frame, label, value, badge, color)
            row.pack(fill="x", pady=3)
    
    def _select_decode_image(self, dropped_path=None):
        path = dropped_path or filedialog.askopenfilename(
            title="Select Encoded Image",
            filetypes=[("Images", "*.png *.bmp *.tiff *.tif *.webp"), ("All", "*.*")]
        )
        if not path:
            return
        
        self.decode_path = path
        self.dec_progress.set(0)
        self.dec_status.configure(text="")
        self.dec_result.pack_forget()
        
        try:
            img = Image.open(path)
            thumb = img.copy()
            thumb.thumbnail((280, 140), Image.LANCZOS)
            self.decode_photo = ImageTk.PhotoImage(thumb)
            self.dec_dropzone.set_preview(self.decode_photo, Path(path).name)
            
            # Show image info
            dec_size = os.path.getsize(path)
            dec_format = img.format or Path(path).suffix[1:].upper()
            
            self.dec_info_placeholder.pack_forget()
            for w in self.dec_info_rows.winfo_children():
                w.destroy()
            self.dec_info_rows.pack(fill="x")
            
            info_items = [
                ("Resolution", f"{img.width} x {img.height}"),
                ("Format", dec_format),
                ("File Size", f"{dec_size/1024:.1f} KB" if dec_size < 1024*1024 else f"{dec_size/1024/1024:.2f} MB"),
            ]
            for label, value in info_items:
                row = ctk.CTkFrame(self.dec_info_rows, fg_color=Theme.BG_TERTIARY, corner_radius=8, height=32)
                row.pack(fill="x", pady=2)
                row.pack_propagate(False)
                ctk.CTkLabel(row, text=label, font=self.fonts["tiny"], text_color=Theme.TEXT_SECONDARY).pack(side="left", padx=10)
                ctk.CTkLabel(row, text=value, font=self.fonts["small"], text_color=Theme.TEXT_PRIMARY).pack(side="right", padx=10)
        except Exception:
            pass
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  MESSAGE & RISK
    # ═══════════════════════════════════════════════════════════════════════════
    def _on_msg_change(self, e=None):
        text = self.msg_textbox.get("1.0", "end-1c")
        count = len(text.encode("utf-8"))
        cap = self.image_info["capacity"] if self.image_info else 0
        
        color = Theme.TEXT_MUTED
        if cap > 0 and count > cap:
            color = Theme.ACCENT_RED
        
        self.char_counter.configure(
            text=f"{count:,} / {cap:,} UTF-8 bytes" if cap else f"{count:,} UTF-8 bytes",
            text_color=color,
        )
        
        self._update_risk(count)
    
    def _update_risk(self, msg_len):
        if not self.image_info or msg_len == 0:
            self.risk_bar.set(0)
            self.risk_pct.configure(text="—", text_color=Theme.TEXT_MUTED)
            self.risk_level.configure(text="")
            return
        
        risk = Stego.risk(msg_len, self.image_info["width"], self.image_info["height"])
        
        Animate.progress(self, self.risk_bar, min(risk / 100, 1.0), 350)
        
        if risk < 10:
            level, color = "LOW RISK", Theme.ACCENT_GREEN
        elif risk < 30:
            level, color = "MEDIUM RISK", Theme.ACCENT_YELLOW
        else:
            level, color = "HIGH RISK", Theme.ACCENT_RED
        
        self.risk_bar.configure(progress_color=color)
        self.risk_pct.configure(text=f"{risk:.1f}%", text_color=color)
        self.risk_level.configure(text=level, text_color=color)
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  PASSWORD TOGGLE
    # ═══════════════════════════════════════════════════════════════════════════
    def _toggle_enc_pwd(self):
        self.enc_pwd_visible = not self.enc_pwd_visible
        self.enc_pwd_entry.configure(show="" if self.enc_pwd_visible else "●")
        self.enc_pwd_btn.configure(text=Icons.EYE_OFF if self.enc_pwd_visible else Icons.EYE)

    def _save_pwd_dialog(self):
        pwd = self.enc_pwd_entry.get().strip()
        if not pwd:
            self.enc_status.configure(text="Enter a password first", text_color=Theme.ACCENT_YELLOW)
            return
        
        # Simple dialog for name
        dialog = ctk.CTkInputDialog(text="Enter a name for this password:", title="Save Password")
        name = dialog.get_input()
        if name:
            self._save_password(name, pwd)
            self.enc_status.configure(text=f"Password saved as '{name}'", text_color=Theme.ACCENT_GREEN)

    def _load_pwd_dialog(self):
        passwords = self._load_passwords()
        if not passwords:
            self.dec_status.configure(text="No saved passwords", text_color=Theme.ACCENT_YELLOW)
            return
        
        # Create selection dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Select Password")
        dialog.geometry("300x400")
        dialog.configure(fg_color=Theme.BG_PRIMARY)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Select a saved password:", font=self.fonts["h3"], text_color=Theme.TEXT_PRIMARY).pack(pady=(20, 10))
        
        for pwd in passwords:
            btn = ctk.CTkButton(
                dialog,
                text=pwd["name"],
                font=self.fonts["body"],
                height=40,
                corner_radius=8,
                fg_color=Theme.BG_SECONDARY,
                hover_color=Theme.BG_TERTIARY,
                text_color=Theme.TEXT_PRIMARY,
                command=lambda p=pwd["password"], d=dialog: self._apply_password(p, d),
            )
            btn.pack(fill="x", padx=20, pady=4)
        
        ctk.CTkButton(dialog, text="Cancel", font=self.fonts["body"], height=36, corner_radius=8, fg_color=Theme.BG_TERTIARY, text_color=Theme.TEXT_SECONDARY, command=dialog.destroy).pack(pady=(10, 20))

    def _apply_password(self, password, dialog):
        self.dec_pwd_entry.delete(0, "end")
        self.dec_pwd_entry.insert(0, password)
        dialog.destroy()
    
    def _toggle_dec_pwd(self):
        self.dec_pwd_visible = not self.dec_pwd_visible
        self.dec_pwd_entry.configure(show="" if self.dec_pwd_visible else "●")
        self.dec_pwd_btn.configure(text=Icons.EYE_OFF if self.dec_pwd_visible else Icons.EYE)

    # ═══════════════════════════════════════════════════════════════════════════
    #  CLEAR
    # ═══════════════════════════════════════════════════════════════════════════
    def _clear_encode(self):
        self.image_path = None
        self.image_info = None
        self.encoded_img = None
        self.enc_dropzone.reset()
        self.info_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        self.info_rows_frame.pack_forget()
        self.msg_textbox.delete("1.0", "end")
        self.enc_pwd_entry.delete(0, "end")
        self.enc_result.pack_forget()
        self.enc_progress.set(0)
        self.enc_status.configure(text="")
        self.char_counter.configure(text="0 UTF-8 bytes", text_color=Theme.TEXT_MUTED)
        self.risk_bar.set(0)
        self.risk_pct.configure(text="—", text_color=Theme.TEXT_MUTED)
        self.risk_level.configure(text="")

    def _clear_decode(self):
        self.decode_path = None
        self.dec_dropzone.reset()
        self.dec_pwd_entry.delete(0, "end")
        self.dec_result.pack_forget()
        self.dec_progress.set(0)
        self.dec_status.configure(text="")

    def _paste_image(self):
        try:
            from PIL import ImageGrab
            clipboard = ImageGrab.grabclipboard()
            if clipboard is None:
                self.dec_status.configure(text="No image in clipboard", text_color=Theme.ACCENT_YELLOW)
                return
            if not hasattr(clipboard, 'save'):
                self.dec_status.configure(text="Clipboard contains text, not an image", text_color=Theme.ACCENT_YELLOW)
                return
            
            # Save clipboard image to temp file
            import tempfile
            temp_path = Path(tempfile.gettempdir()) / "clipboard_image.png"
            clipboard.save(str(temp_path), "PNG")
            
            self.decode_path = str(temp_path)
            self.dec_progress.set(0)
            self.dec_status.configure(text="")
            
            # Show preview
            thumb = clipboard.copy()
            thumb.thumbnail((280, 140), Image.LANCZOS)
            self.decode_photo = ImageTk.PhotoImage(thumb)
            self.dec_dropzone.set_preview(self.decode_photo, "Clipboard Image")
            
            self.dec_status.configure(text="Image pasted from clipboard", text_color=Theme.ACCENT_GREEN)
        except Exception as e:
            self.dec_status.configure(text=f"Paste failed: {e}", text_color=Theme.ACCENT_RED)

    def _on_format_change(self, fmt):
        self.export_format = fmt
        self.save_btn.configure(text=f"{Icons.SAVE}  Save as {fmt}")

    # ═══════════════════════════════════════════════════════════════════════════
    #  BATCH OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    def _batch_encode(self):
        msg = self.msg_textbox.get("1.0", "end-1c").strip()
        if not msg:
            self.enc_status.configure(text="⚠️ Please enter a message first", text_color=Theme.ACCENT_YELLOW)
            return

        from tkinter import filedialog as fd
        files = fd.askopenfilenames(
            title="Select Images to Encode",
            filetypes=[("Images", "*.png *.bmp *.tiff *.tif *.webp"), ("All", "*.*")]
        )
        if not files:
            return

        pwd = self.enc_pwd_entry.get().strip() or None
        fmt = self.export_format

        self.batch_encode_btn.configure(state="disabled", text="⏳ Processing...")
        self.enc_result.pack_forget()

        def work():
            success = 0
            failed = 0
            for i, path in enumerate(files):
                try:
                    self.after(0, lambda p=i: self.enc_status.configure(
                        text=f"Encoding {p+1}/{len(files)}...", text_color=Theme.TEXT_SECONDARY
                    ))
                    img = Stego.encode(path, msg, pwd)
                    stem = Path(path).stem
                    out = str(Path(path).parent / f"{stem}_stego.{fmt.lower()}")
                    img.save(out, fmt)
                    success += 1
                except Exception:
                    failed += 1

            def done():
                self.enc_progress.set(1.0)
                self.batch_encode_btn.configure(state="normal", text="Batch...")
                detail = f"{success} succeeded" + (f", {failed} failed" if failed else "")
                self.enc_status.configure(
                    text=f"✅ Batch complete: {detail}",
                    text_color=Theme.ACCENT_GREEN if failed == 0 else Theme.ACCENT_YELLOW,
                )
            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _batch_decode(self):
        from tkinter import filedialog as fd
        files = fd.askopenfilenames(
            title="Select Images to Decode",
            filetypes=[("Images", "*.png *.bmp *.tiff *.tif *.webp"), ("All", "*.*")]
        )
        if not files:
            return

        pwd = self.dec_pwd_entry.get().strip() or None

        self.batch_decode_btn.configure(state="disabled", text="⏳ Processing...")
        self.dec_result.pack_forget()

        def work():
            results = []
            for i, path in enumerate(files):
                try:
                    self.after(0, lambda p=i: self.dec_status.configure(
                        text=f"Decoding {p+1}/{len(files)}...", text_color=Theme.TEXT_SECONDARY
                    ))
                    msg = Stego.decode(path, pwd)
                    results.append((Path(path).name, msg))
                except Exception as e:
                    results.append((Path(path).name, f"[Error: {e}]"))

            def done():
                self.dec_progress.set(1.0)
                self.batch_decode_btn.configure(state="normal", text="Batch...")
                self.dec_status.configure(
                    text=f"✅ Decoded {len(results)} images",
                    text_color=Theme.ACCENT_GREEN,
                )
                self.decoded_textbox.configure(state="normal")
                self.decoded_textbox.delete("1.0", "end")
                for name, msg in results:
                    self.decoded_textbox.insert("end", f"── {name} ──\n{msg}\n\n")
                self.decoded_textbox.configure(state="disabled")
                self.decoded_info.configure(text=f"{len(results)} messages extracted")
                self.dec_result.pack(fill="x", padx=40, pady=(16, 24))
            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    # ═══════════════════════════════════════════════════════════════════════════
    def _build_settings_view(self):
        view = ctk.CTkFrame(self.content, fg_color="transparent")

        inner = ctk.CTkFrame(view, fg_color="transparent")
        inner.pack(fill="x", padx=40, pady=(24, 0))
        inner.grid_columnconfigure(0, weight=1)

        # Hero Section
        hero = ctk.CTkFrame(inner, fg_color=Theme.BG_SECONDARY, corner_radius=20, border_width=1, border_color=Theme.BORDER)
        hero.pack(fill="x", pady=(0, 24))

        ctk.CTkLabel(hero, text="🔐", font=ctk.CTkFont(size=64)).pack(pady=(32, 8))
        ctk.CTkLabel(hero, text="Hide and Seek", font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"), text_color=Theme.ACCENT_GREEN).pack()

        version_frame = ctk.CTkFrame(hero, fg_color=Theme.BG_TERTIARY, corner_radius=20)
        version_frame.pack(pady=(8, 32))
        ctk.CTkLabel(version_frame, text="  v1.0.0  ", font=self.fonts["small"], text_color=Theme.TEXT_SECONDARY).pack(padx=8, pady=4)

        ctk.CTkLabel(hero, text="A modern Python desktop app for image steganography", font=self.fonts["body"], text_color=Theme.TEXT_SECONDARY).pack(pady=(0, 24))

        # Features Grid
        features_title = ctk.CTkLabel(inner, text="Features", font=self.fonts["h2"], text_color=Theme.TEXT_PRIMARY)
        features_title.pack(anchor="w", pady=(0, 12))

        features_frame = ctk.CTkFrame(inner, fg_color="transparent")
        features_frame.pack(fill="x", pady=(0, 24))
        features_frame.grid_columnconfigure((0, 1), weight=1)

        features = [
            ("🔒", "LSB Encoding", "Hide messages in pixel bits"),
            ("🔑", "AES-256", "Fernet encryption + PBKDF2"),
            ("⬇️", "Drag and Drop", "Drop images onto the app"),
            ("📦", "Batch Process", "Encode multiple images at once"),
            ("📄", "Multi-Format", "Export PNG, BMP, or TIFF"),
            ("🌙", "Dark Theme", "GitHub-inspired dark UI"),
        ]

        for i, (icon, title, desc) in enumerate(features):
            row, col = divmod(i, 2)
            card = ctk.CTkFrame(features_frame, fg_color=Theme.BG_SECONDARY, corner_radius=12, border_width=1, border_color=Theme.BORDER)
            card.grid(row=row, column=col, sticky="nsew", padx=(0 if col == 0 else 8, 0 if col == 1 else 8), pady=(0 if row == 0 else 8, 0))

            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=24)).pack(pady=(12, 4))
            ctk.CTkLabel(card, text=title, font=self.fonts["h3"], text_color=Theme.TEXT_PRIMARY).pack()
            ctk.CTkLabel(card, text=desc, font=self.fonts["small"], text_color=Theme.TEXT_MUTED).pack(pady=(0, 12))

        # How It Works
        how_title = ctk.CTkLabel(inner, text="How It Works", font=self.fonts["h2"], text_color=Theme.TEXT_PRIMARY)
        how_title.pack(anchor="w", pady=(0, 12))

        steps_frame = ctk.CTkFrame(inner, fg_color="transparent")
        steps_frame.pack(fill="x", pady=(0, 24))

        steps = [
            ("1", "Select", "Choose an image"),
            ("2", "Type", "Enter your message"),
            ("3", "Hide", "Embed in pixels"),
            ("4", "Save", "Export stego image"),
        ]

        for i, (num, title, desc) in enumerate(steps):
            step_frame = ctk.CTkFrame(steps_frame, fg_color=Theme.BG_SECONDARY, corner_radius=12, border_width=1, border_color=Theme.BORDER)
            step_frame.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 4, 0 if i == 3 else 4))

            num_circle = ctk.CTkFrame(step_frame, fg_color=Theme.ACCENT_GREEN, corner_radius=20, width=36, height=36)
            num_circle.pack(pady=(12, 4))
            num_circle.pack_propagate(False)
            ctk.CTkLabel(num_circle, text=num, font=self.fonts["small"], text_color="#ffffff").pack(expand=True)

            ctk.CTkLabel(step_frame, text=title, font=self.fonts["h3"], text_color=Theme.TEXT_PRIMARY).pack()
            ctk.CTkLabel(step_frame, text=desc, font=self.fonts["tiny"], text_color=Theme.TEXT_MUTED).pack(pady=(0, 12))

        # Protocol Layout
        proto_title = ctk.CTkLabel(inner, text="Binary Protocol", font=self.fonts["h2"], text_color=Theme.TEXT_PRIMARY)
        proto_title.pack(anchor="w", pady=(0, 12))

        proto_frame = ctk.CTkFrame(inner, fg_color=Theme.BG_SECONDARY, corner_radius=12, border_width=1, border_color=Theme.BORDER)
        proto_frame.pack(fill="x", pady=(0, 24))
        proto_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        blocks = [
            ("MAGIC", "32 bits", Theme.ACCENT_BLUE),
            ("FLAG", "8 bits", Theme.ACCENT_YELLOW),
            ("SALT", "128 bits", Theme.ACCENT_GREEN),
            ("LENGTH", "32 bits", Theme.ACCENT_YELLOW),
            ("PAYLOAD", "N bits", Theme.ACCENT_PURPLE),
        ]

        for i, (label, bits, color) in enumerate(blocks):
            block = ctk.CTkFrame(proto_frame, fg_color=Theme.BG_TERTIARY, corner_radius=8, border_width=2, border_color=color)
            block.grid(row=0, column=i, sticky="nsew", padx=4, pady=12)
            ctk.CTkLabel(block, text=label, font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color=color).pack(pady=(8, 2))
            ctk.CTkLabel(block, text=bits, font=self.fonts["tiny"], text_color=Theme.TEXT_MUTED).pack(pady=(0, 8))

        # Tech Stack
        tech_title = ctk.CTkLabel(inner, text="Built With", font=self.fonts["h2"], text_color=Theme.TEXT_PRIMARY)
        tech_title.pack(anchor="w", pady=(0, 12))

        tech_frame = ctk.CTkFrame(inner, fg_color="transparent")
        tech_frame.pack(fill="x", pady=(0, 24))

        techs = [
            ("🎨", "CustomTkinter"),
            ("🖼️", "Pillow"),
            ("📏", "NumPy"),
            ("🔐", "Cryptography"),
        ]

        for i, (icon, name) in enumerate(techs):
            tech_card = ctk.CTkFrame(tech_frame, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER)
            tech_card.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 4, 0 if i == 3 else 4))
            ctk.CTkLabel(tech_card, text=icon, font=ctk.CTkFont(size=20)).pack(pady=(10, 2))
            ctk.CTkLabel(tech_card, text=name, font=self.fonts["small"], text_color=Theme.TEXT_SECONDARY).pack(pady=(0, 10))

        # Footer

        # Keyboard Shortcuts
        shortcuts_title = ctk.CTkLabel(inner, text="Keyboard Shortcuts", font=self.fonts["h2"], text_color=Theme.TEXT_PRIMARY)
        shortcuts_title.pack(anchor="w", pady=(0, 12))

        shortcuts_frame = ctk.CTkFrame(inner, fg_color=Theme.BG_SECONDARY, corner_radius=12, border_width=1, border_color=Theme.BORDER)
        shortcuts_frame.pack(fill="x", pady=(0, 24))

        shortcuts = [
            ("Ctrl+O", "Open image"),
            ("Ctrl+S", "Save result"),
            ("Ctrl+E", "Encode message"),
            ("Ctrl+D", "Decode message"),
            ("Escape", "Clear current view"),
        ]

        for key, desc in shortcuts:
            row = ctk.CTkFrame(shortcuts_frame, fg_color="transparent", height=36)
            row.pack(fill="x", padx=16, pady=2)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=key, font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color=Theme.ACCENT_GREEN, width=100).pack(side="left", padx=(0, 12))
            ctk.CTkLabel(row, text=desc, font=self.fonts["body"], text_color=Theme.TEXT_SECONDARY).pack(side="left")

        # Tips
        tips_title = ctk.CTkLabel(inner, text="Tips", font=self.fonts["h2"], text_color=Theme.TEXT_PRIMARY)
        tips_title.pack(anchor="w", pady=(0, 12))

        tips_frame = ctk.CTkFrame(inner, fg_color=Theme.BG_SECONDARY, corner_radius=12, border_width=1, border_color=Theme.BORDER)
        tips_frame.pack(fill="x", pady=(0, 24))

        tips = [
            "Drag images directly onto the app to load them",
            "Use the Batch button to process multiple images at once",
            "Right-click the message box for Cut/Copy/Paste options",
            "All processing happens locally - your data never leaves your computer",
        ]

        for tip in tips:
            tip_row = ctk.CTkFrame(tips_frame, fg_color="transparent", height=32)
            tip_row.pack(fill="x", padx=16, pady=2)
            tip_row.pack_propagate(False)
            ctk.CTkLabel(tip_row, text="  \u2022  ", font=self.fonts["body"], text_color=Theme.ACCENT_GREEN).pack(side="left")
            ctk.CTkLabel(tip_row, text=tip, font=self.fonts["small"], text_color=Theme.TEXT_SECONDARY).pack(side="left")

        ctk.CTkLabel(inner, text="Made by Antoush, Long May The Sunshine", font=self.fonts["tiny"], text_color=Theme.TEXT_DISABLED).pack(pady=(16, 40))

        return view

    #  ENCODE
    # ═══════════════════════════════════════════════════════════════════════════
    def _encode(self):
        if not self.image_path:
            self.enc_status.configure(text="⚠️ Please select an image", text_color=Theme.ACCENT_YELLOW)
            return
        
        msg = self.msg_textbox.get("1.0", "end-1c").strip()
        if not msg:
            self.enc_status.configure(text="⚠️ Please enter a message", text_color=Theme.ACCENT_YELLOW)
            return
        
        pwd = self.enc_pwd_entry.get().strip() or None
        
        self.encode_btn.configure(state="disabled", text="⏳  Processing...")
        self.enc_result.pack_forget()
        self.enc_status.configure(text="Encoding...", text_color=Theme.TEXT_SECONDARY)
        
        def work():
            try:
                def prog(v):
                    self.after(0, lambda: Animate.progress(self, self.enc_progress, v, 150))
                
                result = Stego.encode(self.image_path, msg, pwd, prog)
                self.encoded_img = result
                
                def done():
                    self.enc_progress.set(1.0)
                    self.enc_status.configure(text="✅ Message hidden successfully!", text_color=Theme.ACCENT_GREEN)
                    self.encode_btn.configure(state="normal", text=f"{Icons.ENCODE}   Hide")
                    self.enc_result.pack(fill="x", padx=40, pady=(16, 24))
                    Animate.pulse_border(self, self.enc_result, Theme.ACCENT_GREEN, Theme.ACCENT_BLUE, 1200, 2)
                    self._add_to_recent(self.image_path, "encode")
                
                self.after(0, done)
                
            except Exception as e:
                def err():
                    self.enc_progress.set(0)
                    self.enc_status.configure(text=f"❌ {e}", text_color=Theme.ACCENT_RED)
                    self.encode_btn.configure(state="normal", text=f"{Icons.ENCODE}   Hide")
                self.after(0, err)
        
        threading.Thread(target=work, daemon=True).start()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  DECODE
    # ═══════════════════════════════════════════════════════════════════════════
    def _decode(self):
        if not self.decode_path:
            self.dec_status.configure(text="⚠️ Please select an image", text_color=Theme.ACCENT_YELLOW)
            return

        if not os.path.isfile(self.decode_path):
            self.dec_status.configure(text="⚠️ File not found — it may have been moved or deleted", text_color=Theme.ACCENT_RED)
            return
        
        pwd = self.dec_pwd_entry.get().strip() or None
        
        self.decode_btn.configure(state="disabled", text="⏳  Processing...")
        self.dec_result.pack_forget()
        self.dec_status.configure(text="Decoding...", text_color=Theme.TEXT_SECONDARY)
        
        def work():
            try:
                def prog(v):
                    self.after(0, lambda: Animate.progress(self, self.dec_progress, v, 150))
                
                result = Stego.decode(self.decode_path, pwd, prog)
                
                def done():
                    self.dec_progress.set(1.0)
                    self.dec_status.configure(text="✅ Message extracted!", text_color=Theme.ACCENT_GREEN)
                    self.decode_btn.configure(state="normal", text=f"{Icons.DECODE}   Seek")
                    
                    self.decoded_textbox.configure(state="normal")
                    self.decoded_textbox.delete("1.0", "end")
                    self.decoded_textbox.insert("1.0", result)
                    self.decoded_textbox.configure(state="disabled")
                    
                    self.decoded_info.configure(text=f"{len(result):,} characters")
                    self.dec_result.pack(fill="x", padx=40, pady=(16, 24))
                    Animate.pulse_border(self, self.dec_result, Theme.ACCENT_GREEN, Theme.ACCENT_PURPLE, 1200, 2)
                    self._add_to_recent(self.decode_path, "decode")
                
                self.after(0, done)
                
            except ValueError as e:
                msg = str(e)
                def err():
                    self.dec_progress.set(0)
                    if msg == "ENCRYPTED":
                        self.dec_status.configure(text="🔒 Message is encrypted. Enter password.", text_color=Theme.ACCENT_YELLOW)
                    else:
                        self.dec_status.configure(text=f"❌ {msg}", text_color=Theme.ACCENT_RED)
                    self.decode_btn.configure(state="normal", text=f"{Icons.DECODE}   Seek")
                self.after(0, err)
        
        threading.Thread(target=work, daemon=True).start()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  SAVE & COMPARE
    # ═══════════════════════════════════════════════════════════════════════════
    def _save_encoded(self):
        if not self.encoded_img:
            return

        fmt = self.export_format
        ext = fmt.lower()
        name = f"{Path(self.image_path).stem}_stego.{ext}" if self.image_path else f"encoded.{ext}"

        path = filedialog.asksaveasfilename(
            title="Save Encoded Image",
            defaultextension=f".{ext}",
            initialfile=name,
            filetypes=[(fmt, f"*.{ext}")],
        )
        if not path:
            return

        if not path.lower().endswith(f".{ext}"):
            path = str(Path(path).with_suffix(f".{ext}"))

        self.encoded_img.save(path, fmt)
        Animate.typewriter(self, self.enc_status, f"💾 Saved: {Path(path).name}", 20)
    
    def _show_compare(self):
        if not self.image_path or not self.encoded_img:
            return
        
        try:
            diff, psnr = Stego.compare(self.image_path, self.encoded_img)
        except Exception:
            return
        
        win = ctk.CTkToplevel(self)
        win.title("Image Comparison")
        win.geometry("1000x680")
        win.grab_set()
        win.configure(fg_color=Theme.BG_PRIMARY)
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() - 1000) // 2
        y = (win.winfo_screenheight() - 680) // 2
        win.geometry(f"1000x680+{x}+{y}")
        
        # PSNR
        psnr_frame = ctk.CTkFrame(win, fg_color=Theme.BG_SECONDARY, corner_radius=16)
        psnr_frame.pack(fill="x", padx=32, pady=(32, 20))
        
        ctk.CTkLabel(
            psnr_frame,
            text="PSNR (Peak Signal-to-Noise Ratio)",
            font=self.fonts["small"],
            text_color=Theme.TEXT_SECONDARY,
        ).pack(pady=(20, 4))
        
        psnr_val = f"{psnr:.2f} dB" if psnr != float("inf") else "∞ dB"
        ctk.CTkLabel(
            psnr_frame,
            text=psnr_val,
            font=ctk.CTkFont(family="Consolas", size=40, weight="bold"),
            text_color=Theme.ACCENT_GREEN,
        ).pack()
        
        quality = "Excellent — Virtually identical" if psnr > 50 else "Very Good" if psnr > 40 else "Good"
        ctk.CTkLabel(
            psnr_frame,
            text=quality,
            font=self.fonts["body"],
            text_color=Theme.TEXT_SECONDARY,
        ).pack(pady=(4, 20))
        
        # Images
        imgs = ctk.CTkFrame(win, fg_color="transparent")
        imgs.pack(fill="both", expand=True, padx=32, pady=(0, 32))
        imgs.grid_columnconfigure((0, 1, 2), weight=1)
        
        orig = Image.open(self.image_path).convert("RGB")
        enc = self.encoded_img.convert("RGB")
        
        photos = []
        for idx, (title, pil) in enumerate([("Original", orig), ("Encoded", enc), ("Difference ×50", diff)]):
            card = ctk.CTkFrame(imgs, fg_color=Theme.BG_SECONDARY, corner_radius=16)
            card.grid(row=0, column=idx, sticky="nsew", padx=8)
            
            ctk.CTkLabel(
                card,
                text=title,
                font=self.fonts["h3"],
                text_color=Theme.TEXT_PRIMARY,
            ).pack(pady=(16, 12))
            
            thumb = pil.copy()
            thumb.thumbnail((280, 280), Image.LANCZOS)
            photo = ImageTk.PhotoImage(thumb)
            photos.append(photo)
            
            ctk.CTkLabel(card, text="", image=photo).pack(padx=16, pady=(0, 16))
        
        # Keep refs
        win.photos = photos
    
    def _save_decoded(self):
        text = self.decoded_textbox.get("1.0", "end-1c")
        if not text.strip():
            return

        path = filedialog.asksaveasfilename(
            title="Save Decoded Message",
            defaultextension=".txt",
            initialfile="decoded_message.txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")],
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        Animate.typewriter(self, self.dec_status, f"💾 Saved: {Path(path).name}", 20)

    def _copy_decoded(self):
        text = self.decoded_textbox.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        self.copy_btn.configure(text="✓ Copied!")
        self.after(2000, lambda: self.copy_btn.configure(text=f"{Icons.COPY} Copy"))


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = SteganoHide()
    app.mainloop()
