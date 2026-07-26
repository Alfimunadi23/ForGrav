import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math  # Untuk menangani masalah numerik kecil

class GravityForwardModelingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ForGrav")

        # Membuat Menu Bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Menambahkan menu File
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Image", command=self.save_image)  # Save Image menu
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Menambahkan menu Edit
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear All", command=self.clear_vertices)

        # Menambahkan menu Help
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # Variabel untuk menyimpan data
        self.vertices = []  # Daftar untuk menyimpan titik-titik poligon
        self.density = 1000.0  # Kontras densitas default dalam kg/m^3
        self.measurement_data = None
        self.measurement_file_path = ""
        self.x_positions = None
        self.gravity_response = None  # Menyimpan hasil perhitungan anomali (dengan penyesuaian tanda)

        # Setup antarmuka pengguna
        self.setup_ui()

    def setup_ui(self):
        # Menambahkan gaya
        style = ttk.Style()
        style.configure("TButton", font=('Helvetica', 14, 'bold'), padding=15)
        style.configure("TLabel", font=('Helvetica', 14))
        style.configure("TLabelFrame", font=('Helvetica', 16, 'bold'))
        style.configure("TFrame", font=('Helvetica', 12))
        style.configure("TMenu", font=('Helvetica', 12))

        # Membuat font untuk judul "ForGrav" lebih besar
        self.root.option_add("*Font", "Helvetica 16 bold")

        # Frame utama
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Mengonfigurasi grid agar bisa berkembang
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Frame parameter model
        param_frame = ttk.LabelFrame(main_frame, text="Parameter Model", padding="20")
        param_frame.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=15, pady=15)

        ttk.Label(param_frame, text="Kontras Densitas (\u0394\u03C1, kg/m\u00B3):", font=("Helvetica", 14)).grid(row=0, column=0, sticky=tk.W, pady=10)
        self.density_entry = ttk.Entry(param_frame, width=15, font=("Helvetica", 14))
        self.density_entry.grid(row=0, column=1, sticky=tk.W, pady=10)
        self.density_entry.insert(0, "1000")  # Densitas default dalam kg/m^3

        # Tombol dengan ukuran lebih besar
        ttk.Button(param_frame, text="Tambah Titik Poligon", command=self.add_vertex, style="TButton").grid(row=1, column=0, columnspan=2, pady=15)
        ttk.Button(param_frame, text="Hapus Titik Terakhir", command=self.remove_last_vertex, style="TButton").grid(row=2, column=0, columnspan=2, pady=15)
        ttk.Button(param_frame, text="Hapus Semua Titik", command=self.clear_vertices, style="TButton").grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(param_frame, text="Hitung Respon Gravitasi", command=self.calculate_gravity, style="TButton").grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(param_frame, text="Reset", command=self.reset_all, style="TButton").grid(row=5, column=0, columnspan=2, pady=20)

        # Frame plot
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=15, pady=15)

        self.fig = plt.figure(figsize=(9, 8))
        gs = self.fig.add_gridspec(2, hspace=0.4, height_ratios=[1, 1.5])

        self.ax1 = self.fig.add_subplot(gs[0])
        self.ax1.set_title('(a) Anomaly Response', pad=15, fontweight='bold')
        self.ax1.set_xlabel('Distance (m)', fontsize=12)
        self.ax1.set_ylabel('Gravity Anomaly (mGal)', fontsize=12)
        self.ax1.grid(True, linestyle=':', alpha=0.6)

        self.ax2 = self.fig.add_subplot(gs[1])
        self.ax2.set_title('(b) Anomaly Source', pad=15, fontweight='bold')
        self.ax2.set_xlabel('Distance (m)', fontsize=12)
        self.ax2.set_ylabel('Depth (m)', fontsize=12)
        self.ax2.grid(True, linestyle=':', alpha=0.6)
        self.ax2.invert_yaxis()

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.status_bar = ttk.Label(main_frame, text="Siap", relief=tk.SUNKEN, font=("Helvetica", 14))
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

    def show_about(self):
        messagebox.showinfo("About", "ForGrav: Aplikasi untuk Perhitungan Anomali Gravitasi\nDikembangkan oleh Anda.")

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300)  # Save with high quality (300 dpi)
                self.status_bar.config(text=f"Gambar disimpan di: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan saat menyimpan gambar:\n{str(e)}")
                self.status_bar.config(text="Gagal menyimpan gambar")

    def add_vertex(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Tambah Titik Poligon")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Koordinat X (m):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        x_entry = ttk.Entry(dialog)
        x_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Kedalaman Z (m):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        z_entry = ttk.Entry(dialog)
        z_entry.grid(row=1, column=1, padx=5, pady=5)

        def save_vertex():
            try:
                x = float(x_entry.get())
                z = float(z_entry.get())
                if z == 0:
                    messagebox.showerror("Error", "Kedalaman (Z) tidak boleh bernilai nol.")
                    return
                self.vertices.append((x, z))  # Menyimpan nilai z tanpa mengubahnya
                self.update_plots()
                dialog.destroy()
                self.status_bar.config(text=f"Titik ditambahkan: ({x}, Kedalaman {z})")
            except ValueError:
                messagebox.showerror("Error", "Masukkan angka yang valid untuk koordinat.")

        ttk.Button(dialog, text="Simpan", command=save_vertex).grid(row=2, column=0, columnspan=2, pady=10)

        dialog.bind('<Return>', lambda event=None: save_vertex())
        x_entry.focus_set()

    def remove_last_vertex(self):
        if self.vertices:
            removed = self.vertices.pop()
            depth_removed = removed[1]
            self.update_plots()
            self.status_bar.config(text=f"Titik dihapus: ({removed[0]}, Kedalaman {depth_removed})")
        else:
            self.status_bar.config(text="Tidak ada titik untuk dihapus")

    def clear_vertices(self):
        self.vertices = []
        self.update_plots()
        self.status_bar.config(text="Semua titik telah dihapus")

    def reset_all(self):
        # Reset titik dan respon gravitasi
        self.vertices = []
        self.gravity_response = None
        self.x_positions = None
        self.update_plots()
        self.status_bar.config(text="Semua titik dan respon gravitasi telah direset.")

    def update_plots(self):
        self.ax1.clear()
        self.ax2.clear()

        self.ax1.set_title('(a) Anomaly Response (Sign Adjusted)', pad=15, fontweight='bold')
        self.ax1.set_xlabel('Distance (m)')
        self.ax1.set_ylabel('Gravity Anomaly (mGal)')
        self.ax1.grid(True, linestyle=':', alpha=0.6)

        self.ax2.set_title('(b) Anomaly Source', pad=15, fontweight='bold')
        self.ax2.set_xlabel('Distance (m)')
        self.ax2.set_ylabel('Depth (m)')
        self.ax2.grid(True, linestyle=':', alpha=0.6)
        self.ax2.invert_yaxis()

        if self.gravity_response is not None and self.x_positions is not None:
            self.ax1.plot(self.x_positions, self.gravity_response, 'b-', linewidth=2, label='Calculated anomaly')

            if self.measurement_data is not None:
                if self.measurement_data.ndim == 2 and self.measurement_data.shape[1] == 2:
                    self.ax1.plot(self.measurement_data[:, 0], self.measurement_data[:, 1], 'ro', markersize=5, label='Measured data')
                else:
                    self.status_bar.config(text="Warning: Data pengukuran tidak dalam format yang diharapkan (N, 2).")

            self.ax1.legend(loc='upper right')

            if self.x_positions is not None and len(self.x_positions) > 1:
                x_min, x_max = np.min(self.x_positions), np.max(self.x_positions)
                self.ax1.set_xlim(x_min, x_max)
                self.ax2.set_xlim(x_min, x_max)

        elif self.measurement_data is not None:
            if self.measurement_data.ndim == 2 and self.measurement_data.shape[1] == 2:
                self.ax1.plot(self.measurement_data[:, 0], self.measurement_data[:, 1], 'ro', markersize=5, label='Measured data')
                self.ax1.legend(loc='upper right')
                if self.measurement_data.shape[0] > 1:
                    x_min, x_max = np.min(self.measurement_data[:, 0]), np.max(self.measurement_data[:, 0])
                    x_range = x_max - x_min
                    padding = x_range * 0.1
                    self.ax1.set_xlim(x_min - padding, x_max + padding)
                    self.ax2.set_xlim(x_min - padding, x_max + padding)

        if self.gravity_response is None and self.measurement_data is None:
            if self.vertices:
                x_coords = [v[0] for v in self.vertices]
                if len(x_coords) > 1:
                    x_min_poly = min(x_coords)
                    x_max_poly = max(x_coords)
                    x_range_poly = x_max_poly - x_min_poly
                    padding = x_range_poly * 1.5
                    self.ax1.set_xlim(x_min_poly - padding, x_max_poly + padding)
                    self.ax2.set_xlim(x_min_poly - padding, x_max_poly + padding)

        if len(self.vertices) > 1:
            polygon_patch = Polygon(self.vertices, closed=True, fill=True, alpha=0.6,
                                   edgecolor='k', linewidth=1.5, facecolor='orange')
            self.ax2.add_patch(polygon_patch)

            x_coords, y_coords = zip(*self.vertices)
            self.ax2.plot(x_coords, y_coords, 'ko-', markersize=5, linewidth=1.5)

            for i, (x, y) in enumerate(self.vertices):
                if self.ax2.get_xlim()[1] - self.ax2.get_xlim()[0] > 0:
                    x_offset = (self.ax2.get_xlim()[1] - self.ax2.get_xlim()[0]) * 0.01
                else:
                    x_offset = 0.1
                if self.ax2.get_ylim()[1] - self.ax2.get_ylim()[0] > 0:
                    y_offset = (self.ax2.get_ylim()[1] - self.ax2.get_ylim()[0]) * 0.02
                else:
                    y_offset = 0.1

                self.ax2.text(x + x_offset, y + y_offset, f' {i+1}', color='k', fontsize=10,
                              verticalalignment='center')

            y_coords = [v[1] for v in self.vertices]
            if y_coords:
                y_min, y_max = min(y_coords), max(y_coords)
                y_range = y_max - y_min
                y_padding = max(1.0, y_range * 0.2)
                plot_ymin = min(y_max + y_padding, 0.0)
                plot_ymax = y_min - y_padding
                self.ax2.set_ylim(plot_ymin, plot_ymax)
                self.ax2.invert_yaxis()

        self.canvas.draw()

    def calculate_gravity(self):
        if len(self.vertices) < 3:
            messagebox.showerror("Error", "Setidaknya dibutuhkan 3 titik untuk membentuk poligon tertutup.")
            return

        try:
            self.density = float(self.density_entry.get())
            if np.isclose(self.density, 0.0):
                messagebox.showwarning("Warning", "Kontras densitas bernilai nol. Anomali gravitasi akan nol.")
                return

        except ValueError:
            messagebox.showerror("Error", "Masukkan nilai kontras densitas yang valid (angka).")
            return

        if self.vertices:
            x_coords = [v[0] for v in self.vertices]
            if len(x_coords) > 1:
                x_min_poly = min(x_coords)
                x_max_poly = max(x_coords)
                x_range_poly = x_max_poly - x_min_poly
                calculation_range_min = x_min_poly - x_range_poly * 1.5
                calculation_range_max = x_max_poly + x_range_poly * 1.5
                self.x_positions = np.linspace(calculation_range_min, calculation_range_max, 300)
            else:
                self.x_positions = np.linspace(x_coords[0] - 50, x_coords[0] + 50, 300)
        else:
            self.x_positions = np.linspace(-50, 50, 300)

        try:
            calculated_raw_anomaly = self.calculate_polygon_gravity(self.x_positions)

            signed_area = 0.0
            n_vertices = len(self.vertices)
            if n_vertices >= 3:
                for i in range(n_vertices):
                    x1, y1 = self.vertices[i]
                    x2, y2 = self.vertices[(i + 1) % n_vertices]
                    signed_area += (x1 * y2 - x2 * y1)
                signed_area *= 0.5

                if signed_area > 1e-9:
                    calculated_raw_anomaly *= -1

            if np.sign(calculated_raw_anomaly[np.argmax(np.abs(calculated_raw_anomaly))]) != np.sign(self.density) and not np.isclose(self.density, 0):
                self.gravity_response = calculated_raw_anomaly * -1
            else:
                self.gravity_response = calculated_raw_anomaly

            self.update_plots()
            self.status_bar.config(text="Respon gravitasi telah dihitung.")

        except Exception as e:
            messagebox.showerror("Calculation Error", f"Terjadi kesalahan saat menghitung gravitasi:\n{str(e)}")
            self.status_bar.config(text="Gagal menghitung respon gravitasi")

    def calculate_polygon_gravity(self, x_positions):
        G = 6.67408e-11  # Konstanta gravitasi (m^3 kg^-1 s^-2)
        si_to_mgal = 1e5  # Konversi dari m/s^2 ke mGal

        density_kg = self.density
        if np.isclose(density_kg, 0.0):
            messagebox.showwarning("Warning", "Kontras densitas bernilai nol. Anomali gravitasi akan nol.")
            return np.zeros_like(x_positions)

        raw_anomaly_sum = np.zeros_like(x_positions, dtype=float)
        n_vertices = len(self.vertices)

        if n_vertices < 2:
            return np.zeros_like(x_positions) * (2.0 * G * density_kg * si_to_mgal)

        for i in range(len(x_positions)):
            x0 = x_positions[i]
            total_contribution = 0.0

            for j in range(n_vertices):
                x_j, y_j = self.vertices[j]
                x_jplus1, y_jplus1 = self.vertices[(j + 1) % n_vertices]  # Corrected line

                z_j = -y_j
                z_jplus1 = -y_jplus1

                xj_relative = x_j - x0
                xjplus1_relative = x_jplus1 - x0

                psi_j = np.arctan2(xjplus1_relative, z_jplus1) - np.arctan2(xj_relative, z_j)

                ri_sq = xj_relative**2 + z_j**2
                riplus1_sq = xjplus1_relative**2 + z_jplus1**2

                log_term = 0.0
                if ri_sq > 1e-15 and riplus1_sq > 1e-15:
                    log_term = 0.5 * np.log(riplus1_sq / ri_sq)

                segment_contribution = (x_j - x_jplus1) * psi_j + (z_j - z_jplus1) * log_term
                total_contribution += segment_contribution

            raw_anomaly_sum[i] = total_contribution

        final_anomaly = 2.0 * G * density_kg * raw_anomaly_sum * si_to_mgal
        return final_anomaly

if __name__ == "__main__":
    root = tk.Tk()
    app = GravityForwardModelingApp(root)
    root.mainloop()
