"""Compare the exact publisher's two CPU mel functions; no model or vocoder.

Only reviewed pure functions are extracted. The unsafe model.py and complete
upstream modules are never imported. A shape/range match alone is not acceptance.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import sys


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    os.environ.update(CUDA_VISIBLE_DEVICES='',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',NUMBA_DISABLE_JIT='1')
    def no_network(event,args):
        if event in ('socket.connect','socket.getaddrinfo','socket.sendto'):
            raise PermissionError('CPU mel comparison forbids networking')
    sys.addaudithook(no_network)
    source=a.source/'f5_tts/model/modules.py';raw=source.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='f72f28273af28cd3f31c660ff7d18136e250e29f1c3b3d3c29440d3bca08a619'
    import torch,torchaudio
    from librosa.filters import mel
    names={'get_bigvgan_mel_spectrogram','get_vocos_mel_spectrogram'}
    functions=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert len(functions)==2
    namespace={'torch':torch,'torchaudio':torchaudio,'librosa_mel_fn':mel,
               'mel_basis_cache':{},'hann_window_cache':{}}
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(source),'exec'),namespace)
    waveform=(.1*torch.sin(2*torch.pi*440*torch.arange(24000,dtype=torch.float32)/24000)).unsqueeze(0)
    v=namespace['get_vocos_mel_spectrogram'](waveform)
    b=namespace['get_bigvgan_mel_spectrogram'](waveform)
    common=min(v.shape[-1],b.shape[-1])
    difference=float((v[...,:common]-b[...,:common]).abs().mean())
    compatible=v.shape==b.shape and difference<1e-5
    assert not torch.cuda.is_initialized()
    report={'profile':'indicf5','source_sha256':hashlib.sha256(raw).hexdigest(),
            'fixture':'Authored 1-second CPU sine, not generated speech',
            'sample_rate':24000,'channels':100,'hop_length':256,
            'vocos_shape':list(v.shape),'bigvgan_shape':list(b.shape),
            'mean_absolute_difference_over_common_frames':difference,
            'common_frames_used_for_measurement_only':common,
            'frontends_interchangeable':compatible,'real_decoder_or_checkpoint_tested':False,
            'encodec_or_vocos_package_imported':False,'gpu_or_model_inference':False,
            'decision':'No decoder substitution authorized; trained-checkpoint compatibility and commercial codec rights remain unverified'}
    assert 'encodec' not in sys.modules and 'vocos' not in sys.modules
    a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
