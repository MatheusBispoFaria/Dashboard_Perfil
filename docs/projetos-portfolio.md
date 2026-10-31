# Projetos incorporados ao portfólio

## Organização

- **Entrada:** apresentação escura com Matheus em destaque e uma seta que revela
  Análises de Dados, Quem sou Eu, Skills e Projetos. O nome no cabeçalho permite
  retornar à entrada, recolhendo novamente o menu.
- **Renda e perfil socioeconômico:** análise do Census Income Dataset, com
  indicadores de renda, escolaridade, idade, gênero, ocupação e jornada de trabalho.
- **Qualificações, dentro de Quem sou Eu:** Compiler-AI em destaque como projeto de desenvolvimento para
  a TOTVS nas sprints de 2026; Site Passa Bola como experiência em equipe de 2025;
  SkillHub como segundo TCC semestral, com o tema Futuro do Trabalho.
- **Projetos:** apresentações de Compiler-AI, Site Passa Bola, SkillHub e FIAP Bank.
  Compiler-AI é o nome informado pelo autor para o projeto da pasta
  IA-Transcription-v4-contexto, anteriormente apresentado como IA-Transcription /
  CHEFON AI. FIAP Bank identifica o conteúdo do arquivo RM562140.
- **Despesas Públicas · ES (CP5):** dashboard interativo das despesas públicas do Espírito
  Santo, independente dos filtros e gráficos do Census Income Dataset.

As análises são alternadas por abas dentro de Análises de Dados. A navegação
principal apresenta quatro opções, com Projetos após Skills. As páginas internas
mantêm o gradiente diagonal de branco a cinza. Os projetos começam resumidos e
abrem seus detalhes em cartões expansíveis, preservando os relatos e links.

As descrições técnicas foram elaboradas a partir dos arquivos fornecidos.
Os relatos pessoais, o contexto dos projetos, os períodos das sprints e a relação
com a TOTVS e a Passa Bola foram informados pelo autor do portfólio. Não foram
acrescentados cargo, vínculo empregatício, resultados quantitativos ou atribuições
individuais não informadas. A necessidade de organizar informações sobre ingressos
é apresentada como contexto do projeto Passa Bola, sem afirmar a implementação
de uma plataforma de vendas.

Os relatos pessoais ficam no campo `experience` de cada projeto em
`dashboard/content.py`. Enquanto estiverem como `None`, a interface apresenta
“Relato da experiência em preparação.” Os relatos de Compiler-AI, Site Passa Bola
e SkillHub já foram preenchidos. O mesmo conteúdo alimenta Projetos e Qualificações,
evitando versões divergentes.

O campo `role` resume a participação individual antes dos detalhes técnicos.
Passa Bola e SkillHub foram planejados pelo grupo Novus Capital, com três integrantes, com
visão inicial no Figma e responsabilidades definidas. O autor informou ter sido
o principal responsável pela implementação técnica de ambos. No Compiler-AI,
sua participação ocorreu no grupo Chefon Ai, formado por cinco integrantes,
e abrangeu concepção, dashboard, documentação, avaliação e revisão dos resultados
e ampliação das informações da solução em colaboração com a equipe.
No relato do SkillHub, o backend e a revisão de código aparecem como os principais
exemplos de consolidação dos conhecimentos teóricos e técnicos.

`AI_APPROACH` reúne o texto sobre desenvolvimento assistido por IA, exibido em
Quem Sou Eu e Projetos. O texto descreve a definição da solução, a elaboração
de prompts e a avaliação e correção da implementação. As habilidades correspondentes
também constam em Skills.

O primeiro TCC ainda não foi incorporado; o autor informou que enviará o material
posteriormente.

## Dados do CP5

O dashboard reutiliza os cálculos de `src/analytics.py` e `src/charts.py` do
projeto original. O tratamento da fonte foi preservado em
`scripts/cp5_data_preparation.py`.

As oito partes de 2024 e 2025 totalizam 1.092.158 registros na base integral.
O recorte temático contém 62.590 registros de Urbanismo, Transporte, Habitação,
Saneamento e Gestão Ambiental. Não há amostragem desse recorte.

O conjunto preparado fica em `data/despesas_es/despesas_es_2024_2025.csv.gz`, com cerca
de 1 MB. `data/despesas_es/proveniencia.json` registra a origem, os arquivos, o hash do
ZIP, a auditoria e a reconstrução dos rótulos de 2025 pelos códigos de 2024.
Movimentos negativos são preservados. Nenhum índice Pago/Empenho é apresentado
como taxa contábil de execução.

O portfólio carrega o conjunto preparado quando a aba do CP5 é utilizada. A
tabela envia apenas a página consultada ao navegador. Os arquivos brutos não
são necessários durante a execução do dashboard.

Para reconstruir o conjunto a partir do arquivo fornecido:

```powershell
python scripts/prepare_cp5_data.py "C:\caminho\cp5_datascience.zip"
```

O script lê apenas as oito partes esperadas dentro do ZIP e não executa
aplicações contidas no arquivo.

## Material dos demais projetos

Os cartões de Projetos e Qualificações exibem os acessos fornecidos pelo autor:

| Projeto | Demonstração | Código |
| --- | --- | --- |
| Compiler-AI | [Abrir no Render](https://compiler-vzs3.onrender.com) | [GitHub](https://github.com/MatheusBispoFaria/compiler) |
| SkillHub | — | [GitHub](https://github.com/novusscapital/SkillHub_GS25) |
| Site Passa Bola | — | [GitHub](https://github.com/novusscapital/Sprint-Passa-Bola) |
| FIAP Bank | — | [GitHub](https://github.com/MatheusBispoFaria/fiap-cp5-ddd-java) |

Os endereços ficam nos campos `demo_url` e `github_url` em
`dashboard/content.py`. Os botões abrem uma nova aba e reutilizam o mesmo
componente nas duas seções do portfólio.

O portfólio contém a apresentação dos projetos de software. Não depende da
execução dos backends Flask, Node ou Java, nem copia bases de reuniões,
transcrições, chaves de API ou contas demonstrativas dos projetos originais.
As pastas de origem permanecem independentes do dashboard.
