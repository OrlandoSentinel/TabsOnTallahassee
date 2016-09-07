#!/bin/sh

. ./env_vars

/home/tot/virt/bin/pupa update fl people >> /home/tot/logs/people-scrape-`date +%Y-%m-%d`.log 2>&1
/home/tot/virt/bin/pupa update fl bills session=2017 >> /home/tot/logs/bills-scrape-`date +%Y-%m-%d`.log 2>&1
