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

The same release replaces the commit-SHA history identity with the portal's
integer version number. ``upsert_gwflow_job`` accepts
``current_version_number`` instead of ``current_history_id``, GraphQL requests
send ``currentVersionNumber`` and select it in list and detail responses, and
``GWFlowJob`` exposes ``current_version_number``. Callers must migrate before
upgrading.
