"""
Antiloop GUI
============

Reusable progress window for long-running experiments.
Uses tkinter (ships with Python, no extra dependencies).

Usage from an experiment:

    from simulation.gui import run_with_gui

    def my_experiment(out_dir, progress):
        for i in range(100):
            do_work()
            progress.update(i+1, 100, "Phase 1", f"Step {i+1}/100")
            progress.log(f"Step {i+1} done")

    run_with_gui(my_experiment, out_dir="results")
"""

import os
import queue
import threading
import tkinter as tk
from tkinter import ttk


def _find_icon():
    """Locate the antiloop icon file."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for ext in ("ico", "png"):
        path = os.path.join(base, "logo", f"antiloop_icon.{ext}")
        if os.path.isfile(path):
            return path
    return None


def _detect_gpu():
    """Detect GPU availability and return info string."""
    try:
        from simulation.shared.engine import HAS_CUDA
        if not HAS_CUDA:
            return None
        import cupy as cp
        props = cp.cuda.runtime.getDeviceProperties(0)
        name = props["name"]
        if isinstance(name, bytes):
            name = name.decode()
        mem = cp.cuda.Device(0).mem_info
        total_mb = mem[1] / (1024 * 1024)
        return f"{name} ({total_mb:.0f} MB)"
    except Exception:
        return None


class ProgressWindow:
    """Tkinter window showing simulation progress."""

    def __init__(self, title="Antiloop Experiment"):
        self.root = tk.Tk()
        self.root.title(f"ANTILOOP - {title}")
        self.root.geometry("620x460")
        self.root.resizable(True, True)

        # Set window icon
        icon_path = _find_icon()
        if icon_path:
            try:
                if icon_path.endswith(".ico"):
                    self.root.iconbitmap(icon_path)
                else:
                    icon = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, icon)
            except tk.TclError:
                pass

        self._msg_queue = queue.Queue()
        self._done = False
        self._overall_step = 0
        self._overall_total = 1

        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header row: phase label + GPU badge
        header = ttk.Frame(frame)
        header.pack(fill=tk.X)

        self._phase_var = tk.StringVar(value="Initializing...")
        ttk.Label(header, textvariable=self._phase_var,
                  font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)

        # GPU indicator
        gpu_info = _detect_gpu()
        if gpu_info:
            gpu_text = f"CUDA: {gpu_info}"
            gpu_fg = "#4caf50"
        else:
            gpu_text = "CPU only"
            gpu_fg = "#999999"
        self._gpu_label = tk.Label(header, text=gpu_text, fg=gpu_fg,
                                   font=("Consolas", 8))
        self._gpu_label.pack(side=tk.RIGHT)

        # Status label
        self._status_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self._status_var,
                  font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(2, 6))

        # Overall progress bar (seeds)
        overall_frame = ttk.Frame(frame)
        overall_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(overall_frame, text="Overall:",
                  font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(0, 6))
        self._progress = ttk.Progressbar(overall_frame, mode="determinate",
                                         maximum=100)
        self._progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._pct_var = tk.StringVar(value="0%")
        ttk.Label(overall_frame, textvariable=self._pct_var,
                  font=("Segoe UI", 8), width=5).pack(side=tk.LEFT, padx=(6, 0))

        # Per-seed progress bar
        seed_frame = ttk.Frame(frame)
        seed_frame.pack(fill=tk.X, pady=(0, 8))
        self._seed_label_var = tk.StringVar(value="Seed:")
        ttk.Label(seed_frame, textvariable=self._seed_label_var,
                  font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(0, 6))
        self._seed_progress = ttk.Progressbar(seed_frame, mode="determinate",
                                              maximum=100)
        self._seed_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._seed_pct_var = tk.StringVar(value="0%")
        ttk.Label(seed_frame, textvariable=self._seed_pct_var,
                  font=("Segoe UI", 8), width=5).pack(side=tk.LEFT, padx=(6, 0))

        # Log area
        self._log = tk.Text(frame, height=14, font=("Consolas", 9),
                            state=tk.DISABLED, bg="#1e1e1e", fg="#d4d4d4",
                            wrap=tk.WORD)
        self._log.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        self.root.after(50, self._poll)

    def update(self, step, total, phase, status):
        """Thread-safe overall progress update. Stores seed count for interpolation."""
        self._msg_queue.put(("progress", step, total, phase, status))

    def update_seed(self, step, total, label=""):
        """Thread-safe per-seed progress update. Also updates overall bar."""
        self._msg_queue.put(("seed_progress", step, total, label))

    def log(self, text):
        """Thread-safe log line."""
        self._msg_queue.put(("log", text))

    def finish(self):
        """Signal completion."""
        self._msg_queue.put(("done",))

    def _poll(self):
        try:
            while True:
                msg = self._msg_queue.get_nowait()
                if msg[0] == "progress":
                    _, step, total, phase, status = msg
                    self._overall_step = step
                    self._overall_total = max(total, 1)
                    pct = (step / self._overall_total * 100)
                    self._progress["value"] = pct
                    self._pct_var.set(f"{pct:.0f}%")
                    self._phase_var.set(phase)
                    self._status_var.set(status)
                elif msg[0] == "seed_progress":
                    _, step, total, label = msg
                    seed_frac = (step / max(total, 1))
                    pct = seed_frac * 100
                    self._seed_progress["value"] = pct
                    self._seed_pct_var.set(f"{pct:.0f}%")
                    if label:
                        self._seed_label_var.set(label)
                    # Interpolate overall: completed seeds + fraction of current
                    overall_pct = ((self._overall_step + seed_frac)
                                   / self._overall_total * 100)
                    self._progress["value"] = min(overall_pct, 100)
                    self._pct_var.set(f"{min(overall_pct, 100):.0f}%")
                elif msg[0] == "log":
                    self._log.config(state=tk.NORMAL)
                    self._log.insert(tk.END, msg[1] + "\n")
                    self._log.see(tk.END)
                    self._log.config(state=tk.DISABLED)
                elif msg[0] == "done":
                    self._done = True
                    self._progress["value"] = 100
                    self._pct_var.set("100%")
                    self._seed_progress["value"] = 100
                    self._seed_pct_var.set("100%")
                    self._phase_var.set("Done")
                    self._status_var.set("Closing...")
                    self.root.after(1500, self.root.destroy)
                    return
        except queue.Empty:
            pass
        if not self._done:
            self.root.after(50, self._poll)

    def mainloop(self):
        self.root.mainloop()


class Progress:
    """Progress reporting interface passed to experiments.

    Works in both GUI and headless mode. Experiments call:
        progress.update(step, total, phase, status)  — overall (seeds)
        progress.update_seed(step, total, label)      — per-seed
        progress.log("message")
    """

    def __init__(self, window=None):
        self._window = window

    def update(self, step, total, phase, status):
        if self._window:
            self._window.update(step, total, phase, status)

    def update_seed(self, step, total, label=""):
        if self._window:
            self._window.update_seed(step, total, label)

    def log(self, text):
        print(text)
        if self._window:
            self._window.log(text)


def run_with_gui(experiment_fn, title="Antiloop Experiment", **kwargs):
    """Run an experiment function with a GUI progress window.

    Args:
        experiment_fn: callable(progress=Progress, **kwargs)
        title: window title
        **kwargs: passed to experiment_fn
    """
    win = ProgressWindow(title=title)
    progress = Progress(window=win)

    def worker():
        try:
            experiment_fn(progress=progress, **kwargs)
        finally:
            win.finish()

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    win.mainloop()


def run_headless(experiment_fn, **kwargs):
    """Run an experiment function without GUI."""
    progress = Progress(window=None)
    experiment_fn(progress=progress, **kwargs)
