from setuptools import setup, find_packages
from hhat_lang import __version__


readme = open("README.md", "r").read()

requirements = [f.strip('\n') for f in open("requirements.txt", "r").readlines()]

setup(
    name="H-hat",
    author="Eduardo Maschio",
    python_requires=">=3.8",
    description="H-hat: a high level quantum programming language.",
    long_description=readme,
    include_package_data=True,
    packages=find_packages(include=["hhat_lang", "hhat_lang.*"]),
    install_requires=requirements,
    version=__version__
)
