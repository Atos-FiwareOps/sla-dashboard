#!/usr/bin/env bash
#
# To be executed from project root dir.
. ~/virtualenvs/sla-dashboard/bin/activate
./manage.py runserver 0.0.0.0:8000
