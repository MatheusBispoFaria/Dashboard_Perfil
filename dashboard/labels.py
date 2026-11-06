"""Rótulos em português sem alterar os códigos originais do Adult."""

INCOME = {"<=50K": "Até US$ 50 mil/ano", ">50K": "Acima de US$ 50 mil/ano"}
SEX = {"Male": "Masculino", "Female": "Feminino"}
OCCUPATION = {
    "Prof-specialty": "Profissões especializadas",
    "Craft-repair": "Ofícios e reparos",
    "Exec-managerial": "Gestão e direção",
    "Adm-clerical": "Apoio administrativo",
    "Sales": "Vendas", "Other-service": "Outros serviços",
    "Machine-op-inspct": "Operação e inspeção de máquinas",
    "Transport-moving": "Transporte e movimentação",
    "Handlers-cleaners": "Manuseio de materiais e limpeza",
    "Farming-fishing": "Agropecuária e pesca",
    "Tech-support": "Suporte técnico",
    "Protective-serv": "Segurança e proteção",
    "Priv-house-serv": "Serviços domésticos", "Armed-Forces": "Forças Armadas",
}
EDUCATION = {
    "Preschool": "Pré-escola", "1st-4th": "1º ao 4º ano", "5th-6th": "5º ao 6º ano",
    "7th-8th": "7º ao 8º ano", "9th": "9º ano", "10th": "10º ano",
    "11th": "11º ano", "12th": "12º ano",
    "HS-grad": "Ensino médio completo", "Some-college": "Superior incompleto",
    "Assoc-voc": "Superior de 2 anos (profissional)",
    "Assoc-acdm": "Superior de 2 anos (acadêmico)",
    "Bachelors": "Bacharelado", "Masters": "Mestrado",
    "Prof-school": "Formação profissional superior", "Doctorate": "Doutorado",
}
EDUCATION_ORDER = tuple(EDUCATION)
WORKCLASS = {
    "Private": "Setor privado", "Self-emp-not-inc": "Autônomo sem empresa constituída",
    "Self-emp-inc": "Autônomo com empresa constituída", "Federal-gov": "Governo federal",
    "Local-gov": "Governo local", "State-gov": "Governo estadual",
    "Without-pay": "Sem remuneração", "Never-worked": "Nunca trabalhou",
}

def label(value, mapping):
    return "Não informado" if str(value) in {"nan", "N/A", "?", "", "None"} else mapping.get(value, str(value))


def integer(value):
    return f"{int(value):,}".replace(",", ".")


def decimal(value, digits=1):
    return f"{value:.{digits}f}".replace(".", ",")
