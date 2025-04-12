import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import platform
import pexpect # type: ignore
from threading import Thread

import re

NO_COLOR_CMD = r" | sed -r 's/\x1B\[[0-9;]*[mK]//g'"

def remove_colors(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

class TerminalEmulator:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        # 终端输出区域
        self.output_text = tk.Text(parent, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 命令输入框
        self.input_entry = tk.Entry(parent)
        self.input_entry.pack(fill=tk.X, padx=5, pady=5)
        self.input_entry.bind("<Return>", self.on_enter)
        self.input_entry.focus()
        
        # 启动bash子进程
        self.child = pexpect.spawn("/bin/bash", encoding="utf-8")
        self.child.expect(["\\$", "#", ">", "password", ":", "\\?", "[sudo]"])
        
        # 输出监听线程
        self.running = True
        self.output_thread = Thread(target=self.read_child_output, daemon=True)
        self.output_thread.start()

        self.send_command("su root")
        self.app.update_status("请输入 root 密码")

    def on_enter(self, event):
        """处理命令输入"""
        command = self.input_entry.get()
        self.app.update_status(command)
        self.input_entry.delete(0, tk.END)
        self.append_output(f"$ {command}\n")
        self.child.sendline(command)
        self.child.flush()

    def read_child_output(self):
        """持续读取子进程输出"""
        while self.running:
            try:
                index = self.child.expect(["\n", pexpect.EOF, pexpect.TIMEOUT], timeout=10.0)
                # print(index)
                if index == 0:
                    self.append_output(remove_colors(self.child.before))
                    print(self.child.before)
                    print(self.child.after)
                    self.append_output(remove_colors(self.child.after))
                    #if "#" in self.child.before or "$" in self.child.before:
                    #    self.append_output(self.child.after)
                    #    self.app.update_status("就绪1")
                elif index == 1:
                    self.append_output("\n[进程已退出]")
                    break

            except Exception as e:
                self.append_output(f"\n错误: {str(e)}")
                break

    def append_output(self, text):
        """安全更新文本区域"""
        def safe_append():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        self.parent.after(0, safe_append)

    def send_command(self, command):
        """从外部发送命令"""
        self.child.sendline(command)
        self.app.update_status(command)
        self.append_output(f"$ {command}\n")
        self.child.flush()

    def on_close(self):
        """关闭时清理资源"""
        self.running = False
        if self.child.isalive():
            self.child.terminate()

class EasyLinuxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("easyLinux")
        self.root.geometry("1000x820")
        
        # 主题配置
        self.themes = {
            "默认": {"bg": "#F0F0F0", "fg": "black"},
            "深色": {"bg": "#2E2E2E", "fg": "white"}
        }
        self.current_theme = "默认"

        # 创建界面组件
        self.create_menu()
        self.create_status_bar()
        self.create_main_interface()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="切换主题", command=self.change_theme)
        menubar.add_cascade(label="设置", menu=settings_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)

    def create_main_interface(self):
        self.update_status("创建主界面布局 ...")
        """创建主界面布局"""
        main_paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # 上半部分功能面板
        upper_frame = ttk.Frame(main_paned)
        main_paned.add(upper_frame, weight=1)
        
        # 左侧软件管理面板
        left_panel = ttk.LabelFrame(upper_frame, text="软件管理")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 软件安装组件
        ttk.Label(left_panel, text="安装软件：").grid(row=0, column=0, sticky=tk.W)
        self.pkg_entry = ttk.Entry(left_panel, width=30)
        self.pkg_entry.grid(row=0, column=1, padx=5)
        ttk.Button(left_panel, text="安装", command=self.install_package).grid(row=0, column=2)
        
        # 软件列表
        self.software_list = tk.Listbox(left_panel, height=15)
        self.software_list.grid(row=1, column=0, columnspan=3, pady=10, sticky=tk.NSEW)
        for pkg in ["firefox", "vlc", "gimp", "libreoffice"]:
            self.software_list.insert(tk.END, pkg)
        
        # 右侧系统工具面板
        right_panel = ttk.LabelFrame(upper_frame, text="系统工具")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 系统工具按钮
        ttk.Button(right_panel, text="显示系统信息", 
                  command=self.show_system_info).pack(fill=tk.X, pady=2)
        
        # 快速命令按钮
        quick_commands = [
            ("更新软件源", "sudo apt update"),
            ("升级系统", "sudo apt upgrade -y"),
            ("清理缓存", "sudo apt autoclean")
        ]
        for text, cmd in quick_commands:
            ttk.Button(right_panel, text=text, 
                      command=lambda c=cmd: self.terminal.send_command(c)).pack(fill=tk.X, pady=2)
        
        # 文件管理器按钮
        ttk.Button(right_panel, text="文件管理器", 
                  command=self.open_file_manager).pack(fill=tk.X, pady=2)
        
        # 下半部分终端面板
        self.update_status("启动内置终端 ...")
        terminal_frame = ttk.Frame(main_paned)
        main_paned.add(terminal_frame, weight=1)
        self.terminal = TerminalEmulator(terminal_frame, self)
        

    def create_status_bar(self):
        """创建状态栏"""
        self.status = tk.Label(self.root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def install_package(self):
        """安装软件包"""
        pkg = self.pkg_entry.get()
        if pkg:
            self.terminal.send_command(f"sudo apt install -y {pkg}")
            self.update_status(f"正在安装 {pkg}...")

    def open_file_manager(self):
        """打开文件管理器"""
        filedialog.askdirectory(title="选择目录")

    def show_system_info(self):
        """显示系统信息"""
        info = f"""
        系统类型: {platform.system()}
        发行版本: {platform.version()}
        系统架构: {platform.machine()}
        """
        messagebox.showinfo("系统信息", info)

    def change_theme(self):
        """切换主题"""
        self.current_theme = "深色" if self.current_theme == "默认" else "默认"
        theme = self.themes[self.current_theme]
        self.root.config(bg=theme["bg"])
        self.status.config(bg=theme["bg"], fg=theme["fg"])
        self.update_status(f"已切换至 {self.current_theme} 主题")

    def show_about(self):
        """显示关于信息"""
        about_text = """easyLinux 助手 alpha 1.0
        为Linux新手设计的图形界面工具
        作者: XYG_Cat
        """
        messagebox.showinfo("关于", about_text)

    def update_status(self, message):
        """更新状态栏"""
        self.status.config(text=message)

if __name__ == "__main__":
    messagebox.showinfo("提示", "本软件需使用 root \n请在使用之前使用 sudo 或在软件启动后，在下方输入框中使用 su root 命令，回车后，输入密码")
    root = tk.Tk()
    app = EasyLinuxApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.terminal.on_close(), root.destroy()])
    root.mainloop()