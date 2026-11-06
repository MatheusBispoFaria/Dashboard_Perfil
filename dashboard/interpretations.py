"""Leituras descritivas calculadas sobre a seleção e a base de referência."""

from dash import html

from .labels import EDUCATION, INCOME, OCCUPATION, SEX, decimal, integer, label
from .socioeconomic import occupation_summary, wilson_interval
from .statistics import CONFIDENCE_Z

SOURCE = "https://archive.ics.uci.edu/dataset/2/adult"


def table(headers, rows):
    return html.Div(className="analysis-table-scroll", children=html.Table([
        html.Thead(html.Tr([html.Th(value, scope="col") for value in headers])),
        html.Tbody([html.Tr([html.Td(value) for value in row]) for row in rows]),
    ], className="analysis-results-table"))


def paragraph(text):
    return html.P(text)


def base_findings(data):
    total = len(data)
    high = int(data["renda_alta"].sum())
    male = int(data["sex"].eq("Male").sum())
    female = int(data["sex"].eq("Female").sum())
    peak = data["age"].value_counts().idxmax()
    return [
        f"{integer(high)} de {integer(total)} pessoas ({decimal(high/total*100)}%) têm renda anual acima de US$ 50 mil. O restante está na faixa de até US$ 50 mil, incluindo esse limite.",
        f"A composição é de {integer(male)} registros masculinos ({decimal(male/total*100)}%) e {integer(female)} femininos ({decimal(female/total*100)}%). Essa diferença descreve a amostra; sozinha, não mede desigualdade de renda.",
        f"A idade mais frequente é {int(peak)} anos, com {integer(data['age'].eq(peak).sum())} registros. Há {integer(data['age'].eq(84).sum())} registros aos 84 anos e {integer(data['age'].eq(90).sum())} aos 90; a distribuição não chega a zero aos 84.",
        "Aos 86 anos há um registro com jornada de 40 h/semana; aos 87, um com 2 h/semana. Médias baseadas em grupos tão pequenos exigem uma leitura cuidadosa.",
    ]


def analysis_body(chart, selected, confidence="off", removed=0, before=0):
    body = [
        paragraph(f"Seleção atual: {integer(len(selected))} registros. {integer(removed)} registros excluídos pelo IQR entre os {integer(before)} que atendem aos outros filtros."),
        html.H3("Como ler o gráfico"),
    ]
    if selected.empty:
        body.append(paragraph("Nenhum registro atende à combinação atual. Amplie os filtros ou desmarque a exclusão de extremos para explorar a base completa."))
    elif chart == "graph-renda":
        n = len(selected)
        high = int(selected["renda_alta"].sum())
        body += [
            paragraph(f"Nesta seleção, {integer(high)} de {integer(n)} pessoas ({decimal(high/n*100)}%) estão acima de US$ 50 mil por ano; {integer(n-high)} ({decimal((n-high)/n*100)}%) estão na faixa de até US$ 50 mil."),
            paragraph("O denominador é o total de pessoas selecionadas. O gráfico não soma salários nem mostra a participação de cada grupo no dinheiro total. A fonte fornece duas faixas, sem o valor exato da renda de cada pessoa."),
            paragraph("Ao escolher somente a faixa acima de US$ 50 mil, ela passa a representar 100% da seleção por definição. Isso também afeta as comparações dos outros gráficos."),
        ]
        if confidence != "off":
            lo, hi = wilson_interval(high, n, CONFIDENCE_Z[confidence])
            body.append(paragraph(f"IC {confidence}% de Wilson da proporção acima de US$ 50 mil: {decimal(lo)}% a {decimal(hi)}%. Trata-se de uma aproximação amostral, sem os pesos populacionais da fonte original."))
    elif chart == "graph-genero":
        rows = []
        rates = {}
        for sex, title in SEX.items():
            group = selected[selected["sex"].eq(sex)]
            n = len(group)
            high = int(group["renda_alta"].sum())
            rates[sex] = high/n*100 if n else None
            rows.append([title, integer(n), f"{decimal(n/len(selected)*100)}%", integer(n-high), integer(high),
                         f"{decimal(high/n*100)}%" if n else "Sem registros"])
        body += [
            paragraph("A altura total de cada barra indica quantos registros pertencem ao grupo. As cores dividem esse total em duas faixas de renda. Passe o cursor para ver a porcentagem de cada faixa dentro do próprio grupo e a participação do grupo na seleção."),
            table(["Grupo", "Registros", "% da seleção", "Até US$ 50 mil", "Acima de US$ 50 mil", "Taxa acima de US$ 50 mil"], rows),
        ]
        if all(value is not None for value in rates.values()):
            difference = rates["Male"]-rates["Female"]
            body.append(paragraph(f"A taxa acima de US$ 50 mil no grupo masculino menos a do feminino é {decimal(difference)} pontos percentuais nesta seleção. Diferença de composição e diferença de taxa são medidas distintas."))
        body.append(paragraph("A fonte registra a variável sex com as categorias Male e Female. A interface as apresenta como masculino e feminino, sob o filtro de gênero; os dados não descrevem outras identidades de gênero."))
    elif chart == "graph-escolaridade":
        rows = []
        for education, group in selected.groupby("education", sort=False):
            high = int(group["renda_alta"].sum())
            rows.append([label(education, EDUCATION), integer(len(group)), integer(high), f"{decimal(high/len(group)*100)}%"])
        body += [
            paragraph("Cada barra mostra o número de registros de um nível de escolaridade, separado por faixa de renda. A ordenação acompanha os níveis da classificação original, com traduções aproximadas para o português."),
            table(["Escolaridade", "Registros", "Acima de US$ 50 mil", "Taxa dentro do nível"], rows),
            paragraph("Uma taxa alta significa que uma parcela maior daquele nível está acima de US$ 50 mil. Não significa que esse nível concentre a maior parte de todas as pessoas de renda alta. Compare taxas e tamanhos dos grupos; esta análise descritiva não estabelece que a escolaridade, isoladamente, cause maior renda."),
        ]
    elif chart == "graph-ocupacoes":
        summary = occupation_summary(selected)
        rows = [[label(row.occupation, OCCUPATION), integer(row.count), f"{decimal(row.mean_age)} anos"]
                for row in summary.itertuples()]
        body += [
            paragraph("São as dez ocupações com mais registros na seleção. O tamanho representa pessoas, e não salário médio. As cores permitem comparar as duas faixas de renda; o cursor também informa o código original da ocupação."),
            html.H3("Idade média nas ocupações mais frequentes"),
            table(["Ocupação", "Registros", "Idade média"], rows),
            paragraph("As três primeiras linhas respondem à pergunta sobre a idade média das três ocupações mais frequentes. O ranking e as médias acompanham os filtros. Ocupações não informadas ficam fora desse ranking, mas continuam na seleção e na tabela da base."),
        ]
    elif chart == "graph-idade-renda":
        counts = selected.groupby("age").size()
        peak = int(counts.idxmax())
        body += [
            paragraph("O eixo horizontal indica a idade e o vertical, a quantidade de registros. As áreas são empilhadas por faixa de renda: a espessura de cada cor corresponde àquela faixa, e a borda superior é o total das duas."),
            paragraph(f"A idade mais frequente na seleção atual é {peak} anos, com {integer(counts.loc[peak])} registros. As cores representam renda, conforme a legenda. O filtro de gênero permite examinar cada grupo separadamente."),
            paragraph("Idades sem observações recebem contagem zero. Uma queda na curva descreve menos registros daquela idade na amostra e não uma queda da renda individual."),
        ]
    elif chart == "graph-horas-idade":
        rows = []
        for income, group in selected.groupby("income"):
            rows.append([INCOME.get(income, income), integer(len(group)), f"{decimal(group['hours_per_week'].mean())} h/semana"])
        body += [
            paragraph("Cada ponto é a média de horas semanais das pessoas da mesma idade e faixa de renda. A legenda distingue as duas faixas. O cursor informa a média e o número de registros que a sustentam; círculos vazados indicam grupos com menos de cinco registros."),
            table(["Faixa de renda", "Registros", "Média da seleção"], rows),
            paragraph("As médias da tabela usam todos os registros de cada faixa, ponderados pela quantidade de pessoas; não são a média simples dos pontos por idade. As linhas comparam grupos de pessoas diferentes e não acompanham a mesma pessoa ao envelhecer."),
            paragraph("Oscilações nas idades mais altas podem depender de uma ou poucas observações. Quando o intervalo de confiança está ativado, as barras mostram uma aproximação normal da incerteza da média; não se calcula um intervalo para grupos com apenas um registro."),
        ]
    return html.Div(body, className="socio-analysis-copy")
