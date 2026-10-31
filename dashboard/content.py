"""Projetos, relatos pessoais e abordagem de desenvolvimento do portfólio."""

AI_APPROACH = (
    "Gosto de criar soluções para problemas concretos. Em boa parte dos meus projetos, "
    "utilizo a inteligência artificial para apoiar a implementação das ideias: começo "
    "por compreender o que quero construir, estruturo a solução e traduzo essa visão "
    "em instruções e prompts claros para orientar a geração de código.",
    "Minha base técnica me permite avaliar o que foi gerado, identificar problemas, "
    "corrigir a implementação e refinar os prompts. Esse processo faz parte do meu "
    "aprendizado contínuo: evoluo meus conhecimentos enquanto amplio minha capacidade "
    "de transformar ideias em aplicações funcionais.",
)

PROJECTS = (
    {
        "slug": "ia-transcription",
        "name": "Compiler-AI",
        "team": "Chefon Ai",
        "team_size": 5,
        "demo_url": "https://compiler-vzs3.onrender.com",
        "github_url": "https://github.com/MatheusBispoFaria/compiler",
        "category": "TOTVS · Projeto de desenvolvimento · Sprints de 2026",
        "headline": "Transcrições de reuniões transformadas em inteligência de negócio.",
        "summary": (
            "Solução desenvolvida nas sprints de 2026 a partir de uma necessidade "
            "apresentada pela TOTVS: organizar o volume de transcrições de reuniões "
            "do Microsoft Teams em resumos úteis, sinais de negócio e sugestões de ação."
        ),
        "features": (
            "Leitura contextual de churn, satisfação, upsell, cross-sell, concorrência e urgência.",
            "Evidências da transcrição para apoiar a interpretação dos sinais.",
            "Resumos executivos com integração à OpenAI e alternativa de resumo local.",
            "Sugestões de ação e informações organizadas em um dashboard, com histórico em SQLite.",
        ),
        "technologies": ("Python", "Flask", "React", "SQLite", "OpenAI"),
        "icon": "fa-wave-square",
        "featured": True,
        "role": "Participação na concepção da solução, no dashboard, na documentação e na revisão das análises.",
        "experience": (
            "Durante as sprints de 2026, participei da concepção do Compiler-AI "
            "no grupo Chefon Ai, formado por cinco integrantes. O projeto foi "
            "construído a partir de uma necessidade apresentada pela TOTVS: "
            "transformar transcrições de reuniões do Microsoft Teams em resumos úteis, "
            "informações estruturadas e sinais relevantes para o negócio.\n\n"
            "Contribuí para definir como a solução funcionaria, participei da construção "
            "do dashboard e da documentação do projeto. Também fiquei encarregado de "
            "avaliar e revisar os resultados. Em colaboração com o grupo, "
            "trabalhei na ampliação das informações fornecidas à solução para apoiar "
            "a identificação de riscos de cancelamento, oportunidades de upsell e "
            "cross-sell e sugestões de ação.\n\n"
            "Essa experiência me aproximou dos fundamentos de aplicações de "
            "inteligência artificial e da importância de revisar suas respostas. "
            "Também fortaleceu minha colaboração em equipe e minha capacidade de "
            "relacionar uma necessidade de negócio à construção de uma solução prática."
        ),
    },
    {
        "slug": "passa-bola",
        "name": "Site Passa Bola",
        "team": "Novus Capital",
        "team_size": 3,
        "github_url": "https://github.com/novusscapital/Sprint-Passa-Bola",
        "category": "Passa Bola · Desenvolvimento em equipe · Sprints de 2025",
        "headline": "Tecnologia e visibilidade para o futebol feminino.",
        "summary": (
            "Portal dedicado ao futebol feminino, desenvolvido nas sprints de 2025. "
            "A proposta reuniu um portal de notícias e um espaço para a Copa Passa Bola, "
            "principal produto da empresa, para organizar sua presença digital."
        ),
        "features": (
            "Portal de notícias e espaço dedicado à Copa Passa Bola e ao futebol feminino.",
            "Componentes reutilizáveis e rotas com React Router.",
            "Protótipo de backend Express para o fluxo de login.",
        ),
        "technologies": ("React", "JavaScript", "Node.js", "Express", "Tailwind CSS", "Vite"),
        "icon": "fa-futbol",
        "featured": False,
        "role": "Principal responsável pela implementação técnica em uma equipe de três integrantes.",
        "experience": (
            "Nas sprints de 2025, participei da criação de um portal para a Passa Bola, "
            "voltado ao futebol feminino. O projeto nasceu da necessidade de reunir "
            "notícias e organizar a presença digital da Copa Passa Bola, principal "
            "produto da empresa, incluindo um espaço dedicado à competição e às "
            "informações sobre ingressos.\n\n"
            "No grupo Novus Capital, formado por três integrantes, definimos responsabilidades claras, "
            "construímos a visão do projeto no Figma e discutimos funcionalidades, "
            "regras e lógica da aplicação. A partir desse planejamento coletivo, "
            "assumi a principal responsabilidade pela implementação técnica do "
            "projeto, com a interface desenvolvida em React e JavaScript.\n\n"
            "O projeto me ensinou a transformar uma visão construída em equipe em "
            "uma aplicação funcional, organizar um plano de desenvolvimento e "
            "conectar as decisões técnicas às necessidades apresentadas pela empresa."
        ),
    },
    {
        "slug": "skillhub",
        "name": "SkillHub",
        "team": "Novus Capital",
        "team_size": 3,
        "github_url": "https://github.com/novusscapital/SkillHub_GS25",
        "category": "TCC 2 · Tema: Futuro do Trabalho",
        "headline": "Conexões profissionais em uma plataforma inspirada no LinkedIn.",
        "summary": (
            "Plataforma acadêmica de conexão profissional desenvolvida para o TCC "
            "semestral sobre o Futuro do Trabalho. Reúne perfis de profissionais, "
            "busca por competências e interação entre usuários."
        ),
        "features": (
            "Listagem e visualização de perfis profissionais com competências e informações de atuação.",
            "Busca por nome e filtros por área, cidade e tecnologia.",
            "Interação por chat e fluxos de cadastro, login e edição de perfil.",
            "Interface em React integrada a um backend Node.js e Express, com dados locais em JSON.",
        ),
        "technologies": ("React", "JavaScript", "Node.js", "Express", "Tailwind CSS", "Vite"),
        "icon": "fa-people-group",
        "featured": False,
        "role": "Principal responsável pela implementação técnica, com destaque para o backend, em uma equipe de três integrantes.",
        "experience": (
            "No segundo TCC semestral, com o tema Futuro do Trabalho, desenvolvi "
            "o SkillHub no grupo Novus Capital, formado por três integrantes. Inspirada no LinkedIn, "
            "a plataforma reunia perfis profissionais, busca por competências "
            "e interação entre usuários.\n\n"
            "Construímos a visão do projeto no Figma, discutimos as funcionalidades "
            "e organizamos as responsabilidades. Fiquei como principal responsável "
            "pela implementação técnica da aplicação, a partir das ideias e decisões "
            "construídas em conjunto.\n\n"
            "O backend foi a parte que mais consolidou meus conhecimentos: trabalhei "
            "nos fluxos de cadastro e autenticação, na lógica de senhas, no acesso "
            "aos perfis e no envio e recebimento de mensagens. Um dos principais "
            "desafios foi revisar um código que se tornava mais complexo. Ao longo "
            "do desenvolvimento, aprofundei minha compreensão da implementação "
            "e do fluxo de trabalho entre o VS Code, o GitHub e a aplicação web.\n\n"
            "Nesse projeto, consegui conectar os conhecimentos teóricos à prática "
            "técnica. Essa evolução me permitiu compreender melhor o código, "
            "revisá-lo e desenvolver com mais clareza e autonomia."
        ),
    },
    {
        "slug": "fiap-bank",
        "name": "FIAP Bank",
        "github_url": "https://github.com/MatheusBispoFaria/fiap-cp5-ddd-java",
        "category": "Projeto acadêmico · CP5 de Domain Driven Design / Java",
        "headline": "Arquitetura e integração em um sistema bancário acadêmico.",
        "summary": (
            "Projeto acadêmico que reúne Core Bancário, Plataforma de Crédito, "
            "Mesa de Operações e Internet Banking. Explora regras de domínio, "
            "APIs REST e comunicação entre aplicações Java e uma interface Angular."
        ),
        "features": (
            "Core e Plataforma organizados nas camadas de domínio, aplicação, infraestrutura e apresentação.",
            "Gestão de clientes, contas e solicitações de crédito com regras de negócio no domínio.",
            "Integração entre serviços com Feign e interface de Internet Banking em Angular.",
            "Testes de endpoints, validação de entradas e tratamento de erros nas APIs.",
        ),
        "technologies": ("Java 21", "Spring Boot", "DDD", "Angular", "Maven", "H2"),
        "icon": "fa-building-columns",
        "featured": False,
        "experience": None,
        "note": "Demonstração acadêmica com integrações financeiras externas simuladas e banco H2 em memória.",
    },
)

PROJECT_BY_SLUG = {project["slug"]: project for project in PROJECTS}
