"""Source-pinned local model bridges. Imported safely; only main() may load models.

Parent must authenticate installation and isolate this process in a network namespace.
No custom class is loaded from a model directory. No downloaded or hosted backend.
"""
import json,os,sys,shutil,math
from pathlib import Path


def audit_event(event,args):
    if event in ('socket.connect','socket.bind'):
        address=args[1]
        # Native Wan NCCL rendezvous needs local communication in isolated netns.
        if not isinstance(address,tuple) or address[0] not in ('127.0.0.1','::1','localhost'):raise PermissionError('Outbound network prohibited')
    if event in ('os.system','os.exec'):raise PermissionError('Unapproved execution prohibited')
    if event=='os.posix_spawn' and Path(args[0]).name not in (Path(sys.executable).name,'ffmpeg','ffprobe'):raise PermissionError('Unapproved child executable')
    if event=='subprocess.Popen':
        executable=Path(args[0]).name
        if executable not in (Path(sys.executable).name,'ffmpeg','ffprobe'):raise PermissionError('Unapproved child executable')
        if isinstance(args[1],str):raise PermissionError('Shell command prohibited')


def safe_latent(torch,path,loader=None):
    """Future authenticated .pt tensor only; tests pass a software-only fake loader."""
    if Path(path).stat().st_size>16*1024*1024:raise ValueError('Auxiliary tensor file exceeds policy')
    value=(loader or torch.load)(str(path),weights_only=True,map_location='cpu')
    if not isinstance(value,torch.Tensor) or value.ndim!=3 or value.shape[0]!=1 or any(n<1 for n in value.shape) or value.numel()>2_000_000 or not value.is_floating_point() or not bool(torch.isfinite(value).all()):
        raise ValueError('Invalid bounded silence tensor')
    return value.transpose(1,2)


def make_ace_handler(base,torch,model_class,config_class,vae_class,text_class,tokenizer_class,model_root):
    """Explicit reviewed local classes replace upstream dynamic AutoModel loader.
    All initialization fetch/sync hooks are overridden; unknown API changes fail.
    """
    class OfflineAce(base):
        def _ensure_models_present(self,**kwargs):
            if Path(kwargs['checkpoint_path']).resolve()!=Path(model_root).resolve() or kwargs['config_path']!='acestep-v15-turbo':raise ValueError('Exact ACE local bundle required')
            return None  # Parent already verified full signed-by-owner inventory.
        @staticmethod
        def _sync_model_code_if_needed(*args,**kwargs):
            return None  # Fixed reviewed source class, never model-side Python.
        def _load_main_model_from_checkpoint(self,*,model_checkpoint_path,device,use_flash_attention,compile_model,quantization):
            if use_flash_attention or compile_model or quantization is not None:raise ValueError('Unsupported ACE precision/compile recipe')
            cfg=config_class.from_pretrained(model_checkpoint_path,local_files_only=True)
            self.model=model_class.from_pretrained(model_checkpoint_path,config=cfg,local_files_only=True,use_safetensors=True,dtype=self.dtype,attn_implementation='eager').to(device).eval()
            self.config=self.model.config;self.config._attn_implementation='eager'
            self._sync_alignment_config();self._apply_cuda_bool_argsort_workaround()
            self.silence_latent=safe_latent(torch,Path(model_checkpoint_path)/'silence_latent.pt').to(device).to(self.dtype)
            return 'eager'
        def _load_vae_model(self,*,checkpoint_dir,device,compile_model,vae_variant=None):
            if compile_model or vae_variant not in (None,'official'):raise ValueError('Unsupported VAE substitution')
            path=str(Path(checkpoint_dir)/'vae')
            self.vae=vae_class.from_pretrained(path,local_files_only=True,use_safetensors=True).to(device).eval();return path
        def _load_text_encoder_and_tokenizer(self,*,checkpoint_dir,device):
            path=str(Path(checkpoint_dir)/'Qwen3-Embedding-0.6B')
            self.text_tokenizer=tokenizer_class.from_pretrained(path,local_files_only=True,trust_remote_code=False)
            self.text_encoder=text_class.from_pretrained(path,local_files_only=True,trust_remote_code=False,use_safetensors=True).to(device).eval();return path
    return OfflineAce()


def ltx(job):
    from ltx_pipelines.distilled import DistilledPipeline
    from ltx_pipelines.utils.model_paths import ModelPaths
    from ltx_pipelines.utils.types import ImageConditioningInput
    from ltx_pipelines.utils.media_io import encode_media_segments
    from .offline_specialist_preparation import LTX_SLOTS,LTX_AUXILIARY
    root=Path(job['install']['model_root']);r=job['call']['arguments']
    paths=ModelPaths.from_split(**{k+'_path':str(root/v) for k,v in LTX_SLOTS.items()})
    pipeline=DistilledPipeline(model_paths=paths,spatial_upsampler_path=str(root/LTX_AUXILIARY['path']),loras=(),quantization=None)
    images=[]
    if job['references'].get('image_reference'):images=[ImageConditioningInput.at(job['references']['image_reference'],0,1.0)]
    chunks,_,_=pipeline.stream_chunks(**r,images=images)
    output=str(Path(job['output_dir'])/'output.mp4')
    encode_media_segments(chunks,fps=r['frame_rate'],output_path=output,video_chunks_number=None)
    return output


def wan(job):
    from omegaconf import OmegaConf
    from pipelines.wan_animate_2_pipeline import WanAnimate2MPIPipeline
    cfg=OmegaConf.load(str(Path(job['install']['source_root'])/'infer/wan_animate_2.yaml'))
    # Use a fixed class, never upstream arbitrary factory selected by config/user.
    if cfg.pop('type')!='pipelines.wan_animate_2_pipeline.WanAnimate2MPIPipeline':raise ValueError('Unknown native pipeline type')
    root=Path(job['install']['model_root'])
    cfg.model_path=str(root/'wan_animate_2/wan_animate_2_bf16.safetensors')
    for key,name in [('t5_checkpoint','models_t5_umt5-xxl-enc-bf16.pth'),('vae_checkpoint','vae.pth'),('clip_checkpoint','models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth'),('t5_tokenizer','umt5-xxl'),('clip_tokenizer','xlm-roberta-large')]:
        cfg.model[key]=str(root/'videomodel/Wan-AI'/name)
    pipeline=WanAnimate2MPIPipeline(cfg)
    result=pipeline(refer_img_path=job['references']['image_reference'],tpl_video_path=job['references']['video_reference'],output_path=job['output_dir'],**job['call']['arguments'])
    return result


def ace(job):
    import torch
    if not torch.cuda.is_bf16_supported():raise ValueError('Selected native BF16 recipe unavailable; no silent FP16/quantized fallback')
    from acestep.handler import AceStepHandler
    from acestep.models.turbo.modeling_acestep_v15_turbo import AceStepConditionGenerationModel
    from acestep.models.common.configuration_acestep_v15 import AceStepConfig
    from acestep.inference import GenerationParams,GenerationConfig,generate_music
    from diffusers.models import AutoencoderOobleck
    from transformers import AutoModel,AutoTokenizer
    root=job['install']['model_root'];os.environ['ACESTEP_CHECKPOINTS_DIR']=root
    handler=make_ace_handler(AceStepHandler,torch,AceStepConditionGenerationModel,AceStepConfig,AutoencoderOobleck,AutoModel,AutoTokenizer,root)
    _,ok=handler.initialize_service(project_root=job['install']['source_root'],config_path='acestep-v15-turbo',device='cuda',use_flash_attention=False,compile_model=False,offload_to_cpu=False,quantization=None,use_mlx_dit=False,vae_checkpoint='official')
    if not ok:raise ValueError('Offline ACE initialization failed')
    a=job['call']['arguments'];cfg=dict(a['config'],use_random_seed=False,seeds=[a['params']['seed']])
    result=generate_music(handler,None,GenerationParams(**a['params']),GenerationConfig(**cfg),save_dir=job['output_dir'])
    (Path(job['output_dir'])/'raw_native_result.json').write_text(json.dumps(result.to_dict(),ensure_ascii=False,default=str))
    if not result.success or len(result.audios)!=1:raise ValueError('ACE generation failed or wrong artifact count')
    return result.audios[0]['path']


def legacy(job):
    from .offline_preparation import NATIVE
    import importlib
    payload=job['legacy_payload'];path=Path(job['output_dir'])/'legacy_request.json';path.write_text(json.dumps(payload))
    importlib.import_module(NATIVE[job['profile']][2]).run(str(path))
    return payload['output']


def main(path):
    job=json.loads(Path(path).read_text());out=Path(job['output_dir'])
    if job.get('research_execution_authorized') is not True or job.get('network_namespace_required') is not True:raise PermissionError('Explicit isolated research authorization required')
    if not job.get('parent_network_namespace') or job['parent_network_namespace']==os.readlink('/proc/self/ns/net'):raise PermissionError('Kernel-isolated network namespace required before any model import')
    from .native_local_bundle import validate_install,digest_file
    validate_install(job['install'])
    sys.addaudithook(audit_event)
    for k,v in {'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_DATASETS_OFFLINE':'1','TORCH_FORCE_WEIGHTS_ONLY_LOAD':'1','DO_NOT_TRACK':'1'}.items():os.environ[k]=v
    for key in list(os.environ):
        if key.lower().endswith('_proxy') or key in ('HF_TOKEN','HUGGING_FACE_HUB_TOKEN','OPENAI_API_KEY'):os.environ.pop(key,None)
    if job['profile'] in ('ltx25','wan_animate2','ace15'):
        source=Path(job['install']['source_root']);sys.path.insert(0,str(source))
        if job['profile']=='ltx25':
            for package in ('ltx-core','ltx-pipelines'):sys.path.insert(0,str(source/'packages'/package/'src'))
    begin={'inference_started':False,'inference_completed':False,'software_fixture':False,'human_reviewed':False,'production_ready':False}
    state=out/'worker_state.json';state.write_text(json.dumps(begin))
    begin['inference_started']=True;state.write_text(json.dumps(begin))
    result={'ltx25':ltx,'wan_animate2':wan,'ace15':ace}.get(job['profile'],legacy)(job)
    raw=Path(result).absolute()
    if any(p.is_symlink() for p in (raw,*raw.parents)):raise ValueError('Symlink output prohibited')
    artifact=raw.resolve()
    if not artifact.is_relative_to(out.resolve()) or not artifact.is_file() or not 0<artifact.stat().st_size<=512*1024*1024:raise ValueError('Invalid or escaped output artifact')
    begin.update(inference_completed=True,artifact=artifact.relative_to(out.resolve()).as_posix(),artifact_sha256=digest_file(artifact),bytes=artifact.stat().st_size)
    if artifact.suffix=='.wav':
        import wave
        with wave.open(str(artifact),'rb') as w:
            if job['profile']=='ace15' and w.getframerate()!=48000:raise ValueError('ACE output sample rate differs')
            begin.update(sample_rate=w.getframerate(),channels=w.getnchannels(),audio_seconds=w.getnframes()/w.getframerate())
    state.write_text(json.dumps(begin,indent=2))

if __name__=='__main__':main(sys.argv[1])
