import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import math
import statistics as stats
import json
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

A3 = {2:2.659,3:1.954,4:1.628,5:1.427,6:1.287,7:1.182,8:1.099,9:1.032,10:0.975,11:0.927,12:0.886,13:0.850,14:0.817,15:0.789,16:0.763,17:0.739,18:0.718,19:0.698,20:0.680,21:0.663,22:0.647,23:0.633,24:0.619,25:0.606}
B3 = {2:0.000,3:0.000,4:0.000,5:0.000,6:0.030,7:0.118,8:0.185,9:0.239,10:0.284,11:0.321,12:0.354,13:0.382,14:0.406,15:0.428,16:0.448,17:0.466,18:0.482,19:0.497,20:0.510,21:0.523,22:0.534,23:0.545,24:0.555,25:0.565}
B4 = {2:3.267,3:2.568,4:2.266,5:2.089,6:1.970,7:1.882,8:1.815,9:1.761,10:1.716,11:1.679,12:1.646,13:1.618,14:1.594,15:1.572,16:1.552,17:1.534,18:1.518,19:1.503,20:1.490,21:1.477,22:1.466,23:1.455,24:1.445,25:1.435}

def c4(n):
    return math.sqrt(2/(n-1)) * (math.gamma(n/2) / math.gamma((n-1)/2))

def norm_ppf(p):
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
          6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow = 0.02425
    phigh = 1 - plow
    if p <= 0.0:
        return -float("inf")
    if p >= 1.0:
        return float("inf")
    if p < plow:
        q = math.sqrt(-2*math.log(p))
        return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
               ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    if p > phigh:
        q = math.sqrt(-2*math.log(1-p))
        return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
                 ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    q = p - 0.5
    r = q*q
    return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5]) * q / \
           (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1)

def get_data_from_cells(entries):
    vals = []
    for i, e in enumerate(entries, start=1):
        t = e.get().strip()
        if t == "":
            continue
        try:
            vals.append(float(t))
        except:
            raise ValueError(f"Dato inválido en celda {i}: '{t}'")
    if len(vals) < 2:
        raise ValueError("Se requieren al menos 2 datos.")
    return vals

def make_subgroups(data, gsize):
    if gsize < 2:
        raise ValueError("El tamaño de subgrupo debe ser >= 2.")
    k = len(data) // gsize
    if k < 2:
        raise ValueError("Se requieren al menos 2 subgrupos completos.")
    data2 = data[:k*gsize]
    return [data2[i*gsize:(i+1)*gsize] for i in range(k)]

def calc_overall(data):
    mu = stats.mean(data)
    s = stats.stdev(data)
    return mu, s*s, s

def calc_within(subs):
    s_list = [stats.stdev(sg) for sg in subs]
    sbar = stats.mean(s_list)
    n = len(subs[0])
    c4n = c4(n)
    if not (c4n > 0):
        raise ValueError("No se pudo calcular c4(n).")
    sigma_within = sbar / c4n
    return s_list, sbar, sigma_within

def calc_cp_cpk(mu, sigma, lsl, usl):
    cp = (usl - lsl) / (6*sigma)
    cpk = min((usl-mu)/(3*sigma), (mu-lsl)/(3*sigma))
    return cp, cpk

def calc_cpm(mu, sigma, lsl, usl, target):
    return (usl - lsl) / (6*math.sqrt(sigma*sigma + (mu-target)**2))

class App:
    def __init__(self, root):
        self.root = root
        root.title("Capacidad del Proceso – Sixpack")
        root.geometry("1400x800")
        root.minsize(1200, 720)

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except:
            pass
        self.style.configure("Card.TFrame", padding=12)
        self.style.configure("H1.TLabel", font=("Helvetica", 14, "bold"))
        self.style.configure("H2.TLabel", font=("Helvetica", 11, "bold"))
        self.style.configure("Mono.TLabel", font=("Menlo", 12))
        self.style.configure("Primary.TButton", font=("Helvetica", 12, "bold"))

        self.bg = self.style.lookup("TFrame", "background") or "#f0f0f0"

        self.main = ttk.Frame(root, padding=10)
        self.main.pack(fill="both", expand=True)

        self.main.columnconfigure(0, weight=0)
        self.main.columnconfigure(1, weight=1)
        self.main.rowconfigure(0, weight=1)

        self.left = ttk.Frame(self.main, width=480)
        self.left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.right = ttk.Frame(self.main)
        self.right.grid(row=0, column=1, sticky="nsew")

        self.left.grid_rowconfigure(2, weight=1)
        self.left.grid_columnconfigure(0, weight=1)

        head = ttk.Frame(self.left)
        head.grid(row=0, column=0, sticky="ew")
        ttk.Label(head, text="Capacidad del Proceso", style="H1.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(head, text="Cp / Cpk / Cpm + Sixpack", foreground="#888").grid(row=1, column=0, sticky="w", pady=(2, 0))

        controls = ttk.Frame(self.left, style="Card.TFrame")
        controls.grid(row=1, column=0, sticky="ew", pady=(10, 10))
        for col in (1, 3, 5):
            controls.columnconfigure(col, weight=1)

        ttk.Label(controls, text="Especificaciones", style="H2.TLabel").grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))

        ttk.Label(controls, text="LSL").grid(row=1, column=0, sticky="w")
        self.entry_lsl = ttk.Entry(controls, width=12)
        self.entry_lsl.grid(row=1, column=1, sticky="ew", padx=(6, 14))
        self.entry_lsl.insert(0, "7.83")

        ttk.Label(controls, text="USL").grid(row=1, column=2, sticky="w")
        self.entry_usl = ttk.Entry(controls, width=12)
        self.entry_usl.grid(row=1, column=3, sticky="ew", padx=(6, 14))
        self.entry_usl.insert(0, "8.07")

        ttk.Label(controls, text="Target").grid(row=1, column=4, sticky="w")
        self.entry_target = ttk.Entry(controls, width=12)
        self.entry_target.grid(row=1, column=5, sticky="ew", padx=(6, 0))
        self.entry_target.insert(0, "7.92")

        ttk.Label(controls, text="Subgrupo n").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.entry_gsize = ttk.Entry(controls, width=12)
        self.entry_gsize.grid(row=2, column=1, sticky="w", padx=(6, 14), pady=(10, 0))
        self.entry_gsize.insert(0, "10")

        self.var_labels = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Etiquetar puntos", variable=self.var_labels).grid(row=2, column=2, columnspan=2, sticky="w", pady=(10, 0))

        ttk.Label(controls, text="Gráfica").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.combo = ttk.Combobox(controls, state="readonly", width=26)
        self.combo["values"] = (
            "Capability Histogram",
            "Xbar Chart",
            "S Chart",
            "Normal Prob Plot",
            "Last Subgroups",
            "Capability Plot"
        )
        self.combo.current(0)
        self.combo.grid(row=3, column=1, columnspan=3, sticky="ew", padx=(6, 14), pady=(10, 0))

        ttk.Button(controls, text="Calcular / Actualizar", style="Primary.TButton", command=self.update_all).grid(row=4, column=0, columnspan=6, sticky="ew", pady=(12, 6))

        btns = ttk.Frame(controls)
        btns.grid(row=5, column=0, columnspan=6, sticky="ew")
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)
        btns.columnconfigure(2, weight=1)

        ttk.Button(btns, text="Guardar", command=self.save_results).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(btns, text="Cargar", command=self.load_results).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(btns, text="Vaciar", command=self.clear_all).grid(row=0, column=2, sticky="ew", padx=(6, 0))

        data_card = ttk.Frame(self.left, style="Card.TFrame")
        data_card.grid(row=2, column=0, sticky="nsew")
        data_card.grid_rowconfigure(1, weight=1)
        data_card.grid_columnconfigure(0, weight=1)

        ttk.Label(data_card, text="Datos (mm)", style="H2.TLabel").grid(row=0, column=0, sticky="w")

        self.data_canvas = tk.Canvas(data_card, highlightthickness=0, bd=0, background=self.bg)
        self.data_canvas.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        vs = ttk.Scrollbar(data_card, orient="vertical", command=self.data_canvas.yview)
        vs.grid(row=1, column=1, sticky="ns", pady=(8, 0))
        hs = ttk.Scrollbar(data_card, orient="horizontal", command=self.data_canvas.xview)
        hs.grid(row=2, column=0, sticky="ew")

        self.data_canvas.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)

        self.data_inner = ttk.Frame(self.data_canvas)
        self.data_window = self.data_canvas.create_window((0, 0), window=self.data_inner, anchor="nw")

        self.data_entries = []
        self.default_data = [
            7.946,7.966,7.949,7.961,7.967,7.969,7.955,7.951,7.944,7.966,
            7.964,7.957,7.948,7.941,7.967,7.940,7.956,7.955,7.957,7.943,
            7.946,7.958,7.952,7.950,7.941,7.960,7.944,7.947,7.978,7.89,
            7.976,7.979,7.977,7.977,7.977,7.955,7.84,7.98,7.940,7.951,
            7.943,7.959,7.941,7.960,7.951,7.951,7.976,7.947,7.981,7.9,
            7.9,7.979,7.969,7.947,8.01,7.99,7.91,7.982,7.934,7.944,
            7.937,7.922,7.933,7.957,7.947,7.942,7.86,7.966,7.92,7.969,
            8.05,7.98,7.85,7.954,7.93,7.949,7.961,7.87,7.950,7.964,
            7.942,7.940,7.957,8.03,7.965,7.965,7.913,7.957,7.968,7.956,
            7.962,7.965,7.966,7.948,7.969,7.952,7.945,7.954,7.947,7.950
        ]
        for v in self.default_data:
            e = ttk.Entry(self.data_inner, width=10, justify="center")
            e.insert(0, str(v))
            self.data_entries.append(e)

        self.current_cols = 0

        self.data_inner.bind("<Configure>", lambda e: self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all")))
        self.data_canvas.bind("<Configure>", self._on_canvas_resize)

        def _on_mousewheel(event):
            self.data_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _on_shift_mousewheel(event):
            self.data_canvas.xview_scroll(int(-1*(event.delta/120)), "units")

        self.data_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.data_canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)

        out_card = ttk.Frame(self.right, style="Card.TFrame")
        out_card.pack(fill="x", pady=(0, 10))
        out_card.columnconfigure(0, weight=1)

        ttk.Label(out_card, text="Resultados", style="H2.TLabel").grid(row=0, column=0, sticky="w")
        self.output = tk.StringVar(value="")
        ttk.Label(out_card, textvariable=self.output, style="Mono.TLabel", justify="left").grid(row=1, column=0, sticky="w", pady=(6, 0))

        plot_card = ttk.Frame(self.right, style="Card.TFrame")
        plot_card.pack(fill="both", expand=True)
        plot_card.columnconfigure(0, weight=1)
        plot_card.rowconfigure(0, weight=1)

        self.fig = Figure(figsize=(8.6, 6.2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_card)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.combo.bind("<<ComboboxSelected>>", lambda e: self.update_plot_only())

        self.state = None
        self.update_all()

    def _ensure_entries_count(self, n):
        cur = len(self.data_entries)
        if n == cur:
            return
        if n > cur:
            for _ in range(n - cur):
                e = ttk.Entry(self.data_inner, width=10, justify="center")
                self.data_entries.append(e)
        else:
            for e in self.data_entries[n:]:
                e.grid_forget()
                e.destroy()
            self.data_entries = self.data_entries[:n]
        self._relayout_cells(self.current_cols if self.current_cols else 8)

    def _relayout_cells(self, cols):
        if cols < 3:
            cols = 3
        for e in self.data_entries:
            e.grid_forget()
        for i, e in enumerate(self.data_entries):
            r = i // cols
            c = i % cols
            e.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
        self.current_cols = cols

    def _on_canvas_resize(self, event):
        self.data_canvas.itemconfigure(self.data_window, width=event.width)
        cell_px = 92
        cols = max(4, event.width // cell_px)
        if cols != self.current_cols:
            self._relayout_cells(cols)

    def _current_payload(self):
        data = []
        for e in self.data_entries:
            t = e.get().strip()
            if t == "":
                data.append(None)
            else:
                try:
                    data.append(float(t))
                except:
                    data.append(t)
        payload = {
            "lsl": self.entry_lsl.get().strip(),
            "usl": self.entry_usl.get().strip(),
            "target": self.entry_target.get().strip(),
            "gsize": self.entry_gsize.get().strip(),
            "graph": self.combo.get(),
            "labels": bool(self.var_labels.get()),
            "data": data,
            "results_text": self.output.get()
        }
        return payload

    def save_results(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if not path:
            return
        try:
            payload = self._current_payload()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    def load_results(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            self.entry_lsl.delete(0, "end")
            self.entry_lsl.insert(0, str(payload.get("lsl", "7.83")))
            self.entry_usl.delete(0, "end")
            self.entry_usl.insert(0, str(payload.get("usl", "8.07")))
            self.entry_target.delete(0, "end")
            self.entry_target.insert(0, str(payload.get("target", "7.92")))
            self.entry_gsize.delete(0, "end")
            self.entry_gsize.insert(0, str(payload.get("gsize", "10")))

            self.var_labels.set(bool(payload.get("labels", False)))

            graph = payload.get("graph", "Capability Histogram")
            if graph in self.combo["values"]:
                self.combo.set(graph)

            data_list = payload.get("data", [])
            if isinstance(data_list, list) and len(data_list) > 0:
                self._ensure_entries_count(len(data_list))
                for e, v in zip(self.data_entries, data_list):
                    e.delete(0, "end")
                    if v is None:
                        continue
                    e.insert(0, str(v))
            self.update_all()
        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    def clear_all(self):
        for e in self.data_entries:
            e.delete(0, "end")
        self.output.set("")
        self.state = None
        self.ax.clear()
        self.canvas.draw()

    def compute(self):
        data = get_data_from_cells(self.data_entries)
        lsl = float(self.entry_lsl.get())
        usl = float(self.entry_usl.get())
        target = float(self.entry_target.get())
        gsize = int(float(self.entry_gsize.get()))
        subs = make_subgroups(data, gsize)

        mu, var, s_overall = calc_overall(data)
        s_list, sbar, sigma_within = calc_within(subs)

        cp_w, cpk_w = calc_cp_cpk(mu, sigma_within, lsl, usl)
        cp_o, cpk_o = calc_cp_cpk(mu, s_overall, lsl, usl)
        cpm_o = calc_cpm(mu, s_overall, lsl, usl, target)

        xbars = [stats.mean(sg) for sg in subs]
        return {
            "data": data, "lsl": lsl, "usl": usl, "target": target, "gsize": gsize,
            "subs": subs, "mu": mu, "var": var, "s_overall": s_overall, "sigma_within": sigma_within,
            "cp_w": cp_w, "cpk_w": cpk_w, "cp_o": cp_o, "cpk_o": cpk_o, "cpm_o": cpm_o,
            "xbars": xbars, "s_list": s_list
        }

    def update_all(self):
        try:
            self.state = self.compute()
            s = self.state
            ok_ss = (s["cp_w"] >= 2 and s["cpk_w"] >= 2 and s["cpm_o"] >= 2)
            verdict = "CUMPLE SEIS SIGMA" if ok_ss else "NO CUMPLE SEIS SIGMA"

            self.output.set(
                f"n = {len(s['data'])}\n"
                f"LSL = {s['lsl']:.3f}    USL = {s['usl']:.3f}    Target = {s['target']:.3f}\n\n"
                f"Media: {s['mu']:.5f} mm\n"
                f"Varianza: {s['var']:.6f}\n"
                f"StDev Overall: {s['s_overall']:.5f} mm\n"
                f"StDev Within:  {s['sigma_within']:.5f} mm\n\n"
                f"Within:  Cp = {s['cp_w']:.3f}   Cpk = {s['cpk_w']:.3f}\n"
                f"Overall: Cp = {s['cp_o']:.3f}   Cpk = {s['cpk_o']:.3f}   Cpm = {s['cpm_o']:.3f}\n\n"
                f"Evaluación: {verdict}"
            )
            self.update_plot_only()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_plot_only(self):
        if not self.state:
            return
        name = self.combo.get()
        if name == "Capability Histogram":
            self.plot_hist()
        elif name == "Xbar Chart":
            self.plot_xbar()
        elif name == "S Chart":
            self.plot_s()
        elif name == "Normal Prob Plot":
            self.plot_qq()
        elif name == "Last Subgroups":
            self.plot_last()
        elif name == "Capability Plot":
            self.plot_capability()
        self.canvas.draw()

    def plot_hist(self):
        s = self.state
        data = s["data"]
        lsl, usl, target = s["lsl"], s["usl"], s["target"]
        mu, sig = s["mu"], s["s_overall"]

        self.ax.clear()
        _, bins, _ = self.ax.hist(data, bins=15)

        xmin, xmax = min(data), max(data)
        pad = (xmax - xmin) * 0.08 if xmax > xmin else 0.01
        x1, x2 = xmin - pad, xmax + pad

        xs = [x1 + i*(x2-x1)/300 for i in range(301)]
        binw = bins[1] - bins[0] if len(bins) > 1 else 1.0
        ys = []
        for x in xs:
            pdf = (1/(sig*math.sqrt(2*math.pi))) * math.exp(-0.5*((x-mu)/sig)**2)
            ys.append(pdf * len(data) * binw)
        self.ax.plot(xs, ys)

        self.ax.axvline(lsl, linestyle="--")
        self.ax.axvline(usl, linestyle="--")
        self.ax.axvline(target, linestyle=":")
        self.ax.axvline(mu, linewidth=2)

        self.ax.set_title("Capability Histogram")
        self.ax.set_xlabel("Diámetro (mm)")
        self.ax.set_ylabel("Frecuencia")

    def plot_xbar(self):
        s = self.state
        xbars = s["xbars"]
        s_list = s["s_list"]
        n = s["gsize"]
        a3 = A3.get(n)
        if a3 is None:
            raise ValueError("n de subgrupo no soportado para Xbar-S (use 2..25).")

        xbarbar = stats.mean(xbars)
        sbar = stats.mean(s_list)
        ucl = xbarbar + a3*sbar
        lcl = xbarbar - a3*sbar

        self.ax.clear()
        xs = list(range(1, len(xbars)+1))
        self.ax.plot(xs, xbars, marker="o")
        self.ax.axhline(xbarbar, linewidth=2)
        self.ax.axhline(ucl, linestyle="--")
        self.ax.axhline(lcl, linestyle="--")

        if self.var_labels.get():
            for i, y in enumerate(xbars, start=1):
                self.ax.annotate(str(i), (i, y), textcoords="offset points", xytext=(6, 6), fontsize=9)

        self.ax.set_title("Xbar Chart")
        self.ax.set_xlabel("Subgrupo")
        self.ax.set_ylabel("Media del subgrupo")

    def plot_s(self):
        s = self.state
        s_list = s["s_list"]
        n = s["gsize"]
        b3 = B3.get(n)
        b4 = B4.get(n)
        if b3 is None or b4 is None:
            raise ValueError("n de subgrupo no soportado para Xbar-S (use 2..25).")

        sbar = stats.mean(s_list)
        ucl = b4*sbar
        lcl = b3*sbar

        self.ax.clear()
        xs = list(range(1, len(s_list)+1))
        self.ax.plot(xs, s_list, marker="o")
        self.ax.axhline(sbar, linewidth=2)
        self.ax.axhline(ucl, linestyle="--")
        self.ax.axhline(lcl, linestyle="--")

        if self.var_labels.get():
            for i, y in enumerate(s_list, start=1):
                self.ax.annotate(str(i), (i, y), textcoords="offset points", xytext=(6, 6), fontsize=9)

        self.ax.set_title("S Chart")
        self.ax.set_xlabel("Subgrupo")
        self.ax.set_ylabel("StDev del subgrupo")

    def plot_qq(self):
        s = self.state
        data = sorted(s["data"])
        n = len(data)
        theo = [norm_ppf((i-0.5)/n) for i in range(1, n+1)]

        self.ax.clear()
        self.ax.scatter(theo, data)

        x1, x2 = min(theo), max(theo)
        y1, y2 = min(data), max(data)
        self.ax.plot([x1, x2], [y1, y2], linestyle="--")

        if self.var_labels.get():
            for i, (x, y) in enumerate(zip(theo, data), start=1):
                if i % 3 == 0:
                    self.ax.annotate(str(i), (x, y), textcoords="offset points", xytext=(5, 5), fontsize=8)

        self.ax.set_title("Normal Prob Plot (QQ Plot)")
        self.ax.set_xlabel("Cuantiles teóricos (Normal)")
        self.ax.set_ylabel("Datos ordenados")

    def plot_last(self):
        s = self.state
        subs = s["subs"]
        k = len(subs)
        start = max(0, k-10)
        sub_last = subs[start:]

        xs, ys, labs = [], [], []
        for j, sg in enumerate(sub_last, start=start+1):
            for i, v in enumerate(sg, start=1):
                xs.append(j)
                ys.append(v)
                labs.append(f"{j}.{i}")

        self.ax.clear()
        self.ax.scatter(xs, ys)

        if self.var_labels.get():
            for x, y, lab in zip(xs, ys, labs):
                self.ax.annotate(lab, (x, y), textcoords="offset points", xytext=(4, 4), fontsize=7)

        self.ax.set_title("Last 10 Subgroups")
        self.ax.set_xlabel("Subgrupo")
        self.ax.set_ylabel("Valores")

    def plot_capability(self):
        s = self.state
        lsl, usl, target = s["lsl"], s["usl"], s["target"]
        mu = s["mu"]
        sig_w = s["sigma_within"]
        sig_o = s["s_overall"]

        self.ax.clear()
        self.ax.set_title("Capability Plot")
        self.ax.set_xlabel("Diámetro (mm)")
        self.ax.set_yticks([3, 2, 1])
        self.ax.set_yticklabels(["Overall", "Within", "Specs"])
        self.ax.set_ylim(0.5, 3.7)

        def seg(y, center, sig):
            left = center - 3*sig
            right = center + 3*sig
            self.ax.hlines(y, left, right, linewidth=6)
            self.ax.vlines([left, center, right], y-0.13, y+0.13)

        seg(3, mu, sig_o)
        seg(2, mu, sig_w)
        self.ax.hlines(1, lsl, usl, linewidth=6)
        self.ax.vlines([lsl, target, usl], 1-0.13, 1+0.13, linestyles="--")

        box = (
            f"Within\nStDev {sig_w:.5f}\nCp {s['cp_w']:.2f}\nCpk {s['cpk_w']:.2f}\n\n"
            f"Overall\nStDev {sig_o:.5f}\nCp {s['cp_o']:.2f}\nCpk {s['cpk_o']:.2f}\nCpm {s['cpm_o']:.2f}"
        )
        self.ax.text(0.98, 0.97, box, transform=self.ax.transAxes, ha="right", va="top",
                     bbox=dict(boxstyle="round,pad=0.4", alpha=0.2))

        if self.var_labels.get():
            self.ax.annotate("LSL", (lsl, 1), textcoords="offset points", xytext=(0, 10), ha="center")
            self.ax.annotate("T", (target, 1), textcoords="offset points", xytext=(0, 10), ha="center")
            self.ax.annotate("USL", (usl, 1), textcoords="offset points", xytext=(0, 10), ha="center")

root = tk.Tk()
App(root)
root.mainloop()


