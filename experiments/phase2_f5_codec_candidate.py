"""Static, source-locked preparation of a Vocos mel-only review candidate.

No source execution, model imports, constructor, decoder, network or installation.
This is NOT wired to the native Voice worker. Full checkpoint/state/waveform and
secure-runtime acceptance remain required before any production change.
"""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path

LOCK = {
    'modules.py': '1132b0081333cc4abe1c36b2bd709185ceaa243519ea8903bec7ab08e67d5d64',
    'spectral_ops.py': '5577771daae83a9ffc6df3f1a3ce7f3f9c2543562c8ca3f5aff740ee2b515682',
    'models.py': '7031a1e223678cfeb522046f7e179e3ff9efd70aa32f969a4234880b59be1b71',
    'heads.py': '1ae5389805e63a77eaaf36502396591e34e0d92ccc4ae94e69e3f495f551a38d',
    'pretrained.py': 'c7581e848c9b5be216f91a8db638db9bcbd4a8a5ab663d5125013d34df656758',
    'feature_extractors.py': 'a2cd1692a1eb608b2efa6708e2eb442194aef4a10c13bad6ff7daf4edf304a7c',
    'LICENSE': '8f36ba0c214d4f487ffd7ee0b8528da9b67b459bef2d115de9cd001316589f46',
}
# Preserve exact selected class/method AST; do not reimplement the mel algorithm.
SELECTION = (
    ('modules.py', ('safe_log', 'AdaLayerNorm', 'ConvNeXtBlock')),
    ('feature_extractors.py', ('FeatureExtractor', 'MelSpectrogramFeatures')),
    ('models.py', ('Backbone', 'VocosBackbone')),
    ('spectral_ops.py', ('ISTFT',)),
    ('heads.py', ('FourierHead', 'ISTFTHead')),
    ('pretrained.py', ('Vocos',)),
)
METHODS = ('__init__', 'forward', 'decode')


def prepare(files):
    if set(files) != set(LOCK):
        raise ValueError('Complete exact reviewed Vocos source/license set required')
    for name, expected in LOCK.items():
        if hashlib.sha256(files[name]).hexdigest() != expected:
            raise ValueError('Vocos source/license changed: ' + name)
    body = ast.parse('from __future__ import annotations\nfrom typing import Any, Optional\nimport torch\nimport torchaudio\nfrom torch import nn\n').body
    selected = []
    for filename, names in SELECTION:
        tree = ast.parse(files[filename])
        for name in names:
            matches = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name == name]
            if len(matches) != 1:
                raise ValueError('Missing/ambiguous reviewed symbol ' + name)
            node = copy.deepcopy(matches[0])
            if name == 'Vocos':
                node.body = [n for n in node.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str) or isinstance(n, ast.FunctionDef) and n.name in METHODS]
                if {n.name for n in node.body if isinstance(n, ast.FunctionDef)} != set(METHODS):
                    raise ValueError('Exact mel-only Vocos methods required')
            selected.append({'file':filename, 'symbol':name,
                             'selected_ast_sha256':hashlib.sha256(ast.dump(node).encode()).hexdigest()})
            body.append(node)
    module = ast.fix_missing_locations(ast.Module(body=body, type_ignores=[]))
    # A dependency review, not a claim of executable/runtime closure.
    forbidden = {'encodec', 'EncodecFeatures', 'EncodecModel', 'hf_hub_download',
                 'from_pretrained', 'from_hparams', 'codes_to_features', 'load', 'exec', 'eval'}
    for node in ast.walk(module):
        if isinstance(node, ast.Name) and node.id in forbidden or isinstance(node, ast.Attribute) and node.attr in forbidden:
            raise ValueError('Unreviewed codec/download entry point in candidate')
    license_comment = ''.join(('# ' + line if line else '#') + '\n' for line in files['LICENSE'].decode().splitlines())
    source = '# REVIEW CANDIDATE ONLY: NOT RUNTIME ACCEPTED OR ACTIVATED\n' + license_comment + '\n' + ast.unparse(module) + '\n'
    compile(source, '<reviewed-mel-candidate>', 'exec')  # Syntax only. Never exec().
    report = {'package':'vocos==0.1.0', 'selected_source_hashes':LOCK,
              'selected_ast':selected, 'candidate_sha256':hashlib.sha256(source.encode()).hexdigest(),
              'code_license':'MIT, Charactr Inc. 2023; original notice retained',
              'purpose':'Same Vocos mel/ConvNeXt/ISTFT architecture review; NOT a BigVGAN substitution',
              'encodec_source_or_weights_included':False, 'source_executed':False,
              'native_worker_changed':False, 'checkpoint_state_verified':False,
              'decoder_waveform_verified':False, 'sample_rate_contract_verified_by_execution':False,
              'secure_binding_verified':False, 'full_commercial_stack_verified':False,
              'launch_authorized':False,
              'remaining':['Secure private host source/runtime startup',
                           'Actual exact pinned IndicF5 wrapper state/key/tensor compatibility',
                           'Exact mel/decoder/waveform/24kHz acceptance and all checkpoint rights']}
    return source, report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args=parser.parse_args()
    paths={name:args.source/name for name in LOCK}
    if any(p.is_symlink() or not p.is_file() for p in paths.values()):
        raise ValueError('Regular reviewed public source files only')
    source,report=prepare({name:p.read_bytes() for name,p in paths.items()})
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'vocos_mel_candidate.py.txt').write_text(source)
    (args.output/'vocos-mel-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS static source/hash/AST preparation only; no decoder/runtime execution or production change')


if __name__=='__main__':
    main()
