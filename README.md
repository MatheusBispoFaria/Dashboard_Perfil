# Dashboard Profissional

Dashboard em Python com Dash, Plotly e Bootstrap. Reúne o portfólio profissional
e a análise interativa do Census Income Dataset, com filtros de renda, vínculo,
escolaridade, idade e jornada de trabalho, além de intervalos de confiança.
Inclui também uma aba interativa do CP5 de Data Science e a apresentação de
projetos e experiências de desenvolvimento.

## Estrutura

```text
dashboardprofissional/
├── app.py                      # Entrada local e servidor para publicação
├── requirements.txt            # Dependências da aplicação
├── README.md
├── .gitignore
├── assets/                     # Arquivos servidos automaticamente pelo Dash
│   ├── profile.png
│   ├── chrome-ribbon.svg         # Elemento decorativo da entrada
│   └── style.css
├── data/
│   ├── adult_clean.csv          # Base utilizada pelo dashboard
│   └── despesas_es/            # Recorte de despesas e auditoria de origem
├── docs/
│   └── analise_dataset_adult.xlsx # Planilha de apoio à análise
├── dashboard/
│   ├── __init__.py              # Exporta create_app
│   ├── application.py           # Cria e configura a aplicação
│   ├── config.py                # Caminhos e itens de navegação
│   ├── data.py                  # Leitura, preparação e filtros dos dados
│   ├── statistics.py            # Cálculos dos intervalos de confiança
│   ├── theme.py                 # Paleta e estilo dos gráficos
│   ├── charts.py                # Construção dos gráficos
│   ├── callbacks.py             # Navegação e atualização da tela
│   ├── content.py               # Projetos e relatos pessoais
│   ├── cp5/                     # Dados, cálculos, gráficos e interface do CP5
│   └── layouts/
│       ├── __init__.py
│       ├── shell.py             # Cabeçalho, navegação no topo e janela de análise
│       ├── cards.py             # Cartões dos gráficos e botões de análise
│       ├── filters.py           # Controles dos filtros
│       ├── analysis.py          # Tela de análise e resumo de escolaridade
│       ├── projects.py          # Apresentação dos projetos e experiências
│       └── profile.py           # Apresentação, qualificações e skills
├── scripts/                     # Reprodução da preparação dos dados do CP5
└── tests/                       # Verificação do dashboard e da integração CP5
```

## Executar localmente

Use Python 3.10 ou superior. A reorganização foi validada com Python 3.13.
No terminal, dentro desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Acesse <http://127.0.0.1:8050>. A execução local mantém o modo de depuração.
Os caminhos dos dados e de `assets/` são resolvidos a partir da pasta do projeto.

## Publicação

A entrada usada por serviços como o Render continua sendo `app:server`.
Em um ambiente que suporte Gunicorn, execute a partir da pasta do projeto:

```sh
gunicorn app:server
```

## Onde fazer alterações

- **Conteúdo do portfólio:** `dashboard/layouts/profile.py`.
- **Projetos e relatos das experiências:** `dashboard/content.py`.
- **Dashboard Despesas Públicas · ES (CP5):** `dashboard/cp5/`.
- **Menu no topo e estrutura principal:** `dashboard/config.py` e `dashboard/layouts/shell.py`.
- **Cartões e títulos das análises:** `dashboard/layouts/cards.py`.
- **Estilos da interface:** `assets/style.css`.
- **Cores e estilos dos gráficos:** `dashboard/theme.py`.
- **Gráficos e cálculos:** `dashboard/charts.py` e `dashboard/statistics.py`.
- **Filtros:** `dashboard/layouts/filters.py`, `dashboard/data.py` e `dashboard/callbacks.py`.
- **Base de dados:** `data/adult_clean.csv`, mantendo as colunas esperadas por `load_dataset`.

A planilha em `docs/` é um material de apoio e não é carregada pela aplicação.
Cada instância criada por `create_app()` tem seus próprios dados e callbacks.

## Interface

A abertura exibe **Matheus** em uma página de apresentação escura, com tipografia
grande e um elemento metálico. A seta abaixo do nome revela quatro opções:
**Análises de Dados**, **Quem sou Eu**, **Skills** e **Projetos**. O nome no
cabeçalho retorna à entrada e recolhe o menu.

O dashboard utiliza a largura disponível, com cartões arredondados e uma paleta
em azul, turquesa e tons neutros, sobre um gradiente diagonal de branco e cinza.
Os cartões se reorganizam em telas menores.
As análises **Renda e perfil socioeconômico** e **Despesas Públicas · ES** são
alternadas dentro de **Análises de Dados**, mantendo os filtros de cada dashboard
independentes. **Formação e qualificações** permanece acessível em um bloco
expansível de **Quem sou Eu**.

Cada um dos oito gráficos e o resumo de escolaridade têm um botão de seta (↗)
que abre uma janela com o título correspondente. O corpo da janela está vazio,
reservado para a futura análise dos dados. Ela fecha pelo botão de fechar,
pela tecla Escape ou ao clicar fora.

Os seis filtros continuam disponíveis. O botão **Limpar filtros** restaura a
seleção inicial e a contagem de registros acompanha a seleção atual.

## Projetos e experiências

A aba **Projetos** apresenta Compiler-AI (TOTVS), Site Passa Bola, SkillHub e
FIAP Bank. Em **Qualificações**, Compiler-AI tem destaque pelas sprints de 2026
para a TOTVS; Site Passa Bola aparece como experiência de 2025, e SkillHub como
o segundo TCC semestral, com o tema Futuro do Trabalho. Os relatos pessoais
ficam em `dashboard/content.py` e são compartilhados entre as duas seções.

Em Projetos, todos os cartões começam recolhidos. Ao selecionar um projeto,
o cartão se expande com descrição, participação, tecnologias, links e relato.
Os grupos são identificados como **Chefon Ai, com cinco integrantes**, no
Compiler-AI, e **Novus Capital, com três integrantes**, em Passa Bola e SkillHub.

**Quem Sou Eu** e **Projetos** também apresentam a abordagem de desenvolvimento
assistido por IA: compreensão do problema, estruturação da solução, elaboração
de prompts e avaliação e correção do código gerado. As competências correspondentes
aparecem em **Skills**.

A aba **Despesas Públicas · ES** reúne os dados de despesas do Espírito Santo de
2024 e 2025, com filtros próprios, indicadores, oito gráficos, estatísticas e
consulta paginada aos registros. Requer NumPy e SciPy, incluídos nas dependências.
Consulte `docs/projetos-portfolio.md` para a origem e a preparação dos dados.

## Verificações

Os testes usam `unittest`, incluído no Python, e as dependências da aplicação:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Eles verificam preparação e filtros dos dados, intervalos de confiança, respostas
do servidor, navegação recolhida, atualização dos gráficos, seleções sem
resultados, limpeza dos filtros e abertura das janelas de análise.
