from setuptools import setup, find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")
requirements = open("requirements.txt", "r").readlines()
version = open("hhat_lang/version.txt", "r").readline()


setup(
    name="hhat-lang",
    version=version,
    description="H-hat: a high level abstraction quantum programming language.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hhat-lang/hhat_lang",
    author="Eduardo Maschio (Doomsk)",
    author_email="eduardo.maschio@hhat-lang.org",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Interpreters",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="programming language, quantum",
    python_requires=">=3.10, <4",
    install_requires=requirements,
    packages=find_packages(),
    # package_dir={"": "hhat_lang"},
    # package_data={"": ["*.txt"]},
    data_files=[
        ("version", ["hhat_lang/version.txt"]),
    ],
    include_package_data=True,
    extras_require={
        # "netqasm": ["netqasm"],
    },
    entry_points={
        "console_scripts": ["hhat=hhat_lang.exec:main"]
    },
    project_urls={
        "Unitary Fund": "https://unitary.fund/",
        "H-hat documentation": "https://docs.hhat-lang.org"
    }
)
