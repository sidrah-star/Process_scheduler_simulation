import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import random
import time

ALGORITHMS = ["First Come First Serve", "Shortest Job First", "Round Robin", "Priority Scheduling"]

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Process Scheduler")
        self.root.geometry("1300x800")
        self.root.config(bg="#2A2A2A")
        self.font_large = ("Helvetica", 28, "bold")
        self.font_med = ("Helvetica", 20, "bold")
        self.font_small = ("Helvetica", 16, "bold")
        self.processes = []
        self.quantum = 2  # Quantum default for Round Robin

        self.setup_ui()

    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Process Scheduling Simulator", font=self.font_large, bg="#2A2A2A", fg="#00ffcc")
        title.pack(pady=15)

        # Add Process Button
        input_btn = tk.Button(self.root, text="Add Process", font=self.font_med, bg="#66CCFF", fg="#000000", command=self.add_process)
        input_btn.pack(pady=10)

        # Process Listbox
        self.proc_listbox = tk.Listbox(self.root, width=60, height=8, font=self.font_small, bg="#333333", fg="#FFFFFF", selectmode=tk.SINGLE)
        self.proc_listbox.pack(pady=10)

        # Quantum Input for Round Robin
        quantum_frame = tk.Frame(self.root, bg="#2A2A2A")
        quantum_frame.pack(pady=5)
        tk.Label(quantum_frame, text="Round Robin Quantum:", font=self.font_med, fg="#FFFFFF", bg="#2A2A2A").pack(side=tk.LEFT, padx=5)
        self.quantum_entry = tk.Spinbox(quantum_frame, from_=1, to=20, width=5, font=("Helvetica", 20))
        self.quantum_entry.pack(side=tk.LEFT, padx=5)
        self.quantum_entry.delete(0, "end")
        self.quantum_entry.insert(0, "2")

        # Algorithm selection
        frame_algo = tk.Frame(self.root, bg="#2A2A2A")
        frame_algo.pack(pady=10)
        tk.Label(frame_algo, text="Select Algorithm:", font=self.font_med, bg="#2A2A2A", fg="#FFFFFF").pack(side=tk.LEFT, padx=10)
        self.algo_var = tk.StringVar(value=ALGORITHMS[0])
        algo_menu = ttk.Combobox(frame_algo, values=ALGORITHMS, textvariable=self.algo_var, font=self.font_small, state='readonly')
        algo_menu.pack(side=tk.LEFT, padx=10)

        # Run & Reset buttons
        btn_frame = tk.Frame(self.root, bg="#2A2A2A")
        btn_frame.pack(pady=10)
        self.start_btn = tk.Button(btn_frame, text="Run Simulation", font=self.font_med, bg="#00ff99", fg="#000000", command=self.start_sim)
        self.start_btn.pack(side=tk.LEFT, padx=20)
        self.reset_btn = tk.Button(btn_frame, text="Reset", font=self.font_med, bg="#ff66aa", fg="#000000", command=self.reset_all)
        self.reset_btn.pack(side=tk.LEFT, padx=20)

        # Stats Labels Frame
        self.stats_frame = tk.Frame(self.root, bg="#2A2A2A")
        self.stats_frame.pack(pady=8)
        self.avg_waiting_var = tk.StringVar(value="Average Waiting Time: N/A")
        self.avg_turnaround_var = tk.StringVar(value="Average Turnaround Time: N/A")
        self.avg_response_var = tk.StringVar(value="Average Response Time: N/A")
        tk.Label(self.stats_frame, textvariable=self.avg_waiting_var, fg="white", bg="#2A2A2A", font=self.font_med).pack(side=tk.LEFT, padx=20)
        tk.Label(self.stats_frame, textvariable=self.avg_turnaround_var, fg="white", bg="#2A2A2A", font=self.font_med).pack(side=tk.LEFT, padx=20)
        tk.Label(self.stats_frame, textvariable=self.avg_response_var, fg="white", bg="#2A2A2A", font=self.font_med).pack(side=tk.LEFT, padx=20)

        # Matplotlib figure for Gantt chart (hidden initially)
        self.fig, self.ax = plt.subplots(figsize=(11, 4))
        self.ax.set_title("Gantt Chart", fontsize=28, color='#000000')  # Black text for title
        self.ax.set_xlabel("Time", fontsize=22, color='#000000')  # Black text for x-label
        self.ax.set_ylabel("Processes", fontsize=22, color='#000000')  # Black text for y-label
        self.ax.set_yticks([])
        self.ax.set_facecolor('#FFFFFF')  # White background
        self.ax.grid(True, which='both', axis='x', linestyle='--', color='gray', alpha=0.5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)

    def add_process(self):
        try:
            arrival_time = simpledialog.askinteger("Input", "Enter Arrival Time (non-negative):", minvalue=0, parent=self.root)
            if arrival_time is None:
                return
            burst_time = simpledialog.askinteger("Input", "Enter Burst Time (positive):", minvalue=1, parent=self.root)
            if burst_time is None:
                return
            priority = simpledialog.askinteger("Input", "Enter Priority (1=Highest):", minvalue=1, parent=self.root)
            if priority is None:
                return
            proc_desc = f"P{len(self.processes) + 1} | Arrival: {arrival_time} | Burst: {burst_time} | Priority: {priority}"
            self.processes.append({'pid': len(self.processes) + 1, 'arrival': arrival_time, 'burst': burst_time, 'priority': priority})
            self.proc_listbox.insert(tk.END, proc_desc)
        except Exception:
            messagebox.showerror("Error", "Invalid input! Please enter valid integers.", parent=self.root)

    def reset_all(self):
        self.processes.clear()
        self.proc_listbox.delete(0, tk.END)
        self.clear_canvas()
        self.canvas.get_tk_widget().pack_forget()  # Hide chart initially
        self.avg_waiting_var.set("Average Waiting Time: N/A")
        self.avg_turnaround_var.set("Average Turnaround Time: N/A")
        self.avg_response_var.set("Average Response Time: N/A")

    def start_sim(self):
        if not self.processes:
            messagebox.showwarning("No Processes", "Please add at least one process.", parent=self.root)
            return
        try:
            self.quantum = int(self.quantum_entry.get())
        except Exception:
            messagebox.showerror("Invalid Quantum", "Quantum must be an integer.", parent=self.root)
            return
        algorithm = self.algo_var.get()
        threading.Thread(target=self.run_scheduler, args=(algorithm,), daemon=True).start()

    def run_scheduler(self, algo):
        proc_list = [dict(p) for p in self.processes]
        if algo == "First Come First Serve":
            schedule, stats = self.FCFS(proc_list)
        elif algo == "Shortest Job First":
            schedule, stats = self.SJF(proc_list)
        elif algo == "Round Robin":
            schedule, stats = self.RR(proc_list, self.quantum)
        elif algo == "Priority Scheduling":
            schedule, stats = self.Priority(proc_list)
        else:
            schedule, stats = [], {}
        self.root.after(0, lambda: self.show_and_animate_gantt(schedule, stats))

    def FCFS(self, procs):
        schedule = []
        procs = sorted(procs, key=lambda p: p['arrival'])
        current_time = 0
        waiting_times = {}
        response_times = {}
        start_times = {}
        for p in procs:
            start = max(current_time, p['arrival'])
            if p['pid'] not in start_times:
                start_times[p['pid']] = start
                response_times[p['pid']] = start - p['arrival']
            finish = start + p['burst']
            waiting_times[p['pid']] = start - p['arrival']
            schedule.append({'pid': p['pid'], 'start': start, 'end': finish})
            current_time = finish
        turnaround_times = {s['pid']: s['end'] - [p['arrival'] for p in procs if p['pid'] == s['pid']][0] for s in schedule}
        avg_wt = sum(waiting_times.values())/len(waiting_times)
        avg_tat = sum(turnaround_times.values())/len(turnaround_times)
        avg_rt = sum(response_times.values())/len(response_times)
        stats = {'avg_wt': avg_wt, 'avg_tat': avg_tat, 'avg_rt': avg_rt}
        return schedule, stats

    def SJF(self, procs):
        procs = sorted(procs, key=lambda p: p['arrival'])
        ready_queue = []
        schedule = []
        time = 0
        left = procs.copy()
        waiting_times = {}
        response_times = {}
        first_response = {}
        while left or ready_queue:
            for p in left:
                if p['arrival'] <= time:
                    ready_queue.append(p)
            left = [p for p in left if p['arrival'] > time]
            if ready_queue:
                p = min(ready_queue, key=lambda p: p['burst'])
                ready_queue.remove(p)
                start = max(time, p['arrival'])
                if p['pid'] not in first_response:
                    first_response[p['pid']] = start - p['arrival']
                finish = start + p['burst']
                waiting_times[p['pid']] = start - p['arrival']
                schedule.append({'pid': p['pid'], 'start': start, 'end': finish})
                time = finish
            else:
                time += 1
        turnaround_times = {s['pid']: s['end'] - [p['arrival'] for p in procs if p['pid'] == s['pid']][0] for s in schedule}
        avg_wt = sum(waiting_times.values()) / len(waiting_times) if waiting_times else 0
        avg_tat = sum(turnaround_times.values()) / len(turnaround_times) if turnaround_times else 0
        avg_rt = sum(first_response.values()) / len(first_response) if first_response else 0
        stats = {'avg_wt': avg_wt, 'avg_tat': avg_tat, 'avg_rt': avg_rt}
        return schedule, stats

    def RR(self, procs, quantum):
        procs = [dict(p) for p in procs]
        for p in procs:
            p['remaining'] = p['burst']
        ready_queue = []
        schedule = []
        time = 0
        left = procs
        waiting_times = {p['pid']: 0 for p in procs}
        first_response = {}

        while left or ready_queue:
            for p in left:
                if p['arrival'] <= time and p not in ready_queue:
                    ready_queue.append(p)
            left = [p for p in left if p['arrival'] > time]
            if ready_queue:
                p = ready_queue.pop(0)
                start_time = time
                if p['pid'] not in first_response:
                    first_response[p['pid']] = start_time - p['arrival']
                exec_time = min(p['remaining'], quantum)
                time += exec_time
                p['remaining'] -= exec_time
                schedule.append({'pid': p['pid'], 'start': start_time, 'end': time})
                for q in ready_queue:
                    waiting_times[q['pid']] += exec_time
                if p['remaining'] > 0:
                    ready_queue.append(p)
                else:
                    # adjust waiting time for finished process
                    waiting_times[p['pid']] = waiting_times.get(p['pid'], 0) + time - p['arrival'] - p['burst']
            else:
                time += 1

        turnaround_times = {s['pid']: s['end'] - [p['arrival'] for p in procs if p['pid'] == s['pid']][0] for s in schedule}
        avg_wt = sum(waiting_times.values()) / len(waiting_times) if waiting_times else 0
        avg_tat = sum(turnaround_times.values()) / len(turnaround_times) if turnaround_times else 0
        avg_rt = sum(first_response.values()) / len(first_response) if first_response else 0
        stats = {'avg_wt': avg_wt, 'avg_tat': avg_tat, 'avg_rt': avg_rt}
        return schedule, stats

    def Priority(self, procs):
        schedule = []
        time = 0
        procs = sorted(procs, key=lambda p: (p['arrival'], p['priority']))
        left = procs.copy()
        waiting_times = {}
        first_response = {}
        while left:
            available = [p for p in left if p['arrival'] <= time]
            if not available:
                time = left[0]['arrival']
                continue
            p = min(available, key=lambda x: x['priority'])
            start = max(time, p['arrival'])
            if p['pid'] not in first_response:
                first_response[p['pid']] = start - p['arrival']
            finish = start + p['burst']
            waiting_times[p['pid']] = start - p['arrival']
            schedule.append({'pid': p['pid'], 'start': start, 'end': finish})
            time = finish
            left.remove(p)

        turnaround_times = {s['pid']: s['end'] - [p['arrival'] for p in procs if p['pid'] == s['pid']][0] for s in schedule}
        avg_wt = sum(waiting_times.values()) / len(waiting_times) if waiting_times else 0
        avg_tat = sum(turnaround_times.values()) / len(turnaround_times) if turnaround_times else 0
        avg_rt = sum(first_response.values()) / len(first_response) if first_response else 0
        stats = {'avg_wt': avg_wt, 'avg_tat': avg_tat, 'avg_rt': avg_rt}
        return schedule, stats

    def show_and_animate_gantt(self, schedule, stats):
        self.canvas.get_tk_widget().pack(pady=20)
        self.clear_canvas()
        colors = ['#69ff94', '#6096ff', '#ff61a6', '#ffff7e', '#6a55ff', '#ff5964', '#48dbfb']
        p_colors = {}
        for p in self.processes:
            p_colors[p['pid']] = random.choice(colors)

        max_time = max([task['end'] for task in schedule]) if schedule else 1
        bars = []
        for task in schedule:
            pid = task['pid']
            start = task['start']
            end = task['end']
            color = p_colors.get(pid, "#000000")
            bar = mpatches.Rectangle((start, 0.5), 0, 0.5, facecolor=color, edgecolor='black')
            self.ax.add_patch(bar)
            bars.append((bar, start, end, f"P{pid}"))

        self.ax.set_xlim(0, max_time + 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_xticks(range(0, int(max_time) + 2))
        self.ax.tick_params(axis='x', colors='black', labelsize=18)
        self.ax.tick_params(axis='y', colors='black', labelsize=18)
        self.ax.set_yticks([])
        self.ax.set_facecolor('#FFFFFF')

        patches = [mpatches.Patch(color=color, label=f"P{pid}") for pid, color in p_colors.items()]
        self.ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left',
                       fontsize=18, facecolor='#FFFFFF', labelcolor='black')
        self.ax.set_title("Gantt Chart - " + self.algo_var.get(), fontsize=28, color='black')
        self.ax.set_xlabel("Time", fontsize=24, color='black')
        self.ax.set_ylabel("", fontsize=22, color='black')
        self.canvas.draw_idle()

        def animate_bar(idx=0):
            if idx >= len(bars):
                self.avg_waiting_var.set(f"Average Waiting Time: {stats['avg_wt']:.2f}")
                self.avg_turnaround_var.set(f"Average Turnaround Time: {stats['avg_tat']:.2f}")
                self.avg_response_var.set(f"Average Response Time: {stats['avg_rt']:.2f}")
                return
            bar, start, end, label = bars[idx]
            width = end - start
            step = width / 30.0
            cur_width = 0

            def grow():
                nonlocal cur_width
                if cur_width >= width:
                    self.ax.text(start + width / 2, 0.75, label, ha='center', va='center', fontsize=20, color='black', fontweight='bold')
                    self.canvas.draw_idle()
                    animate_bar(idx + 1)
                    return
                cur_width += step
                bar.set_width(cur_width)
                self.canvas.draw_idle()
                self.root.after(30, grow)
            grow()

        animate_bar()

    def clear_canvas(self):
        self.ax.cla()
        self.ax.set_title("Gantt Chart", fontsize=28, color='black')
        self.ax.set_xlabel("Time", fontsize=24, color='black')
        self.ax.set_ylabel("Processes", fontsize=22, color='black')
        self.ax.set_yticks([])
        self.ax.grid(True, which='both', axis='x', linestyle='--', color='gray', alpha=0.5)
        self.ax.set_facecolor('#FFFFFF')
        self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
