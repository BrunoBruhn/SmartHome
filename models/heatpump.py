import pulp

def optim(house_model,duration,LP,T_outside,P_max_el_heatpump,COP,P_el_max_aircon,eta_n_aircon):

	T_house = pulp.LpVariable.dicts("T_house", range(duration), cat=pulp.LpContinuous, lowBound=house_model.T_min_house, upBound=house_model.T_max_house)
	P_heatpump = pulp.LpVariable.dicts("P_heatpump", range(duration), cat=pulp.LpContinuous, upBound=P_max_el_heatpump, lowBound=0)
	P_aircon = pulp.LpVariable.dicts("P_aircon", range(duration), cat=pulp.LpContinuous, upBound=P_el_max_aircon, lowBound=0)

	for t in range(duration):

		if t==0:
			LP += T_house[t] == house_model.T_house_initial
		else:
			LP += T_house[t] == T_house[t-1] + (P_heatpump[t] * COP - P_aircon[t] * eta_n_aircon - (T_house[t-1] - T_outside[t]) * house_model.q_loss) * 60 / house_model.mcp
			
	return T_house,P_heatpump,P_aircon