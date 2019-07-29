import csv,pulp
import pandas as pd
from gurobipy import *
from models import *
import plot_profiles

########################################################################################
########################################################################################
'IMPORT DATA'

# Data has to be put in the file 'profiles.csv'

df=pd.read_csv('profiles.csv')
df=df.round(decimals=3)

PV_production = df['PV'].tolist()
EL_consumption = df['EL'].tolist()
Price_import = df['CP_IM'].tolist()
Q_DHW = df['DHW'].tolist()
T_outside = df['T_OUT'].tolist()

Price_export = 10.64 # (June 2019, Germany)

########################################################################################
########################################################################################
'INITIALIZE PROBLEM'

duration=10080

#init problem and creating object-independent LP variables
LP = pulp.LpProblem('LP',pulp.LpMinimize)  

Import = pulp.LpVariable.dicts("Import", range(duration), lowBound=0,cat=pulp.LpContinuous)
Export = pulp.LpVariable.dicts("Export", range(duration), lowBound=0,cat=pulp.LpContinuous)
Cost = 	 pulp.LpVariable.dicts("Cost", range(duration), cat=pulp.LpContinuous)

MAX_solving_time = None #seconds
MAX_gap = None

SmartHome=SmartHome(duration,LP)

########################################################################################
########################################################################################

'--SET PARAMETERS--'
################################################
'HOUSE'

room_area = 20 			#sqm
room_surface = 2 * (10 + 12.5 + room_area) #sqm
room_height = 2.5		#m
T_house_initial= 20		#celsius
T_min_house = 20		#celsius
T_max_house = 22		#celsius
average_U_value = 0.5 	#W/m2k

House = House(room_area,room_surface,room_height,\
	average_U_value,T_min_house,T_max_house,T_house_initial)
################################################
'WATER HEATER'

Tank_volume=300 			#liter
T_min_waterheater=40 		#celsius
T_max_waterheater=85		#celsius
T_ambient=23				#celsius
P_max_waterheater=5 		#kW
EEC='C' 					#EU energy efficiency class 

water_heater = WaterHeater(Q_DHW,Tank_volume,T_min_waterheater,\
	T_max_waterheater,T_ambient,P_max_waterheater,EEC,SmartHome)
################################################
'AIRCON AND HEAT PUMP'

COP_heatpump=4.2 			
P_max_el_heatpump=3	#kW
COP_aircon=3
P_max_el_aircon=10 	#kW

heating_cooling = Aircon_Heatpump(COP_heatpump,P_max_el_heatpump,\
	COP_aircon,P_max_el_aircon,T_outside,SmartHome)
################################################
'BATTERY'

E_battery_max=10 		#kWh 
eta_n_battery=0.9		
P_charge_battery_max=20	#kW
P_discharge_max=20		#kW

battery = Battery(E_battery_max*3600,P_charge_battery_max,\
	P_discharge_max,eta_n_battery,SmartHome)
################################################
'ELECTRIC VEHICLE'

car_battery_capacity=40 		#kWh
P_car_charge_max=20  			#kW
charge_hour_start=18 			#o'clock
charge_hour_stop=8				#o'clock
eta_n_ev_charging_station=0.95

electric_vehicle = EV(car_battery_capacity*3600,P_car_charge_max,\
	charge_hour_stop,charge_hour_start,eta_n_ev_charging_station,SmartHome)

########################################################################################
'ADDING OBJECT CONSTRAINTS'

T_tank,P_waterheater = water_heater.opti()

T_house,P_heatpump,P_aircon = heating_cooling.opti(House)

E_battery,P_charge_battery = battery.opti()

E_EV,u_charge_EV= electric_vehicle.opti()

########################################################################################
########################################################################################
'SET UP ENERGY BALANCE AND OBJECTIVE - THEN SOLVE'

for t in range(duration):

	LP += PV_production[t] - EL_consumption[t] - P_charge_battery[t] \
	- P_waterheater[t] - P_heatpump[t] - P_aircon[t] - P_car_charge_max*u_charge_EV[t] \
	== Export[t] - Import[t]

	LP += Cost[t] == Import[t] * Price_import[t] - Export[t] * Price_export

LP += sum([Cost[t] for t in range(duration)])

status = LP.solve(pulp.solvers.GUROBI(mip=True, msg=True, timeLimit=MAX_solving_time,epgap=MAX_gap))

print( 'LP status: ' + pulp.LpStatus[status] + '')

########################################################################################
########################################################################################

'PLOT PROFILES'

plot_profiles.show(duration,Import,Export,E_battery,P_charge_battery,T_tank,P_waterheater,T_house,P_heatpump,COP_heatpump,P_aircon,COP_aircon,E_EV,Price_import,PV_production,EL_consumption,Q_DHW,T_outside)

