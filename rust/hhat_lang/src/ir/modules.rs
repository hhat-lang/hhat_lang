use std::env;
use crate::ir::ids::Path;
use crate::ir::hir::{Content, Imports};

/// module for HIR.
/// First module produced for the HIR.
///
pub struct HIRModule {
    /// module name as a vector of strings (`(dir(,dir)*,)*file_name`)
    pub name: Path,
    pub imports: Vec<Imports>,
    pub content: Content
}


impl HIRModule {
    pub fn new(path: String) -> Self {
        todo!()
    }

    fn string_to_vec(path_str: &String) -> Vec<String> {
        let x: Vec<String> = path_str.split("/")
            .filter_map(|x| Some(String::from(x)))
            .collect();
        x
    }

}


#[cfg(test)]
mod tests {
    use crate::ir::modules::HIRModule;

    #[test]
    fn split_string() {
        let path_str = String::from("some/dir/like/str");
        let res = HIRModule::string_to_vec(&path_str);
        println!("{:?}", res);

    }
}