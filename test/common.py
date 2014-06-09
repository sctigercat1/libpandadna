import os
import sys


# We need some of the modules included in the compiler utility:
sys.path.append(os.path.abspath('../compiler'))


from StringIO import StringIO
from dna.base import DNAStorage
from dna.components import DNARoot
from dna.parser.tokens import *
from ply import lex


HEADER = 'PDNA\n{compressed}\n'


class DNAError(Exception):
    pass
__builtins__['DNAError'] = DNAError


lex.lex(optimize=0)


class Compiler:
    def __init__(self, data, compress=False):
        self.data = data
        self.compress = compress

        self.dnaStore = DNAStorage.DNAStorage()

    def compile(self):
        stream = StringIO(self.data)
        root = DNARoot.DNARoot(name='root', dnaStore=self.dnaStore)
        root.read(stream)
        rootData = root.traverse(recursive=True, verbose=False)
        dnaStoreData = self.dnaStore.dump(verbose=False)
        data = str(dnaStoreData + rootData)
        if self.compress:
            import zlib
            data = zlib.compress(data)
        header = HEADER.format(compressed=chr(int(self.compress)))
        return header + data
