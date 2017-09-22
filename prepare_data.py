import os
import json
import netaddr
import radix
import pickle

# Data sources
source_dir = "data/"

# -> From OpenIPMap
OpenIPMap_dir = source_dir + 'OpenIPMap/'
OpenIPMap_ip_rules_file = OpenIPMap_dir + 'ip_rules.json'
OpenIPMap_hostname_rules_file = OpenIPMap_dir + 'hostname_rules.json'
OpenIPMap_mappings_file = OpenIPMap_dir + 'openipmap_mappings.csv'

# -> From DB-IP
# TODO take only root of file, list files in dir then prepare data
DB_IP_dir = source_dir + 'DB-IP/'

# Results file
# -> For OpenIPMap
OpenIPMap_ip_index_file = OpenIPMap_dir + "openIPmap_IP_index_dict.pickle"
OpenIPMap_hostname_index_file = OpenIPMap_dir + "openIPmap_hostname_index_dict.pickle"
OpenIPMap_alias_data_file = OpenIPMap_dir + "openIPmap_alias_data_dict.pickle"
OpenIPMap_hostname_geo_dict_file = OpenIPMap_dir + "openIPmap_hostname_geo_dict.pickle"
OpenIPMap_rtree_v4_file = OpenIPMap_dir + "openIPmap_IP_geo_rtree_v4.pickle"
OpenIPMap_rtree_v6_file = OpenIPMap_dir + "openIPmap_IP_geo_rtree_v6.pickle"

# -> For DB-IP
# TODO take only root of file, use data hint
DB_IP_country_geo_ip_file_suffix = "_dbip_country_ip.pickle"
DB_IP_city_geo_ip_file_suffix = "_dbip_country_city_ip.pickle"
DB_IP_rtree_v4_file_suffix = "_dbip_IP_geo_rtree_v4.pickle"
DB_IP_rtree_v6_file_suffix = "_dbip_IP_geo_rtree_v6.pickle"


def networks_from_range(ip_start, ip_end):
	
	cidr_list = []

	private_start = netaddr.IPAddress(ip_start).is_private()
	reserved_start = netaddr.IPAddress(ip_start).is_reserved()
	private_end = netaddr.IPAddress(ip_end).is_private()
	reserved_end = netaddr.IPAddress(ip_end).is_reserved()
	if private_start or private_end or reserved_start or reserved_end:
		return cidr_list
	
	cidr = netaddr.iprange_to_cidrs(ip_start, ip_end)
	for elt in cidr:
		cidr_list += [str(elt)]

	return cidr_list


def cidr_aggregate(cidr_list):
	global_cidr = []
	for elt in cidr_list:
		global_cidr += [netaddr.IPNetwork(elt)]
	cidr3 = netaddr.cidr_merge(global_cidr)
	return cidr3
	

# Parsing IP geolocation JSON file
def parse_dbip_file(file_name):

	country_geo_ip_dict = {}
	city_geo_ip_dict = {}
	rtree_v4 = None
	rtree_v6 = None

	rtree_v4 = radix.Radix()
	rtree_v6 = radix.Radix()

	with open(file_name, 'rb') as dbip:
		while True:
			line = dbip.readline()
			if not line:
				break
			line = line.rstrip('\r\n')
			# print line
			
			line = line.translate(None, '"')
			elts = line.split(',')

			ip_start = elts[0]
			ip_end = elts[1]
			country = elts[2]
			region = elts[3]
			city = elts[4]
			netlist = networks_from_range(ip_start, ip_end)
			for cidr in netlist:
				if netaddr.IPAddress(ip_start).version == 4:
					node = rtree_v4.add(cidr)
				elif netaddr.IPAddress(ip_start).version == 6:
					node = rtree_v6.add(cidr)
				node.data['country'] = country
				node.data['region'] = region
				node.data['city'] = city

				if country not in country_geo_ip_dict:
					country_geo_ip_dict[country] = []
				country_geo_ip_dict[country] += [cidr]

				if city not in city_geo_ip_dict:
					city_geo_ip_dict[city] = []
				city_geo_ip_dict[city] += [cidr]

	return country_geo_ip_dict, city_geo_ip_dict, rtree_v4, rtree_v6


# Parsing IP geolocation JSON file
def parse_geo_ip_file(file_name):
	ip_geo_data = {}
	with open(file_name) as ip_geo_json_file:
	    ip_geo_data = json.load(ip_geo_json_file)

	rtree_v4 = radix.Radix()
	rtree_v6 = radix.Radix()
	for element in ip_geo_data:
		ip_elt = element['ip']
		ip_net = netaddr.IPNetwork(ip_elt)
		if ip_net.version == 4:
			node = rtree_v4.add(str(ip_net))
		elif ip_net.version == 6:
			node = rtree_v6.add(str(ip_net))
		node.data['georesult'] = element['georesult']
		node.data['canonical_georesult'] = element['canonical_georesult']
		node.data['lat'] = element['lat']
		node.data['lon'] = element['lon']
		node.data['created'] = element['created']
		node.data['user'] = element['user']
		node.data['confidence'] = element['confidence']

	return rtree_v4, rtree_v6
		

# Parsing hostname geolocation JSON file
def parse_geo_hostname_file(file_name):
	hostname_geo_data = {}
	with open(file_name) as hostname_geo_json_file:
	    hostname_geo_data = json.load(hostname_geo_json_file)

	hostname_geo_dict = {}
	for element in hostname_geo_data:
		hostname_geo_dict[element['hostname']] = {}
		hostname_geo_dict[element['hostname']]['created'] = element['created']
		hostname_geo_dict[element['hostname']]['georesult'] = element['georesult']
		hostname_geo_dict[element['hostname']]['canonical_georesult'] = element['canonical_georesult']
		hostname_geo_dict[element['hostname']]['lat'] = element['lat']
		hostname_geo_dict[element['hostname']]['lon'] = element['lon']
		hostname_geo_dict[element['hostname']]['confidence'] = element['confidence']
		hostname_geo_dict[element['hostname']]['user'] = element['user']

	return hostname_geo_dict


def parse_geo_ip_hostname_file(file_name):
	ip_geo_hostname_data = {}
	hostname_geo_ip_data = {}
	alias_data = {}

	index = 0

	with open(file_name, 'rb') as team:
		while True:
			line = team.readline()
			if not line:
				break
			alias_data[index] = {}
			line = line.rstrip('\r\n')
			# print "----"
			# print line
			line_elts = line.split('"')
			alias_data[index]['canonical_georesult'] = line_elts[1]
			alias_data[index]['ip'] = netaddr.IPAddress(line_elts[0].split(',')[0]).value
			lat_elt = line_elts[0].split(',')[1]
			if lat_elt == 'None':
				alias_data[index]['lat'] = None
			else:
				alias_data[index]['lat'] = float(lat_elt)
			lon_elt = line_elts[0].split(',')[2]
			if lon_elt == 'None':
				alias_data[index]['lon'] = None
			else:
				alias_data[index]['lon'] = float(lon_elt)

			alias_data[index]['hostname'] = line_elts[2].split(',')[1]
			alias_data[index]['created'] = line_elts[2].split(',')[2]
			alias_data[index]['user'] = line_elts[2].split(',')[3]
			ip_geo_hostname_data[alias_data[index]['ip']] = index
			hostname_geo_ip_data[alias_data[index]['hostname']] = index

			index += 1

	return ip_geo_hostname_data, hostname_geo_ip_data, alias_data


if __name__ == "__main__":

	print '\nPreparing OpenIPMap data...'
	ip_index_dict = {}
	hostname_index_dict = {}
	alias_data_dict = {}
	ip_index_dict, hostname_index_dict, alias_data_dict = parse_geo_ip_hostname_file(OpenIPMap_mappings_file)

	hostname_geo_dict = {}
	hostname_geo_dict = parse_geo_hostname_file(OpenIPMap_hostname_rules_file)

	rtree_v4, rtree_v6 = parse_geo_ip_file(OpenIPMap_ip_rules_file)

	print "\tSaving OpenIPmap IP index dict..."
	with open(OpenIPMap_ip_index_file, 'wb') as handle:
		pickle.dump(ip_index_dict, handle, -1)

	print "\tSaving OpenIPmap hostname index dict..."
	with open(OpenIPMap_hostname_index_file, 'wb') as handle:
		pickle.dump(hostname_index_dict, handle, -1)

	print "\tSaving OpenIPmap alias data dict..."
	with open(OpenIPMap_alias_data_file, 'wb') as handle:
		pickle.dump(alias_data_dict, handle, -1)

	print "\tSaving OpenIPmap hostname geolocation dict..."
	with open(OpenIPMap_hostname_geo_dict_file, 'wb') as handle:
		pickle.dump(hostname_geo_dict, handle, -1)

	print "\tSaving OpenIPmap IPv4 geolocation radix tree..."
	with open(OpenIPMap_rtree_v4_file, 'wb') as handle:
		pickle.dump(rtree_v4, handle, -1)

	print "\tSaving OpenIPmap IPv6 geolocation radix tree..."
	with open(OpenIPMap_rtree_v6_file, 'wb') as handle:
		pickle.dump(rtree_v6, handle, -1)

	print '\nPreparing DB-IP data...'
	dbip_country_geo_ip_dict = {}
	dbip_city_geo_ip_dict = {}
	dbip_rtree_v4 = None
	dbip_rtree_v6 = None

	# Finding latest data file in directory
	dbip_file = ''
	max_cat = 0
	for root, dirs, files in os.walk(DB_IP_dir):
	    for file in files:
	        if file.endswith('.csv'):
	            file_elts = file[:file.rfind('.')].split("-")
	            cat = int(file_elts[-2] + file_elts[-1])
	            if cat > max_cat:
	            	max_cat = cat
	            	to_parse = file

	dbip_file = DB_IP_dir + to_parse

	dbip_country_geo_ip_dict, dbip_city_geo_ip_dict, dbip_rtree_v4, dbip_rtree_v6 = parse_dbip_file(dbip_file)

	print "Saving dbip country_geo_ip_dict..."
	dbip_country_geo_ip_file = DB_IP_dir + str(max_cat) + DB_IP_country_geo_ip_file_suffix
	with open(dbip_country_geo_ip_file, 'wb') as handle:
		pickle.dump(dbip_country_geo_ip_dict, handle, -1)

	print "Saving dbip city_geo_ip_dict..."
	dbip_city_geo_ip_file = DB_IP_dir + str(max_cat) + DB_IP_city_geo_ip_file_suffix
	with open(dbip_city_geo_ip_file, 'wb') as handle:
		pickle.dump(dbip_city_geo_ip_dict, handle, -1)

	print "Saving dbip rtree_v4..."
	dbip_rtree_v4_file = DB_IP_dir + str(max_cat) + DB_IP_rtree_v4_file_suffix
	with open(dbip_rtree_v4_file, 'wb') as handle:
		pickle.dump(dbip_rtree_v4, handle, -1)

	print "Saving dbip rtree_v6..."
	dbip_rtree_v6_file = DB_IP_dir + str(max_cat) + DB_IP_rtree_v6_file_suffix
	with open(dbip_rtree_v6_file, 'wb') as handle:
		pickle.dump(dbip_rtree_v6, handle, -1)
