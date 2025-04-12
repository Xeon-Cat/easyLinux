import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import platform
import os
import sys

class EasyLinuxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("easyLinux")
        self.root.geometry("1000x700")
        
        # 主题设置
        self.themes = {
            "默认": {"bg": "#F0F0F0", "fg": "black", "text_bg": "white", "text_fg": "black"},
            "深色": {"bg": "#2E2E2E", "fg": "white", "text_bg": "#1E1E1E", "text_fg": "#CCCCCC"}
        }
        self.current_theme = "默认"

        # 创建菜单栏
        self.create_menu()
        
        # 主界面布局
        self.create_main_frame()
        
        # 状态栏
        self.status = tk.Label(root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # 初始化软件列表
        self.update_package_list()

    def create_menu(self):
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

    def create_main_frame(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧功能面板
        left_panel = ttk.LabelFrame(main_frame, text="软件管理")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 搜索框
        search_frame = ttk.Frame(left_panel)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="搜索软件:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text="搜索", command=self.search_packages).pack(side=tk.LEFT)
        
        # 软件列表
        self.software_list = tk.Listbox(left_panel, height=15)
        self.software_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 软件操作按钮
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="刷新列表", command=self.update_package_list).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="安装选中", command=self.install_selected).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="卸载选中", command=self.remove_selected).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 右侧功能面板
        right_panel = ttk.LabelFrame(main_frame, text="系统工具")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 系统信息
        ttk.Button(right_panel, text="显示系统信息", 
                  command=self.show_system_info).pack(fill=tk.X, pady=2)
        
        # 快速命令
        quick_commands = [
            ("更新软件源", "sudo apt update"),
            ("升级系统", "sudo apt upgrade -y"),
            ("清理缓存", "sudo apt autoclean"),
            ("修复依赖", "sudo apt --fix-broken install")
        ]
        for text, cmd in quick_commands:
            ttk.Button(right_panel, text=text, 
                      command=lambda c=cmd: self.run_command_with_output(c)).pack(fill=tk.X, pady=2)
        
        # 文件管理器按钮
        ttk.Button(right_panel, text="文件管理器", 
                  command=self.open_file_manager).pack(fill=tk.X, pady=2)
        
        # 终端输出区域
        self.output_area = scrolledtext.ScrolledText(right_panel, height=10, wrap=tk.WORD)
        self.output_area.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output_area.config(state=tk.DISABLED)

    def update_package_list(self):
        self.software_list.delete(0, tk.END)
        try:
            # 使用环境变量禁用分页器和颜色
            env = dict(os.environ)
            env.update({"PAGER": "cat", "TERM": "dumb"})
            
            result = subprocess.run(
                ["apt", "list", "--installed"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            packages = [line.split("/")[0] for line in result.stdout.splitlines()[1:] if line]
            for pkg in sorted(packages):
                self.software_list.insert(tk.END, pkg)
                
            self.update_status(f"已加载 {len(packages)} 个已安装软件包")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"获取软件列表失败:\n{e.stderr}")

    def search_packages(self):
        query = self.search_entry.get()
        if not query:
            return
            
        try:
            env = dict(os.environ)
            env.update({"PAGER": "cat", "TERM": "dumb"})
            
            result = subprocess.run(
                ["apt", "search", query],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete(1.0, tk.END)
            self.output_area.insert(tk.END, result.stdout)
            self.output_area.config(state=tk.DISABLED)
            
            self.update_status(f"找到 {len(result.stdout.splitlines())} 个匹配结果")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"搜索失败:\n{e.stderr}")

    def install_selected(self):
        selection = self.software_list.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个软件包")
            return
            
        pkg = self.software_list.get(selection[0])
        self.run_command_with_output(f"sudo apt install -y {pkg}")

    def remove_selected(self):
        selection = self.software_list.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个软件包")
            return
            
        pkg = self.software_list.get(selection[0])
        self.run_command_with_output(f"sudo apt remove -y {pkg}")

    def run_command_with_output(self, command):
        try:
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete(1.0, tk.END)
            self.output_area.insert(tk.END, f"$ {command}\n\n")
            self.output_area.see(tk.END)
            self.output_area.config(state=tk.DISABLED)
            
            # 使用伪终端模拟真实终端行为
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 实时显示输出
            for line in process.stdout:
                self.output_area.config(state=tk.NORMAL)
                self.output_area.insert(tk.END, line)
                self.output_area.see(tk.END)
                self.output_area.config(state=tk.DISABLED)
                self.root.update()
                
            process.wait()
            
            if process.returncode == 0:
                self.update_status("命令执行成功")
            else:
                self.update_status("命令执行失败")
                
            # 如果是软件操作，更新列表
            if "apt install" in command or "apt remove" in command:
                self.update_package_list()
                
        except Exception as e:
            messagebox.showerror("错误", f"执行命令时出错:\n{str(e)}")

    def open_file_manager(self):
        filedialog.askdirectory(title="选择目录")

    def show_system_info(self):
        try:
            info = f"""系统信息:
            
            操作系统: {platform.system()}
            发行版本: {platform.freedesktop_os_release().get('PRETTY_NAME', '未知')}
            内核版本: {platform.release()}
            系统架构: {platform.machine()}
            
            内存信息:
            {subprocess.getoutput('free -h')}
            
            磁盘信息:
            {subprocess.getoutput('df -h')}
            """
            
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete(1.0, tk.END)
            self.output_area.insert(tk.END, info)
            self.output_area.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("错误", f"获取系统信息失败:\n{str(e)}")

    def change_theme(self):
        self.current_theme = "深色" if self.current_theme == "默认" else "默认"
        theme = self.themes[self.current_theme]
        
        # 更新主窗口颜色
        self.root.config(bg=theme["bg"])
        
        # 更新状态栏颜色
        self.status.config(bg=theme["bg"], fg=theme["fg"])
        
        # 更新输出区域颜色
        self.output_area.config(
            bg=theme["text_bg"],
            fg=theme["text_fg"],
            insertbackground=theme["text_fg"]
        )
        
        self.update_status(f"已切换至 {self.current_theme} 主题")

    def show_about(self):
        about_text = """easyLinux 助手 v1.1
        
        为Linux新手设计的图形界面工具
        提供软件管理、系统维护等功能
        
        作者: XYG_Cat
        许可证: GPLv3
        """
        messagebox.showinfo("关于", about_text)

    def update_status(self, message):
        self.status.config(text=message)
        self.root.after(5000, lambda: self.status.config(text="就绪"))

if __name__ == "__main__":
    if os.getuid() > 0:
        messagebox.showerror("错误", "需要 root 权限")
        sys.exit(1)
    root = tk.Tk()
    app = EasyLinuxApp(root)
    root.mainloop()