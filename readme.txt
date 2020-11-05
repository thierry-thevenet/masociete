
"""

git pull https://github.com/thierrythevenet1963/masociete.git

cette aplication cliente (main.py) est un server en 127.0.0.1:4000 qui echange avec le serveur d API de talao.co  (qui doit tourner en local)

faire tourner en local le serveur talao.co a l'addresse 127.0.0.1:3000
update de  la variable d environment upload_path

l issuer est toujours "masociete"

pour changer le contenu d'un certificat regarder le code sous la vue '/issue_agreement'

les vues sont à la fin du code


Utilisation
************
$ export MYENV=airbox
$ python main.py

on emet un certificat en appelant  une url sur le seveur l'application client, on a en retour un json qui s affiche 

pour creer un certificat agreement :
http://127.0.0.1:4000/issue_agreement

pour creer un certificat reference
http://127.0.0.1:4000/issue_reference


"""