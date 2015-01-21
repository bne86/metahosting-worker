from setuptools import setup, find_packages

setup(
    name="metahosting",
    version="0.0.1",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(exclude=['env', 'tests']),
    install_requires=[
        'argparse==1.2.1',
        'astroid==1.2.1',
        'docker-py==0.6.0',
        # Ming==0.5.0
        'pep8==1.4.6',
        'pika==0.9.14',
        'pymongo==2.7.2'
    ]
)
