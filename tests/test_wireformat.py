import struct
import unittest
from nbloader import load_notebook

core = load_notebook()


class WireTests(unittest.TestCase):
    def test_rfc_example(self):
        query = core.build_query('www.example.com', qtype=1, qid=0, rd=True)
        self.assertEqual(core.to_dns_param(query), 'AAABAAABAAAAAAAAA3d3dwdleGFtcGxlA2NvbQAAAQAB')
        self.assertEqual(query.hex(), '00000100000100000000000003777777076578616d706c6503636f6d0000010001')
        self.assertEqual(core.from_dns_param(core.to_dns_param(query)), query)

    def test_four_names(self):
        for name, length, encoded in [
            ('example.com', 29, 'AAABAAABAAAAAAAAB2V4YW1wbGUDY29tAAABAAE'),
            ('google.com', 28, 'AAABAAABAAAAAAAABmdvb2dsZQNjb20AAAEAAQ'),
            ('cloudflare.com', 32, 'AAABAAABAAAAAAAACmNsb3VkZmxhcmUDY29tAAABAAE'),
            ('dns.google', 28, 'AAABAAABAAAAAAAAA2RucwZnb29nbGUAAAEAAQ'),
        ]:
            with self.subTest(name=name):
                query = core.build_query(name)
                self.assertEqual(len(query), length)
                self.assertEqual(core.to_dns_param(query), encoded)
                self.assertEqual(core.from_dns_param(encoded), query)

    def test_compressed_answer(self):
        data = bytes.fromhex('123481800001000100000000076578616d706c6503636f6d0000010001'
                             'c00c0001000100000e1000045db8d822')
        self.assertEqual(core.parse_response(data), {
            'id': 4660, 'rcode': 0, 'ra': True, 'ad': False, 'tc': False,
            'questions': [{'name': 'example.com', 'type': 1}],
            'answers': [{'name': 'example.com', 'type': 1, 'ttl': 3600, 'data': '93.184.216.34'}],
            'counts': {'qd': 1, 'an': 1, 'ns': 0, 'ar': 0},
        })

    def test_do_bit_vectors(self):
        for name, length, encoded in [
            ('example.com', 40, 'AAABAAABAAAAAAABB2V4YW1wbGUDY29tAAABAAEAACkE0AAAgAAAAA'),
            ('google.com', 39, 'AAABAAABAAAAAAABBmdvb2dsZQNjb20AAAEAAQAAKQTQAACAAAAA'),
        ]:
            with self.subTest(name=name):
                query = core.build_query(name, dnssec_ok=True)
                self.assertEqual(len(query), length)
                self.assertEqual(struct.unpack_from('!H', query, 10)[0], 1)
                self.assertEqual(query[-11:].hex(), '00002904d0000080000000')
                self.assertEqual(core.to_dns_param(query), encoded)
                self.assertEqual(core.from_dns_param(encoded), query)
        self.assertEqual(core.build_query('example.com', dnssec_ok=True).hex(),
                         '000001000001000000000001076578616d706c6503636f6d000001000100002904d0000080000000')

    def test_short_buffer(self):
        for size in range(12):
            with self.assertRaises(ValueError):
                core.parse_response(bytes(size))

    def test_pointer_cycle(self):
        with self.assertRaises(ValueError):
            core.parse_response(bytes.fromhex('000081800001000000000000c00c00010001'))

    def test_label_boundaries(self):
        with self.assertRaises(ValueError):
            core.build_query('a' * 64 + '.com')
        self.assertEqual(len(core.build_query('a' * 63 + '.com')), 85)

    def test_aaaa_cname_and_flags(self):
        cname = b'\x03www\xc0\x0c'
        data = struct.pack('!6H', 0, 0x83a0, 1, 2, 0, 0) + core.build_query('example.com')[12:]
        data += b'\xc0\x0c' + struct.pack('!HHIH', 5, 1, 60, len(cname)) + cname
        data += b'\xc0\x0c' + struct.pack('!HHIH', 28, 1, 120, 16)
        data += bytes.fromhex('20010db8000000000000000000000001')
        parsed = core.parse_response(data)
        self.assertTrue(parsed['ad'])
        self.assertTrue(parsed['tc'])
        self.assertEqual(parsed['answers'][0]['data'], 'www.example.com')
        self.assertEqual(parsed['answers'][1]['data'], '2001:db8::1')

    def test_malformed_inputs(self):
        for name in ('', 'a..com', 'a/b.com', '.'.join(['a' * 63] * 4), None):
            with self.subTest(name=name), self.assertRaises(ValueError):
                core.build_query(name)
        for encoded in ('=', 'a', 'AA+', 'AB', None):
            with self.subTest(encoded=encoded), self.assertRaises(ValueError):
                core.from_dns_param(encoded)
        for suffix in ('c0ff', '40', '0361', 'c0'):
            with self.subTest(suffix=suffix), self.assertRaises(ValueError):
                core.parse_response(bytes.fromhex('000081800001000000000000' + suffix))
