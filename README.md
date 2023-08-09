# Sensay AI's Core backend Service

## FastAPI nano
This repo is created from the boilerplate FastAPI nano
please refer to this document about how this project 
is structure [a link](./FASTAPINANO_README.md)

## How to add new dependency
1. First of all, this project's will follow [PEP 505](https://peps.python.org/pep-0508/)
please refer to this
2. To add new dependency please add in the [pyproject.toml](./pyproject.toml) file 
   <br/><br/>2.1.1) If that dependency is essential in the production env please add that in the [project] section
   <br/><br/>2.1.2) If that dependency is only need for development env please add it
in the production env please add that in the [project.optional-dependencies]
 section
   <br/><br/>2.2) Then run the [update_deps.sh](./scripts/update_deps.sh) script to generate the [requirement.txt](./requirements.txt) and [requirement-dev.txt](./requirements-dev.txt)
```shell
./scripts/update_deps.sh
```
<br/>For the installation in local you can do the following </br>
   to install core dependencies you run:
```shell
pip install .
```
if you need dev(develop) environment (we use dev because it is a name defined in .toml file, you can use any):
```shell
pip install .[dev]
```
or this if you using zsh
```shell
pip install -e '.[dev]'
```
