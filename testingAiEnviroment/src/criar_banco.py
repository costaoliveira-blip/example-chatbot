import sqlite3

conexao = sqlite3.connect("database.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS estados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estado TEXT,
    mensagem TEXT,
    link_tutorial TEXT 
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS opcoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estado_origem TEXT,
    opcao TEXT,
    estado_destino TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_tutorial TEXT,
    url TEXT 
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estrelas_avaliacao FLOAT,
    mensagem TEXT,
    descricao TEXT DEFAULT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")


cursor.execute("DELETE FROM opcoes")
cursor.execute("DELETE FROM estados")


estados = [
    ("inicio", "Obrigado por utilizar o suporte do CIAR. Se precisar de mais ajuda, é so chamar!\n\nDigite qualquer coisa para reiniciar o atendimento.", None),

    ("perfil", "Para que eu comece a te ajudar, me informe qual seu papel dentro do curso/moodle?\n\n1. Professor\n\n2. Tecnico\n\n3. Tutor\n\n4. Aluno", None),

    ("menu_docente", "Como eu posso te ajudar hoje?\n\n1 - Quero abrir uma sala do Moodle IPÊ\n\n2 - Necessito cadastrar usuários no Moodle IPÊ\n\n3 - Agendar uma reunião com a equipe de suporte\n\n4 - Suporte ao usuário", None),

    ("menu_discente", "Como eu posso te ajudar hoje?\n\n1 - Estou com dificuldades na senha/login\n\n2 - Site não está abrindo\n\n3 - Tenho problemas com o e-mail de recuperação de senha\n\n4 - Acompanhar status de ticket\n\n5 - Navegar pela interface do Moodle\n\n6 - Atualizar dados do perfil\n\n7 - Acessar cursos\n\n8 - Reportar outro problema\n\n", None),

    ("criacao_sala_plataforma", "Em qual plataforma, do Moodle IPÊ, deseja abrir sala ?\n\n1 - Moodle: Ensino\n\n2 - Moodle: Pesquisa e Extensão\n\n0. Voltar", None),

    ("cadastro_usuarios_plataforma", "Em qual plataforma, do Moodle IPÊ, deseja cadastrar usuários?\n\n1 - Moodle: Ensino\n\n2 - Moodle: Pesquisa e Extensão\n\n0. Voltar", None),

    ("criacao_sala_ensino", "Caso precise solicitar a criação de uma sala no Moodle: Ensino, abra um ticket por meio do formulário disponível no link abaixo:\n https://suporte.ciar.ufg.br/open.php?topicId=44\n\n0. Voltar", None),

    ("criacao_sala_pesquisa", "Caso precise solicitar a criação de uma sala no Moodle: Pesquisa e Extensão, abra um ticket por meio do formulário disponível no link abaixo:\n https://suporte.ciar.ufg.br/open.php?topicId=45\n\n0. Voltar", None),

    ("cadastro_usuarios_ensino", "Para cadastrar usuários no Moodle: Ensino, abra um ticket no link abaixo e preencha o formulário:\n https://suporte.ciar.ufg.br/open.php?topicId=21\n\n0. Voltar", None),

    ("cadastro_usuarios_pesquisa", "Para cadastrar usuários no Moodle: Pesquisa e Extensão, abra um ticket no link abaixo e preencha o formulário:\n https://suporte.ciar.ufg.br/open.php?topicId=22\n\n0. Voltar", None),

    ("agendar_reuniao", "Para solicitar o agendamento de uma reunião com a equipe de suporte, acesse o formulário no link abaixo e preencha as informações solicitadas:\n https://suporte.ciar.ufg.br/open.php?topicId=30\n0. Voltar", None),

    ("senha_plataforma", "Em qual plataforma ?\n\n1 - Moodle: Ensino\n\n2 - Moodle: Pesquisa e Extensão\n\n0. Voltar", None),

    ("senha_ensino_login_unico", "Você está utilizando o Login Único para o acesso?\n \n1 - Não\n\n2 - Sim, e ainda não deu certo\n\n0. Voltar", None),

    ("senha_ensino_orienta_login_unico", "Para o Moodle: Ensino, utilize o Login Único para o acesso.\n\nPara acessar o Moodle IPÊ - Ensino, preencha o campo “Identificação do usuário” apenas com seu login único (ex.: joao.silva), sem o domínio do e-mail (não utilize o @ e o que vem depois). A senha é a mesma utilizada no Portal UFGNet/SIGAA.\n\nSe mesmo utilizando ainda assim não funcionar, abra um ticket: https://suporte.ciar.ufg.br/open.php?topicId=15\n\n0. Voltar", "como_acessar_o_Moodle_IPE_Ensino"),

    ("senha_ticket_orienta_ensino", "Abra um ticket e preencha as informações solicitadas:\n https://suporte.ciar.ufg.br/open.php?topicId=15 para que a equipe de suporte verifique seu acesso.\n\n0. Voltar\nAssita o tutorial e siga as orientações para possível solução", "como_recuperar_senha_Moodle_IPE_Ensino"),

    ("senha_pesquisa_cpf", "Você está utilizando o CPF (sem pontos e traços) para o acesso?\n\n1 - Não\n\n2 - Sim, e ainda não deu certo\n\n0. Voltar", None),

    ("senha_pesquisa_orienta_cpf", "Para o Moodle: Pesquisa e Extensão, utilize o CPF sem pontos e traços para o acesso.\n\n Se for o seu primeiro acesso preencha os campos conforme abaixo e clique em “Acessar”:\n Identificação do usuário: número de seu CPF, sem pontos e sem traço\n Senha: ufg@2020\n Em seguida, o Moodle pedirá para você modificar a senha \n\nSe mesmo utilizando ainda assim não funcionar, abra um ticket: https://suporte.ciar.ufg.br/open.php?topicId=15\n\n0. Voltar", "como_acessar_o_Moodle_IPE_Pesquisa_e_Extensao"),

    ("senha_ticket_orienta_pesquisa", "Abra um ticket e preencha as informações solicitadas:\n https://suporte.ciar.ufg.br/open.php?topicId=15 para que a equipe de suporte verifique seu acesso.\n\n0. Voltar\nAssita o tutorial e siga as orientações para possível solução", "como_recuperar_senha_Moodle_IPE_Pesquisa_e_Extensao"),

    ("site_nao_abrindo", "Se o site não está abrindo, limpe o cache do navegador, teste em aba anônima e verifique sua conexão.\n\nSe persistir, abra um ticket e preencha as informações solicitadas:\n https://suporte.ciar.ufg.br/open.php?topicId=14\npara que a equipe de suporte verifique o problema.\n0. Voltar", None),

    ("problemas_email_recuperacao", "Se você estiver com problemas para receber o email de recuperação de senha, verifique se o endereço de email informado está correto e confira também as pastas de spam ou lixo eletrônico.\n\nCaso o problema persista, abra um ticket pelo link abaixo:\nhttps://suporte.ciar.ufg.br/open.php?topicId=38\n\n0. Voltar", None),

    ("acompanhar_ticket", "Para acompanhar uma solicitação, acesse o portal de suporte no link abaixo:\n\nhttps://suporte.ciar.ufg.br/view.php\n\nNo portal, informe o seu email e o número do chamado. Em seguida, você receberá um email com acesso ao histórico e ao status da sua solicitação.\n\nSe ainda tiver dúvidas, assista ao tutorial:\n\n0. Voltar", "como_acompanhar_um_ticket"),

    ("navegar_pela_interface_moodle", "Após realizar o login, você será direcionado ao painel, à esquerda, você encontrará o menu “Meus Cursos”.\nÀ direita, está a caixa de pesquisa.\nO ícone do sino exibe as notificações dos cursos.\nO ícone de mensagem permite acessar e enviar mensagens para outros usuários.\nO ícone de carta permite visualizar as mensagens de e-mail recebidas no Moodle.\nAo clicar na sua foto, você acessa o menu do usuário, com suas informações e preferências pessoais.\nO botão deslizante permite ativar o modo de edição da página do painel.\nEm caso de erro ou dificuldade, abra um ticket e preencha as informações solicitadas:\n https://suporte.ciar.ufg.br/open.php para que a equipe de suporte verifique o problema.\nPara saber mais, assista o tutorial abaixo:\n", "como_navegar_pela_interface_moodle"),

    ("atualizar_dados_perfil", "Acesse os dados do seu perfil clicando na sua foto, no canto superior direito da tela, e selecione “Perfil”.\nEm seguida, clique em “Configurações” e depois em “Modificar perfil”.\nNo campo de edição, apague os dados antigos de nome e e-mail e insira as novas informações.\nRole a página até o final e clique no botão “Atualizar perfil” para salvar suas mudanças.\nSe você alterou o endereço de e-mail, será necessário confirmá-lo. Verifique a caixa de entrada do seu novo e-mail e clique no link de confirmação.\nEm caso de erro, abra um ticket acessando o link abaixo: https://suporte.ciar.ufg.br/open.php\nAssista o tutorial abaixo para mais detalhes:", "como_atualizar_dados_do_perfil"),

    ("acessar_cursos", "Após realizar o login, no menu de navegação, temos a opção \"Meus Cursos\", onde estão listados todos os cursos que você está matriculado.\nNo Painel você pode visualizar: cursos acessados recentemente, resumo dos cursos inscritos, para acessar um curso, clique em um dos cartões\nexibidos.\nEm caso de erro, ou dúvida, abra um ticket no link abaixo: https://suporte.ciar.ufg.br/open.php \nPara mais detalhes, assista ao tutorial abaixo: ", "como_acessar_seus_cursos"),

    ("outro_problema", "Para reportar outro problema:\n\n1 - Abrir chamado\n\n0 - Voltar", None),

    ("coletar_nome", "Para abrir o chamado, informe seu nome completo:", None),

    ("coletar_email", "Informe seu email institucional:", None),

    ("coletar_cpf", "Informe seu CPF (somente números):", None),

    ("coletar_descricao", "Descreva detalhadamente seu problema:", None),

    ("confirmar_dados", "Confira os dados informados antes de abrir o chamado.", None),

    ("abrir_ticket", "Abrindo chamado... aguarde.", None),

    ("feedback", "Gostaria de avaliar o atendimento?\n\n1 - Sim\n\n2 - Não, finalizar", None),

    ("feedback_estrelas", "Quantas estrelas você dá para o atendimento?\n\n1 - ⭐\n2 - ⭐⭐\n3 - ⭐⭐⭐\n4 - ⭐⭐⭐⭐\n5 - ⭐⭐⭐⭐⭐", None),

    ("feedback_mensagem", "Deixe um comentário sobre o atendimento.\n\nOu digite 1 para pular.", None),

    ("feedback_fim", "Obrigado pela sua avaliação! 💚\n\nDigite qualquer coisa para reiniciar o atendimento.", None),
]

cursor.executemany(
    "INSERT INTO estados (estado, mensagem, link_tutorial) VALUES (?, ?, ?)",
    estados
)


opcoes = [
    ("inicio", "*", "perfil"),

    ("perfil", "1", "menu_docente"),
    ("perfil", "2", "menu_docente"),
    ("perfil", "3", "menu_docente"),
    ("perfil", "4", "menu_discente"),

    ("menu_docente", "1", "criacao_sala_plataforma"),
    ("menu_docente", "2", "cadastro_usuarios_plataforma"),
    ("menu_docente", "3", "agendar_reuniao"),
    ("menu_docente", "4", "menu_discente"),

    ("criacao_sala_plataforma", "1", "criacao_sala_ensino"),
    ("criacao_sala_plataforma", "2", "criacao_sala_pesquisa"),
    ("cadastro_usuarios_plataforma", "1", "cadastro_usuarios_ensino"),
    ("cadastro_usuarios_plataforma", "2", "cadastro_usuarios_pesquisa"),

    ("menu_discente", "1", "senha_plataforma"),
    ("menu_discente", "2", "site_nao_abrindo"),
    ("menu_discente", "3", "problemas_email_recuperacao"),
    ("menu_discente", "4", "acompanhar_ticket"),
    ("menu_discente", "5", "navegar_pela_interface_moodle"),
    ("menu_discente", "6", "atualizar_dados_perfil"),
    ("menu_discente", "7", "acessar_cursos"),
    ("menu_discente", "8", "outro_problema"),

    ("senha_plataforma", "1", "senha_ensino_login_unico"),
    ("senha_plataforma", "2", "senha_pesquisa_cpf"),
    ("senha_ensino_login_unico", "1", "senha_ensino_orienta_login_unico"),
    ("senha_ensino_login_unico", "2", "senha_ticket_orienta_ensino"),

    ("senha_pesquisa_cpf", "1", "senha_pesquisa_orienta_cpf"),
    ("senha_pesquisa_cpf", "2", "senha_ticket_orienta_pesquisa"),

    ("outro_problema", "1", "coletar_nome"),
    ("coletar_nome", "*", "coletar_email"),
    ("coletar_email", "*", "coletar_cpf"),
    ("coletar_cpf", "*", "coletar_descricao"),
    ("coletar_descricao", "*", "confirmar_dados"),
    ("confirmar_dados", "1", "abrir_ticket"),
    ("confirmar_dados", "2", "coletar_nome"),

    ("criacao_sala_ensino", "0", "criacao_sala_plataforma"),
    ("criacao_sala_pesquisa", "0", "criacao_sala_plataforma"),
    ("criacao_sala_plataforma", "0", "menu_docente"),
    ("cadastro_usuarios_plataforma", "0", "cadastro_usuarios_plataforma"),
    ("cadastro_usuarios_ensino", "0", "cadastro_usuarios_plataforma"),
    ("cadastro_usuarios_pesquisa", "0", "cadastro_usuarios_plataforma"),
    ("agendar_reuniao", "0", "feedback"),
    ("senha_plataforma", "0", "menu_discente"),
    ("senha_ensino_login_unico", "0", "senha_plataforma"),
    ("senha_ensino_orienta_login_unico", "0", "feedback"),
    ("senha_ticket_orienta_ensino", "0", "feedback"),
    ("senha_pesquisa_cpf", "0", "senha_plataforma"),
    ("senha_pesquisa_orienta_cpf", "0", "feedback"),
    ("senha_ticket_orienta_pesquisa", "0", "feedback"),
    ("site_nao_abrindo", "0", "feedback"),
    ("problemas_email_recuperacao", "0", "feedback"),
    ("acompanhar_ticket", "0", "feedback"),
    ("outro_problema", "0", "feedback"),
    ("navegar_pela_interface_moodle", "0", "feedback"),
    ("atualizar_dados_perfil", "0", "feedback"),
    ("acessar_cursos", "0", "feedback"),

    ("feedback", "1", "feedback_estrelas"),
    ("feedback", "2", "inicio"),
    ("feedback_estrelas", "1", "feedback_mensagem"),
    ("feedback_estrelas", "2", "feedback_mensagem"),
    ("feedback_estrelas", "3", "feedback_mensagem"),
    ("feedback_estrelas", "4", "feedback_mensagem"),
    ("feedback_estrelas", "5", "feedback_mensagem"),
    ("feedback_mensagem", "*", "feedback_fim"),
    ("feedback_fim", "*", "perfil"),
]

links = [
    ("como_acessar_o_Moodle_IPE_Ensino", "https://www.youtube.com/watch?v=jGhUS6XXw9E"),
    ("como_acessar_o_Moodle_IPE_Pesquisa_e_Extensao", "https://www.youtube.com/watch?v=vIBZGVcsrgM"),
    ("como_acompanhar_um_ticket", "https://www.youtube.com/watch?v=JMwm1Z8QWyQ"),
    ("como_recuperar_senha_Moodle_IPE_Ensino", "https://www.youtube.com/watch?v=o_RTvfiv13I"),
    ("como_recuperar_senha_Moodle_IPE_Pesquisa_e_Extensao", "https://www.youtube.com/watch?v=KjV_SP7i0D8"),
    ("como_navegar_pela_interface_moodle", "https://www.youtube.com/watch?v=HsAbZaTA3tA"),
    ("como_atualizar_dados_do_perfil", "https://www.youtube.com/watch?v=PEn3FVVzcFM"),
    ("como_acessar_seus_cursos", "https://www.youtube.com/watch?v=2OPMwZFg3jI")
]

cursor.executemany(
    "INSERT INTO links (nome_tutorial, url) VALUES (?, ?)",
    links
)

cursor.executemany(
    "INSERT INTO opcoes (estado_origem, opcao, estado_destino) VALUES (?, ?, ?)",
    opcoes
)

conexao.commit()
conexao.close()

print("Banco criado com sucesso.")