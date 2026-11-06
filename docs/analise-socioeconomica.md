# Análise socioeconômica

Fonte: [Adult (Census Income), UCI](https://archive.ics.uci.edu/dataset/2/adult),
Becker e Kohavi, publicação de 1996, extraída de dados de 1994.
O CSV adaptado contém 32.561 registros, 14 colunas e não possui o peso `fnlwgt`.
As contagens e proporções são da amostra, sem ponderação populacional.

## Recorte compartilhado

Renda, gênero (variável `sex` na fonte), vínculo, escolaridade, idade e jornada
afetam todos os seis gráficos, suas análises, a tabela e o CSV exportado.
Os nomes das categorias exibidas são traduzidos; os códigos originais usados
pelos filtros não foram alterados. O tooltip das ocupações mostra o código original.

O IQR vem desativado; também permanece desativado ao limpar os filtros. A regra de Tukey mantém observações dentro de
`[Q1 − 1,5 × IQR, Q3 + 1,5 × IQR]`, com `IQR = Q3 − Q1`.
Os limites são calculados na base completa, antes dos filtros, para manter
comparabilidade entre recortes: idade de −2 a 78 anos e jornada de 32,5 a 52,5 h.
É necessário atender aos limites das duas variáveis.
Uma variável com IQR zero não sofre exclusão por essa regra.

Quando ativado sem outros filtros, 23.499 registros são mantidos e 9.062 excluídos. A interface
informa o efeito e permite desativá-lo. Jornadas parciais e extensas legítimas
podem ser excluídas; este filtro não é uma correção de erros nem uma garantia
de representatividade. Ganhos e perdas de capital não entram nessa regra.

Referência: [NIST, box plots com limites](https://www.itl.nist.gov/div898/handbook/eda/section3/boxplot.htm).

## Visualizações e denominadores

- Renda: proporção de pessoas em cada faixa anual, sem somar valores monetários.
- Gênero e renda: contagens empilhadas; no tooltip, taxas dentro do grupo e
  participação do grupo na seleção são medidas separadas.
- Escolaridade: contagens em todos os níveis, separadas por renda. A análise
  detalhada mostra taxas internas, sem inferir causalidade.
- Ocupações: dez categorias mais frequentes entre as ocupações informadas.
  A análise detalhada apresenta contagem e idade média, incluindo as três líderes.
- Idade e renda: contagens empilhadas com legenda explícita e zeros em idades
  sem observações dentro do intervalo observado.
- Jornada: média por idade e faixa de renda, contagem no tooltip e marcador
  vazado para grupos com menos de cinco registros. Idades ausentes interrompem
  a linha. As médias da seleção são ponderadas pelos registros, não pelos pontos.

O IC opcional da renda e dos grupos utiliza Wilson para proporções.
Na jornada, o IC é uma aproximação normal `z × desvio / sqrt(n)` e só aparece
para grupos com pelo menos dois registros. Os gráficos não estimam causalidade
nem probabilidades de risco bancário.

## Referência sem filtros

As leituras gerais ficam apenas no painel Sobre a base, e não são repetidas nos
pop-outs. Elas usam os 32.561 registros sem IQR:
24.720 na faixa até US$ 50 mil e 7.841 acima desse valor (24,1%);
21.790 registros masculinos e 10.771 femininos.
Há um registro aos 86 anos (40 h/semana), um aos 87 (2 h/semana),
dez aos 84 e 43 aos 90. O pico etário é de 898 registros aos 36 anos.
Esses números não devem ser confundidos com a seleção corrente.

## Consulta e exportação

A tabela tem paginação e ordenação no servidor. A busca literal atua apenas
na tabela, sobre os rótulos exibidos. O botão CSV exporta todos os registros
encontrados na busca após os filtros globais e o IQR, com a ordenação escolhida,
em UTF-8 com BOM e separador ponto e vírgula. `Registro` identifica a linha
do CSV original. A base de origem não é sobrescrita.

## Painéis da interface

Os botões Filtros e Sobre a base expandem painéis recolhidos inicialmente.
Abrir um recolhe o outro sem recriar os controles ou apagar a seleção.
A explicação da regra IQR fica em um card acessível por hover e foco no termo
sublinhado; no toque, o botão pode receber foco. O título inferior da consulta
é Consultar Base de Dados.
