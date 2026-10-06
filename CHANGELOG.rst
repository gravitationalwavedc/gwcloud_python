Changelog
=========

3.0.0
-----

This breaking release removes ``GWFlowJob.ligo_only`` and
``EventID.is_ligo_event``, together with the ``ligo_only`` keyword accepted by
``upsert_gwflow_job`` and the ``is_ligo_event`` keywords accepted by
``create_event_id`` and ``update_event_id``. GraphQL requests no longer select
or submit ``ligoOnly`` or ``isLigoEvent``.

Callers must stop reading or supplying these fields before upgrading. Publish
this field-free client while the server still accepts omitted fields, migrate
callers to 3.0.0, and only then remove the matching server schema contract.
