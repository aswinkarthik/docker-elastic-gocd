# Elastic GO CD Agents

Using docker containers for dynamically increasing go-agents whenever load on Go server increases.

## Requirements

- Docker daemon ( *Use boot2docker if on OSX* )

- Set GoServerUrl, Username and Password in `config`. See for other configs.

## Usage

- Run `python src/prepare_goagent_config.py` to render config template.
- Start service with `python src/start_service.py`

## Working parts

- Service monitors go-server and if number of agents fall below THRESHOLD they create new go-agents.
- Whenever agents are in excess they throttle down.
