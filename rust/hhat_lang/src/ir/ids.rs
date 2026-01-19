
/// Use this for naming, such as module paths.
pub struct Path(Vec<String>);

pub struct SymbolId(u32);
pub struct ModuleId(u32);


/// Computational paradigm.
/// Defines the rules and execution planner to run.
/// Some computation paradigms can be executed instructions
/// immediately (strict mode) or lazily (staged mode), while
/// others are restricted to one or the other only.
///
/// Existing enumerated paradigms:
/// - CPU
/// - GPU
/// - NPU
/// - TPU
/// - QPU  (lazy mode only)
///
/// *Note*: only CPU and QPU are available for the current
/// language version.
///
pub enum Paradigm {
    CPU,
    GPU,
    NPU,
    TPU,
    /// QPUs can only execute on lazy (staged) mode.
    QPU,
}
