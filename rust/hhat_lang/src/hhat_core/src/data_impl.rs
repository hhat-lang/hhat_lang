/// Data that lives in the Heap
pub trait HeapData {
    fn new(&mut self) -> Self;
    fn get_data<T>(&mut self) -> Option<T>;
    fn get_last<T>(&mut self) -> Option<T>;
}

/// Type content that lives in the IRa
pub trait TypeDataIRa {}
