"""Read exact publisher metadata only, without following the checkpoint redirect."""
import json
from pathlib import Path
import urllib.error
import urllib.request

root=Path(__file__).resolve().parents[2]
model=json.loads((root/'assets/professional/phase3_candidates.json').read_text())['profiles']['ltx25']
repo,rev=model['repo'],model['revision']
artifact='latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors'
tree=f'https://huggingface.co/api/models/{repo}/tree/{rev}/latent_upscale_models?expand=true'
with urllib.request.urlopen(tree,timeout=15) as response:
    entry=next(row for row in json.load(response) if row['path']==artifact)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        return None

url=f'https://huggingface.co/{repo}/resolve/{rev}/{artifact}'
try:
    with urllib.request.build_opener(NoRedirect()).open(urllib.request.Request(url,method='HEAD'),timeout=15) as response:
        status=response.status
        linked_etag=response.headers.get('X-Linked-Etag')
except urllib.error.HTTPError as response:
    status=response.code
    linked_etag=response.headers.get('X-Linked-Etag')
print(json.dumps({'tree_url':tree,'artifact':artifact,'reported_size':entry['size'],
                  'publisher_lfs_oid':entry.get('lfs',{}).get('oid'),
                  'head_url':url,'head_status':status,'head_linked_etag':linked_etag,
                  'checkpoint_downloaded':False},indent=2))
