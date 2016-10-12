#!/usr/bin/env python
# -*- coding: utf-8 -*-

# clean ups database using directory names
# Example: website root has directory name my.domain.com
# than mysql database shall have the same name my.domain.com

# apt-get install python-mysqldb
# pip install pymysql

import os
import MySQLdb
import _config

print 'Cleaning up website databases'
connection = MySQLdb.connect(_config.host,_config.user,_config.password)
cursor = connection.cursor()
cursor.execute('SHOW DATABASES')

for (db_name,) in cursor:
    if db_name not in _config.sites and db_name not in _config.excludedb:
        print 'Removing: ' + db_name
        cursor.execute('DROP DATABASE `'+db_name+'`')


print 'Cleaning up nginx configuration files'
nginxconfs = _config._lib.list_files(_config.nginxpath)

for site_conf in nginxconfs:
    site_name = site_conf.replace('.conf','')
    if site_name not in _config.sites and site_conf not in _config.excludeconf:
        print 'Removing: ' + _config.nginxpath + '/' + site_conf
        os.remove(_config.nginxpath+'/'+site_conf)