"""
VWAP Reversion Trading Bot GUI v1.0 - With Logo and Updated Colors
With CSV import/export, customizable data refresh, profile management, and market hours detection

Author: Trevor Hunter
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import bot components
from config import Config
from trader import AlpacaTrader
from strategy import VWAPReversionStrategy
from indicators import calculate_all_indicators, get_latest_signals, validate_data_quality
from database import TradeDatabase
from market_hours import get_market_status
from profile_manager import ProfileManager

# Import PIL for image handling
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class VWAPReversionGUI:
    """
    GUI for VWAP Reversion Trading Bot with professional styling and full functionality.
    """
    
    def __init__(self):
        """Initialize the GUI."""
        self.root = tk.Tk()
        self.setup_window()
        
        # Bot components
        self.trader = AlpacaTrader()
        self.strategy = VWAPReversionStrategy()
        self.database = TradeDatabase()
        self.profile_manager = ProfileManager()
        
        # GUI state
        self.bot_running = False
        self.data_refresh_running = False
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval = tk.StringVar(value="5")
        
        # Trading settings
        self.position_size = tk.StringVar(value=str(Config.POSITION_SIZE))
        self.stop_loss_pct = tk.StringVar(value=str(Config.STOP_LOSS_PCT * 100))
        self.take_profit_pct = tk.StringVar(value=str(Config.TAKE_PROFIT_PCT * 100))
        
        # VWAP strategy settings
        self.vwap_buy_threshold = tk.StringVar(value=str(Config.VWAP_BUY_THRESHOLD))
        self.vwap_sell_threshold = tk.StringVar(value=str(Config.VWAP_SELL_THRESHOLD))
        self.rsi_overbought = tk.StringVar(value=str(Config.RSI_OVERBOUGHT))
        self.rsi_period = tk.StringVar(value=str(Config.RSI_PERIOD))
        
        # Symbols
        self.symbols = tk.StringVar(value=", ".join(Config.DEFAULT_SYMBOLS))
        
        # Account info
        self.account_value_var = tk.StringVar(value="Not connected")
        self.buying_power_var = tk.StringVar(value="Not connected")
        self.cash_var = tk.StringVar(value="Not connected")
        self.positions_var = tk.StringVar(value="0 positions")
        
        # Market status
        self.market_status_var = tk.StringVar(value="Checking...")
        self.next_open_var = tk.StringVar(value="")
        
        # Setup GUI
        self.setup_styles()
        self.setup_layout()
        self.setup_dashboard()
        self.setup_trading_settings()
        self.setup_symbols()
        self.setup_logs()
        
        # Load profile data
        self.load_profile_data()
        
        # Start market status updates
        self.update_market_status()
    
    def setup_window(self):
        """Configure the main window."""
        self.root.title("VWAP Reversion Trading Bot v1.0")
        self.root.geometry("1200x800")
        self.root.configure(bg="#ffffff")
        
        # Set window icon if available
        try:
            if PIL_AVAILABLE and os.path.exists("vwap-trader-logo.png"):
                icon_image = Image.open("vwap-trader-logo.png")
                icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(False, icon_photo)
        except Exception as e:
            print(f"Could not set window icon: {e}")
    
    def setup_styles(self):
        """Configure custom styles."""
        style = ttk.Style()
        
        # Configure notebook style
        style.configure('TNotebook', background='#ffffff')
        style.configure('TNotebook.Tab', background='#f0f0f0', foreground='#000000')
        style.map('TNotebook.Tab', background=[('selected', '#0b8fce')])
        
        # Configure button styles
        try:
            style.configure('Accent.TButton', 
                           background='#0b8fce', 
                           foreground='white',
                           font=('Arial', 10, 'bold'))
            
            style.configure('Success.TButton', 
                           background='#00aa00', 
                           foreground='white',
                           font=('Arial', 10, 'bold'))
            
            style.configure('Danger.TButton', 
                           background='#aa0000', 
                           foreground='white',
                           font=('Arial', 10, 'bold'))
        except Exception as e:
            print(f"Warning: Could not configure custom button styles: {e}")
            # Use default styles if custom styles fail
    
    def setup_layout(self):
        """Arrange widgets in the main window."""
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="#ffffff")
        self.main_frame.pack(fill="both", expand=True)
        
        # Header with logo
        self.setup_header()
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_header(self):
        """Setup header with logo and title."""
        header_frame = tk.Frame(self.main_frame, bg="#ffffff", height=80)
        header_frame.pack(fill="x", padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        # Logo
        if PIL_AVAILABLE and os.path.exists("vwap-trader-logo.png"):
            try:
                logo_image = Image.open("vwap-trader-logo.png")
                logo_image = logo_image.resize((64, 64), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                logo_label = tk.Label(header_frame, image=self.logo_photo, bg="#ffffff")
                logo_label.pack(side="left", padx=(0, 20))
            except Exception as e:
                print(f"Could not load logo: {e}")
        
        # Title and subtitle
        title_frame = tk.Frame(header_frame, bg="#ffffff")
        title_frame.pack(side="left", fill="y")
        
        title_label = tk.Label(title_frame, text="VWAP Reversion Trading Bot", 
                              bg="#ffffff", fg="#000000", 
                              font=("Arial", 20, "bold"))
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(title_frame, text="Intraday Mean Reversion Strategy", 
                                 bg="#ffffff", fg="#666666", 
                                 font=("Arial", 12))
        subtitle_label.pack(anchor="w")
    
    def setup_dashboard(self):
        """Setup dashboard tab."""
        self.dashboard_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Account Info section
        account_frame = tk.Frame(self.dashboard_frame, bg="#ffffff")
        account_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(account_frame, text="Account Information", bg="#ffffff", fg="#000000", 
                font=("Arial", 14, "bold")).pack(anchor="w")
        
        # Account details
        account_details_frame = tk.Frame(account_frame, bg="#ffffff")
        account_details_frame.pack(fill="x", pady=10)
        
        # Account value
        tk.Label(account_details_frame, text="Account Value:", bg="#ffffff", fg="#000000", 
                font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=(0, 10))
        tk.Label(account_details_frame, textvariable=self.account_value_var, bg="#ffffff", 
                fg="#0b8fce", font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w")
        
        # Buying power
        tk.Label(account_details_frame, text="Buying Power:", bg="#ffffff", fg="#000000", 
                font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=(0, 10))
        tk.Label(account_details_frame, textvariable=self.buying_power_var, bg="#ffffff", 
                fg="#0b8fce", font=("Arial", 12, "bold")).grid(row=1, column=1, sticky="w")
        
        # Cash
        tk.Label(account_details_frame, text="Cash:", bg="#ffffff", fg="#000000", 
                font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=(0, 10))
        tk.Label(account_details_frame, textvariable=self.cash_var, bg="#ffffff", 
                fg="#0b8fce", font=("Arial", 12, "bold")).grid(row=2, column=1, sticky="w")
        
        # Positions
        tk.Label(account_details_frame, text="Open Positions:", bg="#ffffff", fg="#000000", 
                font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=(0, 10))
        tk.Label(account_details_frame, textvariable=self.positions_var, bg="#ffffff", 
                fg="#0b8fce", font=("Arial", 12, "bold")).grid(row=3, column=1, sticky="w")
        
        # Market Status section
        market_status_frame = tk.Frame(self.dashboard_frame, bg="#ffffff")
        market_status_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(market_status_frame, text="Market:", bg="#ffffff", fg="#000000", 
                font=("Arial", 12, "bold")).pack(side="left")
        self.market_status_label = tk.Label(market_status_frame, textvariable=self.market_status_var, 
                                          bg="#ffffff", fg="#0b8fce", font=("Arial", 12))
        self.market_status_label.pack(side="left", padx=10)
        
        # Next market open info
        self.next_open_label = tk.Label(market_status_frame, textvariable=self.next_open_var, 
                                       bg="#ffffff", fg="#666666", font=("Arial", 10))
        self.next_open_label.pack(side="left", padx=20)
        
        # Control buttons
        control_frame = tk.Frame(self.dashboard_frame, bg="#ffffff")
        control_frame.pack(fill="x", padx=20, pady=20)
        
        # Create buttons with fallback to default style if custom styles fail
        try:
            self.connect_btn = ttk.Button(control_frame, text="Connect to Alpaca", 
                                         command=self.connect_to_alpaca, style="Accent.TButton")
        except:
            self.connect_btn = ttk.Button(control_frame, text="Connect to Alpaca", 
                                         command=self.connect_to_alpaca)
        self.connect_btn.pack(side="left", padx=(0, 10))
        
        try:
            self.start_btn = ttk.Button(control_frame, text="Start Bot", 
                                       command=self.start_bot, style="Success.TButton")
        except:
            self.start_btn = ttk.Button(control_frame, text="Start Bot", 
                                       command=self.start_bot)
        self.start_btn.pack(side="left", padx=(0, 10))
        
        try:
            self.stop_btn = ttk.Button(control_frame, text="Stop Bot", 
                                      command=self.stop_bot, style="Danger.TButton")
        except:
            self.stop_btn = ttk.Button(control_frame, text="Stop Bot", 
                                      command=self.stop_bot)
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        # Bot status
        self.bot_status_var = tk.StringVar(value="Bot stopped")
        self.bot_status_label = tk.Label(control_frame, textvariable=self.bot_status_var, 
                                        bg="#ffffff", fg="#666666", font=("Arial", 12))
        self.bot_status_label.pack(side="left", padx=20)
    
    def setup_trading_settings(self):
        """Setup trading settings tab."""
        self.settings_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.settings_frame, text="Trading Settings")
        
        # Position settings
        position_frame = tk.LabelFrame(self.settings_frame, text="Position Settings", 
                                      bg="#ffffff", fg="#000000", font=("Arial", 12, "bold"))
        position_frame.pack(fill="x", padx=20, pady=10)
        
        # Position size
        tk.Label(position_frame, text="Position Size ($):", bg="#ffffff", fg="#000000", 
                font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        position_entry = tk.Entry(position_frame, textvariable=self.position_size, 
                                 font=("Arial", 10), width=15)
        position_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Stop loss
        tk.Label(position_frame, text="Stop Loss (%):", bg="#ffffff", fg="#000000", 
                font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        stop_loss_entry = tk.Entry(position_frame, textvariable=self.stop_loss_pct, 
                                  font=("Arial", 10), width=15)
        stop_loss_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Take profit
        tk.Label(position_frame, text="Take Profit (%):", bg="#ffffff", fg="#000000", 
                font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        take_profit_entry = tk.Entry(position_frame, textvariable=self.take_profit_pct, 
                                    font=("Arial", 10), width=15)
        take_profit_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # VWAP Strategy settings
        strategy_frame = tk.LabelFrame(self.settings_frame, text="VWAP Strategy Settings", 
                                      bg="#ffffff", fg="#000000", font=("Arial", 12, "bold"))
        strategy_frame.pack(fill="x", padx=20, pady=10)
        
        # VWAP buy threshold
        tk.Label(strategy_frame, text="VWAP Buy Threshold:", bg="#ffffff", fg="#000000", 
                font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        vwap_buy_entry = tk.Entry(strategy_frame, textvariable=self.vwap_buy_threshold, 
                                 font=("Arial", 10), width=15)
        vwap_buy_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # VWAP sell threshold
        tk.Label(strategy_frame, text="VWAP Sell Threshold:", bg="#ffffff", fg="#000000", 
                font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        vwap_sell_entry = tk.Entry(strategy_frame, textvariable=self.vwap_sell_threshold, 
                                  font=("Arial", 10), width=15)
        vwap_sell_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # RSI overbought
        tk.Label(strategy_frame, text="RSI Overbought Level:", bg="#ffffff", fg="#000000", 
                font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        rsi_overbought_entry = tk.Entry(strategy_frame, textvariable=self.rsi_overbought, 
                                       font=("Arial", 10), width=15)
        rsi_overbought_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # RSI period
        tk.Label(strategy_frame, text="RSI Period:", bg="#ffffff", fg="#000000", 
                font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        rsi_period_entry = tk.Entry(strategy_frame, textvariable=self.rsi_period, 
                                   font=("Arial", 10), width=15)
        rsi_period_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Data refresh settings
        refresh_frame = tk.LabelFrame(self.settings_frame, text="Data Refresh Settings", 
                                     bg="#ffffff", fg="#000000", font=("Arial", 12, "bold"))
        refresh_frame.pack(fill="x", padx=20, pady=10)
        
        # Auto refresh checkbox
        auto_refresh_check = tk.Checkbutton(refresh_frame, text="Auto Refresh Data", 
                                           variable=self.auto_refresh, bg="#ffffff", 
                                           fg="#000000", font=("Arial", 10))
        auto_refresh_check.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Refresh interval
        tk.Label(refresh_frame, text="Refresh Interval (minutes):", bg="#ffffff", fg="#000000", 
                font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        refresh_interval_combo = ttk.Combobox(refresh_frame, textvariable=self.refresh_interval, 
                                             values=["1", "5", "10", "15", "30", "60"], 
                                             width=12, state="readonly")
        refresh_interval_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Save settings button
        save_btn = ttk.Button(self.settings_frame, text="Save Settings", 
                             command=self.save_settings, style="Accent.TButton")
        save_btn.pack(pady=20)
    
    def setup_symbols(self):
        """Setup symbols management tab."""
        self.symbols_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.symbols_frame, text="Symbols")
        
        # Symbols input
        symbols_input_frame = tk.Frame(self.symbols_frame, bg="#ffffff")
        symbols_input_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(symbols_input_frame, text="Trading Symbols (comma-separated):", 
                bg="#ffffff", fg="#000000", font=("Arial", 12, "bold")).pack(anchor="w")
        
        symbols_entry = tk.Entry(symbols_input_frame, textvariable=self.symbols, 
                                font=("Arial", 10), width=80)
        symbols_entry.pack(fill="x", pady=5)
        
        # Symbol management buttons
        symbol_buttons_frame = tk.Frame(self.symbols_frame, bg="#ffffff")
        symbol_buttons_frame.pack(fill="x", padx=20, pady=10)
        
        add_symbol_btn = ttk.Button(symbol_buttons_frame, text="Add Symbol", 
                                   command=self.add_symbol, style="Accent.TButton")
        add_symbol_btn.pack(side="left", padx=(0, 10))
        
        remove_symbol_btn = ttk.Button(symbol_buttons_frame, text="Remove Symbol", 
                                      command=self.remove_symbol, style="Danger.TButton")
        remove_symbol_btn.pack(side="left", padx=(0, 10))
        
        import_csv_btn = ttk.Button(symbol_buttons_frame, text="Import CSV", 
                                   command=self.import_csv, style="Accent.TButton")
        import_csv_btn.pack(side="left", padx=(0, 10))
        
        export_csv_btn = ttk.Button(symbol_buttons_frame, text="Export CSV", 
                                   command=self.export_csv, style="Accent.TButton")
        export_csv_btn.pack(side="left", padx=(0, 10))
        
        # Profile management
        profile_frame = tk.LabelFrame(self.symbols_frame, text="Profile Management", 
                                     bg="#ffffff", fg="#000000", font=("Arial", 12, "bold"))
        profile_frame.pack(fill="x", padx=20, pady=10)
        
        profile_buttons_frame = tk.Frame(profile_frame, bg="#ffffff")
        profile_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        save_profile_btn = ttk.Button(profile_buttons_frame, text="Save Profile", 
                                     command=self.save_profile, style="Accent.TButton")
        save_profile_btn.pack(side="left", padx=(0, 10))
        
        load_profile_btn = ttk.Button(profile_buttons_frame, text="Load Profile", 
                                     command=self.load_profile, style="Accent.TButton")
        load_profile_btn.pack(side="left", padx=(0, 10))
        
        delete_profile_btn = ttk.Button(profile_buttons_frame, text="Delete Profile", 
                                       command=self.delete_profile, style="Danger.TButton")
        delete_profile_btn.pack(side="left", padx=(0, 10))
    
    def setup_logs(self):
        """Setup logs tab."""
        self.logs_frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.logs_frame, text="Logs")
        
        # Logs text area
        logs_text_frame = tk.Frame(self.logs_frame, bg="#ffffff")
        logs_text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.logs_text = tk.Text(logs_text_frame, bg="#f8f8f8", fg="#000000", 
                                font=("Consolas", 9), wrap="word")
        logs_scrollbar = tk.Scrollbar(logs_text_frame, orient="vertical", command=self.logs_text.yview)
        self.logs_text.configure(yscrollcommand=logs_scrollbar.set)
        
        self.logs_text.pack(side="left", fill="both", expand=True)
        logs_scrollbar.pack(side="right", fill="y")
        
        # Log controls
        log_controls_frame = tk.Frame(self.logs_frame, bg="#ffffff")
        log_controls_frame.pack(fill="x", padx=20, pady=10)
        
        clear_logs_btn = ttk.Button(log_controls_frame, text="Clear Logs", 
                                   command=self.clear_logs, style="Accent.TButton")
        clear_logs_btn.pack(side="left", padx=(0, 10))
        
        export_logs_btn = ttk.Button(log_controls_frame, text="Export Logs", 
                                    command=self.export_logs, style="Accent.TButton")
        export_logs_btn.pack(side="left", padx=(0, 10))
    
    def log_message(self, message: str):
        """Log a message to the GUI."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if hasattr(self, 'logs_text') and self.logs_text:
            self.logs_text.insert(tk.END, log_entry)
            self.logs_text.see(tk.END)
        else:
            print(log_entry.strip())
    
    def clear_logs(self):
        """Clear the logs."""
        if hasattr(self, 'logs_text') and self.logs_text:
            self.logs_text.delete(1.0, tk.END)
    
    def export_logs(self):
        """Export logs to a file."""
        if not hasattr(self, 'logs_text') or not self.logs_text:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                self.log_message(f"Logs exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {e}")
    
    def connect_to_alpaca(self):
        """Connect to Alpaca API."""
        try:
            if self.trader.connect():
                self.log_message("✓ Connected to Alpaca API")
                self.update_account_info()
                self.connect_btn.config(text="Connected", state="disabled")
            else:
                self.log_message("✗ Failed to connect to Alpaca API")
                messagebox.showerror("Connection Error", "Failed to connect to Alpaca API")
        except Exception as e:
            self.log_message(f"✗ Connection error: {e}")
            messagebox.showerror("Connection Error", f"Connection error: {e}")
    
    def update_account_info(self):
        """Update account information display."""
        try:
            account = self.trader.get_account()
            positions = self.trader.get_positions()
            
            self.account_value_var.set(f"${float(account.equity):,.2f}")
            self.buying_power_var.set(f"${float(account.buying_power):,.2f}")
            self.cash_var.set(f"${float(account.cash):,.2f}")
            self.positions_var.set(f"{len(positions)} positions")
            
        except Exception as e:
            self.log_message(f"Error updating account info: {e}")
    
    def update_market_status(self):
        """Update market status display."""
        try:
            status = get_market_status()
            
            # Update market status
            if status['is_open']:
                self.market_status_var.set("OPEN")
                self.market_status_label.config(fg="#00aa00")  # Green
                self.next_open_var.set("")
            elif status['is_premarket']:
                self.market_status_var.set("PRE-MARKET")
                self.market_status_label.config(fg="#ff8800")  # Orange
                next_open = status['market_open']
                self.next_open_var.set(f"Opens at {next_open.strftime('%H:%M')} ET")
            elif status['is_afterhours']:
                self.market_status_var.set("AFTER-HOURS")
                self.market_status_label.config(fg="#ff8800")  # Orange
                from market_hours import get_next_market_open
                next_open = get_next_market_open()
                self.next_open_var.set(f"Next open: {next_open.strftime('%m/%d %H:%M')} ET")
            else:
                self.market_status_var.set("CLOSED")
                self.market_status_label.config(fg="#aa0000")  # Red
                from market_hours import get_next_market_open
                next_open = get_next_market_open()
                self.next_open_var.set(f"Next open: {next_open.strftime('%m/%d %H:%M')} ET")
                
        except Exception as e:
            self.market_status_var.set("ERROR")
            self.market_status_label.config(fg="#aa0000")
            self.next_open_var.set("")
            self.log_message(f"Error updating market status: {e}")
    
    def start_bot(self):
        """Start the trading bot."""
        if not self.trader.connected:
            messagebox.showerror("Error", "Please connect to Alpaca first")
            return
        
        self.bot_running = True
        self.bot_status_var.set("Bot running")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # Start bot in separate thread
        bot_thread = threading.Thread(target=self.run_bot_loop, daemon=True)
        bot_thread.start()
        
        self.log_message("VWAP Reversion Bot started")
    
    def stop_bot(self):
        """Stop the trading bot."""
        self.bot_running = False
        self.bot_status_var.set("Bot stopped")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        self.log_message("VWAP Reversion Bot stopped")
    
    def run_bot_loop(self):
        """Main bot loop running in separate thread."""
        while self.bot_running:
            try:
                # Always update market status
                self.update_market_status()
                
                # Check if market is open before running trading logic
                status = get_market_status()
                
                if status['is_open']:
                    # Market is open - run full trading logic
                    self.update_account_info()
                    self.update_symbols_data()
                    self.log_message("Market is open - running VWAP Reversion analysis")
                else:
                    # Market is closed - only update account info
                    self.update_account_info()
                    if status['is_weekend']:
                        self.log_message("Market closed (weekend) - minimal updates only")
                    elif status['is_holiday']:
                        self.log_message("Market closed (holiday) - minimal updates only")
                    else:
                        self.log_message("Market closed - minimal updates only")
                
                time.sleep(60)  # Bot checks every 60 seconds
            except Exception as e:
                self.log_message(f"Bot error: {e}")
                time.sleep(60)
    
    def update_symbols_data(self):
        """Update data for all symbols."""
        try:
            symbols_list = [s.strip().upper() for s in self.symbols.get().split(",") if s.strip()]
            
            for symbol in symbols_list:
                try:
                    # Get historical data
                    df = self.trader.get_historical_data(symbol, Config.TIMEFRAME)
                    
                    if not validate_data_quality(df, min_bars=5):
                        self.log_message(f"Insufficient data for {symbol}")
                        continue
                    
                    # Calculate indicators
                    df = calculate_all_indicators(df, Config.RSI_PERIOD)
                    
                    # Get latest signals
                    signals = get_latest_signals(df)
                    if not signals:
                        continue
                    
                    # Check for signals
                    if self.strategy.get_buy_signal(signals, symbol):
                        self.log_message(f"{symbol} → BUY signal (Price: ${signals['close']:.2f}, VWAP: ${signals['vwap']:.2f})")
                    elif self.strategy.get_sell_signal(signals, symbol):
                        self.log_message(f"{symbol} → SELL signal (Price: ${signals['close']:.2f}, VWAP: ${signals['vwap']:.2f})")
                    else:
                        self.log_message(f"{symbol} → HOLD (Price: ${signals['close']:.2f}, VWAP: ${signals['vwap']:.2f})")
                
                except Exception as e:
                    self.log_message(f"Error analyzing {symbol}: {e}")
                    continue
        
        except Exception as e:
            self.log_message(f"Error updating symbols data: {e}")
    
    def save_settings(self):
        """Save trading settings."""
        try:
            # Update strategy parameters
            self.strategy.update_parameters(
                vwap_threshold_buy=float(self.vwap_buy_threshold.get()),
                vwap_threshold_sell=float(self.vwap_sell_threshold.get()),
                rsi_overbought=float(self.rsi_overbought.get()),
                rsi_period=int(self.rsi_period.get())
            )
            
            # Update trader settings
            self.trader.update_trading_settings(
                position_size=float(self.position_size.get()),
                stop_loss_pct=float(self.stop_loss_pct.get()) / 100,
                take_profit_pct=float(self.take_profit_pct.get()) / 100
            )
            
            self.log_message("Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully")
        
        except Exception as e:
            self.log_message(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Error saving settings: {e}")
    
    def add_symbol(self):
        """Add a new symbol."""
        symbol = tk.simpledialog.askstring("Add Symbol", "Enter symbol to add:")
        if symbol:
            symbol = symbol.strip().upper()
            current_symbols = self.symbols.get()
            if symbol not in current_symbols:
                if current_symbols:
                    self.symbols.set(current_symbols + ", " + symbol)
                else:
                    self.symbols.set(symbol)
                self.log_message(f"Added symbol: {symbol}")
            else:
                messagebox.showinfo("Info", f"Symbol {symbol} already exists")
    
    def remove_symbol(self):
        """Remove a symbol."""
        symbol = tk.simpledialog.askstring("Remove Symbol", "Enter symbol to remove:")
        if symbol:
            symbol = symbol.strip().upper()
            current_symbols = [s.strip() for s in self.symbols.get().split(",")]
            if symbol in current_symbols:
                current_symbols.remove(symbol)
                self.symbols.set(", ".join(current_symbols))
                self.log_message(f"Removed symbol: {symbol}")
            else:
                messagebox.showinfo("Info", f"Symbol {symbol} not found")
    
    def import_csv(self):
        """Import symbols from CSV file."""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                symbols = []
                with open(filename, 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row and row[0].strip():
                            symbols.append(row[0].strip().upper())
                
                if symbols:
                    self.symbols.set(", ".join(symbols))
                    self.log_message(f"Imported {len(symbols)} symbols from CSV")
                else:
                    messagebox.showinfo("Info", "No symbols found in CSV file")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error importing CSV: {e}")
    
    def export_csv(self):
        """Export symbols to CSV file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                symbols = [s.strip() for s in self.symbols.get().split(",") if s.strip()]
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    for symbol in symbols:
                        writer.writerow([symbol])
                
                self.log_message(f"Exported {len(symbols)} symbols to CSV")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting CSV: {e}")
    
    def save_profile(self):
        """Save current settings as a profile."""
        profile_name = tk.simpledialog.askstring("Save Profile", "Enter profile name:")
        if profile_name:
            try:
                profile_data = {
                    "symbols": self.symbols.get(),
                    "position_size": self.position_size.get(),
                    "stop_loss_pct": self.stop_loss_pct.get(),
                    "take_profit_pct": self.take_profit_pct.get(),
                    "vwap_buy_threshold": self.vwap_buy_threshold.get(),
                    "vwap_sell_threshold": self.vwap_sell_threshold.get(),
                    "rsi_overbought": self.rsi_overbought.get(),
                    "rsi_period": self.rsi_period.get(),
                    "refresh_interval": self.refresh_interval.get(),
                    "auto_refresh": self.auto_refresh.get()
                }
                
                self.profile_manager.save_profile(profile_name, profile_data)
                self.log_message(f"Profile '{profile_name}' saved successfully")
                messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error saving profile: {e}")
    
    def load_profile(self):
        """Load a saved profile."""
        profiles = self.profile_manager.list_profiles()
        if not profiles:
            messagebox.showinfo("Info", "No profiles found")
            return
        
        profile_name = tk.simpledialog.askstring("Load Profile", f"Enter profile name:\nAvailable: {', '.join(profiles)}")
        if profile_name and profile_name in profiles:
            try:
                profile_data = self.profile_manager.get_profile_data(profile_name)
                if profile_data:
                    self.symbols.set(profile_data.get("symbols", ""))
                    self.position_size.set(profile_data.get("position_size", str(Config.POSITION_SIZE)))
                    self.stop_loss_pct.set(profile_data.get("stop_loss_pct", str(Config.STOP_LOSS_PCT * 100)))
                    self.take_profit_pct.set(profile_data.get("take_profit_pct", str(Config.TAKE_PROFIT_PCT * 100)))
                    self.vwap_buy_threshold.set(profile_data.get("vwap_buy_threshold", str(Config.VWAP_BUY_THRESHOLD)))
                    self.vwap_sell_threshold.set(profile_data.get("vwap_sell_threshold", str(Config.VWAP_SELL_THRESHOLD)))
                    self.rsi_overbought.set(profile_data.get("rsi_overbought", str(Config.RSI_OVERBOUGHT)))
                    self.rsi_period.set(profile_data.get("rsi_period", str(Config.RSI_PERIOD)))
                    self.refresh_interval.set(profile_data.get("refresh_interval", "5"))
                    self.auto_refresh.set(profile_data.get("auto_refresh", True))
                    
                    self.log_message(f"Profile '{profile_name}' loaded successfully")
                    messagebox.showinfo("Success", f"Profile '{profile_name}' loaded successfully")
                else:
                    messagebox.showerror("Error", f"Profile '{profile_name}' not found")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error loading profile: {e}")
    
    def delete_profile(self):
        """Delete a saved profile."""
        profiles = self.profile_manager.list_profiles()
        if not profiles:
            messagebox.showinfo("Info", "No profiles found")
            return
        
        profile_name = tk.simpledialog.askstring("Delete Profile", f"Enter profile name to delete:\nAvailable: {', '.join(profiles)}")
        if profile_name and profile_name in profiles:
            try:
                self.profile_manager.delete_profile(profile_name)
                self.log_message(f"Profile '{profile_name}' deleted successfully")
                messagebox.showinfo("Success", f"Profile '{profile_name}' deleted successfully")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting profile: {e}")
    
    def load_profile_data(self):
        """Load profile data into GUI variables."""
        try:
            profile_data = self.profile_manager.get_current_profile_data()
            
            # If no profile data exists, use defaults
            if not profile_data:
                self.log_message("No profile found - using default settings")
                return
            
            # Load profile data
            self.symbols.set(profile_data.get("symbols", ""))
            self.position_size.set(profile_data.get("position_size", str(Config.POSITION_SIZE)))
            self.stop_loss_pct.set(profile_data.get("stop_loss_pct", str(Config.STOP_LOSS_PCT * 100)))
            self.take_profit_pct.set(profile_data.get("take_profit_pct", str(Config.TAKE_PROFIT_PCT * 100)))
            self.vwap_buy_threshold.set(profile_data.get("vwap_buy_threshold", str(Config.VWAP_BUY_THRESHOLD)))
            self.vwap_sell_threshold.set(profile_data.get("vwap_sell_threshold", str(Config.VWAP_SELL_THRESHOLD)))
            self.rsi_overbought.set(profile_data.get("rsi_overbought", str(Config.RSI_OVERBOUGHT)))
            self.rsi_period.set(profile_data.get("rsi_period", str(Config.RSI_PERIOD)))
            self.refresh_interval.set(profile_data.get("refresh_interval", "5"))
            self.auto_refresh.set(profile_data.get("auto_refresh", True))
            
            self.log_message("Profile data loaded successfully")
        
        except Exception as e:
            self.log_message(f"Error loading profile data: {e}")
    
    def run(self):
        """Start the GUI."""
        self.log_message("VWAP Reversion Trading Bot GUI started")
        self.log_message("Click 'Connect to Alpaca' to begin")
        
        # Initial market status update
        self.update_market_status()
        
        self.root.mainloop()

def main():
    """Main function to run the GUI."""
    try:
        app = VWAPReversionGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        messagebox.showerror("Error", f"Error starting GUI: {e}")

if __name__ == "__main__":
    main()
