import csv,pulp
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import *

########################################################################################
'INITIALIZE PROBLEM'

duration=1440 #
#init problem and creating object-independent LP variables
LP = pulp.LpProblem('LP',pulp.LpMinimize)  

Import = pulp.LpVariable.dicts("Import", range(duration), lowBound=0,cat=pulp.LpContinuous )
Export = pulp.LpVariable.dicts("Export", range(duration), lowBound=0,cat=pulp.LpContinuous)
Cost = pulp.LpVariable.dicts("Cost", range(duration), cat=pulp.LpContinuous)

MAX_solving_time = 15 #seconds
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
Price_export = 10.64 # (Juni 2019, Germany)

########################################################################################
'ADDING BATTERY OBJECT'

import battery
E_battery_max=10 #kWh 
eta_n=1
P_charge_max=20
P_discharge_max=20

E_battery,P_charge = battery.optim(duration,LP,E_battery_max*3600,P_charge_max,P_discharge_max,eta_n)


########################################################################################
'SET UP ENERGY BALANCE AND OBJECTIVE, THEN SOLVE'

for t in range(duration):

	LP += PV_production[t] -EL_consumption[t] -P_charge[t] == Export[t] - Import[t]

	LP += Cost[t]==Import[t]*Price_import[t]-Export[t]*Price_export

LP += sum([Cost[t] for t in range(duration)])

status = LP.solve(pulp.solvers.GUROBI(mip=True, msg=True, timeLimit=MAX_solving_time,epgap=MAX_gap))

print( 'LP status: ' + pulp.LpStatus[status] + '')

########################################################################################
'CREATE LISTS CONTAINING THE VARIABLE PROFILES'

Import_values=[]
Export_values=[]
Energy_levels=[]
P_charge_values=[]

for i in range(duration):
	Import_values.append(Import[i].value())
	Export_values.append(Export[i].value())
	Energy_levels.append(E_battery[i].value()/10**4)
	P_charge_values.append(P_charge[i].value())

########################################################################################
'PLOT PROFILES'

plt.plot(PV_production[:duration],label="PV")
plt.plot(EL_consumption[:duration],label="EL")
plt.plot(Export_values[:duration],label="EXP")
plt.plot(Import_values[:duration],label="IMP")
plt.plot(Energy_levels[:duration],label="E battery")
plt.plot(Price_import[:duration],label='Price_import')
plt.plot(P_charge_values[:duration],label='P_charge')
plt.legend()
plt.show()