# Deployment Scripts for Multi-Service RTMP Broadcaster
Here you will find deployment scripts for various cloud services.
## Linode
[Sign up for Linode cloud hosting here](https://www.linode.com/?r=37246e0d6a6198293308e698647804fbfe02845e).

The `linode-deploy.sh` shell script will create a Linode server, deploy the `multistreaming-server` docker image pulled from Docker Hub, and then launch the image using the JSON configuration file you specify. The `linode-cli` software should be installed on your local computer ([click here for instructions](https://www.linode.com/docs/platform/api/linode-cli/)).

The script is run in the following manner:
```
RTMP_SERVER_LINODE_NODE_TYPE="g6-standard-6" \
  ./linode-deploy.sh \
  -c /path/to/rtmp-config.json \
  -p secure-r00t-password \
  -k ~/.ssh/id_rsa.pub \
  -s stream_password
```

When running this script, it takes the following arguments:
* `-c /path/to/config.json` - The file path the the JSON file containing the multistreaming server configuration. _REQUIRED_
* `-p root_password` - What the root password for the server being created should be set to. _REQUIRED_
* `-s stream_password` - The password that someone needs to use to push a stream to the rebroadcasting server. _REQUIRED_
* `-k /path/to/keyfile` - The file path to the public key file that should be used for keyless SSH connections to the server. If not specified, `~/.ssh/id_rsa.pub` will be used. Having a SSH key file defined on your system is _REQUIRED_.
* `-h` - This will display more detailed information on how to use the script, including environment variables that are supported.

If the script successfully completes, you will have a Linode server running with the Multi-Service RTMP Broadcaster software running. The script also prints some useful information and commands to use at the end of its run. Most notable is the server's IP address. This should be used in your streaming software configuration as described in [this project's README](https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/blob/master/README.md).

There are several environment variables that control details of the type of server that will get deployed. Use the `-h` option to learn more. Two environment variables you might consider setting is the `RTMP_SERVER_LINODE_NODE_TYPE` variable to set the Linode type your server should use and `RTMP_SERVER_LINODE_REGION` variable to set the Linode region your server should reside. The Linode server type should have sufficient cores to handle the transcoding load required for your configuration. The Linode region should be the one closest to where you are streaming from.

## UpCloud
[Sign up for UpCloud cloud hosting here](https://upcloud.com/signup/?promo=A2CVWA)

This `upcloud-deploy.py` python script will create a server using the UpCloud service, deploy the `multistreaming-server` docker image pulled from Docker Hub, and then launch the image using the JSON configuration file you specify. The `upcloud-api` Python library must be installed on your local computer where you will run this script ([click here for instructions](https://github.com/UpCloudLtd/upcloud-python-api)).

The script is run in the following manner:
```
RTMP_SERVER_UPCLOUD_NODE_CORES="2" RTMP_SERVER_UPCLOUD_NODE_RAM="2048" RTMP_SERVER_UPCLOUD_NODE_DISK="32" \
  python3 upcloud-deploy.py \
  -u upcloud_username -p upcloud_password \
  -c /path/to/rtmp-config.json \
  -k ~/.ssh/id_rsa.pub \
  -s stream_password
```
When running this script, it takes the following arguments:
* `-u <upcloud username>` - The user name for the UpCloud account that will be hosting the server.
* `-p <upcloud password>` - The user password for the UpCloud account that will be hosting the server.
* `-c /path/to/config.json` - The file path the the JSON file containing the multistreaming server configuration. _REQUIRED_
* `-k /path/to/ssh_key.pub` - The file path to the public key file that should be used for keyless SSH connections to the server. If not specified, `~/.ssh/id_rsa.pub` will be used. Having a SSH key file defined on your system is _REQUIRED_.
* `-s stream_password` - The password that someone needs to use to push a stream to the rebroadcasting server. _REQUIRED_
* `-h` - This will display more detailed information on how to use the script, including environment variables that are supported.

If the script successfully completes, you will have a UpCloud server running with the Multi-Service RTMP Broadcaster software running. The script also prints some useful information and commands to use at the end of its run. Most notable is the server's IP address. This should be used in your streaming software configuration as described in [this project's README](https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/blob/master/README.md).

There are several environment variables that control details of the type of server that will get deployed. Use the `-h` option to learn more. The environment variables you might consider setting are `RTMP_SERVER_UPCLOUD_NODE_CORES` to indicate the number of cores your server will need, `RTMP_SERVER_UPCLOUD_NODE_RAM` to indicate how much RAM (in MB) your server will need, `RTMP_SERVER_UPCLOUD_NODE_DISK` to indicate the size of the disk (in GB) your server will need (note that all live streams get recorded on the server), and `RTMP_SERVER_UPCLOUD_REGION` to indicate what region your server should be deployed in ([possible values listed here](https://github.com/UpCloudLtd/upcloud-python-api/blob/master/upcloud_api/constants.py#L7)).

## Local Host

Running the `multistreaming-server` locally is a great option if your local internet connection can support bandwidth required to push all of the rebroadcasted streams you intend to push. You should also consider if your local CPU should have sufficient cores to perform any transcoding you desire for individual streams. This script will simply launch a Docker container locally for the `multistreaming-server`.

The script is run in the following manner:
```
./local-deploy.sh \
  -c /path/to/rtmp-config.json \
  -s stream_password
```

When running this script, it takes the following arguments:
* `-c /path/to/config.json` - The file path the the JSON file containing the multistreaming server configuration. _REQUIRED_
* `-s stream_password` - The password that someone needs to use to push a stream to the rebroadcasting server. _REQUIRED_
* `-b` - When present, the Docker image will be built locally (script assumes it has not been moved from this git repository). When not present, the docker image will be pull from Docker Hub. There are no arguments to option.
* `-d` - Use to indicate the Docker image tag name that should be used for either the image built with the `-b` flag or pulled if `-b` is not present. If not present, the default image tag is `multistreaming-server:latest` for local builds using the `-b` option, and `kamprath/multistreaming-server:latest` if not building locally. It is recommended that this option does not get set and thus the default image tag values are used, but this option is provided if you "know what you are doing".
* `-h` - This will display more detailed information on how to use the script, including environment variables that are supported.

If the script successfully completes, you will be running a Docker container locally with the Multi-Service RTMP Broadcaster software running. The script also prints some useful information and commands to use at the end of its run. The IP address you should use to configure your streaming software's destination is `127.0.0.1` or `localhost`.

## Kubernetes

You will find the required manifests to deploy the container to a Kubernetes cluster under the `./kubernetes-kustomize` directory. 

* Exposed RTMP/stats port: The example manifest in this repo will create a Service of type `NodePort` which will expose the RTMP endpoint on port 33195, and the stats endpoint on port 30080 on all the nodes. If you want to change this behavior, update `service.yaml` with the `nodePort` values you want.
* Stream password: Stream password will be created a Kubernetes Secret in the cluster, to set the password open the file `kustomization.yaml` and find the entry with the name `multistreaming` in the list under the key `secretGenerator`. 
* RTMP Configuration JSON: The configuration file must be placed in the same path as the `kustomization.yaml` and should be named `rtmp-configuration.json`. The deployment will automatically read this file and create it in the cluster as a configmap.
* Kubernetes namespace: By default the manifests will be deployed to a namespace called `multistreaming`. You may change this in `kustomization.yaml`. This namespace should be created manually before it can be used for deployments.

Deployment command:
```
# Make sure you have your KUBECONFIG set.
$ cd kubernetes-kustomize/ # or the path where you are storing the manifests
$ kubectl create namespace multistreaming # the target namespace, should only be run once 
$ kubectl apply -k . # can be run many times to refresh the configuration
```