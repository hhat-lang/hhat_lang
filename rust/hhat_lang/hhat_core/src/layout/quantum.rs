//!
//! Quantum memory layouts for quantum data.
//!
//! Quantum layouts are intentionally separate from classical layouts: quantum
//! primitives stay zero-sized in Cranelift-facing layouts, while this module
//! tracks required qubits and ancilla for quantum code generation.
//!

use std::collections::HashMap;

use crate::core::{ArenaIndexHolder, Arenable};
use crate::frontend::types::{Ty, TyArrayKind, TyEnum, TyPrimitive, TyStruct};
use crate::layout::base::TypeLayout;
use crate::SymbolId;

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum QuantumLayoutError {
    ClassicalType(String),
    TypeLayoutMismatch {
        expected: &'static str,
        found: &'static str,
    },
    DynamicQuantumArray,
    UnsupportedTypeLayout(&'static str),
    UnsupportedEnumVariantCount {
        variants: usize,
    },
    MissingCachedLayout(String),
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum QuantumLayoutKind {
    Primitive,
    Struct {
        members: Vec<QuantumMemberLayout>,
    },
    Enum {
        variants: Vec<QuantumVariantLayout>,
    },
    Array {
        element: Box<QuantumTypeLayout>,
        length: u32,
    },
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct QuantumTypeLayout {
    pub qubits: u32,
    pub kind: QuantumLayoutKind,
}

impl QuantumTypeLayout {
    pub fn primitive(qubits: u32) -> Self {
        Self {
            qubits,
            kind: QuantumLayoutKind::Primitive,
        }
    }

    pub fn total_qubits(&self) -> u32 {
        self.qubits
    }

    /// Builds a quantum layout for a type that has already passed classical layout.
    ///
    /// The classical TypeLayout is deliberately only used to validate the
    /// layout kind. It does not carry qubit widths because quantum data must
    /// stay separate from Cranelift-facing byte layouts.
    pub fn from_type_layout(ty: &Ty, type_layout: &TypeLayout) -> Result<Self, QuantumLayoutError> {
        validate_type_layout_kind(ty, type_layout)?;
        QuantumLayoutCache::new().layout_of(ty)
    }
}

impl Arenable for QuantumTypeLayout {}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct QuantumMemberLayout {
    pub name: SymbolId,
    pub offset: u32,
    pub layout: QuantumTypeLayout,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct QuantumVariantLayout {
    pub name: SymbolId,
    pub discriminant: u32,
}

fn primitive_quantum_width(primitive: &TyPrimitive) -> Option<u32> {
    match primitive {
        TyPrimitive::QBool => Some(1),
        TyPrimitive::QU2 => Some(2),
        TyPrimitive::QU3 => Some(3),
        TyPrimitive::QU4 => Some(4),
        TyPrimitive::QU8 => Some(8),
        _ => None,
    }
}

fn is_quantum_type(ty: &Ty) -> bool {
    match ty {
        Ty::Primitive(primitive) => primitive_quantum_width(primitive).is_some(),
        Ty::Struct(s) => s.name.is_quantum(),
        Ty::Enum(e) => e.name.is_quantum(),
        Ty::Array(a) => is_quantum_type(a.element.as_ref()),
    }
}

fn type_name(ty: &Ty) -> &'static str {
    match ty {
        Ty::Primitive(_) => "primitive",
        Ty::Struct(_) => "struct",
        Ty::Enum(_) => "enum",
        Ty::Array(_) => "array",
    }
}

fn type_layout_name(type_layout: &TypeLayout) -> &'static str {
    match type_layout {
        TypeLayout::Primitive(_, _) => "primitive",
        TypeLayout::Struct(_, _) => "struct",
        TypeLayout::Enum(_, _) => "enum",
        TypeLayout::Array(_, _) => "array",
    }
}

fn validate_type_layout_kind(ty: &Ty, type_layout: &TypeLayout) -> Result<(), QuantumLayoutError> {
    let matches_kind = matches!(
        (ty, type_layout),
        (Ty::Primitive(_), TypeLayout::Primitive(_, _))
            | (Ty::Struct(_), TypeLayout::Struct(_, _))
            | (Ty::Enum(_), TypeLayout::Enum(_, _))
            | (Ty::Array(_), TypeLayout::Array(_, _))
    );

    if matches_kind {
        Ok(())
    } else {
        Err(QuantumLayoutError::TypeLayoutMismatch {
            expected: type_name(ty),
            found: type_layout_name(type_layout),
        })
    }
}

#[derive(Clone, Debug, Default)]
pub struct QuantumLayoutCache {
    cache: HashMap<Ty, QuantumTypeLayout>,
}

impl QuantumLayoutCache {
    pub fn new() -> Self {
        Self {
            cache: HashMap::new(),
        }
    }

    pub fn has(&self, ty: &Ty) -> bool {
        self.cache.contains_key(ty)
    }

    pub fn layout_of(&mut self, ty: &Ty) -> Result<QuantumTypeLayout, QuantumLayoutError> {
        if !self.cache.contains_key(ty) {
            let layout = self.build_layout(ty)?;
            self.cache.insert(ty.clone(), layout);
        }

        self.cache
            .get(ty)
            .cloned()
            .ok_or_else(|| QuantumLayoutError::MissingCachedLayout(format!("{ty:?}")))
    }

    pub fn insert_type_layout(
        &mut self,
        ty: Ty,
        type_layout: &TypeLayout,
    ) -> Result<QuantumTypeLayout, QuantumLayoutError> {
        let layout = QuantumTypeLayout::from_type_layout(&ty, type_layout)?;
        self.cache.insert(ty, layout.clone());
        Ok(layout)
    }

    fn build_layout(&mut self, ty: &Ty) -> Result<QuantumTypeLayout, QuantumLayoutError> {
        match ty {
            Ty::Primitive(primitive) => primitive_quantum_width(primitive)
                .map(QuantumTypeLayout::primitive)
                .ok_or_else(|| QuantumLayoutError::ClassicalType(format!("{ty:?}"))),
            Ty::Struct(s) => self.layout_struct(s),
            Ty::Enum(e) => self.layout_enum(e),
            Ty::Array(a) => match a.kind {
                TyArrayKind::Static(length) => {
                    let element_layout = self.layout_of(a.element.as_ref())?;

                    Ok(QuantumTypeLayout {
                        qubits: element_layout.qubits * length,
                        kind: QuantumLayoutKind::Array {
                            element: Box::new(element_layout),
                            length,
                        },
                    })
                }
                TyArrayKind::Dynamic => Err(QuantumLayoutError::DynamicQuantumArray),
            },
        }
    }

    fn layout_struct(&mut self, ty: &TyStruct) -> Result<QuantumTypeLayout, QuantumLayoutError> {
        if !ty.name.is_quantum() {
            return Err(QuantumLayoutError::ClassicalType(format!("{ty:?}")));
        }

        let mut offset = 0;
        let mut members = Vec::with_capacity(ty.members.len());

        for (name, member_ty) in ty.iter() {
            if !is_quantum_type(member_ty) {
                // Classical members in a quantum struct do not consume qubits.
                continue;
            }

            let layout = self.layout_of(member_ty)?;
            members.push(QuantumMemberLayout {
                name: name.clone(),
                // Offsets are relative to this struct; emitters add parent offsets.
                offset,
                layout: layout.clone(),
            });
            offset += layout.qubits;
        }

        if members.is_empty() {
            return Err(QuantumLayoutError::ClassicalType(format!("{ty:?}")));
        }

        Ok(QuantumTypeLayout {
            qubits: offset,
            kind: QuantumLayoutKind::Struct { members },
        })
    }

    fn layout_enum(&mut self, ty: &TyEnum) -> Result<QuantumTypeLayout, QuantumLayoutError> {
        if !ty.name.is_quantum() {
            return Err(QuantumLayoutError::ClassicalType(format!("{ty:?}")));
        }

        if ty.variants.len() != 2 {
            return Err(QuantumLayoutError::UnsupportedEnumVariantCount {
                variants: ty.variants.len(),
            });
        }

        let variants = ty
            .iter()
            .enumerate()
            .map(|(idx, variant)| QuantumVariantLayout {
                name: variant.name().clone(),
                discriminant: idx as u32,
            })
            .collect();

        Ok(QuantumTypeLayout {
            qubits: 1,
            kind: QuantumLayoutKind::Enum { variants },
        })
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct QuantumVariableLayout {
    pub root: SymbolId,
    pub offset: u32,
    pub layout: QuantumTypeLayout,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct CastedQuantumAttribute {
    pub root: SymbolId,
    pub attribute: SymbolId,
    pub qubits: u32,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct QuantumInstructionLayout {
    pub name: SymbolId,
    pub operand_qubits: u32,
    pub ancilla_qubits: u32,
    pub classical_registers: u32,
}

#[derive(Clone, Debug, Default)]
pub struct QuantumProgram {
    pub variables: Vec<QuantumVariableLayout>,
    pub instructions: Vec<QuantumInstructionLayout>,
    pub casted_attributes: Vec<CastedQuantumAttribute>,
}

impl QuantumProgram {
    pub fn new() -> Self {
        Self {
            variables: Vec::new(),
            instructions: Vec::new(),
            casted_attributes: Vec::new(),
        }
    }

    pub fn from_variable(
        root: SymbolId,
        ty: &Ty,
        type_layouts: &mut QuantumLayoutCache,
    ) -> Result<Self, QuantumLayoutError> {
        let mut program = Self::new();
        program.add_variable(root, ty, type_layouts)?;
        Ok(program)
    }

    pub fn add_variable(
        &mut self,
        root: SymbolId,
        ty: &Ty,
        type_layouts: &mut QuantumLayoutCache,
    ) -> Result<&QuantumVariableLayout, QuantumLayoutError> {
        let layout = type_layouts.layout_of(ty)?;

        Ok(self.add_variable_layout(root, layout))
    }

    pub fn add_variable_layout(
        &mut self,
        root: SymbolId,
        layout: QuantumTypeLayout,
    ) -> &QuantumVariableLayout {
        let offset = self.qubits();

        self.variables.push(QuantumVariableLayout {
            root,
            offset,
            layout,
        });

        self.variables.last().expect("pushed quantum variable")
    }

    pub fn add_variable_from_type_layout(
        &mut self,
        root: SymbolId,
        ty: &Ty,
        type_layout: &TypeLayout,
    ) -> Result<&QuantumVariableLayout, QuantumLayoutError> {
        let layout = QuantumTypeLayout::from_type_layout(ty, type_layout)?;
        Ok(self.add_variable_layout(root, layout))
    }

    pub fn add_instruction(
        &mut self,
        name: SymbolId,
        operand_qubits: u32,
        ancilla_qubits: u32,
    ) -> &QuantumInstructionLayout {
        self.add_instruction_with_registers(name, operand_qubits, ancilla_qubits, 0)
    }

    /// Adds an instruction and any classical registers it explicitly reserves.
    ///
    /// If the same measured qubits are also recorded through [`Self::add_casted_attribute`], then
    /// [`Self::classical_registers`] will count both reservations.
    pub fn add_instruction_with_registers(
        &mut self,
        name: SymbolId,
        operand_qubits: u32,
        ancilla_qubits: u32,
        classical_registers: u32,
    ) -> &QuantumInstructionLayout {
        self.instructions.push(QuantumInstructionLayout {
            name,
            operand_qubits,
            ancilla_qubits,
            classical_registers,
        });

        self.instructions
            .last()
            .expect("pushed quantum instruction layout")
    }

    /// Records a casted quantum attribute's classical register width.
    ///
    /// If the same measured qubits are also reserved on an instruction, then
    /// [`Self::classical_registers`] will count both reservations.
    pub fn add_casted_attribute(
        &mut self,
        root: SymbolId,
        attribute: SymbolId,
        ty: &Ty,
        type_layouts: &mut QuantumLayoutCache,
    ) -> Result<&CastedQuantumAttribute, QuantumLayoutError> {
        let layout = type_layouts.layout_of(ty)?;

        self.casted_attributes.push(CastedQuantumAttribute {
            root,
            attribute,
            qubits: layout.qubits,
        });

        Ok(self
            .casted_attributes
            .last()
            .expect("pushed casted quantum attribute"))
    }

    /// Records a casted quantum attribute's classical register width from a cached type layout.
    ///
    /// If the same measured qubits are also reserved on an instruction, then
    /// [`Self::classical_registers`] will count both reservations.
    pub fn add_casted_attribute_from_type_layout(
        &mut self,
        root: SymbolId,
        attribute: SymbolId,
        ty: &Ty,
        type_layout: &TypeLayout,
    ) -> Result<&CastedQuantumAttribute, QuantumLayoutError> {
        let layout = QuantumTypeLayout::from_type_layout(ty, type_layout)?;

        self.casted_attributes.push(CastedQuantumAttribute {
            root,
            attribute,
            qubits: layout.qubits,
        });

        Ok(self
            .casted_attributes
            .last()
            .expect("pushed casted quantum attribute"))
    }

    pub fn qubits(&self) -> u32 {
        self.variables.iter().map(|v| v.layout.qubits).sum()
    }

    pub fn ancilla_qubits(&self) -> u32 {
        self.instructions.iter().map(|i| i.ancilla_qubits).sum()
    }

    /// Counts casted attribute widths plus classical registers reserved explicitly by instructions.
    ///
    /// Callers should account for each measured qubit through exactly one of those paths.
    pub fn classical_registers(&self) -> u32 {
        let cast_registers: u32 = self.casted_attributes.iter().map(|c| c.qubits).sum();
        let instruction_registers: u32 = self
            .instructions
            .iter()
            .map(|i| i.classical_registers)
            .sum();

        cast_registers + instruction_registers
    }

    pub fn total_qubits(&self) -> u32 {
        self.qubits() + self.ancilla_qubits()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::frontend::types::{TyArray, TyPrimitive};
    use crate::layout::arch::Arch;
    use crate::layout::base::LayoutCache;

    fn sid(index: u32) -> SymbolId {
        SymbolId(index, false)
    }

    fn qsid(index: u32) -> SymbolId {
        SymbolId(index, true)
    }

    fn initialized_layout_cache() -> LayoutCache {
        let arch = Arch::get_arch64();
        let mut cache = LayoutCache::new(arch);
        cache.initialize(Some(arch));
        cache
    }

    fn bell_ty() -> Ty {
        let mut ty = TyStruct::new(&qsid(0));
        ty.add_member(&qsid(1), Ty::Primitive(TyPrimitive::QBool));
        ty.add_member(&qsid(2), Ty::Primitive(TyPrimitive::QBool));
        ty.done();
        Ty::Struct(ty)
    }

    #[test]
    fn primitive_quantum_types_use_expected_qubits() {
        let mut cache = QuantumLayoutCache::new();

        assert_eq!(
            cache
                .layout_of(&Ty::Primitive(TyPrimitive::QBool))
                .unwrap()
                .qubits,
            1
        );
        assert_eq!(
            cache
                .layout_of(&Ty::Primitive(TyPrimitive::QU2))
                .unwrap()
                .qubits,
            2
        );
        assert_eq!(
            cache
                .layout_of(&Ty::Primitive(TyPrimitive::QU8))
                .unwrap()
                .qubits,
            8
        );
    }

    #[test]
    fn quantum_struct_members_stack_without_padding() {
        let mut ty = TyStruct::new(&qsid(0));
        ty.add_member(&qsid(1), Ty::Primitive(TyPrimitive::QBool));
        ty.add_member(&qsid(2), Ty::Primitive(TyPrimitive::QU3));
        ty.done();

        let layout = QuantumLayoutCache::new()
            .layout_of(&Ty::Struct(ty))
            .unwrap();

        assert_eq!(layout.qubits, 4);

        let QuantumLayoutKind::Struct { members } = layout.kind else {
            panic!("expected quantum struct layout")
        };

        assert_eq!(members[0].offset, 0);
        assert_eq!(members[1].offset, 1);
        assert_eq!(members[1].layout.qubits, 3);
    }

    #[test]
    fn all_classical_quantum_structs_are_rejected_on_both_paths() {
        let mut ty = TyStruct::new(&qsid(0));
        ty.add_member(&sid(1), Ty::Primitive(TyPrimitive::Bool));
        ty.done();
        let ty = Ty::Struct(ty);

        assert!(matches!(
            QuantumLayoutCache::new().layout_of(&ty),
            Err(QuantumLayoutError::ClassicalType(_))
        ));

        let mut layout_cache = initialized_layout_cache();
        layout_cache.insert_layout(&ty, &Some(Arch::get_arch64()));
        let type_layout = layout_cache.layout_of(&ty);

        assert!(matches!(
            QuantumTypeLayout::from_type_layout(&ty, &type_layout),
            Err(QuantumLayoutError::ClassicalType(_))
        ));
    }

    #[test]
    fn nested_quantum_structs_recurse() {
        let mut inner = TyStruct::new(&qsid(0));
        inner.add_member(&qsid(1), Ty::Primitive(TyPrimitive::QBool));
        inner.add_member(&qsid(2), Ty::Primitive(TyPrimitive::QBool));
        inner.done();

        let mut enum_ty = TyEnum::new(&qsid(6));
        enum_ty.add_variant(&qsid(7), None);
        enum_ty.add_variant(&qsid(8), None);
        enum_ty.done();

        let mut outer = TyStruct::new(&qsid(3));
        outer.add_member(&qsid(4), Ty::Struct(inner));
        outer.add_member(&qsid(5), Ty::Enum(enum_ty));
        outer.add_member(&qsid(9), Ty::Primitive(TyPrimitive::QU4));
        outer.done();

        let layout = QuantumLayoutCache::new()
            .layout_of(&Ty::Struct(outer))
            .unwrap();

        assert_eq!(layout.qubits, 7);
    }

    #[test]
    fn two_variant_quantum_enum_uses_one_qubit() {
        let mut ty = TyEnum::new(&qsid(0));
        ty.add_variant(&qsid(1), None);
        ty.add_variant(&qsid(2), None);
        ty.done();

        let layout = QuantumLayoutCache::new().layout_of(&Ty::Enum(ty)).unwrap();

        assert_eq!(layout.qubits, 1);
    }

    #[test]
    fn static_quantum_array_multiplies_element_layout() {
        let ty = Ty::Array(TyArray::new_static(Ty::Primitive(TyPrimitive::QU2), 3));

        let layout = QuantumLayoutCache::new().layout_of(&ty).unwrap();

        assert_eq!(layout.qubits, 6);
    }

    #[test]
    fn quantum_program_collects_variables_ancilla_and_cast_registers() {
        let mut cache = QuantumLayoutCache::new();
        let mut program = QuantumProgram::new();

        program
            .add_variable(qsid(0), &Ty::Primitive(TyPrimitive::QU4), &mut cache)
            .unwrap();
        program.add_instruction(sid(10), 4, 2);
        program
            .add_casted_attribute(
                qsid(0),
                qsid(1),
                &Ty::Primitive(TyPrimitive::QBool),
                &mut cache,
            )
            .unwrap();

        assert_eq!(program.qubits(), 4);
        assert_eq!(program.ancilla_qubits(), 2);
        assert_eq!(program.classical_registers(), 1);
        assert_eq!(program.total_qubits(), 6);
    }

    #[test]
    fn quantum_program_counts_instruction_classical_registers() {
        let mut cache = QuantumLayoutCache::new();
        let mut program = QuantumProgram::new();

        program
            .add_variable(qsid(0), &Ty::Primitive(TyPrimitive::QU2), &mut cache)
            .unwrap();
        program.add_instruction_with_registers(sid(10), 2, 1, 2);
        program
            .add_casted_attribute(
                qsid(0),
                qsid(1),
                &Ty::Primitive(TyPrimitive::QBool),
                &mut cache,
            )
            .unwrap();

        assert_eq!(program.ancilla_qubits(), 1);
        assert_eq!(program.classical_registers(), 3);
        assert_eq!(program.total_qubits(), 3);
    }

    #[test]
    fn type_layout_converts_to_quantum_layout() {
        let mut layout_cache = initialized_layout_cache();

        let primitive_ty = Ty::Primitive(TyPrimitive::QU4);
        let primitive_layout = layout_cache.layout_of(&primitive_ty);
        let quantum_primitive =
            QuantumTypeLayout::from_type_layout(&primitive_ty, &primitive_layout).unwrap();
        assert_eq!(quantum_primitive.qubits, 4);

        let bell_ty = bell_ty();
        layout_cache.insert_layout(&bell_ty, &Some(Arch::get_arch64()));
        let bell_type_layout = layout_cache.layout_of(&bell_ty);
        let quantum_bell =
            QuantumTypeLayout::from_type_layout(&bell_ty, &bell_type_layout).unwrap();
        assert_eq!(quantum_bell.qubits, 2);

        let QuantumLayoutKind::Struct { members } = quantum_bell.kind else {
            panic!("expected quantum struct layout")
        };

        assert_eq!(members[0].offset, 0);
        assert_eq!(members[1].offset, 1);

        let mut quantum_cache = QuantumLayoutCache::new();
        quantum_cache
            .insert_type_layout(bell_ty.clone(), &bell_type_layout)
            .unwrap();
        assert!(quantum_cache.has(&bell_ty));
    }

    #[test]
    fn type_layout_mixed_classical_quantum_struct_skips_classical_members() {
        let mut ty = TyStruct::new(&qsid(0));
        ty.add_member(&qsid(1), Ty::Primitive(TyPrimitive::QBool));
        ty.add_member(&sid(2), Ty::Primitive(TyPrimitive::Bool));
        ty.add_member(&qsid(3), Ty::Primitive(TyPrimitive::QU2));
        ty.done();

        let mut layout_cache = initialized_layout_cache();
        let ty = Ty::Struct(ty);
        layout_cache.insert_layout(&ty, &Some(Arch::get_arch64()));
        let type_layout = layout_cache.layout_of(&ty);
        let quantum_layout = QuantumTypeLayout::from_type_layout(&ty, &type_layout).unwrap();

        assert_eq!(quantum_layout.qubits, 3);

        let QuantumLayoutKind::Struct { members } = quantum_layout.kind else {
            panic!("expected quantum struct layout")
        };

        assert_eq!(members.len(), 2);
        assert_eq!(members[0].name, qsid(1));
        assert_eq!(members[0].offset, 0);
        assert_eq!(members[0].layout.qubits, 1);
        assert_eq!(members[1].name, qsid(3));
        assert_eq!(members[1].offset, 1);
        assert_eq!(members[1].layout.qubits, 2);
    }

    #[test]
    fn type_layout_nested_structs_recurse_with_relative_offsets() {
        let mut inner = TyStruct::new(&qsid(0));
        inner.add_member(&qsid(1), Ty::Primitive(TyPrimitive::QBool));
        inner.add_member(&qsid(2), Ty::Primitive(TyPrimitive::QBool));
        inner.done();
        let inner_ty = Ty::Struct(inner);

        let mut outer = TyStruct::new(&qsid(3));
        outer.add_member(&qsid(4), inner_ty.clone());
        outer.add_member(&qsid(5), Ty::Primitive(TyPrimitive::QU2));
        outer.done();
        let outer_ty = Ty::Struct(outer);

        let mut layout_cache = initialized_layout_cache();
        layout_cache.insert_layout(&inner_ty, &Some(Arch::get_arch64()));
        layout_cache.insert_layout(&outer_ty, &Some(Arch::get_arch64()));
        let type_layout = layout_cache.layout_of(&outer_ty);
        let quantum_layout = QuantumTypeLayout::from_type_layout(&outer_ty, &type_layout).unwrap();

        assert_eq!(quantum_layout.qubits, 4);

        let QuantumLayoutKind::Struct { members } = quantum_layout.kind else {
            panic!("expected quantum struct layout")
        };

        assert_eq!(members.len(), 2);
        assert_eq!(members[0].offset, 0);
        assert_eq!(members[0].layout.qubits, 2);
        assert_eq!(members[1].offset, 2);
        assert_eq!(members[1].layout.qubits, 2);
    }

    #[test]
    fn quantum_program_from_type_layout_sweeps_instruction_ancillas() {
        let mut layout_cache = initialized_layout_cache();
        let primitive_ty = Ty::Primitive(TyPrimitive::QU4);
        let primitive_layout = layout_cache.layout_of(&primitive_ty);
        let bell_ty = bell_ty();
        layout_cache.insert_layout(&bell_ty, &Some(Arch::get_arch64()));
        let bell_layout = layout_cache.layout_of(&bell_ty);
        let cast_ty = Ty::Primitive(TyPrimitive::QBool);
        let cast_layout = layout_cache.layout_of(&cast_ty);

        for (ty, type_layout, data_qubits) in [
            (primitive_ty, primitive_layout, 4),
            (bell_ty, bell_layout, 2),
        ] {
            for ancilla_qubits in 0..=3 {
                let mut program = QuantumProgram::new();
                program
                    .add_variable_from_type_layout(qsid(0), &ty, &type_layout)
                    .unwrap();
                program.add_instruction(sid(10), data_qubits, ancilla_qubits);
                program
                    .add_casted_attribute_from_type_layout(qsid(0), qsid(1), &cast_ty, &cast_layout)
                    .unwrap();

                assert_eq!(program.qubits(), data_qubits);
                assert_eq!(program.ancilla_qubits(), ancilla_qubits);
                assert_eq!(program.classical_registers(), 1);
                assert_eq!(program.total_qubits(), data_qubits + ancilla_qubits);
            }
        }
    }
}
