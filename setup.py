from setuptools import setup

version = {}
with open("mgyminer/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="MGnifyMiner",
    version=version["__version__"],
    packages=["mgyminer"],
    author="Felix Langer",
    author_email="felix@ebi.ac.uk",
    description="A tool to explore the MGnify Protein Database",
    url="TODO",
    install_requires=["hmmer", "pandas"],
    license="TODO",
    entry_points={"console_scripts": ["MGnifyMiner = mgyminer.__main__:main"]},
    classifiers=[
        "License :: TODO",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
    ],
)
