# Multi-Service RTMP Broadcaster

The goal of this project is to create a Docker-deployed service that will allow you to easily broadcast a live stream to multiple services (YouTube, Twitch, Facebook, etc) at the same time. This stream rebroadcaster is designed to be used by a single source / user.

## Usage
The instructions here assume you are running on Linux. With some modification of the commands, you can make this Docker build work on Windows and Mac OS too.

The first step is to build the docker file. After you clone this repository, `cd` into and and issue:

```
docker build -t multistreaming-server ./multistreaming-server/
```

Once built, start the docker image on a host that has sufficient bandwidth to handle all the rebroadcasting you will do:

```
docker run -it -p 80:80 -p 1935:1935 \
  --env MULTISTREAMING_PASSWORD=__made_up_password__ \
  -v /path/to/my-rtmp-config.json:/rtmp-configuration.json \
  multistreaming-server:latest
```

If this is a host than where you built the docker image, you will need to push the docker image to that host (or build it there). Alternatively, you could use the DockerHub build of this image by pulling and using the `kamprath/multistreaming-server:latest` [Docker image](https://hub.docker.com/repository/docker/kamprath/multistreaming-server). Also, if you plan on doing any transcoding when rebroadcasting a stream, you need to ensure that your docker host's CPU is sufficient for the job. It is recommend that the host CPU has at least four cores for each distinct transcoding the multi-streaming server will do. If the host CPU is not sufficient, bit rates on the transcoded streams will suffer.

Note that some environment variables should be set when running the Docker image:

* `MULTISTREAMING_PASSWORD` _(REQUIRED)_ - This is a password you define and will be used by your steaming software. This is a marginally secure way to prevent other people from pushing to your stream.
* `CONFIG_DISABLE_RECORD` _(OPTIONAL)_ - If this env var is set to a non-empty value, the stream recording feature will be disabled. 
* `CONFIG_NGINX_DEBUG` _(OPTINAL)_ - If this env var is set to a non-empty value, it will enable the nginx debug logging to stderr. This is useful for debugging.
* `CONFIG_FFMPEG_LOG` _(OPTIONAL)_ - If this env var is set to a non-empty value, each ffmpeg process will start logging their output to `/tmp/ffmpeg-$APP.log` in the container. This is useful for debugging issues related to encoding.
* `CONFIG_FFMPEG_MAX_MUXING_QUEUE_SIZE` _(OPTIONAL)_ - This env var must be a numerical value, it will be used as the global default for `-max_muxing_queue_size` argument for the ffmpeg processes. You may need to set this to a higher value (i.e: `4096`) if you run in to this [bug.](https://trac.ffmpeg.org/ticket/6375)

You must also create and JSON file with the RTMP rebroadcasting configuration you desire. This file should get mapped from your local file system to the `/rtmp-configuration.json` file path within the Docker container. The JSON file has the following elements:

* `endpoint`- This is the name of the RTMP ingest endpoint that the source stream will be pushed to. Defaults to `live` if not specified.
* `transcodeProfiles` - This is a JSON object with keys indicating a unique identifier for a transcode profile, and the values specifying the supported transcode options.
    * `pixels` - The pixel dimension that the stream should be transcoded to. Formatted like "1920x1080". If not specified, defaults to "1280x720".
    * `videoBitRate` - The video bit rate that should be used when sending the stream to this destination. Should be a number followed by "k" or "m" for kilo- and mega- bits-per-second. If not specified defaults to "4500k".
    * `videoKeyFrameSecs` - The number of seconds between key frames in the transcoded stream. If not specified, defaults to 2.
    * `videoFrameRate` - The frames per second which the video stream will be re-encoded with, defaults to "30".
    * `audioBitRate` - The bit rate that should be used for the transcoded audio signal. Should be a number followed by "k" or "m" for kilo- and mega- bits-per-second. If not specified, defaults to "160k". If neither `audioBitRate` or `audioSampleRate` are specified, then the audio signal is simply copied from source with no alteration.
    * `audioSampleRate` - The sampling rate to be used for the transcoded audio signal. Should be an integer indicating the sampling Hertz. If not specified, defaults to `48000`. If neither `audioBitRate` or `audioSampleRate` are specified, then the audio signal is simply copied from source with no alteration.
    * `maxMuxingQueueSize` - Individual override for the `CONFIG_FFMPEG_MAX_MUXING_QUEUE_SIZE` env var. See the env var section for the usage.
* `rebroadcastList`- _Required_ Contains a list of JSON objects that each configure a distinct RTMP destination that the stream pushed to the ingest endpoint will be rebroadcasted to. At least one destination should be configured. There is no specific limit on the number of destinations except for the hardware limitations of your host. Each destination is configured with the following JSON elements:
  * `name` - _Required_ A distinct label for this destination. Can be any alphanumeric string with no white space. Must be distinct from all the other destination names in this list.
  * `platform` - _Required_ The platform that this specific rebroadcast stream should be pushed to. The default RTMP destinations will be used for each platform. Supported platforms values are: `youtube`, `facebook`, `twitch`, `instagram`, `periscope`, `microsoft-stream`, `mixcloud`, `dlive` and `custom`. Note that specifying `microsoft-stream` or `custom` will cause the `streamKey` element to be ignored if present and instead use the `fullRTMPURL`
  * `regionCode` - If `periscope` is specified as the platform for this destination, this is the two letter region code that is part of the Periscope server URL. If undefined, it will default to `ca` (the "US West" region)
  * `streamKey` - This is the stream key that identifies the unique stream on the specified platform. This value is provided by the platform. This element must be provided for all `platform` types except for `custom` and `microsoft-stream`.
  * `fullRTMPURL` - If `custom` or `microsoft-stream` is specified in the `platform`, the URL specified in this element is used for the forming destination URL. This should include the `rtmp://` prefix. For the `microsoft-stream` platform, this is the full URL provided in their stream set up. This element is ignored for all other platform types.
  * `transcode` - If present, the stream will be transcoded before rebroadcasting it to this list item's destination. Note that when using this transcoding, the stream will be trancoded to 30 FPS and CBR bit rate. The value is a JSON object with the support for same optoins as an entry in `transcodeProfiles`. Prefer to use `transcodeProfile` key if you have multiple outputs using the same encoding configuration.
  * `transcodeProfile` - If present, this stream will use the transcode settings provided by the `transcodeProfile` referenced by the string identifier set here. If multiple streams refer to the same `transcodeProfile`, the transcoding will only be done once. This option is mutually exclusive with the `transcode` key.


Here is an example of the JSON configuration file:
```
{
  "endpoint": "live",
  "transcodeProfiles": {
    "720_60fps": {
      "pixels": "1280x720",
      "videoBitRate": "4500k",
      "videoFrameRate": 60
    }
  },
  "rebroadcastList": [
    {
      "name": "linkedin-via-restream",
      "platform": "restream",
      "streamKey": "whatever",
      "transcode": {
        "pixels": "1920x1080",
        "videoBitRate": "3500k",
        "videoKeyFrameSecs": 2,
        "audioBitRate": "160k",
        "audioSampleRate": 44100
      }
    },  
    {
      "name": "youtube",
      "platform": "youtube",
      "streamKey": "abc123"
    },
    {
      "name": "facebook-1",
      "platform": "facebook",
      "streamKey": "def456",
      "transcodeProfile": "720_60fps"
    },
    {
      "name": "facebook-2",
      "platform": "facebook",
      "streamKey": "ghi789",
      "transcodeProfile": "720_60fps"
    },
    {
      "name": "periscope",
      "platform": "periscope",
      "regionCode": "ca",
      "streamKey": "jkl012",
      "transcode": {
        "pixels": "1280x720",
        "videoBitRate": "3500k",
        "videoKeyFrameSecs": 3,
        "audioBitRate": "128k",
        "audioSampleRate": 44100
      }
    }
  ]
}
```
Note that as long as the `name` elements are different, you can have more than one destination pushing to the same `platform`, each with different `streamKey` values.

If you would like to capture a recording of the stream sent to the ingest endpoint, bind a local directory on your host to the `/var/www/html/recordings/` file path within the Docker image when launching the Docker container. You can also see statistics about the various streams this server is pushing by visiting this web page: `http://__docker_host_IP_address__/stat`. You can optionally disable recording by setting the env var `CONFIG_DISABLE_RECORD` to a non-empty value.

Once the Docker image is running, set up your stream software with the following parameters:

* **Server** : `rtmp://__docker_host_IP_address__/__endpoint_name__` - Replace `__docker_host_IP_address__` with the IP address of your host that is running this Docker container. Also replace `__endpoint_name__` with the value used for the `endpoint` element in your JSON configuration file.
* **Stream Key** : `__made_up_stream_name__?pwd=__made_up_password__` - Here `__made_up_stream_name__` is any arbitrary stream name, and `__made_up_password__` is the same password defined for `MULTISTREAMING_PASSWORD` above.

In OBS, you would set the above parameters for a "Custom..." Service in the Stream settings.

The next thing to do is start your stream!

## Development

In order to develop on this repository, you must have a python 3.7 environment and [`Pipenv`](https://pypi.org/project/pipenv/) installed.

- Clone the repository
- Navigate to the `multistreaming-server/` directory
- Install dependencies and create the virtual env by running `pipenv install`
- Activate the virtual env by `pipenv shell`

## Future work

Goals for future improvements to this project include:

* Adding more streaming services
* Creating a useful status web page
* Create a control panel web page where you'd set stream keys rather than through a JSON file

Pull requests are welcome!

## Acknowledgements

This work was heavily influenced by the following articles:

* The basic concept: [https://www.scaleway.com/en/docs/setup-rtmp-streaming-server/](https://www.scaleway.com/en/docs/setup-rtmp-streaming-server/)
* How to use `rtmps` with Facebook: [https://dev.to/lax/rtmps-relay-with-stunnel-12d3](https://dev.to/lax/rtmps-relay-with-stunnel-12d3)
