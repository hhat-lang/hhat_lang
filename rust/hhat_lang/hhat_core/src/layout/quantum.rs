use crate::frontend::types::TyPrimitive;
use crate::SymbolId;


#[derive(Clone, Debug)]
pub enum QuantumLayout {
    Primitive(TyPrimitive),
    Struct(SymbolId, Vec<QuantumField>),
    Enum(SymbolId, [SymbolId; 2]),
}

impl QuantumLayout {
    pub fn qubits(&self) -> u32 {
        match self {
            QuantumLayout::Primitive(p) => primitive_qubits(p),
            QuantumLayout::Struct(_, fields) => fields.iter().map(|f| f.layout.qubits()).sum(),
            QuantumLayout::Enum(..) => 1,
        }
    }

    pub fn field(&self, name: &SymbolId) -> Option<&QuantumField> {
        match self {
            QuantumLayout::Struct(_, fields) => fields.iter().find(|f| f.name == *name),
            _ => None,
        }
    }
}


#[derive(Clone, Debug)]
pub struct QuantumField {
    pub name: SymbolId,
    pub offset: u32,
    pub layout: QuantumLayout,
}


pub fn primitive_qubits(ty: &TyPrimitive) -> u32 {
    match ty {
        TyPrimitive::QBool => 1,
        TyPrimitive::QU2 => 2,
        TyPrimitive::QU3 => 3,
        TyPrimitive::QU4 => 4,
        TyPrimitive::QU8 => 8,
        TyPrimitive::Bool
        | TyPrimitive::U32
        | TyPrimitive::U64
        | TyPrimitive::I32
        | TyPrimitive::I64
        | TyPrimitive::F32
        | TyPrimitive::F64
        | TyPrimitive::C64
        | TyPrimitive::C128
        | TyPrimitive::String => 0,
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    fn qsym(pos: u32) -> SymbolId {
        SymbolId(pos, true)
    }

    #[test]
    fn primitive_qubit_counts() {
        assert_eq!(primitive_qubits(&TyPrimitive::QBool), 1);
        assert_eq!(primitive_qubits(&TyPrimitive::QU2), 2);
        assert_eq!(primitive_qubits(&TyPrimitive::QU3), 3);
        assert_eq!(primitive_qubits(&TyPrimitive::QU4), 4);
        assert_eq!(primitive_qubits(&TyPrimitive::QU8), 8);
    }

    #[test]
    fn qubits_and_field_for_each_kind() {
        assert_eq!(QuantumLayout::Primitive(TyPrimitive::QU4).qubits(), 4);
        assert_eq!(QuantumLayout::Enum(qsym(0), [qsym(1), qsym(2)]).qubits(), 1);

        let s = QuantumLayout::Struct(
            qsym(0),
            vec![
                QuantumField {
                    name: qsym(1),
                    offset: 0,
                    layout: QuantumLayout::Primitive(TyPrimitive::QBool),
                },
                QuantumField {
                    name: qsym(2),
                    offset: 1,
                    layout: QuantumLayout::Primitive(TyPrimitive::QU4),
                },
            ],
        );
        assert_eq!(s.qubits(), 5);
        assert_eq!(s.field(&qsym(2)).unwrap().offset, 1);
        assert!(s.field(&qsym(9)).is_none());
    }
}
