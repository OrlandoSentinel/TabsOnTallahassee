Deployment
==========

A complete `ansible <https://ansible.com>`_ deployment plan is provided in the ``ansible/`` directory.

It assumes a clean Ubuntu host (tested w/ 15.04) that'll be used exclusively for hosting ToT.  That said it makes a best effort to be self-contained and not do anything unnecessary system-wide, but is **untested** in a shared hosting environment.

The basics of deployment are (see ``tot/tasks/main.yml`` for detail):
    * installs necessary system-wide packages
    * creates a new user ``tot`` w/ a homedir of ``/home/tot``
    * checks out latest source to ``/home/tot/src/tot``
    * builds a virtualenv in ``/home/tot/virt/``
    * installs tot entries for uwsgi and nginx
    * writes a ``/home/tot/run-scrapers.sh`` script and installs a cron job
      that calls it at regular intervals

This means a homedir that looks something like::

    ~tot
       |
       +-- data         - directory containing uwsig sock files
       +-- logs         - uwsgi, nginx, and scraper logs
       +-- src/tot      - checkout of project
       +-- virt         - virtualenv
       +-- _data        - scraper data directory from last run
       +-- _cache       - scraper cache directory


EC2 Deployment
--------------

Configure SES
~~~~~~~~~~~~~

SES should be configured to send emails to registered users.

* Within the AWS Console select SES -> Identity Management -> Domains
* Add desired domain, console will give instructions on adding DNS entries
* After adding DNS entries domain should show up as verified, be sure to enable DKIM.

Despite verification at this point you can only send emails to verified email addresses.

While this will work for testing, it'll be necessary to use the console to make a support request to Amazon to remove this limitation.


Create RDS instance
~~~~~~~~~~~~~~~~~~~
 tested with Postgres 9.4.4

Create EC2 instance
~~~~~~~~~~~~~~~~~~~
 tested with ami-a85629c2

Set Security Groups
~~~~~~~~~~~~~~~~~~~

Suggested configuration is two groups:

* tot-web - for EC2 instance(s), open to world on port 443 for HTTPS and 22 for selected IPs
* tot-db - for DB instance(s), only open to tot-web

Create Ansible Config
~~~~~~~~~~~~~~~~~~~~~

Create an ec2/ directory with the following contents:

ec2/hosts::

    tot ansible_ssh_host=<instance ip> ansible_ssh_user=ubuntu ansible_ssh_private_key_file=ec2/tot.pem

ec2/hosts/tot.yml::

    ---
    django_environment:
        SECRET_KEY: <random string>
        DEBUG: false
        DATABASE_URL: postgis://<rds username>:<rds password>@<rds host>:5432/<rds db name>
        ADMINS: Name email@example.com, Name 2 email2@example.com
        EMAIL_HOST: email-smtp.us-east-1.amazonaws.com
        EMAIL_HOST_USER: <smtp-username>
        EMAIL_HOST_PASSWORD: <smtp-password>
        DEFAULT_FROM_EMAIL: noreply@example.com
    server_name: ""
    ssl_cert: "..."
    ssl_key: "..."


Run Ansible Playbook
~~~~~~~~~~~~~~~~~~~~

    $ ansible-playbook tot.yml -i ec2/hosts
