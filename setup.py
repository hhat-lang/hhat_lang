from setuptools import setup, find_packages
from hhat_lang import version

readme = open("README.md", "r").read()

requirements = open("requirements.txt", "r").readlines()

setup(
    name="H-hat",
    version='0.1.0',
    description="H-hat: a high level quantum programming language.",
    long_description=readme,
    author="Eduardo Maschio",
    packages=find_packages(include=["hhat_lang", "hhat_lang.*"]),
    install_requires=requirements,
    python_requires="==3.10.9",
    include_package_data=True,
)
