# http://stackoverflow.com/questions/6791911/execute-code-when-django-starts-once-only
def startup():
    from .utils import generate_all_notifier_templates
    generate_all_notifier_templates()

startup()
