use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::error::Error;
use std::fmt;
use std::fs;
use std::path::Path;

pub const DEFAULT_QUANTUM_CONFIG_FILE: &str = "quantum_config.toml";

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct QuantumDeviceConfig {
    pub title: String,
    pub version: String,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub available_devices: Vec<String>,
    #[serde(default)]
    pub devices: Vec<QuantumDevice>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct QuantumDevice {
    pub name: String,
    pub is_active: bool,
    pub vendor: String,
    pub device_kind: DeviceKind,
    pub device_platform: String,
    #[serde(default)]
    pub computation_paradigm: Vec<String>,
    pub specs: QuantumDeviceSpecs,
    pub qll: QuantumLowLevelLanguage,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub extra: BTreeMap<String, toml::Value>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum DeviceKind {
    Simulator,
    Device,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct QuantumDeviceSpecs {
    pub max_n_qubits: u32,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub qubit_topology: BTreeMap<String, toml::Value>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct QuantumLowLevelLanguage {
    pub name: String,
    pub package_name: String,
    pub package_version: String,
    pub file_extension: String,
}

#[derive(Debug)]
pub enum QuantumConfigError {
    Io(std::io::Error),
    Decode(toml::de::Error),
    Encode(toml::ser::Error),
    Validation(String),
}

impl fmt::Display for QuantumConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(error) => write!(f, "quantum device config I/O error: {error}"),
            Self::Decode(error) => write!(f, "invalid quantum device config TOML: {error}"),
            Self::Encode(error) => write!(f, "could not encode quantum device config: {error}"),
            Self::Validation(message) => write!(f, "invalid quantum device config: {message}"),
        }
    }
}

impl Error for QuantumConfigError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::Io(error) => Some(error),
            Self::Decode(error) => Some(error),
            Self::Encode(error) => Some(error),
            Self::Validation(_) => None,
        }
    }
}

impl From<std::io::Error> for QuantumConfigError {
    fn from(error: std::io::Error) -> Self {
        Self::Io(error)
    }
}

impl From<toml::de::Error> for QuantumConfigError {
    fn from(error: toml::de::Error) -> Self {
        Self::Decode(error)
    }
}

impl From<toml::ser::Error> for QuantumConfigError {
    fn from(error: toml::ser::Error) -> Self {
        Self::Encode(error)
    }
}

impl QuantumDeviceConfig {
    pub fn new(title: impl Into<String>, version: impl Into<String>) -> Self {
        Self {
            title: title.into(),
            version: version.into(),
            available_devices: Vec::new(),
            devices: Vec::new(),
        }
    }

    pub fn read_from_file(path: impl AsRef<Path>) -> Result<Self, QuantumConfigError> {
        let mut config: Self = toml::from_str(&fs::read_to_string(path)?)?;
        config.refresh_available_devices();
        config.validate()?;
        Ok(config)
    }

    pub fn write_to_file(&self, path: impl AsRef<Path>) -> Result<(), QuantumConfigError> {
        let mut config = self.clone();
        config.refresh_available_devices();
        config.validate()?;

        if let Some(parent) = path
            .as_ref()
            .parent()
            .filter(|path| !path.as_os_str().is_empty())
        {
            fs::create_dir_all(parent)?;
        }

        fs::write(path, toml::to_string_pretty(&config)?)?;
        Ok(())
    }

    pub fn validate(&self) -> Result<(), QuantumConfigError> {
        if self.title.trim().is_empty() {
            return Err(QuantumConfigError::Validation(
                "title must not be empty".to_string(),
            ));
        }
        if self.version.trim().is_empty() {
            return Err(QuantumConfigError::Validation(
                "version must not be empty".to_string(),
            ));
        }
        if self.devices.is_empty() {
            return Err(QuantumConfigError::Validation(
                "at least one quantum device must be configured".to_string(),
            ));
        }
        if self.active_devices().is_empty() {
            return Err(QuantumConfigError::Validation(
                "at least one quantum device must be active".to_string(),
            ));
        }

        for device in &self.devices {
            device.validate()?;
        }

        Ok(())
    }

    pub fn add_device(&mut self, device: QuantumDevice) {
        self.devices.push(device);
        self.refresh_available_devices();
    }

    pub fn upsert_device(&mut self, device: QuantumDevice) {
        if let Some(existing) = self
            .devices
            .iter_mut()
            .find(|existing| existing.name == device.name)
        {
            *existing = device;
        } else {
            self.devices.push(device);
        }
        self.refresh_available_devices();
    }

    pub fn active_devices(&self) -> Vec<&QuantumDevice> {
        self.devices
            .iter()
            .filter(|device| device.is_active)
            .collect()
    }

    pub fn active_device_names(&self) -> Vec<String> {
        self.active_devices()
            .into_iter()
            .map(|device| device.name.clone())
            .collect()
    }

    pub fn find_device(&self, name: &str) -> Option<&QuantumDevice> {
        self.devices.iter().find(|device| device.name == name)
    }

    pub fn find_active_device(&self, name: &str) -> Option<&QuantumDevice> {
        self.find_device(name).filter(|device| device.is_active)
    }

    pub fn refresh_available_devices(&mut self) {
        self.available_devices = self.active_device_names();
    }
}

impl Default for QuantumDeviceConfig {
    fn default() -> Self {
        Self::new("H-hat Compiler Quantum Device Configuration", "0.1.0")
    }
}

impl QuantumDevice {
    pub fn validate(&self) -> Result<(), QuantumConfigError> {
        if self.name.trim().is_empty() {
            return Err(QuantumConfigError::Validation(
                "device name must not be empty".to_string(),
            ));
        }
        if self.vendor.trim().is_empty() {
            return Err(QuantumConfigError::Validation(format!(
                "device '{}' must include a vendor",
                self.name
            )));
        }
        if self.device_platform.trim().is_empty() {
            return Err(QuantumConfigError::Validation(format!(
                "device '{}' must include a platform",
                self.name
            )));
        }
        if self.computation_paradigm.is_empty() {
            return Err(QuantumConfigError::Validation(format!(
                "device '{}' must include at least one computation paradigm",
                self.name
            )));
        }
        if self.specs.max_n_qubits == 0 {
            return Err(QuantumConfigError::Validation(format!(
                "device '{}' must expose at least one qubit",
                self.name
            )));
        }
        self.qll.validate(&self.name)?;
        Ok(())
    }
}

impl QuantumLowLevelLanguage {
    fn validate(&self, device_name: &str) -> Result<(), QuantumConfigError> {
        if self.name.trim().is_empty()
            || self.package_name.trim().is_empty()
            || self.package_version.trim().is_empty()
            || self.file_extension.trim().is_empty()
        {
            return Err(QuantumConfigError::Validation(format!(
                "device '{device_name}' must include complete QLL information"
            )));
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};

    fn topology(entries: &[(&str, toml::Value)]) -> BTreeMap<String, toml::Value> {
        entries
            .iter()
            .map(|(key, value)| ((*key).to_string(), value.clone()))
            .collect()
    }

    fn device(
        name: &str,
        is_active: bool,
        vendor: &str,
        kind: DeviceKind,
        platform: &str,
        paradigms: &[&str],
        max_n_qubits: u32,
        qll_name: &str,
        package_name: &str,
        package_version: &str,
        file_extension: &str,
    ) -> QuantumDevice {
        QuantumDevice {
            name: name.to_string(),
            is_active,
            vendor: vendor.to_string(),
            device_kind: kind,
            device_platform: platform.to_string(),
            computation_paradigm: paradigms
                .iter()
                .map(|paradigm| (*paradigm).to_string())
                .collect(),
            specs: QuantumDeviceSpecs {
                max_n_qubits,
                qubit_topology: topology(&[("kind", toml::Value::String("all-to-all".into()))]),
            },
            qll: QuantumLowLevelLanguage {
                name: qll_name.to_string(),
                package_name: package_name.to_string(),
                package_version: package_version.to_string(),
                file_extension: file_extension.to_string(),
            },
            extra: BTreeMap::new(),
        }
    }

    fn dummy_config() -> QuantumDeviceConfig {
        let mut config = QuantumDeviceConfig::default();
        config.add_device(device(
            "AerSimulator",
            true,
            "IBM",
            DeviceKind::Simulator,
            "superconducting",
            &["gate"],
            32,
            "openqasm",
            "qiskit",
            "1.0.0",
            "qasm",
        ));
        config.add_device(device(
            "default.qubit",
            true,
            "Xanadu",
            DeviceKind::Simulator,
            "statevector",
            &["gate"],
            16,
            "pennylane",
            "pennylane",
            "0.40.0",
            "py",
        ));
        config.add_device(device(
            "H1-1",
            false,
            "Quantinuum",
            DeviceKind::Device,
            "trapped ions",
            &["gate"],
            20,
            "openqasm",
            "pytket-quantinuum",
            "0.37.0",
            "qasm",
        ));
        config.add_device(device(
            "Aquila",
            false,
            "QuEra",
            DeviceKind::Device,
            "neutral atoms",
            &["analog"],
            256,
            "bloqade",
            "bloqade",
            "0.18.0",
            "json",
        ));
        config
    }

    fn temp_config_path() -> std::path::PathBuf {
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system clock should be after unix epoch")
            .as_nanos();
        std::env::temp_dir()
            .join(format!("hhat_quantum_config_test_{stamp}"))
            .join(DEFAULT_QUANTUM_CONFIG_FILE)
    }

    #[test]
    fn reads_and_writes_dummy_quantum_devices() {
        let path = temp_config_path();
        let config = dummy_config();

        config
            .write_to_file(&path)
            .expect("dummy config should be writable");
        let loaded =
            QuantumDeviceConfig::read_from_file(&path).expect("dummy config should be readable");

        assert_eq!(loaded.title, "H-hat Compiler Quantum Device Configuration");
        assert_eq!(loaded.version, "0.1.0");
        assert_eq!(loaded.devices.len(), 4);
        assert_eq!(
            loaded.available_devices,
            vec!["AerSimulator".to_string(), "default.qubit".to_string()]
        );
        assert_eq!(
            loaded
                .find_active_device("AerSimulator")
                .expect("AerSimulator should be active")
                .qll
                .package_name,
            "qiskit"
        );
        assert!(loaded.find_active_device("H1-1").is_none());

        let _ = fs::remove_file(&path);
        let _ = path.parent().map(fs::remove_dir);
    }

    #[test]
    fn derives_available_devices_when_missing_from_toml() {
        let toml = r#"
title = "H-hat Compiler Quantum Device Configuration"
version = "0.1.0"

[[devices]]
name = "AerSimulator"
is_active = true
vendor = "IBM"
device_kind = "simulator"
device_platform = "superconducting"
computation_paradigm = ["gate"]

[devices.specs]
max_n_qubits = 32
qubit_topology = { kind = "all-to-all" }

[devices.qll]
name = "openqasm"
package_name = "qiskit"
package_version = "1.0.0"
file_extension = "qasm"
"#;

        let mut config: QuantumDeviceConfig =
            toml::from_str(toml).expect("manual quantum config should parse");
        config.refresh_available_devices();
        config.validate().expect("manual quantum config is valid");

        assert_eq!(config.available_devices, vec!["AerSimulator".to_string()]);
    }

    #[test]
    fn rejects_configs_without_active_devices() {
        let mut config = QuantumDeviceConfig::default();
        config.add_device(device(
            "H1-1",
            false,
            "Quantinuum",
            DeviceKind::Device,
            "trapped ions",
            &["gate"],
            20,
            "openqasm",
            "pytket-quantinuum",
            "0.37.0",
            "qasm",
        ));

        let error = config
            .validate()
            .expect_err("config without active devices should fail");

        assert!(error
            .to_string()
            .contains("at least one quantum device must be active"));
    }

    #[test]
    fn upsert_device_refreshes_available_devices() {
        let mut config = dummy_config();
        config.upsert_device(device(
            "Aquila",
            true,
            "QuEra",
            DeviceKind::Device,
            "neutral atoms",
            &["analog"],
            256,
            "bloqade",
            "bloqade",
            "0.18.0",
            "json",
        ));

        assert_eq!(config.devices.len(), 4);
        assert!(config.available_devices.contains(&"Aquila".to_string()));
        assert_eq!(
            config
                .find_active_device("Aquila")
                .expect("Aquila should have been activated")
                .specs
                .max_n_qubits,
            256
        );
    }
}
