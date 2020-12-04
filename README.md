## Primera piedra backend chile gigs

Recordar:
configurar workbench local en carpeta .env
ingresar una clave jwt con m5
luego:
pipenv shell
pipenv install
pipenv run init
pipenv run migrate
pipenv run upgrade
en workbench en la tabla de roles, crear una fila respectiva para admin,dj,cliente, status dejar inicialiado en "1" -> apply
nuevamente ejecutar un migrate y upgrade. Con esto ya puedes crear cuenta en el insomia y logearte.
Con el token, crear perfil.
--
