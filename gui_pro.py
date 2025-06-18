import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import threading
import time
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ProCryptoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💎 Pro Crypto Simulator")
        self.root.geometry("1600x1000")
        self.root.resizable(True, True)
        
        self.load_config()
        
        self.prices = {
            'BTC': 45000.0, 'ETH': 3200.0, 'BNB': 420.0, 'ADA': 1.8,
            'SOL': 120.0, 'DOT': 28.0, 'LINK': 18.5, 'MATIC': 1.2
        }
        
        self.balance = 10000.0
        self.portfolio = {token: 0.0 for token in self.prices}
        self.stats = {
            'total_trades': 0, 'win_rate': 0.0, 'total_profit': 0.0,
            'best_trade': 0.0, 'worst_trade': 0.0, 'roi': 0.0,
            'trade_history': []
        }
        
        self.price_history = {token: [] for token in self.prices}
        self.time_history = []
        
        self.mining_power = 1.0
        self.mining_active = False
        self.total_earned = 0.0
        
        self.setup_styles()
        self.create_interface()
        self.start_updates()
        
    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except:
            self.config = {
                "theme": "light",
                "language": "ru",
                "themes": {
                    "light": {
                        "bg_main": "#f8fafc",
                        "bg_card": "#ffffff",
                        "primary": "#3b82f6",
                        "success": "#10b981",
                        "text_primary": "#1e293b"
                    }
                },
                "languages": {
                    "ru": {"app_title": "💎 Pro Crypto Simulator"}
                }
            }
        
        self.current_theme = self.config["themes"][self.config["theme"]]
        self.texts = self.config["languages"][self.config["language"]]
        
    def save_config(self):
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            
    def setup_styles(self):
        self.root.configure(bg=self.current_theme["bg_main"])
        
        try:
            self.fonts = {
                'title': ('Inter', 24, 'bold'),
                'header': ('Inter', 18, 'bold'),
                'body': ('Inter', 11),
                'button': ('Inter', 10, 'bold'),
                'number': ('JetBrains Mono', 12, 'bold'),
                'small': ('Inter', 9)
            }
        except:
            self.fonts = {
                'title': ('Segoe UI', 24, 'bold'),
                'header': ('Segoe UI', 18, 'bold'),
                'body': ('Segoe UI', 11),
                'button': ('Segoe UI', 10, 'bold'),
                'number': ('Consolas', 12, 'bold'),
                'small': ('Segoe UI', 9)
            }
            
    def create_interface(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_main_tab()
        self.create_stats_tab()
        self.create_settings_tab()
        
    def create_main_tab(self):
        main_frame = tk.Frame(self.notebook, bg=self.current_theme["bg_main"])
        self.notebook.add(main_frame, text="📊 Торговля")
        
        self.create_header(main_frame)
        
        content_frame = tk.Frame(main_frame, bg=self.current_theme["bg_main"])
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.create_quick_stats(content_frame)
        
        panels_frame = tk.Frame(content_frame, bg=self.current_theme["bg_main"])
        panels_frame.pack(fill='both', expand=True, pady=20)
        
        left_frame = tk.Frame(panels_frame, bg=self.current_theme["bg_main"])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = tk.Frame(panels_frame, bg=self.current_theme["bg_main"])
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.create_market_panel(left_frame)
        self.create_trading_panel(right_frame)
        self.create_portfolio_panel(right_frame)
        self.create_mining_panel(left_frame)
        
    def create_stats_tab(self):
        stats_frame = tk.Frame(self.notebook, bg=self.current_theme["bg_main"])
        self.notebook.add(stats_frame, text="📈 Статистика")
        
        tk.Label(stats_frame, text="📈 ДЕТАЛЬНАЯ СТАТИСТИКА",
                font=self.fonts['title'],
                bg=self.current_theme["bg_main"],
                fg=self.current_theme["text_primary"]).pack(pady=20)
        
        stats_container = tk.Frame(stats_frame, bg=self.current_theme["bg_main"])
        stats_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.create_key_metrics(stats_container)
        self.create_charts_panel(stats_container)
        
    def create_settings_tab(self):
        settings_frame = tk.Frame(self.notebook, bg=self.current_theme["bg_main"])
        self.notebook.add(settings_frame, text="⚙️ Настройки")
        
        tk.Label(settings_frame, text="⚙️ НАСТРОЙКИ",
                font=self.fonts['title'],
                bg=self.current_theme["bg_main"],
                fg=self.current_theme["text_primary"]).pack(pady=20)
        
        settings_container = self.create_card(settings_frame, width=600, height=400)
        settings_container.pack(pady=20)
        
        theme_frame = tk.Frame(settings_container, bg=self.current_theme["bg_card"])
        theme_frame.pack(fill='x', padx=30, pady=20)
        
        tk.Label(theme_frame, text="Тема оформления:",
                font=self.fonts['body'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).pack(anchor='w')
        
        self.theme_var = tk.StringVar(value=self.config["theme"])
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                  values=list(self.config["themes"].keys()),
                                  state="readonly", font=self.fonts['body'])
        theme_combo.pack(fill='x', pady=5)
        
        lang_frame = tk.Frame(settings_container, bg=self.current_theme["bg_card"])
        lang_frame.pack(fill='x', padx=30, pady=10)
        
        tk.Label(lang_frame, text="Язык интерфейса:",
                font=self.fonts['body'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).pack(anchor='w')
        
        self.lang_var = tk.StringVar(value=self.config["language"])
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var,
                                 values=list(self.config["languages"].keys()),
                                 state="readonly", font=self.fonts['body'])
        lang_combo.pack(fill='x', pady=5)
        
        buttons_frame = tk.Frame(settings_container, bg=self.current_theme["bg_card"])
        buttons_frame.pack(fill='x', padx=30, pady=20)
        
        save_btn = tk.Button(buttons_frame, text="💾 Сохранить",
                            font=self.fonts['button'],
                            bg=self.current_theme["success"],
                            fg="white", border=0,
                            padx=20, pady=10,
                            command=self.save_settings)
        save_btn.pack(side='right', padx=(10, 0))
        
        reset_btn = tk.Button(buttons_frame, text="🔄 Сброс",
                             font=self.fonts['button'],
                             bg=self.current_theme.get("warning", "#f59e0b"),
                             fg="white", border=0,
                             padx=20, pady=10,
                             command=self.reset_game)
        reset_btn.pack(side='right')
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.current_theme.get("bg_header", "#1e293b"), height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=header_frame['bg'])
        header_content.pack(fill='both', expand=True, padx=30, pady=20)
        
        title_label = tk.Label(header_content,
                              text=self.texts.get("app_title", "💎 Pro Crypto Simulator"),
                              font=self.fonts['title'],
                              bg=header_frame['bg'],
                              fg="white")
        title_label.pack(side='left')
        
        self.time_label = tk.Label(header_content, text="",
                                  font=self.fonts['body'],
                                  bg=header_frame['bg'],
                                  fg="white")
        self.time_label.pack(side='right')
        
    def create_quick_stats(self, parent):
        stats_frame = self.create_card(parent, height=120)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        stats_container = tk.Frame(stats_frame, bg=self.current_theme["bg_card"])
        stats_container.pack(fill='both', expand=True, padx=30, pady=20)
        
        balance_frame = tk.Frame(stats_container, bg=self.current_theme["bg_card"])
        balance_frame.pack(side='left', padx=(0, 40))
        
        tk.Label(balance_frame, text="💰 Баланс",
                font=self.fonts['body'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme.get("text_secondary", "#64748b")).pack()
        
        self.balance_label = tk.Label(balance_frame,
                                     text=f"${self.balance:,.2f}",
                                     font=self.fonts['number'],
                                     bg=self.current_theme["bg_card"],
                                     fg=self.current_theme["success"])
        self.balance_label.pack()
        
        portfolio_frame = tk.Frame(stats_container, bg=self.current_theme["bg_card"])
        portfolio_frame.pack(side='left', padx=(0, 40))
        
        tk.Label(portfolio_frame, text="📊 Портфель",
                font=self.fonts['body'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme.get("text_secondary", "#64748b")).pack()
        
        self.portfolio_value_label = tk.Label(portfolio_frame,
                                             text="$0.00",
                                             font=self.fonts['number'],
                                             bg=self.current_theme["bg_card"],
                                             fg=self.current_theme["primary"])
        self.portfolio_value_label.pack()
        
        profit_frame = tk.Frame(stats_container, bg=self.current_theme["bg_card"])
        profit_frame.pack(side='left', padx=(0, 40))
        
        tk.Label(profit_frame, text="📈 Прибыль",
                font=self.fonts['body'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme.get("text_secondary", "#64748b")).pack()
        
        self.profit_label = tk.Label(profit_frame,
                                    text=f"${self.stats['total_profit']:.2f}",
                                    font=self.fonts['number'],
                                    bg=self.current_theme["bg_card"],
                                    fg=self.current_theme["success"])
        self.profit_label.pack()
        
        winrate_frame = tk.Frame(stats_container, bg=self.current_theme["bg_card"])
        winrate_frame.pack(side='left')
        
        tk.Label(winrate_frame, text="🎯 Win Rate",
                font=self.fonts['body'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme.get("text_secondary", "#64748b")).pack()
        
        self.winrate_label = tk.Label(winrate_frame,
                                     text="0%",
                                     font=self.fonts['number'],
                                     bg=self.current_theme["bg_card"],
                                     fg=self.current_theme.get("info", "#8b5cf6"))
        self.winrate_label.pack()
        
    def create_key_metrics(self, parent):
        metrics_frame = self.create_card(parent, height=200)
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(metrics_frame, text="🏆 КЛЮЧЕВЫЕ МЕТРИКИ",
                font=self.fonts['header'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).pack(pady=15)
        
        metrics_container = tk.Frame(metrics_frame, bg=self.current_theme["bg_card"])
        metrics_container.pack(fill='both', expand=True, padx=30, pady=10)
        
        metrics_data = [
            ("Всего сделок", self.stats['total_trades'], "🔄"),
            ("Успешных сделок", self.stats['successful_trades'], "✅"),
            ("Лучшая сделка", f"${self.stats['best_trade']:.2f}", "🚀"),
            ("Худшая сделка", f"${self.stats['worst_trade']:.2f}", "📉"),
            ("ROI", f"{((self.balance - self.stats['start_balance']) / self.stats['start_balance'] * 100):.1f}%", "📊"),
            ("Майнинг заработок", f"${self.total_earned:.2f}", "⛏️")
        ]
        
        for i, (label, value, icon) in enumerate(metrics_data):
            row = i // 3
            col = i % 3
            
            metric_frame = tk.Frame(metrics_container, bg=self.current_theme.get("border", "#e2e8f0"))
            metric_frame.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
            
            tk.Label(metric_frame, text=f"{icon} {label}",
                    font=self.fonts['small'],
                    bg=metric_frame['bg'],
                    fg=self.current_theme.get("text_secondary", "#64748b")).pack(pady=5)
            
            tk.Label(metric_frame, text=str(value),
                    font=self.fonts['number'],
                    bg=metric_frame['bg'],
                    fg=self.current_theme["text_primary"]).pack(pady=2)
        
        for i in range(3):
            metrics_container.grid_columnconfigure(i, weight=1)
            
    def create_charts_panel(self, parent):
        charts_frame = self.create_card(parent, height=400)
        charts_frame.pack(fill='both', expand=True)
        
        tk.Label(charts_frame, text="📊 ГРАФИКИ ЦЕН",
                font=self.fonts['header'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).pack(pady=15)
        
        try:
            self.create_price_chart(charts_frame)
        except Exception as e:
            tk.Label(charts_frame, text=f"Графики недоступны: {e}",
                    font=self.fonts['body'],
                    bg=self.current_theme["bg_card"],
                    fg=self.current_theme.get("text_secondary", "#64748b")).pack(expand=True)
            
    def create_price_chart(self, parent):
        fig, ax = plt.subplots(figsize=(12, 6), facecolor=self.current_theme["bg_card"])
        ax.set_facecolor(self.current_theme["bg_card"])
        
        x = np.linspace(0, 100, 100)
        for i, (token, price) in enumerate(list(self.prices.items())[:4]):
            y = price + np.sin(x/10 + i) * price * 0.1 + np.random.normal(0, price*0.02, 100)
            ax.plot(x, y, label=token, linewidth=2)
        
        ax.set_title('Динамика цен криптовалют', color=self.current_theme["text_primary"])
        ax.set_xlabel('Время', color=self.current_theme["text_primary"])
        ax.set_ylabel('Цена ($)', color=self.current_theme["text_primary"])
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=10)
        
    def create_market_panel(self, parent):
        market_card = self.create_card(parent, height=400)
        market_card.pack(fill='both', expand=True, pady=(0, 20))
        
        header_frame = tk.Frame(market_card, bg=self.current_theme["bg_card"])
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(header_frame, text="📊 Рынок Криптовалют",
                font=self.fonts['header'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).pack(side='left')
        
        refresh_btn = tk.Button(header_frame, text="🔄 Обновить",
                               font=self.fonts['body'],
                               bg=self.current_theme["primary"],
                               fg="white", border=0,
                               padx=15, pady=5,
                               command=self.manual_update)
        refresh_btn.pack(side='right')
        
        self.market_container = tk.Frame(market_card, bg=self.current_theme["bg_card"])
        self.market_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        headers_frame = tk.Frame(self.market_container, bg=self.current_theme.get("border", "#e2e8f0"))
        headers_frame.pack(fill='x', pady=(0, 10))
        
        headers = ['Монета', 'Цена', 'Изменение', 'Действие']
        for i, header in enumerate(headers):
            label = tk.Label(headers_frame, text=header,
                           font=self.fonts['body'],
                           bg=headers_frame['bg'],
                           fg=self.current_theme["text_primary"],
                           pady=10)
            label.grid(row=0, column=i, sticky='ew', padx=5)
            
        for i in range(4):
            headers_frame.grid_columnconfigure(i, weight=1)
            
        self.tokens_container = tk.Frame(self.market_container, bg=self.current_theme["bg_card"])
        self.tokens_container.pack(fill='both', expand=True)
        
    def create_trading_panel(self, parent):
        trading_card = self.create_card(parent, height=280)
        trading_card.pack(fill='x', pady=(0, 20))
        
        tk.Label(trading_card, text="💱 Торговля",
                font=self.fonts['header'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).pack(pady=(20, 15))
        
        form_frame = tk.Frame(trading_card, bg=self.current_theme["bg_card"])
        form_frame.pack(padx=30, pady=10)
        
        tk.Label(form_frame, text="Выберите монету:",
                font=self.fonts['body'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).grid(row=0, column=0, sticky='w', pady=5)
        
        self.token_var = tk.StringVar(value="BTC")
        token_combo = ttk.Combobox(form_frame, textvariable=self.token_var,
                                  values=list(self.prices.keys()),
                                  state="readonly", font=self.fonts['body'])
        token_combo.grid(row=0, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        tk.Label(form_frame, text="Количество:",
                font=self.fonts['body'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).grid(row=1, column=0, sticky='w', pady=5)
        
        self.amount_entry = tk.Entry(form_frame, font=self.fonts['body'])
        self.amount_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        buttons_frame = tk.Frame(form_frame, bg=self.current_theme["bg_card"])
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        buy_btn = tk.Button(buttons_frame, text="📈 КУПИТЬ",
                           font=self.fonts['button'],
                           bg=self.current_theme["success"],
                           fg="white", border=0,
                           padx=25, pady=10,
                           command=self.buy_token)
        buy_btn.pack(side='left', padx=(0, 10))
        
        sell_btn = tk.Button(buttons_frame, text="📉 ПРОДАТЬ",
                            font=self.fonts['button'],
                            bg=self.current_theme.get("danger", "#ef4444"),
                            fg="white", border=0,
                            padx=25, pady=10,
                            command=self.sell_token)
        sell_btn.pack(side='left')
        
        form_frame.grid_columnconfigure(1, weight=1)
        
    def create_portfolio_panel(self, parent):
        portfolio_card = self.create_card(parent, height=320)
        portfolio_card.pack(fill='both', expand=True)
        
        tk.Label(portfolio_card, text="👛 Мой Портфель",
                font=self.fonts['header'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).pack(pady=(20, 15))
        
        self.portfolio_container = tk.Frame(portfolio_card, bg=self.current_theme["bg_card"])
        self.portfolio_container.pack(fill='both', expand=True, padx=20, pady=10)
        
    def create_mining_panel(self, parent):
        mining_card = self.create_card(parent, height=200)
        mining_card.pack(fill='x')
        
        tk.Label(mining_card, text="⛏️ Майнинг",
                font=self.fonts['header'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).pack(pady=(20, 15))
        
        info_frame = tk.Frame(mining_card, bg=self.current_theme["bg_card"])
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text=f"Мощность: {self.mining_power:.1f} TH/s",
                font=self.fonts['body'],
                bg=self.current_theme["bg_card"],
                fg=self.current_theme["text_primary"]).pack()
        
        buttons_frame = tk.Frame(mining_card, bg=self.current_theme["bg_card"])
        buttons_frame.pack(pady=15)
        
        self.mining_btn = tk.Button(buttons_frame, text="▶️ НАЧАТЬ МАЙНИНГ",
                                   font=self.fonts['button'],
                                   bg=self.current_theme["success"],
                                   fg="white", border=0,
                                   padx=20, pady=8,
                                   command=self.toggle_mining)
        self.mining_btn.pack(side='left', padx=(0, 10))
        
        upgrade_btn = tk.Button(buttons_frame, text="🔧 УЛУЧШИТЬ",
                               font=self.fonts['button'],
                               bg=self.current_theme.get("warning", "#f59e0b"),
                               fg="white", border=0,
                               padx=20, pady=8,
                               command=self.upgrade_mining)
        upgrade_btn.pack(side='left')
        
    def create_card(self, parent, width=None, height=None):
        card = tk.Frame(parent, bg=self.current_theme["bg_card"], relief='solid', bd=1)
        if width:
            card.configure(width=width)
        if height:
            card.configure(height=height)
        return card
        
    def start_updates(self):
        self.update_prices()
        self.update_time()
        
    def update_prices(self):
        for token in self.prices:
            change = random.uniform(-0.05, 0.05)
            self.prices[token] *= (1 + change)
            self.prices[token] = max(0.01, self.prices[token])
            
        self.time_history.append(datetime.now())
        for token, price in self.prices.items():
            self.price_history[token].append(price)
            
        if len(self.time_history) > 100:
            self.time_history = self.time_history[-100:]
            for token in self.price_history:
                self.price_history[token] = self.price_history[token][-100:]
            
        self.update_market_display()
        self.update_portfolio_display()
        self.update_stats_display()
        
        self.root.after(3000, self.update_prices)
        
    def update_time(self):
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        if hasattr(self, 'time_label'):
            self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
        
    def update_market_display(self):
        if not hasattr(self, 'tokens_container'):
            return
            
        for widget in self.tokens_container.winfo_children():
            widget.destroy()
            
        for i, (symbol, price) in enumerate(self.prices.items()):
            row_frame = tk.Frame(self.tokens_container, 
                               bg=self.current_theme.get("hover", "#f1f5f9") if i % 2 == 0 else self.current_theme["bg_card"])
            row_frame.pack(fill='x', pady=2)
            
            tk.Label(row_frame, text=f"🪙 {symbol}",
                    font=self.fonts['body'],
                    bg=row_frame['bg'],
                    fg=self.current_theme["text_primary"]).grid(row=0, column=0, padx=15, pady=8, sticky='w')
            
            price_text = f"${price:.2f}" if price >= 1 else f"${price:.6f}"
            tk.Label(row_frame, text=price_text,
                    font=self.fonts['number'],
                    bg=row_frame['bg'],
                    fg=self.current_theme["text_primary"]).grid(row=0, column=1, padx=15, pady=8)
            
            change = random.uniform(-5, 5)
            change_text = f"{'▲' if change > 0 else '▼'} {change:+.2f}%"
            change_color = self.current_theme["success"] if change > 0 else self.current_theme.get("danger", "#ef4444")
            tk.Label(row_frame, text=change_text,
                    font=self.fonts['small'],
                    bg=row_frame['bg'],
                    fg=change_color).grid(row=0, column=2, padx=15, pady=8)
            
            quick_btn = tk.Button(row_frame, text="Купить",
                                 font=self.fonts['small'],
                                 bg=self.current_theme["primary"],
                                 fg="white", border=0,
                                 padx=15, pady=5,
                                 command=lambda s=symbol: self.quick_buy(s))
            quick_btn.grid(row=0, column=3, padx=15, pady=8)
            
            for j in range(4):
                row_frame.grid_columnconfigure(j, weight=1)
                
    def update_portfolio_display(self):
        if not hasattr(self, 'portfolio_container'):
            return
            
        for widget in self.portfolio_container.winfo_children():
            widget.destroy()
            
        if not self.portfolio:
            empty_label = tk.Label(self.portfolio_container,
                                  text="Ваш портфель пуст\n\nНачните торговать!",
                                  font=self.fonts['body'],
                                  bg=self.current_theme["bg_card"],
                                  fg=self.current_theme.get("text_secondary", "#64748b"),
                                  justify='center')
            empty_label.pack(expand=True)
        else:
            for symbol, amount in self.portfolio.items():
                value = amount * self.prices[symbol]
                
                asset_frame = tk.Frame(self.portfolio_container, bg=self.current_theme.get("border", "#e2e8f0"))
                asset_frame.pack(fill='x', pady=3, padx=5)
                
                info_frame = tk.Frame(asset_frame, bg=asset_frame['bg'])
                info_frame.pack(side='left', fill='both', expand=True, padx=15, pady=10)
                
                tk.Label(info_frame, text=f"🪙 {symbol}",
                        font=self.fonts['body'],
                        bg=asset_frame['bg'],
                        fg=self.current_theme["text_primary"]).pack(anchor='w')
                
                tk.Label(info_frame, text=f"Количество: {amount:.6f}",
                        font=self.fonts['small'],
                        bg=asset_frame['bg'],
                        fg=self.current_theme.get("text_secondary", "#64748b")).pack(anchor='w')
                
                value_frame = tk.Frame(asset_frame, bg=asset_frame['bg'])
                value_frame.pack(side='right', padx=15, pady=10)
                
                tk.Label(value_frame, text=f"${value:.2f}",
                        font=self.fonts['number'],
                        bg=asset_frame['bg'],
                        fg=self.current_theme["success"]).pack()
                        
    def update_stats_display(self):
        if hasattr(self, 'balance_label'):
            self.balance_label.configure(text=f"${self.balance:,.2f}")
        
        portfolio_value = sum(amount * self.prices[symbol] 
                             for symbol, amount in self.portfolio.items())
        if hasattr(self, 'portfolio_value_label'):
            self.portfolio_value_label.configure(text=f"${portfolio_value:,.2f}")
        
        if hasattr(self, 'profit_label'):
            self.profit_label.configure(text=f"${self.stats['total_profit']:.2f}")
        
        if hasattr(self, 'winrate_label'):
            if self.stats['total_trades'] > 0:
                win_rate = (self.stats['successful_trades'] / self.stats['total_trades']) * 100
                self.winrate_label.configure(text=f"{win_rate:.1f}%")
            else:
                self.winrate_label.configure(text="0%")
                
    def manual_update(self):
        self.update_prices()
        
    def quick_buy(self, symbol):
        self.token_var.set(symbol)
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, "0.01")
        self.buy_token()
        
    def buy_token(self):
        try:
            symbol = self.token_var.get()
            amount = float(self.amount_entry.get())
            cost = amount * self.prices[symbol]
            
            if cost <= self.balance:
                self.balance -= cost
                if symbol in self.portfolio:
                    self.portfolio[symbol] += amount
                else:
                    self.portfolio[symbol] = amount
                    
                self.stats['total_trades'] += 1
                profit = cost * random.uniform(-0.1, 0.2)
                self.stats['total_profit'] += profit
                
                if profit > 0:
                    self.stats['successful_trades'] += 1
                    
                if profit > self.stats['best_trade']:
                    self.stats['best_trade'] = profit
                    
                if profit < self.stats['worst_trade']:
                    self.stats['worst_trade'] = profit
                    
                self.stats['trade_history'].append({
                    'type': 'buy',
                    'symbol': symbol,
                    'amount': amount,
                    'price': self.prices[symbol],
                    'timestamp': datetime.now()
                })
                    
                messagebox.showinfo("✅ Успешная покупка!", 
                                   f"Куплено {amount} {symbol} за ${cost:.2f}")
                self.amount_entry.delete(0, tk.END)
            else:
                messagebox.showerror("❌ Ошибка", "Недостаточно средств!")
        except ValueError:
            messagebox.showerror("❌ Ошибка", "Введите корректное количество!")
            
    def sell_token(self):
        try:
            symbol = self.token_var.get()
            amount = float(self.amount_entry.get())
            
            if symbol in self.portfolio and self.portfolio[symbol] >= amount:
                revenue = amount * self.prices[symbol]
                self.balance += revenue
                self.portfolio[symbol] -= amount
                
                if self.portfolio[symbol] <= 0:
                    del self.portfolio[symbol]
                    
                self.stats['total_trades'] += 1
                profit = revenue * random.uniform(-0.1, 0.2)
                self.stats['total_profit'] += profit
                
                if profit > 0:
                    self.stats['successful_trades'] += 1
                    
                self.stats['trade_history'].append({
                    'type': 'sell',
                    'symbol': symbol,
                    'amount': amount,
                    'price': self.prices[symbol],
                    'timestamp': datetime.now()
                })
                    
                messagebox.showinfo("✅ Успешная продажа!", 
                                   f"Продано {amount} {symbol} за ${revenue:.2f}")
                self.amount_entry.delete(0, tk.END)
                self.update_portfolio_display()
            else:
                messagebox.showerror("❌ Ошибка", "Недостаточно токенов!")
        except ValueError:
            messagebox.showerror("❌ Ошибка", "Введите корректное количество!")
            
    def toggle_mining(self):
        if self.mining_active:
            self.mining_active = False
            self.mining_btn.configure(text="▶️ НАЧАТЬ МАЙНИНГ", bg=self.current_theme["success"])
        else:
            self.mining_active = True
            self.mining_btn.configure(text="⏹️ ОСТАНОВИТЬ", bg=self.current_theme.get("danger", "#ef4444"))
            self.start_mining_process()
            
    def start_mining_process(self):
        def mining_loop():
            while self.mining_active:
                time.sleep(5)
                if self.mining_active:
                    reward = self.mining_power * random.uniform(0.0001, 0.0005)
                    if "BTC" in self.portfolio:
                        self.portfolio["BTC"] += reward
                    else:
                        self.portfolio["BTC"] = reward
                    
                    self.total_earned += reward * self.prices["BTC"]
                    
        threading.Thread(target=mining_loop, daemon=True).start()
        
    def upgrade_mining(self):
        cost = int(self.mining_power * 1000)
        
        result = messagebox.askyesno("🔧 Улучшение майнинга", 
                                    f"Улучшить майнинг ферму за ${cost}?\n\n"
                                    f"Мощность: {self.mining_power:.1f} → {self.mining_power + 0.5:.1f} TH/s")
        if result:
            if self.balance >= cost:
                self.balance -= cost
                self.mining_power += 0.5
                messagebox.showinfo("✅ Успех!", "Майнинг ферма улучшена!")
            else:
                messagebox.showerror("❌ Ошибка", "Недостаточно средств!")
                
    def save_settings(self):
        self.config["theme"] = self.theme_var.get()
        self.config["language"] = self.lang_var.get()
        self.save_config()
        
        messagebox.showinfo("✅ Успех!", "Настройки сохранены!\nПерезапустите приложение для применения изменений.")
        
    def reset_game(self):
        result = messagebox.askyesno("🔄 Сброс игры", 
                                    "Вы уверены, что хотите сбросить все данные?\n\nЭто действие нельзя отменить!")
        if result:
            self.balance = 10000.0
            self.portfolio = {token: 0.0 for token in self.prices}
            self.stats = {
                'total_trades': 0, 'win_rate': 0.0, 'total_profit': 0.0,
                'best_trade': 0.0, 'worst_trade': 0.0, 'roi': 0.0,
                'trade_history': []
            }
            self.total_earned = 0.0
            self.mining_power = 1.0
            self.mining_active = False
            
            messagebox.showinfo("✅ Успех!", "Игра сброшена!")
            
    def run(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
        
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = ProCryptoGUI()
        app.run()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        input("Нажмите Enter для выхода...") 