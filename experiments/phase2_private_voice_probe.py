"""Actual source startup and mel-only diagnostics inside the unchanged sandbox.

No checkpoint construction, model forward pass, CUDA or production activation.
Gated source is a separate exact manifest mount and is never exported here.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from redpad_pipeline.native_local_bundle import digest_file,verify_tree
from redpad_pipeline.shared_model_services import profile
from redpad_pipeline.worker_isolation import RuntimeBindings,environment,isolation_command,runtime_identity,source_digest
from verification.runtime_phase2_20261121.sandbox_probe import dependencies

CHILD=r'''
import hashlib,importlib.metadata,inspect,json,os,sys
from pathlib import Path
from redpad_pipeline.worker_isolation import verify_running_runtime
identity,parent,private=json.loads(sys.argv[1]),sys.argv[2],sys.argv[3]
verify_running_runtime(identity)
assert os.readlink('/proc/self/ns/net')!=parent
assert not Path(private).exists()
assert all(k not in os.environ for k in ('HF_TOKEN','GOOGLE_APPLICATION_CREDENTIALS','LD_PRELOAD','HTTPS_PROXY'))
def offline(event,args):
    if event in ('socket.connect','socket.getaddrinfo','socket.sendto'):
        raise PermissionError('Offline model-free diagnostic')
sys.addaudithook(offline)
import torch,torchaudio,numpy,soundfile
from transformers import LlamaForCausalLM,AutoTokenizer
from snac import SNAC
from redpad_pipeline.native_voice_worker import reviewed_module
assert torch.version.cuda is None and not torch.cuda.is_initialized()
speak=reviewed_module(Path('/redpad/source/inference.py'),'reviewed_selected_speak')
decoder=reviewed_module(Path('/redpad/source/vocos/model.py'),'reviewed_selected_decoder')
assert inspect.isclass(speak.TTS) and inspect.isclass(decoder.VocosDecoder)
assert callable(speak.build_prompt) and callable(speak.ids_to_codes)
report={'status':'PASS','profile':'indic_speak','revision':'76e0814f189321efe550011850cd288dae366aad',
 'exact_source_imports':['inference.py:TTS','vocos/model.py:VocosDecoder'],
 'dependency_classes':[LlamaForCausalLM.__name__,AutoTokenizer.__name__,SNAC.__name__],
 'torch':torch.__version__,'torchaudio':torchaudio.__version__,
 'cuda_initialized':False,'weights_loaded':False,'model_inference':False,
 'namespace_private':True,'source_read_only':True,'production_launch_approved':False,
 'model_component_licenses_verified':False,'speaker_consent_granted':False,
 'professional_acceptance':False}
assert 'encodec' not in sys.modules and 'vocos' not in sys.modules
Path('/redpad/output/indic-speak-startup.json').write_text(json.dumps(report,indent=2)+'\n')
# Independent public MIT candidate: deterministic signal processing only.
candidate=Path('/redpad/input/vocos_mel_candidate.py.txt')
assert hashlib.sha256(candidate.read_bytes()).hexdigest()=='f5827f41ffd349ad726fe069182cae2d03823f9e9afbee3b9e5eb0b1ac34d6a1'
scope={'__name__':'reviewed_mel_candidate'}
exec(compile(candidate.read_bytes(),str(candidate),'exec'),scope)
torch.set_num_threads(1)
wave=(.1*torch.sin(2*torch.pi*440*torch.arange(24000,dtype=torch.float32)/24000)).unsqueeze(0)
features=scope['MelSpectrogramFeatures'](sample_rate=24000,n_fft=1024,hop_length=256,n_mels=100,padding='center')
actual=features(wave)
expected=torch.log(torch.clip(torchaudio.transforms.MelSpectrogram(sample_rate=24000,n_fft=1024,
 hop_length=256,n_mels=100,center=True,power=1)(wave),min=1e-7))
mel_error=float((actual-expected).abs().max())
assert list(actual.shape)==[1,100,94] and mel_error<=1e-6 and bool(torch.isfinite(actual).all())
window=torch.hann_window(1024)
spec=torch.stft(wave,n_fft=1024,hop_length=256,win_length=1024,window=window,center=True,return_complex=True)
decoded=scope['ISTFT'](n_fft=1024,hop_length=256,win_length=1024,padding='center')(spec)
expected_wave=wave[...,:decoded.shape[-1]]
error=float((decoded-expected_wave).abs().max())
assert error<=1e-6 and bool(torch.isfinite(decoded).all())
with torch.device('meta'):
    backbone=scope['VocosBackbone'](input_channels=100,dim=512,intermediate_dim=1536,num_layers=8)
    head=scope['ISTFTHead'](dim=512,n_fft=1024,hop_length=256,padding='center')
state={**{'backbone.'+k:list(v.shape) for k,v in backbone.state_dict().items()},
       **{'head.'+k:list(v.shape) for k,v in head.state_dict().items()}}
assert state['backbone.embed.weight']==[512,100,7]
assert state['head.out.weight']==[1026,512]
result={'status':'PASS_PARTIAL_DIAGNOSTIC','profile':'indicf5','candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
 'fixture':'Authored 1-second 440Hz sine; no generated speech',
 'sample_rate':24000,'mel_shape':list(actual.shape),'mel_max_abs_error':mel_error,
 'istft_samples':decoded.shape[-1],'istft_max_abs_error':error,
 'meta_architecture_keys':len(state),'meta_architecture_sha256':hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest(),
 'checkpoint_tensor_compatibility':False,'trained_decoder_waveform_verified':False,
 'full_runtime_accepted':False,'candidate_activated':False,
 'encodec_imported':False,'cuda_initialized':False,'weights_loaded':False,'model_inference':False}
Path('/redpad/output/vocos-mel-cpu.json').write_text(json.dumps(result,indent=2)+'\n')
Path('/redpad/output/vocos-meta-key-shapes.json').write_text(json.dumps(state,sort_keys=True,indent=2)+'\n')
print(json.dumps({'indic_speak':report,'vocos_candidate':result},sort_keys=True),flush=True)
'''

def main():
    p=argparse.ArgumentParser();p.add_argument('task',type=Path);a=p.parse_args()
    task=a.task.resolve(strict=True);prefix=task/'voice-runtime';source=task/'indic-speak'
    out=task/'acceptance';out.mkdir(exist_ok=True)
    previous=out/'completed.json'
    if previous.exists():raise RuntimeError('Completed acceptance exists; recover evidence instead of rerunning')
    selected=json.loads((ROOT/'assets/professional/phase3_voice_selected_source_lock.json').read_text())['models']['indic_speak']
    manifest={k:{'bytes':v['bytes'],'sha256':v['sha256']} for k,v in selected['files'].items()}
    verify_tree(source,manifest)
    interpreter=prefix/'bin/python3.11'
    lock=json.loads(subprocess.check_output([str(interpreter),'-B','-c',
        "import importlib.metadata,json,re; print(json.dumps({re.sub(r'[-_.]+','-',d.metadata['Name'].lower()):d.version for d in importlib.metadata.distributions()}))"],
        env={**environment(),'PYTHONPATH':''},text=True,timeout=30))
    installed=json.loads((task/'install-receipt.json').read_text())
    for name,version in installed['pins'].items():
        assert lock.get(re.sub(r'[-_.]+','-',name))==version,name
    assert lock['torch']=='2.7.1+cpu' and lock['torchaudio']=='2.7.1+cpu'
    assert not any(k.startswith('nvidia-') or k in ('triton','encodec','vocos') for k in lock)
    files={p.relative_to(prefix).as_posix():{'bytes':p.stat().st_size,'sha256':digest_file(p)}
           for p in sorted(prefix.rglob('*')) if p.is_file()}
    system,unresolved=dependencies(prefix,interpreter)
    # Like the existing accepted harness, record static optional-extension
    # sonames. The actual required imports must resolve inside the exact
    # sandbox. No system directories or extra libraries are exposed for them.
    base={'prefix':str(prefix),'interpreter':str(interpreter),'dependency_lock':lock,
          'files':files,'system_files':system,'studio_sha256':source_digest()}
    RuntimeBindings.validate('indic_speak',{**base,'profile':'indic_speak','revision':profile('indic_speak')['revision']})
    digest=hashlib.sha256(json.dumps(base,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    identity=runtime_identity(base,digest)
    (out/'runtime-manifest.json').write_text(json.dumps(base,indent=2)+'\n')
    with tempfile.TemporaryDirectory() as temporary:
        private=Path(temporary)/'private-marker';private.write_text('synthetic private marker')
        job=Path(temporary)/'request.json';job.write_text('{}')
        candidate=ROOT/'verification/phase2_final_three_20261122/vocos_mel_candidate.py.txt'
        command=isolation_command(job,out,[],runtime=base,worker='native_local_worker',
                                  source=(source,manifest),inputs=(candidate,))
        with (out/'source-startup.log').open('w') as stream:
            subprocess.run([*command[:-3],'-c',CHILD,json.dumps(identity),os.readlink('/proc/self/ns/net'),str(private)],
                env=environment(),check=True,timeout=120,stdout=stream,stderr=subprocess.STDOUT)
    report={'profile':'indic_speak','cpu_source_startup':'PASS','secure_binding':'PASS',
        'source_revision':selected['revision'],'source_files':manifest,'runtime_identity':identity,
        'manifest_files':len(files),'runtime_manifest_sha256':digest_file(out/'runtime-manifest.json'),
        'unresolved_elf_sonames':unresolved,'system_files':system,'source_digest':source_digest(),
        'gated_source_published':False,'weights_loaded':False,'gpu':False,'production_launch_approved':False,
        'prior_15_profiles_rerun':False,'phase3_started':False}
    previous.write_text(json.dumps(report,indent=2)+'\n')
    print('RP_VOICE_ACCEPTANCE_PASS '+json.dumps({'profile':'indic_speak','manifest_files':len(files),
        'weights_loaded':False,'gated_source_files':len(manifest),'vocos_candidate':'PARTIAL ONLY'}),flush=True)

if __name__=='__main__':main()
