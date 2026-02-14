use std::fmt::{Display, Formatter};

/// Use this for naming, such as module paths.
pub struct Path(Vec<String>);

impl Display for Path {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0.join("."))
    }
}

impl Path {
    pub fn len(&self) -> usize {
        self.0.len()
    }

}

#[repr(transparent)]
pub struct SymbolId(pub u32);

pub struct ExprId(u32);

pub struct ModuleId(u32);


/// Computational backend kind.
///
/// Defines the rules and execution planner to run.
/// Some backend kinds can be executed instructions
/// immediately (strict mode) or lazily (staged mode),
/// while others are restricted to one or the other only.
///
/// Existing enumerated backend kinds:
/// - CPU
/// - GPU
/// - NPU
/// - TPU
/// - QPU  (lazy mode only)
///
/// *Note*: only CPU and QPU are available for the current
/// language version.
///
pub enum BackendKind {
    CPU,
    GPU,
    NPU,
    TPU,
    /// QPUs can only execute on lazy (staged) mode.
    QPU,
}

impl BackendKind {
    pub fn sugar_fmt(&self) -> String {
        match self {
            BackendKind::CPU => String::from(""),
            BackendKind::GPU => String::from("+"),
            BackendKind::NPU => String::from("!"),
            BackendKind::TPU => String::from("%"),
            BackendKind::QPU => String::from("@"),
        }
    }
    pub fn sugar_str(&self) -> &str {
        match self {
            BackendKind::CPU => "",
            BackendKind::GPU => "+",
            BackendKind::NPU => "!",
            BackendKind::TPU => "%",
            BackendKind::QPU => "@",
        }
    } 
}


pub struct SymbolContext {

}
