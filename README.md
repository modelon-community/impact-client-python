# Modelon-impact-client
Client library for easy scripting against Modelon Impact

## Installation

For installation instructions and requirements, please refer to the [documentation](https://modelon-impact-client.readthedocs.io).


## Develop

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
