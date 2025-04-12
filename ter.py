import tkinter as tk
import pexpect  # type: ignore
from threading import Thread

class TerminalEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal")

        # 输出区域
        self.output_text = tk.Text(root, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # 输入框
        self.input_entry = tk.Entry(root)
        self.input_entry.pack(fill=tk.X, padx=5, pady=5)
        self.input_entry.bind("<Return>", self.on_enter)
        self.input_entry.focus()  # 自动聚焦输入框

        # 启动子进程
        self.child = pexpect.spawn("/bin/bash", encoding="utf-8")
        self.child.expect(["\\$", "#", ">"])  # 匹配通用提示符
        

        # 输出监听线程
        self.running = True
        self.output_thread = Thread(target=self.read_child_output, daemon=True)
        self.output_thread.start()

    def on_enter(self, event):
        command = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        self.append_output(f"$ {command}\n")
        self.child.sendline(command)
        self.child.flush()

    def read_child_output(self):
        while self.running:
            try:
                index = self.child.expect(["\n", pexpect.EOF, pexpect.TIMEOUT], timeout=0.1)
                if index == 0:
                    self.append_output(self.child.before)
                elif index == 1:
                    self.append_output("\n[Process exited]")
                    break
            except Exception as e:
                self.append_output(f"\nError: {str(e)}")
                break

    def append_output(self, text):
        def safe_append():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        self.root.after(0, safe_append)

    def on_close(self):
        self.running = False
        if self.child.isalive():
            self.child.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TerminalEmulator(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()