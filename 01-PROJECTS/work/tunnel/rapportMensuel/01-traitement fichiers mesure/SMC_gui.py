# smc_gui.py – version courte avec dossier de sortie
import os, sys, subprocess, datetime, tkinter as tk
from tkinter import ttk, filedialog, messagebox

def month_str(y, m): return f"{y:04d}-{m:02d}"
def default_year_month():
    today = datetime.date.today()
    first_this = today.replace(day=1)
    last_month = first_this - datetime.timedelta(days=1)
    return last_month.year, last_month.month

def run_extraction(root_dir, y_m, out_dir):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    batch = os.path.join(script_dir, "smc_evolutions.py")
    #batch = os.path.join(script_dir, "smc_deplacements.py")
    if not os.path.exists(batch):
        raise FileNotFoundError(f"Introuvable : {batch}")
    args = [sys.executable, batch, "--root", root_dir]
    if y_m: args += ["--month", y_m]
    if out_dir: args += ["--out", out_dir]
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SMC Extract – Lanceur")
        self.geometry("600x340")
        self.root_dir = tk.StringVar()
        y,m = default_year_month()
        self.year  = tk.StringVar(value=str(y))
        self.month = tk.StringVar(value=f"{m:02d}")
        self.filter_enabled = tk.BooleanVar(value=True)
        self.out_dir = tk.StringVar(value="")
        self.build()

    def build(self):
        frm = ttk.Frame(self); frm.pack(fill="both", expand=True, padx=10, pady=8)
        row=0
        ttk.Label(frm, text="Dossier racine :").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.root_dir).grid(row=row, column=1, sticky="we", padx=6)
        ttk.Button(frm, text="Parcourir…", command=self.browse_root).grid(row=row, column=2, sticky="w"); row+=1

        ttk.Checkbutton(frm, variable=self.filter_enabled, text="Filtrer par mois de modification").grid(row=row, column=0, sticky="w")
        box=ttk.Frame(frm); box.grid(row=row, column=1, sticky="w"); row+=1
        ttk.Combobox(box, textvariable=self.year, width=6, state="readonly",
                     values=[str(y) for y in range(datetime.date.today().year-5, datetime.date.today().year+1)]).pack(side="left")
        ttk.Label(box, text="-").pack(side="left", padx=4)
        ttk.Combobox(box, textvariable=self.month, width=4, state="readonly",
                     values=[f"{i:02d}" for i in range(1,13)]).pack(side="left")

        ttk.Label(frm, text="Dossier de sortie :").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.out_dir).grid(row=row, column=1, sticky="we", padx=6)
        ttk.Button(frm, text="Choisir…", command=self.choose_out_dir).grid(row=row, column=2, sticky="w"); row+=1

        btns=ttk.Frame(frm); btns.grid(row=row, column=0, columnspan=3, sticky="we", pady=(10,0)); row+=1
        ttk.Button(btns, text="Lancer l’extraction", command=self.launch).pack(side="left")
        ttk.Button(btns, text="Quitter", command=self.destroy).pack(side="right")

        ttk.Label(frm, text="Journal :").grid(row=row, column=0, sticky="w", pady=(12,0)); row+=1
        self.txt = tk.Text(frm, height=10); self.txt.grid(row=row, column=0, columnspan=3, sticky="nsew")
        frm.rowconfigure(row, weight=1); frm.columnconfigure(1, weight=1)

    def browse_root(self):
        d = filedialog.askdirectory(title="Choisir le dossier racine")
        if d: self.root_dir.set(d)

    def choose_out_dir(self):
        d = filedialog.askdirectory(title="Choisir le dossier de sortie")
        if d: self.out_dir.set(d)

    def log(self, msg):
        self.txt.insert("end", msg + "\n"); self.txt.see("end"); self.update_idletasks()

    def launch(self):
        root_dir = self.root_dir.get().strip()
        if not root_dir: return messagebox.showwarning("Paramètre manquant","Sélectionne un dossier racine.")
        if not os.path.isdir(root_dir): return messagebox.showerror("Invalide", f"Introuvable : {root_dir}")

        y_m=None
        if self.filter_enabled.get():
            y, m = self.year.get(), self.month.get()
            y_m = f"{y}-{m}"

        out_dir = self.out_dir.get().strip() or root_dir
        self.txt.delete("1.0","end")
        self.log(f"⏳ Dossier : {root_dir}")
        self.log(f"   Mois    : {y_m or 'Aucun'}")
        self.log(f"   Sortie  : {out_dir}")
        try:
            proc = run_extraction(root_dir, y_m, out_dir)
            if proc.stdout: self.log("— STDOUT —\n"+proc.stdout.strip())
            if proc.stderr: self.log("— STDERR —\n"+proc.stderr.strip())
            if proc.returncode==0:
                self.log("✅ Terminé")
                messagebox.showinfo("OK", "Extraction terminée.\nRegarde les CSV dans le dossier de sortie.")
            else:
                self.log(f"❌ Code {proc.returncode}")
                messagebox.showerror("Erreur", "Le script a retourné une erreur.\nVoir le journal.")
        except Exception as e:
            self.log(f"❌ Exception : {e}")
            messagebox.showerror("Exception", str(e))

if __name__ == "__main__":
    App().mainloop()
