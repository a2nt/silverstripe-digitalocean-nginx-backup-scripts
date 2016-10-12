import os
import sys
import subprocess
import socket
import json
import requests
import time
import _config

def list_files(folder):
    return [d for d in os.listdir(folder) if os.path.isfile(os.path.join(folder, d))]
def list_dirs(folder):
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
def exclude(value):
    if value in _config.sites:
        _config.sites.remove(value)

# get current server name
def current_server_name():
    return socket.getfqdn()

# list servers
def get_server_info(servername):
    r = requests.get(
        'https://api.digitalocean.com/v2/droplets',
        **{'headers': {'Authorization': 'Bearer ' + _config.token}}
    )
    data = json.loads(r.text)

    if r.status_code != requests.codes.ok:
        print 'Unable to get list of servers:'
        print data
        sys.exit(0)

    for droplet in data['droplets']:
        if servername == droplet['name']:
            return droplet

# get current region
def get_region_and_id(servername):
    droplet = get_server_info(servername)
    return [droplet['region']['slug'],str(droplet['id'])]

def create_site_backup(site,archive = False):
    if (
        os.path.exists(_config.sitepath + '/' + site + '/site')
        and os.path.exists(_config.sitepath + '/' + site + '/assets')
    ):
        print 'Backing up: ' + _config.sitepath + '/' + site
        subprocess.call([
            _config.scriptspath + '/createsitedump.sh',
            _config.sitepath,
            site,
            _config.user,
            _config.password
        ])
        if archive:
            subprocess.call([
                _config.scriptspath + '/backupsite.sh',
                _config.backuppath,
                _config.sitepath,
                site,
                _config.configpath,
                _config.scriptspath
            ])
    else:
        print 'Unknown framework: ' + _config.sitepath + '/' + site

# create website backups
def create_backups():
    print 'Creating website backups ...'
    if not os.path.exists(_config.backuppath):
        os.makedirs(_config.backuppath)

    for site in _config.sites:
        create_site_backup(site,True)

# create and attach block storage
def create_blockstorage():
    print 'Creating block storage ...'
    r = requests.post(
        'https://api.digitalocean.com/v2/volumes',
        **{
            'headers': {
                'Content-type': 'application/json',
                'Authorization': 'Bearer '+_config.token
            },
            'data': '{"size_gigabytes": "20","name": "backup-'+_config.servername.replace('.','')+'","region": "'+_config.region+'"}'
        }
    )

    data = json.loads(r.text)
    if r.status_code != requests.codes.ok:
        print 'Unable to create block storage:'
        print data
        sys.exit(0)

    _config.volumeid = str(data['volume']['id'])

    print 'Attaching block storage ...'
    r = requests.post(
        'https://api.digitalocean.com/v2/volumes/'+_config.volumeid+'/actions',
        **{
            'headers': {
                'Content-type': 'application/json',
                'Authorization': 'Bearer '+_config.token
            },
            'data': '{"type": "attach","droplet_id": "'+_config.serverid+'","region": "'+_config.region+'"}'
        }
    )
    if r.status_code != requests.codes.ok:
        print 'Unable to attach block storage:'
        print data
        sys.exit(0)

    subprocess.call(['parted','/dev/disk/by-id/scsi-0DO_Volume_backup-'+_config.servername.replace('.','')+' mklabel gpt'])
    subprocess.call(['parted','-a opt /dev/disk/by-id/scsi-0DO_Volume_backup-'+_config.servername.replace('.','')+' mkpart primary ext4 0% 100%'])

    subprocess.call(['mkfs.ext4','/dev/disk/by-id/scsi-0DO_Volume_backup-'+_config.servername.replace('.','')])
    subprocess.call(['mkdir','-p /mnt/backup'])
    subprocess.call(['mount','-t ext4 /dev/disk/by-id/scsi-0DO_Volume_backup-'+_config.servername.replace('.','')+' -o rw /mnt/backup'])

# Deattach and delete block storage
def delete_blockstorage():
    print 'Deattaching block storage ...'
    r = requests.post(
        'https://api.digitalocean.com/v2/volumes/'+_config.volumeid+'/actions',
        **{
            'headers': {
                'Content-type': 'application/json',
                'Authorization': 'Bearer '+_config.token
            },
            'data': '{"type": "detach","droplet_id": "'+_config.serverid+'","region": "'+_config.region+'"}'
        }
    )

    print 'Destroying block storage ...'
    r = requests.delete(
        'https://api.digitalocean.com/v2/volumes?name=backup-'+_config.servername.replace('.','')+'&region='+_config.region,
        **{'headers': {'Authorization': 'Bearer '+_config.token}}
    )
    subprocess.call(['rm','-rf','/mnt/backup'])

def create_backup_server():
    print 'Creating backup server ...'
    r = requests.post(
        'https://api.digitalocean.com/v2/droplets',
        **{
            'headers': {
                'Content-type': 'application/json',
                'Authorization': 'Bearer '+_config.token
            },
            'data': '{"name": "backup-'+_config.servername+'","region": "'+_config.region+'","ssh_keys": ["'+_config.sshkeyid+'"],"size": "512mb","image": "ubuntu-14-04-x64","private_networking": true,"backups": false}'
        }
    )

    data = json.loads(r.text)
    if r.status_code != 202:
        print 'Unable to create backup server:'
        print data
        sys.exit(0)

    # Wait 2 minutes before server will be created and activated
    time.sleep(120)
    droplet = get_server_info('backup-'+_config.servername)

    try:
        droplet['status']
    except NameError:
        print 'Unable to find created droplet'
        sys.exit(0)

    if droplet['status'] != 'active':
        print 'Unable to get droplet activated'
        delete_backup_server(str(droplet['id']))
        sys.exit(0)

    return droplet

def sync_backup_server(droplet):

    for network in droplet['networks']['v4']:
        if network['type'] == 'public': #'private':
            dropletip = network['ip_address']

    print 'Syncing to backup server: ' + dropletip

    # Install zip
    subprocess.call([
        'ssh',
        '-oStrictHostKeyChecking=no',
        'root@'+dropletip,
        'apt-get -yqq install zip'
    ])

    # make php configs dir
    subprocess.call(['ssh','-q','-oStrictHostKeyChecking=no','root@'+dropletip,'mkdir -p '+_config.configpath])
    # sync php configs
    subprocess.call(['scp','-q','-oStrictHostKeyChecking=no','-r',_config.configpath,'root@'+dropletip+':'+_config.configpath+'/..'])

    # make scripts dir
    subprocess.call(['ssh','-q','-oStrictHostKeyChecking=no','root@'+dropletip,'mkdir -p '+_config.scriptspath])
    # sync scripts
    subprocess.call(['scp','-q','-oStrictHostKeyChecking=no','-r',_config.scriptspath,'root@'+dropletip+':'+_config.scriptspath+'/..'])

    # sync dropbox config
    subprocess.call(['scp','-q','-oStrictHostKeyChecking=no','-r','/root/.dropbox_uploader','root@'+dropletip+':/root'])

    # Wait 10 sec to complete
    time.sleep(10)

    for site in _config.sites:
        if (
            os.path.exists(_config.sitepath + '/' + site + '/site')
            and os.path.exists(_config.sitepath + '/' + site + '/assets')
        ):
            create_site_backup(site,False)
            # sync site backup to backing up server
            subprocess.call(['ssh','-oStrictHostKeyChecking=no','root@'+dropletip,'mkdir -p '+_config.sitepath+'/'+site])
            subprocess.call([
                'scp',
                '-q',
                '-oStrictHostKeyChecking=no',
                '-r',
                _config.sitepath+'/'+site+'/site',
                'root@'+dropletip+':'+_config.sitepath+'/'+site
            ])
            subprocess.call([
                'scp',
                '-q',
                '-oStrictHostKeyChecking=no',
                '-r',
                _config.sitepath+'/'+site+'/mysite',
                'root@'+dropletip+':'+_config.sitepath+'/'+site
            ])
            subprocess.call([
                'scp',
                '-q',
                '-oStrictHostKeyChecking=no',
                '-r',
                _config.sitepath+'/'+site+'/composer.json',
                'root@'+dropletip+':'+_config.sitepath+'/'+site
            ])
            subprocess.call([
                'scp',
                '-q',
                '-oStrictHostKeyChecking=no',
                '-r',
                _config.sitepath+'/'+site+'/humans.txt',
                'root@'+dropletip+':'+_config.sitepath+'/'+site
            ])
            subprocess.call([
                'scp',
                '-q',
                '-oStrictHostKeyChecking=no',
                '-r',
                _config.sitepath+'/'+site+'/robots.txt',
                'root@'+dropletip+':'+_config.sitepath+'/'+site
            ])
            subprocess.call([
                'scp',
                '-q',
                '-oStrictHostKeyChecking=no',
                '-r',
                _config.sitepath+'/'+site+'/favicon.ico',
                'root@'+dropletip+':'+_config.sitepath+'/'+site
            ])
            subprocess.call([
                'scp',
                '-q',
                '-oStrictHostKeyChecking=no',
                '-r',
                _config.configpath+'/example_config',
                'root@'+dropletip+':'+_config.sitepath+'/'+site
            ])
            subprocess.call([
                'scp',
                '-q',
                '-oStrictHostKeyChecking=no',
                '-r',
                _config.sitepath+'/'+site+'/assets',
                'root@'+dropletip+':'+_config.sitepath+'/'+site
            ])
            subprocess.call([
                'scp',
                '-q',
                '-oStrictHostKeyChecking=no',
                '-r',
                _config.sitepath+'/'+site+'.sql',
                'root@'+dropletip+':'+_config.sitepath
            ])
            # call dropbox sync
            subprocess.call([
                'ssh',
                '-oStrictHostKeyChecking=no',
                'root@'+dropletip,
                _config.scriptspath+'/backupsite.sh '+_config.backuppath+' '+_config.sitepath+' '+site+' '+' '+_config.configpath+' clean'
            ])

            # remove site
            subprocess.call([
                'ssh',
                '-oStrictHostKeyChecking=no',
                'root@'+dropletip,
                'rm -rf '+_config.sitepath+'/'+site
            ])

            subprocess.call([
                'rm',
                _config.sitepath+'/'+site+'.sql'
            ])

            # Wait 10 sec before uploading next site
            time.sleep(10)



def delete_backup_server(serverid):
    print 'Destroying backup server ...'
    r = requests.delete(
        'https://api.digitalocean.com/v2/droplets/' + serverid,
        **{'headers': {'Authorization': 'Bearer '+_config.token}}
    )
    if r.status_code != 204:
        print 'Unable to delete server:'
        print r.text
        sys.exit(0)