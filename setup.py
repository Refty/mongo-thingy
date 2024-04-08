from setuptools import setup


def get_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="Mongo-Thingy",
    version="0.17.2",
    url="https://github.com/Refty/mongo-thingy",
    license="MIT",
    author="Guillaume Gelin",
    author_email="guillaume@refty.co",
    description=(
        "The most idiomatic and friendly-yet-powerful way to use " "MongoDB with Python"
    ),
    long_description=get_description(),
    long_description_content_type="text/markdown",
    packages=["mongo_thingy"],
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=["thingy>=0.10.0", "pymongo>=4.6.3"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
