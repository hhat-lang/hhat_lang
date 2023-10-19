import pathlib

here = pathlib.Path(__file__).parent.resolve()

__version__ = open(here / "version.txt", "r").readline()
