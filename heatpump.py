import pulp

def optim(duration,LP,room_size,T_min_house,T_max_house,T_outside,P_max_heatpump,COP,heat_loss):
	
	T_house = pulp.LpVariable.dicts("T_house", range(duration), cat=pulp.LpContinuous, lowBound=T_min_house, upBound=T_max_house)
	P_heatpump = pulp.LpVariable.dicts("P_heatpump", range(duration), cat=pulp.LpContinuous, upBound=P_max_heatpump, lowBound=0)

	for t in range(duration):

		if t==0:
			LP += T_house[t] == 22

		else:
			LP += T_house[t] == T_house[t-1] + (P_heatpump[t]*COP-(T_house[t-1]-T_outside)* heat_loss)  * 60 / (2.5*room_size * 1.2) #1.2 kJ/(K*m**3)

	return T_house,P_heatpump