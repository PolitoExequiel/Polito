import hashlib, json, os, re, subprocess, sys, tempfile, tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import fitz

BASE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "DuxTicketPellegrini"
BASE.mkdir(parents=True, exist_ok=True)
CONFIG = BASE / "config.json"
HISTORY = BASE / "impresiones.json"

def read_json(path, default):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError): return default

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def parse_pdf(path):
    with fitz.open(path) as doc:
        text = "\n".join(page.get_text(sort=True) for page in doc)
    if "EGRESO DE CAJA" not in text.upper():
        raise ValueError("El archivo no parece ser un egreso de caja de Dux.")
    def match(pattern, default="NO INFORMADO"):
        m = re.search(pattern, text, re.I | re.M)
        return m.group(1).strip() if m else default
    amount = match(r"TOTAL\s*:\s*\$?\s*([\d.,]+)")
    if amount == "NO INFORMADO":
        matches = re.findall(r"\$\s*([\d.,]+)", text)
        amount = matches[-1] if matches else amount
    return {
        "empresa": next((line.split("S.R.L")[0].strip() + " S.R.L" for line in text.splitlines() if "S.R.L" in line.upper()), "NO INFORMADO"),
        "fecha": match(r"FECHA\s*:\s*(\d{2}/\d{2}/\d{4})"),
        "caja": match(r"CAJA\s*:\s*(?:CAJA\s*:\s*)?(.+?)(?=\s+PERSONAL\s*:|$)"),
        "personal": match(r"PERSONAL\s*:\s*(.+)$"),
        "descripcion": match(r"DESCRIPCI[ÓO]N\s*:\s*(.+)$"),
        "medio": "EFECTIVO" if "EFECTIVO" in text.upper() else "NO INFORMADO",
        "importe": amount
    }

def ticket(data):
    # Keep lines short enough for typical 80mm thermal printer drivers.
    lines = [
        data["empresa"][:28], "EGRESO DE CAJA", "-" * 28,
        "Fecha: " + data["fecha"],
        "Caja: " + data["caja"][:22],
        "Personal: " + data["personal"][:19],
        "Concepto: " + data["descripcion"][:19],
        "Medio: " + data["medio"],
        "-" * 28,
        "TOTAL: $ " + data["importe"],
        "", "", "________________________",
        "Firma de quien recibe", "",
        "Documento no valido como factura"
    ]
    return "\n".join(lines)

def printers():
    if os.name != "nt": return []
    cmd = ["powershell.exe","-NoProfile","-Command",
           "Get-Printer | Select-Object -ExpandProperty Name"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=True)
        return [x.strip() for x in p.stdout.splitlines() if x.strip()]
    except Exception: return []

class App:
    def __init__(self, window):
        self.window = window
        window.title("Dux Ticket - Pellegrini v0.2 (58 mm)")
        window.geometry("560x540")
        self.path = None
        self.data = None
        cfg = read_json(CONFIG,{})
        ttk.Label(window,text="Comprobante de egreso Dux → Ticket 58 mm",font=("Segoe UI",13,"bold")).pack(pady=10)
        ttk.Button(window,text="1. Abrir PDF de egreso",command=self.open_pdf).pack(pady=5)
        ttk.Label(window,text="Impresora de Windows:").pack()
        self.printer = tk.StringVar(value=cfg.get("printer",""))
        self.combo = ttk.Combobox(window,textvariable=self.printer,values=printers(),width=60)
        self.combo.pack(pady=5)
        ttk.Button(window,text="Actualizar impresoras",command=lambda:self.combo.configure(values=printers())).pack()
        self.preview = tk.Text(window,width=50,height=17,font=("Consolas",10))
        self.preview.pack(padx=12,pady=10,fill="both",expand=True)
        bar = ttk.Frame(window);bar.pack(pady=5)
        ttk.Button(bar,text="2. Guardar ticket TXT",command=self.export).pack(side="left",padx=5)
        ttk.Button(bar,text="3. Imprimir",command=self.print_ticket).pack(side="left",padx=5)
        ttk.Button(bar,text="Reimprimir (confirmar)",command=lambda:self.print_ticket(force=True)).pack(side="left",padx=5)
        ttk.Label(window,text="v0.2: 58 mm. La captura desde Chrome sigue pendiente.",foreground="#555").pack(pady=5)
    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF","*.pdf")])
        if not path:return
        try: data = parse_pdf(path)
        except Exception as e:messagebox.showerror("No se pudo leer",str(e));return
        self.path,self.data = path,data
        self.preview.delete("1.0","end")
        self.preview.insert("1.0",ticket(data))
    def export(self):
        if not self.data:return messagebox.showwarning("Falta PDF","Abrí un PDF primero.")
        dest = filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Texto","*.txt")])
        if dest:Path(dest).write_text(ticket(self.data),encoding="utf-8")
    def print_ticket(self,force=False):
        if not self.data:return messagebox.showwarning("Falta PDF","Abrí un PDF primero.")
        if os.name != "nt":return messagebox.showerror("Windows requerido","La impresión se ejecuta en Windows.")
        printer = self.printer.get().strip()
        if not printer:return messagebox.showwarning("Falta impresora","Elegí la impresora de Windows.")
        key = hashlib.sha256(Path(self.path).read_bytes()).hexdigest()
        history = read_json(HISTORY,{})
        if key in history and not force:
            return messagebox.showwarning("Duplicado","Este PDF ya fue enviado a imprimir. Usá Reimprimir si corresponde.")
        if force and not messagebox.askyesno("Reimpresión","¿Querés volver a imprimir este comprobante?"):return
        save_json(CONFIG,{"printer":printer})
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp)/"ticket.txt"
            file.write_text(ticket(self.data),encoding="utf-8")
            script = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "print_ticket.ps1"
            cmd = ["powershell.exe","-NoProfile","-ExecutionPolicy","Bypass",
                   "-File",str(script),"-TicketFile",str(file),"-PrinterName",printer]
            try:
                proc = subprocess.run(cmd,capture_output=True,text=True,timeout=35)
                if proc.returncode:raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
            except Exception as e:
                return messagebox.showerror("Error de impresión",str(e))
        history[key] = {"archivo":Path(self.path).name,"impresora":printer,"estado":"enviado_a_cola"}
        save_json(HISTORY,history)
        messagebox.showinfo("Enviado","El trabajo fue enviado a la cola de Windows. Verificá la salida física del ticket.")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
