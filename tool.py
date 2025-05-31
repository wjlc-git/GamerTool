import tkinter as tk
from tkinter import ttk, colorchooser
import threading
import time
import keyboard
import pyautogui

class CrosshairXApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crosshair X Clone")
        self.root.geometry("400x320")

        # Crosshair variables
        self.crosshair_size = 20
        self.crosshair_thickness = 2
        self.crosshair_color = "#ff0000"

        self.running = False
        self.overlay = None
        self.canvas = None

        self.rgb_cycle_enabled = False
        self.fade_enabled = False

        # Auto-clicker variables
        self.auto_clicking = False
        self.auto_click_delay = 0.1
        self.auto_click_button = "left"

        self.create_ui()

        # Start hotkey listener thread
        threading.Thread(target=self.hotkey_listener, daemon=True).start()

    def create_ui(self):
        self.tabs = ttk.Notebook(self.root)
        self.tab_crosshair = ttk.Frame(self.tabs)
        self.tab_autoclicker = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_crosshair, text="Crosshair")
        self.tabs.add(self.tab_autoclicker, text="Auto-Clicker")
        self.tabs.pack(expand=True, fill="both")

        # Crosshair tab controls
        ttk.Label(self.tab_crosshair, text="Crosshair Size").pack(pady=5)
        self.size_slider = ttk.Scale(self.tab_crosshair, from_=5, to=100, command=self.on_size_change)
        self.size_slider.set(self.crosshair_size)
        self.size_slider.pack(fill="x", padx=10)

        ttk.Label(self.tab_crosshair, text="Thickness").pack(pady=5)
        self.thickness_slider = ttk.Scale(self.tab_crosshair, from_=1, to=10, command=self.on_thickness_change)
        self.thickness_slider.set(self.crosshair_thickness)
        self.thickness_slider.pack(fill="x", padx=10)

        self.color_button = ttk.Button(self.tab_crosshair, text="Choose Color", command=self.choose_color)
        self.color_button.pack(pady=10)

        self.rgb_var = tk.BooleanVar()
        self.rgb_check = ttk.Checkbutton(self.tab_crosshair, text="Enable RGB Cycle", variable=self.rgb_var, command=self.toggle_rgb_cycle)
        self.rgb_check.pack()

        self.fade_var = tk.BooleanVar()
        self.fade_check = ttk.Checkbutton(self.tab_crosshair, text="Enable Fade Animation", variable=self.fade_var, command=self.toggle_fade)
        self.fade_check.pack()

        self.toggle_crosshair_btn = ttk.Button(self.tab_crosshair, text="Toggle Crosshair (F8)", command=self.toggle_crosshair)
        self.toggle_crosshair_btn.pack(pady=10)

        # Auto-clicker tab controls
        ttk.Label(self.tab_autoclicker, text="Click Delay (seconds)").pack(pady=5)
        self.delay_slider = ttk.Scale(self.tab_autoclicker, from_=0.01, to=1.0, command=self.on_delay_change)
        self.delay_slider.set(self.auto_click_delay)
        self.delay_slider.pack(fill="x", padx=10)

        ttk.Label(self.tab_autoclicker, text="Mouse Button").pack(pady=5)
        self.button_combo = ttk.Combobox(self.tab_autoclicker, values=["left", "right", "middle"], state="readonly")
        self.button_combo.set(self.auto_click_button)
        self.button_combo.bind("<<ComboboxSelected>>", self.on_button_change)
        self.button_combo.pack()

        self.toggle_autoclicker_btn = ttk.Button(self.tab_autoclicker, text="Toggle Auto-Clicker (F9)", command=self.toggle_auto_clicker)
        self.toggle_autoclicker_btn.pack(pady=10)

    # Crosshair handlers
    def on_size_change(self, val):
        self.crosshair_size = int(float(val))
        self.redraw_crosshair()

    def on_thickness_change(self, val):
        self.crosshair_thickness = int(float(val))
        self.redraw_crosshair()

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Crosshair Color")
        if color and color[1]:
            self.crosshair_color = color[1]
            self.redraw_crosshair()

    def toggle_rgb_cycle(self):
        self.rgb_cycle_enabled = self.rgb_var.get()
        if self.rgb_cycle_enabled and self.running:
            threading.Thread(target=self.rgb_cycle, daemon=True).start()

    def toggle_fade(self):
        self.fade_enabled = self.fade_var.get()
        if self.fade_enabled and self.running:
            threading.Thread(target=self.fade_animation, daemon=True).start()
        elif self.overlay:
            try:
                self.overlay.attributes('-alpha', 1.0)
            except Exception:
                pass

    def toggle_crosshair(self):
        if self.running:
            self.running = False
            if self.overlay:
                self.overlay.destroy()
                self.overlay = None
        else:
            self.running = True
            threading.Thread(target=self.show_crosshair, daemon=True).start()

    def show_crosshair(self):
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-topmost', True)
        self.overlay.attributes('-transparentcolor', 'white')
        self.overlay.configure(bg='white')
        self.overlay.overrideredirect(True)

        self.canvas = tk.Canvas(self.overlay, bg='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self.redraw_crosshair()

        if self.rgb_cycle_enabled:
            threading.Thread(target=self.rgb_cycle, daemon=True).start()
        if self.fade_enabled:
            threading.Thread(target=self.fade_animation, daemon=True).start()

        # Keep window open until toggled off
        while self.running:
            time.sleep(0.1)
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def redraw_crosshair(self):
        if not self.running or not self.canvas:
            return
        self.canvas.delete("all")
        w = self.overlay.winfo_screenwidth()
        h = self.overlay.winfo_screenheight()
        cx, cy = w//2, h//2
        s = self.crosshair_size
        t = self.crosshair_thickness
        c = self.crosshair_color

        self.canvas.create_line(cx - s, cy, cx + s, cy, fill=c, width=t)
        self.canvas.create_line(cx, cy - s, cx, cy + s, fill=c, width=t)

    def rgb_cycle(self):
        while self.rgb_cycle_enabled and self.running:
            for r in range(0, 256, 5):
                for g in range(0, 256, 5):
                    for b in range(0, 256, 5):
                        if not self.rgb_cycle_enabled or not self.running:
                            return
                        self.crosshair_color = f"#{r:02x}{g:02x}{b:02x}"
                        self.redraw_crosshair()
                        time.sleep(0.02)

    def fade_animation(self):
        alpha = 1.0
        fade_out = True
        while self.fade_enabled and self.running:
            if self.overlay is None:
                break
            if fade_out:
                alpha -= 0.02
                if alpha <= 0.3:
                    alpha = 0.3
                    fade_out = False
            else:
                alpha += 0.02
                if alpha >= 1.0:
                    alpha = 1.0
                    fade_out = True
            try:
                self.overlay.attributes('-alpha', alpha)
            except Exception:
                break
            time.sleep(0.05)

    # Auto-clicker handlers
    def on_delay_change(self, val):
        self.auto_click_delay = float(val)

    def on_button_change(self, event):
        self.auto_click_button = self.button_combo.get()

    def toggle_auto_clicker(self):
        if self.auto_clicking:
            self.auto_clicking = False
        else:
            self.auto_clicking = True
            threading.Thread(target=self.auto_clicker_loop, daemon=True).start()

    def auto_clicker_loop(self):
        while self.auto_clicking:
            pyautogui.click(button=self.auto_click_button)
            time.sleep(self.auto_click_delay)

    # Hotkey listener for toggling crosshair (F8) and autoclicker (F9)
    def hotkey_listener(self):
        while True:
            try:
                if keyboard.is_pressed('F8'):
                    self.toggle_crosshair()
                    time.sleep(0.5)
                if keyboard.is_pressed('F9'):
                    self.toggle_auto_clicker()
                    time.sleep(0.5)
            except:
                # Ignore errors from keyboard module (focus issues)
                time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = CrosshairXApp(root)
    root.mainloop()
