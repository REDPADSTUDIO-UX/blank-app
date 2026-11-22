"""Only new static candidate and authorization contracts. No Torch/inference."""
import ast
from pathlib import Path
import unittest
from unittest.mock import patch

from experiments.phase2_f5_codec_candidate import LOCK, prepare

SOURCE=Path(__file__).resolve().parents[1]/'verification/phase2_final_three_20261122/public-vocos-source'


class MelCandidateTests(unittest.TestCase):
    def files(self):
        return {name:(SOURCE/name).read_bytes() for name in LOCK}

    def test_changed_source_or_license_is_rejected_before_compilation(self):
        for name in ('feature_extractors.py','LICENSE'):
            files=self.files();files[name]+=b' '
            with self.subTest(name=name),self.assertRaises(ValueError):prepare(files)

    def test_missing_or_extra_code_cannot_enter_reviewed_candidate(self):
        for update in ({'additional.py':b'pass'},):
            with self.assertRaises(ValueError):prepare(self.files()|update)
        files=self.files();del files['models.py']
        with self.assertRaises(ValueError):prepare(files)

    def test_no_source_execution_or_module_import_during_preparation(self):
        with patch('builtins.exec',side_effect=AssertionError('No execution')):
            source,report=prepare(self.files())
        self.assertFalse(report['source_executed'])
        self.assertFalse(report['secure_binding_verified'])
        self.assertFalse(report['launch_authorized'])

    def test_encodec_and_hub_download_entrypoints_are_absent(self):
        source,_=prepare(self.files());tree=ast.parse(source)
        imports=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
        self.assertEqual(len(imports),5)
        vocos=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Vocos')
        self.assertEqual({n.name for n in vocos.body if isinstance(n,ast.FunctionDef)}, {'__init__','forward','decode'})
        for name in ('EncodecFeatures','EncodecModel','hf_hub_download','from_pretrained','codes_to_features'):
            self.assertNotIn(name,source)

    def test_selected_mel_ast_and_attribution_are_preserved(self):
        source,report=prepare(self.files())
        original=ast.parse(self.files()['feature_extractors.py'])
        candidate=ast.parse(source)
        for name in ('FeatureExtractor','MelSpectrogramFeatures'):
            a=next(n for n in original.body if isinstance(n,ast.ClassDef) and n.name==name)
            b=next(n for n in candidate.body if isinstance(n,ast.ClassDef) and n.name==name)
            self.assertEqual(ast.dump(a),ast.dump(b))
        self.assertIn('Copyright (c) 2023 Charactr Inc.',source)
        self.assertFalse(report['full_commercial_stack_verified'])
        self.assertFalse(report['checkpoint_state_verified'])


if __name__=='__main__':unittest.main()
