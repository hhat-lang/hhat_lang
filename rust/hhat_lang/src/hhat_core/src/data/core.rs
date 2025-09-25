

pub enum Item {
    Atomic,
    Symbol,
    Literal,
    CompositeSymbol,
    CompositeLiteral,
    CompositeMix,
}

pub struct WorkingDataItem {
    data: Item,
    value: String,
    data_type: String,
    is_quantum: bool,
    suppress_type: bool,
}


pub trait WorkingData {
    fn new();
    fn push();
    fn pop();
    fn free();

    fn is_quantum(&self) -> bool;
}
