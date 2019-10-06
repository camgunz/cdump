from setuptools import setup, find_packages


setup(
    name="cdump",
    version="0.0.1",
    packages=find_packages(),
    scripts=['scripts/cdump'],
    install_requires=[
        'clang>=6.0.0.2',
        'msgpack>=0.6.1'
    ],

    # metadata to display on PyPI
    author="Charlie Gunyon",
    author_email="charles.gunyon@gmail.com",
    description="Tool to parse C definitions",
    keywords="c",
    url="https://github.com/camgunz/cdump/",
    project_urls={
        "Source Code": "https://gitub.com/camgunz/cdump",
    },
    classifiers=[
        'License :: OSI Approved :: GPLv3'
    ],
)
