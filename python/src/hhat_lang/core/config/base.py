"""
Q: Why does this file exist?

A: To keep configuration files and data under strict keys and values,
and expected behavior. This way, generating or retrieving a configuration
file for new dialects, low-level languages, target backends, with
multiple options will always follow the same recipe.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field, asdict
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Optional
from functools import wraps

from hhat_lang.core.config.utils import read_file
from hhat_lang.core.lowlevel.abstract_qlang import BaseLLQManager, BaseLLQ


settings_classes: dict[str, Callable[[], Any]] = dict()
"""
A dictionary containing classes for each setting::
    - 'default' for current settings, 
    - 'dialect' contains the DialectSettings,
    - 'llq' contains LLQSettings, 
    - 'backend' contains TargetBackendSettings,
"""


########################################
# CONSTRUCTORS AND AUXILIARY FUNCTIONS #
########################################


def insert_setting_class(config_name: str) -> Callable:
    """
    Inserts setting class to the settings classes dictionary
    according to the key name (str).
    """

    def decorator(fn: Any) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        settings_classes[config_name] = wrapper
        return wrapper

    return decorator


@insert_setting_class("project_root")
def _build_project_root(settings: dict) -> tuple[Path]:
    return (Path(settings.get("project_root")),)


@insert_setting_class("default")
def _build_default_obj(
    settings: dict,
) -> tuple[CurrentDialect, CurrentLLQ, CurrentBackend]:
    """
    Define the default ('current_settings') configuration data to be used by the
    project to compile and execute code.
    """

    dialect, llq, backend = _retrieve_current_settings_data(settings)

    return (
        CurrentDialect(next(iter(dialect.keys())), **next(iter(dialect.values()))),
        CurrentLLQ(),
        CurrentBackend(),
    )


def _retrieve_current_settings_data(settings: dict) -> tuple[dict, dict, dict]:
    """
    Retrieve project current settings to build the right objects and feed the program executor.

    Args:
        settings: dictionary containing the settings from project's configuration file

    Returns:
        A tuple with dialect, llq and backend data dictionaries
    """

    current: dict | None = settings.get("current_settings", None)

    if current is None:
        raise ValueError("could not find 'current_settings' key on the project configuration file.")

    dialect_list: list[str] = current["dialect"]["dir"]
    llq_list: list[list[str]] = list(k["dir"] for k in current["llq"])
    backend_list: list[list[str]] = list(k["dir"] for k in current["backend"])

    dialect_data: dict = _retrieve_data_from_settings(settings, "dialect", dialect_list)
    llq_data: dict[tuple[str, ...], dict] = _retrieve_data_from_composed_settings(
        settings=settings, which_data="llq", data_list=llq_list
    )
    backend_data: dict[tuple[str, ...], dict] = _retrieve_data_from_composed_settings(
        settings=settings, which_data="backend", data_list=backend_list
    )
    return dialect_data, llq_data, backend_data


def _retrieve_data_from_settings(
    settings: dict, which_data: str, data_dir: list[str]
) -> dict[tuple[str, ...], dict]:
    """
    Retrieve a single dictionary entry from project settings.

    Args:
        settings:
        which_data:
        data_dir:

    Returns:
        The dictionary where key is the data reference name tuple
        and the value is data from settings.
    """

    data: dict = (
        settings[which_data]
        if (avail := settings.get("available_settings", None)) is None
        else avail[which_data]
    )

    for name in data_dir:
        data = data[name]

    return {tuple(data_dir): data}


def _retrieve_data_from_composed_settings(
    settings: dict, which_data: str, data_list: list[list[str]]
) -> dict[tuple[str, ...], dict]:
    """
    Retrieve a list of dictionary entries from project settings.

    Args:
        settings:
        which_data:
        data_list:

    Returns:
        The dictionary where the keys are the data reference name tuple and
        the values are data from settings.
    """

    data: dict = (
        settings[which_data]
        if (avail := settings.get("available_settings", None)) is None
        else avail[which_data]
    )
    res: dict[tuple[str, ...], dict] = dict()

    for data_dir in data_list:
        for name in data_dir:
            data = data[name]

        res.update({tuple(data_dir): data})

    return res


@insert_setting_class("dialect")
def _build_dialects_obj(dialects: dict) -> DialectSettings:
    _opts: tuple[DialectOptions, ...] = ()

    for name_folder, data in dialects.items():
        for version_folder, content in data.items():
            _opts += DialectOptions(
                name=content["name"],
                version=content["version"],
                version_type=content["version_type"],
                package_name=content["package_name"] or "",
                name_folder=name_folder,
                version_folder=version_folder,
            )

    return DialectSettings(*_opts)


@insert_setting_class("llq")
def _build_llq_obj(llqs: dict) -> LLQSettings:
    _opts: tuple[LLQOptions, ...] = ()
    for name_folder, data in llqs.items():
        for version_folder, content in data.items():
            _opts += LLQOptions(
                name=content["name"],
                version=content["version"],
                name_folder=name_folder,
                version_folder=version_folder,
                package_name=content["package_name"],
            )

    return LLQSettings(*_opts)


@insert_setting_class("backend")
def _build_backend_obj(backends: dict) -> TargetBackendSettings:
    def _get_executor(executor: dict) -> ExecutorOptions:
        shots = ShotsSettings(*tuple(ShotsOptions(**shots_opt) for shots_opt in executor["shots"]))
        # implement pass
        # passes = PassSettings(*tuple(PassOptions(**pass_opt) for pass_opt in executor["pass"]))
        passes = PassSettings()
        # implement cast
        # casts = CastSettings(*tuple(CastOptions(**cast_opt) for cast_opt in executor["cast"]))
        casts = CastSettings()

        return ExecutorOptions(shots=shots, passes=passes, cast=casts)

    def _get_device(device: dict) -> DeviceSettings:
        _res = tuple(
            DeviceOptions(name=name, max_num_qubits=dv["max_num_qubits"], metadata=dict())
            for name, dv in device.items()
        )

        return DeviceSettings(*_res)

    _opts: tuple[BackendOptions, ...] = ()

    for backend_folder, data in backends.items():
        for name_folder, content in data.items():
            _opts += BackendOptions(
                name=content["name"],
                package_name=content["package_name"],
                version=content["version"],
                is_simulator=content["is_simulator"],
                name_folder=name_folder,
                backend_folder=backend_folder,
                executor=_get_executor(content["executor"]),
                device=_get_device(content["device"]),
            )

    return TargetBackendSettings(*_opts)


class ConstructorBaseHhatSettings:
    def __new__(cls, setting: str = "default"):
        match setting:
            case "default":
                dialect, llq, backend = settings_classes.get(setting)
                return CurrentSettings(dialect=dialect, llq=llq, backend=backend)

            case _:
                return settings_classes.get(setting)


class OuterSettings(ABC):
    """
    Settings abstract class for outer elements, such as dialects, llq and backend classes
    """

    _opts: dict[tuple[str, str], Any]

    def __getitem__(self, item: tuple[str, str]) -> Any | None:
        return self._opts.get(item)


class InnerSettings(ABC):
    """
    Settings abstract class for inner elements, such as executors and devices classes
    """

    _opts: dict[str, Any]

    def __getitem__(self, item: str) -> Any:
        return self._opts.get(item)


#########################
# BASE SETTINGS CLASSES #
#########################


class HhatProjectSettings:
    """Class to hold all H-hat project settings (current and available ones)."""

    _project_root: Path
    _current: CurrentSettings
    _available: AvailableSettings

    def __init__(self, project_root: Path, current: CurrentSettings, available: AvailableSettings):
        self._project_root = project_root
        self._current = current
        self._available = available

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def current(self) -> CurrentSettings:
        return self._current

    @property
    def available(self) -> AvailableSettings:
        return self._available

    @classmethod
    def load(cls, settings_path: Path | str) -> HhatProjectSettings:
        data = read_file(settings_path)
        # TODO: finish implementing it


@dataclass
class CurrentSettings:
    """
    Use HhatSettings as the main settings class to configure the whole project.
    It contains settings for:

    - dialects
    - low-level quantum languages (llq)
    - target backends (backend)

    Data may be stored in configuration files, such as json, yaml, toml, etc. (according
    to implementations available). They should be able to be retrieved by this very same
    class through its ``load`` method.

    **Important**: it will load data contained in the "current_settings" section of the
    configuration file.
    """

    dialect: DialectSettings
    llq: LLQSettings
    backend: TargetBackendSettings

    @classmethod
    def load(cls, file: Path) -> CurrentSettings:
        """
        Loads data from ``file`` (``Path`` type) to a new H-hat settings instance.
        """

        return ConstructorBaseHhatSettings(**read_file(file))

    def serialize(self) -> dict:
        return {
            **self.dialect.serialize(),
            **self.llq.serialize(),
            **self.backend.serialize(),
        }


class CurrentDialect:
    _dialect: Any
    _module: ModuleType
    _opts: DialectOptions

    def __init__(self, dialect: list[str] | tuple[str, ...], **options: dict):
        self._module = import_module(".".join(dialect))
        self._opts = DialectOptions(**options)

    @property
    def dialect(self) -> ModuleType:
        return self._dialect

    @property
    def opts(self) -> DialectOptions:
        return self._opts


class CurrentLLQ:
    _module: dict[tuple[str, str], ModuleType]
    _manager: dict[tuple[str, str], BaseLLQManager]
    _llq: dict[tuple[str, str], BaseLLQ]
    _opts: LLQSettings

    def __init__(self, llq_dir: tuple[tuple[str, str], ...], **options: dict):
        self._opts = settings_classes["llq"]
        self._module = dict()
        self._manager = dict()
        self._llq = dict()

        for ld in llq_dir:
            self._module = {ld: import_module(".".join(ld))}
            # every module must contain the following ``.base.LLQManager`` and ``.base.LLQ``
            self._manager = {ld: self._module[ld].base.LLQManager()}
            self._llq = {ld: self._module[ld].base.LLQ()}


class CurrentBackend:
    _executor: Callable


class AvailableSettings:
    pass


class DialectSettings(OuterSettings):
    """
    General dialects settings class. Should hold the list of available
    dialect options (``DialectOptions``).
    """

    _opts: dict[tuple[str, str], DialectOptions]

    def __init__(self, *dialects: DialectOptions):
        for dialect in dialects:
            key = (dialect.name_folder, dialect.version_folder)
            if key not in self._opts:
                self._opts[key] = dialect

    @property
    def opts(self) -> dict[tuple[str, str], DialectOptions]:
        return self._opts

    def serialize(self) -> dict:
        res = dict()

        for v in self._opts.values():
            res.update(v.serialize())

        return {"dialect": res}


@dataclass
class DialectOptions:
    name: str
    version: str
    version_type: str
    name_folder: str
    version_folder: Optional[str] = None
    package_name: str = field(default="")

    def serialize(self) -> dict:
        return {
            self.name_folder: {
                self.version_folder: {
                    "name": self.name,
                    "version": self.version,
                    "version_type": self.version_type,
                    "package_name": self.package_name,
                }
            }
        }


class LLQSettings(OuterSettings):
    _opts: dict[tuple[str, str], LLQOptions]

    def __init__(self, *llqs: LLQOptions):
        for llq in llqs:
            key = (llq.name_folder, llq.version_folder)
            if key not in self._opts:
                self._opts[key] = llq

    @property
    def opts(self) -> dict[tuple[str, str], LLQOptions]:
        return self._opts

    def serialize(self) -> dict:
        res = dict()

        for v in self._opts.values():
            res.update(v.serialize())

        return {"llq": res}


@dataclass
class LLQOptions:
    name: str
    version: str
    name_folder: str
    version_folder: str
    package_name: str = field(default="")

    def serialize(self) -> dict:
        return {
            self.name_folder: {
                self.version_folder: {
                    "name": self.name,
                    "version": self.version,
                    "package_name": self.package_name,
                }
            }
        }


class TargetBackendSettings(OuterSettings):
    _opts: dict[tuple[str, str], BackendOptions]

    def __init__(self, *backends: BackendOptions):
        for backend in backends:
            key = (backend.backend_folder, backend.name_folder)
            if key not in self._opts:
                self._opts[key] = backend

    @property
    def opts(self) -> dict[tuple[str, str], BackendOptions]:
        return self._opts

    def serialize(self) -> dict:
        res = dict()

        for v in self._opts.values():
            res.update(v.serialize())

        return {"backend": res}


@dataclass
class BackendOptions:
    name: str
    package_name: str
    version: str
    is_simulator: bool
    executor: ExecutorOptions
    device: DeviceSettings
    backend_folder: str
    name_folder: str

    def serialize(self) -> dict:
        return asdict(self)


@dataclass
class ExecutorOptions:
    shots: ShotsSettings
    passes: PassSettings
    cast: CastSettings

    def serialize(self) -> dict:
        return asdict(self)


class ShotsSettings(InnerSettings):
    """
    Shots settings class. It keeps all the shots options classes under
    a single umbrella. Ex::

        shot_opt1 = ShotsOptions(
            name="shots_per_qubit",
            base=200,
            min=1024,
            max=None
        )
        shot_opt2 = ShotsOptions(
            name="fixed_shots",
            base=2048,
            min=2048,
            max=2048
        )

        shots_settings = ShotsSettings(shot_opt1, shot_opt2)


    This will be translated into a configuration file (such as a json file) as::

        ...
        "executor": {
            ...
            "shots": {
                "shots_per_qubit": {
                    "base": 20,
                    "min": 1024,
                    "max": null
                },
                "fixed_shots": {
                    "base": 2048,
                    "min": 2048,
                    "max": 2048
                }
            }
            ...
        }
        ...
    """

    def __init__(self, *shots_opts: ShotsOptions):
        for opt in shots_opts:
            if opt.name not in self._opts:
                self._opts[opt.name] = opt

    def serialize(self) -> dict:
        res = dict()

        for v in self._opts.values():
            res.update(v.serialize())

        return res


@dataclass
class ShotsOptions:
    name: str
    base: Optional[int] = None
    min: Optional[int] = None
    max: Optional[int] = None

    def serialize(self) -> dict:
        return asdict(self)


class PassSettings(InnerSettings):
    """TODO: implement it"""


@dataclass
class PassOptions:
    """TODO: implement it"""


class CastSettings:
    """TODO: implement it"""

    def __init__(self):
        pass

    def serialize(self) -> dict:
        return dict()


class DeviceSettings(InnerSettings):
    """
    Hold all devices information available for a particular target backend.
    """

    def __init__(self, *devices: DeviceOptions):
        for device in devices:
            if device.name not in self._opts:
                self._opts[device.name] = device

    def serialize(self) -> dict:
        res = dict()

        for v in self._opts.values():
            res.update(v.serialize())

        return res


@dataclass
class DeviceOptions:
    name: str
    max_num_qubits: int
    metadata: dict = field(default_factory=dict)

    def serialize(self) -> dict:
        return asdict(self)
