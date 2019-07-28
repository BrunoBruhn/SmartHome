import pulp

class WaterHeater(object):
	def __init__(self,Q_DHW,Tank_volume,T_min,T_max,T_ambient,P_max,EEC,SmartHome):
		self.Q_DHW=Q_DHW
		self.Tank_volume=Tank_volume
		self.T_min=T_min
		self.T_max=T_max
		self.T_ambient=T_ambient
		self.P_max=P_max
		self.EEC=EEC
		self.duration=SmartHome.duration
		self.LP=SmartHome.LP

	def get_q_loss(self,EEC,Tank_volume):
		if self.EEC == '>=A+':
			k = 5.5
			l = 3.16
		elif self.EEC == 'A':
			k = 7
			l = 3.705
		elif self.EEC == 'B':
			k = 10.25
			l = 5.09
		elif self.EEC == 'C':
			k = 14.33
			l = 7.13
		elif self.EEC == 'D':
			k = 18.83
			l = 9.333
		elif self.EEC == 'E':
			k = 23.5
			l = 11.995
		elif self.EEC == '<=F':
			k = 28.5
			l = 15.16
		else:
			print "EU energy efficiency class %s doesn't exist" % self.EEC
			print '\a'  # beep
			exit()

		q_loss = (k + l * (self.Tank_volume) ** 0.4) / ((65 - 20) * 1000)  # kW/K	

		return q_loss

	def opti(self):

		q_loss=self.get_q_loss(self.EEC,self.Tank_volume)

		T_tank = pulp.LpVariable.dicts("T_tank", range(self.duration), cat=pulp.LpContinuous, lowBound=self.T_min, upBound=self.T_max)
		P_waterheater = pulp.LpVariable.dicts("P_waterheater", range(self.duration), cat=pulp.LpContinuous, upBound=self.P_max,lowBound=0)

		for t in range(self.duration):
			if t==0:
				self.LP += T_tank[t] == 40.001
			else:
				self.LP += T_tank[t] == T_tank[t-1] + (P_waterheater[t]-self.Q_DHW[t]-(T_tank[t-1]-self.T_ambient)* q_loss)  * 60 / (self.Tank_volume * 4.1813)

		return T_tank,P_waterheater 