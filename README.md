# Modelon-impact-client

Client library for easy scripting against Modelon Impact

## Installation

For installation instructions and requirements, please refer to the [documentation](https://modelon-impact-client.readthedocs.io).

## Develop

### Devcontainer

If you are developing with VS Code you can use the devcontainer which gives gives you a ready to use environment for development. Just click the "Reopen in Container" button after opening the project in VS Code.

#### Tips and tricks

It is possible to run the 'make' commands listed bellow using the devcontainer. It will detect being in a container and bypass Docker parts of the commands.

You can open a project with the dev-container directly without having to open and then re-load. Standing in the project directory you can run:

```
devcontainer open .
```

Note that this requires the [devcontainer-cli](https://code.visualstudio.com/docs/remote/devcontainer-cli).

You can add your own extensions to devcontainers. These extensions will be added for all devcontainers. First open your 'settings' as JSON. Then, to add for example the "GitLens" extension, put the following at the bottom of the settings:

```
    ...
    "remote.containers.defaultExtensions": ["eamodio.gitlens"]
}
```

VS Code also have a `'Install Local Extensions in 'Remote'` command, but it must be repeated for each devcontainer and everytime a devcontainer is re-built.

### Creating a shell

Modelon-impact-client is developed using a Docker container for all build tools.
You can get a shell into said container by running:

```
make shell
```

### Manage dependencies

Dependencies are managed by poetry. Add dependencies by running
`poetry add <package>`  or `poetry add <package> --dev` inside the shell

### Running tests

Tests are executed by running `make test`. You can also run `make test-watch` to get a watcher
that continuously re-runs the tests.

### Running lint

```
make lint
```

## Build

Building modelon-impact-client is done by running

```
make wheel
```

## Test

The tests for modelon-impact-client could be run by executing

```
make test
```

### VCR test

Vcrpy(https://vcrpy.readthedocs.io/en/latest/) is used to mock the http requests and
responses for some of the tests. VCR.py records all HTTP interactions that take place
in a flat file called a 'cassette'. These files could are stored in the `impact-client-python/tests/fixtures/vcr_cassettes` folder. When an API response/request body is updated on MI, these files need to be regenerated. To regenerate these file, follow the following steps:

1. Start Modelon impact cloud - https://impact.modelon.cloud.
2. Generate an MI api key and JH token and store them in secrets folder. See [Readme](.secrets/README.md) for more information.
3. Delete the cassette file you wish to regenerate from `impact-client-python/tests/fixtures/vcr_cassettes` folder.
4. The file could now be regenrated by executing

```
make regenerate-cassette
```

## Release

The modelon-impact-client build process is a fully automated using `Semantic-release`.

Automation is enabled for:

- Bumping version
- Generate changelog

This is done based on git commit semantics as described here: https://semantic-release.gitbook.io/semantic-release/

To make a new release simply run:

```
make publish
```

This command will detect what branch you are on and your git history and make a appropriate release.

Current configuration can be found in `.releaserc` and specifies that commits to branch `master` should be released and
commits to branch `beta` should be released as a `pre-release`.

This workflow make sure that no administrative time needs to be put into managing the release workflow.
