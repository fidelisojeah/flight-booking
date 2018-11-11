# flight-booking
Flight Booking Application


## Installation

Make sure to have pyenv installed on your machine

Install the pyenv-virtualenv plugin by running `git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv`

Restart your terminal

intialize pyenv-virtualenv

```shell
eval "$(pyenv virtualenv-init -)"
```

### To change Python Environment Using Virtual Env

- `pyenv virtualenv {PYTHON_VERSION_NEEDED} {VIRTUAL_ENV_NAME}`
> `{PYTHON_VERSION_NEEDED}` would be the version of python you want (just the version number)
> `{VIRTUAL_ENV_NAME}` would be the name and directory for your virtual environment
e.g `pyenv virtualenv 3.6.6 env` would use python 3.6.6 in a virtual env directory named `env`

- `pyenv activate {VIRTUAL_ENV_NAME}` - `{VIRTUAL_ENV_NAME}` would be the name of your particular virtual environment specified before
> e.g `pyenv activate env`

- `pip install -r requirements.txt`
