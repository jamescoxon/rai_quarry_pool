from flask import Flask
from flask import render_template, redirect, url_for, request, abort, flash, session

app = Flask(__name__)

from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import dataset

pool_address = 'xrb_317ngidjcgamhiq79kztd69kx1kiusybhzakya9xhxjoaabkhrmp8mr4wio4'

# connecting to a SQLite database
db = dataset.connect('sqlite:///mydatabase.db')

# get a reference to the table 'user'
table = db['user']

def payout_data():

        url = 'https://raiblockscommunity.net/faucet/paylist.php' # Set destination URL here
        data = {'acc': pool_address, 'json': 1}
        request = Request(url, urlencode(data).encode())
        json = urlopen(request).read().decode()
        return json

@app.route('/')
def start():
    return render_template('info.html')

@app.route('/pool')
def default_pool():
	return render_template('info.html')

@app.route("/redirect", methods=["POST"])
def address_redirect():
	address=request.form['xrb_address']
	complete_address = '/pool/' + address
	return redirect(complete_address)

@app.route('/pool/<address>')
def pool(address=None):
	total_address_claims = table.find(address=address)
	unsubmitted_claims = 0
	unpaid_claims = 0
	for xrb_address in total_address_claims:
#		print("XRB:", xrb_address['address'], " sub:", xrb_address['submitted'])
		if xrb_address['submitted'] == 0:
			unsubmitted_claims = unsubmitted_claims + 1
		if xrb_address['paid'] == 0:
			unpaid_claims = unpaid_claims + 1
#	print(unsubmitted_claims)

	all_unpaid = table.find(paid=0)
	unpaid_address = []
	for unpaid in all_unpaid:
        #       print(unpaid['address'])
		unpaid_address.append(unpaid['address'])

	len_unpaid_address = len(unpaid_address)
	if len_unpaid_address > 0:
		perc_claims = (int(unpaid_address.count(address)) / len_unpaid_address) * 100
	else:
		perc_claims = 0
	print(perc_claims)

	return render_template('pool.html', address=address, unsub_claims=unsubmitted_claims, unpai_claims=unpaid_claims, perc_claims=perc_claims, total_claims=len_unpaid_address)

@app.route('/error')
def error():
        return render_template('error.html')

@app.route("/submit", methods=["POST"])
def submit():
	response = request.form.get('g-recaptcha-response')
	print(response)
	complete_address = request.referrer
	current_address = complete_address.split("/")
	xrb_address = current_address[-1]
	# Insert a new record.
	table.insert(dict(address=xrb_address, paid=0, grecaptcha=response, submitted=0))
	if len(response) > 0:
		return redirect(request.referrer)
	else:
		return redirect(url_for('error'))

@app.route('/stats')
def display_stats():
	payout_raw = payout_data()
	payout = json.loads(payout_raw)
	#print(payout_raw)

	acc_payout = payout['pending']

	print("Pending: ", payout['pending'])
	print("Validated claims: ", acc_payout[0]['pending'])
	print("Threshold: ", payout['threshold'])

	all_unpaid = table.find(paid=0)
	unpaid_address = []
	for unpaid in all_unpaid:
	#       print(unpaid['address'])
		unpaid_address.append(unpaid['address'])

	list_unpaid_address = set(unpaid_address)
	len_unpaid_address = len(unpaid_address)
	list_claims = []
	for unique_address in list_unpaid_address:
		perc_claims = (int(unpaid_address.count(unique_address)) / len_unpaid_address) * 100
		print(unique_address, " : ", unpaid_address.count(unique_address), " " ,perc_claims, "%")
		temp = {'address': unique_address, 'claims' : unpaid_address.count(unique_address), 'perc' : perc_claims}
		list_claims.append(temp)
	return render_template('stats.html', len_unpaid=len_unpaid_address, payout_threshold=payout['threshold'], claims=list_claims )

if __name__ == "__main__":
    app.run(host='0.0.0.0')
