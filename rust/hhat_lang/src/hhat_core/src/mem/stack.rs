use crate::mem::alloc::AllocError;
use crate::mem::base::MemBlock;

/// Stack memory
///
/// To create a new `Stack`, use `Stack::new(size)` where `size` must be power
/// of two, `usize` type and bounded to [`crate::mem::defs::MAX_MEMBLOCK_SIZE`]
pub struct Stack {
    memblock: MemBlock,
}

impl Stack {
    pub fn new(size: usize) -> Result<Self, StackError> {
        match MemBlock::new(size) {
            Ok(memblock) => Ok(Stack { memblock }),
            Err(x) => match x {
                AllocError::ConstraintsNotSatisfied => Err(StackError::LayoutError),
                AllocError::InvalidAlignment => Err(StackError::InvalidAlignment),
                AllocError::InvalidBlockSize => Err(StackError::InvalidBlockSize),
                AllocError::MemoryAlreadyFreed => Err(StackError::MemoryAlreadyFreed),
                AllocError::NotEnoughMemory => Err(StackError::NotEnoughMemory),
                AllocError::NotPowerOfTwo => Err(StackError::SizeNotPowerOfTwo),
                AllocError::NullPointer => Err(StackError::NullPointer),
            },
        }
    }
}

pub enum StackError {
    InvalidBlockSize,
    InvalidAlignment,
    LayoutError,
    MemoryAlreadyFreed,
    NotEnoughMemory,
    NullPointer,
    SizeNotPowerOfTwo,
}
