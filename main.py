
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


from urllib.parse import urlencode
import requests
from flask import Flask, redirect, request, render_template_string, session, send_from_directory
import json
import os
import random
import jwt


# Environment variables set in gunicornconf.py  and transfered to environment.py
myenv = os.getenv('MYENV')

# public RSA key to check JWT
filename = "oauth_RSA_public.txt"
try :
    fp = open(filename,"rb")
    rsa_key = fp.read()
    fp.close()
except :
    print('JWT private RSA key not found')


version = '0.3'
app = Flask(__name__)
app.secret_key = 'ùmkljùmkjagzklj'


# variable d'environment
if myenv == 'airbox' :
    url_callback = 'http://127.0.0.1:4000/callback'
    talao_url = 'http://127.0.0.1:3000'
    upload_path = '/home/thierry/Talao/uploads/'
    client_id = 'iPSoIWDI4shQ0dEG86ZpSFdj'
    client_secret = '68R8QzaaTigNcISRHSymdZb9D53YfaM2AOm8HnULg1ILvrIl'
else :
    url_callback = 'http://masociete.co/callback'
    talao_url = 'https://talao.co'
    upload_path = '/home/admin/masociete/'
    client_id = 'EmiMhjC1gjNVMu7Sek6Hq0Gs'
    client_secret = '4O9qKnKWVU2dFlmM0eRWvR0SkBT2gndgt0G2o9HDXzKtjqXZ'

"""
client_id = 'iPSoIWDI4shQ0dEG86ZpSFdj'
client_secret = '68R8QzaaTigNcISRHSymdZb9D53YfaM2AOm8HnULg1ILvrIl'
"""


# Talao as an OAuth2 Identity Provider
talao_url_authorize = talao_url + '/api/v1/authorize'
talao_url_token = talao_url + '/api/v1/oauth/token'
talao_url_userinfo = talao_url + '/api/v1/user_info'
talao_url_logout = talao_url + '/api/v1/oauth_logout'


@app.route('/sso', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': 'test',
            'nonce' : str(random.randint(0, 99999)),
            'redirect_uri': url_callback,
            'scope': 'profile openid referent partner',
        }
        print('step 1 : demande d autorisation envoyée ')
        return redirect(talao_url_authorize + '?' + urlencode(data))

    else:
        html = """
           <!DOCTYPE html>
           <html lang="en">
           <body>
               <form method=post enctype=multipart/form-data>
                   <h3>Sign In with your Decentralized Identifier
                   <input type="image" src="/uploads/talao2.png"></h3>
               </form>
            </body>
            </html>
        """
        return render_template_string(html)

@app.route('/', methods=['GET', 'POST'])
def login() :
    html = """<html lang="en">
			<body>
				<h1>Website de Ma Société</h1>
                <h2>Our Decentralized IDentifiers is : </h2>
                <p>
                    <li><b>did:talao:talaonet:c5C1B070b46138AC3079cD9Bce10010d6e1fCD8D</b></li>
                </p>
			</body>
		</html>"""
    return render_template_string(html)


@app.route('/callback', methods=['GET', 'POST'])
def talao():
    print('request reçu dans /callback = ', request.args)
    code = request.args.get('code')
    state = request.args.get('state')
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': url_callback,
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'scope' : '' # inutile
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande d un Access Token envoyée')
    if response.status_code == 200:
        token_data = response.json()
        print('Access Token reçu = ', token_data['access_token'])
        # demande d'info sur le profil
        params = {'schema': 'oauth2'}
        headers = {'Authorization': 'Bearer %s' % token_data['access_token']}
        session['id_token'] = token_data.get('id_token')
        decoded_jwt = jwt.decode(session['id_token'], rsa_key, algorithms='RS256', audience=client_id)
        print('decoded ID token = ', decoded_jwt)

        user_info_response = requests.get(talao_url_userinfo, params=params, headers=headers)
        print('step 3 demande de userinfo envoyée')

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <body>
        <h2>Vous etes maintenant connecté au site Web de Ma Societe.</h2>
        <h3> Data received from your Decentralized ID : </h3>
        <p>
        {% for key, value in user_info_response.json().items() %}
        <div>{{key}}: {{value}}</div>
        {% endfor %}
        <br>
        <form method=post action="/logout" enctype=multipart/form-data>
            <button>Logout</button>
        </form>
        </p>
        </body>
        </html>
        """
        return render_template_string(html, user_info_response=user_info_response)
    print('demande access token/ id token  refusée')
    return 'User did not accept your access, demande access token/ id token  refusée'


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        id_token = session['id_token']
        data = {
        'id_token_hint': id_token,
        'state': 'test',
        'post_logout_redirect_uri': 'http://127.0.0.1:4000/post_logout',
        }
        return redirect(talao_url_logout + '?' + urlencode(data))

@app.route('/post_logout', methods=['POST', 'GET'])
def post_logout() :
    session.clear()
    return 'Game over !!!'

# For logo only
@app.route('/uploads/<filename>')
def send_file(filename):
	return send_from_directory(upload_path, filename)

# This is the DID proof
@app.route('/did/', methods=['GET'])
def did_check () :
	html = """<!DOCTYPE html>
		<html lang="en">
			<body>
				<h1>MaSociete.co</h1>
                <h2>Our Decentralized IDentifiers are : </h2>
                <p>
                    <li><b>did:talao:talaonet:c5C1B070b46138AC3079cD9Bce10010d6e1fCD8D</b></li>
                </p>
			</body>
		</html>"""
	return render_template_string(html)

# test de client credentials pour creer une identité
@app.route('/create_person_identity', methods=['GET', 'POST'])
def create_person_identity():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': "",
        'scope' : ''
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande de token envoyée')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 demande envoyée')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        data = {'firstname' : 'pierre', 'lastname' : 'Dupont', 'email' : 'pierre.dupont@talao.co'}
        response = requests.post(talao_url + '/api/v1/create_person_identity', data=json.dumps(data), headers=headers)
        return response.json()
    return 'demande de tokens refusée pour creer une identité'


# test de client credentials pour obteni le status
@app.route('/get_status', methods=['GET', 'POST'])
def get_status():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': "",
        'scope' : ''
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande de token envoyée')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 demande envoyée')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        data = {'did' : 'did:talao:talaonet:fA38BeA7A9b1946B645C16A99FB0eD07D168662b'}
        response = requests.post(talao_url + '/api/v1/get_status', data=json.dumps(data), headers=headers)
        return response.json()
    return 'demande de tokens refusée pour obtenir le status'

# wc de pauldupont 0xfA38BeA7A9b1946B645C16A99FB0eD07D168662b
#did de test1 did:talao:talaonet:3B4bA595955c8E783aB565a9564D0E7F14a6CaaC

# test de client credentials pour emettre un certificat
@app.route('/issue_experience', methods=['GET', 'POST'])
def issue_experience():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': '',
        'scope' : 'experience'
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 1 : demande de token envoyée')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 2 demande envoyée sur final endpoint ')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}

        certificate = {
	"title" : "Développement d'un provider OpenID Connect",
	"description" : "Conception et réalisation d'une application de gestion d'identité numérique sur la blockchain.",
	"start_date" : "2020-02-15",
	"end_date" : "2020-10-25",
	"skills" : ["Python", "Flask", "Oauth 2.0", "IODC"],
	"score_recommendation" : 4,
	"score_delivery" : 4,
	"score_schedule" : 4,
	"score_communication" : 4,
	}
        data = {'did' : 'did:talao:talaonet:fA38BeA7A9b1946B645C16A99FB0eD07D168662b', 'certificate' : certificate}
        response = requests.post(talao_url + '/api/v1/issue', data=json.dumps(data), headers=headers)
        return response.json()
    print('demande de token refusée')
    print('response : ', response.__dict__)
    return 'Demande de token refusée pour creer un certificat d experience'


# test de client credentials pour emettre un certificat d agrement
@app.route('/issue_agreement', methods=['GET', 'POST'])
def issue_agreement():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': '',
        'scope' : 'agreement'
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande de token envoyée')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 demande envoyée sur final endpoint ')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        certificate = {
	        "registration_number" : "2020-11-910151",
	        "title" : "IQ - ISO9001:2020",
	        "description" : "Quality Management Process",
            "standard" : "ISO 9001",
	        "date_of_issue" : "2020-11-01",
	        "valid_until" : "2030-10-31",
	        "location" : "Paris",
	        "service_product_group" : "3D Implementation",
	    }

# talao workspace contract 0x4562DB03D8b84C5B10FfCDBa6a7A509FF0Cdcc68
# workspace contract de newco =  0xC15e3A2f17cD01c5A85F816165c455D9F954cBa9
# workspace contract de newindus = 0x5aE452b6fD5d77dB83F7c617299b6DA88abA915D
# mettre dessous l'adresse du  destinataire du certificat dans {"did" :xxxx


        data = {'did' : 'did:talao:talaonet:5aE452b6fD5d77dB83F7c617299b6DA88abA915D', 'certificate' : certificate}
        response = requests.post(talao_url + '/api/v1/issue_agreement', data=json.dumps(data), headers=headers)
        return response.json()
    print('demande de token refusée')
    print('response : ', response.__dict__)
    return 'Demande de token refusée pour creer un certificat d agrement'



# test de client credentials pour emettre un certificat de reference
@app.route('/issue_reference', methods=['GET', 'POST'])
def issue_reference():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': '',
        'scope' : 'reference'
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande de token envoyée')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 demande envoyée sur final endpoint ')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        certificate = {
            "project_title" : "Ligne de production moteur NFG-1000",
            "project_description" : "Conception, réalisation et installation d'une nouvelle ligne de test",
            "project_budget" : "1000000",
            "project_staff" : "10",
            "project_location" : "Toulouse",
            "start_date" : "2019-02-22",
            "end_date" : "2020-01-25",
            "competencies" : ["CATIA V6",],
            "score_recommendation" : 4,
            "score_delivery" : 3,
            "score_schedule" : 4,
            "score_communication" : 4,
            "score_budget" : 4,
        }

# workspace contract de newindus = 0x5aE452b6fD5d77dB83F7c617299b6DA88abA915D
# talao workspac contract 0x4562DB03D8b84C5B10FfCDBa6a7A509FF0Cdcc68
# wc de newco =  0xC15e3A2f17cD01c5A85F816165c455D9F954cBa9
# mettre dessous l'adresse du  destinataire du certificat dans {"did" :xxxx
        data = {'did' : 'did:talao:talaonet:C15e3A2f17cD01c5A85F816165c455D9F954cBa9', 'certificate' : certificate}
        response = requests.post(talao_url + '/api/v1/issue_reference', data=json.dumps(data), headers=headers)
        return response.json()
    print('demande de token refusée')
    print('response : ', response.__dict__)
    return 'Demande de token refusée pour creer un certificat de reference'


if __name__ == '__main__':
    app.run( port=4000, debug =True)


