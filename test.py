def search_special_aspects(aspect_table):
	yods=[]
	gt=[]
	gc=[]
	stel=[]
	tsq=[]

	for i in xrange(10):
		pn=swisseph.get_planet_name(i)
		count=0
		#valid_entries=[x for x, y in enumerate(aspect_table) if y[0] == pn or y[1] == pn]
		trine_entries=[y for x, y in enumerate(aspect_table) \
		if (y[0] == pn or y[1] == pn) and y[2] == 'trine']
		square_entries=[y for x, y in enumerate(aspect_table) \
		if (y[0] == pn or y[1] == pn) and y[2] == 'square']
		sextile_entries=[y for x, y in enumerate(aspect_table) \
		if (y[0] == pn or y[1] == pn) and y[2] == 'sextile']
		conjunction_entries=[y for x, y in enumerate(aspect_table) \
		if (y[0] == pn or y[1] == pn) and y[2] == 'conjunction']
		inconjunct_entries=[y for x, y in enumerate(aspect_table) \
		if (y[0] == pn or y[1] == pn) and y[2] == 'inconjunct']
		opposition_entries=[y for x, y in enumerate(aspect_table) \
		if (y[0] == pn or y[1] == pn) and y[2] == 'opposition']
		intersection_entries=[]
		intersection_entries2=[]
		intersection_entries3=[]
		intersection_entries4=[]
		intersection_entries5=[]
		#map(itemgetter(0), aspect_table)
		#print "Valid entries for %s" % pn
		if len(trine_entries) > 2:
			for n in trine_entries:
				if n[0] != pn:
					a=[y for x, y in enumerate(aspect_table) if y[0] == n[0] and y[2] == 'trine']
					b=[y for x, y in enumerate(a) if y[1] == n[1]]
					if len(b) > 0:
						intersection_entries.append(b[0])
				else:
					a=[y for x, y in enumerate(aspect_table) if y[1] == n[1] and y[2] == 'trine']
					b=[y for x, y in enumerate(a) if y[0] == n[0]]
				if len(b) > 0:
					intersection_entries.append(b[0])
				if len(intersection_entries) > 2:
					#print intersection_entries
					gt.append(intersection_entries)
					break
		if len(opposition_entries) > 0:
			for n in opposition_entries:
				if n[0] != pn:
					a=[y for x, y in enumerate(aspect_table) if y[0] == n[0] and y[2] == 'square']
					b=[y for x, y in enumerate(aspect_table) if y[0] == n[0] and y[2] == 'opposition']
				else:
					#print "Searching %s entries" % n[0]
					a=[y for x, y in enumerate(aspect_table) if y[1] == n[1] and y[2] == 'square']
					b=[y for x, y in enumerate(aspect_table) if y[1] == n[1] and y[2] == 'opposition']
				if len(b) > 0 and len(a) > 0 and \
				(a not in intersection_entries2 and \
				b not in intersection_entries2):
					intersection_entries2.append(a[0])
					intersection_entries2.append(b[0])
				if len(intersection_entries2) > 3:
					intersection_entries2.append(n)
					gc.append(intersection_entries2)
					break
		if len(square_entries) > 2:
			for i in xrange(len(square_entries)-1):
				otherp=""
				otherp2=""
				if square_entries[i][0] != pn:
					otherp=square_entries[i][0]
				else:
					otherp=square_entries[i][1]
				if square_entries[i+1][0] != pn:
					otherp2=square_entries[i+1][0]
				else:
					otherp2=square_entries[i+1][1]
				miniopposition=[y for x, y in enumerate(aspect_table) \
					if ((y[0] == otherp and y[1] == otherp2) or \
					(y[0] == otherp2 and y[1] == otherp)) and y[2] == 'opposition']
				if len(miniopposition) > 0:
					intersection_entries3.append(square_entries[i])
					intersection_entries3.append(square_entries[i+1])
				for j in miniopposition:
					intersection_entries3.append(j)
				if len(intersection_entries3) > 2:
					#print intersection_entries
					tsq.append(intersection_entries4)
					break
		if len(conjunction_entries) > 3:
			for n in conjunction_entries:
				if n[0] != pn:
					a=[y for x, y in enumerate(aspect_table) if y[0] == n[0] and y[2] == 'conjunction']
					b=[y for x, y in enumerate(a) if y[1] == n[1] and y[2] == 'conjunction']
				else:
					#print "Searching %s entries" % n[0]
					a=[y for x, y in enumerate(aspect_table) if y[1] == n[1] and y[2] == 'conjunction']
					b=[y for x, y in enumerate(a) if y[0] == n[0]]
				if len(b) > 0:
					intersection_entries4.append(b[0])
				if len(intersection_entries4) > 2:
					#print intersection_entries
					stel.append(intersection_entries4)
					break
		if len(inconjunct_entries) > 1:
			for i in xrange(len(inconjunct_entries)-1):
				otherp=""
				otherp2=""
				if inconjunct_entries[i][0] != pn:
					otherp=inconjunct_entries[i][0]
				else:
					otherp=inconjunct_entries[i][1]
				if inconjunct_entries[i+1][0] != pn:
					otherp2=inconjunct_entries[i+1][0]
				else:
					otherp2=inconjunct_entries[i+1][1]
				minisextiles=[y for x, y in enumerate(aspect_table) \
					if ((y[0] == otherp and y[1] == otherp2) or \
					(y[0] == otherp2 and y[1] == otherp)) and y[2] == 'sextile']
				if len(minisextiles) > 0:
					intersection_entries5.append(inconjunct_entries[i])
					intersection_entries5.append(inconjunct_entries[i+1])
				for j in minisextiles:
					intersection_entries5.append(j)
				if len(intersection_entries5) > 0:
					#print intersection_entries
					yods.append(intersection_entries5)
					break

	#clean up the entries of special configs by removing entries describing the same relationship
	gt=[x for i,x in enumerate(gt) if x not in gt[i+1:]]
	yods=[x for i,x in enumerate(yods) if x not in yods[i+1:]]
	gc=[x for i,x in enumerate(gc) if x not in gc[i+1:]]
	stel=[x for i,x in enumerate(stel) if x not in stel[i+1:]]
	tsq=[x for i,x in enumerate(tsq) if x not in tsq[i+1:]]

	return yods,gt,gc,stel,tsq
			#print "--"

			#'yod':((1,'inconjunct'),(2,'sextile')),