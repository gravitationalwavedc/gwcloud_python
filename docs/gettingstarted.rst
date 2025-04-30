Getting started with gwcloud-python
===================================

Installation
------------

You will require Python 3.7+ to be able to use gwcloud-python. The recommended way to install gwcloud-python is with pip:

::

    pip install gwcloud-python


.. _api-token-label:

Getting Access
--------------
Anonymous Access
^^^^^^^^^^^^^^^^
`gwcloud-python` allows anonymous access that is read-only for public data. This can be useful for people who are interested only in searching the database, viewing information, and downloading job results for public jobs.


Authenticated Access
^^^^^^^^^^^^^^^^^^^^
In order to be able to use the `gwcloud-python` package for accessing proprietary data or submitting new jobs, you will need LIGO credentials or a GWCloud account. You will also need an API Token associated with that account.
You can use your GWCloud or LIGO account details on the GWCloud `login page <https://gwcloud.org.au/sso/login/>`_.


If you don't have an existing GWCloud account, `register here <https://gwcloud.org.au/sso/signup/>`_.


Using your GWCloud or LIGO account, you can generate an `API token <https://gwcloud.org.au/api-token/>`_.
You should be greeted with a page which has a "Create Token" button. If you click on this, a new, unique API token will be generated.


An API token operates as your credentials, replacing your username and password when using the API. Click "Copy" to copy the token to your clipboard.
You are also able to revoke your token at any point by clicking the "Revoke Token" button, at which point the token will cease to function.
You must not share it with anybody and should revoke and recreate it if somebody else obtains it.
