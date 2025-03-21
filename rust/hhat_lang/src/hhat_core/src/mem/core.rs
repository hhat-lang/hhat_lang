use crate::mem::defs::{BlockSize, ALIGNMENT, MAX_MEMBLOCK_SIZE};
use std::alloc::{alloc, dealloc, Layout};
use std::mem::size_of_val;
use std::ptr::{read, write, NonNull};

/// A holder for memory block, its pointer in the [`std::alloc::GlobalAlloc`],
/// the default alignment and its total size
pub struct MemBlock {
    ptr: NonNull<u8>,
    size: BlockSize,
    align: usize,
}

impl MemBlock {
    /// create a new memory block with a given size (smaller than [`MAX_MEMBLOCK_SIZE`]
    /// and power of two), and alignment size (power of two).
    pub unsafe fn new(size: BlockSize, align: usize) -> Result<MemBlock, MemAllocError> {
        if size > MAX_MEMBLOCK_SIZE {
            return Err(MemAllocError::InvalidBlockSize);
        }

        let layout: Layout = match Layout::from_size_align(size, align) {
            Ok(layout) => layout,
            Err(_) => return Err(MemAllocError::LayoutError),
        };
        let ptr: *mut u8 = alloc(layout);

        if ptr.is_null() {
            Err(MemAllocError::NullPointer)
        } else {
            Ok(MemBlock {
                ptr: NonNull::new_unchecked(ptr),
                size,
                align,
            })
        }
    }

    pub unsafe fn free(&mut self) -> Result<MemAllocSuccess, MemAllocError> {
        let layout: Layout = match Layout::from_size_align(self.size, ALIGNMENT) {
            Ok(layout) => layout,
            Err(_) => return Err(MemAllocError::LayoutError),
        };

        dealloc(self.ptr.as_ptr(), layout);
        Ok(MemAllocSuccess::MemoryFreed)
    }

    pub fn as_ptr(&self) -> *const u8 {
        self.ptr.as_ptr()
    }

    /// Push data `T` to the memory block and returns its pointer position
    pub unsafe fn push<T>(&mut self, data: T) -> Result<usize, MemAllocError> {
        let offset: usize = size_of_val(&data);
        let ptr: *mut T = self.as_ptr().add(offset) as *mut T;

        if (ptr as usize) <= (self.as_ptr().add(self.size) as usize) {
            write(ptr, data);
            Ok(ptr as usize)
        } else {
            Err(MemAllocError::MemoryOverflow)
        }
    }

    /// Pops the last item from the memory. Because [`MemBlock`] is just a struct
    /// to hold data and its pointer at the [`std::alloc::GlobalAlloc`], it doesn't
    /// know where the last item is. It's up to the API above to define it, such as
    /// stack memory or a heap memory struct.
    ///
    /// It returns a tuple as the data, the data size, and the updated cursor pointer.
    pub unsafe fn pop<T: Clone + Copy>(
        &mut self,
        cursor_ptr: usize,
    ) -> Result<(T, usize, usize), MemAllocError> {
        // read the data from the allocated memory space given a cursor pointer
        let data: T = read(cursor_ptr as *const T);

        let data_size: usize = size_of_val(&data);
        // get the new pointer position subtracted from the data memory space
        let new_cursor_ptr: usize = (cursor_ptr as *const u8).sub(data_size) as usize;

        // the pointer handler (that called this very function) now has an updated
        // pointer to use as its new cursor, for instance.
        Ok((data, data_size, new_cursor_ptr))
    }

    /// Take a look at the data at some pointer position in th memory. The API calling
    /// it should handle the right pointer position (the last written data, for a stack
    /// memory API, for instance). The pointer is not updated since it's just peeking
    /// into the memory.
    pub unsafe fn peek<T>(&mut self, ptr: usize) -> T {
        // let mem_ptr: *const T = self.as_ptr().add(ptr) as *const T;
        // read(mem_ptr)
        read(ptr as *const T)
    }
}

impl Drop for MemBlock {
    fn drop(&mut self) {
        unsafe {
            let _ = self.free();
        }
    }
}

#[derive(Debug)]
pub enum MemAllocError {
    EmptyMemory,
    InvalidBlockSize,
    InvalidAlignment,
    LayoutError,
    MemoryOverflow,
    NotEnoughMemory,
    NotPowerOfTwo,
    NullPointer,
}

#[derive(Debug)]
pub enum MemAllocSuccess {
    MemoryFreed,
    DataPushedToMemory,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_memblock_alloc() {
        unsafe {
            println!("== simple memblock alloc ==");

            let max_size = MAX_MEMBLOCK_SIZE;
            assert!(max_size == MAX_MEMBLOCK_SIZE);

            let mut memblock = MemBlock::new(max_size, 8usize).unwrap();
            let data_ptr = memblock.push(1u64).unwrap();
            assert!(
                memblock.as_ptr().add(size_of_val(&1u64)) <= memblock.as_ptr().add(memblock.size)
            );

            let retrieved_data = memblock.peek::<u64>(data_ptr);
            assert_eq!(retrieved_data, 1u64);

            let (d, ds, p) = match memblock.pop::<u64>(data_ptr) {
                Ok((x, y, z)) => (x, y, z),
                Err(e) => panic!("{:?}", e),
            };
            assert_eq!(d, 1u64);
            assert_eq!(ds, 8);
            assert_eq!(p, memblock.as_ptr() as usize);

            println!(" - memblock");
            println!("   - ptr: {}", memblock.as_ptr() as usize);
            println!("   - input data: {}", 1u64);
            println!("   - push ptr: {:}", data_ptr);
            println!("   - peek data: {:}", retrieved_data);
            println!("   - pop data:");
            println!("   -   - retrieved data: {:}", d);
            println!("   -   - retrieved data size: {:}", ds);
            println!("   -   - retrieved new pointer: {:}", p);
            println!("=====================");
        }
    }
}
