"""New acquisition/preflight paths only; no model, CUDA or network execution."""
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from experiments.phase2_offline_wheels import acquire, validate_row, verified
from redpad_pipeline.fp8_preflight import assigned_device_gate, precision_gate, validate_resolution, KERNEL_REVISION


class OfflineAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.row = dict(filename='fixture-1.0-py3-none-any.whl',
                        url='https://files.pythonhosted.org/packages/fixture-1.0-py3-none-any.whl',
                        bytes=4, sha256=hashlib.sha256(b'good').hexdigest())

    def test_verified_complete_archive_is_never_downloaded_again(self):
        (self.root/self.row['filename']).write_bytes(b'good')
        with patch('urllib.request.urlopen', side_effect=AssertionError('No repeat download')):
            self.assertEqual(acquire(self.row,self.root)['downloaded_bytes'],0)

    def test_same_size_tamper_is_retained_and_rejected(self):
        p=self.root/self.row['filename'];p.write_bytes(b'evil')
        self.assertFalse(verified(p,self.row))
        with patch('urllib.request.urlopen', side_effect=AssertionError('No silent replacement')):
            with self.assertRaises(ValueError):acquire(self.row,self.root)
        self.assertEqual(p.read_bytes(),b'evil')

    def test_wrong_origin_path_and_digest_fail_before_network(self):
        for change in ({'url':'https://example.invalid/fixture-1.0-py3-none-any.whl'},
                       {'filename':'../escape.whl'},{'sha256':'unknown'},{'bytes':True}):
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate_row(self.row|change)

    def test_partial_or_symlink_never_becomes_verified_archive(self):
        p=self.root/self.row['filename'];p.with_suffix('.partial').write_bytes(b'go')
        with self.assertRaises(ValueError):acquire(self.row,self.root)
        p.symlink_to(p.with_suffix('.partial'))
        with self.assertRaises(ValueError):acquire(self.row,self.root)


class FP8GateTests(unittest.TestCase):
    def kernel(self):
        return SimpleNamespace(**{k:lambda:None for k in ('matmul_2d','matmul_batched','matmul_grouped')})

    def test_exact_resolution_and_no_automatic_model_promotion(self):
        validate_resolution(KERNEL_REVISION)
        with self.assertRaises(RuntimeError):validate_resolution('main')
        r=precision_gate('cuda',[(8,9)],self.kernel(),SimpleNamespace(dequantize=False),lambda:None)
        self.assertFalse(r['model_inference_verified']);self.assertFalse(r['kernel_execution_verified'])

    def test_all_devices_and_grouped_kernel_must_pass(self):
        for caps,kernel in (([(9,0),(8,6)],self.kernel()), ([(True,9)],self.kernel()),
                            ([(8,9)],SimpleNamespace(matmul_2d=lambda:None))):
            with self.assertRaises(RuntimeError):
                precision_gate('cuda',caps,kernel,SimpleNamespace(dequantize=False),lambda:None)

    def test_real_backend_precision_mutation_is_rejected(self):
        config=SimpleNamespace(dequantize=False)
        with self.assertRaisesRegex(RuntimeError,'BF16'):
            precision_gate('cuda',[(9,0)],self.kernel(),config,lambda:setattr(config,'dequantize',True))
        with self.assertRaises(RuntimeError):
            precision_gate('cpu',[],self.kernel(),config,lambda:None)

    def test_no_device_probe_before_secure_runtime_or_for_invalid_assignment(self):
        torch=Mock()
        with self.assertRaisesRegex(RuntimeError,'Secure host'):
            assigned_device_gate(torch,None,None,[0])
        torch.cuda.is_available.assert_not_called()
        for assigned in ([0,0],[True],[],[-1]):
            with self.assertRaises(RuntimeError):
                assigned_device_gate(torch,None,None,assigned,isolated_runtime_verified=True)
        torch.cuda.is_available.assert_not_called()


class SelectedSpeakRuntimeTests(unittest.TestCase):
    def test_selected_local_decoder_does_not_require_unrelated_pip_vocos(self):
        from redpad_pipeline.worker_isolation import profile_requirements
        packages=profile_requirements('indic_speak')
        self.assertTrue({'torch','transformers','snac','numpy','soundfile','einops'} <= packages)
        self.assertTrue({'vocos','encodec'}.isdisjoint(packages))

    def test_public_diagnostic_contract_does_not_promote_contract_only_models(self):
        from redpad_pipeline.worker_isolation import profile_requirements
        from redpad_pipeline.shared_model_services import profile
        for identifier in ('qwen35_moe','wan_animate2_distilled'):
            self.assertIn('torch',profile_requirements(identifier))
            self.assertEqual(profile(identifier)['adapter'],'contract_only')


class PublicSourceTests(unittest.TestCase):
    def test_existing_source_tamper_cannot_be_replaced_by_network(self):
        from experiments.phase2_public_sources import fetch
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'source.py';path.write_bytes(b'evil')
            with patch('urllib.request.urlopen',side_effect=AssertionError('No replacement')):
                with self.assertRaises(ValueError):
                    fetch('https://example.invalid/source.py',path,hashlib.sha256(b'good').hexdigest(),4)

    def test_unreviewed_source_archive_rejected_before_extraction(self):
        from experiments.phase2_public_sources import extract_diffusers
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'absent'
            with self.assertRaises(ValueError):extract_diffusers(b'not-the-reviewed-archive',path)
            self.assertFalse(path.exists())


class DistilledPreparationTests(unittest.TestCase):
    def test_exact_source_keeps_original_bytes_and_pins_every_component_explicitly(self):
        from redpad_pipeline.wan_distilled_preparation import INDEX,locked_recipe
        raw=INDEX.read_bytes();recipe=locked_recipe(raw)
        self.assertEqual(INDEX.read_bytes(),raw)
        for name,row in recipe['local_loader_configuration'].items():
            if not name.startswith('_'):
                self.assertRegex(row[2]['revision'],'^[a-f0-9]{40}$')
        self.assertFalse(recipe['launch_authorized'])
        self.assertFalse(recipe['component_weight_equivalence_verified'])
        self.assertFalse(recipe['runtime_verified'])

    def test_changed_publisher_index_cannot_select_an_alias_or_extra_component(self):
        from redpad_pipeline.wan_distilled_preparation import INDEX,locked_recipe
        from redpad_pipeline.agents import AgentError
        for raw in (INDEX.read_bytes()+b' ',b'{"_class_name":"OtherPipeline"}'):
            with self.assertRaises(AgentError):locked_recipe(raw)

    def test_existing_service_exposes_preparation_without_worker_launch(self):
        from redpad_pipeline.shared_model_services import SharedServices
        with tempfile.TemporaryDirectory() as tmp:
            from redpad_pipeline.agents import AgentStore
            service=SharedServices(AgentStore(Path(tmp)/'agent_control.sqlite3'))
            with patch('redpad_pipeline.wan_distilled_preparation.prepare_staged',return_value={'launch_authorized':False}) as prepare:
                result=service.prepare_distilled_loader('fixture-stage')
            prepare.assert_called_once_with(service.store,'fixture-stage')
            self.assertFalse(result['launch_authorized'])


if __name__=='__main__':unittest.main()
