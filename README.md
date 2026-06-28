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
├── app.py                # Inicializa o Flask e registra as rotas
├── config.py             # Configurações (secret key, banco, etc)
├── database.py           # Métodos auxiliares para o banco de dados
├── error_handlers.py     # Tratativa dos erros
├── models/               # Classes do SQLAlchemy
│   ├── __init__.py
│   ├── usuario.py        # Modelo de Usuário
│   ├── postagem.py       # Modelo de Post (com texto e caminho da imagem)
│   └── comentario.py     # Modelo de Comentário
├── routes/               # Lógica das rotas (controllers)
│   ├── __init__.py
│   ├── basic_routes.py   # Basico
│   ├── auth_routes.py    # Login e Cadastro
│   └── blog_routes.py    # CRUD de posts e comentários
└── uploads/              # Pasta para salvar as imagens dos posts
```

### 📦 Pacotes

* **Web**
  * Flask: Gerencia rotas e processa requisições HTTP;
  * Werkzeug: Base do Flask, lida com a parte técnica de baixo nível do protocolo WSGI. Permite o servidor Python converse com a web;
  * Jinja2: Motor de templates do Flask. Permite gerar conteúdo HTML dinâmico. Dependência essencial do Flask;
  * MarkupSafe: Usada pelo Jinja2 para proteger o código contra ataques de injeção (XSS);

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
  * itsdangerous: Biblioteca usada pelo Flask para assinar dados de forma segura (essencial para criar tokens de sessão e proteger cookies).
  * importlib-metadata && zipp: São bibliotecas de utilitários que permitem ao Python ler informações sobre os pacotes instalados no sistema.

### 🧠 Fluxo de Execução Técnica

A API processa requisições através de camadas integradas:
* **Infraestrutura:** O Click inicia a aplicação e o Python gerencia as dependências via importlib-metadata e zipp.
* **Camada Web:** O Werkzeug lida com o protocolo WSGI, enquanto o Flask gerencia a segurança de sessão com itsdangerous.
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
pip install click==8.4.2 Flask==3.1.3 Flask-SQLAlchemy==3.1.1 greenlet==3.5.3 importlib-metadata==9.0.0 itsdangerous==2.2.0 Jinja2==3.1.6 MarkupSafe==3.0.3 nose==1.3.7 SQLAlchemy==2.0.51 SQLAlchemy-Utils==0.42.1 Werkzeug==3.1.8 zipp==4.1.0 flasgger==0.9.7.1 PyYAML==6.0.2
```

### 3. Acesso ao projeto 🚀
```bash
flask run --host 0.0.0.0 --port 5000 --reload
```
Abra o navegador WEB e acesse: http://localhost:5000/#/

---

## 👤 Autor
* Márcio Corbolan - Desenvolvedor Principal

---

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
