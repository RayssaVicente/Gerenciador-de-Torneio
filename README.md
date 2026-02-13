# 🏆 Gerenciador de Torneio - Ranking Oficial

![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![UI](https://img.shields.io/badge/UI-Tkinter-orange.svg)

Uma solução completa para organização de competições esportivas, automatizando desde a entrada de dados via PDF até a gestão de chaves e rankings acumulados.

## 🚀 Funcionalidades

* **Importação Inteligente**: Extração de nomes e CPFs diretamente de arquivos PDF via Regex.
* **Gestão de Chaves**: Lógica automática para chaves baseadas em potência de 2, incluindo rodadas de ajuste.
* **Sistema de Repescagem**: Fluxo completo para definição de 2º e 3º lugares.
* **Interface Adaptável**: Sistema de paginação para suportar torneios com grandes números de atletas.
* **Exportação de Dados**:
    * **Excel**: Ranking acumulado que reconhece atletas antigos e soma pontuações automaticamente.
    * **PDF**: Relatórios oficiais com pódio, histórico de confrontos e logomarca personalizada.

## 📊 Regras de Pontuação

| Categoria | Pontuação |
| :--- | :--- |
| **Participação** | 1 Ponto base |
| **Vitória por Fase** | +1 Ponto |
| **1º Lugar (🥇)** | +10 Pontos bônus |
| **2º Lugar (🥈)** | +8 Pontos bônus |
| **3º Lugar (🥉)** | +6 Pontos bônus |

## 🛠️ Tecnologias Utilizadas

* [Python](https://www.python.org/) - Linguagem base.
* [Pandas](https://pandas.pydata.org/) - Manipulação de dados e Excel.
* [ReportLab](https://www.reportlab.com/) - Geração de PDFs.
* [PyPDF2](https://pypdf2.readthedocs.io/) - Leitura de arquivos PDF.
* [Tkinter](https://docs.python.org/3/library/tkinter.html) - Interface gráfica (GUI).

## 📦 Como Instalar e Rodar

1. **Clone o repositório**:
   git clone https://github.com/RayssaVicente/Gerenciador-de-Torneio.git
2. **Entre no diretório do projeto:**
    cd nome-do-repositorio
3. **Instale as dependências:**
   pip install pandas openpyxl PyPDF2 reportlab
4. **Execute a aplicação:**
      python geradorTorneio4-ultima-alteracao.py

## Desenvolvedora

Rayssa Vicente da Silva Viegas

* [LinkedIn]: (https://www.linkedin.com/in/rayssa-vicente-viegas-0b3027201/)

E-mail: rayssavicenteviegas@gmail.com

Portfólio: Desenvolvedora de Software
