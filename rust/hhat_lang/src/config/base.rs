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
        priority: isize
    }

    impl Device {
        pub fn new(
            name: String,
            is_active: bool,
            vendor: String,
            device_kind: DeviceKind,
            device_platform: String,
            computation_paradigm: Vec<String>,
            device_specs: DeviceSpecs,
            qll: DeviceQuantumLowLevel,
            extra: Option<HashMap<String, toml::Value>>,
            priority: isize,
        ) -> Self {
            Self {
                name,
                is_active,
                vendor,
                device_kind,
                device_platform,
                computation_paradigm,
                device_specs,
                qll,
                extra,
                priority,
            }
        }

        pub fn get_priority(&self) -> isize {
            self.priority
        }
    }

    impl Config {
        pub fn new(
            title: String,
            version: String,
            mut devices: Vec<Device>,
        ) -> Result<Self, String> {
            devices.sort_by(|device_a, device_b| {
                device_b.priority.cmp(&device_a.priority)
            });
            Ok(Self {
                title,
                version,
                devices,
            })
        }

        pub fn to_file(&self, path: &str) -> Result<(), String> {
            let toml_string = toml::to_string(self).map_err(|e| e.to_string())?;
            fs::write(path, toml_string).map_err(|e| e.to_string())
        }

        pub fn from_file(path: &str) -> Result<Self, String> {
            let toml_string = fs::read_to_string(path).map_err(|e| e.to_string())?;
            let mut config: Config = toml::from_str(&toml_string).map_err(|e| e.to_string())?;
            config.devices.sort_by(|device_a, device_b| {
                device_b.priority.cmp(&device_a.priority)
            });
            Ok(config)
        }

        pub fn remove_device(&mut self, index: usize) -> Result<Device, String> {
            if index < self.devices.len() {
                Ok(self.devices.remove(index))
            } else {
                Err(format!("Index {} not found.", index))
            }
        }

        pub fn replace_device(&mut self, index: usize, device: Device) -> Result<Device, String> {
            let removed = self.remove_device(index)?;
            self.add_device(device);
            Ok(removed)
        }

        pub fn add_device(&mut self, new_device: Device) {
            // We want to shift as few elements as possible, so we find the first inactive device and insert to its left
            let insert_index = self.devices.partition_point(|device| device.priority > new_device.priority);
            self.devices.insert(insert_index, new_device);
        }

        // No mut version so that changing a device must be done via replace_device, which ensures the sort
        pub fn get_devices(&self) -> &[Device] {
            &self.devices
        }

        pub fn get_active_devices(&self) -> impl Iterator<Item = &Device> {
            self.devices.iter().filter(|device| device.is_active)
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

    pub(self) fn get_ibm_device(name: String, is_active: bool, priority: isize) -> Device {
        Device::new(
            name,
            is_active,
            "IBM".to_string(),
            if is_active { DeviceKind::Simulator } else { DeviceKind::Device },
            "superconducting".to_string(),
            vec!["gate".to_string()],
            DeviceSpecs {
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
            DeviceQuantumLowLevel {
                name: "openqasm".to_string(),
                package_name: "qiskit_ibm_runtime".to_string(),
                package_version: "0.47.0".to_string(),
                file_extension: "qasm".to_string(),
            },
            if is_active { None } else { Some(HashMap::from([("retired".to_string(), true.into())])) },
            priority
        )
    }

    /// Check that creating a config using `Config::new` sorts the devices and check that the serialization works.
    #[test]
    fn test_serialize_dummy_qiskit_device() {
        let config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                get_ibm_device("ManilaV2".to_string(), false, 0),
                get_ibm_device("FakeManilaV2".to_string(), true, 1),
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
priority = 1

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
priority = 0

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
                priority = 5

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
                priority = -2

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
                    get_ibm_device("ManilaV2".to_string(), false, -2),
                    get_ibm_device("FakeManilaV2".to_string(), true, 5)
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
    fn test_remove_device() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                get_ibm_device("ManilaV2".to_string(), false, 0),
                get_ibm_device("FakeManilaV2".to_string(), true, 1),
                get_ibm_device("ManilaV3".to_string(), false, 2)
            ],
        )
        .unwrap();

        let removed_result = config.remove_device(1);
        assert!(removed_result.is_ok());
        let removed_device = removed_result.unwrap();
        assert_eq!(removed_device.name, "FakeManilaV2");
        assert_eq!(config.get_devices().len(), 2);
        assert_eq!(config.get_devices()[0].name, "ManilaV3");
        assert_eq!(config.get_devices()[1].name, "ManilaV2");
    }

    #[test]
    fn test_remove_device_out_of_bounds_fails() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![get_ibm_device("ManilaV2".to_string(), false, 0)],
        )
        .unwrap();
        match config.remove_device(1) {
            Ok(_) => panic!("Should not have been able to remove this index."),
            Err(e) => assert_eq!(e, "Index 1 not found.".to_string()),
        }
    }

    #[test]
    fn test_replace_device() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                get_ibm_device("ManilaV2".to_string(), false, 0),
                get_ibm_device("FakeManilaV2".to_string(), true, 1),
                get_ibm_device("FakeManilaV3".to_string(), true, 2),
            ],
        )
        .unwrap();
        assert!(
            config
                .replace_device(1, get_ibm_device("ManilaV3".to_string(), false, 3))
                .is_ok()
        );
        assert_eq!(config.get_devices().len(), 3);
        assert_eq!(config.get_devices()[0].name, "ManilaV3");
        assert_eq!(config.get_devices()[1].name, "FakeManilaV3");
        assert_eq!(config.get_devices()[2].name, "ManilaV2");
    }

    #[test]
    fn test_replace_device_out_of_bounds_fails() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                get_ibm_device("FakeManilaV2".to_string(), true, 1),
                get_ibm_device("ManilaV2".to_string(), false, 0),
            ],
        )
        .unwrap();
        match config.replace_device(5, get_ibm_device("FakeManilaV3".to_string(), true, 6)) {
            Ok(_) => {
                panic!("Should not have been able to replace a device at an out-of-bounds index.")
            }
            Err(e) => assert_eq!(e, "Index 5 not found.".to_string()),
        }
    }

    #[test]
    fn test_add_device() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                get_ibm_device("FakeManilaV2".to_string(), true, 4),
                get_ibm_device("ManilaV2".to_string(), false, 0),
                get_ibm_device("ManilaV3".to_string(), false, 2),
            ],
        )
        .unwrap();
        config.add_device(get_ibm_device("FakeManilaV3".to_string(), true, 3));
        let devices = config.get_devices();
        assert_eq!(devices.len(), 4);
        assert_eq!(devices[0].name, "FakeManilaV2");
        assert_eq!(devices[1].name, "FakeManilaV3");
        assert_eq!(devices[2].name, "ManilaV3");
        assert_eq!(devices[3].name, "ManilaV2");
    }

    #[test]
    fn test_access_config() {
        let mut config = Config::new(
            "H-hat Compiler Quantum Device Configuration".to_string(),
            "0.1.0".to_string(),
            vec![
                get_ibm_device("ManilaV2".to_string(), false, 0),
                get_ibm_device("FakeManilaV2".to_string(), true, 1),
            ],
        )
        .unwrap();

        assert_eq!(
            config.title,
            "H-hat Compiler Quantum Device Configuration".to_string()
        );
        assert_eq!(config.version, "0.1.0".to_string());
        assert_eq!(config.get_devices().len(), 2);

        assert_eq!(config.get_devices()[0].name, "FakeManilaV2".to_string());
        assert_eq!(config.get_devices()[1].name, "ManilaV2".to_string());

        assert_eq!(config.get_devices()[0].is_active, true);
        assert_eq!(config.get_devices()[1].is_active, false);

        assert_eq!(config.get_devices()[0].get_priority(), 1);
        assert_eq!(config.get_devices()[1].get_priority(), 0);

        assert_eq!(config.get_devices()[0].device_kind, DeviceKind::Simulator);
        assert_eq!(config.get_devices()[1].device_kind, DeviceKind::Device);

        for i in [0, 1] {
            assert_eq!(config.get_devices()[i].vendor, "IBM".to_string());
            assert_eq!(
                config.get_devices()[i].device_platform,
                "superconducting".to_string()
            );
            assert_eq!(
                config.get_devices()[i].computation_paradigm,
                vec!["gate".to_string()]
            );
            assert_eq!(config.get_devices()[i].device_specs.max_n_qubits, 5);
            assert_eq!(
                config.get_devices()[i].device_specs.qubit_topology,
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
            assert_eq!(config.get_devices()[i].qll.name, "openqasm".to_string());
            assert_eq!(
                config.get_devices()[i].qll.package_name,
                "qiskit_ibm_runtime".to_string()
            );
            assert_eq!(
                config.get_devices()[i].qll.package_version,
                "0.47.0".to_string()
            );
            assert_eq!(
                config.get_devices()[i].qll.file_extension,
                "qasm".to_string()
            );
        }
    }
}
