import os
import requests
import zipfile
import tarfile
import gzip
import shutil

# Accounts file
accounts_file = 'accounts.use'

# Data sources
source_dir = "data/"

# -> IP2location
IP2Location_dir = source_dir + 'IP2location/'
IP2Location_login_url = 'http://lite.ip2location.com/login'
IP2Location_ipv4_db_csv_url = 'http://lite.ip2location.com/download?id=9'
IP2Location_ipv4_db_bin_url = 'http://lite.ip2location.com/download?id=10'
IP2Location_ipv6_db_csv_url = 'http://lite.ip2location.com/download?id=19'
IP2Location_ipv6_db_bin_url = 'http://lite.ip2location.com/download?id=20'
IP2Location_ipv4_db_bin_file = IP2Location_dir + "IP2Location_ipv4_bin_db.zip"
IP2Location_ipv6_db_bin_file = IP2Location_dir + "IP2Location_ipv6_bin_db.zip"
IP2Location_ipv4_db_csv_file = IP2Location_dir + "IP2Location_ipv4_csv_db.zip"
IP2Location_ipv6_db_csv_file = IP2Location_dir + "IP2Location_ipv6_csv_db.zip"

# -> Maxmind
Maxmind_dir = source_dir + 'Maxmind/'
Maxmind_db_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz'
Maxmind_db_file = Maxmind_dir + 'GeoLite2-City.tar.gz'

# -> OpenIPMap
OpenIPMap_dir = source_dir + 'OpenIPMap/'
OpenIPMap_login_url = 'https://access.ripe.net'
OpenIPMap_mappings_url = 'https://marmot.ripe.net/static/openipmap.mappings.csv'
OpenIPMap_mappings_file = OpenIPMap_dir + 'openipmap_mappings.csv'
OpenIPMap_hostname_rules_url = 'https://marmot.ripe.net/openipmap/api/hostname_rules/?format=json'
OpenIPMap_hostname_rules_file = OpenIPMap_dir + 'hostname_rules.json'
OpenIPMap_ip_rules_url = 'https://marmot.ripe.net/openipmap/api/ip_rules/?format=json'
OpenIPMap_ip_rules_file = OpenIPMap_dir + 'ip_rules.json'

# -> DB-IP
DB_IP_dir = source_dir + 'DB-IP/'
DB_IP_generic_url = 'https://db-ip.com/db/download/city'


def retrieve_protected_file(login_url, login_payload, file_url, file_name):
	
	with requests.session() as c:
		print '\tLogging in ' + login_url + '...'
		c.post(login_url, data=login_payload)
		print '\tDownloading ' + file_name + ' from ' + file_url + '...'
		response = c.get(file_url)
		with open(file_name, "wb") as f:
			f.write(response.content)

	return


def retrieve_file(file_url, file_name):

	print '\tDownloading ' + file_name + ' from ' + file_url + '...'
	response = requests.get(file_url)
	with open(file_name, "wb") as f:
		f.write(response.content)

	return


def retrieve_protected_files(login_url, login_payload, file_list):
	
	with requests.session() as c:
		print '\tLogging in ' + login_url + '...'
		c.post(login_url, data=login_payload)
		for element in file_list:
			file_url = element[0]
			file_name = element[1]
			print '\tDownloading ' + file_name + ' from ' + file_url + '...'
			response = c.get(file_url)
			with open(file_name, "wb") as f:
				f.write(response.content)

	return


def unzip(file, path):
	print '\tUnzipping ' + file + ' in ' + path + '...'
	zip = zipfile.ZipFile(file)
	zip.extractall(path=path)
	return


def untargz(file, path):
	print '\tExtracting ' + file + ' in ' + path + '...'
	targz = tarfile.open(file, "r:gz")
	targz.extractall(path=path)
	targz.close()
	return


def ungzip(file, dest_file):
	
	print '\tExtracting ' + file + ' to ' + dest_file + '...'
	with gzip.open(file, 'rb') as f_in, open(dest_file, 'wb') as f_out:
		shutil.copyfileobj(f_in, f_out)
	return


if __name__ == "__main__":

	if not os.path.exists(source_dir):
		os.makedirs(source_dir)

	IP2Location_login_emailaddr = ''
	IP2Location_login_passwd = ''
	OpenIPMap_login_emailaddr = ''
	OpenIPMap_login_passwd = ''
	with open(accounts_file, 'rb') as accounts:
		while True:
			line = accounts.readline()
			if not line:
				break
			line = line.rstrip('\r\n')
			if line.startswith('#'):
				continue
			if line.startswith('IP2location;'):
				elts = line.split(';')
				IP2Location_login_emailaddr = elts[1]
				IP2Location_login_passwd = elts[2]
			if line.startswith('OpenIPMap;'):
				elts = line.split(';')
				OpenIPMap_login_emailaddr = elts[1]
				OpenIPMap_login_passwd = elts[2]

	print '\nRetrieving IP2location DB...'

	if not os.path.exists(IP2Location_dir):
		os.makedirs(IP2Location_dir)

	IP2Location_payload = {
	    'emailAddress': IP2Location_login_emailaddr,
	    'password': IP2Location_login_passwd
	}

	IP2Location_list = []
	IP2Location_list += [(IP2Location_ipv4_db_bin_url, IP2Location_ipv4_db_bin_file)]
	IP2Location_list += [(IP2Location_ipv6_db_bin_url, IP2Location_ipv6_db_bin_file)]
	IP2Location_list += [(IP2Location_ipv4_db_csv_url, IP2Location_ipv4_db_csv_file)]
	IP2Location_list += [(IP2Location_ipv6_db_csv_url, IP2Location_ipv6_db_csv_file)]

	retrieve_protected_files(IP2Location_login_url, IP2Location_payload, IP2Location_list)

	path = IP2Location_ipv4_db_bin_file[:-4] + '/'
	unzip(IP2Location_ipv4_db_bin_file, path)

	path = IP2Location_ipv6_db_bin_file[:-4] + '/'
	unzip(IP2Location_ipv6_db_bin_file, path)

	path = IP2Location_ipv4_db_csv_file[:-4] + '/'
	unzip(IP2Location_ipv4_db_csv_file, path)

	path = IP2Location_ipv6_db_csv_file[:-4] + '/'
	unzip(IP2Location_ipv6_db_csv_file, path)

	print '\nRetrieving Maxmind DB...'

	if not os.path.exists(Maxmind_dir):
		os.makedirs(Maxmind_dir)

	retrieve_file(Maxmind_db_url, Maxmind_db_file)
	untargz(Maxmind_db_file, Maxmind_dir)

	print '\nRetrieving OpenIPMap Data...'

	if not os.path.exists(OpenIPMap_dir):
		os.makedirs(OpenIPMap_dir)

	OpenIPMap_payload = {
	    'email': OpenIPMap_login_emailaddr,
	    'password': OpenIPMap_login_passwd
	}

	OpenIPMap_list = []
	OpenIPMap_list += [(OpenIPMap_mappings_url, OpenIPMap_mappings_file)]
	OpenIPMap_list += [(OpenIPMap_hostname_rules_url, OpenIPMap_hostname_rules_file)]
	OpenIPMap_list += [(OpenIPMap_ip_rules_url, OpenIPMap_ip_rules_file)]

	retrieve_protected_files(OpenIPMap_login_url, OpenIPMap_payload, OpenIPMap_list)

	print '\nRetrieving DB-IP Data...'

	if not os.path.exists(DB_IP_dir):
		os.makedirs(DB_IP_dir)

	# This is a terrible hack to get DB-IP's file URL...
	response = requests.get(DB_IP_generic_url)
	txt = response.text
	DL_URL = txt.split('free_download_link')[1].split('btn btn-outline-primary')[0].split('\'')[2]
	dl_file_name = DB_IP_dir + DL_URL.split('/')[-1]
	
	retrieve_file(DL_URL, dl_file_name)

	extract_file_name = dl_file_name[:dl_file_name.rfind('.')]
	ungzip(dl_file_name, extract_file_name)
