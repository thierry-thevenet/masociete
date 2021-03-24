
"""

git pull https://github.com/thierrythevenet1963/masociete.git

cette aplication cliente (main.py) est un server en 127.0.0.1:4000 qui echange avec le serveur d API de talao.co  (qui doit tourner en local)

faire tourner en local le serveur OIDC_DID a l'addresse 127.0.0.1:8000
update de  la variable d environment upload_path

l issuer est toujours "masociete"
pour changer le contenu d'un certificat regarder le code sous la vue '/issue_agreement'
les vues sont à la fin du code
on emet un certificat en appelant  une url sur le seveur l'application client, on a en retour un json qui s affiche 

# workspace contract de newindus = 0x5aE452b6fD5d77dB83F7c617299b6DA88abA915D
# talao workspac contract 0x4562DB03D8b84C5B10FfCDBa6a7A509FF0Cdcc68
# wc de newco =  0xC15e3A2f17cD01c5A85F816165c455D9F954cBa9
# mettre dessous l'adresse du  destinataire du certificat dans {"did" :xxxx
# TT wc 0x81d8800eDC8f309ccb21472d429e039E0d9C79bB

"""

from urllib.parse import urlencode
import requests
from flask import Flask, redirect, request, render_template_string, session, send_from_directory, jsonify, render_template, flash
import json
import os
import random
import jwt #https://pyjwt.readthedocs.io/en/stable/
from eth_account.messages import encode_defunct
from eth_account import Account
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

#for demo only
client_private_rsa_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA16beMp//Gb7xuPpcIp9GWxEQLCwleBfHNHs4xG5w/h3njYF4
QdF9o/NA5neTzAhO+ks1SzhpmIx4tTM56hfdiU6st4TP2nPbeUITdPK3i7rJeTYt
AfZV5MNdBp0r0rIIf+KhjN24MCDUQJrlfbWQuCmy4E9Tv5kSANv+Ls3e+Yiw08CA
VGOv5mN/81FRf9Dovg6r91ftepOow2MwfxiX3llaf9hCxdOr8591L82d+7HRGlA1
mCyR0/tsWtLa9XCj4KdINMhErYZH+oeVSq901AOHvZ6GumaFUbkGOVIunMrfhNSO
bUmaUqWXoKzJCV0EAtlFYVF3XgDeTGMPagE0pwIDAQABAoIBADrZfkSJdge0HGny
5IbMOVprryKmz3jU4FdZkxXD39DxHzn2DXfEsAk4PktGcY5Z7BeQw5Pp6qMnHl+w
gYr5BUtNrYONWl2OhWOzXPTqsZ0PlaCe4Kxq6Wi6yZ2e8ZEXZYtksNpsvTFhHBsf
SiZCkKI5OufMrhmYr5mNb3GdW85zdu6SGr+8XMpwVPnmVw8b9r5lVX57nDMVFQzm
vpauhszth5TWQx0V8FhWQQjtR604Sx3urrM5lzk7JtNACa3Sas0T0tpinKObCcFX
j++ilKkshVMShOZcdT/dZuUkhUSB+qx/ra5+yR4HXOpWwWoeKN6LthmOFDcpsYN6
+J3pMeUCgYEA3B6j7V6cQrFQ6qkfwYTktDuEvxBpqdJE2atRkIb6nFlKsnLD5i0r
8QRt8DpQqauhIClHFp0ppCXAG4ti5m3SV+GUZzhabMTzagpvKgIw+ddujXkQwiUC
kGyNll2nBOaaENKmnQpS3IhIa3MO1+RkmDKrYfHWVocvPXcXYp7iVasCgYEA+s3J
3rSMVnU70OlpYXeiOZYVYb5Iz/87sMxsAt+S8WooCQCQalGKycRV76rxbSxx76fJ
R0L6egouD14mi+cvU0ScFl4NMca5vSG5ke99KpwH62w6OzwO8ZsBnVrOsRYrjTH0
xRp/01t3ShWlRjjPAr63BbTqfOWI965rNvKHqPUCgYEA0QMvOTf7PMDOSuRoyQL9
f758YEifbKfCxMWOX6Qr18ZZzXR4W9pMvUEte0yER3g3OSi43dpCLiHCduU19gQW
FWiX2COEiX/CetCJmeQWyUYtLZzlstQdyTGqiDtJWrf1V0APAVNKNyoZSh4o3At9
EaAbaJeQpP0ceErbI8Qmup0CgYBwEyHQeVH1GLJAKu3Cdllx7lVjtkqHWADugosJ
xaq+Yre9PhlKyWGBxFC6puL37FKFy66wP4f6nS30BBipkAef6BrwC9tNkQZTNAze
3+xI7CzF0Tk8Wxw6bxALpxaSH9waXmaI5cyVQFxQKNgQRzaKfXr/+9aFNXU9aR3U
EhD5OQKBgBmsOHN1UkmKIkvybdIb86oci/Rcj6u2ZgiV01mjtkeJjHOK4gD6ZhHp
ikxEdmAkFno7I5AP1fSd9qDSmNR3w7/RfpLlK5rVhRuEBzxXLIiA+NrZCvGfWlOn
GVOlCU5+3ZuRb/JHRjN+aaylhzAdCWeAH/iWOKdeWZ2kuud243+n
-----END RSA PRIVATE KEY-----"""

client_private_key = "0xfabc26253be62915e21981951f0a46cc58ae474a29d490413d9878371a10e47a"
client_did = 'did:talao:talaonet:c5C1B070b46138AC3079cD9Bce10010d6e1fCD8D'
client_address = '0x194d92A8798c14Dc59080aF4Baf4588140F34F49'

filename = './talao_rsa_publickey.pem'
try :
	fp = open(filename,"r")
	talao_public_rsa_key = fp.read()
	fp.close()
except :
    print('RSA public key of API Server not found')

# Environment variables set in gunicornconf.py  and transfered to environment.py
myenv = os.getenv('MYENV')

version = '0.7'
app = Flask(__name__)
app.secret_key = 'ùmkljùmkjagzklj'


url_callback = 'http://127.0.0.1:4000/callback'
talao_url = 'http://127.0.0.1:8000'
upload_path = '/home/thierry/Talao/uploads/'
client_id = 'iPSoIWDI4shQ0dEG86ZpSFdj'
client_secret = '68R8QzaaTigNcISRHSymdZb9D53YfaM2AOm8HnULg1ILvrIl'
post_logout_uri = 'http://127.0.0.1:4000/post_logout'

# http://127.0.0.1:8000/api/v1/authorize?response_type=id_token&client_id=iPSoIWDI4shQ0dEG86ZpSFdj&scope=openid+profile&state=state&nonce=nonce



if myenv == 'aws' :
    url_callback = 'http://masociete.co/callback'
    talao_url = 'https://talao.co'
    upload_path = '/home/admin/masociete/'
    client_id = 'JrUy80uksqpJ5cmA5YY6Re8P'
    client_secret = 'fEpPyVXZsguFsjhQaD118q7WUEbvv8jlDhoFPoKMMpJpEbzR'
    post_logout_uri = 'http://masociete.co/post_logout'

# Talao as an OIDC Provider
talao_url_authorize = talao_url + '/api/v1/authorize'
talao_url_token = talao_url + '/api/v1/oauth/token'
talao_url_userinfo = talao_url + '/api/v1/user_info'
talao_url_logout = talao_url + '/api/v1/oauth_logout'


def dict_to_b64(mydict) : 
    token_str = json.dumps(mydict)
    token_bytes = token_str.encode()
    token_b64 = b64encode(token_bytes)
    token = token_b64.decode()
    return token

def b64_to_dict(myb64) :
    rtoken_b64 = myb64.encode()
    rtoken_bytes = b64decode(rtoken_b64)
    rtoken_str = rtoken_bytes.decode()
    return json.loads(rtoken_str)


# website homepage
@app.route('/', methods=['GET', 'POST'])
def login() :
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        input = request.form['button']
        if input == 'fc' :
            data = {
                'response_type': 'code',
                'client_id': client_id,
                'state': str(random.randint(0, 99999)),
                'nonce' :  str(random.randint(10000, 999999)), 
                'redirect_uri': url_callback,
                'scope': 'openid did_authn',
                'client_did' : client_did
            }
            session['flow'] = 'authorization_code'
            # data request is signed by client with its ECDSA key. Signature is added to data request
            canonical_message = data['nonce'] + data['client_did']
            msg = encode_defunct(text=canonical_message)
            data['signature'] = Account.sign_message(msg, client_private_key).signature.hex()

            session['state'] = data['state']

        print('step 1 : demande d autorisation envoyée '+ session['flow'])
        return redirect(talao_url_authorize + '?' + urlencode(data))

# call du logout de oauth 2.0/OIDC
@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        id_token = session.get('id_token')
        data = {
        'id_token_hint': id_token,
        'state': session['state'],
        'post_logout_redirect_uri': post_logout_uri,
        }
        return redirect(talao_url_logout + '?' + urlencode(data))

# logout local de l appli
@app.route('/post_logout', methods=['POST', 'GET'])
def post_logout() :
    session.clear()
    print('Game over !!!')
    return redirect('/')

# update du logo pour le sso
@app.route('/uploads/<filename>')
def send_file(filename):
	return send_from_directory(upload_path, filename)


@app.route('/callback', methods=['GET', 'POST'])
def talao():
    if 'error' in request.args :
        flash(request.args.get('error_description'), 'danger')
        return redirect('/')

    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': url_callback,
        'client_id': client_id,
        'client_secret': client_secret,
        'code': request.args.get('code'),
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande d un Access Token envoyée')

    if response.status_code == 200:
        token_data = response.json()
        session['id_token'] = token_data.get('id_token')

        # decryptage  du JWT et verification de la signature avec la cle RSA publique de Talao
        if token_data.get('id_token') :
            try :
                session['JWT'] = jwt.decode(token_data.get('id_token'),talao_public_rsa_key, algorithms='RS256', audience= 'did:talao:talaonet:4562DB03D8b84C5B10FfCDBa6a7A509FF0Cdcc68')
                print('JWT = ', session['JWT'])
            except Exception as e : # echec verification de la signature
                print(e)
                session['JWT'] = "No ID Token"

        session['credential']= session['JWT']['credential']

        # appel du endpoint selon la variable endpoint
        #headers = {'Authorization': 'Bearer %s' % token_data['access_token']}
        #endpoint_response = requests.get(talao_url_userinfo, headers=headers)
        #print('step 3 call du endpoint envoyé')
        #rep = endpoint_response.json()
        #credential = json.loads(rep['credential'])
        #print('credential = ', credential)

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <body>
        <h2>Vous etes maintenant connecté au site Web de Ma Societe.</h2>
        <h3> Data reçue depuis votre Identité Numérique : </h3>
        <p>
        <b>ID Token</b> : {{session['JWT']}}
        <br>
        <br>
        <b>Credential</b> : {{session['credential']}}
        <form method=post action="/logout" enctype=multipart/form-data>
            <button>Logout</button>
        </form>
        </p>
        </body>
        </html>
        """
        return render_template_string(html)

    print('demande access token/ id token  refusée')
    print('response.status_code = ', response.status_code)
    return redirect('/')

# 127.0.0.1:4000
if __name__ == '__main__':
    app.run( port=4000, debug =True)
