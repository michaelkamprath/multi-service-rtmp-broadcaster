#!/bin/bash

#
# Assumes that the Linode CLI tool is already installed and enabled to create linodes.
#

# helper functions
print_help_and_exit()
{
  echo "Usage: "
  echo "    linode-deploy.sh [-c /path/to/config.json] [-p <new server root password>] [-k /path/to/ssh_key.pub] [-s <streaming password>]"
  echo ""
  echo "Environment Variables (can be used instead of command arguments): "
  echo "    RTMP_SERVER_CONFIG_FILEPATH    : path to RTMP server config JSON file. Can replace -c option."
  echo "    RTMP_SERVER_ROOTPW             : Root password to be set for newly created Linode server. Can replace -p option."
  echo "    RTMP_SERVER_AUTORIZED_KEY_FILE : SSH public key file path to enable secure connections for newly created Linode server. Defaults to  ~/.ssh/id_rsa.pub. Can replace -k option."
  echo "    RTMP_SERVER_STREAM_PASSWORD    : Password used by RTMP streaming server for livestreams. Can replace -s option."
  echo "    RTMP_SERVER_LINODE_REGION      : Linode region to create server in. Defaults to 'us-west'."
  echo "    RTMP_SERVER_LINODE_NODE_TYPE   : Linode node type to use for server. Defaults to 'g6-standard-4'."
  echo ""
  exit 0
}

# check arguments passed to this script
while getopts "c:p:k:s:h" option; do
  case "${option}" in
  c)
    RTMP_SERVER_CONFIG_FILEPATH=$OPTARG
    ;;
  p)
    RTMP_SERVER_ROOTPW=$OPTARG
    ;;
  k)
    RTMP_SERVER_AUTORIZED_KEY_FILE=$OPTARG
    ;;
  s)
    RTMP_SERVER_STREAM_PASSWORD=$OPTARG
    ;;
  h)
    print_help_and_exit
    ;;
  esac
done
shift $((OPTIND -1))

if [ -z $RTMP_SERVER_STREAM_PASSWORD ]; then
  echo "You must define a streaming password for the streaming server. Use the '-s' option or set the RTMP_SERVER_STREAM_PASSWORD environment variable."
  exit 2
fi

if [ -z $RTMP_SERVER_ROOTPW ]; then
  echo "You must define a root password for the server. Use the '-p' option or set the RTMP_SERVER_ROOTPW environement variable."
  exit 2
fi

if [ -z $RTMP_SERVER_CONFIG_FILEPATH ]; then
  echo "You must define a filepath to the streaming server configuration JSON file. Use the -c option."
fi

# Set variables to defaults if unset
RTMP_SERVER_LINODE_REGION=${RTMP_SERVER_LINODE_REGION:-"us-west"}
RTMP_SERVER_LINODE_NODE_TYPE=${RTMP_SERVER_LINODE_NODE_TYPE:-"g6-standard-4"}
RTMP_SERVER_AUTORIZED_KEY_FILE=${RTMP_SERVER_AUTORIZED_KEY_FILE:-"~/.ssh/id_rsa.pub"}

LINODE_DOCKER_SCRIPT_ID="607433"

# launch a Docker server
echo "Creating Linode server ..."
linode_id=$( \
  linode-cli linodes create \
    --image "linode/debian9" \
    --label multistreaming-server \
    --authorized_keys "$(cat $RTMP_SERVER_AUTORIZED_KEY_FILE)" \
    --root_pass "$RTMP_SERVER_ROOTPW" \
    --booted true \
    --region "$RTMP_SERVER_LINODE_REGION" \
    --type "$RTMP_SERVER_LINODE_NODE_TYPE" \
    --stackscript_id "$LINODE_DOCKER_SCRIPT_ID" \
    --text --format 'id' --no-headers \
)
lindode_status=$(linode-cli linodes view ${linode_id} --text --format 'status' --no-headers)
echo "Created Linode ${linode_id}. Current status is '${lindode_status}'. Waiting for it to transition to a running state."
while [ $lindode_status != "running" ]
do
  sleep 10
  lindode_status=$(linode-cli linodes view ${linode_id} --text --format 'status' --no-headers)
  echo "Linode ${linode_id} status is '${lindode_status}'."
done
linode_ip_addr=$(linode-cli linodes view ${linode_id} --text --format 'ipv4' --no-headers)
echo "Linode ${linode_id} creation complete. IPv4 address is: ${linode_ip_addr}"
echo "Waiting 5 minutes for booting and Docker installation to complete."
sleep 60
echo "Waiting 4 minutes for booting and Docker installation to complete."
sleep 60
echo "Waiting 3 minutes for booting and Docker installation to complete."
sleep 60
echo "Waiting 2 minutes for booting and Docker installation to complete."
sleep 60
echo "Waiting 1 minutes for booting and Docker installation to complete."
sleep 60


# Add IP address to known hosts so ssh commands can proceed unimpeded
echo "Addding ${linode_ip_addr} to known_hosts"
ssh-keygen -R ${linode_ip_addr}
ssh-keyscan -T 240 ${linode_ip_addr} >> ~/.ssh/known_hosts

# copy the passed RTMP server config file to the Server
echo "Copying '${RTMP_SERVER_CONFIG_FILEPATH}' to path /root/rtmp_server_config.json on Linode ${linode_id}"
scp -q "$RTMP_SERVER_CONFIG_FILEPATH" root@"${linode_ip_addr}":/root/rtmp_server_config.json
if [ $? -ne 0 ]; then
  echo "ERROR - Unable to copy '${RTMP_SERVER_CONFIG_FILEPATH}' to linode ${linode_id}. Please terminate the Linode with this command:"
  echo "    linode-cli linodes delete ${linode_id}"
  exit 1
fi
# now launch docker container
echo "Launch kamprath/multistreaming-server:latest Docker image."
docker_proc_id=$(ssh root@"$linode_ip_addr" \
  "docker run -d -p 80:80 -p 1935:1935 " \
    "--env MULTISTREAMING_PASSWORD=${RTMP_SERVER_STREAM_PASSWORD} " \
    "-v /root/rtmp_server_config.json:/rtmp-configuation.json " \
    "kamprath/multistreaming-server:latest" \
)
echo "Started Docker container: $docker_proc_id"
# Finished
echo "Finished!"
echo ""
echo "The IP address for the Multistreaming Server is:"
echo "    ${linode_ip_addr}"
echo ""
echo "Visit the Multistreaming Server's statistics page here:"
echo "    http://${linode_ip_addr}/stat"
echo ""
echo "Use this command to kill the server:"
echo "    linode-cli linodes delete ${linode_id}"
echo ""
echo "Use this command to log into the server:"
echo "    ssh root@${linode_ip_addr}"
echo ""
