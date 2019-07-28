import pulp

class EV(object):
	def __init__(self,capacity,P_car_charge_max,charge_hour_stop,charge_hour_start,eta_n_ev_charging_station,SmartHome):
		self.capacity=capacity
		self.P_car_charge_max=P_car_charge_max
		self.charge_hour_stop=charge_hour_stop
		self.charge_hour_start=charge_hour_start
		self.eta_n_ev_charging_station=eta_n_ev_charging_station
		self.duration=SmartHome.duration
		self.LP=SmartHome.LP

	def opti(self):

		#u_charge_EV = pulp.LpVariable.dicts("P_charge_EV", range(self.duration), cat=pulp.LpBinary)

		E_EV={}
		u_charge_EV={}

		for t in range(self.duration):

			min_of_day = t % 1440

			if 8*60<min_of_day<18*60:
				u_charge_EV[t] = pulp.LpVariable("u_charge_EV_"+str(t), cat=pulp.LpInteger, lowBound=0, upBound=0)
			else:
				u_charge_EV[t] = pulp.LpVariable("u_charge_EV_"+str(t), cat=pulp.LpBinary)

			if min_of_day==8*60:
				E_EV[t] = pulp.LpVariable("E_EV_"+str(t), cat=pulp.LpContinuous, upBound=self.capacity, lowBound=self.capacity*0.99)

			else:
				E_EV[t] = pulp.LpVariable("E_EV_"+str(t), cat=pulp.LpContinuous, upBound=self.capacity, lowBound=0)
			

			if t==0:
				self.LP += E_EV[t] == 0
			elif 8 * 60 < min_of_day < 18 * 60:
				self.LP += E_EV[t] == E_EV[t-1]*0.995
			else:
				self.LP += E_EV[t] == E_EV[t-1] + u_charge_EV[t] * self.P_car_charge_max * 60


		return E_EV,u_charge_EV

