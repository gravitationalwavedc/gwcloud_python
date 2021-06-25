Authenticating with the API Token
=================================

Most scripts involving the GWCloud API will be started by using your :ref:`API Token <api-token-label>` to authenticate with the GWCloud service.

::

    from gwcloud_python import GWCloud

    gwc = GWCloud(token='my_unique_gwcloud_api_token')

An instance of the GWCloud class initialised with your token will provide an interface to the GWCloud service, enabling you to manipulate jobs and their results as you might with the GWCloud UI.