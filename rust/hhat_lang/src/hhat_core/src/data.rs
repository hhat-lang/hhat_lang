
/// Data that lives in the Heap
pub trait HeapData {
    fn new(&mut self) -> Self;
    fn get_data<T>(&mut self) -> Option<T>;
    fn get_last<T>(&mut self) -> Option<T>;
}


/// To be implemented by classical and quantum instructions
pub trait CodeInstr<'a> {
    fn new(&mut self) -> Self;
    fn push<T>(&mut self, value: &T) -> Self;
    fn get<T>(&mut self) -> Option<&T>;
}