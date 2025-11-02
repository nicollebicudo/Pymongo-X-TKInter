import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
from pymongo import MongoClient

#*********************************************CONEXAO E CRIAR CHAVE*******************************************************

DATA_DIR = Path(r"C:\Users\User\Documents\BANCODEDADOS")
DATA_DIR.mkdir(parents=True, exist_ok=True)
KEY_FILE = DATA_DIR / "chave.key"

if KEY_FILE.exists():
    fernet_key = KEY_FILE.read_bytes()
    is_first_run = False
else:
    fernet_key = Fernet.generate_key()
    KEY_FILE.write_bytes(fernet_key)
    print(f"Arquivo 'chave.key' criado em: {DATA_DIR}")
    is_first_run = True

if is_first_run:
    print("=" * 60)
    print("SUA CHAVE DE ACESSO:")
    print(fernet_key.decode())
    print("=" * 60)

fernet = Fernet(fernet_key)


MONGO_URI = "mongodb+srv://nicollebicudo:123@apicluster.tr7tovm.mongodb.net/?appName=APICluster"
DB_NAME = "halloween"
COLLECTION_NAME = "doces"
mongo = MongoClient(MONGO_URI)
doces = mongo[DB_NAME][COLLECTION_NAME]

#*****************************************************************CADASTRAR************************************************************

def cadastrar():
    nome = entry_nome.get().strip()
    tipo = entry_tipo.get().strip()
    qtd = entry_qtd.get().strip()
    time = entry_time.get().strip()
    try:
        qtd = int(qtd)
    except Exception as error:
        messagebox.showerror("Erro", str(error))
        return
    timestamp = time or datetime.now().isoformat(timespec="seconds")
    token = fernet.encrypt(tipo.encode())
    doc = {"child": nome, "candy_type": token, "qty": qtd, "timestamp": timestamp}
    doces.insert_one(doc)
    messagebox.showinfo("Sucesso", "Doce cadastrado com sucesso!")
    entry_nome.delete(0, tk.END)
    entry_tipo.delete(0, tk.END)
    entry_qtd.delete(0, tk.END)
    entry_time.delete(0, tk.END)

#****************************************************************LISTAR*******************************************************************

def listar():
    text_output.delete(1.0, tk.END)
    for d in doces.find({}, {"_id": 0, "child": 1, "candy_type": 1, "qty": 1, "timestamp": 1}):
        text_output.insert(tk.END, "\n")
        text_output.insert(tk.END, f"child: {d.get('child')}\n")
        candy = d.get('candy_type')
        if isinstance(candy, bytes):
            text_output.insert(tk.END, f"candy_type: {candy.decode()}\n")
        else:
            text_output.insert(tk.END, f"candy_type: {candy}\n")
        text_output.insert(tk.END, f"qty: {d.get('qty')}\n")
        text_output.insert(tk.END, f"timestamp: {d.get('timestamp')}\n")

#**************************************************************LISTAR DEC*****************************************************************

def listar_desc():
    chave_txt = entry_chave.get().strip()
    try:
        leitor = Fernet(chave_txt.encode())
    except Exception:
        messagebox.showerror("Erro", "Chave inválida.")
        return
    cursor = doces.find(
        {"candy_type": {"$exists": True}},
        {"_id": 0, "child": 1, "candy_type": 1, "qty": 1, "timestamp": 1},
    )
    text_output.delete(1.0, tk.END)
    for d in cursor:
        token = d.get("candy_type")
        if not token:
            continue
        try:
            if isinstance(token, str):
                token = token.encode()
            tipo = leitor.decrypt(token).decode()
        except InvalidToken:
            messagebox.showerror("Erro", "Acesso negado!!! (chave não corresponde)")
            return
        text_output.insert(tk.END, "\n")
        text_output.insert(tk.END, f"child: {d.get('child')}\n")
        text_output.insert(tk.END, f"tipo: {tipo}\n")
        text_output.insert(tk.END, f"qty: {d.get('qty')}\n")
        text_output.insert(tk.END, f"timestamp: {d.get('timestamp')}\n")

#**************************************************************MAIN************************************************************************

root = tk.Tk()
root.title("Gerenciamento de Doces - Halloween")
root.geometry("750x650")
root.configure(bg="#f0f0f0")

style = ttk.Style()
style.configure("TNotebook", background="#f0f0f0")
style.configure("TFrame", background="#f0f0f0")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

frame_cadastrar = ttk.Frame(notebook)
notebook.add(frame_cadastrar, text="📝 Cadastrar")

inner_frame_cadastro = tk.Frame(frame_cadastrar, bg="white", relief=tk.RIDGE, bd=2)
inner_frame_cadastro.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

tk.Label(inner_frame_cadastro, text="Nome:", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=15, pady=10)
entry_nome = ttk.Entry(inner_frame_cadastro, width=45, font=("Arial", 10))
entry_nome.grid(row=0, column=1, padx=15, pady=10)

tk.Label(inner_frame_cadastro, text="Tipo do doce:", bg="white", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=15, pady=10)
entry_tipo = ttk.Entry(inner_frame_cadastro, width=45, font=("Arial", 10))
entry_tipo.grid(row=1, column=1, padx=15, pady=10)

tk.Label(inner_frame_cadastro, text="Quantidade:", bg="white", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=15, pady=10)
entry_qtd = ttk.Entry(inner_frame_cadastro, width=45, font=("Arial", 10))
entry_qtd.grid(row=2, column=1, padx=15, pady=10)

tk.Label(inner_frame_cadastro, text="Dia (YYYY-MM-DD HH:MM):", bg="white", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, padx=15, pady=10)
entry_time = ttk.Entry(inner_frame_cadastro, width=45, font=("Arial", 10))
entry_time.grid(row=3, column=1, padx=15, pady=10)
tk.Label(inner_frame_cadastro, text="(deixe vazio para agora)", bg="white", font=("Arial", 8), fg="gray").grid(row=4, column=1, sticky=tk.W, padx=15)

btn_cadastrar = tk.Button(inner_frame_cadastro, text="✓ Cadastrar", command=cadastrar, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), relief=tk.RAISED, bd=3, padx=20, pady=8)
btn_cadastrar.grid(row=5, column=0, columnspan=2, pady=25)

frame_listar = ttk.Frame(notebook)
notebook.add(frame_listar, text="📋 Listar")

inner_frame_listar = tk.Frame(frame_listar, bg="white", relief=tk.RIDGE, bd=2)
inner_frame_listar.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

frame_buttons = tk.Frame(inner_frame_listar, bg="white")
frame_buttons.pack(pady=15)

btn_listar = tk.Button(frame_buttons, text="📄 Listar Todos", command=listar, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), relief=tk.RAISED, bd=3, padx=15, pady=8)
btn_listar.pack(side=tk.LEFT, padx=10)

frame_chave = tk.Frame(inner_frame_listar, bg="#f9f9f9", relief=tk.GROOVE, bd=2)
frame_chave.pack(pady=10, padx=15, fill=tk.X)

tk.Label(frame_chave, text="🔑 Chave Fernet (para descriptografar):", bg="#f9f9f9", font=("Arial", 10, "bold")).pack(pady=8)
entry_chave = ttk.Entry(frame_chave, width=60, font=("Arial", 9))
entry_chave.pack(pady=5)

btn_listar_chave = tk.Button(frame_chave, text="🔓 Listar com Chave", command=listar_desc, bg="#FF9800", fg="white", font=("Arial", 10, "bold"), relief=tk.RAISED, bd=3, padx=15, pady=8)
btn_listar_chave.pack(pady=10)

tk.Label(inner_frame_listar, text="Resultados:", bg="white", font=("Arial", 10, "bold")).pack(pady=(15, 5))
text_output = scrolledtext.ScrolledText(inner_frame_listar, width=85, height=18, font=("Courier", 9), bg="#fafafa")
text_output.pack(padx=15, pady=(0, 15))

if __name__ == "__main__":
    root.mainloop()