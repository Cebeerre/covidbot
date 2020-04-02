#!/bin/bash
# crontab line:
# @reboot /usr/sbin/daemonize -E BPATH="/some/bot_path" -E BTOKEN="the_bot_token" -o /some/bot_path/covid_bot.log /some/bot_path/covid_bot.sh

until $BPATH/covid_bot.py; do
	sleep 1
done
