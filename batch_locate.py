import os

import py_multi_geoloc

# Data sources
IP_list_file = 'ip_list'
source_dir = "data/"

# -> DB-IP
DB_IP_dir = source_dir + 'DB-IP/'
DB_IP_rtree_v4_file_suffix = "_dbip_IP_geo_rtree_v4.pickle"
DB_IP_rtree_v6_file_suffix = "_dbip_IP_geo_rtree_v6.pickle"

# -> Maxmind
Maxmind_dir = source_dir + 'Maxmind/'

# -> OpenIPMap
OpenIPMap_dir = source_dir + 'OpenIPMap/'
OpenIPMap_ip_index_file = OpenIPMap_dir + "openIPmap_IP_index_dict.pickle"
OpenIPMap_hostname_index_file = OpenIPMap_dir + "openIPmap_hostname_index_dict.pickle"
OpenIPMap_alias_data_file = OpenIPMap_dir + "openIPmap_alias_data_dict.pickle"
OpenIPMap_hostname_geo_dict_file = OpenIPMap_dir + "openIPmap_hostname_geo_dict.pickle"
OpenIPMap_rtree_v4_file = OpenIPMap_dir + "openIPmap_IP_geo_rtree_v4.pickle"
OpenIPMap_rtree_v6_file = OpenIPMap_dir + "openIPmap_IP_geo_rtree_v6.pickle"

# -> IP2location
IP2Location_dir = source_dir + 'IP2location/'
IP2Location_ipv4_db_bin_file = IP2Location_dir + "IP2Location_ipv4_bin_db.zip"
IP2Location_ipv6_db_bin_file = IP2Location_dir + "IP2Location_ipv6_bin_db.zip"


if __name__ == "__main__":
	
	# Finding latest DB-IP data file in directory
	DB_IP_max_date = 0
	for root, dirs, files in os.walk(DB_IP_dir):
	    for file in files:
	        if file.endswith('.csv'):
	            file_elts = file[:file.rfind('.')].split("-")
	            date = int(file_elts[-2] + file_elts[-1])
	            if date > DB_IP_max_date:
	            	DB_IP_max_date = date

	DB_IP_rtree_v4_file = DB_IP_dir + str(DB_IP_max_date) + DB_IP_rtree_v4_file_suffix
	DB_IP_rtree_v6_file = DB_IP_dir + str(DB_IP_max_date) + DB_IP_rtree_v6_file_suffix

	# Finding latest Maxmind data file in directory
	Maxmind_max_date = 0
	Maxmind_db_dir = ''
	for root, dirs, files in os.walk(Maxmind_dir):
	    for directory in dirs:
	    	if 'GeoLite2-City_' in directory:
	        	elements = directory.split('_')
	        	date = int(elements[-1])
	        	if date > Maxmind_max_date:
	        		Maxmind_max_date = date
	        		Maxmind_db_dir = directory

	Maxmind_db_dir = Maxmind_dir + Maxmind_db_dir + '/'
	Maxmind_db_file = Maxmind_db_dir
	for root, dirs, files in os.walk(Maxmind_db_dir):
		for file in files:
			if '.mmdb' in file:
				Maxmind_db_file = Maxmind_db_file + file

	# Finding latest IP2Location data file in directory

	IP2Location_ipv4_db_bin_path = IP2Location_ipv4_db_bin_file[:-4] + '/'
	IP2Location_ipv4_bin_file = ''
	for root, dirs, files in os.walk(IP2Location_ipv4_db_bin_path):
		for file in files:
			if '.BIN' in file:
				IP2Location_ipv4_bin_file = file
	IP2Location_ipv4_bin_file = IP2Location_ipv4_db_bin_path + IP2Location_ipv4_bin_file

	IP2Location_ipv6_db_bin_path = IP2Location_ipv6_db_bin_file[:-4] + '/'
	IP2Location_ipv6_bin_file = ''
	for root, dirs, files in os.walk(IP2Location_ipv6_db_bin_path):
		for file in files:
			if '.BIN' in file:
				IP2Location_ipv6_bin_file = file
	IP2Location_ipv6_bin_file = IP2Location_ipv6_db_bin_path + IP2Location_ipv6_bin_file

	source_data = py_multi_geoloc.load_data_source(Maxmind_db_file,
												   OpenIPMap_ip_index_file,
												   OpenIPMap_hostname_index_file,
												   OpenIPMap_hostname_geo_dict_file,
												   OpenIPMap_alias_data_file,
												   OpenIPMap_rtree_v4_file,
												   None,
												   IP2Location_ipv4_bin_file,
												   None,
												   DB_IP_rtree_v4_file,
												   None)

	with open(IP_list_file, 'rb') as ip_list:
		while True:
			line = ip_list.readline()
			if not line:
				break
			ip = line.rstrip('\r\n')
			multi_ip = py_multi_geoloc.locate_ip_multi(ip, source_data)
			if multi_ip['Maxmind']['city'] is None:
				multi_ip['Maxmind']['city'] = "None"
			if multi_ip['IP2Location']['city'] is None:
				multi_ip['IP2Location']['city'] = "None"
			if multi_ip['OpenIPmap']['city'] is None:
				multi_ip['OpenIPmap']['city'] = "None"
			if multi_ip['DB-IP']['city'] is None:
				multi_ip['DB-IP']['city'] = "None"
			print '\n', ip
			print '\tMaxmind: ', multi_ip['Maxmind']['city']
			print '\tIP2Location: ', multi_ip['IP2Location']['city']
			print '\tOpenIPmap: ', multi_ip['OpenIPmap']['city']
			print '\tDB-IP: ', multi_ip['DB-IP']['city']


