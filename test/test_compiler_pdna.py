#!/usr/bin/env python2
import unittest
import zlib

import common


class TestCompilerStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # TODO: Write a better DNA file for this test.
        with open('test_storage.dna', 'r') as f:
            cls.pdna_data = f.read()

    def test_compressed(self):
        compiler = common.Compiler(self.pdna_data, compress=True)
        compiled = compiler.compile()

        self.assertEquals(compiled[5], chr(1))
        header = compiled[:common.HEADER_LENGTH]
        data = compiled[common.HEADER_LENGTH:]
        try:
            decompressed = zlib.decompress(data)
        except zlib.error:
            self.fail("Couldn't decompress the PDNA file.")

        reader = common.PyReader(header + decompressed)
        try:
            reader.readDNAStorage()
        except:
            self.fail("Couldn't read compressed storage.")
        # TODO: Read the remainder.

    def test_uncompressed(self):
        compiler = common.Compiler(self.pdna_data, compress=False)
        compiled = compiler.compile()

        self.assertEquals(compiled[5], chr(0))
        reader = common.PyReader(compiled)
        try:
            reader.readDNAStorage()
        except:
            self.fail("Couldn't read uncompressed storage.")
        # TODO: Read the remainder.


if __name__ == '__main__':
    unittest.main()
