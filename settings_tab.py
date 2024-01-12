# settings_tab.py
import tkinter as tk
from tkinter import ttk
import json

CONFIG_FILE = 'app_config.json'

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

class SettingsTab:
    def __init__(self, parent, style):
        self.parent = parent
        self.style = style
        self.config = load_config()
        self.create_widgets()

    def create_widgets(self):
        # 主题选择下拉框
        self.theme_label = ttk.Label(self.parent, text="主题:")
        self.theme_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.theme_combobox = ttk.Combobox(self.parent, values=self.style.theme_names(), state='readonly')
        self.theme_combobox.set(self.config.get('theme', 'default'))
        self.theme_combobox.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.theme_combobox.bind('<<ComboboxSelected>>', self.change_theme)

        # 其他设置控件可以继续添加

    def change_theme(self, event):
        new_theme = self.theme_combobox.get()
        self.style.theme_use(new_theme)
        self.config['theme'] = new_theme
        save_config(self.config)
