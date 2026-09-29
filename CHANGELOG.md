# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

### Changed

- The caller identification moved from the `X-Webshare-Source` header into `User-Agent`, which now leads with the product token and ends with the library: `WebshareSDK/<version> (Python; <python version>) webshare-python/<version>`. The `source` client option is unchanged and still replaces that product token.

## [0.1.1] - 2026-08-25

### Changed

- Bump pinned GitHub Actions to their Node 24 releases, clearing the "Node.js 20 is deprecated" CI warnings. First release cut end-to-end through the automated pipeline.

## [0.1.0] - 2026-08-25

### Added

- Initial release.
