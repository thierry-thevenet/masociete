
from urllib.parse import urlencode
import requests
from flask import Flask, redirect, request, render_template_string, session, send_from_directory
import json
import os

# Environment variables set in gunicornconf.py  and transfered to environment.py
mychain = os.getenv('MYCHAIN')
myenv = os.getenv('MYENV')
print('environment variable : ',mychain, myenv)


version = '0.3'
app = Flask(__name__)
app.secret_key = 'ùmkljùmkjagzklj'

# environment
if myenv == 'airbox' :
    url_callback = 'http://127.0.0.1:4000/callback'
    talao_url = 'http://127.0.0.1:3000'
    upload_path = '/home/thierry/Talao/uploads/'
    client_id = 'HjoZ7fxzimmUJOCRE2fzeQcd'
    client_secret = 'yPfyFeK2mn955kPOqHdyzmsMZbznjXEokUjyPTUMrrDUR09T'
else :
    url_callback = 'http://masociete.co/callback'
    talao_url = 'https://talao.co'
    upload_path = '/home/admin/masociete/'
    client_id = 'EmiMhjC1gjNVMu7Sek6Hq0Gs'
    client_secret = '4O9qKnKWVU2dFlmM0eRWvR0SkBT2gndgt0G2o9HDXzKtjqXZ'

# Talao as an OAuth2 Identity Provider
talao_url_authorize = talao_url + '/api/v1/authorize'
talao_url_token = talao_url + '/api/v1/oauth/token'
talao_url_userinfo = talao_url + '/api/v1/user_info'
talao_url_logout = talao_url + '/api/v1/oauth_logout'

@app.route('/sign_in', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': 'test',
            'nonce': 'test',
            'redirect_uri': url_callback,
            'scope': 'profile resume birthdate phone email',
        }
        print('step 1 : demande d autorisation envoyée ')
        return redirect(talao_url_authorize + '?' + urlencode(data))

    else:
        html = """
           <!DOCTYPE html>
           <html lang="en">
           <body>
               <form method=post enctype=multipart/form-data>
                   <h3>Se connecter avec Talao Connect</h3>
                   <input type="image" src="/uploads/talao2.png">
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
    print('grant code reçu ', code)
    print('state', state)
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': url_callback,
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'scope' : '' # inutile
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande de access token envoyée')
    if response.status_code == 200:
        token_data = response.json()
        print('access token reçu = ', token_data['access_token'])
        # demande d'info sur le profil
        params = {
            'schema': 'oauth2',
        }
        headers = {
            'Authorization': 'Bearer %s' % token_data['access_token'],
        }
        session['id_token'] = token_data.get('id_token')
        print('step 3 demande de userinfo envoyée')
        user_info_response = requests.get(talao_url_userinfo, params=params, headers=headers)
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <body>
        <h2>Vous etes maintenant connecté a l'application web de Ma Societe.co </h2>
        <h3> Data received from Talao.io : </h3>
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
    return 'User did not accept your access'


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'GET':
        id_token = session['id_token']
        data = {
        'id_token_hint': id_token,
        'state': 'test',
        'post_logout_redirect_uri': talao_url_logout,
        }
        return redirect(talao_url_logout + '?' + urlencode(data))
    if request.method == 'POST':
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

# test de client credentials
@app.route('/test', methods=['GET', 'POST'])
def talao_2():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': "",
        'scope' : 'create'
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande de token envoyée')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 demande envoyée')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        data = {'firstname' : 'pierre', 'lastname' : 'Dupont', 'email' : 'pierre.dupont@talao.co'}
        response = requests.post(talao_url + '/api/v1/create', data=json.dumps(data), headers=headers)
        return response.json()
    return 'status code probleme'


if __name__ == '__main__':
    app.run( port=4000, debug =True)

