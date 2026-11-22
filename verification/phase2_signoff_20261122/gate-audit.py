"""Fail-closed checks with a temporary empty store and synthetic requests."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from redpad_pipeline.agents import AgentError, AgentStore
from redpad_pipeline.native_local_bundle import verify_ltx_auxiliary
from redpad_pipeline.shared_model_services import SharedServices
from redpad_pipeline.voice_native_contracts import require_reference_consent


def rejection(call,needle):
    try:
        call()
    except AgentError as error:
        assert needle in str(error)
        return str(error)
    raise AssertionError('Approval gate unexpectedly accepted a synthetic request')


with TemporaryDirectory() as folder:
    root=Path(folder)
    store=AgentStore(root/'agent_control.sqlite3')
    service=SharedServices(store)
    results={}
    for name in ('qwen35_moe','wan_animate2_distilled'):
        with patch('redpad_pipeline.shared_model_services.checkpoint_manifest',
                   side_effect=AssertionError('Contract-only route touched a checkpoint')):
            results[name]=rejection(lambda:service.approve_install(
                name,root/'nonexistent','synthetic test','synthetic test',confirmed=True),'No substitution')
    results['ltx25_no_publisher_sha']=rejection(lambda:verify_ltx_auxiliary({}),'SHA256 unverified')
    staged={'plan':{'request':{}},'context':{'task':'synthetic-audit'}}
    results['indicf5_no_consent']=rejection(lambda:require_reference_consent(store,staged,{}),
                                              'explicit human voice consent')
    with store.tx() as db:
        assert db.execute('SELECT COUNT(*) FROM shared_model_installs').fetchone()[0]==0
    print(json.dumps({'check_count':len(results),'checks':results,'installs_created':0},indent=2))
