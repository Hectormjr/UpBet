# UpBet
## Dash do Desafio para Analista de BI

Fiz uma investigação do porque não estava rodando o dash durante a reunião e creio que o problema esteja no banco de dados. Não esou conseguindo efetuar a conexão, enviei um print no email sobre a mensagem no postre, mas estou deixando aqui como baixar e rodar o app, como foi pedido.

### Tecnologias :
Python
Streamlit
Plotypy
PostgreSQL

### Download, Instalação e Uso:
Para fazer o uso local da aplicação é necessario criar um virtual envoriment (venv) na pasta do app, o passo a passo é descrito a seguir.

#### 1.Download :
1.1 Clonar o repositorio :
    git clone https://github.com/Hectormjr/UpBet.git
1.2 Descompactar o arquivo    
 

#### 2.Instalação dos pacotes :
##### Windows :
2.1 Criação do venv :
    python -m venv venv

2.2 Ativação do venv :
    venv/Scripts/activate

2.3 Istalação dos pacotes :
    pip install -r requirements.txt 

##### Mac :
2.1 Criação do venv :
    python3 -m venv venv

2.2 Ativação do venv :
    venv/Scripts/activate

2.3 Istalação dos pacotes :
    pip3 install -r requirements.txt 

#### 3.Uso :
No Streamlit a conexão com o DB é feita através de um arquivo secrets.toml, porém para que possa ser usada feature de deploy deles, da forma correta, não se deve deixar este arquivo no github e conexão é feita nas configurações no site da Streamlit. Por isso, para rodar localmente é necessario a criação deste arquivo manualmente, segue o passo a passo.

3.1 Criação do arquivo secrets para a conexão com o banco de dados :
    3.1.1 Criar pasta ".streamlit" :
        .streamlit

    3.1.2 Criar arquivo :
        secrets.toml

    3.1.3 Setar conexão no arquivo secrets :
        [connections.postgresql]
        dialect = "postgresql"
        host = "144.22.211.147"
        port = "5436"
        database = "upbet"
        username = "bear"
        password = "dev!!!00"
    
3.2 Rodar a aplicação :
    streamlit run dashboard.py
