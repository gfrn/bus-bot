[![CI](https://github.com/gfrn/bus-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/gfrn/bus-bot/actions/workflows/ci.yml)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Bus Bot

Slack bot for obtaining Oxfordshire bus information

## Configuration

- *SQL_DATABASE_URL* - SQL database URL. For example: `postgresql+psycopg://bus_bot_admin:test_pass@127.0.0.1:5432/bus_bot`
- *SLACK_BOT_TOKEN* - Slack bot token
- *SLACK_APP_TOKEN* - Slack app token

## Running

- Start database with `podman-compose -f docker-compose.yml up`
- Set environment variables
- Run bot with `python3 -m bus_bot`

## TODO

- [ ] Enable HTTP mode
- [ ] Add buttons to delete alerts (requires HTTP mode)
- [ ] Use modal for creating alerts (requires HTTP mode)
- [ ] Allow user to only trigger alerts on certain weekdays
- [ ] Alert user if bus is not being tracked
- [ ] Create script to parse ATCO/NAPTAN bus stop listing from CSV file
- [ ] Create tests
