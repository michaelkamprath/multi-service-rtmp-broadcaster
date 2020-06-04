#!/bin/bash

print_help_and_exit()
{
  echo "Usage: "
  echo "    local-deploy.sh [-c /path/to/config.json] [-s <streaming password>] [-d <docker image name>] [-b]"
  echo ""
  echo "Environment Variables (can be used instead of command arguments): "
  echo "    RTMP_SERVER_CONFIG_FILEPATH    : path to RTMP server config JSON file. Can replace -c option."
  echo "    RTMP_SERVER_STREAM_PASSWORD    : Password used by RTMP streaming server for livestreams. Can replace -s option."
  echo "    RTMP_SERVER_DOCKER_IMAGE_NAME  : The image name to pull from Docker hub, or the image name to use if building locally (-b)."
  exit 0
}


build_docker_image_locally()
{
  # assumes this script is running in its original git repository.
  BASEDIR=$(dirname "$BASH_SOURCE")
  if [ $RTMP_SERVER_DOCKER_IMAGE_NAME == $DEFAULT_DOCKER_HUB_IMAGE_NAME ]; then
    RTMP_SERVER_DOCKER_IMAGE_NAME="multistreaming-server:latest"
  fi
  echo "Building Docker image '${RTMP_SERVER_DOCKER_IMAGE_NAME}'"
  docker build -t $RTMP_SERVER_DOCKER_IMAGE_NAME $BASEDIR/../multistreaming-server/
}

DEFAULT_DOCKER_HUB_IMAGE_NAME="kamprath/multistreaming-server:latest"
RTMP_SERVER_DOCKER_IMAGE_NAME=${RTMP_SERVER_DOCKER_IMAGE_NAME:-$DEFAULT_DOCKER_HUB_IMAGE_NAME}

build_locally=false
# check arguments passed to this script
while getopts "c:s:d:bh" option; do
  case "${option}" in
    b)
      # By default this script pulls from Docker hub. This ooption
      # forces a local build of the Docker image.
      build_locally=true
      ;;
    c)
      RTMP_SERVER_CONFIG_FILEPATH=$OPTARG
      ;;
    s)
      RTMP_SERVER_STREAM_PASSWORD=$OPTARG
      ;;
    d)
      RTMP_SERVER_DOCKER_IMAGE_NAME=$OPTARG
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

if [ -z $RTMP_SERVER_CONFIG_FILEPATH ]; then
  echo "You must define a filepath to the streaming server configuration JSON file. Use the -c option."
fi

# Build image if needed
if [ "$build_locally" = true ]; then
    build_docker_image_locally
fi

# Launch the docker image
config_file_absolute_path="$(cd "$(dirname "$RTMP_SERVER_CONFIG_FILEPATH")"; pwd)/$(basename "$RTMP_SERVER_CONFIG_FILEPATH")"
echo "Launching $RTMP_SERVER_DOCKER_IMAGE_NAME Docker image with config at '${config_file_absolute_path}'."
docker_proc_id=$( \
  docker run -d -p 80:80 -p 1935:1935 \
    --env MULTISTREAMING_PASSWORD=${RTMP_SERVER_STREAM_PASSWORD} \
    -v "${config_file_absolute_path}":/rtmp-configuration.json \
    ${RTMP_SERVER_DOCKER_IMAGE_NAME} \
)
docker_short_proc_id=$(echo $docker_proc_id | cut -c1-12)
echo ""
echo "Launched docker container $docker_short_proc_id. To stop this contianer:"
echo "    docker stop $docker_short_proc_id"
echo ""
echo "Visit the Multistreaming Server's statistics page here:"
echo "    http://127.0.0.1/stat"
echo ""
