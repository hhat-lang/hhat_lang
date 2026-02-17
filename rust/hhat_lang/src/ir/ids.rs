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

#[repr(transparent)]
pub struct LiteralId(pub u32);

#[repr(transparent)]
pub struct ExprId(pub u32);

#[repr(transparent)]
pub struct ModuleId(pub u32);


/// Computational backend kind.
///
/// Defines the rules and execution planner to run.
/// Some backend kinds can be executed instructions
/// immediately (strict mode) or lazily (lazy mode),
/// while others are restricted to one or the other only.
///
/// Existing enumerated backend kinds:
/// - CPU
/// - QPU  (lazy mode only)
///
pub enum BackendKind {
    CPU,
    /// QPUs can only execute on lazy mode.
    QPU,
}

impl BackendKind {
    pub fn sugar_fmt(&self) -> String {
        match self {
            BackendKind::CPU => String::from(""),
            BackendKind::QPU => String::from("@"),
        }
    }
    pub fn sugar_str(&self) -> &str {
        match self {
            BackendKind::CPU => "",
            BackendKind::QPU => "@",
        }
    } 
}


pub struct SymbolContext {

}
