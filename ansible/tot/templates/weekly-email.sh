#!/bin/sh

. ./env_vars

/home/tot/virt/bin/python /home/tot/src/tot/manage.py send_email --week >> /home/tot/logs/weekly-email-`date +%Y-%m-%d`.log 2>&1
