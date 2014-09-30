from setuptools import find_packages
from setuptools import setup

setup(
    name='django-notifier-templates',
    version='0.1',
    description='django notifier templates',
    author='Andy Baker',
    install_requires=[
        'django-multi-email-field>=0.1,<1.0',
        'django-dbsettings>=0.7,<1.0',
    ],
    author_email='andy@andybak.net',
    packages=find_packages(),
    package_data={
        'notifier_templates': [
            'templates/*.html',
            'static/*',
        ]
    },
    include_package_data=True,
)
