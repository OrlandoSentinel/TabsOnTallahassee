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
      that calls it at [TODO]

This means a homedir that looks something like::

    ~tot
       |
       +-- data         - directory containing uwsig sock files
       +-- logs         - uwsgi, nginx, and scraper logs
       +-- src/tot      - checkout of project
       +-- virt         - virtualenv
       +-- _data        - scraper data directory from last run
       +-- _cache       - scraper cache directory


Running Ansible
---------------

TBD


Configuration
-------------

TBD
