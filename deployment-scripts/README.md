# Deployment Scripts for Multi-Service RTMP Broadcaster
Here you will find deployment scripts for various cloud services.
## Linode
[Sign up for Linode cloud hosting here](https://www.linode.com/?r=37246e0d6a6198293308e698647804fbfe02845e).

This script will create a Linode server, deploy the `multistreaming-server` docker image pulled from Docker Hub, and then launch the image using the JSON configuration file you specify. The `linode-cli` software should be installed on your local computer ([click here for instructions](https://www.linode.com/docs/platform/api/linode-cli/)).

When running this script, it takes the following arguments:
* `-c /path/to/config.json` - The file path the the JSON file containing the multistreaming server configuration. _REQUIRED_
* `-p root_password` - What the root password for the server being created should be set to. _REQUIRED_
* `-s stream_password` - The password that someone needs to use to push a stream to the rebroadcasting server. _REQUIRED_
* `-k /path/to/keyfile` - The file path to the public key file that should be used for keyless SSH connections to the server. If not specified, `~/.ssh/id_rsa.pub` will be used. Having a SSH key file defined on your system is _REQUIRED_.
* `-h` - This will display more detailed information on how to use the script, including environment variables that are supported.

If the script successfully completes, you will have a Linode server running with the Multi-Service RTMP Broadcaster software running. The script also prints some useful information and commands to use at the end of its run. Most notable is the server's IP address. This should be used in your streaming software configuration as described in [this project's README](https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/blob/master/README.md).

Two environment variables you might consider setting is the `RTMP_SERVER_LINODE_NODE_TYPE` variable to set the Linode type your server should use and `RTMP_SERVER_LINODE_REGION` variable to set the Linode region your server should reside. The Linode server type should have sufficient cores to handle the transcoding load required for your configuration. The Linode region should be the one closest to where you are streaming from.

## Local Host

Running the `multistreaming-server` locally is a great option if your local internet connection can support bandwidth required to push all of the rebroadcasted streams you intend to push. You should also consider if your local CPU should have sufficient cores to perform any transcoding you desire for individual streams. This script will simply launch a Docker container locally for the `multistreaming-server`.

When running this script, it takes the following arguments:
* `-c /path/to/config.json` - The file path the the JSON file containing the multistreaming server configuration. _REQUIRED_
* `-s stream_password` - The password that someone needs to use to push a stream to the rebroadcasting server. _REQUIRED_
* `-b` - When present, the Docker image will be built locally (script assumes it has not been moved from this git repository). When not present, the docker image will be pull from Docker Hub.
* `-h` - This will display more detailed information on how to use the script, including environment variables that are supported.

If the script successfully completes, you will be running a Docker container locally with the Multi-Service RTMP Broadcaster software running. The script also prints some useful information and commands to use at the end of its run. The IP address you should use to configure your streaming software's destination is `127.0.0.1` or `localhost`.
