#!/usr/bin/env bash
PIDS=`ps -fea | grep covid_bot.py | grep -v grep | awk '{ print $2" "$3 }'`
RUNCMD=`crontab -l | grep covid_bot.sh | sed 's/@reboot //g'`
if [ "$PIDS"] ; then
  echo "Killing "$PIDS
  kill -9 $PIDS
  $RUNCMD
else
  echo "Not running"
fi
