import csv,pulp
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import *

########################################################################################
'INITIALIZE PROBLEM'

duration=1440
 #
#init problem and creating object-independent LP variables
LP = pulp.LpProblem('LP',pulp.LpMinimize)  

Import = pulp.LpVariable.dicts("Import", range(duration), lowBound=0,cat=pulp.LpContinuous )
Export = pulp.LpVariable.dicts("Export", range(duration), lowBound=0,cat=pulp.LpContinuous)
Cost = 	 pulp.LpVariable.dicts("Cost", range(duration), cat=pulp.LpContinuous)

MAX_solving_time = 60 #seconds
MAX_gap = None

########################################################################################
'IMPORT DATA'
# Data has to be put in the file 'profiles.csv'

# create dataframe from csv
df=pd.read_csv('profiles.csv')
df=df.round(decimals=3)

#create PV production list
PV_production = df['PV'].tolist()

#create electrical demand list
EL_consumption = df['EL'].tolist()

#create electricity pricing list
Price_import = df['CP_IM'].tolist()
Price_export = 1 # (Juni 2019, Germany)

########################################################################################
'ADDING BATTERY OBJECT'

import battery
E_battery_max=10 	#kWh 
eta_n=1
P_charge_max=20		#kW
P_discharge_max=20	#kW

#add battery variables
E_battery,P_charge = battery.optim(duration,LP,E_battery_max*3600,P_charge_max,P_discharge_max,eta_n)

########################################################################################
'ADDING WATER HEATER OBJECT'

import water_heater
Tank_volume=500 #liter
T_min_waterheater=40 		#celsius
T_max_waterheater=95		#celsius
T_ambient=23				#celsius
P_max_waterheater=5 		#kW
EEC='C' 		# EU energy efficiency class 

#create hot water demand list
Q_DHW = df['DHW'].tolist()

#add waterheater variables
T_tank,P_waterheater = water_heater.optim(duration,LP,Q_DHW,Tank_volume,T_min_waterheater,T_max_waterheater,T_ambient,P_max_waterheater,EEC)


########################################################################################
'ADDING HEAT PUMP FOR GENERAL HEATING'

import heatpump

room_size=40 		# sq meters
T_min_house=21 		#celsius
T_max_house=30		#celsius
T_outside=10		#celsius
COP=3 			
P_max_heatpump=0.1 	#kW
heat_loss=0.005 	#kW/K 	

#add house heating variables
T_house,P_heatpump = heatpump.optim(duration,LP,room_size,T_min_house,T_max_house,T_outside,P_max_heatpump,COP,heat_loss)


########################################################################################
'SET UP ENERGY BALANCE AND OBJECTIVE, THEN SOLVE'

for t in range(duration):

	LP += PV_production[t] -EL_consumption[t] -P_charge[t] - P_waterheater[t]-P_heatpump[t] == Export[t] - Import[t]

	LP += Cost[t]==Import[t]*Price_import[t]-Export[t]*Price_export

LP += sum([Cost[t] for t in range(duration)])

status = LP.solve(pulp.solvers.GUROBI(mip=True, msg=True, timeLimit=MAX_solving_time,epgap=MAX_gap))

print( 'LP status: ' + pulp.LpStatus[status] + '')

########################################################################################
'CREATE LISTS CONTAINING THE VARIABLE PROFILES'

Import_values=[]
Export_values=[]
Battery_levels=[]
P_charge_values=[]
T_tank_values=[]
P_waterheater_values=[]
T_house_values=[]
Q_spaceheater_values=[] # heatpump

for i in range(duration):
	Import_values.append(Import[i].value())
	Export_values.append(Export[i].value())
	Battery_levels.append(E_battery[i].value()/360) #now ckWh
	P_charge_values.append(P_charge[i].value())
	T_tank_values.append(T_tank[i].value())
	P_waterheater_values.append(P_waterheater[i].value())
	T_house_values.append(T_house[i].value())
	Q_spaceheater_values.append(P_heatpump[i].value()*COP)

########################################################################################
'PLOT PROFILES'

# BATTERY
plt.figure()
#plt.hold(True)
plt.plot(PV_production[:duration],label="PV")
plt.plot(EL_consumption[:duration],label="EL")
plt.plot(Battery_levels[:duration],label="E_Battery")
plt.plot(P_charge_values[:duration],label='P_charge')
plt.title('Battery')
plt.legend()

#IMPORT EXPORT
plt.figure()
#plt.hold(True)
plt.plot(PV_production[:duration],label="PV")
plt.plot(EL_consumption[:duration],label="EL")
plt.plot(Export_values[:duration],label="EXP")
plt.plot(Import_values[:duration],label="IMP")
plt.title('Import/Export')
plt.legend()

#WATER HEATER
plt.figure()
#plt.hold(True)
plt.plot(Q_DHW[:duration],label="Q_DHW")
plt.plot(P_waterheater_values[:duration],label="P_waterheater")
plt.plot(T_tank_values[:duration],label="T_tank")
plt.title('Water heater')
plt.legend()



#SPEACE HEATER
plt.figure()
plt.plot(Q_spaceheater_values[:duration],label="P_heatpump")
plt.plot(T_house_values[:duration],label="T_house")
plt.title('Space Heating')
plt.legend()





# create dataframe containing results
df_results = pd.DataFrame() 
df_results['PV[kW]']=PV_production[:duration]
df_results['EL[kW]']=EL_consumption[:duration]
df_results['Import[kW]']=Import_values[:duration]
df_results['Export[kW]']=Export_values[:duration]
df_results['Battery[kWh]']=Battery_levels[:duration]
df_results['P_charge[kW]']=P_charge_values[:duration]
df_results['T_tank[*C]']=T_tank_values[:duration]
df_results['P_waterheater[kW]']=P_waterheater_values[:duration]
df_results['T_house[*C]']=T_house_values[:duration]
df_results['Q_spaceheater[kW]']=Q_spaceheater_values[:duration]


df_results.to_csv(r'Results.csv')
# T_tank_values,P_waterheater_values,T_house_values,T_house_values,Q_spaceheater_values