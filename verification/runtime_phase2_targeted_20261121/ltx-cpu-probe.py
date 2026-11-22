"""Independent LTX CPU dependencies, using synthetic values and no model bundle."""
import importlib
import importlib.metadata
import io
import json
import os
import sys

os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                  HF_HUB_DISABLE_TELEMETRY='1', CUDA_VISIBLE_DEVICES='')


def refuse_network(event, args):
    if event in ('socket.connect','socket.getaddrinfo','socket.sendto'):
        raise PermissionError('Offline LTX CPU probe')


sys.addaudithook(refuse_network)
checks={}
for spec in ('torch','torchvision','torchaudio','transformers:Gemma4UnifiedProcessor',
             'av','scipy','safetensors.torch','accelerate','einops','OpenImageIO','colour','cloudpickle'):
    package,_,symbol=spec.partition(':')
    try:
        module=importlib.import_module(package)
        if symbol:
            getattr(module,symbol)
        checks[spec]={'passed':True}
    except Exception as exc:
        checks[spec]={'passed':False,'error':f'{type(exc).__name__}: {exc}'}

import av
import numpy
import torch
import torchaudio
import torchvision

assert torchvision.ops.nms(torch.tensor([[0.,0.,2.,2.],[0.,0.,2.,2.]]),torch.tensor([1.,.5]),.5).tolist()==[0]
assert torchaudio.functional.resample(torch.zeros(1,80),8000,16000).shape==(1,160)
target=io.BytesIO()
with av.open(target,'w',format='wav') as container:
    stream=container.add_stream('pcm_s16le',rate=16000)
    frame=av.AudioFrame.from_ndarray(numpy.zeros((1,160),dtype=numpy.int16),format='s16',layout='mono')
    frame.sample_rate=16000
    for packet in stream.encode(frame):
        container.mux(packet)
    for packet in stream.encode():
        container.mux(packet)
target.seek(0)
with av.open(target) as container:
    frame=next(container.decode(audio=0))
    assert (frame.samples,frame.sample_rate)==(160,16000)
print(json.dumps({'executable':sys.executable,'python':sys.version,'prefix':sys.prefix,
                  'packages':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
                  'imports':checks,'cpu_native_torchvision_nms':True,'cpu_torchaudio_resample':True,
                  'pyav_synthetic_pcm_roundtrip':True,'exact_ltx_pipeline_imported':False,
                  'weights_loaded':False,'run_in_kernel_sandbox':False},indent=2,sort_keys=True))
raise SystemExit(int(any(not row['passed'] for row in checks.values())))
