# Base de Conhecimento - Sistema Suporte Moodle IPÊ

## Quem é você

- Assistente Virtual do CIAR
- Ipêzinho

## Objetivo

Este documento descreve os procedimentos mais recorrentes realizados pela equipe de suporte dos ambientes Moodle IPÊ.

## Demandas Cobertas

1. Abertura de salas Moodle Ensino
2. Abertura de salas Moodle Pesquisa e Extensão
3. Cadastro manual de usuários
4. Cadastro de usuários em massa via planilha
5. Atendimento a alunos com dificuldade de acesso

---

# Procedimento: Abertura de Sala Moodle

## Aplicação

- Moodle Ensino
- Moodle Pesquisa e Extensão
- Outros ambientes Moodle

## Diferença Principal

### Moodle Ensino

Necessário configurar:

- Código de autoinscrição
- Período de autoinscrição

### Moodle Pesquisa e Extensão

- Não utiliza autoinscrição.
- Inscrição realizada via solicitação no Sistema de Tickets.

---

## Passo 1 - Validar Solicitação

Verificar:

- Instituição responsável pela disciplina
- Faculdade responsável
- Se o solicitante possui autorização para solicitar abertura da sala

---

## Passo 2 - Localizar Categoria

Acessar:

Administração do Site → Cursos → Gerenciar Cursos e Categorias

Localizar a categoria correta conforme:

- Unidade Acadêmica
- Curso
- Semestre

### Exemplo

Disciplina de Química:

Categoria:

Instituto de Química → Semestre correspondente

---

## Passo 3 - Criar Sala

Selecionar:

Criar Novo Curso

### Nome da Sala

Formato:

Nome da disciplina + Código

### Nome Breve

Formato recomendado:

```
CÓDIGO - ANO/SEMESTRE
```

Exemplo:

```
IQ298 - 2026/01
```

### Data de Encerramento

Caso informada no chamado:

- Configurar durante a criação da sala.

---

## Passo 4 - Configurar Participantes

Adicionar:

- Professor(es)
- Tutor(es)
- Equipe de suporte

Conforme informado no chamado.

---

## Passo 5 - Configurar Autoinscrição (Somente Moodle Ensino)

### Chave de Inscrição

Gerar:

- 8 caracteres aleatórios
- Letras minúsculas e/ou números

Exemplo:

```
a7d9k2m1
```

### Período de Autoinscrição

#### Cenário Normal

Início:

- 30 dias antes do início das aulas

Fim:

- 30 dias após o início das aulas

#### Solicitação após início das aulas

Início:

- Data atual

Fim:

- 30 dias após abertura da sala

---

## Passo 6 - Responder Chamado

Enviar ao solicitante:

- Link da sala
- Chave de inscrição
- Informações adicionais relevantes

---

# Procedimento: Cadastro Manual de Usuários

## Quando Utilizar

Recomendado quando:

- Até 10 usuários

Ambientes comuns:

- Moodle Pesquisa
- Moodle Capacita
- Outros ambientes

---

## Passo 1 - Verificar Quantidade

Se:

- Até 10 usuários → Cadastro manual
- Mais de 10 usuários → Cadastro por planilha

---

## Passo 2 - Acessar Cadastro

Navegar para:

Administração do Site → Usuários

Opções:

- Lista de Usuários
- Adicionar Novo Usuário

---

## Passo 3 - Criar Usuário

### Username

Utilizar:

CPF sem pontos e sem traços

Exemplo:

```
12345678900
```

### Senha

#### Moodle Pesquisa e Extensão

Senha padrão:

```
ufg@2020
```

### Importante

Marcar:

```
Forçar mudança de senha
```

---

## Passo 4 - Inscrever Usuário na Sala

Após criar usuário:

1. Acessar a sala indicada no chamado.
2. Inserir usuário.
3. Aplicar o papel informado.

Possíveis papéis:

- Estudante
- Professor
- Tutor
- Suporte

---

# Procedimento: Cadastro de Usuários por Planilha

## Quando Utilizar

Recomendado para:

- Mais de 10 usuários

---

## Estrutura da Planilha

Campos obrigatórios:

| Campo     | Descrição           |
| --------- | ------------------- |
| username  | CPF sem pontuação   |
| password  | Senha               |
| firstname | Primeiro nome       |
| lastname  | Sobrenome           |
| email     | E-mail              |
| course1   | Nome breve do curso |
| role1     | Papel do usuário    |

### Observação

Para estudantes:

- role1 pode permanecer vazio.

---

## Passo 1 - Preparar Dados

Copiar informações do solicitante para a planilha modelo.

---

## Passo 2 - Validar Dados

Conferir:

- CPF com 11 dígitos
- Dados completos
- Nome breve correto do curso

---

## Passo 3 - Salvar Arquivo CSV

Salvar como:

```
CSV (separado por vírgulas)
```

---

## Passo 4 - Converter para UTF-8

Abrir no Bloco de Notas.

Salvar novamente:

- Extensão: .csv
- Codificação: UTF-8

### Atenção

Após converter para UTF-8:

NÃO abrir novamente no Excel.

---

## Passo 5 - Importar Usuários

Acessar:

Administração do Site → Usuários → Carregar Lista de Usuários

Realizar upload do arquivo.

---

## Passo 6 - Validar Resultado

Verificar relatório de importação:

- Quantidade cadastrada
- Quantidade com erro

Registrar resultado para retorno ao solicitante.

---

# Procedimento: Aluno com Dificuldade de Acesso

## Objetivo

Diagnosticar e resolver problemas de autenticação.

---

# Moodle Ensino

## Regra Principal

Usuários do Moodle Ensino devem possuir autenticação:

```
LDAP
```

---

## Problema Mais Comum

Usuário tenta acessar utilizando:

- E-mail institucional completo

Quando deveria utilizar:

- Login único

---

## Verificação

Acessar:

Administração do Site → Usuários → Lista de Usuários

Buscar por:

1. E-mail
2. Nome + sobrenome

Abrir:

Perfil → Modificar Perfil

Verificar:

```
Método de autenticação = LDAP
```

---

## Se LDAP estiver configurado

Conclusão:

Cadastro correto.

Resposta ao usuário:

Informar que deve acessar utilizando o login único.

---

# Moodle Pesquisa, Capacita e Outros

## Verificações

Confirmar:

- CPF correto
- Dados cadastrais corretos

---

## Recuperação de Senha

Orientar usuário a:

- Solicitar redefinição de senha

---

## Caso não receba e-mail

Realizar redefinição manual.

### Senha padrão Moodle Pesquisa

```
ufg@2020
```

---

# Regras de Negócio

## Autoinscrição

Aplicável apenas ao:

- Moodle Ensino

---

## Senha Padrão Moodle Pesquisa

```
ufg@2020
```

---

## Username

Sempre:

CPF sem pontos e sem traços.

---

## Cadastro em Massa

Utilizar quando:

- Mais de 10 usuários

---

## Cadastro Manual

Utilizar quando:

- Até 10 usuários

---

# Palavras-chave para Busca Semântica

- abertura de sala
- criar curso moodle
- autoinscrição
- chave de inscrição
- cadastro manual
- cadastro por planilha
- importar usuários
- csv utf8
- ldap
- login único
- redefinição de senha
- moodle ensino
- moodle pesquisa
- moodle extensão
- tutor
- professor
- estudante
- suporte
- cpf usuário

# Base de Conhecimento - Suporte Moodle IPÊ (CIAR/UFG)

## Visão Geral

O Moodle IPÊ possui duas plataformas:

- Moodle IPÊ - Ensino
- Moodle IPÊ - Pesquisa e Extensão

Esta base de conhecimento auxilia usuários nos principais processos e problemas relacionados ao Moodle IPÊ.

---

# Perfis Atendidos

- Professor
- Técnico
- Tutor
- Aluno

---

# Abertura de Sala Moodle

## Moodle IPÊ - Ensino

Para solicitar a criação de uma sala no Moodle Ensino:

https://suporte.ciar.ufg.br/open.php?topicId=44

---

## Moodle IPÊ - Pesquisa e Extensão

Para solicitar a criação de uma sala no Moodle Pesquisa e Extensão:

https://suporte.ciar.ufg.br/open.php?topicId=45

---

# Cadastro de Usuários

## Moodle IPÊ - Ensino

Para solicitar cadastro de usuários:

https://suporte.ciar.ufg.br/open.php?topicId=21

---

## Moodle IPÊ - Pesquisa e Extensão

Para solicitar cadastro de usuários:

https://suporte.ciar.ufg.br/open.php?topicId=22

---

# Agendamento de Reunião

Para solicitar uma reunião com a equipe de suporte:

https://suporte.ciar.ufg.br/open.php?topicId=30

---

# Problemas de Login e Senha

## Moodle IPÊ - Ensino

### Como acessar

Utilize o Login Único da UFG.

**Identificação do usuário:**

- Apenas o login institucional.
- Exemplo: `joao.silva`
- Não utilizar `@ufg.br`.

**Senha:**

- A mesma utilizada no Portal UFGNet/SIGAA.

### Quando o acesso não funciona

Abra um chamado:

https://suporte.ciar.ufg.br/open.php?topicId=15

### Tutorial

https://www.youtube.com/watch?v=jGhUS6XXw9E

### Recuperação de Senha

https://www.youtube.com/watch?v=o_RTvfiv13I

---

## Moodle IPÊ - Pesquisa e Extensão

### Como acessar

**Primeiro acesso:**

Identificação do usuário:

- CPF sem pontos e sem traços.

Senha inicial:

- `ufg@2020`

Após o primeiro login será solicitada a alteração da senha.

### Quando o acesso não funciona

Abra um chamado:

https://suporte.ciar.ufg.br/open.php?topicId=15

### Tutorial

https://www.youtube.com/watch?v=vIBZGVcsrgM

### Recuperação de Senha

https://www.youtube.com/watch?v=KjV_SP7i0D8

---

# Site Não Abre

## Procedimentos recomendados

1. Limpar cache do navegador.
2. Testar em aba anônima.
3. Verificar conexão com a internet.

Se o problema persistir:

https://suporte.ciar.ufg.br/open.php?topicId=14

---

# Problemas com E-mail de Recuperação

Caso não receba o e-mail de recuperação de senha:

- Verifique se o endereço de e-mail está correto.
- Confira as pastas Spam e Lixo Eletrônico.

Persistindo o problema:

https://suporte.ciar.ufg.br/open.php?topicId=38

---

# Acompanhar Chamado (Ticket)

Para consultar o andamento de uma solicitação:

https://suporte.ciar.ufg.br/view.php

Informações necessárias:

- E-mail utilizado na abertura do chamado.
- Número do ticket.

Tutorial:

https://www.youtube.com/watch?v=JMwm1Z8QWyQ

---

# Navegação na Interface Moodle

Após realizar login:

## Menu Principal

### Meus Cursos

Exibe todos os cursos nos quais o usuário está matriculado.

### Pesquisa

Localizada à direita da tela.

### Notificações

Ícone de sino.

### Mensagens

Ícone de conversa.

### Correio Interno

Ícone de carta.

### Perfil do Usuário

Disponível ao clicar na foto do usuário.

### Modo de Edição

Botão deslizante disponível no painel.

Em caso de dificuldades:

https://suporte.ciar.ufg.br/open.php

Tutorial:

https://www.youtube.com/watch?v=HsAbZaTA3tA

---

# Atualização de Dados do Perfil

## Como alterar informações pessoais

1. Clique na foto do usuário.
2. Acesse "Perfil".
3. Clique em "Configurações".
4. Selecione "Modificar perfil".
5. Atualize nome e e-mail.
6. Clique em "Atualizar perfil".

### Alteração de E-mail

Após alterar o e-mail:

- Verifique sua caixa de entrada.
- Confirme o novo endereço através do link enviado.

Caso ocorra erro:

https://suporte.ciar.ufg.br/open.php

Tutorial:

https://www.youtube.com/watch?v=PEn3FVVzcFM

---

# Acesso aos Cursos

## Onde encontrar os cursos

### Meus Cursos

Exibe todos os cursos vinculados ao usuário.

### Painel

Permite visualizar:

- Cursos acessados recentemente.
- Resumo dos cursos inscritos.
- Cartões de acesso rápido aos cursos.

Caso encontre problemas:

https://suporte.ciar.ufg.br/open.php

Tutorial:

https://www.youtube.com/watch?v=2OPMwZFg3jI

---

# Abertura de Chamado para Outros Problemas

Caso o problema não esteja contemplado nesta base:

Solicitar ao usuário:

1. Nome completo.
2. E-mail institucional.
3. CPF (somente números).
4. Descrição detalhada do problema.

Após coletar as informações, abrir um ticket junto à equipe de suporte.

---

# Encaminhamento para Suporte

Quando não houver solução direta disponível:

Orientar o usuário a abrir um chamado em:

https://suporte.ciar.ufg.br/open.php

---

# Regras de Atendimento para IA

## Prioridade de Resposta

1. Resolver utilizando orientações desta base.
2. Indicar tutorial quando disponível.
3. Encaminhar para abertura de ticket quando necessário.

## Quando abrir ticket obrigatoriamente

- Problemas de acesso não resolvidos.
- Erros de autenticação persistentes.
- Solicitação de criação de salas.
- Cadastro de usuários.
- Problemas técnicos na plataforma.
- Solicitação de reunião.
- Alterações administrativas.

## Tom de Resposta

- Educado.
- Objetivo.
- Didático.
- Focado em resolução.

## Exemplo de Encerramento

"Espero ter ajudado. Caso o problema persista, abra um chamado pelo portal de suporte para que a equipe possa analisar sua situação."
