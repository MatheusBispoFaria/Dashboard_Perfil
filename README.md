# Dashboard Profissional

Dashboard em Python com Dash, Plotly e Bootstrap. Reúne o portfólio profissional
e a análise interativa do Census Income Dataset, com filtros de renda, vínculo,
escolaridade, idade e jornada de trabalho, além de intervalos de confiança.

## Estrutura

```text
dashboardprofissional/
├── app.py                      # Entrada local e servidor para publicação
├── requirements.txt            # Dependências da aplicação
├── README.md
├── .gitignore
├── assets/                     # Arquivos servidos automaticamente pelo Dash
│   ├── profile.jpg
│   └── style.css
├── data/
│   └── adult_clean.csv          # Base utilizada pelo dashboard
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
│   └── layouts/
│       ├── __init__.py
│       ├── shell.py             # Estrutura principal e menu lateral
│       ├── filters.py           # Controles dos filtros
│       ├── analysis.py          # Tela de análise e resumo de escolaridade
│       └── profile.py           # Apresentação, qualificações e skills
└── tests/
    └── test_dashboard.py        # Verificação dos dados e das interações
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
- **Menu e estrutura principal:** `dashboard/config.py` e `dashboard/layouts/shell.py`.
- **Estilos da interface:** `assets/style.css`.
- **Cores e estilos dos gráficos:** `dashboard/theme.py`.
- **Gráficos e cálculos:** `dashboard/charts.py` e `dashboard/statistics.py`.
- **Filtros:** `dashboard/layouts/filters.py`, `dashboard/data.py` e `dashboard/callbacks.py`.
- **Base de dados:** `data/adult_clean.csv`, mantendo as colunas esperadas por `load_dataset`.

A planilha em `docs/` é um material de apoio e não é carregada pela aplicação.
Cada instância criada por `create_app()` tem seus próprios dados e callbacks.

## Verificações

Os testes usam `unittest`, incluído no Python, e as dependências da aplicação:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Eles verificam preparação e filtros dos dados, intervalos de confiança, respostas
do servidor, navegação, atualização dos gráficos e seleções sem resultados.
