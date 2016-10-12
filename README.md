# SilverStripe Digital Ocean + Dropbox + NGINX service scripts

## Dropbox SilverStripe environment backing up scripts using Digital Ocean temporary block storage or server

Allows you to save time and money by creating temporary Digital Ocean block storage / server and syncing it website dumps to Dropbox

Script doesn't require additional space at your server to create backups so you don't need to buy extra disc space

Extra disc space will be used just for some time to create and upload website dumps
so u won't need it to waste your time doing it manually and you will save money cuz you don't need to buy extra disc space for a month.

1) Creates new Digital Ocean Server

2) Creates MySQL database dump based on website root folder name (my.site.domain.com)

3) Setups debian backing up server enviroment: installs zip, uploads backing up scripts, setting up running server Dropbox-Uploader config

4) Uploads to backing up server following folders: mysite, site, assets, example_config
   and files: composer.json, humans.txt, robots.txt, favicon.ico
   and mysql dump: site_name.sql

5) Archives following folders: mysite, site, assets, example_config
   and files: composer.json, humans.txt, robots.txt, favicon.ico
   and mysql dump: my.site.domain.com.sql
   to zip file my.site.domain.com

6) Syncs website dumps to dropbox

7) Deletes temporary server / storage

### Requirements

* SilverStripe websites with NGINX environment at Digital Ocean
* Place this scripts into /srv-service/scripts folder
* Place your SilverStripe blank config to /srv-service/conf.d/php folder
* Your websites shall be at /srv folders named my.site.domain.com
* Your MySQL databases shall be named my.site.domain.com
* Your NGINX config files shall be named my.site.domain.com
* Folder paths maybe changed (see _config.py)
* Take a look at backup.py if you have block storage option available

### Setup

* Install python
* Install following python modules: python-requests, python-sockets, python-subprocess, python-json, python-requests
* Install zip
* Get API key at DigitalOcean control pane (it will be used to create temporary storage / server)
* Setup SSH key at your server and add it to Digital Ocean control pane (it will be used to access temporary server)
* Setup variables at _config.py
* run Dropbox-Uploader/dropbox_uploader.sh to setup Dropbox API variables
* run backup.py to start backup process
* You can put backup.py to crontab to execute it automatically

### Options
* Install python-mysqldb to clean up MySQL database and NGINX configuration files based on site folder names and run cleandb.py
* You can put cleandb.py to crontab to execute it automatically
* Install imagemagic and run imageresize.sh script at a specific folder to resample all images bigger than 1900x1200
