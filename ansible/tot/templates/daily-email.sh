#!/bin/sh

. ./env_vars

/home/tot/virt/bin/python /home/tot/src/tot/manage.py send_email >> /home/tot/logs/daily-email-`date +%Y-%m-%d`.log 2>&1
