# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]
### Changed
* Improved error handling in the RTMP configuration generation script.

### Fixed
* Correct bug in RTMP configuration generation when the audio bit rate is set.
* Addressed coding style issues with the python script `rtmp-conf-generator.py`

## [0.3.0]
### Changed
* **This is a major change that breaks any deployment based on prior version.**
* Migrated away from using environment variables to confihure rebroadcasting destinations and instead now used a JSON file.
* Cleanly enables rebroadcasting to multiple stream keys on the same platform.
* Migrated

### Added
* Created a deployment script for the Linode cloud hosting service.

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


[Unreleased]: https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/michaelkamprath/multi-service-rtmp-broadcaster/compare/v0.1.2...v0.2.0
