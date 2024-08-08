# [4.5.0-dev.3](https://github.com/modelon-community/impact-client-python/compare/v4.5.0-dev.2...v4.5.0-dev.3) (2024-08-08)


### Bug Fixes

* fix typo in docstring example ([1c99c68](https://github.com/modelon-community/impact-client-python/commit/1c99c6855b61aa2163abf3bd5976d9b8c48c3048))

# [4.5.0-dev.2](https://github.com/modelon-community/impact-client-python/compare/v4.5.0-dev.1...v4.5.0-dev.2) (2024-07-30)


### Bug Fixes

* use params argument in request.get to pass query strings instead of passing them in url ([f2142c7](https://github.com/modelon-community/impact-client-python/commit/f2142c7e012c59cc2175237c1ee7215188485bed))

# [4.5.0-dev.1](https://github.com/modelon-community/impact-client-python/compare/v4.4.4...v4.5.0-dev.1) (2024-07-30)


### Bug Fixes

* change default to True for has_default in find method ([5bbafd0](https://github.com/modelon-community/impact-client-python/commit/5bbafd02fa975ff9535123ce50d79b056e30805c))
* updated the AccessSettings object with updated protocol for workspace publish ([a08e9c0](https://github.com/modelon-community/impact-client-python/commit/a08e9c09e4856e8d6c40a84f10085a744d90c0a5))


### Features

* add api support for listing and cleaning orphaned published ws ([55ae97c](https://github.com/modelon-community/impact-client-python/commit/55ae97c01cb8e3fd71654e17cd3851888bcc0532))

## [4.4.4](https://github.com/modelon-community/impact-client-python/compare/v4.4.3...v4.4.4) (2024-07-11)


### Bug Fixes

* propagate context to is_jupyterhub_url method calls ([113b1a5](https://github.com/modelon-community/impact-client-python/commit/113b1a539d747c320a5be52e756eba88f0af17b7))

## [4.4.3](https://github.com/modelon-community/impact-client-python/compare/v4.4.2...v4.4.3) (2024-07-11)


### Bug Fixes

* pass user defined context to unauthenticated HTTPClient ([9622de6](https://github.com/modelon-community/impact-client-python/commit/9622de6146d9fc288c0e769272c35f33bb7fc9bf))

## [4.4.2](https://github.com/modelon-community/impact-client-python/compare/v4.4.1...v4.4.2) (2024-06-26)


### Bug Fixes

* remove assertion for simulation completion from experiment entity api's calls ([1084637](https://github.com/modelon-community/impact-client-python/commit/108463769bdfdb6d73ec761e4592bf9b95ee774e))

## [4.4.1](https://github.com/modelon-community/impact-client-python/compare/v4.4.0...v4.4.1) (2024-06-26)


### Bug Fixes

* make case result import, custom artifact import and get result variable import api's non-experimental ([013e12c](https://github.com/modelon-community/impact-client-python/commit/013e12c130e53a5a61ac8e22f43fdb65087e84ed))
* raise specific exceptions for failed case result and custom artfact import. Also added tests for custom artifact import, case result import and case result variables fetch apis ([3937df7](https://github.com/modelon-community/impact-client-python/commit/3937df71d49f46cec2b00e36517179dc0aaa9867))

# [4.4.0](https://github.com/modelon-community/impact-client-python/compare/v4.3.0...v4.4.0) (2024-06-25)


### Bug Fixes

* bump lower api compatibility version ([9d2a1c4](https://github.com/modelon-community/impact-client-python/commit/9d2a1c4283366d390016fb764611383fc22d138e))
* renamed of internal SAL method to fetch retsult variables for experiment ([c37a67f](https://github.com/modelon-community/impact-client-python/commit/c37a67f1a76d672d6c6384cc77e14548c7e413f0))


### Features

* add api support for fetching single case result variables and updated relevant code to use this api ([240ef12](https://github.com/modelon-community/impact-client-python/commit/240ef1264dc6905d1385e7848d004aa592a87c79))
* added support for result import to case behind experimental flag ([5ecde7f](https://github.com/modelon-community/impact-client-python/commit/5ecde7f3d91dc61384a3196952fce05d3a89e980))

# [4.3.0](https://github.com/modelon-community/impact-client-python/compare/v4.2.0...v4.3.0) (2024-06-12)


### Bug Fixes

* made artifact ID optional and added overwrite flag ([fd2dbbc](https://github.com/modelon-community/impact-client-python/commit/fd2dbbcaf6bed054d1ccdbdefe689662e0ab80a5))
* made import_custom_artifact api experimental ([5ab0201](https://github.com/modelon-community/impact-client-python/commit/5ab0201866c8fd80c9d1507d8675604d43be9f17))


### Features

* added support for custom artifact import for a case ([fb16b87](https://github.com/modelon-community/impact-client-python/commit/fb16b878f32d796bc36811b25f255cfb060c99e0))

# [4.2.0](https://github.com/modelon-community/impact-client-python/compare/v4.1.1...v4.2.0) (2024-06-10)


### Features

* added support for VariableNames data type for custom function ([14b5d51](https://github.com/modelon-community/impact-client-python/commit/14b5d514154a2f58e3ebedbaeafa00335626ff11))

## [4.1.1](https://github.com/modelon-community/impact-client-python/compare/v4.1.0...v4.1.1) (2024-06-10)


### Bug Fixes

* added typing-extensions as a dependency to the client ([73f45a2](https://github.com/modelon-community/impact-client-python/commit/73f45a25a32c0689c073294c5cd23045d5767f6d))

# [4.1.0](https://github.com/modelon-community/impact-client-python/compare/v4.0.0...v4.1.0) (2024-05-31)


### Bug Fixes

* added super function to Case entity to pass attribues to base class ([04181e0](https://github.com/modelon-community/impact-client-python/commit/04181e034ad8333c1c11b27c4d78569b0d97cd97))
* move CustomArtifact class from case entity and added a reference base entity for it ([85e982a](https://github.com/modelon-community/impact-client-python/commit/85e982ae9a6633a0a49bb010e8dcc3018523392c))
* rename CustomArtifactReference -> CustomArtifactURI and ModelicaResourceReference -> ModelicaResourceURI ([ca38950](https://github.com/modelon-community/impact-client-python/commit/ca3895061ba0c25346466f6f436c2d8239fd9ad5))


### Features

* support for FileURI data type in custom function ([f5bafa2](https://github.com/modelon-community/impact-client-python/commit/f5bafa2909ff0e97ae782ec7e13c758d602c25e6))

# [4.0.0](https://github.com/modelon-community/impact-client-python/compare/v3.20.0...v4.0.0) (2024-05-17)


### Features

* update Modelon Impact compatibility version range ([b27c8a8](https://github.com/modelon-community/impact-client-python/commit/b27c8a8eda08c15d91d786f8b9842e6b0092bd30))
* updated the python client to use the new api key based workflow ([dec6145](https://github.com/modelon-community/impact-client-python/commit/dec6145fa60e2e8722d8a340c088330b9f71b24b))


### BREAKING CHANGES

* updated the minimum api compatibility to 4.11.0

# [3.20.0](https://github.com/modelon-community/impact-client-python/compare/v3.19.0...v3.20.0) (2024-05-08)


### Bug Fixes

* added a ParameterDict class for custom function parameters that has a special method to convert to raw dict ([9c8699c](https://github.com/modelon-community/impact-client-python/commit/9c8699c8691bbea6afbfc286190ef10509ea93c1))
* added support for fetching param values as objects from Case definition ([39f63cf](https://github.com/modelon-community/impact-client-python/commit/39f63cfbdf9d70c68776ff032180e433aed53818))
* added support to retrieve ExperimentResult object when fetching definition from experiment ([942c406](https://github.com/modelon-community/impact-client-python/commit/942c4061378911d39ba17af3f7d3010e9ac612d6))
* assert for types in parameter values ([d3ba36f](https://github.com/modelon-community/impact-client-python/commit/d3ba36f9709b77821117d719410874a995f4ff49))
* created a reference class for experiment and case entities and a method to regenerate entities from references ([694fd39](https://github.com/modelon-community/impact-client-python/commit/694fd3989b0c66df77aee416605b29640232865a))
* defaultValue should be an optional value in Custom functions ([459787e](https://github.com/modelon-community/impact-client-python/commit/459787e90d311cf5843cd1b860a80be5b618fc41))
* split entity from ref into seperate methods and made them experimental ([d982b17](https://github.com/modelon-community/impact-client-python/commit/d982b17b57d70e77ff655c3dbd1b77f15da8a4c9))


### Features

* added support for new custom function parameter data types ([0fc8a62](https://github.com/modelon-community/impact-client-python/commit/0fc8a62d9f2a252949d489622d0dfa2712f4e828))

# [3.19.0](https://github.com/modelon-community/impact-client-python/compare/v3.18.1...v3.19.0) (2024-05-03)


### Features

* add convinience label property to the Experiment entity ([9c69ab4](https://github.com/modelon-community/impact-client-python/commit/9c69ab4111285964a9b4bc3ac016e730fd10a309))

## [3.18.1](https://github.com/modelon-community/impact-client-python/compare/v3.18.0...v3.18.1) (2024-05-02)


### Bug Fixes

* add another mock user for tests ([5fcf1bc](https://github.com/modelon-community/impact-client-python/commit/5fcf1bc82d70d680d32602b025c4ff556d341e90))

# [3.18.0](https://github.com/modelon-community/impact-client-python/compare/v3.17.0...v3.18.0) (2024-04-25)


### Bug Fixes

* remove experimental convinience methods used to retrieve definition from experiemnt and case results ([d15a292](https://github.com/modelon-community/impact-client-python/commit/d15a2929aa87db5826778135ca5f23e24bf964eb))


### Features

* added convinience properties to Experiment definition classes ([fb0518e](https://github.com/modelon-community/impact-client-python/commit/fb0518e8572bedcf4cbda39d901e45e018bbb5b0))

# [3.17.0](https://github.com/modelon-community/impact-client-python/compare/v3.16.1...v3.17.0) (2024-04-22)


### Bug Fixes

* add experimental flag for create_experiment_definition_from_experiment_result and create_experiment_definition_from_case_result methods ([2812f83](https://github.com/modelon-community/impact-client-python/commit/2812f83b2b804cc52abd88a50eccef35ff6abb04))
* the create_experiment_definition_from_experiment_result method should ensure the custom function parametrization is preserved as well ([d526fb7](https://github.com/modelon-community/impact-client-python/commit/d526fb715719b701f8f9e259721741d9c873eb35))


### Features

* added support to create_experiment_definition_from_case_result ([3be9cf9](https://github.com/modelon-community/impact-client-python/commit/3be9cf9372ee85b90ae5852106417f4acdeccc6e))

## [3.16.1](https://github.com/modelon-community/impact-client-python/compare/v3.16.0...v3.16.1) (2024-04-18)


### Bug Fixes

* minor correction to docs in FMU based workflow section ([04af5bc](https://github.com/modelon-community/impact-client-python/commit/04af5bc5931b4a74adba3b4074279140919f2bac))
* minor typo fix for Sobol space coverage ([f268e48](https://github.com/modelon-community/impact-client-python/commit/f268e48128a06878d7acd60d3c8b5a045c72c255))

# [3.16.0](https://github.com/modelon-community/impact-client-python/compare/v3.15.0...v3.16.0) (2024-04-17)


### Bug Fixes

* fetch project definition on demand when calling project.definition. Updated project entity tests to use vcr ([1abd5c9](https://github.com/modelon-community/impact-client-python/commit/1abd5c90de60b3e145aace621402e2187f817e29))


### Features

* added support for renaming project ([c2e0d73](https://github.com/modelon-community/impact-client-python/commit/c2e0d73fd2970a4ab654e707dbbb672899f51060))

# [3.15.0](https://github.com/modelon-community/impact-client-python/compare/v3.14.0...v3.15.0) (2024-04-11)


### Bug Fixes

* correct MODELON_IMPACT_CLIENT_URL in Makefile ([d954cf8](https://github.com/modelon-community/impact-client-python/commit/d954cf8b52878800fd8060f9da48d4f5bbf0f581))
* remove experimental flag from tests that test non-experimental api ([ef8f49e](https://github.com/modelon-community/impact-client-python/commit/ef8f49ecc898c126c2e0d94a7c648323ba1980ad))


### Features

* added a utility method to get published workspaces if any corresponding to a local workspace ([47c519e](https://github.com/modelon-community/impact-client-python/commit/47c519e18a667fbc5e31d99d2e7dae02c211acd7))
* added app_mode property to PublishedWorkspaceDefinition class ([7126f1b](https://github.com/modelon-community/impact-client-python/commit/7126f1bbb7016840aa8a676b160245f0096a983e))

# [3.14.0](https://github.com/modelon-community/impact-client-python/compare/v3.13.1...v3.14.0) (2024-04-11)


### Bug Fixes

* fixed a bug where modifiers key was not set when initializing from case for an extension ([87d544d](https://github.com/modelon-community/impact-client-python/commit/87d544d4935c643822e4c3dae2625eb4e4a15829))


### Features

* added support for fetching experiment definition given a experiment result ([106b88a](https://github.com/modelon-community/impact-client-python/commit/106b88a441c9564567deb3fa0e81b4d1e175fe65))

## [3.13.1](https://github.com/modelon-community/impact-client-python/compare/v3.13.0...v3.13.1) (2024-04-05)


### Bug Fixes

* correct documentation for import_to_userspace and experimental method get_access_control_list ([812c714](https://github.com/modelon-community/impact-client-python/commit/812c71495eb240577afe53aad10acc0d0581abef))

# [3.13.0](https://github.com/modelon-community/impact-client-python/compare/v3.12.0...v3.13.0) (2024-04-03)


### Bug Fixes

* ensure 'with_modifiers' method don't removes any previously set modifiers ([0540cd5](https://github.com/modelon-community/impact-client-python/commit/0540cd5fc0c9d4c64b7b52106b0b9a8263ba8074))
* handle 'alpha' for Beta operator modifier correctly ([509de36](https://github.com/modelon-community/impact-client-python/commit/509de36f7b00338486dc5073e28c462f20b81fdd))
* incorrect type for expansion paramter in with_expansion method for experiment ([2136071](https://github.com/modelon-community/impact-client-python/commit/2136071df9e3da1f388d763343cc00da29664b3b))
* type for definition input to create_experiment method is now correct ([0ae1664](https://github.com/modelon-community/impact-client-python/commit/0ae1664c4b30321c351637164e14b893114b009b))


### Features

* adding experimental support for version 3 of experiment definition with enumeration support ([c0725a4](https://github.com/modelon-community/impact-client-python/commit/c0725a404efcd68119309fc9d63b09d2506dbb4c))
* verify consistent types for choices modifier ([420b796](https://github.com/modelon-community/impact-client-python/commit/420b796872767f87b37c4197ca14bb6a21107b54))

# [3.12.0](https://github.com/modelon-community/impact-client-python/compare/v3.11.4...v3.12.0) (2024-04-02)


### Features

* added client method to fetch user data ([0c671f0](https://github.com/modelon-community/impact-client-python/commit/0c671f0a9654f12d5974a8e57075ebe7874c006a))

## [3.11.4](https://github.com/modelon-community/impact-client-python/compare/v3.11.3...v3.11.4) (2024-03-26)


### Bug Fixes

* formatting fixes ([9f2ff5e](https://github.com/modelon-community/impact-client-python/commit/9f2ff5e60134cfbeb33a54cb676fd3d1939476ab))
* more manual formatting fixes ([46c10a6](https://github.com/modelon-community/impact-client-python/commit/46c10a6d1c52f868d3a8c47583e670fd6fcb95b6))

## [3.11.3](https://github.com/modelon-community/impact-client-python/compare/v3.11.2...v3.11.3) (2024-03-26)


### Bug Fixes

* assert username in mock mail or git username before recording tests ([1a03b61](https://github.com/modelon-community/impact-client-python/commit/1a03b61403849dc8aa242595e1ccd06737b55551))
* default MODELON_IMPACT_CLIENT_URL to modelon cloud for test generation ([351c338](https://github.com/modelon-community/impact-client-python/commit/351c33854dc40e83e9db99bfbed2ac4647f99413))

## [3.11.2](https://github.com/modelon-community/impact-client-python/compare/v3.11.1...v3.11.2) (2024-03-25)


### Bug Fixes

* use vcr based tests for client and workspace entities ([c082719](https://github.com/modelon-community/impact-client-python/commit/c082719161e737347bc0178d1c80de3578658c0d))

## [3.11.1](https://github.com/modelon-community/impact-client-python/compare/v3.11.0...v3.11.1) (2024-02-29)


### Bug Fixes

* updated experimental get_access_control_list method as per new protocol on MI ([455b279](https://github.com/modelon-community/impact-client-python/commit/455b2795cac57f59295805052b497e3a00941e17))

# [3.11.0](https://github.com/modelon-community/impact-client-python/compare/v3.10.0...v3.11.0) (2024-02-27)


### Bug Fixes

* rename experimental user access methods for uniformity with other access related methods ([18549f2](https://github.com/modelon-community/impact-client-python/commit/18549f29e5cad177f83cc269ffe742a7a36ea993))


### Features

* add support to grant/revoke group access ([300d05a](https://github.com/modelon-community/impact-client-python/commit/300d05a88a074e1ca07575ea8892bc677178cc58))

# [3.10.0](https://github.com/modelon-community/impact-client-python/compare/v3.9.0...v3.10.0) (2024-02-19)


### Features

* added possibility to find published workspaces filtered by groupName ([c6f14fa](https://github.com/modelon-community/impact-client-python/commit/c6f14fa0070a83dcbe3c8d6795db102e4fa6e973))

# [3.9.0](https://github.com/modelon-community/impact-client-python/compare/v3.8.1...v3.9.0) (2024-02-15)


### Bug Fixes

* added PublishedWorkspaceType enum to __init__.py for easy import and update docs ([c7021d3](https://github.com/modelon-community/impact-client-python/commit/c7021d367ecd9820bc766e3db15a5b62441c006d))
* fix method typo in doc string ([5b1a835](https://github.com/modelon-community/impact-client-python/commit/5b1a8355885b0932afe454643ef86c4d10e22e44))


### Features

* added possibility to export a workspace without group share ([b025b09](https://github.com/modelon-community/impact-client-python/commit/b025b09a2d8f05953e677c70ac0b7651a7a5a659))

## [3.8.1](https://github.com/modelon-community/impact-client-python/compare/v3.8.0...v3.8.1) (2024-02-12)


### Bug Fixes

* minor formatting doc fixes ([6f3beef](https://github.com/modelon-community/impact-client-python/commit/6f3beef9a38256f4d4a5c66e313da18abd2a0a12))

# [3.8.0](https://github.com/modelon-community/impact-client-python/compare/v3.7.1...v3.8.0) (2024-02-01)


### Features

* added support to grant community access to published workspacce ([8634861](https://github.com/modelon-community/impact-client-python/commit/86348618f021c8256a7aef4fc27567484ed1a172))

## [3.7.1](https://github.com/modelon-community/impact-client-python/compare/v3.7.0...v3.7.1) (2024-02-01)


### Bug Fixes

* lower python version restrictions to 3.8 ([e687f45](https://github.com/modelon-community/impact-client-python/commit/e687f453befc6ac7757baadf4ace90189290168d))

# [3.7.0](https://github.com/modelon-community/impact-client-python/compare/v3.6.2...v3.7.0) (2024-01-25)


### Features

* added api to get acl for a published workspace ([8884a5c](https://github.com/modelon-community/impact-client-python/commit/8884a5c292de033dc715b3b8e928e4f6d6a376a4))

## [3.6.2](https://github.com/modelon-community/impact-client-python/compare/v3.6.1...v3.6.2) (2024-01-24)


### Bug Fixes

* add experimental flag for experimental apis ([c38c696](https://github.com/modelon-community/impact-client-python/commit/c38c696b617e92bf109176b406cb5d96b0ebaadb))
* updating the import_to_userspace api to use the backend api when performing an update operation ([5bc932f](https://github.com/modelon-community/impact-client-python/commit/5bc932f3ab22ceffa4ddd3cc443dfd030c88bebf))

## [3.6.1](https://github.com/modelon-community/impact-client-python/compare/v3.6.0...v3.6.1) (2024-01-22)


### Bug Fixes

* bumping the readthedocs-sphinx-search version ([456a6c5](https://github.com/modelon-community/impact-client-python/commit/456a6c523369fa3be3a549217fa2027c9ea63d0e))

# [3.6.0](https://github.com/modelon-community/impact-client-python/compare/v3.5.1...v3.6.0) (2024-01-22)


### Bug Fixes

* added ProjectType to the client __init__.py  for easy import ([26c0c7d](https://github.com/modelon-community/impact-client-python/commit/26c0c7deebd50de56a6f63c5377eb05a3a852888))


### Features

* add support to filter projects for storage location ([6174675](https://github.com/modelon-community/impact-client-python/commit/6174675492ad28b3b1ab1f1048dd5ace85a1544f))

## [3.5.1](https://github.com/modelon-community/impact-client-python/compare/v3.5.0...v3.5.1) (2024-01-03)


### Bug Fixes

* renamed tenant -> tenant_id as per new schema/terminology ([a820127](https://github.com/modelon-community/impact-client-python/commit/a820127bfdab7ade2cb7c05ca761c865fe84c574))

# [3.5.0](https://github.com/modelon-community/impact-client-python/compare/v3.4.2...v3.5.0) (2024-01-02)


### Bug Fixes

* add support for fetching workspaces by kind ([fc65b01](https://github.com/modelon-community/impact-client-python/commit/fc65b01dd95f4b2a588297feb695ab95bcff93bf))
* added request as a special case for get when it fails with access error ([3fa7c2d](https://github.com/modelon-community/impact-client-python/commit/3fa7c2d987896c6c9857d6fa6abfe1a4089451e1))
* added request as a special case for get when it fails with access error ([d16bd4b](https://github.com/modelon-community/impact-client-python/commit/d16bd4b2c0705dc67b2403d52be7548926476a2f))
* added request as a special case for get when it fails with access error ([55a3f9d](https://github.com/modelon-community/impact-client-python/commit/55a3f9dc5b43ba50211894016aaad04a57d92d9c))
* added tests for client.get_by_access_kind ([bad0c72](https://github.com/modelon-community/impact-client-python/commit/bad0c72e1233f76b7f3d32f4f9df9555c58b08b9))
* propagated first and max filtering for get_by_access_kind ([d5bbe58](https://github.com/modelon-community/impact-client-python/commit/d5bbe58d07abcffdc037b44bc53c4ff414375cf8))
* refactored publish workspace functions out of Client module ([4300019](https://github.com/modelon-community/impact-client-python/commit/4300019776696beda2b30786b57676b9373acafe))
* rename grant_access to grant_user_access ([0d1cc36](https://github.com/modelon-community/impact-client-python/commit/0d1cc36fbdfc77cb7d6b9884e68491237816c5e7))


### Features

* added support for granting and revoking access to published workspace ([2143e89](https://github.com/modelon-community/impact-client-python/commit/2143e8931fa47bc61aa50c4d6ee57ec97be4045a))

## [3.4.2](https://github.com/modelon-community/impact-client-python/compare/v3.4.1...v3.4.2) (2023-12-14)


### Bug Fixes

* correct http method(POST->PATCH) for request access ([3a91758](https://github.com/modelon-community/impact-client-python/commit/3a9175827e6dc4e8ca462080ccd72c838937db59))

## [3.4.1](https://github.com/modelon-community/impact-client-python/compare/v3.4.0...v3.4.1) (2023-12-14)


### Bug Fixes

* corrected the api path for request access ([0697279](https://github.com/modelon-community/impact-client-python/commit/0697279b2c3a03ff9a1ae72820a3d202bee7c5ab))

# [3.4.0](https://github.com/modelon-community/impact-client-python/compare/v3.3.0...v3.4.0) (2023-12-06)


### Bug Fixes

* added docstrings for workspace and workspace definition properties ([e43d6a7](https://github.com/modelon-community/impact-client-python/commit/e43d6a75933f07a1730cb3b103c4d341b8a291a0))
* added logging if an existing workspace is found during import of published workspaces ([671ed6e](https://github.com/modelon-community/impact-client-python/commit/671ed6ebf081515f080d689b67bc6fde17bff1a3))
* always fetch latest workspace definition ([13bfcb6](https://github.com/modelon-community/impact-client-python/commit/13bfcb648d90630ae9e15f8a95926d0457ded4cf))
* remove workspace definition from workspace entity constructor ([42a0c20](https://github.com/modelon-community/impact-client-python/commit/42a0c20282ed4942e4910f74660eb2856a29705c))
* use seperate rename method to rename a workspace ([bf85a59](https://github.com/modelon-community/impact-client-python/commit/bf85a5934c7258faae71e9c6666b42b2db7ffeee))


### Features

* added possibility to rename a workspace ([99774e4](https://github.com/modelon-community/impact-client-python/commit/99774e434be7611889c7d8d4ad724834c3923de5))

# [3.3.0](https://github.com/modelon-community/impact-client-python/compare/v3.2.1...v3.3.0) (2023-12-05)


### Features

* add support for exporting publishing app mode workspaces ([d318dba](https://github.com/modelon-community/impact-client-python/commit/d318dba8600ab60920b1285718770c20d6ebc5a5))

## [3.2.1](https://github.com/modelon-community/impact-client-python/compare/v3.2.0...v3.2.1) (2023-12-01)


### Bug Fixes

* added userspace to known spellings ([7bcad1d](https://github.com/modelon-community/impact-client-python/commit/7bcad1d26c0f4381cf63127ffd15b5350d86e7bd))
* minor docs fix ([ad06278](https://github.com/modelon-community/impact-client-python/commit/ad0627827052c36b90aad9fac0cd1d44b2e9ca3d))

# [3.2.0](https://github.com/modelon-community/impact-client-python/compare/v3.1.0...v3.2.0) (2023-11-30)


### Bug Fixes

* fix import_to_userspace test ([8e0f764](https://github.com/modelon-community/impact-client-python/commit/8e0f764467fed30b6a48264a78861d50d70e9a5a))
* improve import_to_userspace docstring ([2235670](https://github.com/modelon-community/impact-client-python/commit/22356700c869d36287f384b22296c7ab894d24a2))
* lint fixes ([dd0b404](https://github.com/modelon-community/impact-client-python/commit/dd0b40422ad450336c46635da220ec3c4a5ed4d6))


### Features

* add possibility to fetch updates from a published workspace ([7fafcf7](https://github.com/modelon-community/impact-client-python/commit/7fafcf76f1f084ed2318f71d3736b7f560eb7e73))
* add support for filtering workspace based on name, app_mode and sharing_id ([bf28a11](https://github.com/modelon-community/impact-client-python/commit/bf28a1103ac5429b751dc1f10f412b6e030558d0))

# [3.1.0](https://github.com/modelon-community/impact-client-python/compare/v3.0.4...v3.1.0) (2023-11-20)


### Bug Fixes

* add experimental markers ([b6759e7](https://github.com/modelon-community/impact-client-python/commit/b6759e7640aab8691d6b2e36c53fdeffed79c0b4))
* add type hints ([9289706](https://github.com/modelon-community/impact-client-python/commit/9289706baa6093242e0fc6775c6259aecaeb2661))
* added tests ([1bee05f](https://github.com/modelon-community/impact-client-python/commit/1bee05f9f4c0d3269cf3fa5714ab4344fb01fa2b))
* decorate workspace publish methods with experimental flag ([76977ff](https://github.com/modelon-community/impact-client-python/commit/76977ff540bf3903edd80b274a14bf51be97427e))
* docformatter fixes ([e25cd85](https://github.com/modelon-community/impact-client-python/commit/e25cd85d11709de68ad2bfa82ed6a58814e92cfc))
* make Experimental class callable ([c7e7304](https://github.com/modelon-community/impact-client-python/commit/c7e73043c3a5a109905c6bac54b7b363c9b22740))


### Features

* added support for publishing workspaces to cloud ([c09687a](https://github.com/modelon-community/impact-client-python/commit/c09687a53a338eef8f71e85db695ac9f2e565bf7))

## [3.0.4](https://github.com/modelon-community/impact-client-python/compare/v3.0.3...v3.0.4) (2023-09-12)


### Bug Fixes

* fixed typo in get_model_description return description ([d227876](https://github.com/modelon-community/impact-client-python/commit/d22787663ef9f0cc2551208d3d22a3acfe9ac6ab))
* minor error message format fix ([b43d589](https://github.com/modelon-community/impact-client-python/commit/b43d58997fd0d86c3c204dada50e40f8bd6f688f))
* remove unsupported platform win32 from compilation options ([6ca1abf](https://github.com/modelon-community/impact-client-python/commit/6ca1abff99efe7179dacc1ccf9a142e4a4d59ca9))

## [3.0.3](https://github.com/modelon-community/impact-client-python/compare/v3.0.2...v3.0.3) (2023-06-13)


### Bug Fixes

* corrected query string for get_projects api ([02f1d19](https://github.com/modelon-community/impact-client-python/commit/02f1d198c757891d7a7d567ab16a8a4ae9a4605a))

## [3.0.2](https://github.com/modelon-community/impact-client-python/compare/v3.0.1...v3.0.2) (2023-06-09)


### Bug Fixes

* fixed the show method in ModelDescription class to print formatted xml ([12d9d3d](https://github.com/modelon-community/impact-client-python/commit/12d9d3d1cad658dfe2e0d245a492c176a7dd59f0))

## [3.0.1](https://github.com/modelon-community/impact-client-python/compare/v3.0.0...v3.0.1) (2023-06-09)


### Bug Fixes

* corrected the trajectory response format in get_last_point method ([bdd143a](https://github.com/modelon-community/impact-client-python/commit/bdd143a7f9b3150f07287d2d580945134f40bc62))

# [3.0.0](https://github.com/modelon-community/impact-client-python/compare/v2.4.0...v3.0.0) (2023-06-08)


### Bug Fixes

* add missing type hints ([03dc33b](https://github.com/modelon-community/impact-client-python/commit/03dc33b5a187439210b73ebe3bd813ae17dd0ef3))
* add py.typed marker ([8761cc1](https://github.com/modelon-community/impact-client-python/commit/8761cc1699c490d488707e0f27202693bc35778f))
* added additional checks and improved error message ([e7a9b25](https://github.com/modelon-community/impact-client-python/commit/e7a9b25d001ab48459abca0a0e5f2a22a8065e5d))
* added an abstract interface class for entities ([1885d4b](https://github.com/modelon-community/impact-client-python/commit/1885d4b2998466362e9cf66e9a8d74f493fd14d2))
* added an extension to auto-generate type hints ([1d7b8d6](https://github.com/modelon-community/impact-client-python/commit/1d7b8d60d135e5a629b647a462882eb44c229991))
* added convinience methods and arguments for fetching projects ([110035d](https://github.com/modelon-community/impact-client-python/commit/110035dbce62e00297b58986cbf675b7681f4e8d))
* added docs for expansion alorithms ([66ea11e](https://github.com/modelon-community/impact-client-python/commit/66ea11e110ea82720f7a6bbb82b92aa1822c7d36))
* added docs for ExperimentRunInfo class ([9a79f3f](https://github.com/modelon-community/impact-client-python/commit/9a79f3f902ec5542c0fa8dde55a8eb08cc2cfdfc))
* added docs for initialize_from in case entity ([fe42407](https://github.com/modelon-community/impact-client-python/commit/fe424072a10585047a92eb2fe98db4d806d9a6fe))
* added docs for run info status property for Case, ModelExecutable and Experiment entites ([08a12f8](https://github.com/modelon-community/impact-client-python/commit/08a12f855167fed4083bd61e61f4abbe59409b1f))
* added docs on preference order for token and api key ([c01a8d0](https://github.com/modelon-community/impact-client-python/commit/c01a8d057315b24935d754f06225c39b9091553a))
* added docstrings for status ([41c51d0](https://github.com/modelon-community/impact-client-python/commit/41c51d04f26c1bdf42470c9fe9d3948b4034d0ca))
* added keys() method to mypy ignore as maping expects KeysView object ([40de4a5](https://github.com/modelon-community/impact-client-python/commit/40de4a56397e89a18a5dc0aa45421c9e3cb8becc))
* added mapping for python client-MI version compatibility ([9bc476b](https://github.com/modelon-community/impact-client-python/commit/9bc476b623e8d3e6e0f8e9c6cad69ce90fcf7877))
* added method for FMU import from ProjectContent ([d058dfb](https://github.com/modelon-community/impact-client-python/commit/d058dfb348b00e40e7f9d2a6053c58d9e3add774))
* added support for new endpoints ([36a64f0](https://github.com/modelon-community/impact-client-python/commit/36a64f07e2c0cebec2a79473a70781b0024915f4))
* added support to fetch project options and refactored model entity to have project_id ([740c9fb](https://github.com/modelon-community/impact-client-python/commit/740c9fb906bc2f3e8d7973698cf0ef00f853e388))
* added tests ([334c129](https://github.com/modelon-community/impact-client-python/commit/334c129650946d3c94eb87128b2264e07671b67d))
* adding datetimestamps to run_info ([7084e27](https://github.com/modelon-community/impact-client-python/commit/7084e27729525aca67a0468ab2f48f87e15ca6e0))
* adding iterable as return type for get_contents to avoid mypy error in get_content_by_name ([dd03c9f](https://github.com/modelon-community/impact-client-python/commit/dd03c9ff22a124cb8403dd09faf5135fa3ea8362))
* assert compilation is successful before calling download FMU api ([cee8892](https://github.com/modelon-community/impact-client-python/commit/cee88921236bcba594075ef6a47f0210898d7c8c))
* bump supported api version range ([be2dced](https://github.com/modelon-community/impact-client-python/commit/be2dced5c2c4bdbcfe38db86f8111eb06212e0c3))
* bump supported version range ([e789a35](https://github.com/modelon-community/impact-client-python/commit/e789a35f316077890ee1446d1a67a0c9999907b5))
* catching general exception while checking for jupyter hub url ([9a9ae39](https://github.com/modelon-community/impact-client-python/commit/9a9ae39a58a9e09e10b6027bd230586aaea1da27))
* check if the user given URL is as substring of the IMPACT_URL value to validate if we connect to the same server as current notebook is running or not ([553f817](https://github.com/modelon-community/impact-client-python/commit/553f81795674af172820d5a8c0740a1d60918380))
* concatination of URLs handles starting slash on relative part ([464b162](https://github.com/modelon-community/impact-client-python/commit/464b1620cd98d3af4bac8bf7bdeb8c4a05ec8f29))
* consistent spelling use for parameterization --> parametrization ([bae4176](https://github.com/modelon-community/impact-client-python/commit/bae41769fe1f9880f9a30028d879595e3195bcdb))
* convert full import name to just class name ([3d7766d](https://github.com/modelon-community/impact-client-python/commit/3d7766df49f50e85cf4be2d89bf7f09bfdc064c5))
* corrected '.impact' to ~/.impact ([50a438e](https://github.com/modelon-community/impact-client-python/commit/50a438e137edf6bc64393e4319d6b86428a4669e))
* corrected spellings ([9de1f0d](https://github.com/modelon-community/impact-client-python/commit/9de1f0d98ca913eab19e02296ac285cfc2fd15b1))
* corrected the docs to upload modelica content to a project ([d4484ea](https://github.com/modelon-community/impact-client-python/commit/d4484ea1656b34f178022586f5648d4a67511397))
* corrected the documentation example for with_result_filter ([e150eb0](https://github.com/modelon-community/impact-client-python/commit/e150eb0054aec147512176e646e477eab89b9b9a))
* corrected the path in .releasesrc ([cebcc19](https://github.com/modelon-community/impact-client-python/commit/cebcc19d54fc936ee273faa58878f8ccc38bd468))
* corrected upload_model_library to import_modelica_library in docs ([256d813](https://github.com/modelon-community/impact-client-python/commit/256d8139acd35bd0c9cd408c4dae9fb84d87ce7c))
* default to https://impact.modelon.cloud/ if no url is provided by user or no environmental variable is set ([0e6593f](https://github.com/modelon-community/impact-client-python/commit/0e6593f878f79172ae5191dcc34b80844d3e5f4c))
* docformatter fixes ([9711ee7](https://github.com/modelon-community/impact-client-python/commit/9711ee7115f7d0f757a00d5e19924cbff20dc100))
* docs updates and docformatter suggested fixes ([6cbd165](https://github.com/modelon-community/impact-client-python/commit/6cbd165c31d974b05425148fee5861397d249fb9))
* docstring fixes to improve rendering ([f62e302](https://github.com/modelon-community/impact-client-python/commit/f62e302059dcd4f669337bf478b70807971d68ed))
* documentation improvements ([8edacaa](https://github.com/modelon-community/impact-client-python/commit/8edacaa7476f80ca07b20176bb415230da42a45d))
* ensure we capture all errors for external result upload ([6bf94ec](https://github.com/modelon-community/impact-client-python/commit/6bf94ec91ae833c4816284e8fbf123bff6ebc964))
* feedback fix ([95d04c0](https://github.com/modelon-community/impact-client-python/commit/95d04c025c4cb9407722ab51061b5783a5852068))
* feedback fixes ([3cd167a](https://github.com/modelon-community/impact-client-python/commit/3cd167a9860ae51f3199d4ebbf45d6a8fd15bb7c))
* feedback fixes ([7975ce0](https://github.com/modelon-community/impact-client-python/commit/7975ce02e63e188a6947e279d2407a216f075abc))
* fix sphinx warnings ([ebed6f3](https://github.com/modelon-community/impact-client-python/commit/ebed6f3ef6dd02e8b314534c47bde01f8712cb49))
* fixed docs for creating and fetching workspaces ([58a0d12](https://github.com/modelon-community/impact-client-python/commit/58a0d12a3cf91b4458ffab819829c9a86c93b86e))
* get project id from location for content import ([cf47fdc](https://github.com/modelon-community/impact-client-python/commit/cf47fdc2cf18c2287362c6791edd346e692c28ed))
* import fixes ([13c1dc2](https://github.com/modelon-community/impact-client-python/commit/13c1dc247a8a2dd042299cb6f5182450f89c0982))
* lint fixes ([1bbff57](https://github.com/modelon-community/impact-client-python/commit/1bbff575f180f43105965e8416886d279c2850a6))
* made _CaseRunInfo,_CaseAnalysis, _CaseMeta, _CaseInput and _ModelExecutableRunInfo classes public ([745a371](https://github.com/modelon-community/impact-client-python/commit/745a371a97859aa6c3aa1610cbf88f50cc8281dc))
* made code compliant with google doc style. Remove return value as sphinx automatically generated from type hints ([5049f2f](https://github.com/modelon-community/impact-client-python/commit/5049f2f87767f773f965fa4b1cbb6508f4a1f5f1))
* make ExternalResultMetaData, ExperimentMetaData and ExperimentRunInfo classes public ([b3aa10e](https://github.com/modelon-community/impact-client-python/commit/b3aa10eeb9866e98edb4eca2609c54a77c5c377a))
* minor docstring fixes for operations ([2caa979](https://github.com/modelon-community/impact-client-python/commit/2caa979d8ff8d2a59c5fb5a640eaf4679cc35769))
* minor fixes ([e3ca047](https://github.com/modelon-community/impact-client-python/commit/e3ca04786e8f65bee94f7de08123cafa2bece9f1))
* move docformatter and napolean to dev dependencies ([7248204](https://github.com/modelon-community/impact-client-python/commit/7248204c386be86fbf4ceab7c0e6e981a6360723))
* moved documentation for getter setter methods to the get methods as setter methods are not visible in docs ([050606c](https://github.com/modelon-community/impact-client-python/commit/050606c3cc5ed71b17ad5102d6989607ab251ded))
* moved fmu_import to model entity ([0bb9f27](https://github.com/modelon-community/impact-client-python/commit/0bb9f27eac97c060f9a7aaa0f76e3e1eca8ac60c))
* ops cannot be None ([88c65a4](https://github.com/modelon-community/impact-client-python/commit/88c65a470bc63a591ae5056442563dc73b8ce12e))
* partial resolution of circular imports ([81cbdd4](https://github.com/modelon-community/impact-client-python/commit/81cbdd410f669132fee5a53850186edbb5a7b805))
* pyright fixes ([c0b727f](https://github.com/modelon-community/impact-client-python/commit/c0b727f04b2c01f107d0bc3b558513edb7f169b3))
* refactored entities to use a single service class ([0719729](https://github.com/modelon-community/impact-client-python/commit/07197292db0c2aa023d21639fbd96039fac73ab5))
* refactored fixtures ([a08e154](https://github.com/modelon-community/impact-client-python/commit/a08e1546d04852205cadb4773f040653a2e5e7a0))
* refactored login workflow to distinguish if python client is run within or outside JH environment ([ed79bf2](https://github.com/modelon-community/impact-client-python/commit/ed79bf29ef8fc6c1c24c3f5cb848909988164e52))
* regenerated docs ([ce1ddd0](https://github.com/modelon-community/impact-client-python/commit/ce1ddd07338bf0950ad5b2add21aa0553d019c3c))
* remove linearize reference from choosing analysis type docs ([1fc62fc](https://github.com/modelon-community/impact-client-python/commit/1fc62fc15fbcfbbbb1e5b7e5fe9c87d314949286))
* remove options argument from export api ([9417ca6](https://github.com/modelon-community/impact-client-python/commit/9417ca6ceea1813efe7721e9e7253243f15818e9))
* removed clone() method from Worksace entity ([3041b5c](https://github.com/modelon-community/impact-client-python/commit/3041b5cc0829f5568b719fca3ba1abcb8025eed1))
* removed project ID from mock content import fixtures ([339e0d7](https://github.com/modelon-community/impact-client-python/commit/339e0d7ae54236f68897a38099ebab8804d917af))
* rename 'import_from_*' methods to import_workspace_from_* ([12afca2](https://github.com/modelon-community/impact-client-python/commit/12afca2ea9b7f4cc5527782a92f2775a9ba9c00d))
* rename Examples-> Example, adding return after Example to make code examples render correctly ([6b1155a](https://github.com/modelon-community/impact-client-python/commit/6b1155a71845f57f4687e047e277e013cb08913a))
* renamed intitialize_from to with_initialize_from in SimpleFMUExperimentDefinition, SimpleModelicaExperimentDefinition and SimpleExperimentExtension ([cf6b908](https://github.com/modelon-community/impact-client-python/commit/cf6b90887fe78e02db533d032657e7b7d4f249aa))
* renamed upload_content to import_content ([91e710a](https://github.com/modelon-community/impact-client-python/commit/91e710ac32c25eb69f11e2fa94354abd4386bb10))
* renamed upload_modelica_library to import_modelica_library ([19637cb](https://github.com/modelon-community/impact-client-python/commit/19637cb98cb6268574e92efcad9e90d749985dfa))
* replace '--' with ':' for arguments docstrings ([a7bb933](https://github.com/modelon-community/impact-client-python/commit/a7bb933b9c2cde863163493e8054ea57479b5844))
* set correct supported version range ([e7e2939](https://github.com/modelon-community/impact-client-python/commit/e7e2939297e44d81e4863f230ff6ce9d179e7fcd))
* specified slots for classes with setter methods ([3faf823](https://github.com/modelon-community/impact-client-python/commit/3faf823cb39719213982e8054d4f7c8321c7bfd7))
* spell fix - parameterization -> parametrization ([1f302cd](https://github.com/modelon-community/impact-client-python/commit/1f302cd5560b811a4b76aa1bfe933110cbfc43ea))
* spelling and formatting fixes ([aa97edd](https://github.com/modelon-community/impact-client-python/commit/aa97eddff8beb0b099a4ed19c0006ce1e985765a))
* the env_name parameter in CredentialManager class now takes a list instead of a string ([783e861](https://github.com/modelon-community/impact-client-python/commit/783e861932fc2d625bf0621cea4fe6940585b759))
* the filter option only accepts list of patterns ([9aa27d4](https://github.com/modelon-community/impact-client-python/commit/9aa27d445244a67257d759b71ae1aa47baf7e061))
* the Status method in Operations class is now a property ([cc8bfb1](https://github.com/modelon-community/impact-client-python/commit/cc8bfb1bc2ed789b01eb267f329667d6b1c6cd3a))
* type fix experiements -> experiments ([bee0dd2](https://github.com/modelon-community/impact-client-python/commit/bee0dd21371b61c85b46212e3fc9cb2352642538))
* typo fix ([1bcd33f](https://github.com/modelon-community/impact-client-python/commit/1bcd33fc627523c2648f6798f37c99c7cc92ef11))
* unified fetching import/export status for all entities ([f20773c](https://github.com/modelon-community/impact-client-python/commit/f20773c7fa831cd05c7eca2839e5ae15f12d0f8d))
* updated docs ([e948f95](https://github.com/modelon-community/impact-client-python/commit/e948f9567481d771bc0de89344eeb120b21ad742))
* updated install.rst ([33d877d](https://github.com/modelon-community/impact-client-python/commit/33d877d3f0933f8f7e2e1bd3f46f555bc3a31d62))
* updated the codebase to use new endpoint for workspace export ([b378fc0](https://github.com/modelon-community/impact-client-python/commit/b378fc0c37192b332f1d452732fadc703a7d9d49))
* updated the get_artifact method to return CustomArtifact class ([b406550](https://github.com/modelon-community/impact-client-python/commit/b4065507292db4787f3a41f5a8354e4eabe847e1))
* updated the metadata property in Experiment entity such that it always return an ExperimentMetaData ([aefe32c](https://github.com/modelon-community/impact-client-python/commit/aefe32c05aeb54dcf0d6d632840833f6d25c659d))
* updated the route for project options endpoint ([75f9a76](https://github.com/modelon-community/impact-client-python/commit/75f9a763d4f49fa6ee64e71f57eb8a3361dddded))
* updated workspace import api to use new routes ([7b34f5d](https://github.com/modelon-community/impact-client-python/commit/7b34f5d2c0256260c895960a9fdacbca062a8357))
* upload content with using latest API ([6531cf3](https://github.com/modelon-community/impact-client-python/commit/6531cf31be558512e4b12eee766e11c639b93469))
* use dict instead of converting to ProjectDefintion while creating Project instance ([57826de](https://github.com/modelon-community/impact-client-python/commit/57826de6990780cf9f1b1a223dfd379f4cc7d868))
* use helper class for dynamic cf ([92ce0e3](https://github.com/modelon-community/impact-client-python/commit/92ce0e3d026e6aa4dd7fe468155c1c86b3d5c156))
* use poetry for rtd build ([d233295](https://github.com/modelon-community/impact-client-python/commit/d23329547984e380fcc5d12dbd8e968c139e1daf))
* using args instead of parameters to folow google style docs ([aab983a](https://github.com/modelon-community/impact-client-python/commit/aab983a1d99417ddb0de65c88b17f5f8c7d39397))
* using callback protocol for creating entity from operation ([3e51aec](https://github.com/modelon-community/impact-client-python/commit/3e51aec71c235d7cc047d86de00993c4307cf9c8))


### Features

* add method to fetch all running executions ([72f1089](https://github.com/modelon-community/impact-client-python/commit/72f10890a3934a8ede1361077f83b2e140975ab9))
* add readthedocs-sphinx-search extension to allow users to search as they type ([b0f36b8](https://github.com/modelon-community/impact-client-python/commit/b0f36b86a2618e8136f015bcc3037f104f03af74))
* add support for fetching project content by id ([b4bbd9a](https://github.com/modelon-community/impact-client-python/commit/b4bbd9ac8fa6cc180fe989723c2aa7307b7bbc32))
* add support to fetch artifact ids ([27b255c](https://github.com/modelon-community/impact-client-python/commit/27b255c0ea4c00e04e0ce61e915bcf6aa9da8470))
* added a cached boolean to experiment._get_info() to allow fetching latest run_info and meta_data for an experiment ([48747b0](https://github.com/modelon-community/impact-client-python/commit/48747b091cc1349c9da7024769fdab433e264980))
* added a cached boolean to model_executable._get_info() to allow fetching latest run_info for an FMU ([a9b60fb](https://github.com/modelon-community/impact-client-python/commit/a9b60fbab18e99a499db026029aeaec104eec463))
* added a label property to experiment metadata class ([c45ca1a](https://github.com/modelon-community/impact-client-python/commit/c45ca1a4efcfed8d788baaaff7f053acd93cc15c))
* added possibility to allow fetching latest run_info for a case ([ddca239](https://github.com/modelon-community/impact-client-python/commit/ddca239d14b17857ba3abf024bab617cc8787637))
* added possibility to fetch model description xml ([4427a2f](https://github.com/modelon-community/impact-client-python/commit/4427a2f4ac39c85e77cd51fab952af04fc1b3a21))
* added possibility to fetch project size ([d793892](https://github.com/modelon-community/impact-client-python/commit/d7938922659822a36fbfe38fc45c2fe7f40bd3fd))
* added possibility to fetch workspace size ([66a8ed2](https://github.com/modelon-community/impact-client-python/commit/66a8ed24c1dfb8ae9950c39019658ac3e67196dd))
* added possibility to get custom_function, class name and options from experiment ([94274b5](https://github.com/modelon-community/impact-client-python/commit/94274b5ab4d74590a40e633eda6cceb0fd71412a))
* added possibility to get experiments for model ([351d860](https://github.com/modelon-community/impact-client-python/commit/351d8606539d2ad18618bbec5cbd1c35f05bd0cc))
* added possibility to set defaults for custom functions and specify variable filter as a list of strings ([493325a](https://github.com/modelon-community/impact-client-python/commit/493325a492ba98bddbc6b751e5f82a1cf0b742b7))
* added projectType filter for get projects ([0a4de76](https://github.com/modelon-community/impact-client-python/commit/0a4de76ff68777e1929212d67d284e29d6073394))
* added spell check for docs ([0a5e4a6](https://github.com/modelon-community/impact-client-python/commit/0a5e4a6d56a6b24f9a0da5b331f85375e6824fc4))
* added support for project import ([1f8828b](https://github.com/modelon-community/impact-client-python/commit/1f8828bc6281adcdcfc3e5e5f61b08929eef74f3))
* added support for workspace project and dependency import ([50e7214](https://github.com/modelon-community/impact-client-python/commit/50e7214707856c4f90fbc92a8d8b9323b4081ffc))
* added support to fetch only last point for a result trajectory ([ad144be](https://github.com/modelon-community/impact-client-python/commit/ad144be46f16d0241703875385b0075dc1621ff6))
* added support to import shared workspaces ([6223512](https://github.com/modelon-community/impact-client-python/commit/6223512e5ef76a753808e7beba90db67a643aebc))
* added test coverage ([5e989a4](https://github.com/modelon-community/impact-client-python/commit/5e989a4bb4fbec8f1bdf2ae4dba8b6d94d83d3f6))
* allow passing initialize_from in new_experiment_definition method in model entity ([8bb697c](https://github.com/modelon-community/impact-client-python/commit/8bb697c8a6092c02a10e9b26149d3732f77e9a54))
* method for converting a workspace to latest version ([3615f0c](https://github.com/modelon-community/impact-client-python/commit/3615f0cfe063c41f12856be1a68eaea02404498d))


### BREAKING CHANGES

* the status method in all operations class inheriting BaseOperation class is now a property
* initialize_from method in SimpleExperimentExtension, SimpleFMUExperimentDefinition and SimpleModelicaExperimentDefinition are now renamed to with_initialize_from
* clone method in Workpace entity has been removed
* the options argument is removed from the download method in workspace entity
* env_names parameter of CredentialManager class now takes a list
* the case.get_artifact method now returns a CustomArtifact class
* any API version less than 4.0.0 is not supported
* the upload_fmu method has been replaced
* the upload_model_library method has been replaced

# [3.0.0-dev.53](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.52...v3.0.0-dev.53) (2023-06-08)


### Bug Fixes

* added docs for run info status property for Case, ModelExecutable and Experiment entites ([08a12f8](https://github.com/modelon-community/impact-client-python/commit/08a12f855167fed4083bd61e61f4abbe59409b1f))
* added docstrings for status ([41c51d0](https://github.com/modelon-community/impact-client-python/commit/41c51d04f26c1bdf42470c9fe9d3948b4034d0ca))


### Features

* added support to fetch only last point for a result trajectory ([ad144be](https://github.com/modelon-community/impact-client-python/commit/ad144be46f16d0241703875385b0075dc1621ff6))

# [3.0.0-dev.52](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.51...v3.0.0-dev.52) (2023-06-07)


### Bug Fixes

* added docs for expansion alorithms ([66ea11e](https://github.com/modelon-community/impact-client-python/commit/66ea11e110ea82720f7a6bbb82b92aa1822c7d36))

# [3.0.0-dev.51](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.50...v3.0.0-dev.51) (2023-06-07)


### Bug Fixes

* added docs for initialize_from in case entity ([fe42407](https://github.com/modelon-community/impact-client-python/commit/fe424072a10585047a92eb2fe98db4d806d9a6fe))
* moved documentation for getter setter methods to the get methods as setter methods are not visible in docs ([050606c](https://github.com/modelon-community/impact-client-python/commit/050606c3cc5ed71b17ad5102d6989607ab251ded))


### Features

* added a cached boolean to experiment._get_info() to allow fetching latest run_info and meta_data for an experiment ([48747b0](https://github.com/modelon-community/impact-client-python/commit/48747b091cc1349c9da7024769fdab433e264980))
* added a cached boolean to model_executable._get_info() to allow fetching latest run_info for an FMU ([a9b60fb](https://github.com/modelon-community/impact-client-python/commit/a9b60fbab18e99a499db026029aeaec104eec463))
* added possibility to allow fetching latest run_info for a case ([ddca239](https://github.com/modelon-community/impact-client-python/commit/ddca239d14b17857ba3abf024bab617cc8787637))

# [3.0.0-dev.50](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.49...v3.0.0-dev.50) (2023-06-07)


### Bug Fixes

* docstring fixes to improve rendering ([f62e302](https://github.com/modelon-community/impact-client-python/commit/f62e302059dcd4f669337bf478b70807971d68ed))

# [3.0.0-dev.49](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.48...v3.0.0-dev.49) (2023-06-07)


### Bug Fixes

* the Status method in Operations class is now a property ([cc8bfb1](https://github.com/modelon-community/impact-client-python/commit/cc8bfb1bc2ed789b01eb267f329667d6b1c6cd3a))


### BREAKING CHANGES

* the status method in all operations class inheriting BaseOperation class is now a property

# [3.0.0-dev.48](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.47...v3.0.0-dev.48) (2023-06-04)


### Bug Fixes

* added tests ([334c129](https://github.com/modelon-community/impact-client-python/commit/334c129650946d3c94eb87128b2264e07671b67d))
* docs updates and docformatter suggested fixes ([6cbd165](https://github.com/modelon-community/impact-client-python/commit/6cbd165c31d974b05425148fee5861397d249fb9))


### Features

* add method to fetch all running executions ([72f1089](https://github.com/modelon-community/impact-client-python/commit/72f10890a3934a8ede1361077f83b2e140975ab9))

# [3.0.0-dev.47](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.46...v3.0.0-dev.47) (2023-06-04)


### Bug Fixes

* corrected upload_model_library to import_modelica_library in docs ([256d813](https://github.com/modelon-community/impact-client-python/commit/256d8139acd35bd0c9cd408c4dae9fb84d87ce7c))


### Features

* added possibility to fetch model description xml ([4427a2f](https://github.com/modelon-community/impact-client-python/commit/4427a2f4ac39c85e77cd51fab952af04fc1b3a21))

# [3.0.0-dev.46](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.45...v3.0.0-dev.46) (2023-05-29)


### Bug Fixes

* spell fix - parameterization -> parametrization ([1f302cd](https://github.com/modelon-community/impact-client-python/commit/1f302cd5560b811a4b76aa1bfe933110cbfc43ea))

# [3.0.0-dev.45](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.44...v3.0.0-dev.45) (2023-05-29)


### Bug Fixes

* corrected the documentation example for with_result_filter ([e150eb0](https://github.com/modelon-community/impact-client-python/commit/e150eb0054aec147512176e646e477eab89b9b9a))

# [3.0.0-dev.44](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.43...v3.0.0-dev.44) (2023-05-28)


### Bug Fixes

* added mapping for python client-MI version compatibility ([9bc476b](https://github.com/modelon-community/impact-client-python/commit/9bc476b623e8d3e6e0f8e9c6cad69ce90fcf7877))

# [3.0.0-dev.43](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.42...v3.0.0-dev.43) (2023-05-25)


### Bug Fixes

* added additional checks and improved error message ([e7a9b25](https://github.com/modelon-community/impact-client-python/commit/e7a9b25d001ab48459abca0a0e5f2a22a8065e5d))
* the filter option only accepts list of patterns ([9aa27d4](https://github.com/modelon-community/impact-client-python/commit/9aa27d445244a67257d759b71ae1aa47baf7e061))

# [3.0.0-dev.42](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.41...v3.0.0-dev.42) (2023-05-25)


### Bug Fixes

* bump supported version range ([e789a35](https://github.com/modelon-community/impact-client-python/commit/e789a35f316077890ee1446d1a67a0c9999907b5))

# [3.0.0-dev.41](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.40...v3.0.0-dev.41) (2023-05-24)


### Bug Fixes

* documentation improvements ([8edacaa](https://github.com/modelon-community/impact-client-python/commit/8edacaa7476f80ca07b20176bb415230da42a45d))

# [3.0.0-dev.40](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.39...v3.0.0-dev.40) (2023-05-15)


### Bug Fixes

* made _CaseRunInfo,_CaseAnalysis, _CaseMeta, _CaseInput and _ModelExecutableRunInfo classes public ([745a371](https://github.com/modelon-community/impact-client-python/commit/745a371a97859aa6c3aa1610cbf88f50cc8281dc))

# [3.0.0-dev.39](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.38...v3.0.0-dev.39) (2023-05-09)


### Bug Fixes

* added docs on preference order for token and api key ([c01a8d0](https://github.com/modelon-community/impact-client-python/commit/c01a8d057315b24935d754f06225c39b9091553a))
* corrected '.impact' to ~/.impact ([50a438e](https://github.com/modelon-community/impact-client-python/commit/50a438e137edf6bc64393e4319d6b86428a4669e))
* corrected the docs to upload modelica content to a project ([d4484ea](https://github.com/modelon-community/impact-client-python/commit/d4484ea1656b34f178022586f5648d4a67511397))
* feedback fixes ([3cd167a](https://github.com/modelon-community/impact-client-python/commit/3cd167a9860ae51f3199d4ebbf45d6a8fd15bb7c))
* remove linearize reference from choosing analysis type docs ([1fc62fc](https://github.com/modelon-community/impact-client-python/commit/1fc62fc15fbcfbbbb1e5b7e5fe9c87d314949286))
* typo fix ([1bcd33f](https://github.com/modelon-community/impact-client-python/commit/1bcd33fc627523c2648f6798f37c99c7cc92ef11))

# [3.0.0-dev.38](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.37...v3.0.0-dev.38) (2023-05-08)


### Bug Fixes

* minor docstring fixes for operations ([2caa979](https://github.com/modelon-community/impact-client-python/commit/2caa979d8ff8d2a59c5fb5a640eaf4679cc35769))
* moved fmu_import to model entity ([0bb9f27](https://github.com/modelon-community/impact-client-python/commit/0bb9f27eac97c060f9a7aaa0f76e3e1eca8ac60c))

# [3.0.0-dev.37](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.36...v3.0.0-dev.37) (2023-05-04)


### Bug Fixes

* renamed upload_content to import_content ([91e710a](https://github.com/modelon-community/impact-client-python/commit/91e710ac32c25eb69f11e2fa94354abd4386bb10))
* renamed upload_modelica_library to import_modelica_library ([19637cb](https://github.com/modelon-community/impact-client-python/commit/19637cb98cb6268574e92efcad9e90d749985dfa))

# [3.0.0-dev.36](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.35...v3.0.0-dev.36) (2023-05-02)


### Bug Fixes

* added an abstract interface class for entities ([1885d4b](https://github.com/modelon-community/impact-client-python/commit/1885d4b2998466362e9cf66e9a8d74f493fd14d2))
* updated docs ([e948f95](https://github.com/modelon-community/impact-client-python/commit/e948f9567481d771bc0de89344eeb120b21ad742))

# [3.0.0-dev.35](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.34...v3.0.0-dev.35) (2023-04-28)


### Bug Fixes

* default to https://impact.modelon.cloud/ if no url is provided by user or no environmental variable is set ([0e6593f](https://github.com/modelon-community/impact-client-python/commit/0e6593f878f79172ae5191dcc34b80844d3e5f4c))

# [3.0.0-dev.34](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.33...v3.0.0-dev.34) (2023-04-28)


### Bug Fixes

* check if the user given URL is as substring of the IMPACT_URL value to validate if we connect to the same server as current notebook is running or not ([553f817](https://github.com/modelon-community/impact-client-python/commit/553f81795674af172820d5a8c0740a1d60918380))

# [3.0.0-dev.33](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.32...v3.0.0-dev.33) (2023-04-27)


### Bug Fixes

* added docs for ExperimentRunInfo class ([9a79f3f](https://github.com/modelon-community/impact-client-python/commit/9a79f3f902ec5542c0fa8dde55a8eb08cc2cfdfc))
* make ExternalResultMetaData, ExperimentMetaData and ExperimentRunInfo classes public ([b3aa10e](https://github.com/modelon-community/impact-client-python/commit/b3aa10eeb9866e98edb4eca2609c54a77c5c377a))
* updated the metadata property in Experiment entity such that it always return an ExperimentMetaData ([aefe32c](https://github.com/modelon-community/impact-client-python/commit/aefe32c05aeb54dcf0d6d632840833f6d25c659d))


### Features

* added a label property to experiment metadata class ([c45ca1a](https://github.com/modelon-community/impact-client-python/commit/c45ca1a4efcfed8d788baaaff7f053acd93cc15c))

# [3.0.0-dev.32](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.31...v3.0.0-dev.32) (2023-04-27)


### Features

* add support for fetching project content by id ([b4bbd9a](https://github.com/modelon-community/impact-client-python/commit/b4bbd9ac8fa6cc180fe989723c2aa7307b7bbc32))
* added possibility to fetch project size ([d793892](https://github.com/modelon-community/impact-client-python/commit/d7938922659822a36fbfe38fc45c2fe7f40bd3fd))
* added possibility to fetch workspace size ([66a8ed2](https://github.com/modelon-community/impact-client-python/commit/66a8ed24c1dfb8ae9950c39019658ac3e67196dd))
* added projectType filter for get projects ([0a4de76](https://github.com/modelon-community/impact-client-python/commit/0a4de76ff68777e1929212d67d284e29d6073394))

# [3.0.0-dev.31](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.30...v3.0.0-dev.31) (2023-04-27)


### Features

* added possibility to get custom_function, class name and options from experiment ([94274b5](https://github.com/modelon-community/impact-client-python/commit/94274b5ab4d74590a40e633eda6cceb0fd71412a))

# [3.0.0-dev.30](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.29...v3.0.0-dev.30) (2023-04-25)


### Features

* added possibility to get experiments for model ([351d860](https://github.com/modelon-community/impact-client-python/commit/351d8606539d2ad18618bbec5cbd1c35f05bd0cc))

# [3.0.0-dev.29](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.28...v3.0.0-dev.29) (2023-04-18)


### Bug Fixes

* renamed intitialize_from to with_initialize_from in SimpleFMUExperimentDefinition, SimpleModelicaExperimentDefinition and SimpleExperimentExtension ([cf6b908](https://github.com/modelon-community/impact-client-python/commit/cf6b90887fe78e02db533d032657e7b7d4f249aa))


### Features

* allow passing initialize_from in new_experiment_definition method in model entity ([8bb697c](https://github.com/modelon-community/impact-client-python/commit/8bb697c8a6092c02a10e9b26149d3732f77e9a54))


### BREAKING CHANGES

* initialize_from method in SimpleExperimentExtension, SimpleFMUExperimentDefinition and SimpleModelicaExperimentDefinition are now renamed to with_initialize_from

# [3.0.0-dev.28](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.27...v3.0.0-dev.28) (2023-04-17)


### Bug Fixes

* get project id from location for content import ([cf47fdc](https://github.com/modelon-community/impact-client-python/commit/cf47fdc2cf18c2287362c6791edd346e692c28ed))
* removed project ID from mock content import fixtures ([339e0d7](https://github.com/modelon-community/impact-client-python/commit/339e0d7ae54236f68897a38099ebab8804d917af))

# [3.0.0-dev.27](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.26...v3.0.0-dev.27) (2023-04-13)


### Bug Fixes

* removed clone() method from Worksace entity ([3041b5c](https://github.com/modelon-community/impact-client-python/commit/3041b5cc0829f5568b719fca3ba1abcb8025eed1))


### BREAKING CHANGES

* clone method in Workpace entity has been removed

# [3.0.0-dev.26](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.25...v3.0.0-dev.26) (2023-04-11)


### Bug Fixes

* add py.typed marker ([8761cc1](https://github.com/modelon-community/impact-client-python/commit/8761cc1699c490d488707e0f27202693bc35778f))

# [3.0.0-dev.25](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.24...v3.0.0-dev.25) (2023-04-06)


### Bug Fixes

* added an extension to auto-generate type hints ([1d7b8d6](https://github.com/modelon-community/impact-client-python/commit/1d7b8d60d135e5a629b647a462882eb44c229991))
* convert full import name to just class name ([3d7766d](https://github.com/modelon-community/impact-client-python/commit/3d7766df49f50e85cf4be2d89bf7f09bfdc064c5))
* fixed docs for creating and fetching workspaces ([58a0d12](https://github.com/modelon-community/impact-client-python/commit/58a0d12a3cf91b4458ffab819829c9a86c93b86e))
* lint fixes ([1bbff57](https://github.com/modelon-community/impact-client-python/commit/1bbff575f180f43105965e8416886d279c2850a6))
* made code compliant with google doc style. Remove return value as sphinx automatically generated from type hints ([5049f2f](https://github.com/modelon-community/impact-client-python/commit/5049f2f87767f773f965fa4b1cbb6508f4a1f5f1))
* rename Examples-> Example, adding return after Example to make code examples render correctly ([6b1155a](https://github.com/modelon-community/impact-client-python/commit/6b1155a71845f57f4687e047e277e013cb08913a))
* spelling and formatting fixes ([aa97edd](https://github.com/modelon-community/impact-client-python/commit/aa97eddff8beb0b099a4ed19c0006ce1e985765a))

# [3.0.0-dev.24](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.23...v3.0.0-dev.24) (2023-04-06)


### Bug Fixes

* catching general exception while checking for jupyter hub url ([9a9ae39](https://github.com/modelon-community/impact-client-python/commit/9a9ae39a58a9e09e10b6027bd230586aaea1da27))

# [3.0.0-dev.23](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.22...v3.0.0-dev.23) (2023-04-06)


### Bug Fixes

* remove options argument from export api ([9417ca6](https://github.com/modelon-community/impact-client-python/commit/9417ca6ceea1813efe7721e9e7253243f15818e9))


### BREAKING CHANGES

* the options argument is removed from the download method in workspace entity

# [3.0.0-dev.22](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.21...v3.0.0-dev.22) (2023-04-05)


### Bug Fixes

* docformatter fixes ([9711ee7](https://github.com/modelon-community/impact-client-python/commit/9711ee7115f7d0f757a00d5e19924cbff20dc100))
* partial resolution of circular imports ([81cbdd4](https://github.com/modelon-community/impact-client-python/commit/81cbdd410f669132fee5a53850186edbb5a7b805))
* use dict instead of converting to ProjectDefintion while creating Project instance ([57826de](https://github.com/modelon-community/impact-client-python/commit/57826de6990780cf9f1b1a223dfd379f4cc7d868))
* using callback protocol for creating entity from operation ([3e51aec](https://github.com/modelon-community/impact-client-python/commit/3e51aec71c235d7cc047d86de00993c4307cf9c8))

# [3.0.0-dev.21](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.20...v3.0.0-dev.21) (2023-04-04)


### Bug Fixes

* refactored login workflow to distinguish if python client is run within or outside JH environment ([ed79bf2](https://github.com/modelon-community/impact-client-python/commit/ed79bf29ef8fc6c1c24c3f5cb848909988164e52))

# [3.0.0-dev.20](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.19...v3.0.0-dev.20) (2023-03-29)


### Bug Fixes

* corrected the path in .releasesrc ([cebcc19](https://github.com/modelon-community/impact-client-python/commit/cebcc19d54fc936ee273faa58878f8ccc38bd468))

# [3.0.0-dev.19](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.18...v3.0.0-dev.19) (2023-03-29)


### Bug Fixes

* use poetry for rtd build ([d233295](https://github.com/modelon-community/impact-client-python/commit/d23329547984e380fcc5d12dbd8e968c139e1daf))


### Features

* add readthedocs-sphinx-search extension to allow users to search as they type ([b0f36b8](https://github.com/modelon-community/impact-client-python/commit/b0f36b86a2618e8136f015bcc3037f104f03af74))

# [3.0.0-dev.18](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.17...v3.0.0-dev.18) (2023-03-28)


### Bug Fixes

* add missing type hints ([03dc33b](https://github.com/modelon-community/impact-client-python/commit/03dc33b5a187439210b73ebe3bd813ae17dd0ef3))
* added keys() method to mypy ignore as maping expects KeysView object ([40de4a5](https://github.com/modelon-community/impact-client-python/commit/40de4a56397e89a18a5dc0aa45421c9e3cb8becc))
* adding iterable as return type for get_contents to avoid mypy error in get_content_by_name ([dd03c9f](https://github.com/modelon-community/impact-client-python/commit/dd03c9ff22a124cb8403dd09faf5135fa3ea8362))
* pyright fixes ([c0b727f](https://github.com/modelon-community/impact-client-python/commit/c0b727f04b2c01f107d0bc3b558513edb7f169b3))

# [3.0.0-dev.17](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.16...v3.0.0-dev.17) (2023-03-28)


### Bug Fixes

* the env_name parameter in CredentialManager class now takes a list instead of a string ([783e861](https://github.com/modelon-community/impact-client-python/commit/783e861932fc2d625bf0621cea4fe6940585b759))
* updated install.rst ([33d877d](https://github.com/modelon-community/impact-client-python/commit/33d877d3f0933f8f7e2e1bd3f46f555bc3a31d62))


### BREAKING CHANGES

* env_names parameter of CredentialManager class now takes a list

# [3.0.0-dev.16](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.15...v3.0.0-dev.16) (2023-03-27)


### Features

* added hint with URL for where to generate key/token for authentication ([7dfdb98](https://github.com/modelon-community/impact-client-python/commit/7dfdb982a7d056caaf867388f940ddad243820fe))

# [3.0.0-dev.15](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.14...v3.0.0-dev.15) (2023-03-27)


### Bug Fixes

* corrected spellings ([9de1f0d](https://github.com/modelon-community/impact-client-python/commit/9de1f0d98ca913eab19e02296ac285cfc2fd15b1))
* fix sphinx warnings ([ebed6f3](https://github.com/modelon-community/impact-client-python/commit/ebed6f3ef6dd02e8b314534c47bde01f8712cb49))
* move docformatter and napolean to dev dependencies ([7248204](https://github.com/modelon-community/impact-client-python/commit/7248204c386be86fbf4ceab7c0e6e981a6360723))
* replace '--' with ':' for arguments docstrings ([a7bb933](https://github.com/modelon-community/impact-client-python/commit/a7bb933b9c2cde863163493e8054ea57479b5844))
* using args instead of parameters to folow google style docs ([aab983a](https://github.com/modelon-community/impact-client-python/commit/aab983a1d99417ddb0de65c88b17f5f8c7d39397))


### Features

* added spell check for docs ([0a5e4a6](https://github.com/modelon-community/impact-client-python/commit/0a5e4a6d56a6b24f9a0da5b331f85375e6824fc4))

# [3.0.0-dev.14](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.13...v3.0.0-dev.14) (2023-03-23)


### Bug Fixes

* regenerated docs ([ce1ddd0](https://github.com/modelon-community/impact-client-python/commit/ce1ddd07338bf0950ad5b2add21aa0553d019c3c))

# [3.0.0-dev.13](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.12...v3.0.0-dev.13) (2023-03-14)


### Bug Fixes

* consistent spelling use for parameterization --> parametrization ([bae4176](https://github.com/modelon-community/impact-client-python/commit/bae41769fe1f9880f9a30028d879595e3195bcdb))
* specified slots for classes with setter methods ([3faf823](https://github.com/modelon-community/impact-client-python/commit/3faf823cb39719213982e8054d4f7c8321c7bfd7))

# [3.0.0-dev.12](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.11...v3.0.0-dev.12) (2023-03-14)


### Bug Fixes

* updated the get_artifact method to return CustomArtifact class ([b406550](https://github.com/modelon-community/impact-client-python/commit/b4065507292db4787f3a41f5a8354e4eabe847e1))


### Features

* add support to fetch artifact ids ([27b255c](https://github.com/modelon-community/impact-client-python/commit/27b255c0ea4c00e04e0ce61e915bcf6aa9da8470))


### BREAKING CHANGES

* the case.get_artifact method now returns a CustomArtifact class

# [3.0.0-dev.11](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.10...v3.0.0-dev.11) (2023-03-01)


### Bug Fixes

* feedback fix ([95d04c0](https://github.com/modelon-community/impact-client-python/commit/95d04c025c4cb9407722ab51061b5783a5852068))
* rename 'import_from_*' methods to import_workspace_from_* ([12afca2](https://github.com/modelon-community/impact-client-python/commit/12afca2ea9b7f4cc5527782a92f2775a9ba9c00d))
* unified fetching import/export status for all entities ([f20773c](https://github.com/modelon-community/impact-client-python/commit/f20773c7fa831cd05c7eca2839e5ae15f12d0f8d))
* updated workspace import api to use new routes ([7b34f5d](https://github.com/modelon-community/impact-client-python/commit/7b34f5d2c0256260c895960a9fdacbca062a8357))


### Features

* added support for project import ([1f8828b](https://github.com/modelon-community/impact-client-python/commit/1f8828bc6281adcdcfc3e5e5f61b08929eef74f3))
* added support for workspace project and dependency import ([50e7214](https://github.com/modelon-community/impact-client-python/commit/50e7214707856c4f90fbc92a8d8b9323b4081ffc))

# [3.0.0-dev.10](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.9...v3.0.0-dev.10) (2023-03-01)


### Bug Fixes

* updated the route for project options endpoint ([75f9a76](https://github.com/modelon-community/impact-client-python/commit/75f9a763d4f49fa6ee64e71f57eb8a3361dddded))
* use helper class for dynamic cf ([92ce0e3](https://github.com/modelon-community/impact-client-python/commit/92ce0e3d026e6aa4dd7fe468155c1c86b3d5c156))

# [3.0.0-dev.9](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.8...v3.0.0-dev.9) (2023-01-24)


### Bug Fixes

* assert compilation is successful before calling download FMU api ([cee8892](https://github.com/modelon-community/impact-client-python/commit/cee88921236bcba594075ef6a47f0210898d7c8c))

# [2.4.0](https://github.com/modelon-community/impact-client-python/compare/v2.3.0...v2.4.0) (2023-01-11)


### Features

* added hint with URL for where to generate key/token for authentication ([7dfdb98](https://github.com/modelon-community/impact-client-python/commit/7dfdb982a7d056caaf867388f940ddad243820fe))

# [3.0.0-dev.8](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.7...v3.0.0-dev.8) (2022-12-21)


### Bug Fixes

* ensure we capture all errors for external result upload ([6bf94ec](https://github.com/modelon-community/impact-client-python/commit/6bf94ec91ae833c4816284e8fbf123bff6ebc964))

# [3.0.0-dev.7](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.6...v3.0.0-dev.7) (2022-12-21)


### Features

* method for converting a workspace to latest version ([3615f0c](https://github.com/modelon-community/impact-client-python/commit/3615f0cfe063c41f12856be1a68eaea02404498d))

# [3.0.0-dev.6](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.5...v3.0.0-dev.6) (2022-12-19)


### Bug Fixes

* bump sphinx version ([fd239dc](https://github.com/modelon-community/impact-client-python/commit/fd239dce877b62d4bd936f7968496b639e8efc19))
* bump version of dependencies, locked spinx to 4.0.0 to have a importlib-metadata version lower than 5.1.0(https://stackoverflow.com/questions/73929564/entrypoints-object-has-no-attribute-get-digital-ocean) ([0b9c949](https://github.com/modelon-community/impact-client-python/commit/0b9c949b29efce4c63fdfa54069eed01a532c977))
* corrected minor typo fix in the docs ([8031e97](https://github.com/modelon-community/impact-client-python/commit/8031e977652bd42790b317c61bbeb7b5ac6f8c32))
* formatting fixes ([8180c19](https://github.com/modelon-community/impact-client-python/commit/8180c19dea356493ba319020094ee34b91f3f95d))
* generated docs for mixing modules ([55b8f4b](https://github.com/modelon-community/impact-client-python/commit/55b8f4be7115b20d4f3437dc6f3ac2e60560ada1))


### Features

* added make command to generate docs ([aae8efd](https://github.com/modelon-community/impact-client-python/commit/aae8efda046e08d05047e68955236a426d075156))

# [3.0.0-dev.5](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.4...v3.0.0-dev.5) (2022-12-18)


### Bug Fixes

* bump supported api version range ([be2dced](https://github.com/modelon-community/impact-client-python/commit/be2dced5c2c4bdbcfe38db86f8111eb06212e0c3))
* feedback fixes ([7975ce0](https://github.com/modelon-community/impact-client-python/commit/7975ce02e63e188a6947e279d2407a216f075abc))
* ops cannot be None ([88c65a4](https://github.com/modelon-community/impact-client-python/commit/88c65a470bc63a591ae5056442563dc73b8ce12e))
* updated the codebase to use new endpoint for workspace export ([b378fc0](https://github.com/modelon-community/impact-client-python/commit/b378fc0c37192b332f1d452732fadc703a7d9d49))

# [2.3.0](https://github.com/modelon-community/impact-client-python/compare/v2.2.3...v2.3.0) (2022-12-14)


### Bug Fixes

* bump sphinx version ([fd239dc](https://github.com/modelon-community/impact-client-python/commit/fd239dce877b62d4bd936f7968496b639e8efc19))
* bump version of dependencies, locked spinx to 4.0.0 to have a importlib-metadata version lower than 5.1.0(https://stackoverflow.com/questions/73929564/entrypoints-object-has-no-attribute-get-digital-ocean) ([0b9c949](https://github.com/modelon-community/impact-client-python/commit/0b9c949b29efce4c63fdfa54069eed01a532c977))
* formatting fixes ([8180c19](https://github.com/modelon-community/impact-client-python/commit/8180c19dea356493ba319020094ee34b91f3f95d))
* generated docs for mixing modules ([55b8f4b](https://github.com/modelon-community/impact-client-python/commit/55b8f4be7115b20d4f3437dc6f3ac2e60560ada1))


### Features

* added make command to generate docs ([aae8efd](https://github.com/modelon-community/impact-client-python/commit/aae8efda046e08d05047e68955236a426d075156))

## [2.2.3](https://github.com/modelon-community/impact-client-python/compare/v2.2.2...v2.2.3) (2022-12-02)


### Bug Fixes

* corrected minor typo fix in the docs ([8031e97](https://github.com/modelon-community/impact-client-python/commit/8031e977652bd42790b317c61bbeb7b5ac6f8c32))

# [3.0.0-dev.4](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.3...v3.0.0-dev.4) (2022-10-18)


### Bug Fixes

* concatination of URLs handles starting slash on relative part ([464b162](https://github.com/modelon-community/impact-client-python/commit/464b1620cd98d3af4bac8bf7bdeb8c4a05ec8f29))

# [3.0.0-dev.3](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.2...v3.0.0-dev.3) (2022-09-26)


### Bug Fixes

* refactored fixtures ([a08e154](https://github.com/modelon-community/impact-client-python/commit/a08e1546d04852205cadb4773f040653a2e5e7a0))

# [3.0.0-dev.2](https://github.com/modelon-community/impact-client-python/compare/v3.0.0-dev.1...v3.0.0-dev.2) (2022-09-26)


### Bug Fixes

* added convinience methods and arguments for fetching projects ([110035d](https://github.com/modelon-community/impact-client-python/commit/110035dbce62e00297b58986cbf675b7681f4e8d))

# [3.0.0-dev.1](https://github.com/modelon-community/impact-client-python/compare/v2.3.0-dev.5...v3.0.0-dev.1) (2022-09-16)


### Bug Fixes

* set correct supported version range ([e7e2939](https://github.com/modelon-community/impact-client-python/commit/e7e2939297e44d81e4863f230ff6ce9d179e7fcd))
* upload content with using latest API ([6531cf3](https://github.com/modelon-community/impact-client-python/commit/6531cf31be558512e4b12eee766e11c639b93469))


### BREAKING CHANGES

* any API version less than 4.0.0 is not supported
* the upload_fmu method has been replaced
* the upload_model_library method has been replaced

# [2.3.0-dev.5](https://github.com/modelon-community/impact-client-python/compare/v2.3.0-dev.4...v2.3.0-dev.5) (2022-09-16)


### Features

* added test coverage ([5e989a4](https://github.com/modelon-community/impact-client-python/commit/5e989a4bb4fbec8f1bdf2ae4dba8b6d94d83d3f6))

# [2.3.0-dev.4](https://github.com/modelon-community/impact-client-python/compare/v2.3.0-dev.3...v2.3.0-dev.4) (2022-09-14)


### Bug Fixes

* added method for FMU import from ProjectContent ([d058dfb](https://github.com/modelon-community/impact-client-python/commit/d058dfb348b00e40e7f9d2a6053c58d9e3add774))
* added support to fetch project options and refactored model entity to have project_id ([740c9fb](https://github.com/modelon-community/impact-client-python/commit/740c9fb906bc2f3e8d7973698cf0ef00f853e388))
* adding datetimestamps to run_info ([7084e27](https://github.com/modelon-community/impact-client-python/commit/7084e27729525aca67a0468ab2f48f87e15ca6e0))
* import fixes ([13c1dc2](https://github.com/modelon-community/impact-client-python/commit/13c1dc247a8a2dd042299cb6f5182450f89c0982))
* minor fixes ([e3ca047](https://github.com/modelon-community/impact-client-python/commit/e3ca04786e8f65bee94f7de08123cafa2bece9f1))
* refactored entities to use a single service class ([0719729](https://github.com/modelon-community/impact-client-python/commit/07197292db0c2aa023d21639fbd96039fac73ab5))

# [2.3.0-dev.3](https://github.com/modelon-community/impact-client-python/compare/v2.3.0-dev.2...v2.3.0-dev.3) (2022-09-06)


### Features

* added support to import shared workspaces ([6223512](https://github.com/modelon-community/impact-client-python/commit/6223512e5ef76a753808e7beba90db67a643aebc))

# [2.3.0-dev.2](https://github.com/modelon-community/impact-client-python/compare/v2.3.0-dev.1...v2.3.0-dev.2) (2022-09-01)


### Bug Fixes

* added support for new endpoints ([36a64f0](https://github.com/modelon-community/impact-client-python/commit/36a64f07e2c0cebec2a79473a70781b0024915f4))

# [2.3.0-dev.1](https://github.com/modelon-community/impact-client-python/compare/v2.2.2...v2.3.0-dev.1) (2022-08-29)


### Features

* added possibility to set defaults for custom functions and specify variable filter as a list of strings ([493325a](https://github.com/modelon-community/impact-client-python/commit/493325a492ba98bddbc6b751e5f82a1cf0b742b7))

## [2.2.2](https://github.com/modelon-community/impact-client-python/compare/v2.2.1...v2.2.2) (2022-06-13)


### Bug Fixes

* compability for accessing status enums for users ([4b377e8](https://github.com/modelon-community/impact-client-python/commit/4b377e82b29faab98d7d9f04614416f4949ca7fa))

## [2.2.1](https://github.com/modelon-community/impact-client-python/compare/v2.2.0...v2.2.1) (2022-06-09)


### Bug Fixes

* added types-requests package as a dependency ([b165fed](https://github.com/modelon-community/impact-client-python/commit/b165feda8c1b20ea415cef72bf39214175343fd8))
* update python dependencies ([e4ae2d4](https://github.com/modelon-community/impact-client-python/commit/e4ae2d434de0fd458dcabcf4c1d7a6797b68cdd3))

# [2.2.0](https://github.com/modelon-community/impact-client-python/compare/v2.1.0...v2.2.0) (2022-06-08)


### Bug Fixes

* breakout entities ([861b287](https://github.com/modelon-community/impact-client-python/commit/861b287da57e363eb8fd9974f04a49409defc630))
* refactored operator into a seperate model and updated to use dataclass ([4df0d30](https://github.com/modelon-community/impact-client-python/commit/4df0d302756dce61df5058bb420745969b237e48))
* refactored service class ([001b10b](https://github.com/modelon-community/impact-client-python/commit/001b10bb3dbc6099f7708edf865f60fe8073cc3d))
* updated python dependency ([fa4fe95](https://github.com/modelon-community/impact-client-python/commit/fa4fe9502f613caa18e7b033f66ae4b5c2d05608))


### Features

* added support for expansion algorithms ([17c0259](https://github.com/modelon-community/impact-client-python/commit/17c0259931c2cfdffec1cdda792afe13e03d48b4))

# [2.2.0-beta.2](https://github.com/modelon-community/impact-client-python/compare/v2.2.0-beta.1...v2.2.0-beta.2) (2022-06-02)


### Bug Fixes

* breakout entities ([1340401](https://github.com/modelon-community/impact-client-python/commit/13404017c7e37be542d8e3b37fe2ab203e423a2c))
* refactored service class ([74658cf](https://github.com/modelon-community/impact-client-python/commit/74658cfea7e439c10833c93594e3f1e43dc112cd))

# [2.2.0-beta.1](https://github.com/modelon-community/impact-client-python/compare/v2.1.1-beta.2...v2.2.0-beta.1) (2022-05-31)


### Features

* added support for expansion algorithms ([3acfbb4](https://github.com/modelon-community/impact-client-python/commit/3acfbb49e10bccf701ae8d20a153445103b7ea84))

## [2.1.1-beta.2](https://github.com/modelon-community/impact-client-python/compare/v2.1.1-beta.1...v2.1.1-beta.2) (2022-05-31)


### Bug Fixes

* refactored operator into a seperate model and updated to use dataclass ([3dcafdd](https://github.com/modelon-community/impact-client-python/commit/3dcafdd2a1cb02604500980592d7dd41bee6b870))

## [2.1.1-beta.1](https://github.com/modelon-community/impact-client-python/compare/v2.1.0...v2.1.1-beta.1) (2022-05-25)


### Bug Fixes

* updated python dependency ([e5cbd29](https://github.com/modelon-community/impact-client-python/commit/e5cbd29540c01365fd088d281630cb0423cd1ff4))

# [2.1.0](https://github.com/modelon-community/impact-client-python/compare/v2.0.1...v2.1.0) (2022-05-25)


### Features

* Added possibility to specify result format ([3ab12c8](https://github.com/modelon-community/impact-client-python/commit/3ab12c854e1615e4335fe7d4d21682a1c98de4f8))

# [2.1.0-beta.2](https://github.com/modelon-community/impact-client-python/compare/v2.1.0-beta.1...v2.1.0-beta.2) (2022-05-25)


### Bug Fixes

* add started to CaseStatus enum to mirror impact Case statuses ([1dcbf12](https://github.com/modelon-community/impact-client-python/commit/1dcbf1222ae3527ce89709bc569ee6e649e95b34))

# [2.1.0-beta.1](https://github.com/modelon-community/impact-client-python/compare/v2.0.0...v2.1.0-beta.1) (2022-02-17)


### Features

* Added possibility to specify result format ([3ab12c8](https://github.com/modelon-community/impact-client-python/commit/3ab12c854e1615e4335fe7d4d21682a1c98de4f8))
## [2.0.1](https://github.com/modelon-community/impact-client-python/compare/v2.0.0...v2.0.1) (2022-05-25)


### Bug Fixes

* add started to CaseStatus enum to mirror impact Case statuses ([1dcbf12](https://github.com/modelon-community/impact-client-python/commit/1dcbf1222ae3527ce89709bc569ee6e649e95b34))

# [2.0.0](https://github.com/modelon-community/impact-client-python/compare/v1.2.1...v2.0.0) (2022-02-17)


### Features

* remove workspace locks ([f93255f](https://github.com/modelon-community/impact-client-python/commit/f93255f5e0c5fe1c82cbab9346b02363290ce274))


### BREAKING CHANGES

* workspace locks removed

## [1.2.1](https://github.com/modelon-community/impact-client-python/compare/v1.2.0...v1.2.1) (2022-02-12)


### Bug Fixes

* Update impact api version range ([fdc6183](https://github.com/modelon-community/impact-client-python/commit/fdc61836bcaa882d0adf7388a74cf6d7841a137c))

# [1.2.0](https://github.com/modelon-community/impact-client-python/compare/v1.1.2...v1.2.0) (2022-02-02)


### Bug Fixes

* Added docs for installing the client with conda ([100297c](https://github.com/modelon-community/impact-client-python/commit/100297c5206b33e4e4ef13a5b46f97998cfa3bc9))
* Added docs for JupyterHub authentiation ([9001b1b](https://github.com/modelon-community/impact-client-python/commit/9001b1b0295e788df232581cd9bf6abbb58c3275))
* Appended underscore for init attributes ([43674ea](https://github.com/modelon-community/impact-client-python/commit/43674ea80b997c4a28fec9c04eaf2ac388cd9953))
* Assert reinitialization with multiple entities ([de090c2](https://github.com/modelon-community/impact-client-python/commit/de090c2ebfbadc36baffb4df55c399a2f175a34b))
* better documentation for setting a label for an experiment ([b64bb7c](https://github.com/modelon-community/impact-client-python/commit/b64bb7c31fa97f8ff5f9389cafc18d8b6d390e41))
* case update will get server changes ([bcc284e](https://github.com/modelon-community/impact-client-python/commit/bcc284e49eec50091cc076bbcacede4089da2079))
* changing the method name from updat to sync ([c05a711](https://github.com/modelon-community/impact-client-python/commit/c05a711fc85cbc8b37eea9e9669b519e24b3e0a1))
* clarification on documentation ([7786a92](https://github.com/modelon-community/impact-client-python/commit/7786a92a90182a6d1970e56e45258167b6979b28))
* correct order of arguments for creating case ([eb3cba2](https://github.com/modelon-community/impact-client-python/commit/eb3cba2aaa2c19901003222951067998ae6ab6e8))
* Corrected analysis to be a property ([48b7d5d](https://github.com/modelon-community/impact-client-python/commit/48b7d5dab360de586b4ac2b56e8686a1aa727f53))
* docs fix ([e489676](https://github.com/modelon-community/impact-client-python/commit/e489676711beea5dfec3ecfd8377c6454fcc9307))
* exmple creating set of all FMUs does now works ([e962361](https://github.com/modelon-community/impact-client-python/commit/e962361b8fc1ed7432e12e28254230772f47f335))
* experiment.is_successful() method now returns true only if all cases pass successfuly ([7994a0b](https://github.com/modelon-community/impact-client-python/commit/7994a0be653c273c99b93e360f9d103183e2082c))
* format of .rleaserc file ([a50356f](https://github.com/modelon-community/impact-client-python/commit/a50356ffaff822ec9140cd5c96326d7c8de2fc13))
* given empty string as API key, do anon login and don't save key ([8eaf3de](https://github.com/modelon-community/impact-client-python/commit/8eaf3de138656583f7488937c47c3cebd13476cf))
* imports that works for Python 3.6 ([0bcaa03](https://github.com/modelon-community/impact-client-python/commit/0bcaa03ae0446e50e5f915cd2fb13cffe8e56b1d))
* initialize_from assignments ([d59423e](https://github.com/modelon-community/impact-client-python/commit/d59423eb6912ab64e0a8a646438fe32b7115bd61))
* make sure only newer versions of the API with needed features are used ([9fb2cf7](https://github.com/modelon-community/impact-client-python/commit/9fb2cf7b9b49f3afbabe846126422027140c3380))
* making license type more explicit in error message ([be9c38f](https://github.com/modelon-community/impact-client-python/commit/be9c38fe145408d2f558c24ddea8a7fc5da55e5b))
* making warning logging more precise ([d6be8d6](https://github.com/modelon-community/impact-client-python/commit/d6be8d6fd492fd219ce30a867d417dbeaadbe193))
* making warning message a little more precise ([1805636](https://github.com/modelon-community/impact-client-python/commit/1805636d5f45e2898d007aef85ef64e4b20f96ad))
* message and re-try for Windows ctrl+v bug ([be1f8c0](https://github.com/modelon-community/impact-client-python/commit/be1f8c021f3895b3bb6e1251c0c489a800884866))
* Modified label and description to defaults ([21fe7ff](https://github.com/modelon-community/impact-client-python/commit/21fe7ffb24a470381153d9c1722d65e2fc3bb6d1))
* not started status not checked for successful experiment ([96d08c8](https://github.com/modelon-community/impact-client-python/commit/96d08c894178bf51d0549b8245b3853c921e8dfe))
* Remove conda install instrictions from docs ([0d175a1](https://github.com/modelon-community/impact-client-python/commit/0d175a1fbe1a6d5d98bad82294ba3ed67c89bc42))
* removing configuration of log level in modules ([d8b2030](https://github.com/modelon-community/impact-client-python/commit/d8b2030cfdbc3928746a28770995fa37f2faf138))
* removing separate lint step ([805987a](https://github.com/modelon-community/impact-client-python/commit/805987a7eb5e89309225a478f2cdc43e25919f6a))
* removing some old 'update' references ([991f237](https://github.com/modelon-community/impact-client-python/commit/991f2372759438082988dfe54cfac8b3db0aa270))
* removing unused code ([cdb9901](https://github.com/modelon-community/impact-client-python/commit/cdb99019bce9f0eabbe498f6401fa51cb1d4ded0))
* spelling ([1ee0df3](https://github.com/modelon-community/impact-client-python/commit/1ee0df3de21ca1e531795f66bf3b1b4173cc21de))
* update node version to one that work with latest semantic-release ([60575a0](https://github.com/modelon-community/impact-client-python/commit/60575a032599faab967af1cfed478717818a5790))
* Using a mock file to emulate fmu import test ([77cd52e](https://github.com/modelon-community/impact-client-python/commit/77cd52e3ac3a3d7c42cee22d196f8c8d0894f26d))


### Features

* Added API support for deleting fmus and experiments ([aede75e](https://github.com/modelon-community/impact-client-python/commit/aede75ead69c1ec40ffed6b7842b4ae138bae8f0))
* Added documentation for newly added functionality ([42708a0](https://github.com/modelon-community/impact-client-python/commit/42708a0fef180d0ac39e3c1b2ccbec7fbdafb254))
* Added possibility to specify and update label ([8517b83](https://github.com/modelon-community/impact-client-python/commit/8517b83e61d19049eeb5c458bda2fa33a6580e3b))
* Added support for external result file upload ([5855c32](https://github.com/modelon-community/impact-client-python/commit/5855c324d479410d429ac2bc3893397f49e2f751))
* Added support for FMU import ([389fa6b](https://github.com/modelon-community/impact-client-python/commit/389fa6b4c07d4a9ab77a43e7611b13fb73d06880))
* Added support for initializing from case and experiment ([7f694ff](https://github.com/modelon-community/impact-client-python/commit/7f694ff8ac12902727cece6b8f2f51954db01b24))
* Added support for initializing from external result ([5e1243c](https://github.com/modelon-community/impact-client-python/commit/5e1243cba2318232d7d7adb0bfac7cb2fe141d60))
* Added support to execute list of cases ([e070d8a](https://github.com/modelon-community/impact-client-python/commit/e070d8ae0a390764c1774d8c25102a1c4c984166))
* Added support to set labels for experiment ([361555c](https://github.com/modelon-community/impact-client-python/commit/361555cfa975eaa89a2a3c5a5607947e5326cc1d))
* Added support to update and execute cases ([eae776a](https://github.com/modelon-community/impact-client-python/commit/eae776a77a9e3b5d942819c3cdb776e19759a3dd))
* case data is only fetched for cases when created ([e918644](https://github.com/modelon-community/impact-client-python/commit/e9186444714f31cf81aa4daab17ab968190daa5f))
* check if user has license, else give error ([f986dbe](https://github.com/modelon-community/impact-client-python/commit/f986dbe975ffc7ec66e0651f23d345b58b161f8d))
* detect if working against Jupyterhub and throw error ([ced00a7](https://github.com/modelon-community/impact-client-python/commit/ced00a7fd23ace70f7ed40677ac2990858470be4))
* enable user_data attached to experiments ([83bbcf8](https://github.com/modelon-community/impact-client-python/commit/83bbcf8810d568f5d76bedbea52a394311883614))
* login again if there is an authentication error ([3e9ff3d](https://github.com/modelon-community/impact-client-python/commit/3e9ff3d932281564eb20c3387e3651b3aa4ef456))
* make credential manager customizable ([949ccb6](https://github.com/modelon-community/impact-client-python/commit/949ccb6cb33f9072a541f554b76edf4035a66741))
* possible to authorize against Jupyterhub ([2d2b1f4](https://github.com/modelon-community/impact-client-python/commit/2d2b1f4eadee1a28f18bbf42b911a8589eb28a75))
* possible to check if a case is consistent ([98c48ae](https://github.com/modelon-community/impact-client-python/commit/98c48aea89634001cfdc5e4cdd7716595a73df6a))
* Support for executing a created experiment ([17452b9](https://github.com/modelon-community/impact-client-python/commit/17452b984e1c50ee63df4eec961701578cddfdc5))
* sync changes automatically for cases when executing them ([c2f178e](https://github.com/modelon-community/impact-client-python/commit/c2f178edb1928b4371afe62f1ec1d880e90d4847))

# [1.2.0-beta.33](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.32...v1.2.0-beta.33) (2022-01-31)


### Bug Fixes

* Added docs for JupyterHub authentiation ([0be6f3c](https://github.com/modelon-community/impact-client-python/commit/0be6f3c92373771dcbff15dbc913b58d7c2b66ee))

# [1.2.0-beta.32](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.31...v1.2.0-beta.32) (2022-01-10)


### Bug Fixes

* docs fix ([f96d65a](https://github.com/modelon-community/impact-client-python/commit/f96d65a667fc722dd12a5a4b0bed214beb217f38))

# [1.2.0-beta.31](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.30...v1.2.0-beta.31) (2021-12-20)


### Bug Fixes

* Added docs for installing the client with conda ([c9c3253](https://github.com/modelon-community/impact-client-python/commit/c9c325364e5d0a3f09250de31c4a664d708512ae))

# [1.2.0-beta.30](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.29...v1.2.0-beta.30) (2021-12-20)


### Bug Fixes

* Remove conda install instrictions from docs ([a13a66a](https://github.com/modelon-community/impact-client-python/commit/a13a66a57b79744dab48867fa8f8737257c524a2))

# [1.2.0-beta.29](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.28...v1.2.0-beta.29) (2021-12-15)


### Features

* Added documentation for newly added functionality ([42e82a2](https://github.com/modelon-community/impact-client-python/commit/42e82a2887713324067af90c8f25fec056c43f24))

# [1.2.0-beta.28](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.27...v1.2.0-beta.28) (2021-12-07)


### Bug Fixes

* making license type more explicit in error message ([5c98b1e](https://github.com/modelon-community/impact-client-python/commit/5c98b1e28875ef1f483b80056b93f8890197ac44))


### Features

* check if user has license, else give error ([b52c1ed](https://github.com/modelon-community/impact-client-python/commit/b52c1ed1654a5982775334257ce03102be048240))

# [1.2.0-beta.27](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.26...v1.2.0-beta.27) (2021-12-02)


### Features

* login again if there is an authentication error ([d4b39a8](https://github.com/modelon-community/impact-client-python/commit/d4b39a80a3ab70140ae30a26bee476a9120df8eb))

# [1.2.0-beta.26](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.25...v1.2.0-beta.26) (2021-11-19)


### Features

* enable user_data attached to experiments ([538fca2](https://github.com/modelon-community/impact-client-python/commit/538fca2d301f1162a7bfea0a95b29b709681d2dc))

# [1.2.0-beta.25](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.24...v1.2.0-beta.25) (2021-11-04)


### Bug Fixes

* imports that works for Python 3.6 ([ec5a7c2](https://github.com/modelon-community/impact-client-python/commit/ec5a7c27a7038fc868478d6a09bd9afceaeb57cf))

# [1.2.0-beta.24](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.23...v1.2.0-beta.24) (2021-11-02)


### Bug Fixes

* format of .rleaserc file ([7d0c8d0](https://github.com/modelon-community/impact-client-python/commit/7d0c8d02ab3086747926e665fad9cb61c80c41c9))
* making warning logging more precise ([7598c4e](https://github.com/modelon-community/impact-client-python/commit/7598c4eeeadaf9fc88ff8b24f6ecf393359a2142))
* making warning message a little more precise ([7d14f94](https://github.com/modelon-community/impact-client-python/commit/7d14f94666e6c94ee0c9d3c2f4976ce9f3b421c4))
* message and re-try for Windows ctrl+v bug ([2f82dd4](https://github.com/modelon-community/impact-client-python/commit/2f82dd40e7e90a54e6e98a145540ebbcda5ec29c))
* removing separate lint step ([1aaa9d9](https://github.com/modelon-community/impact-client-python/commit/1aaa9d933a2a3ece936ea324ed63c5b3a2ab73c1))


### Features

* detect if working against Jupyterhub and throw error ([7fa2278](https://github.com/modelon-community/impact-client-python/commit/7fa2278c0a27e7acda63ea85c9a32268869d490f))
* make credential manager customizable ([a7e05b9](https://github.com/modelon-community/impact-client-python/commit/a7e05b95ef93ab1e9b200f71c4c532bda4f34474))
* possible to authorize against Jupyterhub ([c6d700c](https://github.com/modelon-community/impact-client-python/commit/c6d700cc3afd3c0a7f0a5be3906c3d221d5dfb5a))

# [1.2.0-beta.23](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.22...v1.2.0-beta.23) (2021-10-15)


### Bug Fixes

* given empty string as API key, do anon login and don't save key ([f9567e2](https://github.com/modelon-community/impact-client-python/commit/f9567e2ca5bcaadb924556a6802aeb17775e1a06))

# [1.2.0-beta.22](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.21...v1.2.0-beta.22) (2021-10-11)


### Features

* Added possibility to specify and update label ([29f2aa9](https://github.com/modelon-community/impact-client-python/commit/29f2aa9a4758efed2d7874de2892a5946f2ee95e))

# [1.2.0-beta.21](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.20...v1.2.0-beta.21) (2021-09-28)


### Bug Fixes

* changing the method name from updat to sync ([ead2710](https://github.com/modelon-community/impact-client-python/commit/ead2710bbd83d7d371d94d671c69d3ee91ce3667))
* removing some old 'update' references ([1728c32](https://github.com/modelon-community/impact-client-python/commit/1728c3225a5b06253761b93f0fe8320210fdaa81))
* update node version to one that work with latest semantic-release ([40935ad](https://github.com/modelon-community/impact-client-python/commit/40935adf68d58a3874c4397e2273dd5eef6af82c))


### Features

* sync changes automatically for cases when executing them ([c96873e](https://github.com/modelon-community/impact-client-python/commit/c96873e09b0f0125099834c3e7f870d6528e8c4c))

# [1.2.0-beta.20](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.19...v1.2.0-beta.20) (2021-09-08)


### Bug Fixes

* Appended underscore for init attributes ([3117c59](https://github.com/modelon-community/impact-client-python/commit/3117c59c7e31bc48b04b1e87e03ea18ddbca5274))
* Corrected analysis to be a property ([fbb196a](https://github.com/modelon-community/impact-client-python/commit/fbb196a471c2d2e9f1c0e90b3a129c6aa90dbdf0))

# [1.2.0-beta.19](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.18...v1.2.0-beta.19) (2021-09-08)


### Bug Fixes

* Assert reinitialization with multiple entities ([8f0d44d](https://github.com/modelon-community/impact-client-python/commit/8f0d44d5c11bbb1bbe08839a6ba8aa600da1b711))

# [1.2.0-beta.18](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.17...v1.2.0-beta.18) (2021-09-07)


### Features

* possible to check if a case is consistent ([33d2b52](https://github.com/modelon-community/impact-client-python/commit/33d2b52fec8258127bcc1e60e0b6a8ea749df829))

# [1.2.0-beta.17](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.16...v1.2.0-beta.17) (2021-09-07)


### Bug Fixes

* case update will get server changes ([3230ad5](https://github.com/modelon-community/impact-client-python/commit/3230ad5af16c8afd188cc14792698ba109ad50be))
* spelling ([9642222](https://github.com/modelon-community/impact-client-python/commit/96422229ca04387d97b4f35ff6024cac3944ff8c))

# [1.2.0-beta.16](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.15...v1.2.0-beta.16) (2021-09-06)


### Bug Fixes

* Modified label and description to defaults ([c639f23](https://github.com/modelon-community/impact-client-python/commit/c639f235cd8ffb16be91871f9f3b34fd0b0928d7))

# [1.2.0-beta.15](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.14...v1.2.0-beta.15) (2021-09-06)


### Features

* Added support for external result file upload ([8a08702](https://github.com/modelon-community/impact-client-python/commit/8a0870202c5609733b2f262d11603347b34a3c6c))
* Added support for initializing from external result ([851ba1f](https://github.com/modelon-community/impact-client-python/commit/851ba1f65e0dc71b8a766737da9b0142f55babdc))

# [1.2.0-beta.14](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.13...v1.2.0-beta.14) (2021-09-03)


### Bug Fixes

* clarification on documentation ([2a16655](https://github.com/modelon-community/impact-client-python/commit/2a166552c29f692d9960971aaf0191d676fa7731))
* removing configuration of log level in modules ([8f2ede3](https://github.com/modelon-community/impact-client-python/commit/8f2ede388bb497512f5feb3e4cb44f48097bd1ce))
* removing unused code ([153d1e9](https://github.com/modelon-community/impact-client-python/commit/153d1e92b4b6d7ae5265d4477386980322f60d5d))


### Features

* case data is only fetched for cases when created ([ee37d53](https://github.com/modelon-community/impact-client-python/commit/ee37d53d3db21a073c62c84b610082536f0b8949))

# [1.2.0-beta.13](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.12...v1.2.0-beta.13) (2021-09-02)


### Bug Fixes

* Using a mock file to emulate fmu import test ([ee8125d](https://github.com/modelon-community/impact-client-python/commit/ee8125def1f32a53661e77b10f7e1796e141d097))

# [1.2.0-beta.12](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.11...v1.2.0-beta.12) (2021-09-02)


### Bug Fixes

* better documentation for setting a label for an experiment ([3cb46a0](https://github.com/modelon-community/impact-client-python/commit/3cb46a074e5fbd0ef85adcf2928328cdcd499704))
* make sure only newer versions of the API with needed features are used ([13d4673](https://github.com/modelon-community/impact-client-python/commit/13d46730dcf2300677ab72b4cc1c34d29e9f66ee))

# [1.2.0-beta.11](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.10...v1.2.0-beta.11) (2021-08-27)


### Bug Fixes

* initialize_from assignments ([7fc376d](https://github.com/modelon-community/impact-client-python/commit/7fc376d7eb376c27e7086a0ab3313e46571f2a04))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.9...v1.2.0-beta.10) (2021-08-27)


### Bug Fixes

* correct order of arguments for creating case ([0941c51](https://github.com/modelon-community/impact-client-python/commit/0941c51220a268b109f5eddbdd018cd83b55ed3b))

# [1.2.0-beta.9](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.8...v1.2.0-beta.9) (2021-08-13)


### Features

* Added support for FMU import ([0351ecf](https://github.com/modelon-community/impact-client-python/commit/0351ecf08f9bc4bad0549c27e5e4acbbb7cab06e))

# [1.2.0-beta.8](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.7...v1.2.0-beta.8) (2021-08-03)


### Features

* Added support for initializing from case and experiment ([d104e6a](https://github.com/modelon-community/impact-client-python/commit/d104e6a9fe6b8086cdc4f5a1df5d40562fbcc75c))

# [1.2.0-beta.7](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.6...v1.2.0-beta.7) (2021-08-01)


### Bug Fixes

* not started status not checked for successful experiment ([d655d7c](https://github.com/modelon-community/impact-client-python/commit/d655d7cf1b46240c7cf675458e39de1abe79f1ef))

# [1.2.0-beta.6](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.5...v1.2.0-beta.6) (2021-07-27)


### Bug Fixes

* experiment.is_successful() method now returns true only if all cases pass successfuly ([252a69b](https://github.com/modelon-community/impact-client-python/commit/252a69be254b8d0355e73327b308faad516a3e1b))

# [1.2.0-beta.5](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.4...v1.2.0-beta.5) (2021-07-21)


### Features

* Added support to set labels for experiment ([b6bdebb](https://github.com/modelon-community/impact-client-python/commit/b6bdebb434a4f9cf81782639a1b049593c9c3fd0))

# [1.2.0-beta.4](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.3...v1.2.0-beta.4) (2021-07-21)


### Features

* Added support to update and execute cases ([bd5467c](https://github.com/modelon-community/impact-client-python/commit/bd5467ca0310b62eef4e1d21d4cbd03881efee1c))

# [1.2.0-beta.3](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.2...v1.2.0-beta.3) (2021-07-16)


### Features

* Added support to execute list of cases ([2df49b4](https://github.com/modelon-community/impact-client-python/commit/2df49b435dbda82e100196b243c4fc69821e4dfb))

# [1.2.0-beta.2](https://github.com/modelon-community/impact-client-python/compare/v1.2.0-beta.1...v1.2.0-beta.2) (2021-07-15)


### Features

* Support for executing a created experiment ([76f2a32](https://github.com/modelon-community/impact-client-python/commit/76f2a32872f2a85f2a9790fe4f49064448d2a285))

# [1.2.0-beta.1](https://github.com/modelon-community/impact-client-python/compare/v1.1.2...v1.2.0-beta.1) (2021-07-13)


### Bug Fixes

* exmple creating set of all FMUs does now works ([53ff423](https://github.com/modelon-community/impact-client-python/commit/53ff423f40b10701ada533563df8a683eaff4076))


### Features

* Added API support for deleting fmus and experiments ([d1affd8](https://github.com/modelon-community/impact-client-python/commit/d1affd879744677d1b7283f49a348a3a043442ec))

## [1.1.2](https://github.com/modelon-community/impact-client-python/compare/v1.1.1...v1.1.2) (2021-04-20)


### Bug Fixes

* Corrected docs for get_experiment() ([97491be](https://github.com/modelon-community/impact-client-python/commit/97491bec50d369fcbd9f26512b872e1bb13a36c0))

## [1.1.1](https://github.com/modelon-community/impact-client-python/compare/v1.1.0...v1.1.1) (2021-03-26)


### Bug Fixes

* clarification on 'interactive' argument in client docstring ([0b3e1da](https://github.com/modelon-community/impact-client-python/commit/0b3e1da8b01d65e7b0ef4b29d628d368885dd5fa))

# [1.1.0](https://github.com/modelon-community/impact-client-python/compare/v1.0.0...v1.1.0) (2021-02-09)


### Bug Fixes

* __repr__ function does not throw attribute error ([083e195](https://github.com/modelon-community/impact-client-python/commit/083e1955c161cdf60d86c7ae65941e3bca8b0840))
* add _sal_custom_func to cloned workspace ([0389de5](https://github.com/modelon-community/impact-client-python/commit/0389de536b60a140291e19c8e9c2ab566b5b9d9c))
* Added docs ([fb96bcd](https://github.com/modelon-community/impact-client-python/commit/fb96bcd2bbccb73f5966f6ff3e5b5d454902b5d7))
* Added documentation for setting log level ([1850d22](https://github.com/modelon-community/impact-client-python/commit/1850d22bc741f7beff680f62871a798fafbbf69e))
* added failure status for experiment and way to get errors ([368bcfe](https://github.com/modelon-community/impact-client-python/commit/368bcfec8920d65b18bc573636392657300a7da4))
* Added missing raises and return to documentation ([594eefb](https://github.com/modelon-community/impact-client-python/commit/594eefb4957e51623cf467c59702969086fafdae))
* Added semantic versioning to the requirements. This was causing failure to build the docs for modelon.impact.client.client module. ([0b11416](https://github.com/modelon-community/impact-client-python/commit/0b114167aa8f9fcfbec0638ca4fa5f7a654087e5))
* Adding Docstrings and minor fixes ([fe87659](https://github.com/modelon-community/impact-client-python/commit/fe876598d28623dd80ae2165920a548506fdd45c))
* Adding read the docs specifics ([ec2fd03](https://github.com/modelon-community/impact-client-python/commit/ec2fd03fbc114ce4cfb86f9fdafacfdcf140e528))
* allow integers in custom function parameters ([f23ddf4](https://github.com/modelon-community/impact-client-python/commit/f23ddf4583264640b661888f3f79ce6cf9739c3f))
* Allowing options/specs to be given as a dict or options/specs class instance ([9b3bf83](https://github.com/modelon-community/impact-client-python/commit/9b3bf83a16843fedfa7e9d7d1f8f322375eb2879))
* Avoid users to hard-code api keys ([85d0a63](https://github.com/modelon-community/impact-client-python/commit/85d0a6362d8c0726fb192b2a1583c7070814f08f))
* cases,case --> get_cases,get_case ([d0895a3](https://github.com/modelon-community/impact-client-python/commit/d0895a3bad3c39653cc533ea41632d57cc5e75f6))
* change docs to match current signature of client.upload_workspace ([88b69c8](https://github.com/modelon-community/impact-client-python/commit/88b69c823c9e8857047355124dba5a00d8f4928d))
* change wording on refreshing api keys ([d4f229f](https://github.com/modelon-community/impact-client-python/commit/d4f229f5418592b2b32f747dc9cc6fc8f5ddcc21))
* changed imports to be python 3.6 compatible ([ebbbf52](https://github.com/modelon-community/impact-client-python/commit/ebbbf524af365a56f263a349caebbb73927691e9))
* Consistent naming of functions ([fb0cee0](https://github.com/modelon-community/impact-client-python/commit/fb0cee03cf95aa718526fe66020485b1bcb0b0b9))
* correct artifactory URL ([4b4195d](https://github.com/modelon-community/impact-client-python/commit/4b4195d6645db9ebfca740e70d144c379efa5d60))
* correct artifactory URL ([b0f5615](https://github.com/modelon-community/impact-client-python/commit/b0f56158827d7ae4429675674fdc0cbd3589f866))
* correct docs on model.new_experiment_definition ([#83](https://github.com/modelon-community/impact-client-python/issues/83)) ([b38da7c](https://github.com/modelon-community/impact-client-python/commit/b38da7c6be20d4e32c7045aa81ec9ee24568e57e))
* correct some spelling in the documentation ([#87](https://github.com/modelon-community/impact-client-python/issues/87)) ([11da229](https://github.com/modelon-community/impact-client-python/commit/11da2290d3ac2e2c35e7eefb9d9452cc24b3e1ee))
* Corrected the compilation response from json to plain/text ([69743b4](https://github.com/modelon-community/impact-client-python/commit/69743b4bf437a3e374a047d0e3e0c78711721fdd))
* Corrected the default compiler log level to 'warning' ([1b53a4f](https://github.com/modelon-community/impact-client-python/commit/1b53a4fce11a7a7d25b3fe319f60d681d2f1c01c))
* Corrected the response json property name returned for endpoint '/workspaces' ([f1f881b](https://github.com/modelon-community/impact-client-python/commit/f1f881bf9a710e8a4e28d9e513e5f5d16e83f542))
* Corrected the to_dict to be method rather than a property ([15297d2](https://github.com/modelon-community/impact-client-python/commit/15297d2cf24e56a98c373fb87061774dca012186))
* Corrected the upload_workspace api ([16e9cc8](https://github.com/modelon-community/impact-client-python/commit/16e9cc84495f69c4491af406b7cbe8fc8125b20b))
* Correcting the compilation/simulation status checks. ([d27d1c3](https://github.com/modelon-community/impact-client-python/commit/d27d1c323eca39f135289c580cb113da5beab4fc))
* delete invalid api keys to let user reenter new ones ([#61](https://github.com/modelon-community/impact-client-python/issues/61)) ([f1c71af](https://github.com/modelon-community/impact-client-python/commit/f1c71afd31006628768d08dff77a0e4cd6c72fa5))
* do not give NoResponseFetchVersionError for SSL error ([3b842a9](https://github.com/modelon-community/impact-client-python/commit/3b842a93796417b1485519269f8f574a2de29c70))
* do not save key if asking for it interactively, it might be invalid ([b8cef20](https://github.com/modelon-community/impact-client-python/commit/b8cef20c5e45308a24f795925453809c67ec1eea))
* error fix ([65c4884](https://github.com/modelon-community/impact-client-python/commit/65c4884905f39abd005ba9cbcdd4f75a6c8d1bfe))
* example doc code should be closer to being executable now ([1506fd2](https://github.com/modelon-community/impact-client-python/commit/1506fd20cea85c1053cbf980ae925681ba5ad40e))
* ExecutionOption -> ExecutionOptions ([dcad9a6](https://github.com/modelon-community/impact-client-python/commit/dcad9a6521abadef20d1f334b139902cb6f8b4d2))
* Feedback fixes ([88d59e1](https://github.com/modelon-community/impact-client-python/commit/88d59e10ffccd943acb1ab015d0662bce3276cb1))
* fix bad kerning in svg file ([fe85eb6](https://github.com/modelon-community/impact-client-python/commit/fe85eb6c94f7e47eb2cd98c3df9755c04c9ef70e))
* Fixed a typo ([4783eb2](https://github.com/modelon-community/impact-client-python/commit/4783eb2f9f47957a03f9767cd7a2a0f0877936a6))
* Formatting and lint fixes ([4d98783](https://github.com/modelon-community/impact-client-python/commit/4d98783cdd8c1bd06471b94d203241b4bd072b62))
* Grammar/font fixes ([7ddd2bd](https://github.com/modelon-community/impact-client-python/commit/7ddd2bde116db4167ac995b77661a2cc3fc16dec))
* Inheriting mapping class for ExecutionOptions ([e934d92](https://github.com/modelon-community/impact-client-python/commit/e934d92dbe16ad9f418d7ce23b233a5a7a8fc6c1))
* less confusing __repr__ for workspace ([fb42587](https://github.com/modelon-community/impact-client-python/commit/fb4258797df9f0b25dac8c420b1abc320f49fd9a))
* Lint fixes ([2c4a7f4](https://github.com/modelon-community/impact-client-python/commit/2c4a7f443286da683e81222717fc6db36ab9402c))
* Made fmu.modifier method private ([dde8351](https://github.com/modelon-community/impact-client-python/commit/dde8351b832b7270383cfc070ff2ecfd4b57b6a2))
* making release.sh executable ([71cbac2](https://github.com/modelon-community/impact-client-python/commit/71cbac272d9ba160bd9f79763e90670e4b802d00))
* Moving info to constructor ([e31b589](https://github.com/modelon-community/impact-client-python/commit/e31b589c45f0e432ee16b9c46635bafca41ca7ba))
* Moving info to model_exe constructor ([b00eeba](https://github.com/modelon-community/impact-client-python/commit/b00eeba710ac6f05063e32962bfb464c48712a8f))
* mypy and formatting corrections ([478b06b](https://github.com/modelon-community/impact-client-python/commit/478b06b2b36ec7e9c38347a24cdda1dc23e0a28f))
* performance improvement, do not call cases unless neccessary ([0f382db](https://github.com/modelon-community/impact-client-python/commit/0f382dbde5755b5c10e4ee9d7a243ff6e5228f47))
* Performance improvements - Raising exceptions instead of waiting for operation completion when calling compilation/simulation methods/properties ([5834241](https://github.com/modelon-community/impact-client-python/commit/58342416dd6e3d4947b7bcbe3f51bc4921b294b1))
* pretty print the log ([e277c68](https://github.com/modelon-community/impact-client-python/commit/e277c684c9a8280d9ec96d2040d7a3d55184f0c6))
* Python 3.6 compatibility fixes ([048158f](https://github.com/modelon-community/impact-client-python/commit/048158f5cf3d21134e67b78b54500529abfb3735))
* Remove dead code ([ac5cfec](https://github.com/modelon-community/impact-client-python/commit/ac5cfecd19044af0cb2e97a546b8a682d0ad81c9))
* Remove trailing commas when single values are given in Choices o… ([#79](https://github.com/modelon-community/impact-client-python/issues/79)) ([b1bb184](https://github.com/modelon-community/impact-client-python/commit/b1bb184463f3e537001966b7eea72b4b491a47e0))
* Removed an unwanted check from wait() function ([f91c5e0](https://github.com/modelon-community/impact-client-python/commit/f91c5e0d4512d7d1b662e1ce089735f483eb7e6f))
* Removed kwargs argument from docs as we only need to support 'qualified' variable names ([5cc63e3](https://github.com/modelon-community/impact-client-python/commit/5cc63e30b921a01770eff8bd354faf2bd4f1b874))
* removing test not running on module ([472a917](https://github.com/modelon-community/impact-client-python/commit/472a917a34a59275093de6c7bb60b05f33aa75d2))
* Removing the pandas dependency due to performance hits ([50fca3a](https://github.com/modelon-community/impact-client-python/commit/50fca3aae4cbf6ccc3e33d1979ef8d58244d0f61))
* Removing the settable parameter call from the assert ([bd011a2](https://github.com/modelon-community/impact-client-python/commit/bd011a2fc470c52177b05e737a2f278691a53f08))
* Renamed experiment_definition -> experiment_definition ([0879358](https://github.com/modelon-community/impact-client-python/commit/08793586da5bd54f65b13cdc5ee62de307c66bed))
* Renamed options to values in execution options ([7ef6745](https://github.com/modelon-community/impact-client-python/commit/7ef6745f4c6a70e24d152838ad73be3d59844065))
* Renaming import_library to upload_model_library ([7705160](https://github.com/modelon-community/impact-client-python/commit/7705160689b97f5a82c98c58b8f50d3ce9560ec6))
* save api key even if .impact already exists ([a3fe58e](https://github.com/modelon-community/impact-client-python/commit/a3fe58e53c41f22788be4d8eabe6e43c0fd4545b))
* Seperate methods for getting and printing log ([c600364](https://github.com/modelon-community/impact-client-python/commit/c6003640bf65d91d0288544fb042ef2cb7dced25))
* Seperating the operations and entities module ([e953cf0](https://github.com/modelon-community/impact-client-python/commit/e953cf022a264ca887e0e8f8f605212554f455db))
* Simplifying the code for engineers ([74e3bdf](https://github.com/modelon-community/impact-client-python/commit/74e3bdf106fccd34b3642762a81ce62b4447e7ea))
* Striping quotes from suggested filename ([f735b50](https://github.com/modelon-community/impact-client-python/commit/f735b5058cbcc62e5deec640606b67cc3f0d88e9))
* Upadted the supported api version number ([cc2540e](https://github.com/modelon-community/impact-client-python/commit/cc2540e916784049ac17eae1f526be1c64c12d09))
* update tests ([0f6901b](https://github.com/modelon-community/impact-client-python/commit/0f6901bfa3b7b327a6ce88e7713222aedaa556c6))
* Updated modifers to be a dict ([7adb322](https://github.com/modelon-community/impact-client-python/commit/7adb3225516fc950c0c855d003155c6457f99dde))
* Updated Readme and pyproject.toml ([272debf](https://github.com/modelon-community/impact-client-python/commit/272debf1c498e89b6c469b0244fd123b1fe1e52f))
* Updated the defaults for get_trajectories ([f77b7e4](https://github.com/modelon-community/impact-client-python/commit/f77b7e473a15376e588f7744768b45fc5c2c57d2))
* Updated the metadata property to use the new POST /steady-state-metadata api ([#85](https://github.com/modelon-community/impact-client-python/issues/85)) ([9be7b4e](https://github.com/modelon-community/impact-client-python/commit/9be7b4eb0a22e03f7bdfdac7bf57510a042df8f5))
* using api tokens instead of usename password for jenkins ([76ee2a2](https://github.com/modelon-community/impact-client-python/commit/76ee2a2bbcbb97c4d3289d2e5e5e4c261a9babf1))
* using correct body field for the secret key ([0d5f306](https://github.com/modelon-community/impact-client-python/commit/0d5f306ae14c664577964840feb99422bfc43e63))
* workaround for performance issues on Windows ([ae3eb5b](https://github.com/modelon-community/impact-client-python/commit/ae3eb5bc4609240420e2450452c64e13b070325d))


### Features

* Add possibility to download FMU ([5e597f0](https://github.com/modelon-community/impact-client-python/commit/5e597f01bcee76b71f54b0c720cc000c37f89da7))
* Added checks to use cached FMU if available ([4fcb616](https://github.com/modelon-community/impact-client-python/commit/4fcb6164667269c01c74339b05ec90923906487f))
* Added possibility to set parameter modifers as a part of experiment definition instead of using legacy routes ([9802d84](https://github.com/modelon-community/impact-client-python/commit/9802d84c6b116c5eddfd53462f630ab0869672f6))
* Added semantic version checks for API ([94fed15](https://github.com/modelon-community/impact-client-python/commit/94fed15d84313d1471c038ae91d411da5d3d9271))
* Added support for choices operator ([3a2cfd0](https://github.com/modelon-community/impact-client-python/commit/3a2cfd0ab5f096bd1a2578958aad3cf3abb147eb))
* Added support for download result artifact ([e6b8108](https://github.com/modelon-community/impact-client-python/commit/e6b81083fd00207aca2d979b853868880ab81dc2))
* Added support for fetching fmus executed for a case ([#80](https://github.com/modelon-community/impact-client-python/issues/80)) ([9034ba8](https://github.com/modelon-community/impact-client-python/commit/9034ba832f734ab378dc1840f946f93000471f51))
* Added support for modelica_class name based workflows ([0106196](https://github.com/modelon-community/impact-client-python/commit/01061960c6f63e421ee1f533e87f6e9c11f054d5))
* Adding functions for the workspace and model class entities ([63cb71b](https://github.com/modelon-community/impact-client-python/commit/63cb71b56e28d171f245ac01d95ecb7add48cf9f))
* default behaviour for option input to SimpleExperiment ([3bdb899](https://github.com/modelon-community/impact-client-python/commit/3bdb8998c7999b0057270de177a274b1c56a56ad))
* initial repository setup ([1630038](https://github.com/modelon-community/impact-client-python/commit/16300382033c76679adedfefeff9c6de068446dd))
* integrating custom function entity ([97951b7](https://github.com/modelon-community/impact-client-python/commit/97951b7aace16eaa3deb419f232b9264410cf976))
* Possibility to add extensions to experiment ([0c4c2d8](https://github.com/modelon-community/impact-client-python/commit/0c4c2d814be80008a6762bd6e2def140be866725))
* possible to specify client inputs through env variables ([e0f6bfe](https://github.com/modelon-community/impact-client-python/commit/e0f6bfef58e907c91e7143d6aa6bdc80cba26846))
* run_info attributes returs documented class objects, info ([f46b5ab](https://github.com/modelon-community/impact-client-python/commit/f46b5abcf43bd032b5b5592fff9cf2011e447e3e))
* Using the case trajectory api to fetch case trajectories ([8d16708](https://github.com/modelon-community/impact-client-python/commit/8d167084dd4d58f419f55318509f7a170ab5474e))

# [1.1.0-beta.19](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.18...v1.1.0-beta.19) (2021-02-09)


### Bug Fixes

* correct some spelling in the documentation ([#87](https://github.com/modelon-community/impact-client-python/issues/87)) ([11da229](https://github.com/modelon-community/impact-client-python/commit/11da2290d3ac2e2c35e7eefb9d9452cc24b3e1ee))

# [1.1.0-beta.18](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.17...v1.1.0-beta.18) (2021-02-09)


### Bug Fixes

* Made fmu.modifier method private ([dde8351](https://github.com/modelon-community/impact-client-python/commit/dde8351b832b7270383cfc070ff2ecfd4b57b6a2))

# [1.1.0-beta.17](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.16...v1.1.0-beta.17) (2021-02-09)


### Bug Fixes

* Updated the metadata property to use the new POST /steady-state-metadata api ([#85](https://github.com/modelon-community/impact-client-python/issues/85)) ([9be7b4e](https://github.com/modelon-community/impact-client-python/commit/9be7b4eb0a22e03f7bdfdac7bf57510a042df8f5))

# [1.1.0-beta.16](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.15...v1.1.0-beta.16) (2021-02-08)


### Bug Fixes

* correct docs on model.new_experiment_definition ([#83](https://github.com/modelon-community/impact-client-python/issues/83)) ([b38da7c](https://github.com/modelon-community/impact-client-python/commit/b38da7c6be20d4e32c7045aa81ec9ee24568e57e))

# [1.1.0-beta.15](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.14...v1.1.0-beta.15) (2021-02-08)


### Bug Fixes

* change docs to match current signature of client.upload_workspace ([88b69c8](https://github.com/modelon-community/impact-client-python/commit/88b69c823c9e8857047355124dba5a00d8f4928d))

# [1.1.0-beta.14](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.13...v1.1.0-beta.14) (2021-02-05)


### Bug Fixes

* add _sal_custom_func to cloned workspace ([0389de5](https://github.com/modelon-community/impact-client-python/commit/0389de536b60a140291e19c8e9c2ab566b5b9d9c))

# [1.1.0-beta.13](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.12...v1.1.0-beta.13) (2021-02-05)


### Bug Fixes

* __repr__ function does not throw attribute error ([083e195](https://github.com/modelon-community/impact-client-python/commit/083e1955c161cdf60d86c7ae65941e3bca8b0840))
* added failure status for experiment and way to get errors ([368bcfe](https://github.com/modelon-community/impact-client-python/commit/368bcfec8920d65b18bc573636392657300a7da4))


### Features

* run_info attributes returs documented class objects, info ([f46b5ab](https://github.com/modelon-community/impact-client-python/commit/f46b5abcf43bd032b5b5592fff9cf2011e447e3e))

# [1.1.0-beta.12](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.11...v1.1.0-beta.12) (2021-02-04)


### Features

* Added support for fetching fmus executed for a case ([#80](https://github.com/modelon-community/impact-client-python/issues/80)) ([9034ba8](https://github.com/modelon-community/impact-client-python/commit/9034ba832f734ab378dc1840f946f93000471f51))

# [1.1.0-beta.11](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.10...v1.1.0-beta.11) (2021-01-29)


### Bug Fixes

* Remove trailing commas when single values are given in Choices o… ([#79](https://github.com/modelon-community/impact-client-python/issues/79)) ([b1bb184](https://github.com/modelon-community/impact-client-python/commit/b1bb184463f3e537001966b7eea72b4b491a47e0))

# [1.1.0-beta.10](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.9...v1.1.0-beta.10) (2021-01-25)


### Bug Fixes

* Added docs ([fb96bcd](https://github.com/modelon-community/impact-client-python/commit/fb96bcd2bbccb73f5966f6ff3e5b5d454902b5d7))

# [1.1.0-beta.9](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.8...v1.1.0-beta.9) (2021-01-25)


### Bug Fixes

* Removed kwargs argument from docs as we only need to support 'qualified' variable names ([5cc63e3](https://github.com/modelon-community/impact-client-python/commit/5cc63e30b921a01770eff8bd354faf2bd4f1b874))

# [1.1.0-beta.8](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.7...v1.1.0-beta.8) (2021-01-19)


### Features

* Added support for modelica_class name based workflows ([0106196](https://github.com/modelon-community/impact-client-python/commit/01061960c6f63e421ee1f533e87f6e9c11f054d5))

# [1.1.0-beta.7](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.6...v1.1.0-beta.7) (2021-01-19)


### Features

* Added checks to use cached FMU if available ([4fcb616](https://github.com/modelon-community/impact-client-python/commit/4fcb6164667269c01c74339b05ec90923906487f))

# [1.1.0-beta.6](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.5...v1.1.0-beta.6) (2021-01-11)


### Bug Fixes

* Added documentation for setting log level ([1850d22](https://github.com/modelon-community/impact-client-python/commit/1850d22bc741f7beff680f62871a798fafbbf69e))
* Corrected the upload_workspace api ([16e9cc8](https://github.com/modelon-community/impact-client-python/commit/16e9cc84495f69c4491af406b7cbe8fc8125b20b))


### Features

* Added support for download result artifact ([e6b8108](https://github.com/modelon-community/impact-client-python/commit/e6b81083fd00207aca2d979b853868880ab81dc2))

# [1.1.0-beta.5](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.4...v1.1.0-beta.5) (2021-01-08)


### Bug Fixes

* Added semantic versioning to the requirements. This was causing failure to build the docs for modelon.impact.client.client module. ([0b11416](https://github.com/modelon-community/impact-client-python/commit/0b114167aa8f9fcfbec0638ca4fa5f7a654087e5))


### Features

* Added support for choices operator ([3a2cfd0](https://github.com/modelon-community/impact-client-python/commit/3a2cfd0ab5f096bd1a2578958aad3cf3abb147eb))

# [1.1.0-beta.4](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.3...v1.1.0-beta.4) (2020-10-23)


### Features

* Possibility to add extensions to experiment ([0c4c2d8](https://github.com/modelon-community/impact-client-python/commit/0c4c2d814be80008a6762bd6e2def140be866725))

# [1.1.0-beta.3](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.2...v1.1.0-beta.3) (2020-10-22)


### Bug Fixes

* Striping quotes from suggested filename ([f735b50](https://github.com/modelon-community/impact-client-python/commit/f735b5058cbcc62e5deec640606b67cc3f0d88e9))

# [1.1.0-beta.2](https://github.com/modelon-community/impact-client-python/compare/v1.1.0-beta.1...v1.1.0-beta.2) (2020-10-22)


### Features

* Using the case trajectory api to fetch case trajectories ([8d16708](https://github.com/modelon-community/impact-client-python/commit/8d167084dd4d58f419f55318509f7a170ab5474e))

# [1.1.0-beta.1](https://github.com/modelon-community/impact-client-python/compare/v1.0.0...v1.1.0-beta.1) (2020-10-14)


### Bug Fixes

* Added missing raises and return to documentation ([594eefb](https://github.com/modelon-community/impact-client-python/commit/594eefb4957e51623cf467c59702969086fafdae))
* Adding Docstrings and minor fixes ([fe87659](https://github.com/modelon-community/impact-client-python/commit/fe876598d28623dd80ae2165920a548506fdd45c))
* Adding read the docs specifics ([ec2fd03](https://github.com/modelon-community/impact-client-python/commit/ec2fd03fbc114ce4cfb86f9fdafacfdcf140e528))
* allow integers in custom function parameters ([f23ddf4](https://github.com/modelon-community/impact-client-python/commit/f23ddf4583264640b661888f3f79ce6cf9739c3f))
* Allowing options/specs to be given as a dict or options/specs class instance ([9b3bf83](https://github.com/modelon-community/impact-client-python/commit/9b3bf83a16843fedfa7e9d7d1f8f322375eb2879))
* Avoid users to hard-code api keys ([85d0a63](https://github.com/modelon-community/impact-client-python/commit/85d0a6362d8c0726fb192b2a1583c7070814f08f))
* cases,case --> get_cases,get_case ([d0895a3](https://github.com/modelon-community/impact-client-python/commit/d0895a3bad3c39653cc533ea41632d57cc5e75f6))
* change wording on refreshing api keys ([d4f229f](https://github.com/modelon-community/impact-client-python/commit/d4f229f5418592b2b32f747dc9cc6fc8f5ddcc21))
* changed imports to be python 3.6 compatible ([ebbbf52](https://github.com/modelon-community/impact-client-python/commit/ebbbf524af365a56f263a349caebbb73927691e9))
* Consistent naming of functions ([fb0cee0](https://github.com/modelon-community/impact-client-python/commit/fb0cee03cf95aa718526fe66020485b1bcb0b0b9))
* correct artifactory URL ([b0f5615](https://github.com/modelon-community/impact-client-python/commit/b0f56158827d7ae4429675674fdc0cbd3589f866))
* correct artifactory URL ([4b4195d](https://github.com/modelon-community/impact-client-python/commit/4b4195d6645db9ebfca740e70d144c379efa5d60))
* Corrected the compilation response from json to plain/text ([69743b4](https://github.com/modelon-community/impact-client-python/commit/69743b4bf437a3e374a047d0e3e0c78711721fdd))
* Corrected the default compiler log level to 'warning' ([1b53a4f](https://github.com/modelon-community/impact-client-python/commit/1b53a4fce11a7a7d25b3fe319f60d681d2f1c01c))
* Corrected the response json property name returned for endpoint '/workspaces' ([f1f881b](https://github.com/modelon-community/impact-client-python/commit/f1f881bf9a710e8a4e28d9e513e5f5d16e83f542))
* Corrected the to_dict to be method rather than a property ([15297d2](https://github.com/modelon-community/impact-client-python/commit/15297d2cf24e56a98c373fb87061774dca012186))
* Correcting the compilation/simulation status checks. ([d27d1c3](https://github.com/modelon-community/impact-client-python/commit/d27d1c323eca39f135289c580cb113da5beab4fc))
* delete invalid api keys to let user reenter new ones ([#61](https://github.com/modelon-community/impact-client-python/issues/61)) ([f1c71af](https://github.com/modelon-community/impact-client-python/commit/f1c71afd31006628768d08dff77a0e4cd6c72fa5))
* do not give NoResponseFetchVersionError for SSL error ([3b842a9](https://github.com/modelon-community/impact-client-python/commit/3b842a93796417b1485519269f8f574a2de29c70))
* do not save key if asking for it interactively, it might be invalid ([b8cef20](https://github.com/modelon-community/impact-client-python/commit/b8cef20c5e45308a24f795925453809c67ec1eea))
* error fix ([65c4884](https://github.com/modelon-community/impact-client-python/commit/65c4884905f39abd005ba9cbcdd4f75a6c8d1bfe))
* example doc code should be closer to being executable now ([1506fd2](https://github.com/modelon-community/impact-client-python/commit/1506fd20cea85c1053cbf980ae925681ba5ad40e))
* ExecutionOption -> ExecutionOptions ([dcad9a6](https://github.com/modelon-community/impact-client-python/commit/dcad9a6521abadef20d1f334b139902cb6f8b4d2))
* Feedback fixes ([88d59e1](https://github.com/modelon-community/impact-client-python/commit/88d59e10ffccd943acb1ab015d0662bce3276cb1))
* fix bad kerning in svg file ([fe85eb6](https://github.com/modelon-community/impact-client-python/commit/fe85eb6c94f7e47eb2cd98c3df9755c04c9ef70e))
* Fixed a typo ([4783eb2](https://github.com/modelon-community/impact-client-python/commit/4783eb2f9f47957a03f9767cd7a2a0f0877936a6))
* Formatting and lint fixes ([4d98783](https://github.com/modelon-community/impact-client-python/commit/4d98783cdd8c1bd06471b94d203241b4bd072b62))
* Grammar/font fixes ([7ddd2bd](https://github.com/modelon-community/impact-client-python/commit/7ddd2bde116db4167ac995b77661a2cc3fc16dec))
* Inheriting mapping class for ExecutionOptions ([e934d92](https://github.com/modelon-community/impact-client-python/commit/e934d92dbe16ad9f418d7ce23b233a5a7a8fc6c1))
* less confusing __repr__ for workspace ([fb42587](https://github.com/modelon-community/impact-client-python/commit/fb4258797df9f0b25dac8c420b1abc320f49fd9a))
* Lint fixes ([2c4a7f4](https://github.com/modelon-community/impact-client-python/commit/2c4a7f443286da683e81222717fc6db36ab9402c))
* making release.sh executable ([71cbac2](https://github.com/modelon-community/impact-client-python/commit/71cbac272d9ba160bd9f79763e90670e4b802d00))
* Moving info to constructor ([e31b589](https://github.com/modelon-community/impact-client-python/commit/e31b589c45f0e432ee16b9c46635bafca41ca7ba))
* Moving info to model_exe constructor ([b00eeba](https://github.com/modelon-community/impact-client-python/commit/b00eeba710ac6f05063e32962bfb464c48712a8f))
* mypy and formatting corrections ([478b06b](https://github.com/modelon-community/impact-client-python/commit/478b06b2b36ec7e9c38347a24cdda1dc23e0a28f))
* performance improvement, do not call cases unless neccessary ([0f382db](https://github.com/modelon-community/impact-client-python/commit/0f382dbde5755b5c10e4ee9d7a243ff6e5228f47))
* Performance improvements - Raising exceptions instead of waiting for operation completion when calling compilation/simulation methods/properties ([5834241](https://github.com/modelon-community/impact-client-python/commit/58342416dd6e3d4947b7bcbe3f51bc4921b294b1))
* pretty print the log ([e277c68](https://github.com/modelon-community/impact-client-python/commit/e277c684c9a8280d9ec96d2040d7a3d55184f0c6))
* Python 3.6 compatibility fixes ([048158f](https://github.com/modelon-community/impact-client-python/commit/048158f5cf3d21134e67b78b54500529abfb3735))
* Remove dead code ([ac5cfec](https://github.com/modelon-community/impact-client-python/commit/ac5cfecd19044af0cb2e97a546b8a682d0ad81c9))
* Removed an unwanted check from wait() function ([f91c5e0](https://github.com/modelon-community/impact-client-python/commit/f91c5e0d4512d7d1b662e1ce089735f483eb7e6f))
* removing test not running on module ([472a917](https://github.com/modelon-community/impact-client-python/commit/472a917a34a59275093de6c7bb60b05f33aa75d2))
* Removing the pandas dependency due to performance hits ([50fca3a](https://github.com/modelon-community/impact-client-python/commit/50fca3aae4cbf6ccc3e33d1979ef8d58244d0f61))
* Removing the settable parameter call from the assert ([bd011a2](https://github.com/modelon-community/impact-client-python/commit/bd011a2fc470c52177b05e737a2f278691a53f08))
* Renamed experiment_definition -> experiment_definition ([0879358](https://github.com/modelon-community/impact-client-python/commit/08793586da5bd54f65b13cdc5ee62de307c66bed))
* Renamed options to values in execution options ([7ef6745](https://github.com/modelon-community/impact-client-python/commit/7ef6745f4c6a70e24d152838ad73be3d59844065))
* Renaming import_library to upload_model_library ([7705160](https://github.com/modelon-community/impact-client-python/commit/7705160689b97f5a82c98c58b8f50d3ce9560ec6))
* save api key even if .impact already exists ([a3fe58e](https://github.com/modelon-community/impact-client-python/commit/a3fe58e53c41f22788be4d8eabe6e43c0fd4545b))
* Seperate methods for getting and printing log ([c600364](https://github.com/modelon-community/impact-client-python/commit/c6003640bf65d91d0288544fb042ef2cb7dced25))
* Seperating the operations and entities module ([e953cf0](https://github.com/modelon-community/impact-client-python/commit/e953cf022a264ca887e0e8f8f605212554f455db))
* Simplifying the code for engineers ([74e3bdf](https://github.com/modelon-community/impact-client-python/commit/74e3bdf106fccd34b3642762a81ce62b4447e7ea))
* Upadted the supported api version number ([cc2540e](https://github.com/modelon-community/impact-client-python/commit/cc2540e916784049ac17eae1f526be1c64c12d09))
* update tests ([0f6901b](https://github.com/modelon-community/impact-client-python/commit/0f6901bfa3b7b327a6ce88e7713222aedaa556c6))
* Updated modifers to be a dict ([7adb322](https://github.com/modelon-community/impact-client-python/commit/7adb3225516fc950c0c855d003155c6457f99dde))
* Updated Readme and pyproject.toml ([272debf](https://github.com/modelon-community/impact-client-python/commit/272debf1c498e89b6c469b0244fd123b1fe1e52f))
* Updated the defaults for get_trajectories ([f77b7e4](https://github.com/modelon-community/impact-client-python/commit/f77b7e473a15376e588f7744768b45fc5c2c57d2))
* using api tokens instead of usename password for jenkins ([76ee2a2](https://github.com/modelon-community/impact-client-python/commit/76ee2a2bbcbb97c4d3289d2e5e5e4c261a9babf1))
* using correct body field for the secret key ([0d5f306](https://github.com/modelon-community/impact-client-python/commit/0d5f306ae14c664577964840feb99422bfc43e63))
* workaround for performance issues on Windows ([ae3eb5b](https://github.com/modelon-community/impact-client-python/commit/ae3eb5bc4609240420e2450452c64e13b070325d))


### Features

* Add possibility to download FMU ([5e597f0](https://github.com/modelon-community/impact-client-python/commit/5e597f01bcee76b71f54b0c720cc000c37f89da7))
* Added possibility to set parameter modifers as a part of experiment definition instead of using legacy routes ([9802d84](https://github.com/modelon-community/impact-client-python/commit/9802d84c6b116c5eddfd53462f630ab0869672f6))
* Added semantic version checks for API ([94fed15](https://github.com/modelon-community/impact-client-python/commit/94fed15d84313d1471c038ae91d411da5d3d9271))
* Adding functions for the workspace and model class entities ([63cb71b](https://github.com/modelon-community/impact-client-python/commit/63cb71b56e28d171f245ac01d95ecb7add48cf9f))
* default behaviour for option input to SimpleExperiment ([3bdb899](https://github.com/modelon-community/impact-client-python/commit/3bdb8998c7999b0057270de177a274b1c56a56ad))
* initial repository setup ([1630038](https://github.com/modelon-community/impact-client-python/commit/16300382033c76679adedfefeff9c6de068446dd))
* integrating custom function entity ([97951b7](https://github.com/modelon-community/impact-client-python/commit/97951b7aace16eaa3deb419f232b9264410cf976))
* possible to specify client inputs through env variables ([e0f6bfe](https://github.com/modelon-community/impact-client-python/commit/e0f6bfef58e907c91e7143d6aa6bdc80cba26846))

# 1.0.0 (2020-09-28)


### Features

* First release of modelon-impact-client ([6aa3720](https://github.com/modelon-community/impact-client-python/commit/6aa3720b78f2595547d0aa89953739da3ba2d9bf))

# [1.0.0-beta.50](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.49...v1.0.0-beta.50) (2020-09-28)


### Bug Fixes

* delete invalid api keys to let user reenter new ones ([#61](https://github.com/modelon-community/impact-client-python/issues/61)) ([f1c71af](https://github.com/modelon-community/impact-client-python/commit/f1c71afd31006628768d08dff77a0e4cd6c72fa5))

# [1.0.0-beta.49](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.48...v1.0.0-beta.49) (2020-09-28)


### Bug Fixes

* Avoid users to hard-code api keys ([85d0a63](https://github.com/modelon-community/impact-client-python/commit/85d0a6362d8c0726fb192b2a1583c7070814f08f))

# [1.0.0-beta.48](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.47...v1.0.0-beta.48) (2020-09-25)


### Bug Fixes

* Grammar/font fixes ([7ddd2bd](https://github.com/modelon-community/impact-client-python/commit/7ddd2bde116db4167ac995b77661a2cc3fc16dec))

# [1.0.0-beta.47](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.46...v1.0.0-beta.47) (2020-09-25)


### Bug Fixes

* fix bad kerning in svg file ([fe85eb6](https://github.com/modelon-community/impact-client-python/commit/fe85eb6c94f7e47eb2cd98c3df9755c04c9ef70e))

# [1.0.0-beta.46](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.45...v1.0.0-beta.46) (2020-09-23)


### Bug Fixes

* Updated Readme and pyproject.toml ([272debf](https://github.com/modelon-community/impact-client-python/commit/272debf1c498e89b6c469b0244fd123b1fe1e52f))

# [1.0.0-beta.45](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.44...v1.0.0-beta.45) (2020-09-23)


### Bug Fixes

* using api tokens instead of usename password for jenkins ([76ee2a2](https://github.com/modelon-community/impact-client-python/commit/76ee2a2bbcbb97c4d3289d2e5e5e4c261a9babf1))

# [1.0.0-beta.44](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.43...v1.0.0-beta.44) (2020-09-23)


### Bug Fixes

* Adding read the docs specifics ([ec2fd03](https://github.com/modelon-community/impact-client-python/commit/ec2fd03fbc114ce4cfb86f9fdafacfdcf140e528))
* error fix ([65c4884](https://github.com/modelon-community/impact-client-python/commit/65c4884905f39abd005ba9cbcdd4f75a6c8d1bfe))

# [1.0.0-beta.43](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.42...v1.0.0-beta.43) (2020-09-23)


### Bug Fixes

* Inheriting mapping class for ExecutionOptions ([e934d92](https://github.com/modelon-community/impact-client-python/commit/e934d92dbe16ad9f418d7ce23b233a5a7a8fc6c1))

# [1.0.0-beta.42](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.41...v1.0.0-beta.42) (2020-09-22)


### Bug Fixes

* Renaming import_library to upload_model_library ([7705160](https://github.com/modelon-community/impact-client-python/commit/7705160689b97f5a82c98c58b8f50d3ce9560ec6))

# [1.0.0-beta.41](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.40...v1.0.0-beta.41) (2020-09-17)


### Features

* possible to specify client inputs through env variables ([e0f6bfe](https://github.com/modelon-community/impact-client-python/commit/e0f6bfef58e907c91e7143d6aa6bdc80cba26846))

# [1.0.0-beta.40](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.39...v1.0.0-beta.40) (2020-09-17)


### Bug Fixes

* Simplifying the code for engineers ([74e3bdf](https://github.com/modelon-community/impact-client-python/commit/74e3bdf106fccd34b3642762a81ce62b4447e7ea))

# [1.0.0-beta.39](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.38...v1.0.0-beta.39) (2020-09-17)


### Bug Fixes

* cases,case --> get_cases,get_case ([d0895a3](https://github.com/modelon-community/impact-client-python/commit/d0895a3bad3c39653cc533ea41632d57cc5e75f6))

# [1.0.0-beta.38](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.37...v1.0.0-beta.38) (2020-09-15)


### Bug Fixes

* Renamed experiment_definition -> experiment_definition ([0879358](https://github.com/modelon-community/impact-client-python/commit/08793586da5bd54f65b13cdc5ee62de307c66bed))

# [1.0.0-beta.37](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.36...v1.0.0-beta.37) (2020-09-14)


### Bug Fixes

* allow integers in custom function parameters ([f23ddf4](https://github.com/modelon-community/impact-client-python/commit/f23ddf4583264640b661888f3f79ce6cf9739c3f))

# [1.0.0-beta.36](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.35...v1.0.0-beta.36) (2020-09-14)


### Bug Fixes

* Corrected the default compiler log level to 'warning' ([1b53a4f](https://github.com/modelon-community/impact-client-python/commit/1b53a4fce11a7a7d25b3fe319f60d681d2f1c01c))

# [1.0.0-beta.35](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.34...v1.0.0-beta.35) (2020-09-07)


### Bug Fixes

* Moving info to model_exe constructor ([b00eeba](https://github.com/modelon-community/impact-client-python/commit/b00eeba710ac6f05063e32962bfb464c48712a8f))

# [1.0.0-beta.34](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.33...v1.0.0-beta.34) (2020-09-07)


### Features

* default behaviour for option input to SimpleExperiment ([3bdb899](https://github.com/modelon-community/impact-client-python/commit/3bdb8998c7999b0057270de177a274b1c56a56ad))

# [1.0.0-beta.33](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.32...v1.0.0-beta.33) (2020-09-07)


### Bug Fixes

* performance improvement, do not call cases unless neccessary ([0f382db](https://github.com/modelon-community/impact-client-python/commit/0f382dbde5755b5c10e4ee9d7a243ff6e5228f47))

# [1.0.0-beta.32](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.31...v1.0.0-beta.32) (2020-09-07)


### Bug Fixes

* Moving info to constructor ([e31b589](https://github.com/modelon-community/impact-client-python/commit/e31b589c45f0e432ee16b9c46635bafca41ca7ba))

# [1.0.0-beta.31](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.30...v1.0.0-beta.31) (2020-09-07)


### Bug Fixes

* Updated modifers to be a dict ([7adb322](https://github.com/modelon-community/impact-client-python/commit/7adb3225516fc950c0c855d003155c6457f99dde))

# [1.0.0-beta.30](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.29...v1.0.0-beta.30) (2020-09-07)


### Bug Fixes

* Allowing options/specs to be given as a dict or options/specs class instance ([9b3bf83](https://github.com/modelon-community/impact-client-python/commit/9b3bf83a16843fedfa7e9d7d1f8f322375eb2879))

# [1.0.0-beta.29](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.28...v1.0.0-beta.29) (2020-09-07)


### Bug Fixes

* do not give NoResponseFetchVersionError for SSL error ([3b842a9](https://github.com/modelon-community/impact-client-python/commit/3b842a93796417b1485519269f8f574a2de29c70))

# [1.0.0-beta.28](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.27...v1.0.0-beta.28) (2020-09-07)


### Bug Fixes

* change wording on refreshing api keys ([d4f229f](https://github.com/modelon-community/impact-client-python/commit/d4f229f5418592b2b32f747dc9cc6fc8f5ddcc21))

# [1.0.0-beta.27](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.26...v1.0.0-beta.27) (2020-09-07)


### Features

* Add possibility to download FMU ([5e597f0](https://github.com/modelon-community/impact-client-python/commit/5e597f01bcee76b71f54b0c720cc000c37f89da7))

# [1.0.0-beta.26](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.25...v1.0.0-beta.26) (2020-09-06)


### Bug Fixes

* example doc code should be closer to being executable now ([1506fd2](https://github.com/modelon-community/impact-client-python/commit/1506fd20cea85c1053cbf980ae925681ba5ad40e))

# [1.0.0-beta.25](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.24...v1.0.0-beta.25) (2020-09-06)


### Bug Fixes

* Removing the settable parameter call from the assert ([bd011a2](https://github.com/modelon-community/impact-client-python/commit/bd011a2fc470c52177b05e737a2f278691a53f08))

# [1.0.0-beta.24](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.23...v1.0.0-beta.24) (2020-09-04)


### Bug Fixes

* ExecutionOption -> ExecutionOptions ([dcad9a6](https://github.com/modelon-community/impact-client-python/commit/dcad9a6521abadef20d1f334b139902cb6f8b4d2))
* pretty print the log ([e277c68](https://github.com/modelon-community/impact-client-python/commit/e277c684c9a8280d9ec96d2040d7a3d55184f0c6))
* Remove dead code ([ac5cfec](https://github.com/modelon-community/impact-client-python/commit/ac5cfecd19044af0cb2e97a546b8a682d0ad81c9))
* Renamed options to values in execution options ([7ef6745](https://github.com/modelon-community/impact-client-python/commit/7ef6745f4c6a70e24d152838ad73be3d59844065))
* Seperate methods for getting and printing log ([c600364](https://github.com/modelon-community/impact-client-python/commit/c6003640bf65d91d0288544fb042ef2cb7dced25))

# [1.0.0-beta.23](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.22...v1.0.0-beta.23) (2020-09-03)


### Bug Fixes

* Added missing raises and return to documentation ([594eefb](https://github.com/modelon-community/impact-client-python/commit/594eefb4957e51623cf467c59702969086fafdae))

# [1.0.0-beta.22](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.21...v1.0.0-beta.22) (2020-09-02)


### Bug Fixes

* Python 3.6 compatibility fixes ([048158f](https://github.com/modelon-community/impact-client-python/commit/048158f5cf3d21134e67b78b54500529abfb3735))

# [1.0.0-beta.21](https://github.com/modelon-community/impact-client-python/compare/v1.0.0-beta.20...v1.0.0-beta.21) (2020-09-02)


### Bug Fixes

* Adding Docstrings and minor fixes ([fe87659](https://github.com/modelon-community/impact-client-python/commit/fe876598d28623dd80ae2165920a548506fdd45c))
* Lint fixes ([2c4a7f4](https://github.com/modelon-community/impact-client-python/commit/2c4a7f443286da683e81222717fc6db36ab9402c))

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
