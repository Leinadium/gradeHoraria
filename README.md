# GradeGenerator

Repositório do código do site [GradeGenerator](http://5p.myddns.me:5000). O site é baseado em *Flask*, possui uma base de dados *MySQL*
e se utiliza de *Selenium* para coletar as disciplinas diariamente disponibilizadas pela PUC-Rio.

O aplicativo é capaz de criar sua grade através de várias configurações, automaticamente selecionando a melhor grade.

O aplicativo também é capaz de armazenar o seu resultado, permitindo o compartilhamento através de um link.

---

## Requerimentos

* Python 3.7
* MySQL
* Firefox/Chrome

OBS: Caso não seja possível instalar em seu servidor o Firefox ou Chrome ou outro navegador, será necessário atualizar o banco de dados das 
disciplinas e turmas manualmente.

---

## Instalação

O seguinte tutorial corresponde a um sistema linux

Começe baixando o código do programa.

```
git clone https://github.com/Leinadium/gradeHoraria.git
cd gradeHoraria
```

Após isso, baixe as suas bibliotecas.

``` 
pip install -r requirements.txt
```


Instale o [servidor do MySQL](https://dev.mysql.com/downloads/mysql/).
Crie uma conta e um bando de dados `grade_horaria`. Estes serão utilizados 
pelo site para manter um banco com as disciplinas e turmas.

Edite o arquivo `instance/model_config.py`. Coloque uma `secret_key`, assim como
o acesso para o banco de dados, conforme o modelo. Renomeie o arquivo para `config.py`.

Crie um arquivo `app/scraper/credentials.json` com as credenciais para o banco de dados:

```json
{
  "user": "usuário",
  "passwd": "senha",
  "db": "grade_horaria"
}
```

#### Caso tenha Firefox:

Baixe o [geckodriver](https://github.com/mozilla/geckodriver/releases) do Firefox. É recomendada a versão 0.27 Mova
para o diretório `app/scraper/driver/`.

Verifique se o nome do arquivo corresponde com o nome dentro do código do arquivo `app/scraper/scraper.py`.

`PATH_TO_DRIVER = path.join(SRCPATH, 'driver', 'geckodriver27.exe`

Por ultimo, altere a variavel `SELENIUM_SOURCE` para "firefox".

#### Caso tenha Chrome (ou Chromium para linux):

Baixe as bibliotecas para o chromedriver:

```shell
sudo apt-get update
sudo apt-get install chromedriver
```

Veja o local onde foi instalado o chromedriver:

`whereis chromedriver`

No arquivo `app/scraper/scraper.py`, altere a variável `PATH_TO_DRIVER_PI` com o caminho para o driver.

Por ultimo, altere a variavel `SELENIUM_SOURCE` para "chrome". 

#### Iniciando o banco de dados

Crie os modelos no banco de dados.
```shell
set FLASK_APP=run.py
set FLASK_CONFIG=development
flask db init
flask db migrate
flask db upgrade
```

Popule o banco de dados.
```python
from app import scraper
scraper.run()
scraper.update_database()
```

#### Iniciando o servidor

Para iniciar o servidor localmente:
```shell
set FLASK_APP=run.py
set FLASK_CONFIG=production
flask run
```

### Para fazer um deploy

Para fazer um deploy, não é recomendado utilizar o `flask run`. Por isso, será necessário usar o *gunicorn*

```
pip install gunicorn
```

Crie um serviço no linux.

```
cd /etc/systemd/system
sudo nano gradeHoraria.service
```

Digite o seguinte serviço no arquivo

```
[Unit]
Description=Gunicorn instance of GradeHoraria
After=network.target

[Service]
User=pi
Group=www-data
WorkingDirectory=/PATH/TO/YOUR/APP
Environment="PATH=/PATH/TO/YOUR/APP/venv/bin"
ExecStart=/PATH/TO/YOUR/APP/venv/bin/gunicorn --timeout 300 --workers 3 --bind 0.0.0.0:5000 -m 007 "run_gunicorn:create_app('production')"

[Install]
WantedBy=multi-user.target
```

Para rodar o serviço por trás:
```
sudo systemctl daemon-reload
sudo systemctl start gradeHoraria
sudo systemctl status gradeHoraria
```

---
### Alternativa ao *Selenium* (caso não tenha Firefox/Chrome)
O Selenium é utilizado para coletar as turmas fornecidas em *[puc-rio.br/microhorario]()*.
O script de atualização é executado durante a noite automaticamente, mas pode ser desligado editando o arquivo
`app/__init__.py`, desabilitando o *APScheduler*.

---

### Créditos:

**Tutorial**: [Build a CRUD web app with python and flask](https://www.digitalocean.com/community/tutorials/build-a-crud-web-app-with-python-and-flask-part-one)

**HTML Template**: [Cover Template](https://getbootstrap.com/docs/5.0/examples/cover/#)

**Javascript**: [SelectPure](https://www.cssscript.com/multi-select-autocomplete-selectpure/)