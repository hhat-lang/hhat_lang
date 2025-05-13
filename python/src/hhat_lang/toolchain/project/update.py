"""
Update current files; It can be to create respective doc files for
the existing files.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from hhat_lang.toolchain.project.utils import str_to_path


def update_project(project_name: str | Path) -> Any:
    project_name = str_to_path(project_name)
    # TODO: implement it
