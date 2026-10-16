import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock
import dns.exception
import dns.resolver
import pandas as pd

spec = importlib.util.spec_from_file_location('mx',Path(__file__).parents[1]/'scripts/mx_lookup.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
def record(preference,host):return SimpleNamespace(preference=preference,exchange=Mock(to_text=lambda:host))
class MxTests(unittest.TestCase):
    def test_sorts_preferences_and_normalizes_hosts(self):
        resolver=Mock(); resolver.resolve.return_value=[record(20,'backup.example.org.'),record(10,'mail.example.org.')]
        row=module.get_mx_records('example.org',resolver)
        self.assertEqual(row['Primary_Host'],'mail.example.org')
        self.assertEqual(row['Preferences'],'10; 20')

    def test_null_mx_has_no_deliverable_primary(self):
        resolver=Mock();resolver.resolve.return_value=[record(0,'.')]
        row=module.get_mx_records('example.org',resolver)
        self.assertEqual(row['MX_Found'],'Null MX');self.assertEqual(row['Primary_Host'],'N/A')

    def test_timeout_and_no_answer_are_different(self):
        resolver=Mock();resolver.resolve.side_effect=dns.exception.Timeout()
        self.assertEqual(module.get_mx_records('example.org',resolver)['MX_Found'],'Error')
        resolver.resolve.side_effect=dns.resolver.NoAnswer()
        self.assertEqual(module.get_mx_records('example.org',resolver)['MX_Found'],'No')

    def test_missing_domain_column_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);pd.DataFrame({'Host':['example.org']}).to_excel(root/'input.xlsx',index=False)
            with self.assertRaisesRegex(ValueError,'Domain column'):
                module.audit(root/'input.xlsx',root/'output.xlsx',Mock())
            self.assertFalse((root/'output.xlsx').exists())

if __name__=='__main__':unittest.main()
