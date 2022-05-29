"""H-hat main runner to external files """

import sys
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from hhat_lang.new_evaluator import GenAST, Eval


    def start(args):
        if len(args) > 1:
            with open(args[1], 'r') as f:
                data = f.read()

            g = GenAST(data)
            gst = g.st
            ev = Eval()
            ev.walk(gst)


if __name__ == '__main__':
    start(sys.argv)
