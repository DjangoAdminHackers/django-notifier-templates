"""
    NotifierActions is a mixin for any ModelAdmin class where you also use django-admin-row-actions
    Currently all it does is simply include any defined notified actions to the row actions
    See: https://github.com/DjangoAdminHackers/django-admin-row-actions
    or: https://pypi.python.org/pypi?%3Aaction=pkg_edit&name=django-admin-row-actions
"""


class NotifierActions(object):

    def get_row_actions(self, obj):
        row_actions = super(NotifierActions, self).get_row_actions(obj)
        notifier_actions = obj._get_notifier_actions_list()
        if notifier_actions:
            notifier_actions[0]['divided'] = True
            row_actions += notifier_actions
        return row_actions