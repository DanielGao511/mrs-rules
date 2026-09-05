import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build import verify

class CoverageTests(unittest.TestCase):
    def test_domain_case_and_redundant_children(self):
        verify(['+.Example.com','a.example.com'],['+.example.com'],'domain')
    def test_reject_missing_domain(self):
        with self.assertRaises(ValueError):verify(['+.example.com','another.org'],['+.example.com'],'domain')
    def test_reject_broader_domain(self):
        with self.assertRaises(ValueError):verify(['a.example.com'],['+.example.com'],'domain')
    def test_ip_merge_ipv4_and_ipv6(self):
        verify(['10.0.0.0/25','10.0.0.128/25','fc00::/7'],['10.0.0.0/24','fc00::/7'],'ipcidr')
    def test_reject_broader_ip(self):
        with self.assertRaises(ValueError):verify(['10.0.0.0/25'],['10.0.0.0/24'],'ipcidr')

if __name__=='__main__':unittest.main()
