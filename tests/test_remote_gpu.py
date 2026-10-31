import io,json,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from redpad_pipeline.remote_gpu import generate,GPUError

class RemoteGPUTests(unittest.TestCase):
    def picture(self):
        b=io.BytesIO();Image.new('RGB',(32,32)).save(b,format='PNG');return b.getvalue()
    def test_invalid_input_never_submits(self):
        with patch('gradio_client.Client') as client:
            with self.assertRaises(GPUError):generate(b'bad','motion','/unused')
            client.assert_not_called()
    def test_success_is_actual_download_and_no_token(self):
        calls={}
        class FakeClient:
            def __init__(self,*args,**kw):calls.update(kw)
            def submit(self,*args,**kw):
                path=Path(calls['download_files'])/'clip.mp4';path.parent.mkdir();path.write_bytes(b'video'*1000)
                return types.SimpleNamespace(result=lambda timeout:(str(path),117))
        with tempfile.TemporaryDirectory() as root,patch('gradio_client.Client',FakeClient),patch('gradio_client.handle_file',lambda x:x),patch('redpad_pipeline.media.duration',return_value=3.56):
            out=generate(self.picture(),'motion',root)
            self.assertEqual(out.read_bytes(),b'video'*1000)
            self.assertIs(calls['hf_token'],False)
            state=json.loads(out.with_name('job.json').read_text())
            self.assertEqual(state['stage'],'complete');self.assertFalse(state['paid_fallback'])
    def test_quota_saves_no_clip_and_no_retry(self):
        with tempfile.TemporaryDirectory() as root,patch('gradio_client.Client',side_effect=RuntimeError('quota exceeded')) as client:
            with self.assertRaisesRegex(GPUError,'quota'):generate(self.picture(),'motion',root)
            self.assertEqual(client.call_count,1)
            self.assertEqual(list(Path(root).rglob('animation.mp4')),[])
            state=json.loads(next(Path(root).rglob('job.json')).read_text())
            self.assertEqual(state['stage'],'failed-or-unknown')

if __name__=='__main__':unittest.main()

class FreeAccountTests(unittest.TestCase):
    def tearDown(self):
        from redpad_pipeline.remote_gpu import _verify_free_account
        pass
    def test_free_account_verified_without_gpu_call(self):
        from redpad_pipeline.remote_gpu import free_account_token
        from unittest.mock import Mock
        reply=Mock();reply.json.return_value={'type':'user','isPro':False}
        with patch.dict('os.environ',{'REDPAD_HF_FREE_TOKEN':'test-secret'}),patch('requests.get',return_value=reply):
            self.assertEqual(free_account_token(),'test-secret')
    def test_paid_or_unknown_account_blocked(self):
        from redpad_pipeline.remote_gpu import free_account_token,_verify_free_account
        from unittest.mock import Mock
        for profile in [{'type':'user','isPro':True},{'type':'org','isPro':False},{'type':'user'}]:
            pass;reply=Mock();reply.json.return_value=profile
            with patch.dict('os.environ',{'REDPAD_HF_FREE_TOKEN':'test-secret'}),patch('requests.get',return_value=reply),patch('gradio_client.Client') as client:
                with self.assertRaises(GPUError):free_account_token()
                client.assert_not_called()
