
def merge_nearby_regions(elongated_droplets):
#	twins = {}
#	print("WARNING: Sketchy logic ahead!!")
#	
#	for i in range(len(elongated_droplets)):
#		loc = elongated_droplets[i].centroid
#		loc = (loc[0]/spacing, loc[1]/spacing)
#		bbox = elongated_droplets[i].bbox
#		w = bbox[3] - bbox[1]
#		h = bbox[2] - bbox[0]
#	
#	#	print("\n", round(elongated_droplets[i].area_filled,2))
#	#	print("Loc:", loc, "\nbbox:", bbox, "\nw:", w, "\th:", h)
#	
#		for j in range(len(elongated_droplets)):
#			if i != j:
#				loc2 = elongated_droplets[j].centroid
#				loc2 = (loc2[0]/spacing, loc2[1]/spacing)
#				bbox2 = elongated_droplets[j].bbox
#				w2 = bbox2[3] - bbox2[1]
#				h2 = bbox2[2] - bbox2[0]
#	
#				bounds_y = (loc[0] - h - h2, loc[0] + h + h2)
#				bounds_x = (loc[1] - w - w2, loc[1] + w + w2)
#	
#	#			print("\t", round(elongated_droplets[j].area_filled,2))
#	#			print("\tBounds:", bounds_y, bounds_x)
#				if bounds_y[0] < loc2[0] < bounds_y[1] and\
#				   bounds_x[0] < loc2[1] < bounds_x[1]:
#					if i in twins:
#						if j not in twins[i]:
#							twins[i].append(j)
#					else:
#						# Isn't a key yet, could be a value somewhere
#						if j in twins:
#							if i not in twins[j]:
#								twins[j].append(i)
#						else:
#							twins[i] = [j]
#	
#					print("Twins:", round(elongated_droplets[i].area_filled,2),\
#									round(elongated_droplets[j].area_filled,2))
#	
#	for i in range(len(elongated_droplets)):
#		print(i, round(elongated_droplets[i].area_filled,2))
#	print(twins)
#	
#	twins_new = {}
#	
#	for k,v	in twins.items():
#		for val in v:
#			if val in twins:
#				duplicate = True
#				for j in twins[val]:
#					if j not in v:
#						duplicate = False
#				
#	
#	print(twins)
	elongated_droplets_new = elongated_droplets
	round_droplets_new = []
	return (elongated_droplets_new, round_droplets_new)
