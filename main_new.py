import csv,pulp
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import *
df=pd.read_csv('profiles.csv')
df=df.round(decimals=3)
PV_production = df['PV'].tolist()
EL_consumption = df['EL'].tolist()
Price_import = df['CP_IM'].tolist()
Price_export = 2
E_battery_max=10*3600 #kJ 
eta_n=1

duration=1440 #	<=	365 * 1440

#SOC_new=SOC_last+difference_kwh/Battery_capacity
#Export=difference_kwh-(SOC_new-SOC_last)*Battery_capacity

#init problem
LP = pulp.LpProblem('LP',pulp.LpMinimize)  

#add variables
E_battery = pulp.LpVariable.dicts("E_battery", range(duration), cat=pulp.LpContinuous, lowBound=0, upBound=E_battery_max)
Import = pulp.LpVariable.dicts("Import", range(duration), lowBound=0,cat=pulp.LpContinuous )
Export = pulp.LpVariable.dicts("Export", range(duration), lowBound=0,cat=pulp.LpContinuous)
Cost = pulp.LpVariable.dicts("Cost", range(duration), cat=pulp.LpContinuous)
P_charge = pulp.LpVariable.dicts("P_charge", range(duration), cat=pulp.LpContinuous, upBound=20,lowBound=-20)


for t in range(duration):
	if t==0:
		LP += E_battery[t]==60*P_charge[t]

	else:
		LP += E_battery[t]==E_battery[t-1]+60*P_charge[t]*eta_n

	LP += PV_production[t] -EL_consumption[t] -P_charge[t] == Export[t] - Import[t]

	LP += Cost[t]==Import[t]*Price_import[t]-Export[t]*Price_export

LP += sum([Cost[t] for t in range(duration)])

status = LP.solve(pulp.solvers.GUROBI(mip=True, msg=True, timeLimit=15,epgap=None))

print( 'LP status: ' + pulp.LpStatus[status] + '')

Import_values=[]
Export_values=[]
Energy_levels=[]
P_charge_values=[]

for i in range(duration):
	Import_values.append(Import[i].value())
	Export_values.append(Export[i].value())
	Energy_levels.append(E_battery[i].value()/10**4)
	P_charge_values.append(P_charge[i].value())

plt.plot(PV_production[:duration],label="PV")
plt.plot(EL_consumption[:duration],label="EL")
plt.plot(Export_values[:duration],label="EXP")
plt.plot(Import_values[:duration],label="IMP")
plt.plot(Energy_levels[:duration],label="E battery")
plt.plot(Price_import[:duration],label='Price_import')
plt.plot(P_charge_values[:duration],label='P_charge')
plt.legend()
plt.show()