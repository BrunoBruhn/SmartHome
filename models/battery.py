import pulp

class Battery(object):
	def __init__(self,capacity,P_charge_max,P_discharge_max,eta_n,SmartHome):
		self.capacity=capacity
		self.P_charge_max=P_charge_max
		self.P_discharge_max=P_discharge_max
		self.eta_n=eta_n
		self.duration=SmartHome.duration
		self.LP=SmartHome.LP

	def opti(self):
		E_battery = pulp.LpVariable.dicts("E_battery", range(self.duration), cat=pulp.LpContinuous, lowBound=0, upBound=self.capacity)
		P_charge = pulp.LpVariable.dicts("P_charge", range(self.duration), cat=pulp.LpContinuous, upBound=self.P_charge_max,lowBound=-self.P_discharge_max)

		for t in range(self.duration):
			if t==0:
				self.LP += E_battery[t]==60*P_charge[t]*self.eta_n
			else:
				self.LP += E_battery[t]==E_battery[t-1]+60*P_charge[t]*self.eta_n

		return E_battery,P_charge