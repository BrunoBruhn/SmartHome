import pulp

def optim(house_model,duration,LP,T_outside,P_el_max_aircon,eta_n_aircon,T_house):

	P_aircon = pulp.LpVariable.dicts("P_aircon", range(duration), cat=pulp.LpContinuous, upBound=P_el_max_aircon, lowBound=0)

	for t in range(1,duration):
		

	return P_aircon