mod inner {
    use std::collections::HashMap;
    use std::fs;

    use serde::{Deserialize, Serialize};

    #[derive(Serialize, Deserialize)]
    pub struct Config {
        pub title: String,
        pub version: String,
        devices: Vec<Device>,
    }

    #[derive(Serialize, Deserialize, PartialEq, Eq, Debug)]
    pub enum DeviceKind {
        Simulator,
        Device,
    }

    #[derive(Serialize, Deserialize, PartialEq, Eq)]
    pub struct DeviceSpecs {
        pub max_n_qubits: u32,
        pub qubit_topology: Vec<(u32, u32)>,
    }

    #[derive(Serialize, Deserialize, PartialEq, Eq)]
    pub struct DeviceQuantumLowLevel {
        pub name: String,
        pub package_name: String,
        pub package_version: String,
        pub file_extension: String,
    }

    #[derive(Serialize, Deserialize)]
    pub struct Device {
        pub name: String,
        pub is_active: bool,
        pub vendor: String,
        pub device_kind: DeviceKind,
        pub device_platform: String,
        pub computation_paradigm: Vec<String>,
        pub device_specs: DeviceSpecs,
        pub qll: DeviceQuantumLowLevel,
        pub extra: Option<HashMap<String, toml::Value>>,
    }

    impl Config {
        pub fn new(
            title: String,
            version: String,
            mut devices: Vec<Device>,
        ) -> Result<Self, String> {
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

        pub fn to_file(&self, path: &str) -> Result<(), String> {
            let toml_string = toml::to_string(self).map_err(|e| e.to_string())?;
            fs::write(path, toml_string).map_err(|e| e.to_string())
        }

        pub fn from_file(path: &str) -> Result<Self, String> {
            let toml_string = fs::read_to_string(path).map_err(|e| e.to_string())?;
            let mut config: Config = toml::from_str(&toml_string).map_err(|e| e.to_string())?;
            config.devices.sort_by(|device_a, device_b| {
                device_a.is_active.cmp(&device_b.is_active).reverse()
            });

            match config.devices.iter().find(|device| device.is_active) {
                Some(_) => Ok(config),
                None => Err("At least one device must be active.".to_string()),
            }
        }

        pub fn remove_device(&mut self, index: usize) -> Result<Device, String> {
            if index < self.devices.len() {
                if self.devices[index].is_active
                    && self
                        .devices
                        .iter()
                        .filter(|device| device.is_active)
                        .count()
                        == 1
                {
                    Err("Can't remove the only active device.".to_string())
                } else {
                    Ok(self.devices.remove(index))
                }
            } else {
                Err(format!("Index {} not found.", index))
            }
        }

        pub fn replace_device(&mut self, index: usize, device: Device) -> Result<(), String> {
            if index < self.devices.len() {
                if self.devices[index].is_active
                    && !device.is_active
                    && self.devices.iter().filter(|d| d.is_active).count() == 1
                {
                    Err("Can't replace the only active device with an inactive one.".to_string())
                } else {
                    self.devices[index] = device;
                    Ok(())
                }
            } else {
                Err(format!("Index {} not found.", index))
            }
        }

        pub fn add_device(&mut self, device: Device) {
            if !device.is_active {
                self.devices.push(device);
            } else {
                // We want to shift as few elements as possible, so we find the first inactive device and insert to its left
                let insert_index = self.devices.partition_point(|device| device.is_active);
                self.devices.insert(insert_index, device);
            }
        }

        // No mut version so that changing a device must be done via replace_device, which ensures the sort
        // and the fact that at least one device must be active
        pub fn get_devices(&self) -> &[Device] {
            &self.devices
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
}

pub use inner::*;

#[cfg(test)]
mod tests {
    use std::collections::HashMap;
    use std::fs;

    use super::{Config, Device, DeviceKind, DeviceQuantumLowLevel, DeviceSpecs};

    pub(self) fn active_device(name: String) -> Device {
        Device {
            name,
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
        }
    }

    pub(self) fn inactive_device(name: String) -> Device {
        Device {
            name,
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
        }
    }

    /// Check that creating a config using `Config::new` sorts the devices and check that the serialization works.
    #[test]
    fn test_serialize_dummy_qiskit_device() {
        let config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                inactive_device("ManilaV2".to_string()),
                active_device("FakeManilaV2".to_string()),
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
            vec![inactive_device("ManilaV2".to_string())],
        );
        match config {
            Ok(_) => panic!("Config should not have been created successfully."),
            Err(e) => assert_eq!(e, "At least one device must be active.".to_string(),),
        }
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
        match derived_config {
            Ok(_) => panic!("Config should not have been created successfully."),
            Err(e) => assert_eq!(e, "At least one device must be active.".to_string(),),
        }
    }

    #[test]
    fn test_remove_inactive_device() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                inactive_device("ManilaV2".to_string()),
                active_device("FakeManilaV2".to_string()),
            ],
        )
        .unwrap();

        // 1 is the inactive one since it has been sorted
        let removed_result = config.remove_device(1);
        assert!(removed_result.is_ok());
        let removed_device = removed_result.unwrap();
        assert_eq!(removed_device.name, "ManilaV2");
        assert_eq!(config.get_devices().len(), 1);
        assert_eq!(config.get_devices()[0].name, "FakeManilaV2");
    }

    #[test]
    fn test_remove_active_device_with_other_active_present() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                active_device("FakeManilaV2".to_string()),
                inactive_device("ManilaV2".to_string()),
                active_device("FakeManilaV3".to_string()),
            ],
        )
        .unwrap();

        // 1 is active since it has been sorted
        let removed_result = config.remove_device(1);
        assert!(removed_result.is_ok());
        let removed_device = removed_result.unwrap();
        assert_eq!(removed_device.name, "FakeManilaV3");
        assert_eq!(config.get_devices().len(), 2);
        assert_eq!(config.get_devices()[0].name, "FakeManilaV2");
        assert_eq!(config.get_devices()[1].name, "ManilaV2");
    }

    #[test]
    fn test_remove_only_active_device_fails() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![active_device("FakeManilaV2".to_string())],
        )
        .unwrap();
        match config.remove_device(0) {
            Ok(_) => panic!("Should not have been able to remove the only active device."),
            Err(e) => assert_eq!(e, "Can't remove the only active device.".to_string()),
        }
    }

    #[test]
    fn test_remove_device_out_of_bounds_fails() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![active_device("FakeManilaV2".to_string())],
        )
        .unwrap();
        match config.remove_device(1) {
            Ok(_) => panic!("Should not have been able to remove this index."),
            Err(e) => assert_eq!(e, "Index 1 not found.".to_string()),
        }
    }

    #[test]
    fn test_replace_inactive_device() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                active_device("FakeManilaV2".to_string()),
                inactive_device("ManilaV2".to_string()),
            ],
        )
        .unwrap();
        assert!(
            config
                .replace_device(1, active_device("FakeManilaV3".to_string()))
                .is_ok()
        );
        assert_eq!(config.get_devices()[1].name, "FakeManilaV3");
    }

    #[test]
    fn test_replace_active_device_with_active() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                active_device("FakeManilaV2".to_string()),
                inactive_device("ManilaV2".to_string()),
            ],
        )
        .unwrap();
        assert!(
            config
                .replace_device(0, active_device("FakeManilaV3".to_string()))
                .is_ok()
        );
        assert_eq!(config.get_devices()[0].name, "FakeManilaV3");
    }

    #[test]
    fn test_replace_active_device_with_another_active() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                active_device("FakeManilaV2".to_string()),
                inactive_device("ManilaV2".to_string()),
            ],
        )
        .unwrap();
        assert!(
            config
                .replace_device(0, active_device("FakeManilaV3".to_string()))
                .is_ok()
        );
        assert_eq!(config.get_devices()[0].name, "FakeManilaV3");
        assert_eq!(config.get_devices()[1].name, "ManilaV2");
    }

    #[test]
    fn test_replace_only_active_device_with_inactive_fails() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                active_device("FakeManilaV2".to_string()),
                inactive_device("ManilaV2".to_string()),
            ],
        )
        .unwrap();
        match config.replace_device(0, inactive_device("ManilaV3".to_string())) {
            Ok(_) => panic!(
                "Should not have been able to replace the only active device with an inactive one."
            ),
            Err(e) => assert_eq!(
                e,
                "Can't replace the only active device with an inactive one.".to_string()
            ),
        }
    }

    #[test]
    fn test_replace_device_out_of_bounds_fails() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                active_device("FakeManilaV2".to_string()),
                inactive_device("ManilaV2".to_string()),
            ],
        )
        .unwrap();
        match config.replace_device(5, active_device("FakeManilaV2".to_string())) {
            Ok(_) => {
                panic!("Should not have been able to replace a device at an out-of-bounds index.")
            }
            Err(e) => assert_eq!(e, "Index 5 not found.".to_string()),
        }
    }

    #[test]
    fn test_add_inactive_device_appends() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                active_device("FakeManilaV2".to_string()),
                inactive_device("ManilaV2".to_string()),
            ],
        )
        .unwrap();
        config.add_device(inactive_device("ManilaV3".to_string()));
        let devices = config.get_devices();
        assert_eq!(devices.len(), 3);
        assert_eq!(devices.last().unwrap().name, "ManilaV3");
    }

    #[test]
    fn test_add_active_device_placed_before_inactive() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                active_device("FakeManilaV2".to_string()),
                inactive_device("ManilaV2".to_string()),
            ],
        )
        .unwrap();
        config.add_device(active_device("FakeManilaV3".to_string()));
        let devices = config.get_devices();
        assert_eq!(devices.len(), 3);
        assert_eq!(devices[0].name, "FakeManilaV2");
        assert_eq!(devices[1].name, "FakeManilaV3");
        assert_eq!(devices[2].name, "ManilaV2");
    }

    #[test]
    fn test_access_config() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![active_device("FakeManilaV2".to_string())],
        )
        .unwrap();

        assert_eq!(
            config.title,
            "H-hat Compiler Quantum Device Configuration".to_string()
        );
        assert_eq!(config.version, "0.1.0".to_string());
        assert_eq!(config.get_devices().len(), 1);
        assert_eq!(config.get_devices()[0].name, "FakeManilaV2".to_string());
        assert_eq!(config.get_devices()[0].is_active, true);
        assert_eq!(config.get_devices()[0].vendor, "IBM".to_string());
        assert_eq!(config.get_devices()[0].device_kind, DeviceKind::Simulator);
        assert_eq!(
            config.get_devices()[0].device_platform,
            "superconducting".to_string()
        );
        assert_eq!(
            config.get_devices()[0].computation_paradigm,
            vec!["gate".to_string()]
        );
        assert_eq!(config.get_devices()[0].device_specs.max_n_qubits, 5);
        assert_eq!(
            config.get_devices()[0].device_specs.qubit_topology,
            vec![
                (0, 1),
                (1, 0),
                (1, 2),
                (2, 1),
                (2, 3),
                (3, 2),
                (3, 4),
                (4, 3),
            ]
        );
        assert_eq!(config.get_devices()[0].qll.name, "openqasm".to_string());
        assert_eq!(
            config.get_devices()[0].qll.package_name,
            "qiskit_ibm_runtime".to_string()
        );
        assert_eq!(
            config.get_devices()[0].qll.package_version,
            "0.47.0".to_string()
        );
        assert_eq!(
            config.get_devices()[0].qll.file_extension,
            "qasm".to_string()
        );
    }
}
