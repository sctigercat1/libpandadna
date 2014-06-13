#!/usr/bin/env python2
import unittest
import zlib

import common


class TestCompilerPDNA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('test.dna', 'r') as f:
            cls.data = f.read()

    def test_compressed(self):
        compiler = common.Compiler(self.data, compress=True)
        compiled = compiler.compile()

        self.assertEquals(compiled[5], chr(1))
        data = compiled[common.HEADER_LENGTH:]
        try:
            decompressed = zlib.decompress(data)
        except zlib.error:
            self.fail("Couldn't decompress the PDNA file.")

        reader = common.Reader(decompressed)
        try:
            reader.readDNAStorage()
        except:
            self.fail("Couldn't read compressed storage.")
        try:
            reader.readComponents()
        except:
            self.fail("Couldn't read the compressed components.")

    def test_uncompressed(self):
        compiler = common.Compiler(self.data, compress=False)
        compiled = compiler.compile()

        self.assertEquals(compiled[5], chr(0))
        reader = common.Reader(compiled)
        try:
            reader.readDNAStorage()
        except:
            self.fail("Couldn't read uncompressed storage.")
        try:
            reader.readComponents()
        except:
            self.fail("Couldn't read the uncompressed components.")


if __name__ == '__main__':
    unittest.main()
