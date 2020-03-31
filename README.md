# Multi-Service RTMP Broadcaster

The goal of this project is to create a Docker-deployed service that will allow you to easily broadcast a livestream to multiple services (YouTube, Twitch, Facebook, etc) at the same time. This stream rebroadcaster is designed to be used by a single source / user. 

## Usage
The instructions here assume you are running on linux. With some modification of the commands, you can make this Docker build work on Windows and Mac OS too.

The first step is to build the docker file. After you clone this repository, `cd` into and and issue:

```
docker build -t multistreaming-server ./multistreaming-server/
```

Once built, start the serve on the same host as where your streaming source (e.g., OBS) is running with:

```
docker run -it -p 80:80 -p 1935:1935 \
  --env MULTISTEAMING_PASSWORD=__made_up_password__ \
  --env "MULTISTEAMING_KEY_TWITCH=__your_twitch_stream_key__" \
  --env "MULTISTEAMING_KEY_FACEBOOK=__your_facebook_stream_key__" \
  --env "MULTISTEAMING_KEY_YOUTUBE=__your_youtube_stream_key__" \  
  multistreaming-server:latest
```

Note that several environment variables are set:

* `MULTISTEAMING_PASSWORD` _(REQUIRED)_ - This is a password you define and will be used by your steaming software. This is a marginally secure way to prevent other people from pushing to your stream. 
* `MULTISTEAMING_KEY_TWITCH` _(OPTIONAL)_ - Your Twitch stream key. Only define if you want to rebroadcast your stream to Twitch.
* `MULTISTEAMING_KEY_FACEBOOK` _(OPTIONAL)_ - Your Facebook stream key. Only define if you want to rebroadcast your stream to Facebook.
* `MULTISTEAMING_KEY_YOUTUBE` _(OPTIONAL)_ - Your YouTube stream key. Only define if you want to rebroadcast your stream to YouTube.

You could start this docker with no stream keys defined, but that wouldn't do anything interesting then.

Once the Docker image is running, set up your stream software with the following paramters:

* *Server* - `rtmp://<docker_host_IP_address>/live`
* *Stream Key* - `__made_up_stream_name__?pwd=__made_up_password__` : Here `__made_up_stream_name__` is any arbitrary stream name, and `__made_up_password__` is the same password defined for `MULTISTEAMING_PASSWORD` above.

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
