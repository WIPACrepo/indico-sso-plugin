from indico.core import signals
from indico.util.i18n import make_bound_gettext


_ = make_bound_gettext('WIPACSSOGroups')


@signals.core.import_tasks.connect
def _import_tasks(sender, **kwargs):
    import indico_wipac_sso_groups.task  # noqa: F401
