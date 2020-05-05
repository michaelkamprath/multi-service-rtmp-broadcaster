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
  --env "MULTISTREAMING_KEY_TWITCH=__your_twitch_stream_key__" \
  --env "MULTISTREAMING_KEY_FACEBOOK=__your_facebook_stream_key__" \
  --env "MULTISTREAMING_KEY_INSTAGRAM=__your_instagram_stream_key_from_yellow_duck__" \
  --env "MULTISTREAMING_KEY_YOUTUBE=__your_youtube_stream_key__" \  
  --env "MULTISTREAMING_KEY_MICROSOFTSTREAM=__your_microsoft_stream_ingest_url__" \
  --env "MULTISTREAMING_KEY_CUSTOM=__your_full_rtmp_url__" \
  --env "MULTISTREAMING_KEY_PERISCOPE=__your_periscope_stream_key__" \
  --env "PERISCOPE_REGION_ID=__periscope_2-letter_region_code__" \
  --env "MULTISTREAMING_ICECAST=__your_icecast_url__" \
  multistreaming-server:latest
```

Alternatively, you could use the DockerHub build of this image by pulling and using the `kamprath/multistreaming-server:latest` [Docker image](https://hub.docker.com/repository/docker/kamprath/multistreaming-server).

Note that several environment variables are set when running the Docker image:

* `MULTISTREAMING_PASSWORD` _(REQUIRED)_ - This is a password you define and will be used by your steaming software. This is a marginally secure way to prevent other people from pushing to your stream.
* `MULTISTREAMING_KEY_TWITCH` _(OPTIONAL)_ - Your Twitch stream key. Only define if you want to rebroadcast your stream to Twitch.
* `MULTISTREAMING_KEY_FACEBOOK` _(OPTIONAL)_ - Your Facebook stream key. Only define if you want to rebroadcast your stream to Facebook.
* `FACEBOOK_TRANSCODE` _(OPTIONAL)_ - Define and set to 1 if you want to transcode the stream sent to Facebook to it's recommended maximum of 1280x720 @ 4500 Kbps. Not required to stream to Facebook, but if you are streaming above the recommended maximum, Facebook will complain.
* `MULTISTREAMING_KEY_INSTAGRAM` _(OPTIONAL)_ - Your Instagram stream key. You will need to use https://yellowduck.tv/ to retrieve your stream key for Instagram. Only define if you want to rebroadcast your stream to Instagram.
* `MULTISTREAMING_KEY_YOUTUBE` _(OPTIONAL)_ - Your YouTube stream key. Only define if you want to rebroadcast your stream to YouTube.
* `MULTISTREAMING_KEY_MICROSOFTSTREAM` _(OPTIONAL)_ - Your Microsoft Stream Ingest URL. Only define if you want to rebroadcast your stream to Microsoft Stream.
* `MULTISTREAMING_KEY_CUSTOM` _(OPTIONAL)_ - Your full RTMP URL, including rtmp://, to any live stream service. Only define if you want to rebroadcast your stream to a custom service.
* `MULTISTREAMING_KEY_PERISCOPE` _(OPTIONAL)_ - Your Periscope stream key. Only define if you want to rebroadcast your stream to Periscope.
* `PERISCOPE_REGION_ID` _(OPTIONAL)_ - The two letter region code that is part of the Periscope server URL. If undefined, it will default to `ca` (the "US West" region)
* `MULTISTREAMING_ICECAST` _(OPTIONAL)_ - Your full Icecast URL, including icecast://, username, password and mount point. For example: icecast://source:password@icecast-hostname:8000/stream

You could start this docker with no stream keys defined, but that wouldn't do anything interesting then. Note that if your configuration requires transcoding (Facebook or Periscope), then you might get poor bit rates if your CPU isn't up to the job. It is recommended that your modern CPU has at least 4 cores for each transcoding task you enable.

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
