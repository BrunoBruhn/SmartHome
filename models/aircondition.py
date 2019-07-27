import pulp

def optim(house_model,duration,LP,T_outside,P_el_max_aircon,eta_n_aircon,T_house):

	P_aircon = pulp.LpVariable.dicts("P_aircon", range(duration), cat=pulp.LpContinuous, upBound=P_el_max_aircon, lowBound=0)

	for t in range(1,duration):
		LP += T_house[t]-T_house[t-1] ==   ((T_outside[t]-T_house[t-1])* house_model.q_loss-P_aircon[t]*eta_n_aircon)  * 60 / house_model.mcp

	return P_aircon