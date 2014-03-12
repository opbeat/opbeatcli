##########
Opbeat CLI
##########

Command line client for `Opbeat <https://opbeat.com/>`_.


.. image:: https://badge.fury.io/py/opbeatcli.png
   :target: https://pypi.python.org/pypi/opbeatcli


.. image:: https://secure.travis-ci.org/opbeat/opbeatcli.png?branch=dev
   :target: http://travis-ci.org/opbeat/opbeatcli


Installation
============

Make sure you have Git and a supported version Python installed on your system.
The supported Python versions are: ``2.6.x``, ``2.7.x``, ``3.3+`` and PyPy.

.. code-block:: bash

    $ python --version


Opbeat CLI can then be installed using the standard Python package installation
method:

.. code-block:: bash

    $ pip install opbeatcli

If ``pip`` is not available, you can alternatively use ``easy_install``:

.. code-block:: bash

    $ easy_install opbeatcli

To verify successful installation of Opbeat CLI:

.. code-block:: bash

    $ opbeat --version


Usage
=====

.. code-block:: bash

    $ opbeat [common options] sub-command [sub-command options]


Common Options
--------------

These options are shared by all sub-commands.

To obtain these, please go to your app settings on opbeat.com:

======================   ======================================================
``--org-id, -o``         Organization ID
``--app-id, -a``         Application ID.
``--secret-token, -t``   Secret API authentication token.
======================   ======================================================


For more information and a complete list of the available common options,
please see the command help:

.. code-block:: bash

    $ opbeat --help


Sub-Commands
------------


``deployment``
~~~~~~~~~~~~~~

This command registers a deployment of an application to a machine with
the Opbeat API. Deployment tracking enables advanced features of the
Opbeat platform, such as version history and the ability to relate errors
with particular deployments, etc. It is meant to be run from the machine
that is being deployed to:

.. code-block:: bash

    # A basic deployment registration: Run this from your application
    # repository directory on the machine which it's been deployed to:
    $ opbeat -o ORGANISATION_ID -a APP_ID -t SECRET_TOKEN \
        deployment --component path:.

For more information and examples please see
`deployment tracking documentation <https://opbeat.com/docs/release_standard/>`_
and the command help:

.. code-block:: bash

    $ opbeat deployment --help



