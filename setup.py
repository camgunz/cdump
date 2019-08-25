from setuptools import setup, find_packages


setup(
    name="cdump",
    version="0.0.1",
    packages=find_packages(),
    scripts=['scripts/cdump'],

    # metadata to display on PyPI
    author="Charlie Gunyon",
    author_email="charles.gunyon@gmail.com",
    description="Tool to dump C definitions to XML",
    keywords="c",
    url="https://github.com/camgunz/cdump/",
    project_urls={
        "Source Code": "https://gitub.com/camgunz/cdump",
    },
    classifiers=[
        'License :: OSI Approved :: GPLv3'
    ]
)
