import redis
import requests
from BeautifulSoup import BeautifulSoup as bs
import json
from math import floor

class PrimaWeb: 
	def __init__(self):
		self.redis = redis.Redis("localhost")
		self.page_size = 50
		self.historic_max = 100
		
	def add_datapoint(self, prima):
		len = self.redis.llen("prima_historic")
		if len > 0:
			if self.redis.lrange("prima_historic", len-1, len-1)[0].split("##")[1] != prima.split("##")[1]: 
				self.redis.rpush("prima_historic", prima)
				self.redis.ltrim("prima_historic", len - self.historic_max, self.historic_max)
		else:
			self.redis.rpush("prima_historic", prima)
		
	def prima_value(self):
		if not self.redis.exists("prima_value"): 
			r = requests.get('http://laprimaderiesgo.com').content
			s = bs(r)
			p = s.h6.string + "##" + s.h2.string
			
			self.redis.set("prima_value", p)
			self.redis.expire("prima_value", 60)
			
			self.add_datapoint(p)
		else:
			p = self.redis.get("prima_value")
			
		return p
		
	def prima_data(self):
		data = self.redis.lrange("prima_historic", 0, -1)
		result = [['Hora', 'Valor']]
		
		for datapoint in data:
			vars = datapoint.split("##")
			vars[0] = vars[0].split("@")[1];
			vars[1] = float(vars[1].replace(",", "."))
			
			result.append(vars)
			
		return result
		
	def min_max(self):
		data = self.redis.lrange("prima_historic", 0, -1)
		
		tmp = []
		for datapoint in data:
			tmp.append(float(datapoint.split("##")[1].replace(",", ".")))
			
		return [str(min(tmp)).split("."), str(max(tmp)).split(".")]
		
	def place_bet(self, val, who):
		bets = self.redis.lrange("prima_bets", 0, -1)
		if bets:
			for bet in bets:
				data = bet.split("##")
				if data[2] == who:
					return False
	
		try:
			avatar = json.loads(requests.get('http://twitter.com/users/' + who + '.json').content)['profile_image_url'].replace("_normal", "_reasonably_small")
			avatar = unicode(avatar)
		except:
			return False
			
		self.redis.rpush("prima_bets", avatar + "##" + str(val) + "##" + who)
		return True
		
	def paged_bets(self, page):
		count = self.bet_count()
		start = self.page_size * page
		end = start + self.page_size - 1
		bets = self.redis.lrange("prima_bets", start, end)
		
		result = []
		if bets:
			for bet in bets:
				data = bet.split("##")
				result.append({"avatar": data[0], "bet": data[1], "who": data[2]})

		return reversed(result)
	
	def bet_count(self):
		return self.redis.llen("prima_bets")
		
	def last_page(self):
		return floor(self.bet_count() / self.page_size)