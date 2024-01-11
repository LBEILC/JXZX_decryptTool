import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from pathlib import Path

from decrypt import decrypt
from encrypt import encode

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("交错战线 Assets 加密解密工具 V0.3")

        # 状态文本
        self.status_label = tk.Label(root, text="未开始加密或解密")
        self.status_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        # 解密文件目录输入框
        tk.Label(root, text="解密assets文件目录:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.decrypt_entry = tk.Entry(root, width=50)
        self.decrypt_entry.grid(row=1, column=1, padx=5, pady=5)
        # 解密选择按钮和解密按钮
        self.decrypt_select_button = tk.Button(root, text="选择", command=self.select_decrypt_folder)
        self.decrypt_select_button.grid(row=1, column=2, padx=5, pady=5)
        self.decrypt_button = tk.Button(root, text="解密", command=lambda: self.start_process(decrypt))
        self.decrypt_button.grid(row=1, column=3, padx=5, pady=5)

        # 加密文件目录输入框
        tk.Label(root, text="加密assets文件目录:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.encrypt_entry = tk.Entry(root, width=50)
        self.encrypt_entry.grid(row=2, column=1, padx=5, pady=5)
        # 加密选择按钮和加密按钮
        self.encrypt_select_button = tk.Button(root, text="选择", command=self.select_encrypt_folder)
        self.encrypt_select_button.grid(row=2, column=2, padx=5, pady=5)
        self.encrypt_button = tk.Button(root, text="加密", command=lambda: self.start_process(encode))
        self.encrypt_button.grid(row=2, column=3, padx=5, pady=5)

        # 选择index_cache文件按钮和显示所选文件的标签
        self.select_cache_button = tk.Button(root, text="选择index_cache文件", command=self.select_cache_file)
        self.select_cache_button.grid(row=3, column=0, padx=5, pady=5)
        self.cache_file_label = tk.Label(root, text="未选择index_cache文件")
        self.cache_file_label.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # 日志文件标签
        tk.Label(root, text="日志文件").grid(row=5, column=0, padx=5, pady=5, sticky="w")

        # 日志显示框（多行文本框）和滚动条
        self.log_text = scrolledtext.ScrolledText(root, height=10, width=80)
        self.log_text.grid(row=6, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

        # 配置行和列的权重，使得文本框能够随窗口大小变化而拉伸
        root.grid_rowconfigure(6, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # 用于存储用户选择的index_cache文件路径
        self.selected_cache_file = None

    def select_decrypt_folder(self):
        directory = filedialog.askdirectory()
        if directory:
            self.decrypt_entry.delete(0, tk.END)
            self.decrypt_entry.insert(0, directory)

    def select_encrypt_folder(self):
        directory = filedialog.askdirectory()
        if directory:
            self.encrypt_entry.delete(0, tk.END)
            self.encrypt_entry.insert(0, directory)

    def start_process(self, process_func):
        directory = self.decrypt_entry.get() if process_func == decrypt else self.encrypt_entry.get()
        if not directory:
            messagebox.showwarning("警告", "请选择一个有效的目录")
            return
        if process_func == encode and not self.selected_cache_file:
            messagebox.showwarning("警告", "请先选择一个index_cache文件")
            return
        self.disable_buttons(process_func)
        threading.Thread(target=self.run_process, args=(process_func, directory), daemon=True).start()

    def select_cache_file(self):
        file_path = filedialog.askopenfilename(initialdir="index_cache", title="选择index_cache文件", filetypes=[("JSON files", "*.json")])
        if file_path:
            self.selected_cache_file = file_path
            self.cache_file_label['text'] = Path(file_path).name  # 显示所选文件的名称

    def run_process(self, process_func, directory):
        try:
            path = Path(directory)
            if process_func == encode:
                process_func(path, self.selected_cache_file, self.log)
            elif process_func == decrypt:
                process_func(path, self.log)
            self.status_label['text'] = '完成'
            self.log(f'{process_func.__name__.capitalize()}完成\n')
        except Exception as e:
            messagebox.showerror("错误", str(e))
            self.log(f'错误: {e}\n')
        finally:
            self.enable_buttons(process_func)

    def log(self, message):
        self.log_text.insert(tk.END, message)  # 在多行文本框的末尾插入日志信息
        self.log_text.see(tk.END)  # 自动滚动到多行文本框的末尾

    def disable_buttons(self, process_func):
        self.decrypt_button['state'] = 'disabled'
        self.encrypt_button['state'] = 'disabled'
        self.select_cache_button['state'] = 'disabled'
        action_text = '加密' if process_func == encode else '解密'
        self.status_label['text'] = f'正在{action_text}...'

    def enable_buttons(self, process_func):
        self.decrypt_button['state'] = 'normal'
        self.encrypt_button['state'] = 'normal'
        self.select_cache_button['state'] = 'normal'
        action_text = '加密' if process_func == encode else '解密'
        self.status_label['text'] = f'{action_text}完成'

# 创建并运行应用程序
root = tk.Tk()
app = App(root)
root.mainloop()
