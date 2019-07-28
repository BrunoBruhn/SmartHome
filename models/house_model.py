class house(object):
	def __init__(self,room_area,room_surface,room_height,average_U_value,T_min_house,T_max_house,T_house_initial):

		self.room_area=room_area
		self.room_surface=room_surface
		self.room_height=room_height 
		self.average_U_value=average_U_value #W/m2K
		self.T_min_house=T_min_house
		self.T_max_house=T_max_house
		self.T_house_initial=T_house_initial

		self.q_loss=self.average_U_value*self.room_surface/1000 #kW/K
		self.mcp=self.room_area*self.room_height*1.2 #kJ/K
