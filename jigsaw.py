import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import threading
import json

CONFIG_FILE = "config.json"

class PenTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("jigsaw")
        self.targets = []
        self.tool_vars = {}
        self.tool_config = self.load_config()
        self.setup_ui()

    def setup_ui(self):
        # -------------------------- 目标输入区域 --------------------------
        ttk.Label(self.root, text="目标 (IP/URL，每行一个):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.target_text = tk.Text(self.root, height=10, width=60)
        self.target_text.grid(row=1, column=0, padx=10, pady=5)
        
        # "导入目标" 按钮
        ttk.Button(self.root, text="从文件导入目标", command=self.import_targets).grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # -------------------------- 工具选择区域 --------------------------
        ttk.Label(self.root, text="选择渗透测试工具:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.tool_frame = ttk.Frame(self.root)  # 独立的Frame容器
        self.tool_frame.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.update_tool_selectors()

        # -------------------------- 工具管理按钮 --------------------------
        btn_frame = ttk.Frame(self.root)
        btn_frame.grid(row=5, column=0, padx=10, pady=5, sticky="w") 
        ttk.Button(btn_frame, text="添加工具", command=self.add_tool).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="删除工具", command=self.delete_tool).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="配置工具", command=self.configure_tools).pack(side="left", padx=5)

        # -------------------------- 开始测试按钮 --------------------------
        ttk.Button(self.root, text="开始测试", command=self.start_test).grid(row=6, column=0, padx=10, pady=10)

        # -------------------------- 状态输出区域 --------------------------
        ttk.Label(self.root, text="测试状态:").grid(row=7, column=0, padx=10, pady=10, sticky="w")
        self.status_text = tk.Text(self.root, height=10, width=60, state="disabled")
        self.status_text.grid(row=8, column=0, padx=10, pady=5)

        # 清空按钮
        ttk.Button(self.root, text="清空输出", command=self.clear_output).grid(row=9, column=0, padx=10, pady=10, sticky="w")

    def import_targets(self):
        """从文件导入目标"""
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as f:
                self.targets = [line.strip() for line in f.readlines() if line.strip()]
            self.target_text.delete(1.0, tk.END)
            self.target_text.insert(tk.END, "\n".join(self.targets))
            messagebox.showinfo("导入成功", f"已导入 {len(self.targets)} 个目标。")

    def update_tool_selectors(self):
        """动态更新工具选择区域"""
        # 清空之前的工具选择区域
        for widget in self.tool_frame.winfo_children():
            widget.destroy()

        # 动态生成工具选择区域
        for tool in self.tool_config.keys():
            var = tk.BooleanVar()
            self.tool_vars[tool] = var
            ttk.Checkbutton(self.tool_frame, text=tool, variable=var).pack(anchor="w", pady=2)

    def add_tool(self):
        """添加工具"""
        tool_name = simpledialog.askstring("添加工具", "请输入工具名称:")
        if tool_name:
            tool_path = simpledialog.askstring("添加工具", "请输入工具路径:")
            tool_command = simpledialog.askstring("添加工具", "请输入工具命令（使用 {target} 作为目标占位符）:")
            if tool_path and tool_command:
                self.tool_config[tool_name] = {"path": tool_path, "command": tool_command}
                self.save_config()
                self.update_tool_selectors()
                messagebox.showinfo("添加成功", f"工具 '{tool_name}' 已添加！")
            else:
                messagebox.showwarning("错误", "工具路径和命令不能为空！")

    def delete_tool(self):
        """删除工具"""
        tool_name = simpledialog.askstring("删除工具", "请输入要删除的工具名称:")
        if tool_name and tool_name in self.tool_config:
            del self.tool_config[tool_name]
            self.save_config()
            self.update_tool_selectors()
            messagebox.showinfo("删除成功", f"工具 '{tool_name}' 已删除！")
        elif tool_name:
            messagebox.showwarning("错误", f"工具 '{tool_name}' 不存在！")

    def configure_tools(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("配置工具")

        self.entries = {}  # 存储所有工具的输入框

        for idx, (tool, config) in enumerate(self.tool_config.items()):
            ttk.Label(config_window, text=tool).grid(row=idx, column=0, padx=10, pady=5)
            ttk.Label(config_window, text="路径:").grid(row=idx, column=1, padx=5, pady=5)
            path_entry = ttk.Entry(config_window, width=30)
            path_entry.insert(0, config.get("path", ""))
            path_entry.grid(row=idx, column=2, padx=5, pady=5)
            ttk.Label(config_window, text="命令:").grid(row=idx, column=3, padx=5, pady=5)
            command_entry = ttk.Entry(config_window, width=30)
            command_entry.insert(0, config.get("command", ""))
            command_entry.grid(row=idx, column=4, padx=5, pady=5)

            # 将输入框保存到字典中
            self.entries[tool] = {"path": path_entry, "command": command_entry}

        def save_config():
            for tool, entries in self.entries.items():
                self.tool_config[tool]["path"] = entries["path"].get()
                self.tool_config[tool]["command"] = entries["command"].get()
            self.save_config()
            messagebox.showinfo("保存成功", "工具配置已保存！")
            config_window.destroy()

        ttk.Button(config_window, text="保存配置", command=save_config).grid(row=len(self.tool_config), column=2, columnspan=3, padx=10, pady=10)


    def start_test(self):
        """开始测试"""
        # 获取目标和工具
        self.targets = self.target_text.get(1.0, tk.END).strip().splitlines()
        self.selected_tools = [tool for tool, var in self.tool_vars.items() if var.get()]

        if not self.targets:
            messagebox.showwarning("错误", "请输入至少一个目标！")
            return
        if not self.selected_tools:
            messagebox.showwarning("错误", "请选择至少一个工具！")
            return

        # 启动测试线程
        threading.Thread(target=self.run_tests, daemon=True).start()

    def run_tests(self):
        self.update_status("测试开始...\n")
        
        # 创建输出目录
        output_dir = "results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for target in self.targets:
            self.update_status(f"正在测试目标: {target}\n")
            for tool in self.selected_tools:
                self.update_status(f"正在运行 {tool}...\n")
                try:
                    config = self.tool_config[tool]
                    path = config.get("path", tool.split()[0].lower())
                    command = config.get("command", "").replace("{target}", target)
                    full_command = f"{path} {command}"
                    print(full_command)

                    # 获取工具路径的目录部分
                    tool_path = os.path.dirname(path)
                    # 获取工具文件名
                    tool_name = os.path.basename(path)


                    # 执行工具命令
                    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
                    self.update_status(result.stdout + "\n")

                    # 将结果保存到文件
                    output_file = os.path.join(output_dir, f"{tool}_{target.replace('/', '_')}.txt")
                    with open(output_file, "w") as f:
                        f.write(f"工具: {tool}\n")
                        f.write(f"目标: {target}\n")
                        f.write("命令: " + full_command + "\n")
                        f.write("输出结果:\n")
                        f.write(result.stdout)
                        f.write("\n错误输出:\n")
                        f.write(result.stderr)

                    self.update_status(f"结果已保存到: {output_file}\n")
                except Exception as e:
                    self.update_status(f"错误: {e}\n")
                finally:
                    # 恢复当前工作目录
                    os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.update_status("测试完成！\n")

    def update_status(self, message):
        """更新状态输出"""
        self.status_text.configure(state="normal")
        self.status_text.insert(tk.END, message)
        self.status_text.configure(state="disabled")
        self.status_text.see(tk.END)
        self.root.update()

    def clear_output(self):
        """清空输出"""
        self.status_text.configure(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.status_text.configure(state="disabled")

    def load_config(self):
        """加载工具配置"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {
            "Nmap (端口扫描)": {"path": "F:\\Nmap\\nmap.exe", "command": "-A -v {target}"},
            "Nikto (Web漏洞扫描)": {"path": "nikto", "command": "-h {target}"},
            "SQLmap (SQL注入测试)": {"path": "sqlmap", "command": "-u {target} --batch"}
        }

    def save_config(self):
        """保存工具配置"""
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.tool_config, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = PenTestApp(root)
    root.mainloop()

