from setuptools import setup, find_packages


requires = [
    'tornado',
    'tornado-sqlalchemy',
    'psycopg2',
    'passlib'
]

tests_require = []

dev_requires = [
    'ipython',
    'requests'
]

setup(
    name='tornado_todo',
    version='0.0',
    description='tornado_todo',
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Tornado',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Nicholas Hunt-Walker',
    author_email='nhuntwalker@gmail.com',
    url='',
    keywords='web tornado',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
        'dev': dev_requires
    },
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'serve_app = tornado_todo:main',
            'initdb = tornado_todo.initializedb:main'
        ],
    },
)
