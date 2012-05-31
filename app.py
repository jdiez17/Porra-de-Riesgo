from flask import Flask, render_template, url_for, jsonify, request, redirect, session, flash
import primaweb

app = Flask(__name__)

def do_index(page=0):
	curr = prima.prima_value().split('##')[1].split(',')
	minmax = prima.min_max()
	bets = prima.paged_bets(page)
	num_bets = prima.bet_count()
	return render_template('index.html', 
							curr_int=curr[0],
							curr_dec=curr[1], 
							min_int=minmax[1][0],
							min_dec=minmax[1][1], 
							max_int=minmax[0][0], 
							max_dec=minmax[0][1], 
							bets=bets,
							num_bets=num_bets,
							page=page)

@app.route('/current')
def prima():
	return prima.prima_value()

@app.route('/graph')
def graph():
	return render_template('graph.html')

@app.route('/data')
def data():
	return jsonify(data = prima.prima_data())
	
@app.route('/bet', methods=['POST'])
def bet():
	val = int(request.form['prima'])
	user = request.form['twitter'].replace("@", "").lower()

	if not val or not user or user == "twitter" or val > 999:
		flash("Tienes que apostar por un valor e introducir tu twitter", 'error')
	else:
		if val < float(prima.prima_value().split("##")[1].replace(",", ".")): 
			flash("Tienes que apostar un valor superior a la prima actual", 'error')
		else: 
			if prima.place_bet(val, user):
				flash(val, user)
			else:
				flash("El usuario de twitter especificado no existe o ya ha apostado.", 'error')
		
	return redirect(url_for('index'))

@app.route('/')
def index():
	last_page = prima.last_page()
	return do_index(last_page)	
	
@app.route('/page/<int:page>')
def page(page):
	bets = prima.paged_bets(page)
	return render_template("bets.html", bets=bets)

prima = primaweb.PrimaWeb()
app.secret_key = "lolwut"
	
if __name__ == '__main__':
	
	app.run(host='0.0.0.0', port=5000, debug=True)