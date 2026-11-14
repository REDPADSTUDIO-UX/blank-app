"""Bounded PCM-WAV measurements; never pronunciation, acting or musicality scores."""
import math,wave
import numpy as np
from .agents import AgentError
from .offline_media import media_path

def measure(name,sidecar):
    path=media_path(sidecar,name)
    if path.suffix.lower()!='.wav' or path.stat().st_size>100*1024*1024:raise AgentError('Bounded local PCM WAV required for audio metrics.')
    try:
        with wave.open(str(path),'rb') as wav:
            channels=wav.getnchannels();width=wav.getsampwidth();rate=wav.getframerate();frames=wav.getnframes()
            if not 1<=channels<=2 or width not in (1,2,3,4) or not 8000<=rate<=96000 or not 0<frames/rate<=300:raise AgentError('Audio metric micro-tests support mono/stereo PCM up to five minutes.')
            n=0;total=0.;squares=0.;peak=0.;full=0;quiet=0
            while raw:=wav.readframes(rate):
                if width==1:x=(np.frombuffer(raw,dtype=np.uint8).astype(np.float64)-128)/128
                elif width in (2,4):x=np.frombuffer(raw,dtype='<i'+str(width)).astype(np.float64)/(2**(8*width-1))
                else:
                    a=np.frombuffer(raw,dtype=np.uint8).reshape(-1,3).astype(np.int32)
                    x=(a[:,0]|a[:,1]<<8|a[:,2]<<16);x=np.where(x&0x800000,x-0x1000000,x).astype(np.float64)/8388608
                n+=len(x);total+=float(x.sum());squares+=float((x*x).sum());peak=max(peak,float(np.max(np.abs(x))))
                full+=int((np.abs(x)>=1-1/(2**(8*width-1))).sum());quiet+=int((np.abs(x)<.001).sum())
            if n!=frames*channels:raise AgentError('PCM sample count incomplete.')
    except (wave.Error,EOFError,ValueError):raise AgentError('Invalid PCM WAV; no audio quality score inferred.') from None
    db=lambda v:20*math.log10(v) if v>0 else None
    return {'duration_seconds':frames/rate,'sample_rate':rate,'channels':channels,'peak_dbfs':db(peak),'rms_dbfs':db(math.sqrt(squares/n)),
            'dc_offset':total/n,'sample_full_scale_fraction':full/n,'below_minus60dbfs_fraction':quiet/n,
            'listening_review_completed':False,'pronunciation_verified':False,'musicality_verified':False,
            'scope':'Signal measurements only. Quiet samples can be intentional pauses; full-scale samples are a warning, not proof of audible clipping. Not LUFS.'}
