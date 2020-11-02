import unittest
from aspa_logic import *

class ASPATests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ASPATests, self).__init__(*args, **kwargs)

        # just an example for the tests
        aspa_records = {
            IPv4: {
                3356: {0},
                2914: {0},
                174: {0},
                13238: {6762, 174, 9002, 6939, 208722, 1299, 3356},
                43247: {13238},
                12389: {1273, 1299, 3257, 3356, 3491, 5511}
            },
            IPv6: {
            }
        }
        self.aspa_manager = ASPA(aspa_records)

    def test_upstream_path_valid(self):
        aspath = [Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 3356, IPv4), Valid)

        aspath = [Segment(3356, AS_SEQUENCE), Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 3356, IPv4), Valid)

        aspath = [Segment(13238, AS_SEQUENCE), Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 3356, IPv4), Valid)

        aspath = [Segment(13238, AS_SEQUENCE), Segment(13238, AS_SEQUENCE),
                  Segment(3356, AS_SEQUENCE), Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 3356, IPv4), Valid)

        aspath = [Segment(43247, AS_SEQUENCE), Segment(13238, AS_SEQUENCE),
                  Segment(3356, AS_SEQUENCE), Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 3356, IPv4), Valid)

    def test_upstream_path_invalid(self):
        # aspath with zero length
        aspath = []
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 3356, IPv4), Invalid)

        # invalid neighbor
        aspath = [Segment(2914, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 3356, IPv4), Invalid)

        # invalid aspa
        aspath = [Segment(3356, AS_SEQUENCE), Segment(2914, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 2914, IPv4), Invalid)

        # invalid aspa + set in the beginning
        aspath = [Segment(3356, AS_SET), Segment(3356, AS_SEQUENCE), Segment(2914, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 2914, IPv4), Invalid)

        # invalid aspa + set at the end
        aspath = [Segment(3356, AS_SEQUENCE), Segment(2914, AS_SEQUENCE), Segment(2914, AS_SET)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 2914, IPv4), Invalid)

        # invalid aspa in the middle
        aspath = [Segment(3356, AS_SEQUENCE), Segment(12389, AS_SEQUENCE), Segment(2914, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 2914, IPv4), Invalid)

        # invalid aspa in the middle + prepend
        aspath = [Segment(3356, AS_SEQUENCE), Segment(12389, AS_SEQUENCE), Segment(12389, AS_SEQUENCE), Segment(2914, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 2914, IPv4), Invalid)

    def test_upstream_path_unknown(self):
        # unknown pair at the origin
        aspath = [Segment(1, AS_SEQUENCE), Segment(13238, AS_SEQUENCE), Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 3356, IPv4), Unknown)

        # unknown pair in the middle
        aspath = [Segment(13238, AS_SEQUENCE), Segment(9002, AS_SEQUENCE), Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 3356, IPv4), Unknown)

        # two unknown pairs
        aspath = [Segment(13238, AS_SEQUENCE), Segment(9002, AS_SEQUENCE), Segment(1, AS_SEQUENCE), Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_upflow_path(aspath, 3356, IPv4), Unknown)

    def test_downstream_path_valid(self):
        # single T1 in the path
        aspath = [Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 3356, IPv4, from_ix=False), Valid)

        # single T1 in the path through IX without 6695 in the path
        aspath = [Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 6695, IPv4, from_ix=True), Valid)

        # just an ISP
        aspath = [Segment(12389, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 12389, IPv4, from_ix=False), Valid)

        # ISP + T1
        aspath = [Segment(12389, AS_SEQUENCE), Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 3356, IPv4, from_ix=False), Valid)

        # ISP + T1 + T1
        aspath = [Segment(12389, AS_SEQUENCE), Segment(3356, AS_SEQUENCE), Segment(2914, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 2914, IPv4, from_ix=False), Valid)

        # ISP + T1 + T1 + ISP (upflow and downflow fragments)
        aspath = [Segment(12389, AS_SEQUENCE), Segment(3356, AS_SEQUENCE),
                  Segment(174, AS_SEQUENCE), Segment(13238, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 13238, IPv4, from_ix=False), Valid)

        # ISP + T1 + T1 + ISP + prepend (upflow and downflow fragments)
        aspath = [Segment(12389, AS_SEQUENCE), Segment(3356, AS_SEQUENCE), Segment(3356, AS_SEQUENCE),
                  Segment(174, AS_SEQUENCE), Segment(13238, AS_SEQUENCE), Segment(13238, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 13238, IPv4, from_ix=False), Valid)

    def test_downstream_path_invalid(self):
        # invalid neighbor
        aspath = [Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 2914, IPv4, from_ix=False), Invalid)

        # T1, T1, T1
        aspath = [Segment(3356, AS_SEQUENCE), Segment(2914, AS_SEQUENCE), Segment(174, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 174, IPv4, from_ix=False), Invalid)

        # T1, ISP, T1
        aspath = [Segment(3356, AS_SEQUENCE), Segment(12389, AS_SEQUENCE), Segment(174, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 174, IPv4, from_ix=False), Invalid)

        # Leak of the peer
        aspath = [Segment(13238, AS_SEQUENCE), Segment(20485, AS_SEQUENCE), Segment(174, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 174, IPv4, from_ix=False), Invalid)

        # Leak of the peer
        aspath = [Segment(13238, AS_SEQUENCE), Segment(20485, AS_SEQUENCE), Segment(174, AS_SEQUENCE), Segment(3356, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 174, IPv4, from_ix=False), Invalid)

    def test_downstream_path_unknown(self):
        # Unknown in the beginning
        aspath = [Segment(1, AS_SEQUENCE), Segment(12389, AS_SEQUENCE), Segment(3356, AS_SEQUENCE),
                  Segment(174, AS_SEQUENCE), Segment(13238, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 13238, IPv4, from_ix=False), Unknown)

        # Unknown in the middle
        aspath = [Segment(12389, AS_SEQUENCE), Segment(3356, AS_SEQUENCE),
                  Segment(174, AS_SEQUENCE), Segment(1, AS_SEQUENCE), Segment(13238, AS_SEQUENCE)]

        # Unknown in the end
        aspath = [Segment(12389, AS_SEQUENCE), Segment(3356, AS_SEQUENCE),
                  Segment(174, AS_SEQUENCE), Segment(13238, AS_SEQUENCE), Segment(1, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 1, IPv4, from_ix=False), Unknown)

    def test_downstream_path_unverifiable(self):
        # Unknown in the beginning
        aspath = [Segment(1, AS_SET), Segment(12389, AS_SEQUENCE), Segment(3356, AS_SEQUENCE),
                  Segment(174, AS_SEQUENCE), Segment(13238, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 13238, IPv4, from_ix=False), Unverifiable)

        # Unknown in the middle
        aspath = [Segment(12389, AS_SEQUENCE), Segment(3356, AS_SEQUENCE),
                  Segment(174, AS_SEQUENCE), Segment(1, AS_SET), Segment(13238, Unverifiable)]

        # Unknown in the end
        aspath = [Segment(12389, AS_SEQUENCE), Segment(3356, AS_SEQUENCE),
                  Segment(174, AS_SEQUENCE), Segment(13238, AS_SEQUENCE), Segment(1, AS_SET)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 1, IPv4, from_ix=False), Unverifiable)

        # Leak of the peer
        aspath = [Segment(13238, AS_SEQUENCE), Segment(20485, AS_SET), Segment(174, AS_SEQUENCE)]
        self.assertEqual(self.aspa_manager.check_downflow_path(aspath, 174, IPv4, from_ix=False), Unverifiable)

if __name__ == '__main__':
    unittest.main()