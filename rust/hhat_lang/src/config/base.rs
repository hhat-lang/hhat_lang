use std::collections::HashMap;
use std::fs;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct Config {
    title: String,
    version: String,
    devices: Vec<Device>,
}

#[derive(Serialize, Deserialize, PartialEq, Eq)]
enum DeviceKind {
    Simulator,
    Device,
}

#[derive(Serialize, Deserialize, PartialEq, Eq)]
struct DeviceSpecs {
    max_n_qubits: u32,
    qubit_topology: Vec<(u32, u32)>,
}

#[derive(Serialize, Deserialize, PartialEq, Eq)]
struct DeviceQuantumLowLevel {
    name: String,
    package_name: String,
    package_version: String,
    file_extension: String,
}

#[derive(Serialize, Deserialize)]
struct Device {
    name: String,
    is_active: bool,
    vendor: String,
    device_kind: DeviceKind,
    device_platform: String,
    computation_paradigm: Vec<String>,
    device_specs: DeviceSpecs,
    qll: DeviceQuantumLowLevel,
    extra: Option<HashMap<String, toml::Value>>,
}

impl Config {
    fn new(title: String, version: String, mut devices: Vec<Device>) -> Result<Self, String> {
        let check_active_device = devices.iter().find(|device| device.is_active).is_some();

        if check_active_device {
            devices.sort_by(|device_a, device_b| {
                device_a.is_active.cmp(&device_b.is_active).reverse()
            });
            Ok(Self {
                title,
                version,
                devices,
            })
        } else {
            Err("At least one device must be active.".to_string())
        }
    }

    fn to_file(&self, path: &str) -> Result<(), String> {
        let toml_string = toml::to_string(self).map_err(|e| e.to_string())?;
        fs::write(path, toml_string).map_err(|e| e.to_string())
    }

    fn from_file(path: &str) -> Result<Self, String> {
        let toml_string = fs::read_to_string(path).map_err(|e| e.to_string())?;
        let mut config: Config = toml::from_str(&toml_string).map_err(|e| e.to_string())?;
        config
            .devices
            .sort_by(|device_a, device_b| device_a.is_active.cmp(&device_b.is_active).reverse());

        match config.devices.iter().find(|device| device.is_active) {
            Some(_) => Ok(config),
            None => Err("At least one device must be active.".to_string()),
        }
    }
}

// Since toml::Value doesn't implement PartialEq, we define the equality up to the `extra` field
impl PartialEq for Config {
    fn eq(&self, other: &Self) -> bool {
        if self.title != other.title {
            return false;
        }
        if self.version != other.version {
            return false;
        }
        if self.devices.len() != other.devices.len() {
            return false;
        }
        for (device_a, device_b) in self.devices.iter().zip(other.devices.iter()) {
            if device_a.name != device_b.name
                || device_a.is_active != device_b.is_active
                || device_a.vendor != device_b.vendor
                || device_a.device_kind != device_b.device_kind
                || device_a.device_platform != device_b.device_platform
                || device_a.computation_paradigm != device_b.computation_paradigm
                || device_a.device_specs != device_b.device_specs
                || device_a.qll != device_b.qll
            {
                return false;
            }
        }

        true
    }
}
impl Eq for Config {}

#[cfg(test)]
mod tests {
    use super::*;

    /// Check that creating a config using `Config::new` sorts the devices and check that the serialization works.
    #[test]
    fn test_serialize_dummy_qiskit_device() {
        let config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                Device {
                    name: "ManilaV2".to_string(),
                    is_active: false,
                    vendor: "IBM".to_string(),
                    device_kind: DeviceKind::Device,
                    device_platform: "superconducting".to_string(),
                    computation_paradigm: vec!["gate".to_string()],
                    device_specs: DeviceSpecs {
                        max_n_qubits: 5,
                        qubit_topology: vec![
                            (0, 1),
                            (1, 0),
                            (1, 2),
                            (2, 1),
                            (2, 3),
                            (3, 2),
                            (3, 4),
                            (4, 3),
                        ],
                    },
                    qll: DeviceQuantumLowLevel {
                        name: "openqasm".to_string(),
                        package_name: "qiskit_ibm_runtime".to_string(),
                        package_version: "0.47.0".to_string(),
                        file_extension: "qasm".to_string(),
                    },
                    extra: Some(HashMap::from([("retired".to_string(), true.into())])),
                },
                Device {
                    name: "FakeManilaV2".to_string(),
                    is_active: true,
                    vendor: "IBM".to_string(),
                    device_kind: DeviceKind::Simulator,
                    device_platform: "superconducting".to_string(),
                    computation_paradigm: vec!["gate".to_string()],
                    device_specs: DeviceSpecs {
                        max_n_qubits: 5,
                        qubit_topology: vec![
                            (0, 1),
                            (1, 0),
                            (1, 2),
                            (2, 1),
                            (2, 3),
                            (3, 2),
                            (3, 4),
                            (4, 3),
                        ],
                    },
                    qll: DeviceQuantumLowLevel {
                        name: "openqasm".to_string(),
                        package_name: "qiskit_ibm_runtime".to_string(),
                        package_version: "0.47.0".to_string(),
                        file_extension: "qasm".to_string(),
                    },
                    extra: None,
                },
            ],
        )
        .unwrap();
        config
            .to_file("test_serialize_dummy_qiskit_device.toml")
            .unwrap();
        let written_data = fs::read_to_string("test_serialize_dummy_qiskit_device.toml").unwrap();
        assert_eq!(
            written_data,
            r#"title = "H-hat Compiler Quantum Device Configuration"
version = "0.1.0"

[[devices]]
name = "FakeManilaV2"
is_active = true
vendor = "IBM"
device_kind = "Simulator"
device_platform = "superconducting"
computation_paradigm = ["gate"]

[devices.device_specs]
max_n_qubits = 5
qubit_topology = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]

[devices.qll]
name = "openqasm"
package_name = "qiskit_ibm_runtime"
package_version = "0.47.0"
file_extension = "qasm"

[[devices]]
name = "ManilaV2"
is_active = false
vendor = "IBM"
device_kind = "Device"
device_platform = "superconducting"
computation_paradigm = ["gate"]

[devices.device_specs]
max_n_qubits = 5
qubit_topology = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]

[devices.qll]
name = "openqasm"
package_name = "qiskit_ibm_runtime"
package_version = "0.47.0"
file_extension = "qasm"

[devices.extra]
retired = true
"#
        );
        fs::remove_file("test_serialize_dummy_qiskit_device.toml").unwrap();
    }

    #[test]
    fn test_deserialize_dummy_qiskit_device() {
        fs::write(
            "test_deserialize_dummy_qiskit_device.toml",
            r#"
                title = "H-hat Compiler Quantum Device Configuration"
                version = "0.1.0"

                [[devices]]
                name = "FakeManilaV2"
                is_active = true
                vendor = "IBM"
                device_kind = "Simulator"
                device_platform = "superconducting"
                computation_paradigm = ["gate"]

                [devices.device_specs]
                max_n_qubits = 5
                qubit_topology = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]

                [devices.qll]
                name = "openqasm"
                package_name = "qiskit_ibm_runtime"
                package_version = "0.47.0"
                file_extension = "qasm"

                [[devices]]
                name = "ManilaV2"
                is_active = false
                vendor = "IBM"
                device_kind = "Device"
                device_platform = "superconducting"
                computation_paradigm = ["gate"]

                [devices.device_specs]
                max_n_qubits = 5
                qubit_topology = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]

                [devices.qll]
                name = "openqasm"
                package_name = "qiskit_ibm_runtime"
                package_version = "0.47.0"
                file_extension = "qasm"

                [devices.extra]
                retired = true
            "#,
        )
        .unwrap();
        if let Ok(derived_config) = Config::from_file("test_deserialize_dummy_qiskit_device.toml") {
            fs::remove_file("test_deserialize_dummy_qiskit_device.toml").unwrap();
            let config = Config::new(
                "H-hat Compiler Quantum Device Configuration".to_string(),
                "0.1.0".to_string(),
                vec![
                    Device {
                        name: "ManilaV2".to_string(),
                        is_active: false,
                        vendor: "IBM".to_string(),
                        device_kind: DeviceKind::Device,
                        device_platform: "superconducting".to_string(),
                        computation_paradigm: vec!["gate".to_string()],
                        device_specs: DeviceSpecs {
                            max_n_qubits: 5,
                            qubit_topology: vec![
                                (0, 1),
                                (1, 0),
                                (1, 2),
                                (2, 1),
                                (2, 3),
                                (3, 2),
                                (3, 4),
                                (4, 3),
                            ],
                        },
                        qll: DeviceQuantumLowLevel {
                            name: "openqasm".to_string(),
                            package_name: "qiskit_ibm_runtime".to_string(),
                            package_version: "0.47.0".to_string(),
                            file_extension: "qasm".to_string(),
                        },
                        extra: Some(HashMap::from([("retired".to_string(), true.into())])),
                    },
                    Device {
                        name: "FakeManilaV2".to_string(),
                        is_active: true,
                        vendor: "IBM".to_string(),
                        device_kind: DeviceKind::Simulator,
                        device_platform: "superconducting".to_string(),
                        computation_paradigm: vec!["gate".to_string()],
                        device_specs: DeviceSpecs {
                            max_n_qubits: 5,
                            qubit_topology: vec![
                                (0, 1),
                                (1, 0),
                                (1, 2),
                                (2, 1),
                                (2, 3),
                                (3, 2),
                                (3, 4),
                                (4, 3),
                            ],
                        },
                        qll: DeviceQuantumLowLevel {
                            name: "openqasm".to_string(),
                            package_name: "qiskit_ibm_runtime".to_string(),
                            package_version: "0.47.0".to_string(),
                            file_extension: "qasm".to_string(),
                        },
                        extra: None,
                    },
                ],
            )
            .unwrap();
            assert!(derived_config == config);
        } else {
            fs::remove_file("test_deserialize_dummy_qiskit_device.toml").unwrap();
            panic!("Failed to deserialize the config file.");
        }
    }

    #[test]
    fn test_new_with_no_active_device() {
        let config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![Device {
                name: "ManilaV2".to_string(),
                is_active: false,
                vendor: "IBM".to_string(),
                device_kind: DeviceKind::Device,
                device_platform: "superconducting".to_string(),
                computation_paradigm: vec!["gate".to_string()],
                device_specs: DeviceSpecs {
                    max_n_qubits: 5,
                    qubit_topology: vec![
                        (0, 1),
                        (1, 0),
                        (1, 2),
                        (2, 1),
                        (2, 3),
                        (3, 2),
                        (3, 4),
                        (4, 3),
                    ],
                },
                qll: DeviceQuantumLowLevel {
                    name: "openqasm".to_string(),
                    package_name: "qiskit_ibm_runtime".to_string(),
                    package_version: "0.47.0".to_string(),
                    file_extension: "qasm".to_string(),
                },
                extra: Some(HashMap::from([("retired".to_string(), true.into())])),
            }],
        );
        assert!(config.is_err());
    }

    #[test]
    fn test_from_file_with_no_active_devices() {
        fs::write(
            "test_from_file_with_no_active_devices.toml",
            r#"
                title = "H-hat Compiler Quantum Device Configuration"
                version = "0.1.0"

                [[devices]]
                name = "ManilaV2"
                is_active = false
                vendor = "IBM"
                device_kind = "Device"
                device_platform = "superconducting"
                computation_paradigm = ["gate"]

                [devices.device_specs]
                max_n_qubits = 5
                qubit_topology = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 4], [4, 3]]

                [devices.qll]
                name = "openqasm"
                package_name = "qiskit_ibm_runtime"
                package_version = "0.47.0"
                file_extension = "qasm"

                [devices.extra]
                retired = true
            "#,
        )
        .unwrap();
        let derived_config = Config::from_file("test_from_file_with_no_active_devices.toml");
        fs::remove_file("test_from_file_with_no_active_devices.toml").unwrap();
        assert!(derived_config.is_err());
    }
}
