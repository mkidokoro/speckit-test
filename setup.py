from setuptools import setup, find_packages

setup(
    name='alert_notification_system',
    version='0.1.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'alert-notification=main:main'
        ]
    }
)
