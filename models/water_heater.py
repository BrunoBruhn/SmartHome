import pulp
def get_q_loss(EEC,Tank_volume):
	if EEC == '>=A+':
		k = 5.5
		l = 3.16
	elif EEC == 'A':
		k = 7
		l = 3.705
	elif EEC == 'B':
		k = 10.25
		l = 5.09
	elif EEC == 'C':
		k = 14.33
		l = 7.13
	elif EEC == 'D':
		k = 18.83
		l = 9.333
	elif EEC == 'E':
		k = 23.5
		l = 11.995
	elif EEC == '<=F':
		k = 28.5
		l = 15.16
	else:
		print "EU energy efficiency class %s doesn't exist" % EEC
		print '\a'  # beep
		exit()

	q_loss = (k + l * (Tank_volume) ** 0.4) / ((65 - 20) * 1000)  # kW/K	

	return q_loss


def optim(duration,LP,Q_DHW,Tank_volume,T_min,T_max,T_ambient,P_max,EEC):
	
	q_loss=get_q_loss(EEC,Tank_volume)

	T_tank = pulp.LpVariable.dicts("T_tank", range(duration), cat=pulp.LpContinuous, lowBound=T_min, upBound=T_max)
	P_waterheater = pulp.LpVariable.dicts("P_waterheater", range(duration), cat=pulp.LpContinuous, upBound=P_max,lowBound=0)

	for t in range(duration):

		if t==0:
			LP += T_tank[t] == 40.001

		else:
			LP += T_tank[t] == T_tank[t-1] + (P_waterheater[t]-Q_DHW[t]-(T_tank[t-1]-T_ambient)* q_loss)  * 60 / (Tank_volume * 4.1813)


	return T_tank,P_waterheater 