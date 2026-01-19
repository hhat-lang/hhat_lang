use crate::ir::ids::Path;
use crate::ir::uir::{UContent, UnresolvedImports};

/// Unresolved module.
/// First module produced for the unresolved IR.
///
pub struct UnresolvedModule {
    /// module name as a vector of strings (`(dir(,dir)*,)*file_name`)
    pub name: Path,
    pub imports: Vec<UnresolvedImports>,
    pub content: UContent
}
