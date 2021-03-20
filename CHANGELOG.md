# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]
### Changed
* Bumped jinja2 from 2.11.2 to 2.11.3

## [0.4.1]
### Changed
* Updated `ffmpeg` to the 4.3.x version branch

### Fixed
* Corrected bug that occurred when audio bit rated was configured in JSON using an integer
* Corrected a bug where each transcode block pushed to all destinations

## [0.4.0]
### Added
* Support for Mixcloud and DLive.
* Added support for specifying transcode profiles that can be used across multiple destination configurations.
* Add kubernetes manifests, fix nginx logging, streamline the dockerfile

### Changed
* Refactored how processes are managed within the Docker container. Migrated to `jinja2`, use `pipfile` and `supervisord`.

### Fixed
* Corrected a spelling error in the file path that the Docker image looks for the JSON configuration.
* Adjusted the timing of the UpCloud deployment script to better handle timing variation in the cloud service.
* Fixed a bug in the UpCloud deployment script that manifested when the configuration filepath has spaces in it.
* Changed `localhost` references to `127.0.0.1` to prevent IPv6 resolution. 

## [0.3.1]
### Added
* Created a deployment script for running the `multistreaming-server` locally.
* Created a deployment script for the [UpCloud cloud hosting service](https://upcloud.com/signup/?promo=A2CVWA).

### Changed
* Improved error handling in the RTMP configuration generation script.
* Improved error handling in the Lindode deploy script.

### Fixed
* Correct bug in RTMP configuration generation when the audio bit rate is set.
* Reinstated support for Microsoft Stream
* Addressed coding style issues with the python script `rtmp-conf-generator.py`

## [0.3.0]
### Changed
* **This is a major change that breaks any deployment based on prior version.**
* Migrated away from using environment variables to confihure rebroadcasting destinations and instead now used a JSON file.
* Cleanly enables rebroadcasting to multiple stream keys on the same platform.
* Migrated

### Added
* Created a deployment script for the [Linode cloud hosting service](https://www.linode.com/?r=37246e0d6a6198293308e698647804fbfe02845e).

### Fixed
* Corrected how transcoding is implemented: larger buffer, better audio

## [0.2.0]
### Changed
* Migrated Docker base to `jrottenberg/ffmpeg:4.2-alpine` in order to get a more robust `ffmpeg` compilation.
* Migrated RTMP module to use a more recent and currently maintained branch.

### Added
* Ability to transcode the stream being sent to Facebook.

## 0.1.2
* First verison!


[Unreleased]: https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/compare/v0.4.1...HEAD
[0.4.1]: https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/compare/v0.1.2...v0.2.0
