import _lib

# Digital Ocean API token (to create temporary block storage / server)
token = ''
# Digital Ocean SSH Key ID (will be used to connect to temporary backing up server)
sshkeyid = ''

# your web sites root folder path (with the folders named: my.domain.com)
sitepath = '/srv'
sites = _lib.list_dirs(sitepath)
# exclude following folder names
_lib.exclude('tmp')
_lib.exclude('01virus.twma.pro')
_lib.exclude('02empty')
_lib.exclude('backups')

# your block storage mount point / local backing up folder path
backuppath = '/mnt/backup'
# framework configuration path (to store example_config folder which will be added to backup file)
configpath = '/srv-service/conf.d/php'
# server scripts path
scriptspath = '/srv-service/scripts'

# your web sites configuraion nginx path (will be used to remove excessive my.domain.com.conf files)
nginxpath = '/srv-service/conf.d/nginx/sites'
# Exclude following nginx conf files
excludeconf = [
    '01fastcgi_cache_zone.conf',
    '02twma.pro.conf',
    '03ban_ip.conf',
    '04gzip.conf',
]

# MySQL host (will be used to backup database and to remove excessive my.domain.com databases)
host = 'localhost'
# MySQL user
user = 'root'
# MySQL password
password = ''
# Exclude following MySQL DB's
excludedb = [
    'performance_schema',
    'information_schema',
    'mysql',
    'user',
    'sys',
]

servername = _lib.current_server_name()
server = _lib.get_region_and_id(servername)
region = server[0]
serverid = server[1]

volumeid = 0