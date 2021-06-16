Authenticating with the API Token
=================================

Most scripts involving the GWCloud API will be started by using you API token to authenticate with the GWCloud service.

::

    from gwcloud_python import GWCloud

    gwc = GWCloud(token='my_unique_gwcloud_api_token')

By creating an instance of the GWCloud class with your API Token, you are able to use this instance to interact with the Bilby service.