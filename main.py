
from urllib.parse import urlencode
import requests
from flask import Flask, redirect, request, render_template_string, session, send_from_directory
import json

version = '0.1.2'
app = Flask(__name__)
app.secret_key = 'ùmkljùmkjagzklj'

client_id = 'eID4kHps5w0HFdv3fJ9fuVde'
client_secret = 'Qe99WEiFmTcSmSHfh6z92mbVbrZOa4CfDT6iyNqRqxfd7mBG'

# local masociete.co
url_callback = 'http://127.0.0.1:4000/callback'

# Talao as an OAuth2 Identity Provider
talao_url = 'http://127.0.0.1:3000'
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
        #http://127.0.0.1:3000/api/v1/authorize?response_type=code&client_id=eID4kHps5w0HFdv3fJ9fuVde&scope=profile+resume+birthdate+email+phone

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
				<h1>Website de MaSociete.co</h1>
                <h2>Our Decentralized IDentifiers are : </h2>
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
    print('code reçu ', code)
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
    #curl -u G2eHD21HP8ZVmIPVG0tbtqKH:rp9maPLRQEJ3bviGwTMPXvQdcx8YlqONuVDFZSAqupDdgXb9 -XPOST http://127.0.0.1:3000/api/v1/oauth/token -F grant_type=authorization_code -F code=0sWGCgebZ85Z1gZ0teZqpwRyPXcvBEioP9kaEtzC6PtKr8k0

    if response.status_code == 200:
        token_data = response.json()
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
        #curl -H "Authorization: Bearer ${access_token}" http://127.0.0.1:3000/api/v&/userinfo

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
        'post_logout_redirect_uri': 'http://localhost:3000/logout',
        }
        return redirect(talao_url_logout + '?' + urlencode(data))
    if request.method == 'POST':
        return 'Game over !!!'

@app.route('/uploads/<filename>')
def send_file(filename):
	return send_from_directory('/home/thierry/Talao/uploads/', filename)


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



@app.route('/test', methods=['GET', 'POST'])
def talao_2():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': "",
        'scope' : 'identity'
    }
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : demande de token envoyée')
    #curl -u G2eHD21HP8ZVmIPVG0tbtqKH:rp9maPLRQEJ3bviGwTMPXvQdcx8YlqONuVDFZSAqupDdgXb9 -XPOST http://127.0.0.1:3000/api/v1/oauth/token -F grant_type=authorization_code -F scope=profile -F code=0sWGCgebZ85Z1gZ0teZqpwRyPXcvBEioP9kaEtzC6PtKr8k0
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 demande envoyée')
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        data = {'firstname' : 'pierre', 'lastname' : 'Dupont'}
        response = requests.post('http://127.0.0.1:3000/api/v1/create_identity', data=json.dumps(data), headers=headers)
        return response.json()
    return 'status code probleme'


if __name__ == '__main__':
    app.run( port=4000, debug =True)

