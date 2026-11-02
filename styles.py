import tkinter as tk
from tkinter import ttk

def apply_minimal_theme(root):
    """Transforms the application into a premium, modern dashboard structure."""
    style = ttk.Style()
    style.theme_use('clam')
    
    # Premium Dashboard Color Matrix
    CANVAS_BG = "#F8F9FC"        # Crisp, light neutral background canvas
    SIDEBAR_BG = "#11131A"      # Deep obsidian midnight sidebar accent
    CARD_BG = "#FFFFFF"         # Floating clean white cards
    TEXT_MAIN = "#1E2229"       # Sharp dark charcoal typography
    TEXT_MUTED = "#8A94A6"      # Soft grey slate secondary captions
    ACCENT_PILL = "#F0F2F7"     # Subtle card background or active tab state
    
    root.configure(bg=CANVAS_BG)
    
    # Structural layout widgets
    style.configure("TFrame", background=CANVAS_BG)
    style.configure("Sidebar.TFrame", background=SIDEBAR_BG)
    style.configure("Card.TFrame", background=CARD_BG, borderwidth=1, bordercolor="#EAEFF5")
    
    # Modern Typography Hierarchy
    style.configure("TLabel", background=CANVAS_BG, foreground=TEXT_MAIN, font=("Segoe UI", 10))
    style.configure("CardLabel.TLabel", background=CARD_BG, foreground=TEXT_MAIN, font=("Segoe UI", 10))
    style.configure("CardMuted.TLabel", background=CARD_BG, foreground=TEXT_MUTED, font=("Segoe UI", 9))
    style.configure("Heading.TLabel", background=CANVAS_BG, foreground=TEXT_MAIN, font=("Segoe UI", 18, "bold"))
    style.configure("Subheading.TLabel", background=CANVAS_BG, foreground=TEXT_MUTED, font=("Segoe UI", 11))
    
    # Sidebar Vertical Tab Buttons (Flat styling)
    style.configure("Sidebar.TButton", background=SIDEBAR_BG, foreground="#D1D5DB", font=("Segoe UI", 10), padding=[15, 12], borderwidth=0, relief="flat", anchor="w")
    style.map("Sidebar.TButton",
              background=[('active', "#1F2431"), ('selected', "#FFFFFF")],
              foreground=[('active', "#FFFFFF"), ('selected', "#11131A")])
    
    # Core Action Buttons (Premium Dark Accent)
    style.configure("TButton", background=SIDEBAR_BG, foreground="#FFFFFF", font=("Segoe UI", 9, "bold"), padding=[12, 8], borderwidth=0)
    style.map("TButton", background=[('active', "#252B3A")])
    
    style.configure("Secondary.TButton", background="#FFFFFF", foreground=TEXT_MAIN, font=("Segoe UI", 9), padding=[12, 8], borderwidth=1, bordercolor="#DCDFE6")
    style.map("Secondary.TButton", background=[('active', ACCENT_PILL)])
    
    # Sophisticated Entry Controls
    style.configure("TEntry", fieldbackground=CARD_BG, foreground=TEXT_MAIN, padding=6, borderwidth=1, bordercolor="#DCDFE6")
    style.configure("TCombobox", fieldbackground=CARD_BG, background=CARD_BG, foreground=TEXT_MAIN, padding=5, borderwidth=1, bordercolor="#DCDFE6")
    
    # Frameless Clean Data Views
    style.configure("Treeview", background=CARD_BG, fieldbackground=CARD_BG, foreground=TEXT_MAIN, rowheight=32, borderwidth=0, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", background=ACCENT_PILL, foreground=TEXT_MAIN, font=("Segoe UI", 9, "bold"), borderwidth=0)
    style.map("Treeview", background=[('selected', ACCENT_PILL)], foreground=[('selected', TEXT_MAIN)])
    
    # Hide the default native tabs from the Notebook completely to allow the left sidebar to drive navigation
    style.configure("TNotebook", background=CANVAS_BG, borderwidth=0, highlightthickness=0)
    style.configure("TNotebook.Tab", width=0, padding=0, borderwidth=0)