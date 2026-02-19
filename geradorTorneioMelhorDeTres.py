import tkinter as tk
from tkinter import messagebox, filedialog
import math
import os
import pandas as pd
from datetime import datetime
from PyPDF2 import PdfReader
import re
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

class TorneioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Torneio - Ranking Oficial")
        self.root.geometry("1000x900")
        
        self.bg = "#121212"
        self.card = "#1e1e1e"
        self.accent = "#ff6600"
        self.text = "white"
        self.root.configure(bg=self.bg)

        self.logo_path = None
        self.setup_ui_inicial()
        # No __init__ ou no início do iniciar_torneio, adicione:
        self.pagina_atual = 0

    def limpar_tela(self):
        for w in self.root.winfo_children(): w.destroy()

    def criar_area_rolagem(self):
        container = tk.Frame(self.root, bg=self.bg)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg=self.bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.bg)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((500, 0), window=scroll_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return scroll_frame

    def setup_ui_inicial(self):
        self.limpar_tela()
        self.historico_confrontos = []
        self.perdedores_geral = []
        self.competidores_dados = {}
        self.pontos_atleta_atual = {} 
        self.campeao = self.vice = self.terceiro = None
        self.em_repescagem = False
        

        tk.Label(self.root, text="RANKING E TORNEIO OFICIAL", fg=self.accent,
                  bg=self.bg, font=("Arial", 22, "bold")).pack(pady=15)

        card = tk.Frame(self.root, bg=self.card, padx=20, pady=10)
        card.pack(pady=10, fill="x", padx=40)

        f_info = tk.Frame(card, bg=self.card)
        f_info.pack(fill="x")

        tk.Label(f_info, text="NOME DA PROVA:", bg=self.card, fg=self.text).grid(row=0, column=0, sticky="w", padx=5)
        self.ent_prova = tk.Entry(f_info, width=25); self.ent_prova.insert(0, "TPM - DUELO"); self.ent_prova.grid(row=0, column=1, pady=5)

        tk.Label(f_info, text="CLUBE:", bg=self.card, fg=self.text).grid(row=0, column=2, sticky="w", padx=5)
        self.ent_clube = tk.Entry(f_info, width=25); self.ent_clube.insert(0, ""); self.ent_clube.grid(row=0, column=3, pady=5)

        tk.Label(f_info, text="CATEGORIA:", bg=self.card, fg=self.text).grid(row=1, column=0, sticky="w", padx=5)
        self.ent_cat = tk.Entry(f_info, width=25); self.ent_cat.insert(0, ""); self.ent_cat.grid(row=1, column=1, pady=5)

        tk.Label(f_info, text="DATA (DD/MM/AAAA):", bg=self.card, fg=self.text).grid(row=1, column=2, sticky="w", padx=5)
        self.ent_data = tk.Entry(f_info, width=25)
        self.ent_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_data.grid(row=1, column=3, pady=5)

        tk.Button(card, text="📄 IMPORTAR PDF (NOMES)", command=self.importar_pdf, font=("Arial", 9, "bold")).pack(pady=5)

        list_frame = tk.Frame(card, bg=self.card)
        list_frame.pack(fill="both", expand=True, pady=10)

        col1 = tk.Frame(list_frame, bg=self.card); col1.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(col1, text="NOMES", bg=self.card, fg=self.accent).pack()
        self.txt_nomes = tk.Text(col1, height=10, width=30); self.txt_nomes.pack(fill="both")

        col2 = tk.Frame(list_frame, bg=self.card); col2.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(col2, text="CPFs", bg=self.card, fg=self.accent).pack()
        self.txt_cpfs = tk.Text(col2, height=10, width=30); self.txt_cpfs.pack(fill="both")

        tk.Button(card, text="🖼️ SELECIONAR LOGO", command=self.selecionar_logo).pack(pady=5)

        tk.Button(self.root, text="GERAR COMPETIÇÃO", bg=self.accent, fg="white",
                  font=("Arial", 14, "bold"), command=self.iniciar_torneio, height=2).pack(pady=20)
        
       # --- SEÇÃO DE CRÉDITOS FIXA NA TELA INICIAL ---
        # Um separador visual sutil
        tk.Frame(self.root, height=1, bg="#333", bd=0).pack(fill="x", padx=100, pady=20)

        # Container para os créditos
        frame_creditos = tk.Frame(self.root, bg=self.bg)
        frame_creditos.pack(pady=10)

        # Nome com destaque
        tk.Label(frame_creditos, text="Rayssa Vicente da Silva Viegas", 
                 fg=self.accent, bg=self.bg, 
                 font=("Arial", 12, "bold")).pack()

        # Descrição e Contato em uma linha ou duas
        contato_texto = "Desenvolvedora de Software | Contato: rayssavicenteviegas@gmail.com"
        tk.Label(frame_creditos, text=contato_texto, 
                 fg=self.text, bg=self.bg, 
                 font=("Arial", 9, "italic")).pack()
    
    

    def selecionar_logo(self):
        tipos = [("Imagens", "*.png *.jpg *.jpeg *.ico")]
        self.logo_path = filedialog.askopenfilename(filetypes=tipos)
        if self.logo_path: messagebox.showinfo("Sucesso", "Logo carregada!")

    def importar_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path:
            return

        try:
            reader = PdfReader(path)
            texto_completo = ""

            # Extração de texto de todas as páginas para cobrir arquivos longos
            for pagina in reader.pages:
                page_text = pagina.extract_text()
                if page_text:
                    texto_completo += page_text + "\n"

            if not texto_completo.strip():
                return messagebox.showwarning("Aviso", "O PDF não contém texto selecionável.")

            nomes_extraidos = []
            cpfs_extraidos = []

            # 1. Captura global de CPFs para casos de listas separadas (como no teste3.pdf) [cite: 56-63]
            todos_cpfs = re.findall(r'(\d{3}\.?\d{3}\.?\d{3}-?\d{2})', texto_completo)
            todos_cpfs = [re.sub(r'\D', '', c) for c in todos_cpfs]

            linhas = texto_completo.splitlines()

            # Caso 1: Nome e CPF na mesma linha (Padrão da maioria dos testes) [cite: 1, 41, 64, 67, 68]
            for linha in linhas:
                linha_limpa = linha.strip()
                if not linha_limpa: continue
                
                # Busca CPF na linha atual
                cpf_na_linha = re.search(r'(\d{3}\.?\d{3}\.?\d{3}-?\d{2})', linha_limpa)
                
                if cpf_na_linha:
                    cpf_bruto = cpf_na_linha.group(1)
                    cpf_limpo = re.sub(r'\D', '', cpf_bruto)
                    
                    # --- LIMPEZA PROFUNDA DO NOME ---
                    # Remove o CPF da string para isolar o nome
                    nome = linha_limpa.replace(cpf_bruto, "")
                    
                    # Remove etiquetas "Nome:", "CPF:" e variações 
                    nome = re.sub(r'(?i)\bNome:?\b|\bCPF:?\b', '', nome)
                    
                    # Remove todos os pontos (.) e dois-pontos (:) solicitados
                    nome = re.sub(r'[\.:]', '', nome)
                    
                    # Remove numeração de lista no início (ex: "1-", "2.", "9)") [cite: 41-45, 64-67]
                    nome = re.sub(r'^[\d\-\s)]+', '', nome)
                    
                    # Remove outros caracteres residuais e espaços extras
                    nome = re.sub(r'\s+', ' ', nome).strip().upper()
                    
                    if nome and len(cpf_limpo) == 11:
                        nomes_extraidos.append(nome)
                        cpfs_extraidos.append(cpf_limpo)

            # Caso 2: Processamento para listas em blocos separados (como no teste3.pdf) 
            if not nomes_extraidos:
                # Filtra linhas que não são CPFs e não são cabeçalhos
                potenciais_nomes = [l.strip().upper() for l in linhas if l.strip() and not re.search(r'(\d{11})|NOMES|CPFS', l, re.I)]
                
                # Remove pontuação residual dos nomes capturados em bloco
                potenciais_nomes = [re.sub(r'[\.:]', '', n).strip() for n in potenciais_nomes]
                
                if potenciais_nomes and len(todos_cpfs) == len(potenciais_nomes):
                    nomes_extraidos = potenciais_nomes
                    cpfs_extraidos = todos_cpfs

            # --- ATUALIZAÇÃO DOS CAMPOS DE TEXTO NA INTERFACE ---
            if nomes_extraidos:
                self.txt_nomes.delete("1.0", tk.END)
                self.txt_cpfs.delete("1.0", tk.END)
                self.txt_nomes.insert("1.0", "\n".join(nomes_extraidos))
                self.txt_cpfs.insert("1.0", "\n".join(cpfs_extraidos))
                messagebox.showinfo("Sucesso", f"{len(nomes_extraidos)} participantes importados!")
            else:
                messagebox.showwarning("Aviso", "Nenhum padrão de Nome/CPF reconhecido nos arquivos.")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar PDF: {e}")



    def iniciar_torneio(self):
        # --- NOVA VALIDAÇÃO DE CAMPOS ---
        self.clube = self.ent_clube.get().strip().upper()
        self.categoria = self.ent_cat.get().strip().upper()
        self.nome_prova = self.ent_prova.get().strip().upper()
        self.data_etapa = self.ent_data.get().strip()
        self.vitorias_md3 = {}

        if not self.clube or not self.categoria or not self.nome_prova:
            return messagebox.showwarning("Campos Obrigatórios", 
                "Por favor, preencha: Nome da Prova, Categoria e Clube antes de iniciar.")

        nomes = [n.strip().upper() for n in self.txt_nomes.get("1.0", tk.END).split('\n') if n.strip()]
        cpfs = [c.strip() for c in self.txt_cpfs.get("1.0", tk.END).split('\n') if c.strip()]
        
        if len(nomes) != len(cpfs):
            return messagebox.showerror("Erro", "Quantidade de nomes e CPFs não coincide.")
        if len(nomes) < 2: 
            return messagebox.showerror("Erro", "Mínimo 2 atletas.")

        # Restante dos dados da competição
        self.competidores_dados = {nomes[i]: cpfs[i] for i in range(len(nomes))}
        self.pontos_atleta_atual = {n: {"vitorias": 0, "bonus": 0} for n in nomes}
        self.participantes_originais = list(nomes)
        
         #     # --- LÓGICA DE EDITAL (POTÊNCIA DE 2) ---
        n = len(nomes)
        proxima_potencia = 2**math.floor(math.log2(n))
        num_lutas_ajuste = n - proxima_potencia

        if num_lutas_ajuste > 0:
            # Fase 1: Apenas os últimos atletas da lista lutam para 'ajustar' a chave
            # Ex: Se são 9, os atletas 8 e 9 lutam entre si.
            self.atletas_espera = nomes[:proxima_potencia - num_lutas_ajuste]
            self.chave = nomes[len(self.atletas_espera):]
            self.fase_n = 1
            self.rodada_ajuste = True
        else:
            # Já é potência de 2 (2, 4, 8, 16...)
            self.chave = nomes
            self.atletas_espera = []
            self.fase_n = 1
            self.rodada_ajuste = False

        self.gerar_fase_ui()

    

    def gerar_fase_ui(self):
        self.limpar_tela()
        
        # Inicializa lista de vencedores se for a primeira página da fase
        if self.pagina_atual == 0: 
            self.vencedores_fase = []
            # Reinicia o contador de MD3 apenas se estivermos entrando na final principal agora
            if len(self.chave) == 2 and not self.em_repescagem:
                self.vitorias_md3 = {}

        # --- DEFINIÇÃO DO TÍTULO DINÂMICO ---
        if len(self.chave) == 2 and not self.em_repescagem:
            titulo_texto = "GRANDE FINAL (MELHOR DE 3)"
            cor_titulo = "gold"
        else:
            titulo_texto = f"FASE {self.fase_n}" + (" (REPESCAGEM)" if self.em_repescagem else "")
            cor_titulo = self.accent

        tk.Label(self.root, text=titulo_texto, fg=cor_titulo, bg=self.bg,
                font=("Arial", 16, "bold")).pack(pady=5)

        # --- LÓGICA DE MONTAGEM DOS DUELOS ---
        chave_copia = list(self.chave)
        if len(chave_copia) % 2 != 0:
            chave_copia.append("W.O.")

        todos_duelos = []
        for i in range(0, len(chave_copia), 2):
            a, b = chave_copia[i:i+2]
            if a != "W.O." and b != "W.O.":
                todos_duelos.append([a, b])
            else:
                venc = a if b == "W.O." else b
                if venc != "W.O.":
                    self.vencedores_fase.append(venc)
                    self.pontos_atleta_atual[venc]["vitorias"] += 1

        # --- PAGINAÇÃO ---
        itens_por_pagina = 12
        total_paginas = math.ceil(len(todos_duelos) / itens_por_pagina)

        if total_paginas == 0:
            self.proxima_fase()
            return

        # --- NAVEGAÇÃO ---
        nav_frame = tk.Frame(self.root, bg=self.bg)
        nav_frame.pack(fill="x", pady=5)

        self.btn_next = tk.Button(
            nav_frame, bg="#28a745", fg="white",
            font=("Arial", 12, "bold"), height=1, width=20,
            relief="raised", state="disabled"
        )
        self.btn_next.pack(side="top", pady=2)

        tk.Label(nav_frame, text=f"Página {self.pagina_atual + 1} de {total_paginas}",
                fg="white", bg=self.bg, font=("Arial", 10)).pack()

        inicio = self.pagina_atual * itens_por_pagina
        fim = inicio + itens_por_pagina
        
        if fim < len(todos_duelos):
            self.btn_next.config(text="PRÓXIMA PÁGINA ➔", command=self.proxima_pagina)
        else:
            self.btn_next.config(text="FINALIZAR FASE ➔", command=self.proxima_fase)

        # --- ÁREA DE SCROLL E DUELOS ---
        container = tk.Frame(self.root, bg=self.bg)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=self.bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.bg)

        canvas_window = canvas.create_window((500, 0), window=scroll_frame, anchor="n")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.votos_pagina = 0
        duelos_pagina = todos_duelos[inicio:fim]
        self.duelos_reais_pagina = len(duelos_pagina)

        for a, b in duelos_pagina:
            f_duelo = tk.Frame(scroll_frame, bg=self.card, pady=8, padx=15)
            f_duelo.pack(pady=4, fill="x", padx=100)

            btn_params = {
                "width": 22, "height": 1, "font": ("Arial", 11, "bold"),
                "wraplength": 180, "cursor": "hand2"
            }

            tk.Button(
                f_duelo, text=a, **btn_params,
                command=lambda v=a, p=b, f=f_duelo: self.vencer_paginado(v, p, f)
            ).pack(side="left", expand=True)

            tk.Label(f_duelo, text="VS", fg=self.accent, bg=self.card,
                     font=("Arial", 10, "bold")).pack(side="left", padx=10)

            tk.Button(
                f_duelo, text=b, **btn_params,
                command=lambda v=b, p=a, f=f_duelo: self.vencer_paginado(v, p, f)
            ).pack(side="left", expand=True)

        if self.duelos_reais_pagina == 0:
            self.btn_next.config(state="normal")

    def vencer_paginado(self, vencedor, perdedor, frame):

        # ===== FINAL MELHOR DE 3 =====
        if len(self.chave) == 2 and not self.em_repescagem:

            if vencedor not in self.vitorias_md3:
                self.vitorias_md3[vencedor] = 0
            if perdedor not in self.vitorias_md3:
                self.vitorias_md3[perdedor] = 0

            self.vitorias_md3[vencedor] += 1

            placar_v = self.vitorias_md3[vencedor]
            placar_p = self.vitorias_md3[perdedor]

            messagebox.showinfo(
                "Final - Melhor de 3",
                f"{vencedor} venceu esta disputa!\n\n"
                f"PLACAR:\n{vencedor} {placar_v} x {placar_p} {perdedor}"
            )

            # ainda não terminou
            if placar_v < 2:
                # reativa botões para próxima disputa
                for b in frame.winfo_children():
                    if isinstance(b, tk.Button):
                        b.config(state="normal", bg="white")
                return

            # ===== CAMPEÃO DEFINIDO =====
            messagebox.showinfo(
                "CAMPEÃO!",
                f"{vencedor} venceu por {placar_v} x {placar_p}!"
            )

        # ===== LÓGICA NORMAL DO MATA-MATA =====
        for b in frame.winfo_children():
            if isinstance(b, tk.Button):
                b.config(state="disabled", bg="#333")

        if vencedor not in self.vencedores_fase:
            self.vencedores_fase.append(vencedor)
            self.pontos_atleta_atual[vencedor]["vitorias"] += 1

        tag = "Repescagem" if self.em_repescagem else f"Fase {self.fase_n}"
        self.historico_confrontos.append([tag, f"{vencedor} venceu {perdedor}"])

        if not self.em_repescagem:
            if len(self.chave) == 2:
                self.perdedor_final_principal = perdedor
            elif len(self.chave) > 2 and perdedor != "W.O.":
                self.perdedores_geral.append(perdedor)

        self.votos_pagina += 1

        if self.votos_pagina >= self.duelos_reais_pagina:
            self.btn_next.config(state="normal")


    def proxima_fase(self):
        self.pagina_atual = 0
        
        if self.rodada_ajuste:
            self.chave = self.atletas_espera + self.vencedores_fase
            self.rodada_ajuste = False
            self.fase_n += 1
            self.gerar_fase_ui()
            
        elif len(self.vencedores_fase) == 1:
            if not self.em_repescagem:
                self.campeao = self.vencedores_fase[0]
                self.iniciar_repescagem_completa()
            else:
                self.campeao_repescagem = self.vencedores_fase[0]
                self.disputa_final_vice()
        else:
            # Passa apenas os vencedores REAIS para a próxima chave
            self.chave = [v for v in self.vencedores_fase if v != "W.O."]
            self.fase_n += 1
            self.gerar_fase_ui()

    def proxima_fase(self):
        self.pagina_atual = 0
        
        if self.rodada_ajuste:
            # Fase de ajuste (quando não é potência de 2, ex: 9 ou 10 atletas)
            proxima_chave = self.atletas_espera + self.vencedores_fase
            self.chave = proxima_chave
            self.rodada_ajuste = False
            self.fase_n += 1
            self.gerar_fase_ui()
            
        elif len(self.vencedores_fase) == 1:
            # Determinou o vencedor da chave atual
            if not self.em_repescagem:
                self.campeao = self.vencedores_fase[0]
                self.iniciar_repescagem_completa()
            else:
                self.campeao_repescagem = self.vencedores_fase[0]
                self.disputa_final_vice()
        else:
            # Avança normal (Vencedores viram a nova chave)
            self.chave = list(self.vencedores_fase)
            self.fase_n += 1
            self.gerar_fase_ui()

    def registrar_vitoria_direta(self, venc):
        """Auxiliar para processar W.O. sem interface"""
        if venc != "W.O.":
            self.vencedores_fase.append(venc)
            self.pontos_atleta_atual[venc]["vitorias"] += 1
        self.votos_fase_total += 1 # Conta para o total da fase técnica

    def vencer_paginado(self, vencedor, perdedor, frame):
        """Versão modificada do 'vencer' para suportar páginas"""
        for b in frame.winfo_children():
            if isinstance(b, tk.Button): b.config(state="disabled", bg="#333")
            
        self.vencedores_fase.append(vencedor)
        self.pontos_atleta_atual[vencedor]["vitorias"] += 1
        
        tag = "Repescagem" if self.em_repescagem else f"Fase {self.fase_n}"
        self.historico_confrontos.append([tag, f"{vencedor} venceu {perdedor}"])
        
        # Lógica de perdedores
        if not self.em_repescagem:
            if len(self.chave) == 2: self.perdedor_final_principal = perdedor
            elif len(self.chave) > 2 and perdedor != "W.O.": self.perdedores_geral.append(perdedor)

        self.votos_pagina += 1
        if self.votos_pagina == self.duelos_reais_pagina:
            self.btn_next.config(state="normal")

    def proxima_pagina(self):
        self.pagina_atual += 1
        self.gerar_fase_ui()

    def vencer(self, vencedor, perdedor, frame):
        for b in frame.winfo_children():
            if isinstance(b, tk.Button): b.config(state="disabled", bg="#333")
        self.vencedores_fase.append(vencedor)
        self.pontos_atleta_atual[vencedor]["vitorias"] += 1
        tag = "Repescagem" if self.em_repescagem else f"Fase {self.fase_n}"
        self.historico_confrontos.append([tag, f"{vencedor} venceu {perdedor}"])
        if not self.em_repescagem:
            if len(self.chave) == 2:
                # Perdedor da final principal
                self.perdedor_final_principal = perdedor
            elif len(self.chave) > 2 and perdedor != "W.O.":
                # Só perde ANTES da semifinal
                self.perdedores_geral.append(perdedor)

        self.votos += 1
        if self.votos == len(self.chave)//2: self.btn_next.config(state="normal")

    def proxima_fase(self):
        # Resetar página para a nova fase/repescagem
        self.pagina_atual = 0
        
        if self.rodada_ajuste:
            # Une os vencedores da Fase 1 com os atletas que estavam esperando
            competidores_fase_2 = self.atletas_espera + self.vencedores_fase
            
            # Garante que a chave da Fase 2 tenha tamanho par (Potência de 2)
            tamanho_alvo = 2 ** math.ceil(math.log2(len(competidores_fase_2)))
            self.chave = competidores_fase_2 + (["W.O."] * (tamanho_alvo - len(competidores_fase_2)))
            
            self.rodada_ajuste = False
            self.fase_n += 1
            self.gerar_fase_ui()
            
        elif len(self.vencedores_fase) == 1:
            # Lógica de finalização (Campeão)
            if not self.em_repescagem:
                self.campeao = self.vencedores_fase[0]
                self.iniciar_repescagem_completa()
            else:
                self.campeao_repescagem = self.vencedores_fase[0]
                self.disputa_final_vice()
        else:
            # Avança para a próxima fase comum (Quartas -> Semi -> Final)
            vencedores_reais = [p for p in self.vencedores_fase if p != "W.O."]
            tamanho_alvo = 2 ** math.ceil(math.log2(len(vencedores_reais)))
            self.chave = vencedores_reais + (["W.O."] * (tamanho_alvo - len(vencedores_reais)))
            
            self.fase_n += 1
            self.gerar_fase_ui()


    def iniciar_repescagem_completa(self):
        self.em_repescagem = True; self.fase_n = 1
        self.chave_rep = [p for p in self.perdedores_geral if p != "W.O."]
        if not self.chave_rep:
            self.campeao_repescagem = "Nenhum"; self.disputa_final_vice()
            return
        tamanho = 2 ** math.ceil(math.log2(len(self.chave_rep)))
        self.chave = self.chave_rep + (["W.O."] * (tamanho - len(self.chave_rep)))
        self.gerar_fase_ui()

    def disputa_final_vice(self):
        self.limpar_tela()
        tk.Label(self.root, text="DISPUTA DE 2º E 3º LUGAR", fg="cyan", bg=self.bg, font=("Arial", 20, "bold")).pack(pady=20)
        a, b = self.perdedor_final_principal, self.campeao_repescagem
        if b == "Nenhum" or b == "W.O.":
            self.vice, self.terceiro = a, "---"
            self.finalizar_torneio()
            return
        frame = tk.Frame(self.root, bg=self.card, pady=20); frame.pack(pady=20)
        tk.Button(frame, text=f"{a}\n(Perdedor Principal)", width=35, height=3, command=lambda: self.set_vice_terceiro(a, b)).pack(side="left", padx=10)
        tk.Button(frame, text=f"{b}\n(Vencedor Repescagem)", width=35, height=3, command=lambda: self.set_vice_terceiro(b, a)).pack(side="left", padx=10)

    def set_vice_terceiro(self, v, t):
        self.vice, self.terceiro = v, t
        if self.campeao: self.pontos_atleta_atual[self.campeao]["bonus"] = 10
        if self.vice: self.pontos_atleta_atual[self.vice]["bonus"] = 8
        if self.terceiro != "---": self.pontos_atleta_atual[self.terceiro]["bonus"] = 6
        self.finalizar_torneio()


    def salvar_excel(self):
        # 1. Coletar dados para o nome dinâmico
        clube_clean = self.clube.strip().replace(" ", "_")
        prova_clean = self.nome_prova.strip().replace(" ", "_")
        categoria_clean = self.categoria.strip().replace(" ", "_")
        
        nome_dinamico = f"Ranking_{clube_clean}_{prova_clean}_{categoria_clean}.xlsx"
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        caminho_arquivo = os.path.join(desktop, nome_dinamico)

        # 3. Lógica de "Salvar ou Atualizar"
        if os.path.exists(caminho_arquivo):
            atualizar = messagebox.askyesno("Planilha Encontrada", f"Deseja ATUALIZAR os dados em '{nome_dinamico}'?")
            if not atualizar: return 
            modo = "a"
        else:
            modo = "w"

        data_coluna = self.data_etapa.strip()
        
        # --- 4. PREPARAÇÃO DOS DADOS COM A NOVA REGRA DE PONTOS ---
        dados_chave = []
        dados_etapa = []

        for atleta in self.participantes_originais:
            # vitorias = número de vezes que avançou de fase
            # Como ele participou da Fase 1, o mínimo de pontos de fase é 1
            vitorias = self.pontos_atleta_atual[atleta]["vitorias"]
            pontos_fase = vitorias + 1 # +1 porque a simples participação na Fase 1 vale 1 ponto
            
            bonus = self.pontos_atleta_atual[atleta]["bonus"]
            total_pontos = pontos_fase + bonus

            # Dados para a aba de detalhes (CHAVE)
            dados_chave.append({
                "ATLETA": atleta,
                "CPF": self.competidores_dados.get(atleta, ""),
                "PONTOS FASE": pontos_fase,
                "BÔNUS": bonus,
                "TOTAL ETAPA": total_pontos
            })

            # Dados para o RANKING GERAL
            dados_etapa.append({
                "NOME DO ATLETA": atleta,
                "CPF": self.competidores_dados.get(atleta, ""),
                data_coluna: total_pontos
            })

        df_chave = pd.DataFrame(dados_chave)
        df_etapa = pd.DataFrame(dados_etapa)
        nome_aba_chave = f"CHAVE_{data_coluna.replace('/', '-')}"

        # 5. Lógica de União de Rankings
        if modo == "a":
            try:
                df_rank = pd.read_excel(caminho_arquivo, sheet_name="RANKING_GERAL", skiprows=2)
            except Exception:
                df_rank = pd.DataFrame(columns=["NOME DO ATLETA", "CPF"])
        else:
            df_rank = pd.DataFrame(columns=["NOME DO ATLETA", "CPF"])

        # Limpeza de colunas calculadas antigas
        for col in ["PONTUAÇÃO FINAL", "CLASSIFICAÇÃO"]:
            if col in df_rank.columns: df_rank.drop(columns=col, inplace=True)
        
        if data_coluna not in df_rank.columns: df_rank[data_coluna] = 0

        # Atualiza ou Insere novos atletas
        for _, row in df_etapa.iterrows():
            mask = df_rank["NOME DO ATLETA"] == row["NOME DO ATLETA"]
            if mask.any():
                df_rank.loc[mask, data_coluna] = row[data_coluna]
            else:
                # Se o atleta não existia, cria linha com zeros e insere os pontos de hoje
                nova_linha = {c: 0 for c in df_rank.columns}
                nova_linha.update(row.to_dict())
                df_rank = pd.concat([df_rank, pd.DataFrame([nova_linha])], ignore_index=True)

        # Recalcular Totais Gerais do Ranking
        col_datas = [c for c in df_rank.columns if re.match(r"\d{2}/\d{2}/\d{4}", str(c))]
        df_rank["PONTUAÇÃO FINAL"] = df_rank[col_datas].sum(axis=1)
        df_rank = df_rank.sort_values("PONTUAÇÃO FINAL", ascending=False).reset_index(drop=True)
        df_rank["CLASSIFICAÇÃO"] = df_rank.index + 1

        # 6. Salvamento Final
        try:
            writer = pd.ExcelWriter(caminho_arquivo, engine="openpyxl", mode=modo, 
                                    if_sheet_exists="replace" if modo == "a" else None)
            with writer:
                df_rank.to_excel(writer, sheet_name="RANKING_GERAL", index=False, startrow=2)
                ws = writer.sheets["RANKING_GERAL"]
                ws["A1"] = f"RANKING DA MODALIDADE: {self.categoria}"
                ws["A2"] = f"NOME CLUBE: {self.clube}"
                df_chave.to_excel(writer, sheet_name=nome_aba_chave, index=False)
                
            messagebox.showinfo("Sucesso", f"Ranking atualizado!\nMínimo de 1 ponto atribuído por participação.")
        except Exception as e:
            messagebox.showerror("Erro", f"Feche o Excel antes de salvar!\nErro: {e}")


    def exportar_pdf(self):
        # Nome formatado: Relatorio_Categoria_Clube_Data
        nome_sugerido = f"Relatorio_{self.categoria}_{self.clube}_{self.data_etapa}.pdf"
        
        # Substituir caracteres que o Windows não aceita em nomes de arquivos (como "/")
        nome_sugerido = nome_sugerido.replace("/", "-") 

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=nome_sugerido
        )
        if not path: return

        doc = SimpleDocTemplate(path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        style_centro = ParagraphStyle(name='Centro', parent=styles['Normal'], alignment=1, spaceAfter=10)

        # ===== LOGO =====
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                img = RLImage(self.logo_path, width=70, height=70)
                img.hAlign = "CENTER"
                elements.append(img)
                elements.append(Spacer(1, 10))
            except: pass

        # ===== TÍTULO E SUBTÍTULO =====
        elements.append(Paragraph(f"<b>RELATÓRIO: {self.nome_prova}</b>", styles["Title"]))
        elements.append(Paragraph(f"<b>{self.clube}</b> | CATEGORIA: {self.categoria} | DATA: {self.data_etapa}", style_centro))
        elements.append(Spacer(1, 20))

        

        # ===== PÓDIO FINAL =====
        elements.append(Paragraph("<b>PÓDIO FINAL</b>", styles["Heading2"]))
        podio_data = [
            ["Posição", "Atleta", "CPF"],
            ["1º Lugar", self.campeao, self.competidores_dados.get(self.campeao, "")],
            ["2º Lugar", self.vice, self.competidores_dados.get(self.vice, "")],
            ["3º Lugar", self.terceiro, self.competidores_dados.get(self.terceiro, "")]
        ]
        t_podio = Table(podio_data, colWidths=[80, 200, 120])
        t_podio.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.black),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
        ]))
        elements.append(t_podio)
        elements.append(Spacer(1, 25))

        # --- A PARTE DA PONTUAÇÃO DETALHADA FOI REMOVIDA DAQUI ---

        # ===== HISTÓRICO DE CONFRONTOS =====
        elements.append(Paragraph("<b>HISTÓRICO DE CONFRONTOS</b>", styles["Heading2"]))
        elements.append(Spacer(1, 8))
        
        hist_data = [["Fase", "Resultado"]]
        for f, r in self.historico_confrontos:
            hist_data.append([f, r])

        t_hist = Table(hist_data, colWidths=[100, 340])
        t_hist.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(t_hist)

        # Gerar o PDF
        try:
            doc.build(elements)
            messagebox.showinfo("Sucesso", "Relatório PDF gerado (sem pontuação detalhada)!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")

    def finalizar_torneio(self):
        self.limpar_tela()
        tk.Label(self.root, text="RESULTADO DA ETAPA", fg="gold", bg=self.bg, font=("Arial", 26, "bold")).pack(pady=30)
        for p, c in [("🥇 1º", self.campeao), ("🥈 2º", self.vice), ("🥉 3º", self.terceiro)]:
            tk.Label(self.root, text=f"{p}: {c}", fg="white", bg=self.bg, font=("Arial", 18, "bold")).pack(pady=10)
        
        tk.Button(self.root, text="📥 ATUALIZAR RANKING EXCEL", bg="#1D6F42", fg="white", font=("Arial", 12, "bold"), width=35, command=self.salvar_excel).pack(pady=10)
        tk.Button(self.root, text="📄 GERAR RELATÓRIO PDF (NOMES + CPFs)", bg="#c4302b", fg="white", font=("Arial", 12, "bold"), width=35, command=self.exportar_pdf).pack(pady=5)
        tk.Button(self.root, text="🔄 NOVO TORNEIO", bg=self.accent, fg="white", width=35, command=self.setup_ui_inicial).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk(); app = TorneioApp(root); root.mainloop()