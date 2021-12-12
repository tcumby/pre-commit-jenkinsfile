.. image:: https://img.shields.io/badge/python-3.8%2B-blue
    :alt: supported python versions

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
    :alt: Security Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code Style: Black

======================
pre-commit-jenkinsfile
======================

    A `pre-commit`_ hook script for linting `Jenkinsfile`_ declarative pipelines.
      .. _pre-commit: https://pre-commit.com/
      .. _Jenkinsfile: https://www.jenkins.io/doc/book/pipeline/syntax/


Available Hook
==============

lint-jenkinsfile
________________

HTTP Access Options
~~~~~~~~~~~~~~~~~~~

--jenkins_url <url>           The URL for the Jenkins server.
--jenkin_login <login>        The login for an account on the Jenkins server.
--jenkins_api_token <token>   The API token for the account on the Jenkins server.

SSH Access Options
~~~~~~~~~~~~~~~~~~

--jenkins_hostname <hostname>     The hostname for the Jenkins server.
--jenkins_ssh_port <port>         The SSH port number for the Jenkins server. Default is 22.

Config File Option
~~~~~~~~~~~~~~~~~~
Alternatively, these settings can be specified in an INI formatted file

--config <file>                  An absolute or relative file path.

Config File Syntax
~~~~~~~~~~~~~~~~~~

The following are the allow sections and keys for the config file:

::

      [http]
      url = <url>
      login = <login>
      api_key = <key>

      [ssh]
      hostname = <hostname>
      port = <port>

Note that is only necessary to specify the keys in the **http** or **ssh** section.


Using with pre-commit
=====================
To use with pre-commit, add the following to your .pre-commit-config.yaml file:

::

    - repo: https://github.com/tcumby/pre-commit-jenkinsfile
      rev: master
      hooks:
       - id: lint-jenkinsfile
