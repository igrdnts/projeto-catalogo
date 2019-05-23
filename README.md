#Catálogo de itens

## Resumo

Quarto projeto do curso nanodegree da Udacity de Desenvolvedor Full-stack. Este projeto é um pequeno servidor em python, utilizando o framework Flask, que hospeda um serviço de registro de catálogo, onde o usuário deve logar com uma conta Facebook para adicionar categorias e itens. Há também um endpoint de API.

## Arquivos

Nesse projeto há vários arquivos:
  
  `database_setup.py` - arquivo de configuração do banco de dados.

`populate_db.py` - arquivo para popular o banco de dados.

`application.py` - arquivo back-end do site.

`fb_client_secrets.json` - arquivo com as chaves de acesso para API de login do Facebook

`/templates`- arquivos HTML responsáveis pela exibição. 

`/static` - arquivos CSS responsáveis pelo estilo da página.


## Como executar

Passo a passo para configuração e execução da máquina virtual, bem como rodar a aplicação:

1 - Instale o VirtualBox para o seu sistema operacional através desse link <https://www.virtualbox.org/wiki/Downloads>;

2 - Instale o Vagrant para o seu sistema operacional através desse link <https://www.vagrantup.com/downloads.html>;

3 - Coloque o arquivo catalog.zip na pasta vagrant e descompacte-o;

4 - No seu terminal, acesse o diretório vagrant, execute o comando `vagrant up` para carregar a máquina virtual linux;

5 - Com a máquina carregada, execute o comando `vagrant ssh` para acessar a máquina virtual;

6 - Acesse a pasta onde o `catalog.zip` está com o comando `cd /vagrant`;

6 - Execute o comando `python database_setup.py` para configurar o BD;

7 - Execute o comando `python populate_db.py` para popular o BD;

8 - Para rodar a aplicação, execute o comando `python application.py`

9 - Abra seu navegador e acesse o endereço http://localhost:5000
  
OBS: por rodar em ambiente local (sem validação https), use os seguintes dados para testar com o facebook login:
- Usuário: open_mqveiie_user@tfbnw.net	
- senha: catalogoteste


## Requisitos necessários

- Python 2.7 <https://www.python.org/download/releases/2.7/>
- Virtual Box <https://www.virtualbox.org/wiki/Downloads>
- Vagrant <https://www.vagrantup.com/downloads.html>