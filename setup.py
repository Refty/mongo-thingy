from setuptools import setup


def get_description():
    with open("README.rst") as file:
        return file.read()


setup(
    name="Mongo-Thingy",
    version="0.12.0",
    url="https://github.com/numberly/mongo-thingy",
    license="MIT",
    author="Guillaume Gelin",
    author_email="ramnes@1000mercis.com",
    description=("The most idiomatic and friendly-yet-powerful way to use "
                 "MongoDB with Python"),
    long_description=get_description(),
    packages=["mongo_thingy"],
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=[
        "thingy>=0.8.3",
        "pymongo>=3.7"
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
