import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ttkbootstrap import Style
import subprocess
import os
import signal
import re
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

# Initialize ttkbootstrap style
executor = ThreadPoolExecutor(max_workers=4)
style = Style(theme='litera')

# Global variable
vpn_process = None
servers = [
    {"name": "Japan(GPT/Netflix/Youtube)No.1", "ip": "20.27.92.68", "port": "6666", "latency": "N/A", "usage": "50.0%"},
    {"name": "USA(GPT/Netflix/Youtube)No.2", "ip": "170.106.178.152", "port": "1959", "latency": "N/A", "usage": "30.0%"},
]


def run_vpn_command(select_server):
    global vpn_process
    if not select_server:
        messagebox.showerror("Error", "Unknown server selected.")
        return
    cmd = f"sudo ./lwvpn client vpn.key {select_server['ip']} {select_server['port']}"
    try:
        vpn_process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start VPN process: {e}")


def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text
        else:
            return None
    except requests.RequestException:
        return None

def check_connection(type=1):
    #check connection status through two methods according to the type value
    if type:
        with open('status.units', "r") as file:
            status = file.read(1)
        if status == 'T':
            app.after(0, lambda: status_label.config(text="Status: Connected"))
        elif status == 'F':
            app.after(0, lambda: status_label.config(text="Status: Disconnected"))
        else:
            app.after(0, lambda: status_label.config(text="Status: Unknown"))
    else:
        ip_local = get_public_ip()
        for ip_server in servers:
            if ip_server['ip'] == ip_local:
                app.after(0, lambda: status_label.config(text="Status: Connected"))
                break
            else:
                app.after(0, lambda: status_label.config(text="Status: Disconnected"))

# # For main thread to check the connection status, improving the smoothness of the GUI
def check_connect_thread():
    thread = threading.Thread(target=check_connection)
    thread.daemon = True
    thread.start()
    #app.after(8000, check_connect_thread)


def connect_vpn():
    if tree.selection() == ():
        messagebox.showwarning("VPN Connection", "No server selected.")
        return
    if vpn_process:
        messagebox.showwarning("VPN Connection", "A VPN connection is already active.")
        return
    selected_server_name = tree.item(tree.selection())['values'][0]
    selected_server = next((server for server in servers if server['name'] == selected_server_name), None)
    run_vpn_command(selected_server)
    messagebox.showinfo("VPN Connection", f"Connecting to {selected_server_name}...")
    executor.submit(check_connection)


def disconnect_vpn():
    global vpn_process
    if vpn_process:
        print("Attempting to disconnect VPN...")
        try:
            os.killpg(os.getpgid(vpn_process.pid), signal.SIGINT)
            vpn_process = None
            messagebox.showinfo("VPN Connection", "Disconnected VPN.")
            executor.submit(check_connection)
            print("VPN disconnected successfully.")
        except Exception as e:
            print(f"Error disconnecting VPN: {e}")
    else:
        messagebox.showwarning("VPN Connection", "No VPN connection is active.")


def parse_latency(output):
    match = re.search(r"time=(\d+\.?\d*)\s*ms", output)
    if match:
        return match.group(1)
    else:
        return "N/A"

def update_latency(server):
    try:
        ip = server['ip']
        # using ping to detect the latency
        result = subprocess.run(['ping', '-c', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if result.returncode == 0:
            latency = parse_latency(result.stdout)
            server['latency'] = latency + " ms"
        else:
            server['latency'] = "N/A"
    except Exception as e:
        server['latency'] = "Error"
    finally:
        item_id = item_ids[server['name']]
        app.after(0, lambda: tree.item(item_id, values=(server['name'], server['usage'], server['latency'])))

def update_server_latency():
    for server in servers:
        executor.submit(update_latency, server)
    app.after(8000, update_server_latency)


def on_closing():
    if vpn_process:
        vpn_process.terminate()
        try:
            vpn_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            vpn_process.kill()
    # 等待线程池中的任务完成再关闭
    executor.shutdown(wait=True)
    app.destroy()


# Create the main application window
app = style.master
app.title("LwVPN")
app.geometry('800x600')  # Set the window size
app.minsize(800, 600)  # Set the minimum size of the window

# Create a frame for user information
user_info_frame = ttk.Frame(app, padding="10")
user_info_frame.pack(side=tk.TOP, fill=tk.X)

# Email label
user_email_label = ttk.Label(user_info_frame, text="Email: user@example.com", anchor='center')
user_email_label.pack(side=tk.TOP, fill=tk.X)

# Expiration label
expiration_time_label = ttk.Label(user_info_frame, text="Expires: 2024/2/5 21:02", anchor='center')
expiration_time_label.pack(side=tk.TOP, fill=tk.X)

# Data usage label
data_usage_label = ttk.Label(user_info_frame, text="Data left: 999.0 GB", anchor='center')
data_usage_label.pack(side=tk.TOP, fill=tk.X)

# Create a frame for the server list
server_list_frame = ttk.Frame(app, padding="10")
server_list_frame.pack(fill=tk.BOTH, expand=True)

# Create a Treeview widget for the server list
columns = ("server", "usage", "latency", "status")
tree = ttk.Treeview(server_list_frame, columns=columns, show='headings')
tree.heading('server', text='Server')
tree.heading('usage', text='Usage')
tree.heading('latency', text='Latency')
tree.heading('status', text='Status')

# Set the columns' width and alignment
tree.column('server', anchor='center', width=180)
tree.column('usage', anchor='center', width=100)
tree.column('latency', anchor='center', width=100)
tree.column('status', anchor='center', width=100)

# Populate the treeview with the new server names
item_ids = {}
for server in servers:
    item_id = tree.insert('', 'end', values=(server['name'], server['usage'], server['latency']))
    item_ids[server['name']] = item_id

tree.pack(fill=tk.BOTH, expand=True)

# Create a frame for the status bar
status_frame = ttk.Frame(app, padding="10")
status_frame.pack(side=tk.BOTTOM, fill=tk.X)

status_label = ttk.Label(status_frame, text="Status: Disconnected")
status_label.pack(side=tk.LEFT)

# Create Connect and Disconnect buttons
button_frame = ttk.Frame(app, padding="10")
button_frame.pack(side=tk.BOTTOM, fill=tk.X)

connect_button = ttk.Button(button_frame, text="Connect", command=connect_vpn, bootstyle='success')
connect_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

disconnect_button = ttk.Button(button_frame, text="Disconnect", command=disconnect_vpn, bootstyle='danger')
disconnect_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

# Remove the default window icon
app.iconbitmap(None)

# Check the connection status every 1000 milliseconds
# app.after(1000, check_connection)
# app.after(8000, update_server_latency)
update_server_latency()
check_connect_thread()
# check_connection()

# Handle the window close event
app.protocol("WM_DELETE_WINDOW", on_closing)

# Run the application
app.mainloop()
