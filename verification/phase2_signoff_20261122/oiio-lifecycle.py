"""Bounded synthetic CPU lifecycle test, using the existing pinned LTX prefix."""
import argparse
import gc
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def checkpoint(operations):
    status=Path('/proc/self/status').read_text().splitlines()
    rss=int(next(line.split()[1] for line in status if line.startswith('VmRSS:')))
    return {'operations':operations,'pid':os.getpid(),'rss_kib':rss,
            'file_descriptors':len(list(Path('/proc/self/fd').iterdir()))}


def child(case):
    import torch
    import OpenImageIO as oiio
    if case=='torch-oiio-colour':
        import colour
    assert torch.version.cuda is None
    samples=[]
    with tempfile.TemporaryDirectory() as folder:
        target=str(Path(folder)/'synthetic.png')
        for index in range(160):
            pixels=oiio.ImageBuf(oiio.ImageSpec(32,32,3,oiio.UINT8))
            assert oiio.ImageBufAlgo.fill(pixels,(1.0,0.0,0.0)),pixels.geterror()
            assert pixels.write(target),pixels.geterror()
            read=oiio.ImageBuf(target)
            assert read.read(),read.geterror()
            assert tuple(read.getpixel(0,0))==(1.0,0.0,0.0)
            del pixels,read
            if (index+1)%16==0:
                gc.collect()
                samples.append(checkpoint(index+1))
        print(json.dumps({'case':case,'samples':samples,'python':sys.version,
                          'versions':{name:importlib.metadata.version(name)
                                      for name in ('torch','openimageio','colour-science')},
                          'weights_loaded':False,'gpu_inference':False}),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--child',choices=('torch-oiio','torch-oiio-colour'))
    args=parser.parse_args()
    if args.child:
        child(args.child)
        return
    cases=[]
    clean={'PATH':'/usr/bin:/bin','HOME':'/tmp','TMPDIR':'/tmp','LOGNAME':'redpad-worker',
           'CUDA_VISIBLE_DEVICES':'','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1',
           'PYTHONDONTWRITEBYTECODE':'1'}
    for case in ('torch-oiio','torch-oiio-colour','torch-oiio','torch-oiio-colour'):
        start=time.monotonic()
        result=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--child',case],
                              env=clean,capture_output=True,text=True,timeout=60)
        result.check_returncode()
        telemetry=json.loads(result.stdout.splitlines()[-1])
        samples=telemetry['samples']
        assert len({sample['pid'] for sample in samples})==1 and samples[-1]['operations']==160
        assert len({sample['file_descriptors'] for sample in samples})==1
        # A restart after teardown is a separate fresh process.
        cases.append({**telemetry,'exit_code':result.returncode,
                      'elapsed_seconds':round(time.monotonic()-start,3),
                      'stderr':result.stderr,
                      'nanobind_warning':'nanobind: leaked' in result.stderr,
                      'rss_first_to_last_kib':samples[-1]['rss_kib']-samples[0]['rss_kib']})
    assert len({case['samples'][0]['pid'] for case in cases})==len(cases)
    print(json.dumps({'scope':'host CPU only; bounded persistent process and clean exit',
                      'executable':sys.executable,'cases':cases},indent=2))


if __name__=='__main__':
    main()
