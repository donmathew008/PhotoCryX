import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from subprocess import Popen
from threading import Thread
from PIL import Image, ImageTk
import os
import pty
import sys
import time
import shutil

class MultiAreaGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PhotoCryX")
        self.geometry("1200x800")
        self.active_process = None
        self.current_image_folder = ""

        # UI Layout
        self.area1 = tk.Frame(self, bg="lightgrey", width=200, height=750)
        self.area2 = tk.Frame(self, bg="darkgrey", width=200, height=750)
        self.area3 = tk.Frame(self, bg="lightgrey", width=800, height=750)
        self.area4 = tk.Frame(self, bg="black", width=1200, height=50)

        self.area1.grid(row=0, column=0, sticky="nsew")
        self.area2.grid(row=0, column=1, sticky="nsew")
        self.area3.grid(row=0, column=2, sticky="nsew")
        self.area4.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=2)

        # initialize UI
        self.initialize_area1()
        self.initialize_area3()
        self.initialize_area4()

    # ========= AREA 1 ==========
    def initialize_area1(self):
        tk.Label(self.area1, text="Select PC Type", bg="lightgrey").pack(pady=10)

        buttons = [
            ("1D-Photonic Crystal", self.load_area2_interface, "1D"),
            ("2D-Photonic Crystal", self.load_area2_interface, "2D"),
            ("3D-Photonic Crystal", self.load_area2_interface, "3D"),
            ("GDSII Structure Import", self.load_area2_interface, "EXEC")
        ]

        for text, command, folder in buttons:
            tk.Button(self.area1, text=text, width=20, height=2, bg="lightgreen",
                      command=lambda t=text, f=folder: command(t, f)).pack(pady=5)



        # ========= AREA 2 ==========
    def load_area2_interface(self, option, folder):
        self.clear_area(self.area2)
        tk.Label(self.area2, text=f"{option} Simulation", bg="darkgrey").pack(pady=20)

        if folder == "1D":
            tk.Button(self.area2, text="Run Simulation", width=20, height=2,
                      command=lambda: self.prepare_and_run_template("1D", "")).pack(pady=10)

        elif folder == "2D":
            self.display_subfolders("2D", ["hexagonal", "honeycomb", "square"])

        elif folder == "3D":
            self.display_subfolders("3D", ["SC", "FCC","BCC","diamond"])

        elif folder == "EXEC":
            self.load_exec_buttons()

    def display_subfolders(self, parent_folder, subfolders):
        for subfolder in subfolders:
            tk.Button(self.area2, text=subfolder, width=20, height=2,
                      command=lambda sf=subfolder: self.prepare_and_run_template(parent_folder, sf)).pack(pady=5)

    # ========= EXEC MODE BUTTONS ==========
    def load_exec_buttons(self):
        self.clear_area(self.area2)
        tk.Label(self.area2, text="EXEC Mode", bg="darkgrey").pack(pady=20)

        exec_items = [
            ("1D", "mpb_1d"),
            ("square", "mpb_sq"),
            ("hexagonal_or_honeycomb", "mpb_hx"),
            ("valley", "mpb_vy")
        ]

        for label, exe in exec_items:
            tk.Button(
                self.area2,
                text=label,
                width=25,
                height=2,
                bg="orange",
                command=lambda e=exe: self.exec_mode_run(e)
            ).pack(pady=5)

    # ========= TEXT VIEWER POPUP FOR mpb.in ==========
    def open_text_viewer(self, filepath):
        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"{filepath} not found")
            return

        top = tk.Toplevel(self)
        top.title("mpb.in Viewer")
        top.geometry("700x600")

        text_widget = tk.Text(top, wrap="word")
        text_widget.pack(fill="both", expand=True)

        with open(filepath, "r") as f:
            text_widget.insert("1.0", f.read())

    # ========= EXEC MODE RUNNER ==========
    def exec_mode_run(self, exe_name):
        folder = filedialog.askdirectory(title="Select simulation directory")
        if not folder:
            return

        folder = os.path.abspath(folder)
        mpb_in_path = os.path.join(folder, "mpb.in")

        if os.path.exists(mpb_in_path):
            self.open_text_viewer(mpb_in_path)
        else:
            messagebox.showwarning("Warning", "mpb.in not found")

        exec_path = os.path.abspath(os.path.join("EXEC", exe_name))
        if not os.path.exists(exec_path):
            messagebox.showerror("Error", f"Executable missing: {exec_path}")
            return

        self.current_image_folder = folder
#        self.start_output_in_folder(folder)

        try:
            self.active_process = Popen(
                [exec_path],
                stdin=self.slave_fd, stdout=self.slave_fd, stderr=self.slave_fd,
                text=True, cwd=folder
            )
        except Exception as e:
            self.append_to_terminal(f"EXEC run failed: {e}\n")
            return

    # ========= NEW FOLDER CREATION + COPY ==========
    def prepare_and_run_template(self, main_folder, subfolder):
        source = os.path.join(main_folder, subfolder) if subfolder else main_folder
        source = os.path.abspath(source)

        if not os.path.exists(source):
            messagebox.showerror("Error", f"Template folder missing: {source}")
            return

        choice = messagebox.askyesno(
            "Folder Choice",
            "Do you want to create a NEW folder?\n\n"
            "YES = Create new folder\n"
            "NO  = Select existing folder"
        )

        if not choice:
            target_dir = filedialog.askdirectory(title="Select existing simulation folder")
            if not target_dir:
                return

            target_dir = os.path.abspath(target_dir)

            try:
                shutil.copytree(source, target_dir, dirs_exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

            script_path = os.path.join(target_dir, "band.py")
            if not os.path.exists(script_path):
                messagebox.showerror("Error", "band.py missing!")
                return

            self.current_image_folder = target_dir
            self.run_simulation(target_dir, script_path)
            return

        base_dir = filedialog.askdirectory(title="Select parent directory")
        if not base_dir:
            return

        folder_name = simpledialog.askstring("New Folder", "Enter new folder name:")
        if not folder_name:
            return

        new_folder = os.path.join(os.path.abspath(base_dir), folder_name)
        try:
            os.makedirs(new_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error creating folder", str(e))
            return

        try:
            shutil.copytree(source, new_folder, dirs_exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        script_path = os.path.join(new_folder, "band.py")
        if not os.path.exists(script_path):
            messagebox.showerror("Error", "band.py missing!")
            return

        self.current_image_folder = new_folder
        self.run_simulation(new_folder, script_path)

    # ========= RUN SIMULATION ==========
    def run_simulation(self, folder, script_path):
        if not os.path.exists(folder):
            self.append_to_terminal(f"Error: Folder {folder} does not exist!\n")
            return

        self.clear_images()

        epsilon_path = os.path.join(folder, "epsilon.jpg")
        band_path = os.path.join(folder, "band_structure.jpg")

        old_ep = os.path.getmtime(epsilon_path) if os.path.exists(epsilon_path) else None
        old_bs = os.path.getmtime(band_path) if os.path.exists(band_path) else None

        try:
            self.active_process = Popen(
                ["python3", script_path],
                stdin=self.slave_fd, stdout=self.slave_fd, stderr=self.slave_fd,
                text=True, cwd=folder
            )
        except Exception as e:
            self.append_to_terminal(f"Failed to start process: {e}\n")
            return

        self.current_image_folder = folder

        Thread(target=self.monitor_simulation_images,
               args=(folder, old_ep, old_bs), daemon=True).start()

    # IMAGE MONITOR, AUTO DISPLAY, CANVAS HANDLING, TERMINAL HANDLING...

    def monitor_simulation_images(self, folder, old_ep, old_bs):
        ep_path = os.path.join(folder, "epsilon.jpg")
        bs_path = os.path.join(folder, "band_structure.jpg")

        ep_loaded = False
        bs_loaded = False

        for _ in range(600):
            if not ep_loaded and os.path.exists(ep_path):
                if old_ep is None or os.path.getmtime(ep_path) > old_ep:
                    self.auto_load_image1(ep_path)
                    ep_loaded = True

            if not bs_loaded and os.path.exists(bs_path):
                if old_bs is None or os.path.getmtime(bs_path) > old_bs:
                    self.auto_load_image2(bs_path)
                    bs_loaded = True

            if ep_loaded and bs_loaded:
                break

            time.sleep(0.5)

    def auto_load_image1(self, image_path):
        try:
            self.current_image1 = Image.open(image_path)
            self.zoom_level1 = 0.68
            self.after(0, self.display_image1)
        except Exception as e:
            self.append_to_terminal(f"Error loading image: {e}\n")

    def auto_load_image2(self, image_path):
        try:
            self.current_image2 = Image.open(image_path)
            self.zoom_level2 = 0.68
            self.after(0, self.display_image2)
        except Exception as e:
            self.append_to_terminal(f"Error loading image: {e}\n")

    def initialize_area3(self):
        tk.Label(self.area3, text="Image Viewer", bg="lightgrey").pack(pady=10)

        zoom1 = tk.Frame(self.area3, bg="lightgrey")
        zoom1.pack(pady=5)
        tk.Button(zoom1, text="View Structure", command=self.open_image1).pack(side=tk.LEFT, padx=5)
        tk.Button(zoom1, text="+ Structure", command=self.zoom_in1).pack(side=tk.LEFT, padx=5)
        tk.Button(zoom1, text="- Structure", command=self.zoom_out1).pack(side=tk.LEFT, padx=5)

        zoom2 = tk.Frame(self.area3, bg="lightgrey")
        zoom2.pack(pady=5)
        tk.Button(zoom2, text="Open Image", command=self.open_image2).pack(side=tk.LEFT, padx=5)
        tk.Button(zoom2, text="Zoom in", command=self.zoom_in2).pack(side=tk.LEFT, padx=5)
        tk.Button(zoom2, text="Zoom out", command=self.zoom_out2).pack(side=tk.LEFT, padx=5)

        self.canvas1 = tk.Canvas(self.area3, bg="white")
        self.canvas1.pack(fill="both", expand=True, side=tk.LEFT)

        self.canvas2 = tk.Canvas(self.area3, bg="white")
        self.canvas2.pack(fill="both", expand=True, side=tk.LEFT)

        self.current_image1 = None
        self.current_image2 = None
        self.zoom_level1 = 1.0
        self.zoom_level2 = 1.0

    def open_image1(self):
        if self.current_image_folder:
            path = os.path.join(self.current_image_folder, "epsilon.jpg")
            if os.path.exists(path):
                self.current_image1 = Image.open(path)
                self.zoom_level1 = 0.68

            # --- AUTO-FIT INITIAL SCALING ---
                cw = self.canvas1.winfo_width()
                ch = self.canvas1.winfo_height()
                iw, ih = self.current_image1.size
                if cw > 0 and ch > 0:
                    scale = min(cw / iw, ch / ih)
                    self.zoom_level1 = scale

                self.display_image1()


    def open_image2(self):
        folder = self.current_image_folder
        if folder:
            path = filedialog.askopenfilename(
                initialdir=folder,
                filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.eps")]
            )
            if path:
                self.current_image2 = Image.open(path)
                self.zoom_level2 = 0.68

            # --- AUTO-FIT INITIAL SCALING ---
                cw = self.canvas2.winfo_width()
                ch = self.canvas2.winfo_height()
                iw, ih = self.current_image2.size
                if cw > 0 and ch > 0:
                    scale = min(cw / iw, ch / ih)
                    self.zoom_level2 = scale

                self.display_image2()


    def display_image1(self):
        self.canvas1.delete("all")
        if self.current_image1:
            w, h = self.current_image1.size
            resized = self.current_image1.resize(
                (int(w * self.zoom_level1), int(h * self.zoom_level1)),
                Image.LANCZOS
            )
            self.imgtk1 = ImageTk.PhotoImage(resized)
            self.canvas1.create_image(0, 0, anchor="nw", image=self.imgtk1)


    def display_image2(self):
        self.canvas2.delete("all")
        if self.current_image2:
            w, h = self.current_image2.size
            resized = self.current_image2.resize(
                (int(w * self.zoom_level2), int(h * self.zoom_level2)),
                Image.LANCZOS
            )
            self.imgtk2 = ImageTk.PhotoImage(resized)
            self.canvas2.create_image(0, 0, anchor="nw", image=self.imgtk2)


    def zoom_in1(self):
        if self.current_image1:
            self.zoom_level1 *= 1.1
            self.display_image1()

    def zoom_out1(self):
        if self.current_image1:
            self.zoom_level1 /= 1.1
            self.display_image1()

    def zoom_in2(self):
        if self.current_image2:
            self.zoom_level2 *= 1.1
            self.display_image2()

    def zoom_out2(self):
        if self.current_image2:
            self.zoom_level2 /= 1.1
            self.display_image2()

    def clear_images(self):
        self.canvas1.delete("all")
        self.canvas2.delete("all")
        self.current_image1 = None
        self.current_image2 = None

    # ========= TERMINAL ==========
    def initialize_area4(self):
        self.clear_area(self.area4)
        self.terminal_output = tk.Text(self.area4, bg="black", fg="white")
        self.terminal_output.pack(fill="both", expand=True)
        self.terminal_output.bind("<Return>", self.send_terminal_input)

        self.master_fd, self.slave_fd = pty.openpty()
        self.start_terminal_process()

    def start_terminal_process(self):
        self.terminal_process = Popen(
            ["bash"], stdin=self.slave_fd, stdout=self.slave_fd, stderr=self.slave_fd, text=True
        )
        Thread(target=self.read_terminal_output, daemon=True).start()

    def read_terminal_output(self):
        while True:
            try:
                output = os.read(self.master_fd, 1024).decode("utf-8", errors="ignore")
                if output:
                    self.append_to_terminal(output)
            except OSError:
                break
            except Exception:
                time.sleep(0.1)

    def append_to_terminal(self, text):
        clean_text = text.replace("\r", "")
        self.terminal_output.insert(tk.END, clean_text)
        self.terminal_output.see(tk.END)
        self.output_file.write(clean_text)

    def send_terminal_input(self, event):
        text = self.terminal_output.get("insert linestart", "insert lineend")
        try:
            os.write(self.master_fd, (text + "\n").encode())
        except Exception as e:
            print("Failed to send terminal input:", e)
        self.terminal_output.insert(tk.END, "\n")
        return "break"

    def clear_area(self, area):
        for w in area.winfo_children():
            w.destroy()


if __name__ == "__main__":
    app = MultiAreaGUI()
    app.mainloop()
