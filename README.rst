.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/pre-commit-jenkinsfile.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/pre-commit-jenkinsfile
    .. image:: https://readthedocs.org/projects/pre-commit-jenkinsfile/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://pre-commit-jenkinsfile.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/pre-commit-jenkinsfile/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/pre-commit-jenkinsfile
    .. image:: https://img.shields.io/pypi/v/pre-commit-jenkinsfile.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/pre-commit-jenkinsfile/
    .. image:: https://img.shields.io/conda/vn/conda-forge/pre-commit-jenkinsfile.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/pre-commit-jenkinsfile
    .. image:: https://pepy.tech/badge/pre-commit-jenkinsfile/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/pre-commit-jenkinsfile


.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

======================
pre-commit-jenkinsfile
======================

    A `pre-commit`_ hook script for linting `Jenkinsfile`_ declarative pipelines.
.. _pre-commit: https://pre-commit.com/
.. _Jenkinsfile: https://www.jenkins.io/doc/book/pipeline/syntax/


Available Hook
====

lint-jenkinsfile
____

HTTP Access Options
~~~~
--jenkins_url <url>           The URL for the Jenkins server.
--jenkin_login <login>        The login for an account on the Jenkins server.
--jenkins_api_token <token>   The API token for the account on the Jenkins server.

SSH Access Options
~~~~
--jenkins_hostname <hostname>       The hostname for the Jenkins server.
--jenkins_ssh_port <port number>    The SSH port number for the Jenkins server. Default is 22.

Config File Option
~~~~
Alternatively, these settings can be specified in an INI formatted file

--config <file path>    An absolute or relative file path.

Config File Syntax
~~~~
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
