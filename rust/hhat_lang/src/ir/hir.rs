pub struct HIR {

}

pub enum ModuleKind {
    Consts,
    Types,
    Fns,
}


enum ModuleImports {
    Consts,
    Types,
    Fns,
    MetaFns,
    Modifiers
}


pub struct ModuleHIR<T> {
    imports: ModuleImports,
    module: Option<T>,
    module_type: ModuleKind,
}


pub struct Fn {

}

pub struct Block {

}


pub struct Instr {

}

pub struct Terminator {

}

pub struct Value {

}

pub struct Place {

}
