import psutil
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

cpu_data = []

def update_data():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    cpu_label.config(text=f"CPU: {cpu}%")
    ram_label.config(text=f"RAM: {memory}%")
    disk_label.config(text=f"Disk: {disk}%")

    # Alert color
    cpu_label.config(fg="red" if cpu > 80 else "green")

    # Graph update
    cpu_data.append(cpu)
    if len(cpu_data) > 20:
        cpu_data.pop(0)

    ax.clear()
    ax.plot(cpu_data)
    ax.set_title("CPU Usage")
    canvas.draw()

    # Update processes
    for row in tree.get_children():
        tree.delete(row)

    processes = sorted(psutil.process_iter(['pid','name','cpu_percent']),
                       key=lambda p: p.info['cpu_percent'], reverse=True)[:10]

    for p in processes:
        tree.insert("", "end", values=(p.info['pid'], p.info['name'], p.info['cpu_percent']))

    root.after(1000, update_data)

def kill_process():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a process first!")
        return

    pid = tree.item(selected[0])['values'][0]

    try:
        p = psutil.Process(pid)
        p.terminate()
        messagebox.showinfo("Success", f"Process {pid} terminated")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Window
root = tk.Tk()
root.title("🔥 Advanced System Monitor")
root.geometry("700x550")
root.configure(bg="#1e1e1e")

# Labels
cpu_label = tk.Label(root, font=("Arial", 12), fg="green", bg="#1e1e1e")
cpu_label.pack()

ram_label = tk.Label(root, font=("Arial", 12), fg="white", bg="#1e1e1e")
ram_label.pack()

disk_label = tk.Label(root, font=("Arial", 12), fg="white", bg="#1e1e1e")
disk_label.pack()

# Graph
fig, ax = plt.subplots(figsize=(6,2))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Table
columns = ("PID", "Name", "CPU %")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)

for col in columns:
    tree.heading(col, text=col)

tree.pack(fill="both", expand=True)

# Kill button
kill_btn = tk.Button(root, text="❌ Kill Process", command=kill_process, bg="red", fg="white")
kill_btn.pack(pady=10)

update_data()
root.mainloop()
