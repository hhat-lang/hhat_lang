use crate::mem::defs::{BlockSize, ALIGNMENT, MAX_MEMBLOCK_SIZE};
use std::alloc::{alloc, dealloc, Layout};
use std::mem::size_of_val;
use std::ptr::{read, write, NonNull};

/// A holder for memory block, its pointer in the [`std::alloc::GlobalAlloc`],
/// the default alignment and its total size.
///
/// The `MemBlock` implementation is basically all unsafe since we are dealing with
/// the raw memory directly here. Although it is being checked internally to make
/// sure things don't go wild, unsafe reinforces the awareness the handler code must
/// have when interacting with it.
pub struct MemBlock {
    ptr: NonNull<u8>,
    size: BlockSize,
    align: usize,
    is_freed: bool,
}

impl MemBlock {
    /// create a new memory block with a given size (smaller than [`MAX_MEMBLOCK_SIZE`]
    /// and power of two), and alignment size (power of two).
    pub unsafe fn new(size: BlockSize, align: usize) -> Result<MemBlock, MemAllocError> {
        // size must not exceed the maximum permitted block size
        if size > MAX_MEMBLOCK_SIZE {
            return Err(MemAllocError::InvalidBlockSize);
        }

        // size must be power of two so a memory block can be properly allocated
        if !size.is_power_of_two() {
            return Err(MemAllocError::NotPowerOfTwo)
        }

        match Self::alloc_memblock(size, align) {
            Ok(value) => Ok(MemBlock {
                ptr: value,
                size,
                align,
                is_freed: false,
            }),
            Err(value) => Err(value),
        }

    }

    unsafe fn alloc_memblock(size: BlockSize, align: usize) -> Result<NonNull<u8>, MemAllocError> {
        let layout: Layout = match Layout::from_size_align(size, align) {
            Ok(layout) => layout,
            Err(_) => return Err(MemAllocError::LayoutError),
        };
        let ptr: *mut u8 = alloc(layout);

        if ptr.is_null() {
            return Err(MemAllocError::NullPointer)
        }
        Ok(NonNull::new_unchecked(ptr))
    }

    pub unsafe fn free(&mut self) -> Result<MemAllocSuccess, MemAllocError> {
        if !self.is_freed {
            let layout: Layout = match Layout::from_size_align(self.size, ALIGNMENT) {
                Ok(layout) => layout,
                Err(_) => return Err(MemAllocError::LayoutError),
            };

            dealloc(self.ptr.as_ptr(), layout);
            self.is_freed = true;
            Ok(MemAllocSuccess::MemoryFreed)
        } else {
            Err(MemAllocError::MemoryAlreadyFreed)
        }
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
    pub unsafe fn pop<T: Clone>(
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

    /// Take a look at the data at some pointer position in the memory. The API calling
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
    MemoryAlreadyFreed,
    MemoryOverflow,
    NotEnoughMemory,
    NotPowerOfTwo,
    NullPointer,
}

#[derive(Debug)]
pub enum MemAllocSuccess {
    MemoryFreed,
    MemoryAlreadyFreed,
    DataPushedToMemory,
}

#[cfg(test)]
mod tests {
    use super::*;

    /// test memory block allocation, writing, reading and de-allocation
    #[test]
    fn test_simple_memblock_operations() {
        unsafe {
            println!("== simple memblock alloc ==");

            let max_size = MAX_MEMBLOCK_SIZE;
            assert_eq!(max_size, MAX_MEMBLOCK_SIZE);

            let mut memblock = MemBlock::new(max_size, 8usize).unwrap();
            println!(" - memblock");
            println!("   - [x] ptr: {}", memblock.as_ptr() as usize);

            let data_ptr = memblock.push(1u64).unwrap();
            println!("   - [x] input data: {}", 1u64);
            assert!(
                memblock.as_ptr().add(size_of_val(&1u64)) <= memblock.as_ptr().add(memblock.size)
            );
            println!("   - [x] push data, received ptr: {:}", data_ptr);

            let retrieved_data = memblock.peek::<u64>(data_ptr);
            assert_eq!(retrieved_data, 1u64);
            println!("   - [x] peek data: {:}", retrieved_data);

            let (d, ds, p) = match memblock.pop::<u64>(data_ptr) {
                Ok((x, y, z)) => (x, y, z),
                Err(e) => panic!("{:?}", e),
            };
            assert_eq!(d, 1u64);
            assert_eq!(ds, 8);
            assert_eq!(p, memblock.as_ptr() as usize);
            println!("   - [x] pop data:");
            println!("   -   - [x] retrieved data: {:}", d);
            println!("   -   - [x] retrieved data size: {:}", ds);
            println!("   -   - [x] retrieved new pointer: {:}", p);

            memblock.free().unwrap();
            println!("   - [x] memblock freed");

            println!("=====================");
        }
    }

    /// test many memory blocks allocation, writing, reading and de-allocation
    #[test]
    fn test_many_memblock_operations() {}

    #[test]
    fn test_struct_memblock_operations() {
        unsafe {
            #[derive(Debug, Copy, Clone, Ord, PartialOrd, Eq, PartialEq)]
            struct TestStruct {
                x: u64,
                y: u64
            }

            println!("=== complex memblock alloc ===");

            let mut memblock = match MemBlock::new(MAX_MEMBLOCK_SIZE, 8usize) {
                Ok(block) => block,
                Err(err) => panic!("{:?}", err)
            };
            println!(" - memblock");
            println!("   - [x] ptr: {}", memblock.as_ptr() as usize);

            let data_struct = TestStruct{x:1u64, y:65535u64};
            let data_ptr = memblock.push(data_struct.clone()).unwrap();
            println!("   - [x] input data: {:?}", data_struct);
            println!("   - [x] push data, received ptr: {:}", data_ptr);
            let retrieved_data = memblock.peek::<TestStruct>(data_ptr);
            assert_eq!(retrieved_data, data_struct);
            println!("   - [x] peek data: {:?}", retrieved_data);

            let (d, ds, p) = match memblock.pop::<TestStruct>(data_ptr) {
                Ok((x, y, z)) => (x, y, z),
                Err(e) => panic!("{:?}", e),
            };
            assert_eq!(d, data_struct);
            assert_eq!(ds, 16);
            assert_eq!(p, memblock.as_ptr() as usize);
            println!("   - [x] pop data:");
            println!("   -   - [x] retrieved data: {:?}", d);
            println!("   -   - [x] retrieved data size: {:}", ds);
            println!("   -   - [x] retrieved new pointer: {:}", p);
        }
    }
}
