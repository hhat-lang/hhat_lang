"""
Use to execute classical functions test. It follows the regular code execution path::

    raw code -> AST -> IR
                 _______|__________
                |                  |
                v                  v
          quantum branch      classical branch
                |                  |-> memory
                |                  |-> executor
                |-> program
                |-> executor
                        | -> low level language
                        | -> target (simulator or QPU device)
                        | -> classical branch (if needed)

"""
