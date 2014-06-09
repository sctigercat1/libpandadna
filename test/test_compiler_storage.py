#!/usr/bin/env python2
import unittest
import zlib

import common


class TestCompilerStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('test_storage.dna', 'r') as f:
            cls.pdna_data = f.read()
            cls.compiler = common.Compiler(cls.pdna_data, compress=False)
            cls.compiled = cls.compiler.compile()
            cls.reader = common.PyReader(cls.compiled)
            cls.reader.readDNAStorage()

    def test_compressed(self):
        compiler = common.Compiler(self.pdna_data, compress=True)
        compiled = compiler.compile()

        self.assertEquals(compiled[5], chr(1))
        header = compiled[:common.HEADER_LENGTH]
        data = compiled[common.HEADER_LENGTH:]
        try:
            decompressed = zlib.decompress(data)
        except zlib.error:
            self.fail("Couldn't decompress PDNA file.")

        reader = common.PyReader(header + decompressed)
        try:
            reader.readDNAStorage()
        except:
            self.fail("Couldn't read decompressed storage.")

    def test_catalog_codes(self):
        self.assertEquals(len(self.reader.dnaStore.catalogCodes), 5)
        expected = {
            'my_root': ['my_code_and_search_path', 'my_code'],
            'prop': ['prop_my_model_1'],
            'hood': ['hood_my_model_2'],
            'font': ['my_font_code', 'my_ttf_code'],
            'texture': ['street_floor', 'street_sidewalk', 'street_curb']
        }
        self.assertDictEqual(self.reader.dnaStore.catalogCodes, expected)

    def test_textures(self):
        self.assertEquals(len(self.reader.dnaStore.textures), 3)
        expected = {
            'street_curb': 'path/maps/curb.jpg',
            'street_sidewalk': 'path/maps/sidewalk.jpg',
            'street_floor': 'path/maps/floor.jpg'
        }
        self.assertDictEqual(self.reader.dnaStore.textures, expected)

    def test_fonts(self):
        self.assertEquals(len(self.reader.dnaStore.fonts), 2)
        expected = {
            'my_font_code': 'path/fonts/my_font_0.bam',
            'my_ttf_code': 'path/fonts/my_font_1.ttf'
        }
        self.assertDictEqual(self.reader.dnaStore.fonts, expected)

    def test_nodes(self):
        self.assertEquals(len(self.reader.dnaStore.nodes), 2)
        expected = {
            'my_code_and_search_path': ('path/models/my_model_0.egg', 'my_code_and_search_path'),
            'my_code': ('path/models/my_model_0.egg', 'search_path')
        }
        self.assertDictEqual(self.reader.dnaStore.nodes, expected)

    def test_hood_nodes(self):
        self.assertEquals(len(self.reader.dnaStore.hoodNodes), 1)
        expected = {'hood_my_model_2': ('path/models/my_model_2.bam', '')}
        self.assertDictEqual(self.reader.dnaStore.hoodNodes, expected)

    def test_place_nodes(self):
        self.assertEquals(len(self.reader.dnaStore.placeNodes), 1)
        expected = {'prop_my_model_1': ('path/models/my_model_1.bam', '')}
        self.assertDictEqual(self.reader.dnaStore.placeNodes, expected)


if __name__ == '__main__':
    unittest.main()
