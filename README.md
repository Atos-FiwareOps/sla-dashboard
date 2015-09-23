# SLA Dashboard

The SLA Dashboard provides a web user interface to manage SLAs for several
FIWARE components. This project is part of [FIWARE](http://www.fiware.org/).

It is a Django frontend application that allows to manage the whole SLA 
lifecycle. It works in conjunction with the
[Atos SLA Manager Core](https://github.com/Atos-FiwareOps/sla-framework) 
that acts as the backend. To get information about users and components it
interacts with the Monitoring and Authentication Generic Enablers from
[FiWare](http://fiware.org/).

For any feedbacks or bug reports, please use the the github issues tool.

# Table of contents

* [Introduction](#introduction)
* [Features implemented](#features-implemented)
* [Directory structure](#directory-structure)
* [Installation](#installation)
	* [Software Requirements](#software-requirements)
	* [Installation steps](#installation-steps)
	* [Configuration](#configuration)
* [Running](#running)
	* [Running in development mode](#running-in-development-mode)
	* [Deploying in production mode](#deploying-in-production-mode)
* [Installation verification](#installation-verification)
* [User guide](#user-guide)
	* [As a service provider](#as-a-service-provider)
	* [As an end user](#as-an-end-user)
* [License](#license)


## Introduction

The SLA Dashboard allows to perform the actions exposed by the 
[Atos SLA Manager Core](https://github.com/Atos-FiwareOps/sla-framework) in a
graphical way, so the user can easily:

* Create SLA templates for exiting services in Fiware.
* Create SLA Agreements from defined templates.
* Check information about an existing SLA template.
* Check information about an existing SLA agreement.
* Visualize information about violations and breaches.

All these operations rely tightly on the user credentials and permissions inside
the Fiware's project. This information is retrieved from the Fiware's
identity manager.

In the following figure the components that intervene in the SLA dashboard 
operations are depicted.

![slasystem](docs/images/slasystem.png "SLA Manager Architecture inside Fiware")

## Features implemented

This version of the SLA Manager (v1.1) supports the new features offered in the
last version of the SLA Framework in terms of defining intervals for KPI
conditions. Thus, when defining the KPIs restrictions for a feature, a new
widget will allow the service provider to define a range of time. Then,
violations for that KPI will only be raised when the mean of these measurements
over the specified interval exceeds the defined threshold.

![userguide12](docs/images/features01.png "Time range widget")

In the current state of the tool, we restrict the interval to four values: real
time, over 6 hours, over 12 hours and over 24 hours. The "real time" option
implements the previous available operation, where violations were raised (if
needed) every time the SLA Framework got the information from the Fiware
Monitoring component.

Another implemented feature is the dynamic retrieval of the monitored data when
selecting a service. Up to now, when the service provider defined as SLA
template, the same KPIs were offered to be monitored, for all the services and
hosts. This could lead to problems when some service do not offer information
about, for example, RAM usage. Now, when selecting a service in the SLA Template
creation stage, the SLA Dashboard queries the Monitoring component for the
available KPIs that can be monitored for that particular service. If this does
not offer any monitoring data, the service provider gets properly notified.

## Directory structure

The sla-dashboard application is composed by the following directories:
* sladashboard: the app related to the application itself. The settings
    file maybe need to be modified: read below.
* slagui: the SLA Dashboard GUI project.
* slaclient: this project contains all the code needed to connect to
    SLA Manager REST interface, and the conversion from xml/json to python
    objects.
* samples: this directory contains sample files to load in the SLA Manager for
    testing.
* bin: some useful scripts


## Installation

### Software requirements

* Python 2.7.x
* Python Virtualenv (recommended).
* [SLA Manager](https://github.com/Atos-FiwareOps/sla-framework)
(Java backend) needs to be running in order to use the dashboard.

### Installation steps

The SLA Dashboard is a Django-based web application. As a recommendation, any
Python application should run in it own Virtual Environment, so it can use the
needed versions of its dependeces without interfering with other applications'
dependencies.

You can find the dependency list in the file requirements.txt. This is a Python
standard file, understandable by pip, that defines the list of packages that 
need to be installed. It allows to install the whole bunch of needed libraries
all at once.

The list of steps to get the SLA installed are the following:

1. Install virtualenv

		$ pip install virtualenv

2. Create virtualenv

		$ virtualenv $VIRTUALENV_NAME

3. Activate virtualenv

		$ . $VIRTUALENV_NAME/bin/activate

4. Change to application directories and install requirements

		($VIRTUALENV_NAME)$ cd $SLA_DASHBOARD_DIR
		($VIRTUALENV_NAME)$ pip install -r requirements.txt

5. Create needed tables for sessions, admin, etc

		($VIRTUALENV_NAME)$ python manage.py syncdb

6. You must create a super user in order to manage the users and providers:

		($VIRTUALENV_NAME)$ python manage.py createsuperuser
		Username (leave blank to use 'user'): {admin_username}
		Email address: {admin_email_address}
		Password: {admin_password}
		Password (again): {admin_password}
		Superuser created successfully.

### Configuration

The SLA Dashboard application needs a minimal configuration. Basically, the only
parameters to be set are the URL where the SLA Manager Core instance that is
going to be used can be found and the parameter that enables the debug mode.

These parameters can be found in the file sladashboard/settings.py as:

* SLA_MANAGER_URL: The URL of the SLA Manager REST interface.
* DEBUG: Please, set this to FALSE in production

## Running

The Django framework provides its own and lightweight development server. It
allows to quickly deploy the web application, without dealing with production
server configurations and use it for testing purposes. It also provides
automatic redeploying of the application when changes are performed, as well as
debugging capabilities in conjunction with other Python debugging tools.

When deploying the application in production mode several solutions exist.
Web servers like Apache or Nginx can be used in combination with other
application servers. In this document we propose an deployment environment using
Nginx, Gunicorn, Virtualenv and Supervisor on a Debian 8 machine.
Please, feel free to send us feedback about other possible configurations.

### Running in development mode

If you want to run and test quickly the SLA Dashboard application, the easiest
way is to use the embedded web server integrated in the Django framework. To do
so, after performing the previous installation and configuration instructions,
follow these steps:

1. Activate virtualenv

		$ . $VIRTUALENVS_NAME/bin/activate

2. Change to the application directory

		($VIRTUALENV_NAME)$ cd $SLA_DASHBOARD

3. Start server

		($VIRTUALENV_NAME)$ python manage.py runserver

	The default URL served by the server is 127.0.0.0:8000. In order you want to use
	a different url or port, you can indicate it in the command:

		($VIRTUALENV_NAME)$ python manage.py runserver 0.0.0.0:8001

	You can find more information about the development server in the [Django
	documentation webpage](https://docs.djangoproject.com/en/1.8/ref/django-admin/#runserver-port-or-address-port).

4. Test

		$ curl http://127.0.0.1:8000/slagui

### Deploying in production mode

As mentioned before, several deployment configurations are possible. In this
section we described how we deployed this in a production environment using
Debian 8, Nginx, Gunicorn, Supervisor and Virtualenv.

We suppose that you have performed the installation steps and you have set up a
virtual environment for the project.

We also suppose those global variables:

* $SLA_DASHBOARD_DIR: the directory the SLA Dashboard code has been placed.
* $SLA_DASHBOARD_VENV_DIR: the directory where the dedicated virtual 
environment for the SLA Dashboard resides.

Most of the scripts have are based on [Michał Karzyński](https://gist.github.com/postrational)
Gist examples on [how to set up Django on Nginx with Gunicorn and supervisor](https://gist.github.com/postrational/5747293#file-gunicorn_start-bash).

The steps are the following:

1. Install the dependences

		$ sudo pip install virtualenv
		$ sudo aptitude install nginx gunicorn supervisor

2. Create a Gunicorn start script

	This script can be placed wherever you want. In our case, we placed it in
	$SLA_DASHBOARD_DIR/bin/gunicorn_start.

		#!/bin/bash

		NAME="sladashboard"                           # Name of the application
		DJANGODIR=$SLA_DASHBOARD_DIR                  # Django project directory
		SOCKFILE=$SLA_DASHBOARD_DIR/gunicorn.sock     # we will communicate using this unix socket
		USER=root                                     # the user to run as
		GROUP=root                                    # the group to run as
		NUM_WORKERS=3                                 # how many worker processes should Gunicorn spawn
		DJANGO_SETTINGS_MODULE=sladashboard.settings  # which settings file should Django use
		DJANGO_WSGI_MODULE=sladashboard.wsgi          # WSGI module name
		
		# Activate the virtual environment
		cd $DJANGODIR
		source $SLA_DASHBOARD_VENV_DIR/bin/activate
		export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
		export PYTHONPATH=$DJANGODIR:$PYTHONPATH
		
		# Create the run directory if it doesn't exist
		RUNDIR=$(dirname $SOCKFILE)
		test -d $RUNDIR || mkdir -p $RUNDIR
		
		# Start your Django Unicorn
		# Programs meant to be run under supervisor should
		#   not daemonize themselves (do not use --daemon)
		exec $SLA_DASHBOARD_VENV_DIR/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \

		  --name $NAME \
		  --workers $NUM_WORKERS \
		  --user=$USER --group=$GROUP \
		  --bind=unix:$SOCKFILE \
		  --log-level=debug \
		  --log-file=-

3. Create the Supervisor script to start/stop the application:

	It should be placed in /etc/supervisor/conf.d/sladashboard.conf and should
	contain the following parameters:

		[program:sladashboard]
		command = $SLA_DASHBOARD_DIR/bin/gunicorn_start                   ; Command to start app
		user = root                                                       ; User to run as
		stdout_logfile = $SLA_DASHBOARD_DIR/logs/gunicorn_supervisor.log  ; Where to write log messages
		redirect_stderr = true                                            ; Save stderr in the same log
		environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8 

4. Create Nginx virtual servers

	This script should be placed in /etc/nginx/sites-available/slagui

		upstream sladashboard_app_server {
		  # fail_timeout=0 means we always retry an upstream even if it failed
		  # to return a good HTTP response (in case the Unicorn master nukes a
		  # single worker for timing out).

		  server unix:$SLA_DASHBOARD_DIR/gunicorn.sock fail_timeout=0;
		}

		server {
			listen   0.0.0.0:80;
			server_name localhost {public_ip};

			client_max_body_size 4G;

			access_log $SLA_DASHBOARD_DIR/logs/nginx-access.log;
			error_log $SLA_DASHBOARD_DIR/logs/nginx-error.log;

			location /static {
				alias   $SLA_DASHBOARD_DIR/static/;
			}

			location /media/ {
				alias   $SLA_DASHBOARD_DIR/media/;
			}

			location / {
				# an HTTP header important enough to have its own Wikipedia entry:
				#   http://en.wikipedia.org/wiki/X-Forwarded-For
				proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

				# enable this if and only if you use HTTPS, this helps Rack
				# set the proper protocol for doing redirects:
				# proxy_set_header X-Forwarded-Proto https;

				# pass the Host: header from the client right along so redirects
				# can be set properly within the Rack application
				proxy_set_header Host $http_host;

				# we don't want nginx trying to do something clever with
				# redirects, we set the Host: header above already.
				proxy_redirect off;

				# set "proxy_buffering off" *only* for Rainbows! when doing
				# Comet/long-poll stuff.  It's also safe to set if you're
				# using only serving fast clients with Unicorn + nginx.
				# Otherwise you _want_ nginx to buffer responses to slow
				# clients, really.
				# proxy_buffering off;

				# Try to serve static files from nginx, no point in making an
				# *application* server like Unicorn/Rainbows! serve static files.
				if (!-f $request_filename) {
					proxy_pass http://sladashboard_app_server;
					break;
				}
			}

			# Error pages
			error_page 500 502 503 504 /500.html;
			location = /500.html {
				root $SLA_DASHBOARD_DIR/static/;
			}
		}

5. Create a common directory for static files of all the Django applications in
the SLA Dashboard, to be easily served in production:

		$ cd $SLA_DASHBOARD_DIR
		$ . $VIRTUALENV_NAME/bin/activate
		($VIRTUALENV_NAME)$ python manage.py collectstatic

6. Start/restart the application using supervisor:

		$ sudo supervisorctl restart sladashboard

7. Add the virtual server for the SLA Dashboard application to the directory of
enabled sites and restart Nginx:

		$ sudo ln -s /etc/nginx/sites-available/slagui /etc/nginx/sites-enabled
		$ sudo systemctl restart nginx.service 

## Installation verification

To check that everything was correctly installed, run the project in development
mode, open your browser and go to the following URL:

        http://localhost:8000/slagui

If it redirects you to the FIWARE login page, it is properly configured locally.
Remember that in order to fully use it the application must be registered in
FIWARE and you must have permissions to run it.

## Configure the users and roles

The file initial_data.json has created automatically the groups CONSUMER AND
PROVIDER when you have executed "python manage.py syncdb".

You only need to create the users and the providers associated to the agreements
and to assign the correct role (CONSUME and PROVIDER).

In order to introduce them you have to connect to http://localhost:8000/admin
and add the new users (with CONSUME or PROVIDER groups).

# User guide

The SLA Dashboard allows to create templates and agreements for all kind of
components that can be monitored by Fiware's  Federation Monitoring component.
So the following applies both for services, virtual machines and hosts,
although, for simplicity, we will refer only as "services".

## As a service provider

When somebody connects to the SLA Dashboard home page, a list of existing
agreements is shown. From the service provider perspective, this page is only
informational. The real interest may be managing templates to offer a certain
quality of service level on the provided resources.

To do that, the "Templates" link should be clicked. Then, the complete list of
created templates is shown.

![userguide01](docs/images/userguide01.png "Template list")

To create a new one, the service provider have to click on the "Create
Template" check box. Then, a new panel will be presented, where a template name
and an expiration date.

![userguide02](docs/images/userguide02.png "Creating a new template")

By clicking on the "Show services" link, the service provider can check the
provided services that the template terms can apply to. This information is
retrieved from the Fiware's DCA component, that given the id of a registered
user, allows to get the information about its monitored services.

![userguide03](docs/images/userguide03.png "Assigning a service in a new template")

Once the service provider has selected a service, he can add business values to
the template by clicking in the "Add properties" button below. This allows to
define which metrics will be monitored, as well as define the different
guarantee levels for each one. This information is retrieved from the
Federation Monitoring component which, given a service, provides the list of
available metrics.

These metrics can be evaluated in real time or over a period (currently we
provide over 6, 12 and 24 hours).

![userguide04](docs/images/userguide04.png "Assigning business values in a new template")

Once the new template has been created, the list of available templates is
updated.

![userguide05](docs/images/userguide05.png "Updated template list")

And by clicking on their names, the service provider can check the details
of a particular template.

![userguide06](docs/images/userguide06.png "Template details")

## As an end user

An end user, when connecting to the SLA Dashboard home page, will be provided
with a list of his active service level agreements.

![userguide07](docs/images/userguide07.png "Agreement list")

The process to create a new agreement, begins when checking the "Create
agreement" check box. Then, a new form is shown, where the end user can set a
name for the new agreement.

Then, clicking on the "Show services" link, a new window appears, where all the
services the user is registered in are shown.

![userguide08](docs/images/userguide08.png "Selecting a service for a new SLA")

After selecting a service, the SLA Dashboard retrieves all the SLA templates
offered for that service, and shows them in a list, so the user can choose
which to apply.

When clicking on one of the available templates, all the information about it
is shown, so the end user can check the business values before creating the
agreement.

![userguide09](docs/images/userguide09.png "SLA parameters from the selected template")

Once the agreement is created, the list of agreements is updated...

![userguide10](docs/images/userguide10.png "Updated agreement list")

... and after a few minutes, the SLA Manager core begins to retrieve metrics 
and evaluate the new agreement, which state is shown in the SLA Dashboard.

![userguide11](docs/images/userguide11.png "Status update for the new SLA")

In the list of agreements the "+" icon shows a brief summary of what is
monitored in the agreement, and the status in terms of fulfillment.

![userguide12](docs/images/userguide12.png "Agreement list with summary")

When clicking in the "i" icon, a more detailed information page is shown. In
that view, all the agreement information is shown, as well as a summary of
the violations that have been raised.

![userguide13](docs/images/userguide13.png "Monitoring agreement detail (no violations)")

Moreover, a pie chart is shown when there are violations, classified by the
violated guarantee term.

![userguide14](docs/images/userguide14.png "Monitoring agreement detail (with violatiosn)")

Back in the home page, when the end user clicks is checking one of the agreement
summaries and one of the guarantee terms has been violated, a "Violations" link
is shown next to it. When clicking on this link, a new page is shown, where the
details of the violations for this business value are shown. For example, the
date and the actual monitoring value are shown for every raised violation.

![userguide15](docs/images/userguide15.png "Violations detail")

## License

Licensed under the [Apache License, Version 2.0](#http://www.apache.org/licenses/LICENSE-2.0)
