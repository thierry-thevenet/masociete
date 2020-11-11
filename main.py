
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



# workspace contract de newindus = 0x5aE452b6fD5d77dB83F7c617299b6DA88abA915D
# talao workspac contract 0x4562DB03D8b84C5B10FfCDBa6a7A509FF0Cdcc68
# wc de newco =  0xC15e3A2f17cD01c5A85F816165c455D9F954cBa9
# mettre dessous l'adresse du  destinataire du certificat dans {"did" :xxxx
# TT wc 0x81d8800eDC8f309ccb21472d429e039E0d9C79bB

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

# public RSA key to check JWT (OpenID Connect)
filename = "oauth_RSA_public.txt"
try :
    fp = open(filename,"rb")
    rsa_key = fp.read()
    fp.close()
except :
    print('JWT private RSA key not found')

version = '0.4.1'
app = Flask(__name__)
app.secret_key = 'ùmkljùmkjagzklj'


# variables d'environment
if myenv == 'airbox-masociete' :
    url_callback = 'http://127.0.0.1:4000/callback'
    talao_url = 'http://127.0.0.1:3000'
    upload_path = '/home/thierry/Talao/uploads/'
    client_id = 'iPSoIWDI4shQ0dEG86ZpSFdj'
    client_secret = '68R8QzaaTigNcISRHSymdZb9D53YfaM2AOm8HnULg1ILvrIl'

elif myenv == 'airbox-newco' :
    url_callback = 'http://127.0.0.1:4000/callback'
    talao_url = 'http://127.0.0.1:3000'
    upload_path = '/home/thierry/Talao/uploads/'
    client_id = 'DXfJZvRXdmudrbINyYrp1QnB'
    client_secret = 'k9cENAebOwCoG2tMsNEIP5NZWYWWmNSHyWtMmLpAIYfBXLAT'

elif myenv == 'airbox-talao' :
    url_callback = 'http://127.0.0.1:4000/callback'
    talao_url = 'http://127.0.0.1:3000'
    upload_path = '/home/thierry/Talao/uploads/'
    client_id = 'w64Jp7ZtCpk23QyjfUnklYsj'
    client_secret = 'l71TC4j5bVZL5vVCIks95qiTVGS5BTqyRYGp0s74V8XEDRuB'

elif myenv == 'aws' :
    url_callback = 'http://masociete.co/callback'
    talao_url = 'https://talao.co'
    upload_path = '/home/admin/masociete/'
    client_id = 'EmiMhjC1gjNVMu7Sek6Hq0Gs'
    client_secret = '4O9qKnKWVU2dFlmM0eRWvR0SkBT2gndgt0G2o9HDXzKtjqXZ'

else :
    print('erreur MYENV')
    exit()

# Talao as an OAuth2 Identity Provider
talao_url_authorize = talao_url + '/api/v1/authorize'
talao_url_token = talao_url + '/api/v1/oauth/token'
talao_url_userinfo = talao_url + '/api/v1/user_info'
talao_url_logout = talao_url + '/api/v1/oauth_logout'



# home page local
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


# call du logout de oauth 2.0/OIDC
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

# logout local de l appli
@app.route('/post_logout', methods=['POST', 'GET'])
def post_logout() :
    session.clear()
    return 'Game over !!!'

# update du logo pour le sso
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

###############" TEST des API Authorization code flow ##################"

 #test de Openid connect flow, login  de l application locale avec redirection sur le login Talao.co par OpenId Connect (scope openid)
@app.route('/sso', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': str(random.randint(0, 99999)),
            'nonce' :  'test',
            'redirect_uri': url_callback,
            'scope': 'profile openid resume birthdate email phone',
        }
        session['state'] = data['state']
        session['scope'] = 'user_info'

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

 #test de user_accepts_company_referent avec redirection sur le login Talao.co
@app.route('/user_accepts_company_referent', methods=['GET', 'POST'])
def root_2():
    if request.method == 'POST':
        data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': str(random.randint(0, 99999)),
            'nonce' : 'test',
            'redirect_uri': url_callback,
            'scope': 'user_manages_referent',
        }
        session['state'] = data['state']
        session['scope'] = data['scope']
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


 #test de user_issues_certificate avec redirection sur le login Talao.co
@app.route('/user_issues_certificate', methods=['GET', 'POST'])
def root_3():
    if request.method == 'POST':
        data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': str(random.randint(0, 99999)),
            'nonce' : 'test',
            'redirect_uri': url_callback,
            'scope': 'user_issues_certificate',
        }
        session['state'] = data['state']
        session['scope'] = data['scope']
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

 # Callback avec call sur les 2 endpoints précédents
@app.route('/callback', methods=['GET', 'POST'])
def talao():
    print('request reçu dans /callback = ', request.args)
    code = request.args.get('code')
    if request.args.get('state') != session['state'] :
        print('probleme state/CSRF')
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
        # appel du endpoint selon la variable state
        params = {'schema': 'oauth2'}
        headers = {'Authorization': 'Bearer %s' % token_data['access_token']}
        if session['scope'] == 'user_manages_referent' :
            endpoint_response = requests.get('http://127.0.0.1:3000/api/v1/user_accepts_company_referent', params=params, headers=headers)
        elif session['scope'] == 'user_info' :
            # decryptage  du JWT
            print('JWT = ', jwt.decode(token_data.get('id_token'), rsa_key, algorithms=['RS256'], audience=client_id))
            # cell du endpoint
            endpoint_response = requests.get(talao_url_userinfo, params=params, headers=headers)
        elif session['scope'] == 'user_issues_certificate' :
        # talao emet un certificat a thierrythevenet workspace contract = 0x81d8800eDC8f309ccb21472d429e039E0d9C79bB
        # talao est dans la referent list de thierrythevenet
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
            certificate = {
	                "registration_number" : "2020-11-75012",
	                "title" : "IQ - ISO9001:2020",
	                "description" : "Quality Management Process",
                    "standard" : "ISO 9001",
	                "date_of_issue" : "2020-11-01",
	                "valid_until" : "2030-10-31",
	                "location" : "Toulouse Bordeaux Paris",
	                "service_product_group" : "Drone Serie production line",
	                }
            data = {'did_issued_to' : 'did:talao:talaonet:81d8800eDC8f309ccb21472d429e039E0d9C79bB', 'certificate_type' : 'agreement', 'certificate' : certificate}
            endpoint_response = requests.post(talao_url + '/api/v1/user_issues_certificate', data=json.dumps(data), headers=headers)
        print('step 3 call du endpoint envoyé')

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <body>
        <h2>Vous etes maintenant connecté au site Web de Ma Societe.</h2>
        <h3> Data received from your Decentralized ID : </h3>
        <p>
        {% for key, value in endpoint_response.json().items() %}
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
        return render_template_string(html, endpoint_response=endpoint_response)
    print('demande access token/ id token  refusée')
    return 'User did not accept your access, demande access token/ id token  refusée'




###############" TEST des API Client Credentials flow ##################"

# test de client credentials pour creer une identité
@app.route('/create_person_identity', methods=['GET', 'POST'])
def create_person_identity():
    print('my env = ', myenv)
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


# test de client credentials pour obtenir le status
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


# test de client credentials pour emettre un certificat d experience
@app.route('/issue_experience', methods=['GET', 'POST'])
def issue_experience():
    print('my env = ', myenv)
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
        response = requests.post(talao_url + '/api/v1/issue_experience', data=json.dumps(data), headers=headers)
        return response.json()
    print('demande de token refusée')
    print('response : ', response.__dict__)
    return 'Demande de token refusée pour creer un certificat d experience'


# test de client credentials pour emettre un certificat d agrement a une entreprise
@app.route('/issue_agreement', methods=['GET', 'POST'])
def issue_agreement():
    print('my env = ', myenv)
    print('client id =  ', client_id)
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
	        "registration_number" : "2020-11-31003",
	        "title" : "IQ - ISO9001:2020",
	        "description" : "Quality Management Process",
            "standard" : "ISO 9001",
	        "date_of_issue" : "2020-11-01",
	        "valid_until" : "2030-10-31",
	        "location" : "Toulouse Bordeaux Paris",
	        "service_product_group" : "Drone Serie production line",
	    }
        data = {'did' : 'did:talao:talaonet:5aE452b6fD5d77dB83F7c617299b6DA88abA915D', 'certificate' : certificate}
        response = requests.post(talao_url + '/api/v1/issue_agreement', data=json.dumps(data), headers=headers)
        return response.json()
    print('demande de token refusée')
    print('response : ', response.__dict__)
    return 'Demande de token refusée pour creer un certificat d agrement'


# talao workspace contract 0x4562DB03D8b84C5B10FfCDBa6a7A509FF0Cdcc68
# workspace contract de newco =  0xC15e3A2f17cD01c5A85F816165c455D9F954cBa9
# workspace contract de newindus = 0x5aE452b6fD5d77dB83F7c617299b6DA88abA915D
# mettre dessous l'adresse du  destinataire du certificat dans {"did" :xxxx


# test de client credentials pour emettre un certificat de reference
@app.route('/issue_reference', methods=['GET', 'POST'])
def issue_reference():
    print('client id =  ', client_id)
    print('my env = ', myenv)
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
            "project_title" : "Prototypage d'un objet connecté",
            "project_description" : "Conception et prototypage",
            "project_budget" : "95000",
            "project_staff" : "3",
            "project_location" : "Paris",
            "start_date" : "2020-09-01",
            "end_date" : "2020-10-31",
            "competencies" : [],
            "score_recommendation" : 4,
            "score_delivery" : 4,
            "score_schedule" : 4,
            "score_communication" : 4,
            "score_budget" : 4,
        }
        data = {'did' : 'did:talao:talaonet:5aE452b6fD5d77dB83F7c617299b6DA88abA915D', 'certificate' : certificate}
        response = requests.post(talao_url + '/api/v1/issue_reference', data=json.dumps(data), headers=headers)
        return response.json()
    print('demande de token refusée')
    print('response : ', response.__dict__)
    return 'Demande de token refusée pour creer un certificat de reference'

# workspace contract de newindus = 0x5aE452b6fD5d77dB83F7c617299b6DA88abA915D
# talao workspac contract 0x4562DB03D8b84C5B10FfCDBa6a7A509FF0Cdcc68
# wc de newco =  0xC15e3A2f17cD01c5A85F816165c455D9F954cBa9
# mettre dessous l'adresse du  destinataire du certificat dans {"did" :xxxx
# TT wc 0x81d8800eDC8f309ccb21472d429e039E0d9C79bB


# test de client credentials pour obtenir une liste de certificat
@app.route('/get_certificate_list', methods=['GET', 'POST'])
def get_certificate_list():
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
        #did de newindus = did:talao:talaonet:5aE452b6fD5d77dB83F7c617299b6DA88abA915D
        data = {'did' : 'did:talao:talaonet:5aE452b6fD5d77dB83F7c617299b6DA88abA915D', 'certificate_type' : 'reference'}
        response = requests.post(talao_url + '/api/v1/get_certificate_list', data=json.dumps(data), headers=headers)
        return response.json()
    return 'demande de tokens refusée pour obtenir le status'



# test de client credentials pour obtenir une liste de certificat
@app.route('/get_certificate', methods=['GET', 'POST'])
def get_certificate():
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
        #did de newindus = did:talao:talaonet:5aE452b6fD5d77dB83F7c617299b6DA88abA915D
        data = {'certificate_id' : 'did:talao:talaonet:81d8800eDC8f309ccb21472d429e039E0d9C79bB:document:12'}
        response = requests.post(talao_url + '/api/v1/get_certificate', data=json.dumps(data), headers=headers)
        return response.json()
    return 'demande de tokens refusée pour obtenir le status'




# 127.0.0.1:4000
if __name__ == '__main__':
    app.run( port=4000, debug =True)


