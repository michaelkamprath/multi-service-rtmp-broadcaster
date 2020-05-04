# Multi-Service RTMP Broadcaster

The goal of this project is to create a Docker-deployed service that will allow you to easily broadcast a live stream to multiple services (YouTube, Twitch, Facebook, etc) at the same time. This stream rebroadcaster is designed to be used by a single source / user.

## Usage
The instructions here assume you are running on Linux. With some modification of the commands, you can make this Docker build work on Windows and Mac OS too.

The first step is to build the docker file. After you clone this repository, `cd` into and and issue:

```
docker build -t multistreaming-server ./multistreaming-server/
```

Once built, start the serve on the same host as where your streaming source (e.g., OBS) is running with:

```
docker run -it -p 80:80 -p 1935:1935 \
  --env MULTISTREAMING_PASSWORD=__made_up_password__ \
  -v /path/to/my-rtmp-config.json:/rtmp-configuation.json
  multistreaming-server:latest
```

Alternatively, you could use the DockerHub build of this image by pulling and using the `kamprath/multistreaming-server:latest` [Docker image](https://hub.docker.com/repository/docker/kamprath/multistreaming-server).

Note that several environment variables are set when running the Docker image:

* `MULTISTREAMING_PASSWORD` _(REQUIRED)_ - This is a password you define and will be used by your steaming software. This is a marginally secure way to prevent other people from pushing to your stream.

You must create and JSON file with the RTMP rebroadcasting configuration ... _TBC_

Once the Docker image is running, set up your stream software with the following parameters:

* **Server** : `rtmp://__docker_host_IP_address__/live` - Replace `__docker_host_IP_address__` with the IP address of your host that is running this Docker container.
* **Stream Key** : `__made_up_stream_name__?pwd=__made_up_password__` - Here `__made_up_stream_name__` is any arbitrary stream name, and `__made_up_password__` is the same password defined for `MULTISTREAMING_PASSWORD` above.

In OBS, you would set the above parameters for a "Custom..." Service in the Stream settings.

The next thing to do is start your stream!

## Future work

Goals for future improvements to this project include:

* Adding more streaming services
* Creating a useful status web page
* Create a control panel web page where you'd set stream keys rather than through environment variables
* Enable management of multiple stream rebroadcasts

## Acknowledgements

This work was heavily influenced by the following articles:

* The basic concept: [https://www.scaleway.com/en/docs/setup-rtmp-streaming-server/](https://www.scaleway.com/en/docs/setup-rtmp-streaming-server/)
* How to use `rtmps` with Facebook: [https://dev.to/lax/rtmps-relay-with-stunnel-12d3](https://dev.to/lax/rtmps-relay-with-stunnel-12d3)
