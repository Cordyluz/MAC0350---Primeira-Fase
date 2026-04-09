# Banana Clicker 🍌🐒

Projeto desenvolvido para a disciplina de WebMAC utilizando a stack ensinada no curso: HTML, CSS, JavaScript, HTMX, FastAPI e SQLModel.

## Sobre o Projeto
**Banana Clicker** é um web app inspirado no jogo Cookie Clicker. Segue a lógica de um jogo idle clicker, onde o jogador deve clicar na banana para ganhar pontos e usar esses pontos para comprar Upgrades que aumentam a taxa de ganho. Estes upgrades podem ser Macacos, que geram bananas por segundo, cliques dourados que aumentam o quanto cada clique gera ou boosts que aumentam a efetividade dos macacos.

Todo o progresso é atrelado a um perfil de jogador e os usuários podem ver a sua posição no **Leaderboard**.

## Tecnologias e Requisitos (WebMAC)

1. **Front-end**: Conta com duas interfaces, a Tela do Jogo e o Leaderboard.
2. **Back-end em FastAPI**: Toda a lógica de estado global é gerida de forma assíncrona por uma API REST montada com FastAPI.
3. **Banco de Dados Relacional**: Implementado mediante SQLite usando `SQLModel`. Possui relacionamentos `Many-To-Many` gerenciando o Inventário de **Upgrades (Macacos)** que cada **Jogador** possui.
4. **Integração com HTMX e CRUD Completo**:
   - **Post (Create)**: Criação de perfil no jogo (htmx form).
   - **Get (Read)**: Carregar a lista paginada do Leaderboard a cada consulta.
   - **Put (Update)**: Salvar progresso atual (número de bananas/cliques) no banco.
   - **Delete (Delete)**: Apagar os dados e resets de usuário completamente do banco de forma retroativa.


## Como as peças se encaixam
- **JavaScript Local**: Lida com a experiência do usuário de clicar, para que o jogo não atrase com o ping de rede.
- **Integração HTMX**: A cada intervalo de tempo ou compra na loja, o Frontend e o Backend sincronizam o número verificado de Bananas no Banco de Dados através do HTMX, atualizando os blocos HTML condizentes do painel iterativo.
- **FastAPI / SQLModel**: O Backend lida estritamente com os dados e entrega visões parciais pelo servidor.

## Arquitetura de Diretórios e Arquivos
A estrutura do projeto está organizada da seguinte maneira:
- `main.py`: Ponto de entrada da aplicação FastAPI, contendo todas as rotas e a lógica de negócio do jogo (cálculo de BPS, poder de clique e validação de compras).
- `models.py`: Definição das tabelas e do esquema relacional utilizando SQLModel.
- `database.py`: Configuração de conexão e da engine do banco de dados SQLite (`banana_clicker.db`).
- `templates/`: Diretório que armazena os templates HTML usados para renderização com Jinja2 e HTMX (Ex: `index.html`, `game.html`, `partials/leaderboard.html`).
- `static/`: Diretório de arquivos estáticos contendo o CSS para estilização e o JS para as atualizações imediatas no lado do cliente.

## Modelagem e Banco de Dados (SQLModel)
O sistema relacional é composto por 3 tabelas principais:
- **Player**: Guarda os perfis e a pontuação global de cada usuário (`username`, `bananas_count`).
- **MonkeyUpgrade**: Catálogo mestre de melhorias que inclui Custo Base, Benefício (`bananas_per_second`) e Tipo (`monkey`, `click`, `boost`).
- **PlayerUpgrade (Junção N:N)**: Tabela associativa que guarda o status e a quantidade (`quantity`) de cada Upgrade contido no Inventário de um Player.

## Mecânicas do Jogo
A progressão é baseada num misto de engajamento ativo e progresso inativo (Idle):
- **Upgrades de Clique (`click`)**: Aumentam o número de bananas geradas a cada clique manual do usuário.
- **Upgrades Passivos (`monkey`)**: Macacos contratados que "farmam" bananas automaticamente a cada segundo de fundo (BPS - Bananas Por Segundo).
- **Boosts (`boost`)**: Melhorias que afetam o status de outros macacos específicos.
- **Escalonamento de Custo**: Cada compra de uma melhoria aumenta o custo dela mesma em 15%.

## Endpoints e Rotas Principais
A API do FastAPI unifica o suporte às views clássicas de DOM HTML e integrações reativas com HTMX:
- `GET /` e `POST /register`: Autenticação e reestruturação do perfil sem uso complexo de senhas, gerando e trazendo o progresso anterior automaticamente caso o nome de Usuário exista na base.
- `PUT /player/{id}/save`: Processa em tempo real (ou via intervalo em batch) a quantia atual somada no Front-end para refletir seguramente e continuamente no SQLite. 
- `POST /player/{id}/buy/{upg_id}`: Rota que gerencia o checkout. Deduz o balanço do `Player`, computa o avanço logístico dos descontos e atualiza condicionalmente o Template da Loja após recarregar as estatísticas globais no Python.
- `GET /leaderboard?page=N`: Promove Paginação da lista dos jogadores.
- `DELETE /player/{id}`: Executa exclusão e eliminação em cascata permanente de Saves e relatórios de jogabilidade.

## Como Executar Localmente
Siga as instruções abaixo para rodar o app no ambiente de desenvolvimento:

1. **Instale as dependências (FastAPI, Uvicorn, SQLModel)**:
   ```bash
   pip install fastapi uvicorn sqlmodel
   ```
2. **Inicie o App**:
   ```bash
   uvicorn main:app --reload
   ```
3. Abra a porta do Servidor no seu navegador (normalmente `http://localhost:8000`).

## Uso de AI
Foi usado IA para consultas de sintaxe e documentação das bibliotecas utilizadas, revisão de erros, sugestao de melhorias e documentação do projeto.
