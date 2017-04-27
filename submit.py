
import dataset
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import time

pool_address = 'xrb_317ngidjcgamhiq79kztd69kx1kiusybhzakya9xhxjoaabkhrmp8mr4wio4'
top_60 = 0

def post_data(data):

	url = 'https://raiblockscommunity.net/faucet/elaborate.php' # Set destination URL here

	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()
	return str(json)

def payout_data():

	url = 'https://raiblockscommunity.net/faucet/paylist.php' # Set destination URL here
	data = {'acc': pool_address, 'json': 1}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()
	return json

# connecting to a SQLite database
db = dataset.connect('sqlite:///mydatabase.db')

# get a reference to the table 'user'
table = db['user']

while 1:
	total_address_claims = table.find(submitted=0)
	cap_data = []
	for xrb_address in total_address_claims:
		print("XRB:", xrb_address['address'], " sub:", xrb_address['submitted'], " paid:", xrb_address['paid'])
		cap_data.append(xrb_address['grecaptcha'])

	if len(cap_data) > 0:
		total_claims_data = len(cap_data)
		print("Claims to send: ", total_claims_data)
		json_string = json.dumps(cap_data)
		data = {}
		data['ask_address']=pool_address
		data['donate']=1
		data['accepted']=1
		data['captchas']=json_string

#	print(data)

		data_response = post_data(data)
		print(data_response)

		split_data_response = data_response.split('{')
		print("{", split_data_response[1])
		first_data_response = "{" + split_data_response[1]
		json_response = json.loads(first_data_response)
		print(json_response)

		#{"error":"no","valid":1,"thanks":1,"valid_captchas":[0]}
		if json_response['error'] == "no":
			print("Submit accepted, valid: ", json_response['valid'])
			diff = total_claims_data - int(json_response['valid'])
			print("Diff: ", diff)
			print("Array of submissions: ", json_response['valid_captchas'])

			for submissions in json_response['valid_captchas']:
				table.update(dict(grecaptcha=cap_data[submissions], submitted=1), ['grecaptcha'])

			if diff > 0:
				#Remove invalid claims
				claims_left = table.find(submitted=0)
				for claims in claims_left:
					print(claims['id'])
					table.delete(id=claims['id'])

			print("Database updated")
		else:
			for update_data in cap_data:
				table.delete(grecaptcha=update_data)
			print("Database updated")


	payout_raw = payout_data()
	payout = json.loads(payout_raw)
	print(payout_raw)

	acc_payout = payout['pending']
	exp_payout = acc_payout[0]['expected-pay']
	print("Expected: ", exp_payout)

	if ((top_60 == 1) and int(exp_payout) == 0):
		payout_id = time.time()
		print("Now update database:", payout_id)
		top_60 = 0
		all_unpaid = table.find(paid=0)
		for unpaid in all_unpaid:
			data = dict(id=unpaid['id'], paid=payout_id)
			table.update(data, ['id'])
		print("Table updated")

	if (int(exp_payout) > 0):
		print("In the top 60")
		top_60 = 1

		if (int(acc_payout[0]['pending']) == 0):
			payout_id = time.time()
			print("Now update database:", payout_id)
#	all_unpaid = table.find(paid=0)
#	for unpaid in all_unpaid:
#		data = dict(id=unpaid['id'], paid=payout_id)
#		table.update(data, ['id'])
#	print("Table updated")
	else:
		print("Continue claiming")

	print("Pending: ", payout['pending'])
	print("Validated claims: ", acc_payout[0]['pending'])
	print("Threshold: ", payout['threshold'])

	all_unpaid = table.find(paid=0)
	unpaid_address = []
	for unpaid in all_unpaid:
#	print(unpaid['address'])
		unpaid_address.append(unpaid['address'])

	total_unpaid_address = len(unpaid_address)

	list_unpaid_address = set(unpaid_address)
	for unique_address in list_unpaid_address:
		perc_claims = (int(unpaid_address.count(unique_address)) / total_unpaid_address) * 100
		print(unique_address, " : ", unpaid_address.count(unique_address), " " ,perc_claims, "%")

	print("Done")

	time.sleep(90)
