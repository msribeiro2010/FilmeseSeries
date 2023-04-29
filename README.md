# FilmeseSeries

Para agendar o app rodar automaticamente toda Sexta-Feira:

Você pode usar o cron. 
Para fazer isso, abra o terminal e digite crontab -e para editar o arquivo cron. Adicione uma linha como esta:

0 0 * * 5 cd /caminho/para/seu/script && /caminho/para/python3 seu_script.py

Essa linha diz ao cron para executar o comando cd /caminho/para/seu/script && /caminho/para/python3 seu_script.py à meia-noite de todas as sextas-feiras. 
Você deve substituir /caminho/para/seu/script pelo diretório onde está o seu script e /caminho/para/python3 pelo caminho para o executável Python
