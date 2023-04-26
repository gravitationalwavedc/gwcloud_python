Importing and Authenticating
============================


Any script you can write involving running jobs or accessing proprietary/embargoed data will require you to be authenticated with the GWCloud service first. If you have not yet obtained an API token to authenticate with, read the :ref:`Getting Access <api-token-label>` section first.

::

    from gwcloud_python import GWCloud

    gwc = GWCloud(token='my_unique_gwcloud_api_token')

    # gwc is a full access instance

An instance of the GWCloud class initialised with your token will provide an interface to the GWCloud service, enabling you to manipulate jobs and their results as you might with the GWCloud UI.
Remember not to share this token with others!

It is possible to use the GWCloud API anonymously. This will provide a read-only view of the public data of GWCloud. You will not be able to run any jobs or access any proprietary or embargoed data. To do this, you can omit the token when you instantiate GWCloud.

::

    from gwcloud_python import GWCloud

    gwc = GWCloud()

    # gwc is now a read only instance