from celery.schedules import crontab

from indico.core.celery import celery
from indico.core.db import db
from indico.util.date_time import now_utc


@celery.periodic_task(run_every=crontab(minute='0', hour='2'), plugin='sso_group_mapping')
def scheduled_group_check():
    from .plugin import WIPACSSOGroupsPlugin
    if not WIPACSSOGroupsPlugin.settings.get('enable_group_cleanup'):
        WIPACSSOGroupsPlugin.logger.warning('Local Group cleanup not enabled, skipping run')
        return
    identity_provider = WIPACSSOGroupsPlugin.settings.get('identity_provider')
    if not identity_provider:
        WIPACSSOGroupsPlugin.logger.warning('Identity provider not set, not cleaning up group')
        return
    group = WIPACSSOGroupsPlugin.settings.get('sso_group')
    if not group:
        WIPACSSOGroupsPlugin.logger.warning('Local Users Group not set, not cleaning up group')
        return

    expire_login_days = WIPACSSOGroupsPlugin.settings.get('expire_login_days')

    any_users_discarded = False
    for user in group.members.copy():
        for identity in user.identities:
            if identity.provider == identity_provider:
                last_login_dt = identity.safe_last_login_dt
                login_ago = now_utc() - last_login_dt
                if login_ago.days > expire_login_days:
                    WIPACSSOGroupsPlugin.logger.info('Removing user with identity %s '
                                                     'from local group %s, last login was '
                                                     '%d days ago', identity.identifier, group, login_ago.days)
                    group.members.discard(user)
                    any_users_discarded = True
    if any_users_discarded:
        db.session.commit()
