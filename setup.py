from setuptools import setup, find_packages
from hhat_lang import version


readme = open("README.md", "r").read()

requirements = open("requirements.txt", "r").readlines()

setup(
    author="Eduardo Maschio",
    python_requires=">=3.8",
    description="H-hat: a high level quantum programming language.",
    long_description=readme,
    include_package_data=True,
    name="H-hat",
    packages=find_packages(include=["hhat_lang", "hhat_lang.*"]),
    requires=requirements,
    version=version
)
