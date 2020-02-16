from setuptools import setup, find_packages


setup(
    name="cdump",
    version="0.0.1",
    packages=find_packages(),
    scripts=['scripts/cdump'],
    python_requires='>=3.7.0',
    install_requires=[
        line for line in open('requirements.txt', 'r').readlines()
        if line and not line.startswith('-')
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
