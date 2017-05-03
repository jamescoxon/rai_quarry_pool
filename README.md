# rai_quarry_pool

This is alpha code - while it has been tested it might not work for you...

## Testing

You can test the pool at http://46.101.95.140:5000/pool (however server may be closed at a later date)

## Installation Guide (Rough)

1. `apt-get update`
2. `apt-get install python3-pip`
3. `pip3 install --upgrade pip`
4. `pip3 install dataset`
5. `pip3 install flask`
6. `pip3 install gunicorn`

7. `git clone https://github.com/jamescoxon/rai_quarry_pool.git`

8. Edit app.py and submit.py and add the address you want the faucet to pay to

9. Open `screen`
10. `gunicorn --bind 0.0.0.0:5000 app:app`
11. Detach the screen using Ctrl-A-D

12. Find out your IP address using `ifconfig`
13. check in web browser http://<ip_address>:5000/pool

14. Run another screen
15. `python3 submit.py` <- this now submits the data every 90seconds

## Notes
If you are using a new raiblocks account then you need to send it some xrb or the server won't detect that it exists.

## Things to add

1. add interaction with a raiblocks node which will allow auto payout
