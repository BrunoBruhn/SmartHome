import matplotlib.pyplot as plt

def show(duration,Import,Export,E_battery,P_charge_battery,T_tank,P_waterheater,T_house,P_heatpump,COP_heatpump,P_aircon,COP_aircon,E_EV,Price_import,PV_production,EL_consumption,Q_DHW,T_outside):

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

	for i in range(duration):
		Import_values.append(Import[i].value())
		Export_values.append(Export[i].value())
		Battery_levels.append(E_battery[i].value()/360) #now ckWh
		P_charge_battery_values.append(P_charge_battery[i].value())
		T_tank_values.append(T_tank[i].value())
		P_waterheater_values.append(P_waterheater[i].value())
		T_house_values.append(T_house[i].value())
		Q_spaceheater_values.append(P_heatpump[i].value()*COP_heatpump*100)
		Q_aircon_values.append(P_aircon[i].value()*COP_aircon*100)
		E_EV_values.append(E_EV[i].value()/360) #now ckWh

	#BATTERY
	plt.figure()
	plt.plot(Price_import[:duration],label="Price")
	plt.plot(PV_production[:duration],label="PV")
	plt.plot(EL_consumption[:duration],label="EL")
	plt.plot(Battery_levels[:duration],label="E_Battery")
	plt.plot(P_charge_battery_values[:duration],label='P_charge_battery')
	plt.title('Battery')
	plt.legend()

	#IMPORT EXPORT
	plt.figure()
	plt.plot(Price_import[:duration],label="Price")
	plt.plot(PV_production[:duration],label="PV")
	plt.plot(EL_consumption[:duration],label="EL")
	plt.plot(Export_values[:duration],label="Export")
	plt.plot(Import_values[:duration],label="Import")
	plt.title('Import/Export')
	plt.legend()

	#WATER HEATER
	plt.figure()
	plt.plot(Price_import[:duration],label="Price")
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
	plt.plot(Price_import[:duration],label="Price")
	plt.plot(E_EV_values[:duration],label="E_EV")
	plt.title('Electric Vehicle')
	plt.legend()

	#ALL
	plt.figure()
	plt.title('ALL')
	plt.plot(Price_import[:duration],label="Price")
	plt.plot(PV_production[:duration],label="PV")
	plt.plot(EL_consumption[:duration],label="EL")
	plt.plot(P_charge_battery_values[:duration],label='P_charge_battery')
	plt.plot(PV_production[:duration],label="PV")
	plt.plot(EL_consumption[:duration],label="EL")
	plt.plot(Export_values[:duration],label="Export")
	plt.plot(Import_values[:duration],label="Import")
	plt.plot(P_waterheater_values[:duration],label="P_waterheater")
	plt.plot(E_EV_values[:duration],label="E_EV")
	plt.legend()

	import pandas as pd


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




	plt.show()