import pickle
import netaddr
import geoip2.database
import IP2Location


def load_data_source(geodb_file,
					 oim_ip_index_file,
					 oim_hostname_index_file,
					 oim_hostname_geo_dict_file,
					 oim_alias_data_file,
					 oim_rtree_v4_file,
					 oim_rtree_v6_file,
					 ip2location_v4_db_file,
					 ip2location_v6_db_file,
					 dbip_rtree_v4_file,
					 dbip_rtree_v6_file):
	
	source_data = {}
	
	geoip2_reader = None
	if geodb_file is not None:
		geoip2_reader = geoip2.database.Reader(geodb_file)
	
	# Maxmind's GeoIP2
	print "Loading Maxmind..."
	source_data['Maxmind'] = {}
	source_data['Maxmind']['geoip2_reader'] = geoip2_reader

	# OpenIPMap
	print "Loading OpenIPMap..."
	source_data['OpenIPmap'] = {}
	source_data['OpenIPmap']['ip_index_dict'] = {}
	source_data['OpenIPmap']['hostname_index_dict'] = {}
	source_data['OpenIPmap']['alias_data_dict'] = {}
	if oim_ip_index_file is not None:
		with open(oim_ip_index_file, 'rb') as handle:
			source_data['OpenIPmap']['ip_index_dict'] = pickle.load(handle)
	if oim_hostname_index_file is not None:
		with open(oim_hostname_index_file, 'rb') as handle:
			source_data['OpenIPmap']['hostname_index_dict'] = pickle.load(handle)
	if oim_alias_data_file is not None:
		with open(oim_alias_data_file, 'rb') as handle:
			source_data['OpenIPmap']['alias_data_dict'] = pickle.load(handle)

	source_data['OpenIPmap']['hostname_geo_dict'] = {}
	if oim_hostname_geo_dict_file is not None:
		with open(oim_hostname_geo_dict_file, 'rb') as handle:
			source_data['OpenIPmap']['hostname_geo_dict'] = pickle.load(handle)

	source_data['OpenIPmap']['rtree_v4'] = None
	source_data['OpenIPmap']['rtree_v6'] = None
	if oim_rtree_v4_file is not None:
		with open(oim_rtree_v4_file, 'rb') as handle:
			source_data['OpenIPmap']['rtree_v4'] = pickle.load(handle)
	if oim_rtree_v6_file is not None:
		with open(oim_rtree_v6_file, 'rb') as handle:
			source_data['OpenIPmap']['rtree_v6'] = pickle.load(handle)

	# IP2Location
	print "Loading IP2Location..."
	source_data['IP2Location'] = {}
	if ip2location_v4_db_file is not None:
		source_data['IP2Location']['IP2Loc_v4'] = IP2Location.IP2Location()
		source_data['IP2Location']['IP2Loc_v4'].open(ip2location_v4_db_file)
	if ip2location_v6_db_file is not None:
		source_data['IP2Location']['IP2Loc_v6'] = IP2Location.IP2Location()
		source_data['IP2Location']['IP2Loc_v6'].open(ip2location_v6_db_file)

	# DB-IP
	print "Loading DB-IP..."
	source_data['DB-IP'] = {}

	source_data['DB-IP']['rtree_v4'] = None
	source_data['DB-IP']['rtree_v6'] = None
	if dbip_rtree_v4_file is not None:
		with open(dbip_rtree_v4_file, 'rb') as handle:
			source_data['DB-IP']['rtree_v4'] = pickle.load(handle)
	if dbip_rtree_v6_file is not None:
		with open(dbip_rtree_v6_file, 'rb') as handle:
			source_data['DB-IP']['rtree_v6'] = pickle.load(handle)

	return source_data


def locate_ip_oim(ip_addr,
				  oim_source_data):
	result = {}
	result['ip'] = ip_addr
	result['ip_version'] = 0
	result['city'] = None
	result['region'] = None
	result['country'] = None
	result['latitude'] = None
	result['longitude'] = None
	# result['created'] = None
	# result['user'] = None
	result['confidence'] = None
	result['hostname'] = None

	ip_index_dict = oim_source_data['ip_index_dict']
	alias_data_dict = oim_source_data['alias_data_dict']
	hostname_geo_dict = oim_source_data['hostname_geo_dict']
	rtree_v4 = oim_source_data['rtree_v4']
	rtree_v6 = oim_source_data['rtree_v6']

	ip_addr_obj = netaddr.IPAddress(ip_addr)
	result['ip_version'] = ip_addr_obj.version
	ip_geo_data = None
	if result['ip_version'] == 4 and rtree_v4 is not None:
		ip_geo_data = rtree_v4.search_best(ip_addr)
	elif result['ip_version'] == 6 and rtree_v6 is not None:
		ip_geo_data = rtree_v6.search_best(ip_addr)
	elif rtree_v6 is None or rtree_v4 is None:
		result['confidence'] = 0
	alias_geo_data = None
	host_geo_data = None
	if ip_addr_obj.value in ip_index_dict:
		alias_geo_data = alias_data_dict[ip_index_dict[ip_addr_obj.value]]
		host_geo_data = hostname_geo_dict[alias_geo_data['hostname']]

	# favour CSV data over hostname geo data over IP geo data
	if ip_geo_data is not None:
		ip_canonical_georesult = ip_geo_data['canonical_georesult']
		ip_canonical_georesult_elts = ip_canonical_georesult.split(',')
		result['city'] = ip_canonical_georesult_elts[0]
		result['region'] = ip_canonical_georesult_elts[1]
		result['country'] = ip_canonical_georesult_elts[2]
		result['latitude'] = ip_geo_data['lat']
		result['longitude'] = ip_geo_data['lon']
		# result['created'] = ip_geo_data['created']
		# result['user'] = ip_geo_data['user']
		result['confidence'] = ip_geo_data['confidence']
	if host_geo_data is not None:
		host_canonical_georesult = host_geo_data['canonical_georesult']
		if host_canonical_georesult is not None:
			host_canonical_georesult_elts = host_canonical_georesult.split(',')
		else:
			host_canonical_georesult_elts = [None, None, None]
		result['city'] = host_canonical_georesult_elts[0]
		result['region'] = host_canonical_georesult_elts[1]
		result['country'] = host_canonical_georesult_elts[2]
		result['latitude'] = host_geo_data['lat']
		result['longitude'] = host_geo_data['lon']
		# result['created'] = host_geo_data['created']
		# result['user'] = host_geo_data['user']
		result['confidence'] = host_geo_data['confidence']
	if alias_geo_data is not None:
		alias_canonical_georesult = alias_geo_data['canonical_georesult']
		if host_canonical_georesult is not None:
			alias_canonical_georesult_elts = alias_canonical_georesult.split(',')
		else:
			alias_canonical_georesult_elts = [None, None, None]
		# print alias_canonical_georesult_elts
		result['city'] = alias_canonical_georesult_elts[0]
		result['region'] = alias_canonical_georesult_elts[1]
		result['country'] = alias_canonical_georesult_elts[2]
		result['latitude'] = alias_geo_data['lat']
		result['longitude'] = alias_geo_data['lon']
		# result['created'] = alias_geo_data['created']
		# result['user'] = alias_geo_data['user']
		result['hostname'] = alias_geo_data['hostname']

	return result


def locate_ip_dbip(ip_addr,
				   dbip_source_data):
	result = {}
	result = {}
	result['ip'] = ip_addr
	result['ip_version'] = 0
	result['city'] = None
	result['region'] = None
	result['country'] = None

	rtree_v4 = None
	if 'rtree_v4' in dbip_source_data:
		rtree_v4 = dbip_source_data['rtree_v4']
	rtree_v6 = None
	if 'rtree_v6' in dbip_source_data:
		rtree_v6 = dbip_source_data['rtree_v6']

	ip_addr_obj = netaddr.IPAddress(ip_addr)
	result['ip_version'] = ip_addr_obj.version
	ip_geo_data = None
	if result['ip_version'] == 4 and rtree_v4 is not None:
		ip_geo_data = rtree_v4.search_best(ip_addr)
	elif result['ip_version'] == 6 and rtree_v6 is not None:
		ip_geo_data = rtree_v6.search_best(ip_addr)
	
	if ip_geo_data is not None:
		# print "ip_geo_data for ", ip_addr, " : ", ip_geo_data.data
		result['country'] = ip_geo_data.data['country']
		result['region'] = ip_geo_data.data['region']
		result['city'] = ip_geo_data.data['city']

	return result


def locate_ip_max(ip_addr,
				  maxmind_source_data):
	
	# TODO Try to get region granularity for subdivisions
	result = {}
	result['ip'] = ip_addr
	result['ip_version'] = 0
	result['city'] = None
	result['country'] = None
	result['latitude'] = None
	result['longitude'] = None
	result['confidence'] = None
	result['hostname'] = None

	geoip2_reader = maxmind_source_data['geoip2_reader']
	if geoip2_reader is None:
		ip_addr_obj = netaddr.IPAddress(ip_addr)
		result['ip_version'] = ip_addr_obj.version
		result['confidence'] = 0
		return result

	try:
		response = geoip2_reader.city(ip_addr)
		ip_addr_obj = netaddr.IPAddress(ip_addr)
		result['ip_version'] = ip_addr_obj.version
		result['city'] = response.city.name
		result['country'] = str(response.country.iso_code)
		result['latitude'] = response.location.latitude
		result['longitude'] = response.location.latitude
		# Compute a confidence score:
		# Null if radius over 1000 km
		# equals to accuracy_radius / 1000 in % otherwise
		if response.location.accuracy_radius is None:
			result['confidence'] = 0
		elif response.location.accuracy_radius > 1000:
			result['confidence'] = 0
		else:
			result['confidence'] = int(response.location.accuracy_radius) / 10
		result['hostname'] = None
	except geoip2.errors.AddressNotFoundError:
	    pass

	return result


def locate_ip_i2l(ip_addr,
				  ip2loc_source_data):
	
	result = {}
	result['ip'] = ip_addr
	result['ip_version'] = 0
	result['city'] = None
	result['country'] = None
	result['latitude'] = None
	result['longitude'] = None
	result['confidence'] = 0
	result['hostname'] = None

	IP2Loc_v4 = None
	if 'IP2Loc_v4' in ip2loc_source_data:
		IP2Loc_v4 = ip2loc_source_data['IP2Loc_v4']
	IP2Loc_v6 = None
	if 'IP2Loc_v6' in ip2loc_source_data:
		IP2Loc_v6 = ip2loc_source_data['IP2Loc_v6']

	ip_addr_obj = netaddr.IPAddress(ip_addr)
	result['ip_version'] = ip_addr_obj.version
	response = None
	if result['ip_version'] == 4 and IP2Loc_v4 is not None:
		response = IP2Loc_v4.get_all(ip_addr)
	elif result['ip_version'] == 6 and IP2Loc_v6 is not None:
		response = IP2Loc_v6.get_all(ip_addr)
	if response is not None:
		result['ip'] = response.ip
		result['city'] = response.city
		result['country'] = response.country_short
		result['latitude'] = response.latitude
		result['longitude'] = response.longitude
		# Confidence expresses the fact that the ip
		# given in the response is the ip of the response.
		if response.ip == ip_addr:
			result['confidence'] = 100

	return result


def locate_ip_multi(ip_addr,
					source_data):

	result = {}
	result['Maxmind'] = locate_ip_max(ip_addr,
									  source_data['Maxmind'])
	result['IP2Location'] = locate_ip_i2l(ip_addr,
				  						  source_data['IP2Location'])
	result['OpenIPmap'] = locate_ip_oim(ip_addr,
				  						source_data['OpenIPmap'])
	result['DB-IP'] = locate_ip_dbip(ip_addr,
									 source_data['DB-IP'])

	return result


def has_duplicates(seq):
    return any(seq.count(x) > 1 for x in seq)


def locate_ip(ip_addr,
			  criteria,
			  source_data):
	
	result = {}
	result['ip'] = ip_addr
	result['ip_version'] = 0
	result['city'] = None
	result['country'] = None
	result['latitude'] = None
	result['longitude'] = None
	result['confidence'] = None
	result['hostname'] = None

	multi_result = locate_ip_multi(ip_addr, source_data)

	if criteria == "confidence":
		# print criteria
		# print "Maxmind: ", multi_result['Maxmind']['confidence']
		# print "IP2Location: ", multi_result['IP2Location']['confidence']
		# print "OpenIPmap: ", multi_result['OpenIPmap']['confidence']
		
		# Sources are ordered in the confidence_set by preferenec order
		# We prefer OpenIPMap over Maxmind over IP2Location in case of a tie
		# The reason is OpenIPMap is better for infrastructure IPs, Maxmind is the
		# commercial leader. DB-IP is last
		providers = ['OpenIPmap', 'Maxmind', 'IP2Location', 'DB-IP']
		confidence_set = [multi_result[providers[0]]['confidence'],
						  multi_result[providers[1]]['confidence'],
						  multi_result[providers[2]]['confidence'],
						  multi_result[providers[3]]['confidence']]
		# print max(confidence_set)
		max_indexes = [i for i, j in enumerate(confidence_set) if j == max(confidence_set)]
		# print providers[max_indexes[0]]
		result = multi_result[providers[max_indexes[0]]]

	elif criteria == "consensus":
		# TODO implement criteria
		print criteria, " will be implemented later"

	else:
		print "Criteria should be:"
		print "* 'confidence'"
		print "* 'consensus'"

	return result
