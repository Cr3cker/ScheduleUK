from setuptools import setup, Extension


setup(
    ext_modules=[
        Extension(
            'db',
            ['db.cpp'],
            libraries=['sqlite3']
        )
    ]
)

