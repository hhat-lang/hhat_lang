use std::collections::HashMap;
use std::rc::Rc;
use uuid::Uuid;

use crate::data_impl::HeapData;
use crate::ir::Identifier;

//-----------------------
// MEMORY MANAGER SCOPE
//-----------------------

/// Memory manager
///
/// - holds stack, heap, index, processes ids (pid), quantum
///     instructions (q_instr) for a specific closure, namely
///     main body of the program, functions, quantum routines
pub struct Memory<'a, V: HeapData, const N: usize> {
    pub stack: Stack<'a, V, N>,
    pub heap: Heap<'a, Identifier, V>,
    pub index: Index<'a>,
    pub q_instr: QInstr<'a>,
    pub pid: Pid<'a>,
}

impl<'a, V: HeapData, const N: usize> Memory<'a, V, N> {
    pub fn new(id_counter: IdCounter) -> Memory<'a, V, N> {
        Memory {
            stack: Stack::new(),
            heap: Heap::new(),
            index: Index::new(),
            q_instr: QInstr::new(),
            pid: Pid::new(id_counter),
        }
    }
}

//--------------
// STACK SCOPE
//--------------

/// Stack manager
///
/// - struct:
///     - handles stack data
/// - impl:
///     - handles stack operations
pub struct Stack<'a, V: HeapData, const N: usize> {
    data: [V; N],
    stack_pointer: usize,
}

impl<'a, T: HeapData, const N: usize> Stack<'a, T, N> {
    pub fn new() -> Stack<'a, T, N> {
        Stack {
            data: [0; N],
            stack_pointer: 0,
        }
    }

    pub fn push(&mut self, value: T) {
        self.stack_pointer += 1;
        self.data[self.stack_pointer] = value;
    }
}

//-------------
// HEAP SCOPE
//-------------

/// Heap manager
///
/// - struct:
///     - handles heap data
/// - impl:
///     - handles heap operations
pub struct Heap<'a, Identifier, V: HeapData> {
    data: HashMap<Identifier, Rc<V>>,
}

impl<'a, Identifier, V: HeapData> Heap<'a, Identifier, V> {
    pub fn new() -> Heap<'a, Identifier, V> {
        Heap {
            data: HashMap::new(),
        }
    }
}

//--------------
// INDEX SCOPE
//--------------

/// Index manager
///
/// - struct:
///     - handles index data
/// - impl:
///     - handles index operations
pub struct Index<'a> {}

impl<'a> Index<'a> {
    pub fn new() -> Index<'a> {
        Index {}
    }
}

//-----------------------------
// QUANTUM INSTRUCTIONS SCOPE
//-----------------------------

/// Quantum Instructions manager
///
/// - struct:
///     - handles quantum instructions data
/// - impl:
///     - handles quantum instructions operations
pub struct QInstr<'a> {}

impl<'a> QInstr<'a> {
    pub fn new() -> QInstr<'a> {
        QInstr {}
    }
}

//----------------------
// PROCESSES IDS SCOPE
//----------------------

/// Processes Ids manager
///
/// - struct:
///     - handles pids data
/// - impl:
///     - handles pids operations
pub struct Pid<'a> {
    id: Uuid,
}

impl<'a> Pid<'a> {
    pub fn new(mut id_counter: IdCounter) -> Pid<'a> {
        Pid {
            id: id_counter.gen_id(),
        }
    }
}

struct PidState {
    id: Uuid,
    status: PidStatus,
}

enum PidStatus {
    Active,                // being executed
    Ready,                 // waiting in the queue for execution
    Waiting,               // waiting external operation to reply
    Done,                  // successfully executed; nothing else to do
    Disabled,              // stopped by parent process
    Error(PidErrorNumber), // some error occurred
}

/// Possible list of errors to use for [`PidStatus`] enum:
/// - `Timeout`
/// - `InvalidData`
/// - `InvalidOperation`
/// - `AccessingDonePid`
/// - `AccessingDisabledPid`
enum PidErrorNumber {
    Timeout,
    InvalidData,
    InvalidOperation,
    AccessingDonePid,
    AccessingDisabledPid,
}

pub struct IdCounter {
    last_id: Option<Uuid>,
    ids_list: HashMap<Uuid, PidState>,
}

impl IdCounter {
    pub fn init() -> IdCounter {
        IdCounter {
            last_id: None,
            ids_list: HashMap::new(),
        }
    }

    /// to generate and get a new ID for [`Pid`]
    pub fn gen_id(&mut self) -> Uuid {
        let mut id: Uuid = Uuid::new_v4();
        self.ids_list.insert(
            id.clone(),
            PidState {
                id: id.clone(),
                status: PidStatus::Ready,
            },
        );
        self.last_id = Some(id.clone());
        id
    }

    pub fn get_last_id(&mut self) -> Uuid {
        self.last_id.unwrap().clone()
    }
}
