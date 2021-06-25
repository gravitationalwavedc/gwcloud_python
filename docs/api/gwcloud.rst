GWCloud class
=============

The GWCloud object class can be thought of as the link to the GWCloud service, though they are primarily used as a means by which to manipulate Bilby jobs. 
It can used for submitting a new job to the queue, obtaining the information for a single specific job, or even obtaining lists of jobs matching certain search criteria.
Indeed, :class:`~gwcloud_python.bilby_job.BilbyJob` objects also use a reference to the GWCloud class to request their own files and information.

.. automodule:: gwcloud_python.gwcloud
   :members:
   :undoc-members:
   :show-inheritance:
