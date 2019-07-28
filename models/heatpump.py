import pulp

class Aircon_Heatpump(object):
	def __init__(self,COP,P_max_el_heatpump,eta_n_aircon,P_max_el_aircon,T_outside,SmartHome):
		self.COP=COP
		self.P_max_el_heatpump=P_max_el_heatpump
		self.eta_n_aircon=eta_n_aircon
		self.P_max_el_aircon=P_max_el_aircon
		self.T_outside=T_outside
		self.duration=SmartHome.duration
		self.LP=SmartHome.LP

	def opti(self,house_model):

		T_house = pulp.LpVariable.dicts("T_house", range(self.duration), cat=pulp.LpContinuous, lowBound=house_model.T_min_house, upBound=house_model.T_max_house)
		P_heatpump = pulp.LpVariable.dicts("P_heatpump", range(self.duration), cat=pulp.LpContinuous, upBound=self.P_max_el_heatpump, lowBound=0)
		P_aircon = pulp.LpVariable.dicts("P_aircon", range(self.duration), cat=pulp.LpContinuous, upBound=self.P_max_el_aircon, lowBound=0)

		for t in range(self.duration):
			if t==0:
				self.LP += T_house[t] == house_model.T_house_initial
			else:
				self.LP += T_house[t] == T_house[t-1] + (P_heatpump[t] * self.COP - P_aircon[t] * self.eta_n_aircon - (T_house[t-1] - self.T_outside[t]) * house_model.q_loss) * 60 / house_model.mcp
				
		return T_house,P_heatpump,P_aircon