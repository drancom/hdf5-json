##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of H5Serv (HDF5 REST Server) Service, Libraries and      #
# Utilities.  The full HDF5 REST Server copyright notice, including          #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################
import unittest
import logging
import numpy as np
import sys
from h5py import special_dtype
from h5py import check_dtype
import six

sys.path.append('../../lib')
import hdf5dtype

if six.PY3:
    unicode = str


class Hdf5dtypeTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Hdf5dtypeTest, self).__init__(*args, **kwargs)
        # main
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def testBaseIntegerTypeItem(self):
        dt = np.dtype('<i1')
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_INTEGER')
        self.failUnlessEqual(typeItem['base'], 'H5T_STD_I8LE')
        typeItem = hdf5dtype.getTypeResponse(typeItem) # non-verbose format
        self.failUnlessEqual(typeItem['class'], 'H5T_INTEGER')
        self.failUnlessEqual(typeItem['base'], 'H5T_STD_I8LE')


    def testBaseFloatTypeItem(self):
        dt = np.dtype('<f8')
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_FLOAT')
        self.failUnlessEqual(typeItem['base'], 'H5T_IEEE_F64LE')
        typeItem = hdf5dtype.getTypeResponse(typeItem) # non-verbose format
        self.failUnlessEqual(typeItem['class'], 'H5T_FLOAT')
        self.failUnlessEqual(typeItem['base'], 'H5T_IEEE_F64LE')

    def testBaseStringTypeItem(self):
        dt = np.dtype('S3')
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_STRING')
        self.failUnlessEqual(typeItem['length'], 3)
        self.failUnlessEqual(typeItem['strPad'], 'H5T_STR_NULLPAD')
        self.failUnlessEqual(typeItem['charSet'], 'H5T_CSET_ASCII')

    def testBaseStringUTFTypeItem(self):
        dt = np.dtype('U3')
        try:
            typeItem = hdf5dtype.getTypeItem(dt)
            self.assertTrue(False)  # expected exception
        except TypeError:
            pass # expected

    def testBaseVLenAsciiTypeItem(self):
        dt = special_dtype(vlen=str)
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_STRING')
        self.failUnlessEqual(typeItem['length'], 'H5T_VARIABLE')
        self.failUnlessEqual(typeItem['strPad'], 'H5T_STR_NULLTERM')
        self.failUnlessEqual(typeItem['charSet'], 'H5T_CSET_ASCII')

    def testBaseVLenUnicodeTypeItem(self):
        dt = special_dtype(vlen=unicode)
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_STRING')
        self.failUnlessEqual(typeItem['length'], 'H5T_VARIABLE')
        self.failUnlessEqual(typeItem['strPad'], 'H5T_STR_NULLTERM')
        self.failUnlessEqual(typeItem['charSet'], 'H5T_CSET_UTF8')

    def testBaseEnumTypeItem(self):
        mapping = {'RED': 0, 'GREEN': 1, 'BLUE': 2}
        dt = special_dtype(enum=(np.int8, mapping))
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_ENUM')
        baseItem = typeItem['base']
        self.failUnlessEqual(baseItem['class'], 'H5T_INTEGER')
        self.failUnlessEqual(baseItem['base'], 'H5T_STD_I8LE')
        self.assertTrue('mapping' in typeItem)
        self.failUnlessEqual(typeItem['mapping']['GREEN'], 1)

    def testBaseArrayTypeItem(self):
        dt = np.dtype('(2,2)<int32')
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_ARRAY')
        baseItem = typeItem['base']
        self.failUnlessEqual(baseItem['class'], 'H5T_INTEGER')
        self.failUnlessEqual(baseItem['base'], 'H5T_STD_I32LE')

    def testCompoundArrayTypeItem(self):
        dt = np.dtype([('a', '<i1'), ('b', 'S1', (10,))])
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_COMPOUND')
        fields = typeItem['fields']
        field_a = fields[0]
        self.failUnlessEqual(field_a['name'], 'a')
        field_a_type = field_a['type']
        self.failUnlessEqual(field_a_type['class'], 'H5T_INTEGER')
        self.failUnlessEqual(field_a_type['base'], 'H5T_STD_I8LE')
        field_b = fields[1]
        self.failUnlessEqual(field_b['name'], 'b')
        field_b_type = field_b['type']
        self.failUnlessEqual(field_b_type['class'], 'H5T_ARRAY')
        self.failUnlessEqual(field_b_type['dims'], (10,))
        field_b_basetype = field_b_type['base']
        self.failUnlessEqual(field_b_basetype['class'], 'H5T_STRING')


    def testOpaqueTypeItem(self):
        dt = np.dtype('V200')
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_OPAQUE')
        self.assertTrue('base' not in typeItem)

    def testVlenDataItem(self):
        dt = special_dtype(vlen=np.dtype('int32'))
        typeItem = hdf5dtype.getTypeItem(dt)
        self.failUnlessEqual(typeItem['class'], 'H5T_VLEN')
        self.failUnlessEqual(typeItem['size'], 'H5T_VARIABLE')
        baseItem = typeItem['base']
        self.failUnlessEqual(baseItem['base'], 'H5T_STD_I32LE')

    def testCompoundTypeItem(self):
        dt = np.dtype([("temp", np.float32), ("pressure", np.float32), ("wind", np.int16)])
        typeItem = hdf5dtype.getTypeItem(dt)
        self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
        self.assertTrue('fields' in typeItem)
        fields = typeItem['fields']
        self.assertEqual(len(fields), 3)
        tempField = fields[0]
        self.assertEqual(tempField['name'], 'temp')
        self.assertTrue('type' in tempField)
        tempFieldType = tempField['type']
        self.assertEqual(tempFieldType['class'], 'H5T_FLOAT')
        self.assertEqual(tempFieldType['base'], 'H5T_IEEE_F32LE')

        typeItem = hdf5dtype.getTypeResponse(typeItem) # non-verbose format
        self.assertEqual(typeItem['class'], 'H5T_COMPOUND')
        self.assertTrue('fields' in typeItem)
        fields = typeItem['fields']
        self.assertEqual(len(fields), 3)
        tempField = fields[0]
        self.assertEqual(tempField['name'], 'temp')
        self.assertTrue('type' in tempField)
        tempFieldType = tempField['type']
        self.failUnlessEqual(tempFieldType['class'], 'H5T_FLOAT')
        self.failUnlessEqual(tempFieldType['base'], 'H5T_IEEE_F32LE')

    def testCreateBaseType(self):
        dt = hdf5dtype.createDataType('H5T_STD_U32BE')
        self.assertEqual(dt.name, 'uint32')
        self.assertEqual(dt.byteorder, '>')
        self.assertEqual(dt.kind, 'u')

        dt = hdf5dtype.createDataType('H5T_STD_I16LE')
        self.assertEqual(dt.name, 'int16')
        self.assertEqual(dt.kind, 'i')

        dt = hdf5dtype.createDataType('H5T_IEEE_F64LE')
        self.assertEqual(dt.name, 'float64')
        self.assertEqual(dt.kind, 'f')

        dt = hdf5dtype.createDataType('H5T_IEEE_F32LE')
        self.assertEqual(dt.name, 'float32')
        self.assertEqual(dt.kind, 'f')

        typeItem = { 'class': 'H5T_INTEGER', 'base': 'H5T_STD_I32BE' }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'int32')
        self.assertEqual(dt.kind, 'i')

    def testCreateBaseStringType(self):
        typeItem = { 'class': 'H5T_STRING', 'charSet': 'H5T_CSET_ASCII', 'length': 6 }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'string48')
        self.assertEqual(dt.kind, 'S')

    def testCreateBaseUnicodeType(self):
        typeItem = { 'class': 'H5T_STRING', 'charSet': 'H5T_CSET_UTF8', 'length': 32 }
        try:
            dt = hdf5dtype.createDataType(typeItem)
            self.assertTrue(False)  # expected exception
        except TypeError:
            pass

    def testCreateNullTermStringType(self):
        typeItem = { 'class': 'H5T_STRING', 'charSet': 'H5T_CSET_ASCII',
            'length': 6, 'strPad': 'H5T_STR_NULLTERM'}
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'string48')
        self.assertEqual(dt.kind, 'S')


    def testCreateVLenStringType(self):
        typeItem = { 'class': 'H5T_STRING', 'charSet': 'H5T_CSET_ASCII', 'length': 'H5T_VARIABLE' }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'object')
        self.assertEqual(dt.kind, 'O')
        self.assertEqual(check_dtype(vlen=dt), str)


    def testCreateVLenUTF8Type(self):
        typeItem = { 'class': 'H5T_STRING', 'charSet': 'H5T_CSET_UTF8', 'length': 'H5T_VARIABLE' }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'object')
        self.assertEqual(dt.kind, 'O')
        self.assertEqual(check_dtype(vlen=dt), unicode)

    def testCreateVLenDataType(self):
        typeItem = { 'class': 'H5T_VLEN', 'base': 'H5T_STD_I32BE' }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'object')
        self.assertEqual(dt.kind, 'O')

    def testCreateOpaqueType(self):
        typeItem = { 'class': 'H5T_OPAQUE', 'size': 200 }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'void1600')
        self.assertEqual(dt.kind, 'V')

    def testCreateCompoundType(self):
        typeItem = {'class': 'H5T_COMPOUND', 'fields':
                [{'name': 'temp',     'type': 'H5T_IEEE_F32LE'},
                 {'name': 'pressure', 'type': 'H5T_IEEE_F32LE'},
                 {'name': 'location', 'type': {
                     'length': 'H5T_VARIABLE',
                     'charSet': 'H5T_CSET_ASCII',
                     'class': 'H5T_STRING',
                     'strPad': 'H5T_STR_NULLTERM' } },
                 {'name': 'wind',     'type': 'H5T_STD_I16LE'} ] }

        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'void144')
        self.assertEqual(dt.kind, 'V')
        self.assertEqual(len(dt.fields), 4)
        dtLocation = dt[2]
        self.assertEqual(dtLocation.name, 'object')
        self.assertEqual(dtLocation.kind, 'O')
        self.assertEqual(check_dtype(vlen=dtLocation), str)

    def testCreateCompoundTypeUnicodeFields(self):
        typeItem = {'class': 'H5T_COMPOUND', 'fields':
                [{'name': u'temp',     'type': 'H5T_IEEE_F32LE'},
                 {'name': u'pressure', 'type': 'H5T_IEEE_F32LE'},
                 {'name': u'wind',     'type': 'H5T_STD_I16LE'} ] }

        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'void80')
        self.assertEqual(dt.kind, 'V')
        self.assertEqual(len(dt.fields), 3)

    def testCreateArrayType(self):
        typeItem = {'class': 'H5T_ARRAY',
                    'base': 'H5T_STD_I64LE',
                    'dims': (3, 5) }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'void960')
        self.assertEqual(dt.kind, 'V')

    def testCreateArrayIntegerType(self):
        typeItem = {'class': 'H5T_INTEGER',
                    'base': 'H5T_STD_I64LE',
                    'dims': (3, 5) }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(dt.name, 'void960')
        self.assertEqual(dt.kind, 'V')

    def testCreateCompoundArrayType(self):
        typeItem = {
            "class": "H5T_COMPOUND",
            "fields": [
                {
                    "type": {
                        "base": "H5T_STD_I8LE",
                        "class": "H5T_INTEGER"
                    },
                    "name": "a"
                },
                {
                    "type": {
                        "dims": [
                            10
                        ],
                        "base": {
                            "length": 1,
                            "charSet": "H5T_CSET_ASCII",
                            "class": "H5T_STRING",
                            "strPad": "H5T_STR_NULLPAD"
                        },
                    "class": "H5T_ARRAY"
                },
                "name": "b"
                }
            ]
        }
        dt = hdf5dtype.createDataType(typeItem)
        self.assertEqual(len(dt.fields), 2)
        self.assertTrue('a' in dt.fields.keys())
        self.assertTrue('b' in dt.fields.keys())



if __name__ == '__main__':
    #setup test files

    unittest.main()
