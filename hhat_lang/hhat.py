"""H-hat main runner to external files """

import sys
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from hhat_lang.evaluator import Code


    def start(args):
        if len(args) > 1:
            with open(args[1], 'r') as f:
                data = f.read()
                
            code_exec = Code(data)
            code_exec.run()

if __name__ == '__main__':
    start(sys.argv)
