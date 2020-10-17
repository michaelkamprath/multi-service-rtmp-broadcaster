#!/usr/bin/env python3

import json
import re
import sys
import os
import jinja2

#
# Configurable ENV VARS
#

CONFIG_NGINX_DEBUG = os.getenv("CONFIG_NGINX_DEBUG", False)
CONFIG_FFMPEG_LOG = os.getenv("CONFIG_FFMPEG_LOG", False)
CONFIG_FFMPEG_MAX_MUXING_QUEUE_SIZE = os.getenv(
    "CONFIG_FFMPEG_MAX_MUXING_QUEUE_SIZE", False
)
CONFIG_DISABLE_RECORD = os.getenv("CONFIG_DISABLE_RECORD", False)

#
# Defaults
#

RTMP_TRANSCODE_AUDIO_OPTS_COPY = "-c:a copy"
RTMP_TRANSCODE_AUDIO_OPTS_CUSTOM = (
    "-c:a libfdk_aac -b:a %%AUDIO_BIT_RATE%% -ar %%AUDIO_SAMPLE_RATE%%"
)

PUSH_URL_YOUTUBE = "rtmp://a.rtmp.youtube.com/live2/%%STREAM_KEY%%"
PUSH_URL_FACEBOOK = "rtmp://127.0.0.1:19350/rtmp/%%STREAM_KEY%%"
PUSH_URL_TWITCH = "rtmp://live-cdg.twitch.tv/app/%%STREAM_KEY%%"
PUSH_URL_INSTAGRAM = "rtmp://127.0.0.1:19351/rtmp/%%STREAM_KEY%%"
PUSH_URL_PERISCOPE = "rtmp://%%REGION_CODE%%.pscp.tv:80/x/%%STREAM_KEY%%"
PUSH_URL_MICROSOFT_STREAM = "%%RTMP_URL%% app=live/%%APP_NAME%%"
PUSH_URL_MIXCLOUD = "rtmp://rtmp.mixcloud.com/broadcast/%%STREAM_KEY%%"
PUSH_URL_DLIVE = "rtmp://stream.dlive.tv/live/%%STREAM_KEY%%"


DEFAULT_TRANSCODE_CONFIG = {
    "pixels": "1280x720",
    "videoBitRate": "4500k",
    "videoFrameRate": 60,
    "keyFrames": 60,
    "audioOpts": "-c:a copy",
    "logFfmpeg": True if CONFIG_FFMPEG_LOG else False,
    "applicationEndpoints": set(),
    "maxMuxingQueueSize": int(CONFIG_FFMPEG_MAX_MUXING_QUEUE_SIZE)
    if CONFIG_FFMPEG_MAX_MUXING_QUEUE_SIZE
    else None,
}

DEFAULT_AUDIO_OPTS = {
    "audioBitRate": "160k",
    "audioSampleRate": "48000",
}


def generatePlatormPushURL(block_config):
    if "platform" not in block_config:
        print("ERROR - Application block is missing platform element.", file=sys.stderr)
        exit(1)
    push_url = "push-it-real-good"
    if block_config["platform"] == "youtube":
        push_url = PUSH_URL_YOUTUBE.replace("%%STREAM_KEY%%", block_config["streamKey"])
    elif block_config["platform"] == "facebook":
        # must push through stunnel. Push through Facebook stunnel port.
        push_url = PUSH_URL_FACEBOOK.replace(
            "%%STREAM_KEY%%", block_config["streamKey"]
        )
    elif block_config["platform"] == "twitch":
        push_url = PUSH_URL_TWITCH.replace("%%STREAM_KEY%%", block_config["streamKey"])
    elif block_config["platform"] == "instagram":
        # must push through stunnel. Push through Instagram stunnel port.
        push_url = PUSH_URL_INSTAGRAM.replace(
            "%%STREAM_KEY%%", block_config["streamKey"]
        )
    elif block_config["platform"] == "periscope":
        region_code = (
            block_config["regionCode"] if "regionCode" in block_config else "ca"
        )
        push_url = PUSH_URL_PERISCOPE.replace(
            "%%STREAM_KEY%%", block_config["streamKey"]
        ).replace("%%REGION_CODE%%", region_code)
    elif block_config["platform"] == "custom":
        push_url = block_config["customRTMPURL"]
    elif block_config["platform"] == "microsoft-stream":
        ms_source_url = block_config["fullRTMPURL"]
        ms_rtmp_url = re.search(r"^(.*)/live/", ms_source_url).group(1)
        ms_app_name = re.search(r"/live/(.*)$", ms_source_url).group(1)
        push_url = PUSH_URL_MICROSOFT_STREAM.replace(
            "%%RTMP_URL%%", ms_rtmp_url
        ).replace("%%APP_NAME%%", ms_app_name)
    elif block_config["platform"] == "mixcloud":
        push_url = PUSH_URL_MIXCLOUD.replace(
            "%%STREAM_KEY%%", block_config["streamKey"]
        )
    elif block_config["platform"] == "dlive":
        push_url = PUSH_URL_DLIVE.replace("%%STREAM_KEY%%", block_config["streamKey"])
    else:
        print(
            "ERROR - an unsupported platform type was provided in destination configation",
            file=sys.stderr,
        )
        exit(1)
    return push_url


def generateTranscodeConfig(transcode_config_name, block_config, config):
    block_config_name = block_config["name"]
    default_transcode_config = DEFAULT_TRANSCODE_CONFIG.copy()
    transcode_config_block = config.get("transcodeProfiles", {}).get(
        transcode_config_name, block_config.get("transcode")
    )
    if not transcode_config_block:
        print(
            f"ERROR - unable to resolve transcode profile for {transcode_config_name} in block {block_config_name}",
            file=sys.stderr,
        )
        exit(1)
    transcode_config = {
        key: transcode_config_block.get(key, DEFAULT_TRANSCODE_CONFIG[key])
        for key in default_transcode_config.keys()
    }

    if "videoKeyFrameSecs" in transcode_config_block:
        transcode_config["keyFrames"] = 30 * transcode_config_block["videoKeyFrameSecs"]

    if ("audioBitRate" in transcode_config_block) or (
        "audioSampleRate" in transcode_config_block
    ):
        transcode_config["audioOpts"] = RTMP_TRANSCODE_AUDIO_OPTS_CUSTOM.replace(
            "%%AUDIO_BIT_RATE%%",
            transcode_config_block.get(
                "audioBitRate", DEFAULT_AUDIO_OPTS["audioBitRate"]
            ),
        ).replace(
            "%%AUDIO_SAMPLE_RATE%%",
            transcode_config_block.get(
                "audioSampleRate", DEFAULT_AUDIO_OPTS["audioSampleRate"]
            ),
        )
    return transcode_config


def loadJsonConfig(path):
    try:
        with open(path, "r") as f:
            config = json.load(f)
    except json.decoder.JSONDecodeError as err:
        print(
            'ERROR decoding JSON config file "{0}": {1}'.format(path, err),
            file=sys.stderr,
        )
        exit(1)
    except:
        print('ERROR loading JSON config file "{0}"'.format(path), file=sys.stderr)
        exit(1)

    return config


def generateConfig(config_file, nginx_config_template):
    config = loadJsonConfig(config_file)
    # unfortunate hack to make code compatible with previous spelling error
    config_list_key = (
        "rebroacastList" if "rebroacastList" in config else "rebroadcastList"
    )

    record_mode = "off" if CONFIG_DISABLE_RECORD else "all"
    nginx_error_log = True if CONFIG_NGINX_DEBUG else False

    endpoint_name = config["endpoint"] if "endpoint" in config else "live"

    application_configs = {}
    transcode_configs = {}
    push_only_applications = set()

    for block_config in config[config_list_key]:
        if block_config.get("disabled", False):
            continue

        block_config_name = block_config["name"]
        application_configs[block_config_name] = {
            "pushUrl": generatePlatormPushURL(block_config)
        }

        if ("transcodeProfile" in block_config) or "transcode" in block_config:
            transcode_config_name = block_config.get(
                "transcodeProfile", f"inline_{block_config_name}"
            )

            if transcode_config_name not in transcode_configs:
                transcode_configs[transcode_config_name] = generateTranscodeConfig(
                    transcode_config_name, block_config, config
                )
            transcode_configs[transcode_config_name]["applicationEndpoints"].add(
                block_config_name
            )

        else:
            push_only_applications.add(block_config_name)

    with open(nginx_config_template) as fh:
        template = jinja2.Template(fh.read())

    return template.render(
        nginx_error_log=nginx_error_log,
        endpoint_name=endpoint_name,
        record_mode=record_mode,
        transcode_configs=transcode_configs,
        push_only_applications=push_only_applications,
        application_configs=application_configs,
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Must pass two arguments of the JSON configuration file path and the nginx config.",
            file=sys.stderr,
        )
        sys.exit(1)
    rtmp_conf = generateConfig(sys.argv[1], sys.argv[2])
    print(rtmp_conf)
