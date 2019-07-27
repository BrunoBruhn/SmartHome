import pulp

def optim(duration,LP,capacity,P_charge_max,P_discharge_max,eta_n):

	E_battery = pulp.LpVariable.dicts("E_battery", range(duration), cat=pulp.LpContinuous, lowBound=0, upBound=capacity)
	P_charge = pulp.LpVariable.dicts("P_charge", range(duration), cat=pulp.LpContinuous, upBound=P_charge_max,lowBound=-P_discharge_max)

	for t in range(duration):

		if t==0:
			LP += E_battery[t]==60*P_charge[t]*eta_n

		else:
			LP += E_battery[t]==E_battery[t-1]+60*P_charge[t]*eta_n


	return E_battery,P_charge