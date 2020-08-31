# [1.0.0-beta.20](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.19...v1.0.0-beta.20) (2020-08-31)


### Bug Fixes

* using correct body field for the secret key ([0d5f306](https://github.com/modelon-community/impact-client-python/commit/0d5f306ae14c664577964840feb99422bfc43e63))

# [1.0.0-beta.19](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.18...v1.0.0-beta.19) (2020-08-31)


### Bug Fixes

* Seperating the operations and entities module ([e953cf0](https://github.com/modelon-community/impact-client-python/commit/e953cf022a264ca887e0e8f8f605212554f455db))

# [1.0.0-beta.18](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.17...v1.0.0-beta.18) (2020-08-27)


### Bug Fixes

* Fixed a typo ([4783eb2](https://github.com/modelon-community/impact-client-python/commit/4783eb2f9f47957a03f9767cd7a2a0f0877936a6))

# [1.0.0-beta.17](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.16...v1.0.0-beta.17) (2020-08-26)


### Bug Fixes

* changed imports to be python 3.6 compatible ([ebbbf52](https://github.com/modelon-community/impact-client-python/commit/ebbbf524af365a56f263a349caebbb73927691e9))

# [1.0.0-beta.16](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.15...v1.0.0-beta.16) (2020-08-25)


### Bug Fixes

* Feedback fixes ([88d59e1](https://github.com/modelon-community/impact-client-python/commit/88d59e10ffccd943acb1ab015d0662bce3276cb1))

# [1.0.0-beta.15](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.14...v1.0.0-beta.15) (2020-08-24)


### Bug Fixes

* Removing the pandas dependency due to performance hits ([50fca3a](https://github.com/modelon-community/impact-client-python/commit/50fca3aae4cbf6ccc3e33d1979ef8d58244d0f61))

# [1.0.0-beta.14](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.13...v1.0.0-beta.14) (2020-08-17)


### Bug Fixes

* Upadted the supported api version number ([cc2540e](https://github.com/modelon-community/impact-client-python/commit/cc2540e916784049ac17eae1f526be1c64c12d09))

# [1.0.0-beta.13](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.12...v1.0.0-beta.13) (2020-08-11)


### Bug Fixes

* Performance improvements - Raising exceptions instead of waiting for operation completion when calling compilation/simulation methods/properties ([5834241](https://github.com/modelon-community/impact-client-python/commit/58342416dd6e3d4947b7bcbe3f51bc4921b294b1))

# [1.0.0-beta.12](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.11...v1.0.0-beta.12) (2020-08-10)


### Bug Fixes

* Corrected the to_dict to be method rather than a property ([15297d2](https://github.com/modelon-community/impact-client-python/commit/15297d2cf24e56a98c373fb87061774dca012186))
* Correcting the compilation/simulation status checks. ([d27d1c3](https://github.com/modelon-community/impact-client-python/commit/d27d1c323eca39f135289c580cb113da5beab4fc))
* Removed an unwanted check from wait() function ([f91c5e0](https://github.com/modelon-community/impact-client-python/commit/f91c5e0d4512d7d1b662e1ce089735f483eb7e6f))
* Updated the defaults for get_trajectories ([f77b7e4](https://github.com/modelon-community/impact-client-python/commit/f77b7e473a15376e588f7744768b45fc5c2c57d2))


### Features

* Added possibility to set parameter modifers as a part of experiment definition instead of using legacy routes ([9802d84](https://github.com/modelon-community/impact-client-python/commit/9802d84c6b116c5eddfd53462f630ab0869672f6))

# [1.0.0-beta.11](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.10...v1.0.0-beta.11) (2020-07-28)


### Bug Fixes

* Consistent naming of functions ([fb0cee0](https://github.com/modelon-community/impact-client-python/commit/fb0cee03cf95aa718526fe66020485b1bcb0b0b9))
* Corrected the compilation response from json to plain/text ([69743b4](https://github.com/modelon-community/impact-client-python/commit/69743b4bf437a3e374a047d0e3e0c78711721fdd))
* Formatting and lint fixes ([4d98783](https://github.com/modelon-community/impact-client-python/commit/4d98783cdd8c1bd06471b94d203241b4bd072b62))

# [1.0.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.9...v1.0.0-beta.10) (2020-07-10)


### Features

* integrating custom function entity ([97951b7](https://github.com/modelon-community/impact-client-python/commit/97951b7aace16eaa3deb419f232b9264410cf976))

# [1.0.0-beta.9](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.8...v1.0.0-beta.9) (2020-07-10)


### Bug Fixes

* do not save key if asking for it interactively, it might be invalid ([b8cef20](https://github.com/modelon-community/impact-client-python/commit/b8cef20c5e45308a24f795925453809c67ec1eea))
* save api key even if .impact already exists ([a3fe58e](https://github.com/modelon-community/impact-client-python/commit/a3fe58e53c41f22788be4d8eabe6e43c0fd4545b))
* update tests ([0f6901b](https://github.com/modelon-community/impact-client-python/commit/0f6901bfa3b7b327a6ce88e7713222aedaa556c6))

# [1.0.0-beta.8](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.7...v1.0.0-beta.8) (2020-07-10)


### Features

* Adding functions for the workspace and model class entities ([63cb71b](https://github.com/modelon-community/impact-client-python/commit/63cb71b56e28d171f245ac01d95ecb7add48cf9f))

# [1.0.0-beta.7](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.6...v1.0.0-beta.7) (2020-07-02)


### Bug Fixes

* mypy and formatting corrections ([478b06b](https://github.com/modelon-community/impact-client-python/commit/478b06b2b36ec7e9c38347a24cdda1dc23e0a28f))


### Features

* Added semantic version checks for API ([94fed15](https://github.com/modelon-community/impact-client-python/commit/94fed15d84313d1471c038ae91d411da5d3d9271))

# [1.0.0-beta.6](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.5...v1.0.0-beta.6) (2020-06-30)


### Bug Fixes

* Corrected the response json property name returned for endpoint '/workspaces' ([f1f881b](https://github.com/modelon-community/impact-client-python/commit/f1f881bf9a710e8a4e28d9e513e5f5d16e83f542))

# [1.0.0-beta.5](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.4...v1.0.0-beta.5) (2020-06-29)


### Bug Fixes

* less confusing __repr__ for workspace ([fb42587](https://github.com/modelon-community/impact-client-python/commit/fb4258797df9f0b25dac8c420b1abc320f49fd9a))
* removing test not running on module ([472a917](https://github.com/modelon-community/impact-client-python/commit/472a917a34a59275093de6c7bb60b05f33aa75d2))
* workaround for performance issues on Windows ([ae3eb5b](https://github.com/modelon-community/impact-client-python/commit/ae3eb5bc4609240420e2450452c64e13b070325d))

# [1.0.0-beta.4](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.3...v1.0.0-beta.4) (2020-06-26)


### Bug Fixes

* correct artifactory URL ([4b4195d](https://github.com/modelon-community/impact-client-python/commit/4b4195d6645db9ebfca740e70d144c379efa5d60))

# [1.0.0-beta.3](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.2...v1.0.0-beta.3) (2020-06-26)


### Bug Fixes

* correct artifactory URL ([b0f5615](https://github.com/modelon-community/impact-client-python/commit/b0f56158827d7ae4429675674fdc0cbd3589f866))

# [1.0.0-beta.2](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.1...v1.0.0-beta.2) (2020-06-26)


### Bug Fixes

* making release.sh executable ([71cbac2](https://github.com/modelon-community/impact-client-python/commit/71cbac272d9ba160bd9f79763e90670e4b802d00))

# 1.0.0-beta.1 (2020-06-26)


### Features

* initial repository setup ([1630038](https://github.com/modelon-community/impact-client-python/commit/16300382033c76679adedfefeff9c6de068446dd))
