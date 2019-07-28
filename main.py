import csv,pulp
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import *
from models import *

########################################################################################
########################################################################################

'--IMPORT DATA--'
# Data has to be put in the file 'profiles.csv'

df=pd.read_csv('profiles.csv')
df=df.round(decimals=3)

PV_production = df['PV'].tolist()
EL_consumption = df['EL'].tolist()
Price_import = df['CP_IM'].tolist()
Q_DHW = df['DHW'].tolist()
T_outside = df['T_OUT'].tolist()

Price_export = 10 # (Juni 2019, Germany)
########################################################################################
########################################################################################
'INITIALIZE PROBLEM'

duration=1440*7

#init problem and creating object-independent LP variables
LP = pulp.LpProblem('LP',pulp.LpMinimize)  

Import = pulp.LpVariable.dicts("Import", range(duration), lowBound=0,cat=pulp.LpContinuous)
Export = pulp.LpVariable.dicts("Export", range(duration), lowBound=0,cat=pulp.LpContinuous)
Cost = 	 pulp.LpVariable.dicts("Cost", range(duration), cat=pulp.LpContinuous)

MAX_solving_time = 60 #seconds
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
T_house_initial= 22		#celsius
T_min_house = 18		#celsius
T_max_house = 22		#celsius
average_U_value = 0.5 	#W/m2k

House = House(room_area,room_surface,room_height,average_U_value,T_min_house,T_max_house,T_house_initial)
################################################
'WATER HEATER'

Tank_volume=5000 			#liter
T_min_waterheater=40 		#celsius
T_max_waterheater=95		#celsius
T_ambient=23				#celsius
P_max_waterheater=50 		#kW
EEC='C' 					#EU energy efficiency class 

water_heater = WaterHeater(Q_DHW,Tank_volume,T_min_waterheater,T_max_waterheater,T_ambient,P_max_waterheater,EEC,SmartHome)
################################################
'AIRCON AND HEAT PUMP'

COP=3 			
P_max_el_heatpump=3000	#kW
eta_n_aircon=0.3
P_max_el_aircon=10000 	#kW

heating_cooling = Aircon_Heatpump(COP,P_max_el_heatpump,eta_n_aircon,P_max_el_aircon,T_outside,SmartHome)
################################################
'BATTERY'

E_battery_max=0 		#kWh 
eta_n_battery=0.9
P_charge_battery_max=20	#kW
P_discharge_max=20		#kW

battery = Battery(E_battery_max*3600,P_charge_battery_max,P_discharge_max,eta_n_battery,SmartHome)
################################################
'ELECTRIC VEHICLE'

car_battery_capacity=40 		#kWh
P_car_charge_max=20  			#kW
charge_hour_start=18 			#o'clock
charge_hour_stop=8				#o'clock
eta_n_ev_charging_station=0.0001

electric_vehicle = EV(car_battery_capacity*3600,P_car_charge_max,charge_hour_stop,charge_hour_start,eta_n_ev_charging_station,SmartHome)

########################################################################################
'ADDING CONSTRAINTS'

T_tank,P_waterheater = water_heater.opti()

T_house,P_heatpump,P_aircon = heating_cooling.opti(House)

E_battery,P_charge_battery = battery.opti()

E_EV,u_charge_EV= electric_vehicle.opti()

########################################################################################
'SET UP ENERGY BALANCE AND OBJECTIVE, THEN SOLVE'

for t in range(duration):

	LP += PV_production[t] - EL_consumption[t] - P_charge_battery[t] - P_waterheater[t] - P_heatpump[t] - P_aircon[t] - P_car_charge_max*u_charge_EV[t] == Export[t] - Import[t]

	LP += Cost[t] == Import[t] * Price_import[t] - Export[t] * Price_export

LP += sum([Cost[t] for t in range(duration)])

status = LP.solve(pulp.solvers.GUROBI(mip=True, msg=True, timeLimit=MAX_solving_time,epgap=MAX_gap))

print( 'LP status: ' + pulp.LpStatus[status] + '')

########################################################################################
'CREATE LISTS CONTAINING THE VARIABLE PROFILES'

Import_values=[]
Export_values=[]
Battery_levels=[]
P_charge_battery_values=[]
T_tank_values=[]
P_waterheater_values=[]
T_house_values=[]
Q_spaceheater_values=[] # heatpump
Q_aircon_values=[] 
E_EV_values=[]
#P_charge_EV_values=[]

for i in range(duration):
	Import_values.append(Import[i].value())
	Export_values.append(Export[i].value())
	Battery_levels.append(E_battery[i].value()/360) #now ckWh
	P_charge_battery_values.append(P_charge_battery[i].value())
	T_tank_values.append(T_tank[i].value())
	P_waterheater_values.append(P_waterheater[i].value())
	T_house_values.append(T_house[i].value())
	Q_spaceheater_values.append(P_heatpump[i].value()*COP*100)
	Q_aircon_values.append(P_aircon[i].value()*eta_n_aircon*100)
	E_EV_values.append(E_EV[i].value()/360) #now ckWh
	#P_charge_EV_values.append(P_charge_EV[i].value())

########################################################################################
'PLOT PROFILES'

# BATTERY
plt.figure()
plt.plot(PV_production[:duration],label="PV")
plt.plot(EL_consumption[:duration],label="EL")
plt.plot(Battery_levels[:duration],label="E_Battery")
plt.plot(P_charge_battery_values[:duration],label='P_charge_battery')
plt.title('Battery')
plt.legend()

#IMPORT EXPORT
plt.figure()
plt.plot(PV_production[:duration],label="PV")
plt.plot(EL_consumption[:duration],label="EL")
plt.plot(Export_values[:duration],label="Export")
plt.plot(Import_values[:duration],label="Import")
plt.title('Import/Export')
plt.legend()

#WATER HEATER
plt.figure()
plt.plot(Q_DHW[:duration],label="Q_DHW")
plt.plot(P_waterheater_values[:duration],label="P_waterheater")
plt.plot(T_tank_values[:duration],label="T_tank")
plt.title('Water heater')
plt.legend()

#SPACE HEATER
plt.figure()
plt.plot(Price_import[:duration],label="Price")
plt.plot(Q_spaceheater_values[:duration],label="P_heatpump")
plt.plot(T_house_values[:duration],label="T_house")
plt.plot(T_outside[:duration],label="T_outside")
plt.plot(Q_aircon_values[:duration],label="Q_aircon")
plt.title('Space Heating and Cooling')
plt.legend()

# EV
plt.figure()
plt.plot(E_EV_values[:duration],label="E_EV")
#plt.plot(P_charge_EV_values[:duration],label="EV_charge")
plt.title('Electric Vehicle')
plt.legend()

plt.show()

# create dataframe containing results
df_results = pd.DataFrame() 
df_results['PV[kW]']=PV_production[:duration]
df_results['EL[kW]']=EL_consumption[:duration]
df_results['Import[kW]']=Import_values[:duration]
df_results['Export[kW]']=Export_values[:duration]
df_results['Battery[kWh]']=Battery_levels[:duration]
df_results['P_charge_battery[kW]']=P_charge_battery_values[:duration]
df_results['T_tank[*C]']=T_tank_values[:duration]
df_results['P_waterheater[kW]']=P_waterheater_values[:duration]
df_results['T_house[*C]']=T_house_values[:duration]
df_results['Q_spaceheater[kW]']=Q_spaceheater_values[:duration]
df_results['Q_aircon[kW]']=Q_aircon_values[:duration]

df_results.to_csv(r'Results.csv')