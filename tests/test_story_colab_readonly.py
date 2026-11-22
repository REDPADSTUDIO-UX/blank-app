"""New metadata/checkpoint checks only; fake GPU inventory, no real inference."""
import ast,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from experiments import story_colab_readonly as readonly

class StoryColabReadonlyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        p=self.root/'self/attr';p.mkdir(parents=True)
        (self.root/'self/status').write_text('CapEff:\t0000000000000000\nNoNewPrivs:\t0\nSeccomp:\t2\nUnrelated:\tPRIVATE_NOT_CAPTURED\n')
        (self.root/'self/attr/current').write_text('MANUAL_TEST_POLICY')
        (self.root/'meminfo').write_text('MemTotal: 12000000 kB\nMemAvailable: 10000000 kB\n')
        self.commands=[]
        def fake(argv,**kwargs):
            self.commands.append(argv)
            self.assertEqual(Path(argv[0]).name,'nvidia-smi');self.assertEqual(kwargs['timeout'],12)
            return type('Result',(),{'stdout':'UNIT_FAKE_GPU, 15360, 14900, UNIT_DRIVER, 7.5'})()
        self.fake=fake
    def observe(self):return readonly.collect(proc=self.root,roots=[self.root/'manual-cache'],runner=self.fake,tool='/manual/nvidia-smi')
    def test_only_readonly_gpu_query_no_mount_namespace_install_or_generation(self):
        out=self.observe();self.assertEqual(len(self.commands),1);self.assertEqual(out['isolation_operations_attempted'],[])
        self.assertFalse(out['kernel_isolation_verified']);self.assertEqual(out['model_inferences'],0)
        self.assertNotIn('Unrelated',out['kernel_metadata']['status']);self.assertFalse(out['kernel_metadata']['cap_sys_admin_effective'])
    def test_cache_inventory_never_opens_or_hashes_checkpoint_or_receipt(self):
        cache=self.root/'manual-cache';cache.mkdir();weight=cache/readonly.MODEL['file'];weight.write_bytes(b'UNIT_NOT_WEIGHTS');(cache/'installation.json').write_text('UNIT_NOT_AN_APPROVAL')
        original=Path.read_text
        def guard(p,*a,**kw):
            if p.parent==cache:raise AssertionError('NO MODEL OR RECEIPT CONTENT READ')
            return original(p,*a,**kw)
        with patch.object(Path,'read_text',guard),patch.object(Path,'read_bytes',side_effect=AssertionError('NO WEIGHT READ')):
            out=self.observe()
        row=out['cache_metadata'][0];self.assertTrue(row['exact_filename_present']);self.assertEqual(row['bytes'],len(b'UNIT_NOT_WEIGHTS'))
        self.assertFalse(row['weight_hash_verified']);self.assertFalse(row['receipt_contents_inspected'])
    def test_symlink_cache_is_rejected_without_following_private_contents(self):
        (self.root/'manual-cache').symlink_to(self.root,target_is_directory=True)
        row=self.observe()['cache_metadata'][0];self.assertTrue(row['symlink_rejected']);self.assertFalse(row['exact_filename_present'])
    def test_missing_metadata_is_unknown_not_a_kernel_failure_or_runtime_grant(self):
        for p in (self.root/'self/status',self.root/'self/attr/current'):p.unlink()
        out=self.observe();self.assertIsNone(out['kernel_metadata']['cap_sys_admin_effective']);self.assertIsNone(out['kernel_metadata']['lsm_profile'])
        self.assertFalse(out['security_equivalence_verified']);self.assertFalse(out['model_bytes_read'])
    def test_research_boundary_is_pending_existing_approval_not_re_requested(self):
        plan=readonly.boundary_plan();self.assertFalse(plan['execution_authorized']);self.assertFalse(plan['launch_enabled'])
        self.assertEqual(plan['exact_fallback']['sha256'],'03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8')
        self.assertEqual(plan['conservative_unspent_slots'],5);self.assertFalse(plan['security_equivalent_to_studio'])
        self.assertIn('already granted',plan['fallback_model_authorization']);self.assertIn('exceeds',plan['budget_feasibility'])
    def test_probe_imports_no_model_runtime_or_network_and_never_launches_on_import(self):
        tree=ast.parse(Path(readonly.__file__).read_text())
        for n in tree.body:
            if isinstance(n,ast.Import):self.assertFalse(any(x.name in ('torch','transformers','llama_cpp','urllib.request','requests') for x in n.names))
        source=Path(readonly.__file__).read_text();self.assertNotIn('Popen(',source);self.assertNotIn('urlopen(',source);self.assertNotIn('weights_only=',source)
    def test_reproducible_notebook_pauses_even_if_a_flag_is_edited_without_authorized_launcher(self):
        root=Path(__file__).resolve().parents[1]
        notebook=json.loads((root/'verification/story_colab_compatibility_20261116/STORY_COLAB_READONLY_AND_BOUNDARY_REVIEW.ipynb').read_text())
        self.assertFalse(notebook['metadata']['redpad']['inference_enabled'])
        cells=[c for c in notebook['cells'] if c['cell_type']=='code']
        self.assertEqual(''.join(cells[0]['source']),Path(readonly.__file__).read_text())
        guard=''.join(cells[-1]['source'])
        with self.assertRaises(PermissionError):exec(compile(guard,'UNIT_NOTEBOOK_GUARD','exec'),{})
        # A boolean alone cannot enable execution or grant the new boundary.
        with self.assertRaises(RuntimeError):exec(compile(guard.replace('OPTION_C_OWNER_AUTHORIZED = False','OPTION_C_OWNER_AUTHORIZED = True'),'UNIT_NOTEBOOK_GUARD','exec'),{})
