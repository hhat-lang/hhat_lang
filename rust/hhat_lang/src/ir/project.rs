//! Definition of project-related objects.
//!
//! The objects appearance order reflects its position on the compilation steps.
//!

use std::fmt::{Display, Formatter};
use std::fs::read_to_string;
use std::path::PathBuf;
use walkdir::WalkDir;
use crate::ir::ids::ModuleId;
use crate::utils::errors::ModuleError;


/// Raw code's project object.
/// It will list every single hat file and read its content,
/// adding to a vector of module sources.
///
/// It is the very first step on the project compilation pipeline.
#[derive(Debug)]
pub struct SourceProject {
    pub root: PathBuf,
    pub sources: Vec<SourceModule>,
}

impl SourceProject {
    pub fn new(root_path: &str) -> Self {
        Self {
            root:PathBuf::from(root_path),
            sources: SourceProject::get_modules(root_path)
        }
    }

    pub fn is_empty(&self) -> bool {
        self.sources.is_empty()
    }

    fn get_modules(path: &str) -> Vec<SourceModule> {
        SourceProject::get_files(path).into_iter()
            .filter_map(|f| {
                Some(SourceModule::new(
                    f.to_str()
                        .expect("could not get module source path from {path}"))
                )
            })
            .collect::<Vec<SourceModule>>()
    }

    fn get_files(path: &str) -> Vec<PathBuf> {
        WalkDir::new(path).into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_type().is_file())
            .filter(|e|
                e.path()
                    .extension()
                    .and_then(|x| x.to_str())
                    .is_some_and(|x| x.eq("hat"))
            )
            .map(|e| e.into_path())
            .collect()
    }
}

impl Display for SourceProject {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "\n\nProject source\n\n-path: {}\n-modules:\n{:#?}",
            // already a known PathBuf, unwrapping it should be fine
            self.root.to_str().unwrap(),
            self.sources
        )
    }
}

/// Raw code's module object.
///
#[derive(Debug)]
pub struct SourceModule {
    pub path: PathBuf,
    pub raw_code: String
}

impl SourceModule {
    pub fn new(path: &str) -> Self {
        if !path.is_empty() {
            return match SourceModule::read_file(&path) {
                Ok(raw_code) => {
                    let path_buf = PathBuf::from(path);
                    if path_buf.is_file() {
                        Self { path: path_buf, raw_code }
                    }
                    else { panic!("\"{}\" is not a file to load module source", path) }
                },
                Err(err) => panic!("{} {}", err, path)
            }
        }
        panic!("provided path for module source is empty.")
    }

    fn read_file(path: &str) -> Result<String, ModuleError> {
        match read_to_string(path) {
            Ok(x) => Ok(x),
            Err(_) => Err(ModuleError::CannotReadFile)
        }
    }
}

impl Display for SourceModule {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Module\n-path:{:?}\n-code:\n{}",
            self.path,
            self.raw_code
        )
    }
}

/// Unresolved project.
/// The project set after [`SourceProject`] during the first compilation pass.
///
pub struct UnresolvedProject {
    pub modules: Vec<UnresolvedModule>
}


/// Unresolved imports for H-hat Intermediate Representation (HIR).
///
pub enum UnresolvedImports {
    Consts,
    Types,
    Fns,
    Modifiers,
    MetaFns,
}

/// Unresolved constant definition.
///
pub struct UConstDef {

}


/// Unresolved type definition.
///
pub struct UTypeDef {

}

/// Unresolved function definition.
///
pub struct UFnDef {

}

/// Unresolved cast definition.
///
pub struct UCastDef {

}


/// Unresolved modifier definition.
///
pub struct UModifierDef {

}


/// Unresolved meta-functions definition.
///
pub struct UMetaFnDef {

}


/// Unresolved groups definition.
/// First IR generated.
///
pub enum UGroupDef {
    Fns(Vec<UFnDef>),
    Casts(Vec<UCastDef>),
    Modifiers(Vec<UModifierDef>),
    MetaFns(Vec<UMetaFnDef>)
}


/// Content inside a [`UnresolvedModule`].
/// First content generated, yet unresolved.
///
pub enum UnresolvedContent {
    Consts(Vec<UConstDef>),
    Types(Vec<UTypeDef>),
    /// Groups include unresolved function, cast, modifier or meta-functions
    Groups(UGroupDef),
}


/// Unresolved module for H-hat Intermediate Representation (HIR).
/// First generated IR module.
/// It is the parsing step (first compilation pass) from raw text to parsed code.
///
pub struct UnresolvedModule {
    pub id: ModuleId,
    pub path: PathBuf,
    pub imports: UnresolvedImports,
    pub content: UnresolvedContent
}


/// Project object for the second compilation pass.
/// Holds [`MappedModule`]s.
///
pub struct MappedProject {
    pub modules: Vec<MappedModule>
}


/// Module object where symbols are linked, types are resolved, but
/// meta-functions are not addressed and lazy plans are not resolved.
///
pub struct MappedModule {
    pub id: ModuleId,
}


/// Tests for some sanity checks
#[cfg(test)]
mod tests {
    use std::path::PathBuf;
    use crate::ir::project::SourceProject;

    /// TODO: replace the python path for an independent place to retrieve
    ///  hat code for debugging and checking purposes.
    ///
    /// Common path containing hat files for test purposes.
    const PATH: &str = "../../python/tests/dialects/heather/parsing/parse-test/";

    #[test]
    fn check_project_source() {
        assert!(PathBuf::from(PATH).exists());
        let ps = SourceProject::new(PATH);
        println!("{}", ps);
        assert!(!ps.is_empty());

    }
}