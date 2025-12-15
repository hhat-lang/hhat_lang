use crate::utils::FullName;

pub struct TypeContainer {
    fullname: FullName,
    type_ds: TypeDataStructure,
}

/// Define the type container structure
pub trait TypeTemplate {
    fn new() -> Self;
    fn get_type() -> FullName;
    fn ir_alloc(&mut self);
}

type TypeFullName = FullName;

pub struct SingleType {
    fullname: FullName,
    datatype: TypeFullName,
    data: (),
}

impl SingleType {
    pub fn assign_data<T>(&mut self, data: T) {}
}

/// Type data structure for composing types. It can be
/// - `Single`: as `u16` or `bool`, they are simple, single-valued types.
/// - `Struct`: similar to `struct` in C or Rust, hold members as a name + type.
/// - `Enum`: similar to `enum` in Rust, can contain constant members or structs.
/// - `Union`: similar to `union` in C or Rust, holds members as a name + type, but
///     con only assign one of its members at once.
pub enum TypeDataStructure {
    Single,
    Struct(StructType),
    Enum { members: Vec<EnumMember> },
    Union { members: Vec<UnionMember> },
}


enum ConstantMember {
    Constant,
}

struct StructType {
    members: Vec<(String, TypeFullName)>,
}

enum EnumMember {
    Constant(ConstantMember),
    Struct(StructType),
}

enum UnionMember {
    Constant(ConstantMember),
    Struct(StructType),
    Enum(EnumMember),
}
