""" Web connector to be used with External Issuer
python 3.7+
Flask
 """
DID = 'did:talao:talaonet:4562DB03D8b84C5B10FfCDBa6a7A509FF0Cdcc68'

from flask import Flask, redirect, request, render_template_string, session, send_from_directory


# This is to prove Talao DID
#@app.route('/did', methods=['GET'])
def did_check () :
	html = """<!DOCTYPE html>
		<html lang="en">
			<body>
				<p> 'Our Decentralized Identifier is <b>""" + DID + """</b> </p>
			</body>
		</html>"""
	return render_template_string(html)

# This is to Verify a Certificate issued by Talao . To be completed for database access
#@app.route('/verify', methods=['GET'])
def certificate_check () :
	certificate_id = request.args.get('certificate_id')
	html = """<!DOCTYPE html>
		<html lang="en">
			<body>
				<p>The Certificate #<b>""" + certificate_id + """</b> has been issued by Talao.io</p>
			</body>
		</html>"""
	return render_template_string(html)