import tkinter as tk
from tkinter import messagebox
import sqlite3

def init_db():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            genero TEXT NOT NULL,
            email TEXT NOT NULL,
            celular TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def inserir_dados(nome, idade, cpf, genero, email, celular):
    try:
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pessoas (nome, idade, cpf, genero, email, celular)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, idade, cpf, genero, email, celular))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        if "cpf" in str(e).lower():
            mostrar_erro("CPF já cadastrado.")
        elif "celular" in str(e).lower():
            mostrar_erro("Celular já cadastrado.")
        else:
            mostrar_erro("Erro de integridade: " + str(e))
        return False
    except Exception as e:
        mostrar_erro("Erro inesperado: " + str(e))
        return False

def mostrar_erro(msg):
    messagebox.showwarning("Validação", msg)

def validar_dados(nome, idade, cpf, genero, email, celular):
    if not all([nome, idade, cpf, genero, email, celular]):
        mostrar_erro("Todos os campos são obrigatórios.")
        return False
    if not idade.isdigit():
        mostrar_erro("Idade deve conter apenas números.")
        return False
    if not cpf.isdigit() or len(cpf) != 11:
        mostrar_erro("CPF deve conter exatamente 11 dígitos numéricos.")
        return False
    if genero.upper() not in ["M", "F", "O"]:
        mostrar_erro("Gênero deve ser M, F ou O.")
        return False
    if '@' not in email:
        mostrar_erro("E-mail inválido. Deve conter '@'.")
        return False
    if not celular.isdigit():
        mostrar_erro("Celular deve conter apenas números.")
        return False
    return True

def adicionar():
    nome = entry_nome.get().strip()
    idade = entry_idade.get().strip()
    cpf = entry_cpf.get().strip().replace('.', '').replace('-', '')
    genero = entry_genero.get().strip().upper()
    email = entry_email.get().strip()
    celular = entry_celular.get().strip()
    if not validar_dados(nome, idade, cpf, genero, email, celular):
        return
    if inserir_dados(nome, idade, cpf, genero, email, celular):
        limpar_campos()
        listar()

def listar(selecionar_id=None, dados_personalizados=None):
    listbox.delete(0, tk.END)
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    if dados_personalizados:
        cursor.execute(dados_personalizados[0], dados_personalizados[1])
    else:
        cursor.execute("SELECT * FROM pessoas")
    global registros
    registros = cursor.fetchall()
    for idx, row in enumerate(registros):
        texto = f"ID: {row[0]} | Nome: {row[1]} | Idade: {row[2]} | CPF: {row[3]} | Gênero: {row[4]} | Email: {row[5]} | Celular: {row[6]}"
        listbox.insert(tk.END, texto)
        if selecionar_id and row[0] == selecionar_id:
            listbox.selection_set(idx)
            listbox.activate(idx)
    conn.close()

def deletar():
    selecionado = listbox.curselection()
    if not selecionado:
        mostrar_erro("Selecione um item para deletar.")
        return
    item = registros[selecionado[0]]
    id = item[0]
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pessoas WHERE id=?", (id,))
    conn.commit()
    conn.close()
    listar()
    limpar_campos()

def atualizar():
    selecionado = listbox.curselection()
    if not selecionado:
        mostrar_erro("Selecione um item para atualizar.")
        return
    item = registros[selecionado[0]]
    id = item[0]
    nome = entry_nome.get().strip()
    idade = entry_idade.get().strip()
    cpf = entry_cpf.get().strip().replace('.', '').replace('-', '')
    genero = entry_genero.get().strip().upper()
    email = entry_email.get().strip()
    celular = entry_celular.get().strip()
    if not validar_dados(nome, idade, cpf, genero, email, celular):
        return
    try:
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE pessoas
            SET nome=?, idade=?, cpf=?, genero=?, email=?, celular=?
            WHERE id=?
        ''', (nome, idade, cpf, genero, email, celular, id))
        conn.commit()
        conn.close()
        listar(selecionar_id=id)
        limpar_campos()
    except sqlite3.IntegrityError as e:
        if "cpf" in str(e).lower():
            mostrar_erro("CPF já cadastrado.")
        elif "celular" in str(e).lower():
            mostrar_erro("Celular já cadastrado.")
        else:
            mostrar_erro("Erro de integridade: " + str(e))
    except Exception as e:
        mostrar_erro("Erro inesperado: " + str(e))

def limpar_campos():
    for entry in [entry_nome, entry_idade, entry_cpf, entry_genero, entry_email, entry_celular]:
        entry.delete(0, tk.END)

def preencher_campos(event):
    selecionado = listbox.curselection()
    if not selecionado:
        return
    item = registros[selecionado[0]]
    entry_nome.delete(0, tk.END)
    entry_nome.insert(0, item[1])
    entry_idade.delete(0, tk.END)
    entry_idade.insert(0, item[2])
    entry_cpf.delete(0, tk.END)
    entry_cpf.insert(0, item[3])
    entry_genero.delete(0, tk.END)
    entry_genero.insert(0, item[4])
    entry_email.delete(0, tk.END)
    entry_email.insert(0, item[5])
    entry_celular.delete(0, tk.END)
    entry_celular.insert(0, item[6])

def abrir_janela_busca():
    def executar_busca():
        termo = entry_busca.get().strip()
        if not termo:
            mostrar_erro("Digite um termo para buscar.")
            return
        query = "SELECT * FROM pessoas WHERE 1=0"
        params = []
        if var_nome.get():
            query += " OR nome LIKE ?"
            params.append(f"%{termo}%")
        if var_cpf.get():
            query += " OR cpf LIKE ?"
            params.append(f"%{termo}%")
        if var_id.get():
            if termo.isdigit():
                query += " OR id=?"
                params.append(int(termo))
        listar(dados_personalizados=(query, params))
        janela.destroy()

    def limpar_filtros():
        var_nome.set(0)
        var_cpf.set(0)
        var_id.set(0)
        entry_busca.delete(0, tk.END)

    janela = tk.Toplevel(root)
    janela.title("Buscar Pessoa")
    frame_busca = tk.Frame(janela)
    frame_busca.pack(padx=10, pady=10)
    entry_busca = tk.Entry(frame_busca, width=40)
    entry_busca.pack(pady=5)
    var_nome = tk.IntVar()
    var_cpf = tk.IntVar()
    var_id = tk.IntVar()
    tk.Checkbutton(frame_busca, text="Nome", variable=var_nome).pack(anchor='w')
    tk.Checkbutton(frame_busca, text="CPF", variable=var_cpf).pack(anchor='w')
    tk.Checkbutton(frame_busca, text="ID", variable=var_id).pack(anchor='w')
    tk.Button(frame_busca, text="Buscar", command=executar_busca).pack(pady=5)
    tk.Button(frame_busca, text="Limpar Filtros", command=limpar_filtros).pack()

init_db()
root = tk.Tk()
root.title("Cadastro de Pessoas")
root.geometry("1000x600")
root.rowconfigure(10, weight=1)
root.columnconfigure(1, weight=1)
frame_form = tk.Frame(root)
frame_form.grid(row=0, column=0, columnspan=2, pady=10, sticky='n')
labels = ["Nome", "Idade", "CPF", "Gênero (M/F/O)", "Email", "Celular"]
entries = []
for i, texto in enumerate(labels):
    tk.Label(frame_form, text=texto + ":").grid(row=i, column=0, padx=5, pady=5, sticky='e')
    entry = tk.Entry(frame_form, width=30)
    entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
    entries.append(entry)
entry_nome, entry_idade, entry_cpf, entry_genero, entry_email, entry_celular = entries
frame_botoes = tk.Frame(root)
frame_botoes.grid(row=0, column=2, rowspan=7, padx=10, pady=10, sticky='n')
tk.Button(frame_botoes, text="Adicionar", width=15, command=adicionar).pack(pady=5)
tk.Button(frame_botoes, text="Atualizar", width=15, command=atualizar).pack(pady=5)
tk.Button(frame_botoes, text="Deletar", width=15, command=deletar).pack(pady=5)
tk.Button(frame_botoes, text="Listar", width=15, command=listar).pack(pady=5)
tk.Button(root, text="Procurar", command=abrir_janela_busca).grid(row=7, column=0, sticky='w', padx=10, pady=5)
frame_lista = tk.Frame(root)
frame_lista.grid(row=8, column=0, columnspan=3, sticky='nsew')
frame_lista.grid_columnconfigure(0, weight=1)
listbox = tk.Listbox(frame_lista, width=150)
listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
listbox.bind('<<ListboxSelect>>', preencher_campos)
listar()
root.mainloop()
