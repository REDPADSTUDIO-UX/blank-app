"""New private-prefix repair only; never starts a runtime or accesses a provider."""
from pathlib import Path
import tempfile
import unittest
from experiments.phase2_private_voice_install import remove_bootstrap_pip_metadata


class PrivateBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.original=Path(self.temp.name)/'original';self.copy=Path(self.temp.name)/'private-copy'
        for root in (self.original,self.copy):
            old=root/'lib/python3.11/site-packages/pip-26.2.2.dist-info'
            old.mkdir(parents=True);(old/'METADATA').write_text('Name: pip\nVersion: 26.2.2\n')
        self.old=self.copy/'lib/python3.11/site-packages/pip-26.2.2.dist-info'
        self.new=self.copy/'lib/python3.11/site-packages/pip-26.3.dist-info'
        self.new.mkdir();(self.new/'METADATA').write_text('Name: pip\nVersion: 26.3\n')

    def test_only_identical_obsolete_metadata_removed_original_untouched(self):
        rows=remove_bootstrap_pip_metadata(self.original,self.copy,'26.3')
        self.assertEqual(len(rows),1);self.assertFalse(self.old.exists())
        self.assertTrue((self.original/'lib/python3.11/site-packages/pip-26.2.2.dist-info/METADATA').is_file())
        self.assertTrue((self.new/'METADATA').is_file())

    def test_altered_old_metadata_rejected_without_deleting_it(self):
        (self.old/'METADATA').write_text('unexpected change')
        with self.assertRaises(RuntimeError):remove_bootstrap_pip_metadata(self.original,self.copy,'26.3')
        self.assertTrue(self.old.is_dir())

    def test_missing_pinned_replacement_preserves_bootstrap(self):
        (self.new/'METADATA').unlink()
        with self.assertRaises(RuntimeError):remove_bootstrap_pip_metadata(self.original,self.copy,'26.3')
        self.assertTrue(self.old.is_dir())

    def test_resume_does_not_repeat_metadata_removal(self):
        remove_bootstrap_pip_metadata(self.original,self.copy,'26.3')
        self.assertEqual(remove_bootstrap_pip_metadata(self.original,self.copy,'26.3'),[])


if __name__=='__main__':unittest.main()
