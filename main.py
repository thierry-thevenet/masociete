
from urllib.parse import urlencode

import requests
from flask import Flask, redirect, request, render_template_string, session, send_from_directory

version = '0.1.2'

app = Flask(__name__)
app.secret_key = 'ùmkljùmkjagzklj'


url_callback = 'http://localhost:3000/callback'
client_id = '211286433e39cce01db448d80181bdfd005554b19cd51b3fe7943f6b3b86ab6e'
client_secret = '2791a731e6a59f56b6b4dd0d08c9b1f593b5f3658b9fd731cb24248e2669af4b'

url_callback = 'http://localhost:3000/callback'

fc_url = 'https://fcp.integ01.dev-franceconnect.fr'
fc_url_authorize = fc_url + '/api/v1/authorize'
fc_url_token = fc_url + '/api/v1/token'
fc_url_userinfo = fc_url + '/api/v1/userinfo'
fc_url_logout = fc_url + '/api/v1/logout'

@app.route('/france_connect', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': 'test',
            'nonce': 'test',
            'redirect_uri': url_callback,
            'scope': 'openid identite_pivot test thierry',
        }
        print('POST envoyé = ', urlencode(data))
        return redirect(fc_url_authorize + '?' + urlencode(data))

    else:
        html = """
<!DOCTYPE html>
<html lang="en">
    <body>
        <form method=post enctype=multipart/form-data>
            <input type="image" src="/uploads/FCboutons-10.png">
        </form>
    </body>
</html>
        """
        return render_template_string(html)

@app.route('/', methods=['GET', 'POST'])
def login() :
    return 'ok website masociete.co'


@app.route('/callback', methods=['GET', 'POST'])
def france_connect():
    print(request.args)
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
    }
    response = requests.post(fc_url_token, data=data)
    if response.status_code == 200:
        token_data = response.json()
        print('avant demande info ', token_data )
        # demande d'info sur l identite pivot
        params = {
            'schema': 'openid',
        }
        headers = {
            'Authorization': 'Bearer %s' % token_data['access_token']
        }
        session['id_token'] = token_data.get('id_token')
        user_info_response = requests.get(fc_url_userinfo, params=params, headers=headers)
        html = """
<!DOCTYPE html>
<html lang="en">
    <body>
    {% for key, value in user_info_response.json().items() %}
        <div>{{key}}: {{value}}</div>
    {% endfor %}
        <form method=post action="/logout" enctype=multipart/form-data>
            <button>Logout</button>
        </form>
    </body>
</html>
        """
        return render_template_string(html, user_info_response=user_info_response)
    return 'Something failed'


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'GET':
        id_token = session['id_token']
        data = {
        'id_token_hint': id_token,
        'state': 'test',
        'post_logout_redirect_uri': 'http://localhost:3000/logout',
        }
        print(urlencode(data))
        return redirect(fc_url_logout + '?' + urlencode(data))
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

if __name__ == '__main__':
    app.run( port=4000, debug =True)