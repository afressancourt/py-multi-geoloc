# Py-multi-geoloc

I have developped this set of Python scripts to use IP geolocation tools in a coordinated way.

## Table of Contents

* [Usage](#Usage)
* [Requirements](#Requirements)
* [Scripts](#Scripts)
  * [get_data.py](#get_data.py)
  * [prepare_data.py](#prepare_data.py)
  * [py\_multi\_geoloc.py](#py\_multi\_geoloc.py)
  * [bulk_locate.py](#bulk_locate.py)
* [Future Enhancements](#Future Enhancements) 

=============================
## Usage

This set of scripts is composed of four components.

The core script is `py-multi-geoloc.py`. It contains a set of methods to load geolocation data and use them. 

The script `bulk_locate.py`gives an example of the use of `py-multi-geoloc.py` to lookup several IP addresses listed in a file, `ip_list`.

The scripts `get_data.py`and `prepare_data.py` are used less often to retrieve data from sources and to prepare this data.

=============================
## Requirements

The following modules ar erequired for this set of script to work:

* requests (pip install requests)
* netaddr (pip install netaddr)
* radix (pip install py-radix)
* geoip2 (pip install geoip2)

=============================
## Scripts

=============================
### get_data.py

This script retrieves data from:

* IP2Location ([http://lite.ip2location.com](http://lite.ip2location.com))
* Maxmind ([https://dev.maxmind.com/geoip/geoip2/geolite2/](https://dev.maxmind.com/geoip/geoip2/geolite2/))
* Open IP Map ([https://github.com/RIPE-Atlas-Community/openipmap](https://github.com/RIPE-Atlas-Community/openipmap))
* DB-IP ([https://db-ip.com/db/](https://db-ip.com/db/))

Downloading resources from IP2Location and Open IP Map requires creating an account on IP2Location and on RIPE respectively. Please create those accounts, then put the account's credentials in an `accounts.use` file. An example of such a file is given, `accounts.use.example`

=============================
### prepare_data.py

This scripts prepare the data from the sources retrieved using `get_data.py`. Be advised that this data preparation takes time, given the volume of data to gather and parse.

=============================
### py\_multi\_geoloc.py

This script gathers a set of functions to load and manipulate the data prepared earlier. 

The method to load data is called `load_data_source`. It takes the references of the prepared data source files. If a reference is set to `None`, then the data source is ignored. A dictionnary gathering the loaded data sources is returned.

`locate_ip_multi` is the function used to retreived information on the location of a given IP address according to the various data sources. 

`locate_ip` gives the best location information for an IP according to one of the following criteria:

* `confidence`
* `consensus` (To be implemented)

=============================
### bulk_locate.py

this script gives an example of the usage of `py_multi_geoloc.py`. This scripts takes the IP addresses listed in a file, `ip_list` and looks them up in various database.

Given the time to load the IP geolocation data sources, we advise to perform lookups in large batches. Besides, you can avoid loading some data sources if they are not necessary, by setting the data source to `None` in the call of `load_data_source`.

=============================
## Future enhancements

* Work on more efficent data structure
* Work on data history 

