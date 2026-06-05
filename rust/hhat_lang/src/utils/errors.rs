use std::fmt::{Display, Formatter};
use std::error::Error;

pub enum ProjectError {
    ProjectNotFound,
}

#[derive(Debug)]
pub enum ModuleError {
    ModuleNotFound,
    CannotReadFile,
}

impl Display for ModuleError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            ModuleError::ModuleNotFound => write!(f, "Module not found"),
            ModuleError::CannotReadFile => write!(f, "Cannot read file"),
        }
    }
}

impl Error for ModuleError {}