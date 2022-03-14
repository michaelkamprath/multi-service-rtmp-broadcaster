# upcloud-deploy.py
#
# This python script deploys and instance of the Multiservice RTMP broadcaster
# to a newly created server in the UpCloud hosting service.
#
# Assumes that the upcloud-api python library is installed.
# Run with python3
#
import getopt
import os
import subprocess
import sys
import time

import upcloud_api as up

# This shell script is run on the server once the server is running.
# It is used to install and configur Docker.
INIT_SCRIPT = """
# Update the system and install useful packages
apt-get update
apt-get upgrade -y
apt-get install htop

# Install docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Enable firewall
ufw enable
ufw allow 22
ufw allow http
ufw allow 1935

# configure the rtmpserver user
usermod -a -G docker rtmpserver

"""

def print_help():
    print(
        'Example usage:\n    '
        'python3 upcloud-deploy.py '
        '-u <upcloud username> '
        '-p <upcloud password> '
        '-c /path/to/config.json '
        '-k /path/to/ssh_key.pub '
        '-s <streaming password>'
        '\n'
    )
    print('Environment Variables (can be used instead of command arguments):')
    print('    RTMP_SERVER_UPCLOUD_USER       : UpCloud user name to authenticate with. Can replace \'-u\' option.')
    print('    RTMP_SERVER_UPCLOUD_PASSWORD   : UpCloud user password to authenticate with. Can replace \'-p\' option.')
    print('    RTMP_SERVER_UPCLOUD_REGION     : UpCloud region to create server in. Defaults to \'us-sjo1\'.')
    print('    RTMP_SERVER_UPCLOUD_NODE_CORES : The number cores for the UpCloud server. Defaults to \'4\'')
    print('    RTMP_SERVER_UPCLOUD_NODE_RAM   : The amount of RAM in MB for the UpCloud server. Defaults to \'4096\'')
    print('    RTMP_SERVER_UPCLOUD_NODE_DISK  : The amount of disk space in GB for the UpCloud server. Defaults to \'64\'')

# Default values for config
upcloud_user = None \
    if 'RTMP_SERVER_UPCLOUD_USER' not in os.environ \
    else os.environ['RTMP_SERVER_UPCLOUD_USER']
upcloud_password = None \
    if 'RTMP_SERVER_UPCLOUD_PASSWORD' not in os.environ \
    else os.environ['RTMP_SERVER_UPCLOUD_PASSWORD']
upcloud_region = up.ZONE.SanJose \
    if 'RTMP_SERVER_UPCLOUD_REGION' not in os.environ \
    else os.environ['RTMP_SERVER_UPCLOUD_REGION']
upcloud_cores = 4 \
    if 'RTMP_SERVER_UPCLOUD_NODE_CORES' not in os.environ \
    else int(os.environ['RTMP_SERVER_UPCLOUD_NODE_CORES'])
upcloud_ram = 4096 \
    if 'RTMP_SERVER_UPCLOUD_NODE_RAM' not in os.environ \
    else int(os.environ['RTMP_SERVER_UPCLOUD_NODE_RAM'])
upcloud_disk = 64 \
    if 'RTMP_SERVER_UPCLOUD_NODE_DISK' not in os.environ \
    else int(os.environ['RTMP_SERVER_UPCLOUD_NODE_DISK'])
rtmp_config_filepath = None
ssh_key_filepath = '~/.ssh/id_rsa.pub'
rtmp_streaming_password = None

# fetch CLI arguments
try:
    opts, args = getopt.getopt(sys.argv[1:],"u:p:c:k:s:h")
except getopt.GetoptError as err:
    print(err)
    print_help()
    exit(2)

for opt, arg in opts:
    if opt == '-u':
        upcloud_user = arg
    elif opt == '-p':
        upcloud_password = arg
    elif opt == '-c':
        rtmp_config_filepath = arg
    elif opt == '-k':
        ssh_key_filepath = arg
    elif opt == '-s':
        rtmp_streaming_password = arg
    elif opt == '-h':
        print_help()
        exit(0)
    else:
        print('ERROR - Got on unrecognized command line option "{0}"'.format(opt))
        exit(2)

if upcloud_user is None \
    or upcloud_password is None \
    or rtmp_config_filepath is None \
    or ssh_key_filepath is None \
    or rtmp_streaming_password is None:
    print('ERROR - configuration is not complete.')
    exit(2)

# Connect to UpCloud
manager = up.CloudManager(upcloud_user, upcloud_password, timeout=60)
manager.authenticate()
print('Connected to UpCloud API as user "{0}"'.format(upcloud_user))

res = subprocess.run(
    'cat {0}'.format(ssh_key_filepath),
    shell=True,
    stdout=subprocess.PIPE,
    text=True,
)
ssh_key_value = res.stdout.strip()
rtmp_user_desc = up.login_user_block(
    username='rtmpserver',
    ssh_keys=[ssh_key_value],
    create_password=False,
)

rtmp_server_desc = up.Server(
    core_number=upcloud_cores, # CPU cores
    memory_amount=upcloud_ram, # RAM in MB
    zone=upcloud_region,
    title='Multiservice RTMP Broadcaster',
    # UpCloud strangely requires that every server have a qualified domain
    # name. (?!) Using a totaly made up name here.
    hostname='multiservice-rtmp-server.com',
    storage_devices=[
        up.Storage(os='Ubuntu 18.04', size=upcloud_disk ),
    ],
    login_user=rtmp_user_desc,  # user and ssh-keys
    user_data=INIT_SCRIPT,
)

print('Starting creation of server with these parameters:')
print(
    '    cores = {0}\n'
    '    RAM = {1} MB\n'
    '    disk = {2} GB\n'
    '    region = {3}'.format(
        upcloud_cores, upcloud_ram, upcloud_disk, upcloud_region
    )
)
rtmp_server = manager.create_server(rtmp_server_desc)
ip_addr = rtmp_server.get_ip()
print(
    'Server creation done.\n'
    '    server = {0}\n'
    '    IP address = {1}'.format(rtmp_server, ip_addr)
)

# wait for the server to finish booting and installing docker
print('Waiting 8 minutes for server set up to complete ...')
time.sleep(60)
print('Waiting 7 minutes for server set up to complete ...')
time.sleep(60)
print('Waiting 6 minutes for server set up to complete ...')
time.sleep(60)
print('Waiting 5 minutes for server set up to complete ...')
time.sleep(60)
print('Waiting 4 minutes for server set up to complete ...')
time.sleep(60)
print('Waiting 3 minutes for server set up to complete ...')
time.sleep(60)
print('Waiting 2 minutes for server set up to complete ...')
time.sleep(60)
print('Waiting 1 minutes for server set up to complete ...')
time.sleep(60)

# Send configuration to server and launch Docker image
print('Adding IP address {0} to known hosts ...'.format(ip_addr))
res = subprocess.run('ssh-keygen -R {}'.format(ip_addr), shell=True)
if res.returncode != 0:
    print('ERROR when removing server IP from known hosts.\n    {0}'.format(res.stderr))
    exit(1)
elif res.stdout is not None:
    print(res.stdout)
res = subprocess.run('ssh-keyscan -T 240 {0} >> ~/.ssh/known_hosts'.format(ip_addr), shell=True)
if res.returncode != 0:
    print('ERROR when adding server IP to known hosts.\n    {0}'.format(res.stderr))
    exit(1)
elif res.stdout is not None:
    print(res.stdout)

# send configuration file to Server
scp_cmd = 'scp \'{0}\' rtmpserver@{1}:/home/rtmpserver/rtmp_server_config.json'.format(
            rtmp_config_filepath,
            ip_addr
        )
print('Sending configuration file to serverr with: {0}'.format(scp_cmd))
res = subprocess.run(
    scp_cmd,
    shell=True
)
if res.returncode != 0:
    print(
    	'ERROR when sending RTMP configuration to server.\n'
    	'    returncode = {0}\n    stderr = {1}'.format(res.returncode, res.stderr)
    )
    exit(1)
elif res.stdout is not None:
    print(res.stdout)

# start the docker subprocess
res = subprocess.run(
    'ssh rtmpserver@{0} '
        '"docker run -d -p 80:80 -p 1935:1935 '
        '--env MULTISTREAMING_PASSWORD={1} '
        '-v /home/rtmpserver/rtmp_server_config.json:/rtmp-configuration.json '
        'kamprath/multistreaming-server:latest"'.format(
            ip_addr, rtmp_streaming_password
        ),
    shell=True,
    stdout=subprocess.PIPE,
    text=True,
)
docker_container_id = res.stdout[:12]
print('Started Docker container: {0}'.format(docker_container_id))

# Finished
print('Finished!\n')
print('The IP address for the Multistreaming Server is:')
print('    {0}\n'.format(ip_addr))
print('Visit the Multistreaming Server\'s statistics page here:')
print('    http://{0}/stat\n'.format(ip_addr))
print('Use this command to log into the server (if needed):')
print('    ssh rtmpserver@{0}\n'.format(ip_addr))
print('When done, terminate this server in the UpCloud Web Console here:')
print('    https://hub.upcloud.com/\n')
