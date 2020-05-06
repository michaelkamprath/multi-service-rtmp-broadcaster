# Deployment Scripts for Multi-Service RTMP Broadcaster
Here you will find deployment scripts for various cloud services.
## Linode
[Sign up for Linode cloud hosting here](https://www.linode.com/?r=37246e0d6a6198293308e698647804fbfe02845e).

This script will create a Linode server, deploy the `multistreaming-server` docker image pulled from Docker Hub, and then launch the image using the JSON configuration file you specify. The `linode-cli` software should be installed on your local computer ([click here for instructions](https://www.linode.com/docs/platform/api/linode-cli/)).

When running this script, it takes the following arguments:
* `-c /path/to/config.json` - The file path the the JSON file containing the multistreaming server configuration. _REQUIRED_
* `-p root_password` - What the root password for the server being created should be set to. _REQUIRED_
* `-s stream_password` - The password that someone needs to use to push a stream to this
* `-k /path/to/keyfile` - The file path to the public key file that should be used for keyless SSH connecitons to the server. If not specified, `~/.ssh/id_rsa.pub` will be used. Having a SSH key file defined on your system is _REQUIRED_.
* `-h` - This will display more detailed information on how to use the script, including environment variables that are supported.

If the script successfully completes, you will have a Linode server running with the Multi-Service RTMP Broadcaster software running. The script also prints some useful information and commands to use at the end of its run. Most notable is the server's IP address. This should be used in your streaming software configuration as described in [this project's README](https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/blob/master/README.md).
