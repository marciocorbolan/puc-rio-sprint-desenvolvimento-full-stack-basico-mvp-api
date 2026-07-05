# PUC RIO - Desenvolvimento Full Stack Básico - MVP - Blog API

Este projeto é o MVP da sprint de Desenvolvimento Full Stack Básico, focado na construção de uma API.

* Foco desta entrega: Desenvolvimento exclusivo da camada de API (Backend), responsável pela persistência de dados, autenticação e regras de negócio.
* Integração: Este componente foi projetado para servir como base para uma aplicação SPA (Single Page Application), que compõe a segunda parte desta sprint e consumirá os endpoints aqui definidos.

---

## 📋 Funcionalidades

* **Controle de acesso:** Sistema de registro e autenticação de usuário.
* **Gerenciamento de Conteúdo:** Criação, listagem e busca de postagens contendo texto e arquivo de imagem.
* **Interação Social:** Sistema comentário, exclusivo para usuários autenticados.
* **Documentação:** Swagger (OpenAPI).

---

## 🛠️ Estrutura do Projeto

```text
puc-rio-sprint-desenvolvimento-full-stack-basico-mvp-api/
├── app.py                # Ponto de entrada da aplicação; configura o Flask e registra as rotas
├── config.py             # Gerenciamento de variáveis de ambiente e configurações globais (ex: SECRET_KEY)
├── database.py           # Instanciação e configuração da conexão com o banco de dados (SQLAlchemy)
├── error_handlers.py     # Centralização de tratativas de erros e exceções
├── middlewares/          # Camada de processamento intermediário
│   ├── __init__.py
│   └── decorators.py     # Tratativa customizadas (ex: controle de acesso e autenticação JWT)
├── models/               # Definição das entidades do banco de dados (ORM)
│   ├── __init__.py
│   ├── blog.py           # Modelo blog
│   ├── comment.py        # Modelo comment
│   ├── post.py           # Modelo post
│   ├── user_status.py    # Modelo status do modelo user
│   └── user.py           # Modelo user
├── routes/               # Lógica das rotas (controllers)
│   ├── __init__.py
│   ├── auth_routes.py    # Endpoints de autenticação (registro, login, logout)
│   ├── basic_routes.py   # Endpoints basico (status / home)
│   ├── blog_routes.py    # Endpoints para o blog (CRUD completo)
│   └── user_routes.py    # Endpoints de gerenciamento de perfil do usuário
├── utils/                # Conjunto de funções auxiliares e lógica de suporte
│   ├── __init__.py
│   ├── file_manager.py   # Lógica para salvamento e leitura de arquivos em disco
│   ├── text_utils.py     # Funções auxiliares para manipulação de texto (ex: slugify)
│   └── validation.py     # Lógica de validação de dados de entrada e imagens (Base64)
└── uploads/              # Diretório de armazenamento físico de ativos (imagens)
```

### 📦 Pacotes

* **Web**
  * Flask: Gerencia rotas e processa requisições HTTP;
  * Werkzeug: Base do Flask, lida com a parte técnica de baixo nível do protocolo WSGI. Permite o servidor Python converse com a web;
  * Jinja2: Motor de templates do Flask. Permite gerar conteúdo HTML dinâmico. Dependência essencial do Flask;
  * MarkupSafe: Usada pelo Jinja2 para proteger o código contra ataques de injeção (XSS);

* **Segurança e Comunicação**
  * Flask-CORS: Essencial para APIs que serão consumidas por aplicações hospedadas em origens diferentes. Ele gerencia os cabeçalhos HTTP necessários para permitir requisições Cross-Origin com segurança;
  * PyJWT: Criar, codificar e decodificar tokens JWT (JSON Web Tokens), utilizado na autenticação;
  * itsdangerous: Biblioteca usada pelo Flask para assinar dados de forma segura (essencial para criar tokens de sessão e proteger cookies).
  * Flask-Limiter: Adiciona limites de taxa (rate limiting) às rotas da API. Protege a aplicação contra abusos e ataques de força bruta, limitando a quantidade de requisições por usuário ou IP. (Novo)

* **Documentação**
  * Flasgger: Integra o Swagger UI ao Flask, permitindo a criação da interface interativa e processamento de arquivos .yml.
  * PyYAML: Biblioteca que permite ao Flasgger ler e interpretar o conteúdo dos seus arquivos de documentação YAML.

* **Banco de Dados**
  * SQLAlchemy: O ORM (Object-Relational Mapper). Permite consultas de banco de dados usando classes e objetos;
  * Flask-SQLAlchemy: Uma ponte que integra o SQLAlchemy ao Flask. Facilita configuração da conexão e o gerenciamento da sessões;
  * SQLAlchemy-Utils: Funcionalidades extras do SQLAlchemy (ex: tipos específicos para moedas, e-mails ou senhas);
  * greenlet: Dependência de baixo nível que o SQLAlchemy utiliza para gerenciar tarefas;

* **Utilitários e Infraestrutura**
  * Click: Interfaces de linha de comando para o Flask (ex: flask run);
  * importlib-metadata && zipp: São bibliotecas de utilitários que permitem ao Python ler informações sobre os pacotes instalados no sistema.

### 🧠 Fluxo de Execução Técnica

A API processa requisições através de camadas integradas:
* **Infraestrutura:** O Click inicia a aplicação e o Python gerencia as dependências via importlib-metadata e zipp.
* **Camada Web:** O Werkzeug lida com o protocolo WSGI, o Flask-CORS filtra a origem das requisições e o Flask-Limiter impõe restrições de tráfego, bloqueando requisições excessivas antes do processamento completo. Em seguida, o Flask gerencia a segurança de sessão com itsdangerous e o PyJWT valida a autenticação de usuários via tokens.
* **Camada de Dados:** O Flask-SQLAlchemy utiliza o SQLAlchemy e greenlet para traduzir objetos Python em consultas SQL eficientes.

### ⚙️ Ferramentas de Desenvolvimento
* **Visual Studio Code:** `sudo snap install code --classic`
* **Git:** `sudo apt install git -y`
* **Python 3:** `sudo apt install python3-full -y`

---

## 💻 Projeto

### 1. Clonar o repositório
~~~bash
cd ~/
git clone https://github.com/marciocorbolan/puc-rio-sprint-desenvolvimento-full-stack-basico-mvp-api.git
cd puc-rio-sprint-desenvolvimento-full-stack-basico-mvp-api
~~~

### 2. Requisito básicos

1. **Ambiente virtual - Criação:** O ambiente é criado na pasta do projeto (Ação única).
```bash
python3 -m venv venv
```

2. **Ambiente virtual - Inicialização:** Sempre que fechar/abrir o terminal, será necessário iniciar o ambiente.
```bash
source venv/bin/activate
```

3. **Pacotes - Instalação:** Os pacotes estão versionados para garantir a compatibilidade (Ação única).
```bash
pip install click==8.4.2 flasgger==0.9.7.1 Flask==3.1.3 flask-cors==6.0.5 flask-limiter==4.1.1 Flask-SQLAlchemy==3.1.1 greenlet==3.5.3 importlib-metadata==9.0.0 itsdangerous==2.2.0 Jinja2==3.1.6 MarkupSafe==3.0.3 nose==1.3.7 PyJWT==2.13.0 PyYAML==6.0.2 SQLAlchemy==2.0.51 SQLAlchemy-Utils==0.42.1 Werkzeug==3.1.8 zipp==4.1.0
```

### 3. Acesso ao projeto 🚀
```bash
flask run --host 0.0.0.0 --port 8000 --reload
```
Abra o navegador WEB e acesse: http://localhost:8000
Documenteção: http://localhost:8000/apidocs

---

## 👤 Autor
* Márcio Corbolan - Desenvolvedor Principal

---

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
