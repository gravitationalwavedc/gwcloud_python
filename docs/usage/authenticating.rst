Importing and Authenticating
============================

Almost any script you can write involving the GWCloud API will require authenticating with the GWCloud service first.
If you have not yet obtained an API token to authenticate with, read the :ref:`Getting Access <api-token-label>` section first.

::

    from gwcloud_python import GWCloud

    gwc = GWCloud(token='my_unique_gwcloud_api_token')

An instance of the GWCloud class initialised with your token will provide an interface to the GWCloud service, enabling you to manipulate jobs and their results as you might with the GWCloud UI.
Remember not to share this token with others!