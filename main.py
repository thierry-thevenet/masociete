
"""

git pull https://github.com/thierrythevenet1963/masociete.git

cette aplication cliente (main.py) est un server en 127.0.0.1:4000 qui echange avec le serveur d API de talao.co  (qui doit tourner en local)

faire tourner en local le serveur talao.co a l'addresse 127.0.0.1:3000
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
import jwt


filename = './talao_rsa_publickey.pem'
try :
	fp = open(filename,"r")
	talao_public_rsa_key = fp.read()
	fp.close()
except :
    print('RSA public key of API Server not found')

# Environment variables set in gunicornconf.py  and transfered to environment.py
myenv = os.getenv('MYENV')

version = '0.5'
app = Flask(__name__)
app.secret_key = 'ùmkljùmkjagzklj'


url_callback = 'http://127.0.0.1:4000/callback'
talao_url = 'http://127.0.0.1:3000'
upload_path = '/home/thierry/Talao/uploads/'
client_id = 'iPSoIWDI4shQ0dEG86ZpSFdj'
client_secret = '68R8QzaaTigNcISRHSymdZb9D53YfaM2AOm8HnULg1ILvrIl'
post_logout = 'http://1227.0.0.1:4000/post_logout',




if myenv == 'aws' :
    url_callback = 'http://masociete.co/callback'
    talao_url = 'https://talao.co'
    upload_path = '/home/admin/masociete/'
    client_id = 'JrUy80uksqpJ5cmA5YY6Re8P'
    client_secret = 'fEpPyVXZsguFsjhQaD118q7WUEbvv8jlDhoFPoKMMpJpEbzR'
    post_logout = 'http://masociete.co/post_logout',

# Talao as an OAuth2 Identity Provider
talao_url_authorize = talao_url + '/api/v1/authorize'
talao_url_token = talao_url + '/api/v1/oauth/token'
talao_url_userinfo = talao_url + '/api/v1/user_info'
talao_url_logout = talao_url + '/api/v1/oauth_logout'


# home page local avec affichage du did et choix du test
@app.route('/', methods=['GET', 'POST'])
def login() :
    if request.method == 'GET':
        html = """<html lang="en">
			<body>
				<h1>Website de Ma Société</h1>
                <h2>Our Decentralized IDentifiers is : </h2>
                <p>
                    <li><b>did:talao:talaonet:c5C1B070b46138AC3079cD9Bce10010d6e1fCD8D</b></li>
                </p>
                <form method="post" action="/" class="inline">
                <input type="hidden" name="parametre">

                <button type="submit" name="button" value="sso" class="link-button">
                <b>Connect to this application with Talao Connect</b></button>
                <br><br>
                <button type="submit" name="button" value="user_accepts_company_referent" class="link-button">
                <b>Endpoint user_accepts_company_referent</b></button>
                <br><br>
                <button type="submit" name="button" value="user_adds_referent" class="link-button">
                <b>Endpoint user_adds_referent</b></button>
                <br><br>
                <button type="submit" name="button" value="user_issues_certificate" class="link-button">
                <b>Endpoint user_issues_certificate</b></button>

                <br><br>
                <button type="submit" name="button" value="user_updates_company_settings" class="link-button">
                <b>Endpoint user_updates_company_settings</b></button>

                 <br><br>
                <button type="submit" name="button" value="user_uploads_signature" class="link-button">
                <b>Endpoint user_uploads_signature</b></button>

                </form>
                <br>
                <a href="http://127.0.0.1:3000/create_company_cci/"> Lien vers la page CCI (locale)</a><br>
                <a href="https://talao.co/create_company_cci/"> Lien vers la page CCI (AWS)</a>
			</body>
		    </html>"""
        #return render_template_string(html)
        return render_template('index.html')

    if request.method == 'POST':
        input = request.form['button']
        if input == 'sso' :
            return redirect('/sso')
        elif input == 'user_accepts_company_referent' :
            return redirect('/user_accepts_company_referent')
        elif input == 'user_adds_referent' :
            return redirect('/user_adds_referent')
        elif input == 'user_issues_certificate' :
            return redirect('/user_issues_certificate')
        elif input == 'user_updates_company_settings' :
            return redirect('/user_updates_company_settings')
        elif input == 'user_uploads_signature' :
            return redirect('/user_uploads_signature')


# call du logout de oauth 2.0/OIDC
@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        id_token = session['id_token']
        data = {
        'id_token_hint': id_token,
        'state': 'test',
        'post_logout_redirect_uri': post_logout,
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

# This is the DID proof (on_line_checking)
@app.route('/did/', methods=['GET', 'POST'])
def did_check () :
    if request.method == 'GET' :
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
    if request.method == 'POST' :
        print('code reçu et renvoyé pour DID proof = ', request.form.get('code'))
        return jsonify({"code" : request.form.get('code')}), 200


###############" TEST des API Authorization code flow ##################"

 #test de Openid connect flow, login  de l application locale avec redirection sur le login Talao.co par OpenId Connect (scope openid)
@app.route('/sso', methods=['GET', 'POST'])
def root():
    data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': str(random.randint(0, 99999)),
            'nonce' :  'test2' + str(random.randint(0, 99999)),
            'redirect_uri': url_callback,
            'scope': 'openid email address resume profile',
        }
    session['state'] = data['state']
    session['endpoint'] = 'user_info'
    print('step 1 : demande d autorisation envoyée ')
    return redirect(talao_url_authorize + '?' + urlencode(data))

 #test de user_accepts_company_referent avec redirection sur le login Talao.co
@app.route('/user_accepts_company_referent', methods=['GET', 'POST'])
def root_2():
    data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': str(random.randint(0, 99999)),
            'nonce' : 'test',
            'redirect_uri': url_callback,
            'scope': 'user:manage:referent',
        }
    session['state'] = data['state']
    session['endpoint'] = 'user_accepts_company_referent'
    print('step 1 : demande d autorisation envoyée ')
    return redirect(talao_url_authorize + '?' + urlencode(data))


#test de user_adds_referent avec redirection sur le login Talao.co
@app.route('/user_adds_referent', methods=['GET', 'POST'])
def root_3():
    data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': str(random.randint(0, 99999)),
            'nonce' : 'test',
            'redirect_uri': url_callback,
            'scope': 'user:manage:referent',
        }
    session['state'] = data['state']
    session['endpoint'] = 'user_adds_referent'
    print('step 1 : demande d autorisation envoyée ')
    return redirect(talao_url_authorize + '?' + urlencode(data))


 #test de user_issues_certificate avec redirection sur le login Talao.co
@app.route('/user_issues_certificate', methods=['GET', 'POST'])
def root_4():
    data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': str(random.randint(0, 99999)),
            'nonce' : 'test',
            'redirect_uri': url_callback,
            'scope': 'user:manage:certificate',
        }
    session['state'] = data['state']
    session['endpoint'] = 'user_issues_certificate'
    print('step 1 : demande d autorisation envoyée ')
    return redirect(talao_url_authorize + '?' + urlencode(data))


 #test de user_updates_company_settings
@app.route('/user_updates_company_settings', methods=['GET', 'POST'])
def root_5():
    data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': str(random.randint(0, 99999)),
            'nonce' : 'test',
            'redirect_uri': url_callback,
            'scope': 'user:manage:data',
        }
    session['state'] = data['state']
    session['endpoint'] = 'user_updates_company_settings'
    print('step 1 : demande d autorisation envoyée ')
    return redirect(talao_url_authorize + '?' + urlencode(data))

 #test de user_uploads signature
@app.route('/user_uploads_signature', methods=['GET', 'POST'])
def root_6():
    data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': str(random.randint(0, 99999)),
            'nonce' : 'test',
            'redirect_uri': url_callback,
            'scope': 'user:manage:data',
        }
    session['state'] = data['state']
    session['endpoint'] = 'user_uploads_signature'
    print('step 1 : demande d autorisation envoyée ')
    return redirect(talao_url_authorize + '?' + urlencode(data))


 # Callback avec call sur les endpoints précédents
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
        #print('Refresh Token = ',token_data.get('refresh_token'))
        session['id_token'] = token_data.get('id_token')

        # decryptage  du JWT et verification de la signature avec la cle RSA publique de Talao
        if token_data.get('id_token') :
            try :
                JWT = jwt.decode(token_data.get('id_token'),talao_public_rsa_key, algorithms='RS256', audience=client_id)
                print('JWT = ', JWT)
            except Exception as e : # echec verification de la signature
                print(e)

        # appel du endpoint selon la variable endpoint
        headers = {'Authorization': 'Bearer %s' % token_data['access_token']}

        if session['endpoint'] == 'user_accepts_company_referent' :
            endpoint_response = requests.post('http://127.0.0.1:3000/api/v1/user_accepts_company_referent', headers=headers)

        elif session['endpoint'] == 'user_info' : #OIDC standard call
            endpoint_response = requests.get(talao_url_userinfo, headers=headers)

        elif session['endpoint'] == 'user_issues_certificate' :
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

        elif session['endpoint'] == 'user_adds_referent' :
            # talao est ajouté comme referent a thierrythevenet Talao workspace contract = 0x4562DB03D8b84C5B10FfCDBa6a7A509FF0Cdcc68
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
            data = {'did_referent' : 'did:talao:talaonet:4562DB03D8b84C5B10FfCDBa6a7A509FF0Cdcc68'}
            endpoint_response = requests.post(talao_url + '/api/v1/user_adds_referent', data=json.dumps(data), headers=headers)

        elif session['endpoint'] == 'user_updates_company_settings' :
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
            data = {'staff' : "6"}
            endpoint_response = requests.post(talao_url + '/api/v1/user_updates_company_settings', data=json.dumps(data), headers=headers)

        elif session['endpoint'] == 'user_uploads_signature' :
            headers = {'Authorization': 'Bearer %s' % token_data['access_token']}
            signature = {'image': open('signature.png', 'rb')}
            endpoint_response = requests.post(talao_url + '/api/v1/user_uploads_signature', files=signature, headers=headers)

        print('step 3 call du endpoint envoyé')
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <body>
        <h2>Vous etes maintenant connecté au site Web de Ma Societe.</h2>
        <h3> Data reçue depuis votre Identité Numérique : </h3>
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
    print('response.status_code = ', response.status_code)
    flash('Identity not found !', 'danger')
    return redirect('/')



###############" TEST des API Client Credentials flow ##################"

# test de client credentials pour creer l'identité d une personne
@app.route('/create_person_identity', methods=['GET', 'POST'])
def create_person_identity():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': "",
        'scope' : 'client:create:identity'
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande de token envoyée')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 demande envoyée')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        data = {'firstname' : 'pierre', 'lastname' : 'Dupont', 'email' : 'pierre.dupont@talao.co', 'send_email' : False} # no email"
        response = requests.post(talao_url + '/api/v1/create_person_identity', data=json.dumps(data), headers=headers)
        return response.json()
    return 'demande de tokens refusée pour creer une identité'


# test de client credentials pour creer l'identité d une company
@app.route('/create_company_identity', methods=['GET', 'POST'])
def create_company_identity():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': "",
        'scope' : 'client:create:identity'
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande de token envoyée')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 demande envoyée')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        data = {'name' : 'companytest4', 'email' : 'pierre.dupont@talao.co'} # with email
        response = requests.post(talao_url + '/api/v1/create_company_identity', data=json.dumps(data), headers=headers)
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
        'scope' : 'client:issue:experience'
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 1 : demande de token envoyée')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 2 demande envoyée sur final endpoint ')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        certificate = {
	    "title" : "Test : Développement d'un provider OpenID Connect",
	    "description" : "Conception et réalisation d'une application de gestion d'identité numérique sur la blockchain.",
	    "start_date" : "2020-02-15",
	    "end_date" : "2020-10-25",
	    "skills" : ["Python", "Flask", "Oauth 2.0", "IODC"],
	    "score_recommendation" : 4,
	    "score_delivery" : 4,
	    "score_schedule" : 4,
	    "score_communication" : 4,
	    }
        # 0x81d8800eDC8f309ccb21472d429e039E0d9C79bB Thierrythevenet
        data = {'did' : 'did:talao:talaonet:81d8800eDC8f309ccb21472d429e039E0d9C79bB', 'certificate' : certificate}
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
        'scope' : 'client:issue:agreement'
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
        'scope' : 'client:issue:reference'
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande de token envoyée')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 demande envoyée sur final endpoint ')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        certificate = {
            "title" : "Prototypage d'un objet connecté",
            "description" : "Conception et prototypage",
            "budget" : "95000",
            "staff" : "3",
            "location" : "Paris",
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
        data = {'did' : 'did:talao:talaonet:81d8800eDC8f309ccb21472d429e039E0d9C79bB', 'certificate_type' : 'all'}
        response = requests.post(talao_url + '/api/v1/get_certificate_list', data=json.dumps(data), headers=headers)
        return response.json()
    return 'demande de tokens refusée pour obtenir le status'



# test de client credentials pour obtenir un certificat
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


