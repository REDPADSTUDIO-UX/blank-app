"""Build safe artifacts from captured Colab stdout. No inference or downloads."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_COMMIT = 'ed1362f44df708ab19a103412f422a2cd2b5e160'

def save(name, value):
    (HERE/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def main():
    observed = json.loads((HERE/'colab_stdout.txt').read_text())
    historical = json.loads((ROOT/'verification/story_t4_20261114/call_summary.json').read_text())
    assert len(historical) == 2
    assert observed['call_budget'] == {'ceiling':7,'historical_consumed':2,'new_calls':0,'remaining':5}
    assert not any(x['exact_filename_present'] for x in observed['cache_metadata'])
    assert not any(x['present'] for x in observed['runtime_files'])
    assert observed['model_downloads'] == observed['model_inferences'] == 0
    assert observed['research_boundary_checks']['drive_mount_detected'] is False
    save('current_preflight.json', observed)
    model = observed['previously_approved_fallback']
    runtime_assets = [
        {'file':'cudart-llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz','bytes':594371580,
         'sha256':'caec3617f1fd440b85b80f0c2db031ef483f383a1939c684f0476d1d3086caea'},
        {'file':'llama-b12318-bin-ubuntu-cuda-12.8-x64.tar.gz','bytes':197999267,
         'sha256':'e5c7ec6d5924059d6222cfad3b266d88fafdb3772700e23f8b0d23f7d68ce797'}]
    for item in runtime_assets:
        item['url'] = 'https://github.com/ggml-org/llama.cpp/releases/download/b12318/'+item['file']
    receipt = json.loads((ROOT/'verification/story_t4_20261114/colab_export/installation.json').read_text())
    manifest = {
        'base_commit':BASE_COMMIT,'status':'BLOCKED_MISSING_LOCAL_BUNDLE_DOWNLOAD_DECISION',
        'owner_option_c_authorization':{'granted':True,'source':'Current user-authored OPTION C AUTHORIZATION & EXECUTION prompt',
          'scope':'Separate research-only fictional Story benchmark; no Studio security-equivalence claim'},
        'download_authorization_for_missing_bundle':False,
        'download_stop_source':'Current owner instruction 8: missing approved model requires necessary download authorization; no automatic download',
        'model':model,'model_url':f"https://huggingface.co/{model['repo']}/resolve/{model['revision']}/{model['file']}",
        'model_license':'Apache-2.0 per preserved pinned source; current source not re-fetched',
        'runtime':{'repo':'ggml-org/llama.cpp','release':'b12318','commit':'7021f7e09','license':'MIT',
          'binary_sha256':receipt['binary_sha256'],'archives':runtime_assets},
        'necessary_transfer_bytes':model['bytes']+sum(x['bytes'] for x in runtime_assets),
        'current_local_hash_verification':'NOT POSSIBLE: exact files absent in checked approved paths',
        'runtime_compatibility':'NOT TESTED: runtime absent; historical successful same binary/model evidence retained',
        'browser':{'family':'Chrome','owner_existing_notebook_access':'VERIFIED','notebook_all_changes_saved':True,
          'session':'Disconnected on arrival; one successful normal reconnect; no quota bypass',
          'free_tier':'You are not subscribed; zero compute units; free resources not guaranteed',
          'ui_session_estimate':'Up to 3 hours 40 minutes; not guaranteed remaining GPU quota',
          'remaining_gpu_quota_hours':None},
        'boundary':observed['research_boundary_checks'],
        'production_worker_changed':False,'bubblewrap_or_unshare_retest':False,
        'new_calls':0,'new_downloads':0,'new_canary':'NOT RUN','new_complete_story':'ABSENT',
        'human_review':'PENDING','artistic_acceptance':False,'production_ready':False,
        'next_action':'Obtain exact missing-bundle download authorization; then verify pinned source/artifact hashes, clean research workspace, dependency compatibility, and budget before any generation',
        'cache_scope':'Only named approved roots and exact runtime paths; no claim that every private/global cache was searched'}
    save('continuation_manifest.json', manifest)
    save('call_ledger.json', {
        'ceiling':7,'historical_calls':historical,'historical_consumed':2,'new_calls':[],
        'conservative_remaining':5,'counter_reset':False,
        'fresh_canary_plus_five_existing_sections':{'required_calls':6,'fits':False},
        'execution_requirement':'Before any launcher import, retain historical reservations/receipts in the effective ledger; a fresh output directory must never reset the total',
        'existing_runner_review':'Preserved runner counts local output JSON files only. Do not launch it on an empty directory without binding the two historical calls to the effective budget.',
        'budget_increase_authorized':False})
    evaluation = json.loads((ROOT/'verification/story_colab_compatibility_20261116/story_evaluation_status.json').read_text())
    assert len(evaluation['criteria']) == 15
    assert all(x['score'] is None for x in evaluation['criteria'])
    evaluation['option_c_checkpoint'] = 'No generation: missing local bundle; earlier partial-defect evidence preserved without rerunning evaluation'
    save('story_evaluation_status.json', evaluation)
    previous = json.loads((ROOT/'verification/story_colab_compatibility_20261116/preservation.json').read_text())['files_unchanged']
    for relative, expected in previous.items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == expected, relative
    for relative in ['PHASE3_STORY_COLAB_COMPATIBILITY_REPORT_BN.md',
       'verification/story_colab_compatibility_20261116/STORY_COLAB_READONLY_AND_BOUNDARY_REVIEW.ipynb']:
        previous[relative] = hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
    save('preservation.json',{'base_commit':BASE_COMMIT,'files_unchanged':previous,
      'scope':'Protected production architecture, prior evidence, original report/notebook; no successful tests repeated'})
    source = (HERE/'preflight_cell.py').read_text()
    ast.parse(source)
    notebook = {'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3'},
        'research_only':True,'inference_enabled':False,'original_notebook_reused_without_modification':
        'verification/story_colab_compatibility_20261116/STORY_COLAB_READONLY_AND_BOUNDARY_REVIEW.ipynb'},
      'cells':[
        {'cell_type':'markdown','id':'scope','metadata':{},'source':[
         '# Option C — authorized research-only checkpoint\n',
         'This is a faithful export of the new metadata cell run in the owner’s existing Colab notebook.\n',
         'No model launcher, automatic downloads, Drive mount, production integration, or isolation-equivalence claim.\n',
         'Original paused boundary notebook is preserved. Option C authorization is now granted by the owner; missing-bundle download is not.\n',
         'Do not Run All in the historical Stages notebook. Reuse already saved outputs; no successful tests need rerunning.\n']},
        {'cell_type':'code','id':'actual-preflight','metadata':{'evidence_source':'Browser-observed Cell 13; original execution count 3'},
         'source':source.splitlines(keepends=True),'execution_count':3,
         'outputs':[{'output_type':'stream','name':'stdout','text':(HERE/'colab_stdout.txt').read_text().splitlines(keepends=True)}]},
        {'cell_type':'markdown','id':'stop','metadata':{},'source':[
         '## BLOCKED — missing exact approved model and reviewed runtime\n',
         'Seven total calls: two historical calls retained, zero new calls, five remaining. A fresh canary plus five sections would require six.\n',
         'Current kernel/PID/mount/network security equivalence is NOT verified; production Story Secure Worker remains unchanged.\n',
         'All 15 new creative scores remain null; independent human review PENDING.\n']}]}
    save('STORY_OPTION_C_RESEARCH_PREFLIGHT.ipynb',notebook)
    save('validation_receipt.json', {'validation':'One new artifact consistency/static syntax/preservation validation; not model tests or creative proof',
      'parsed_actual_stdout':True,'fifteen_criteria_unscored':True,'historical_calls_preserved':2,
      'protected_files_byte_identical':len(previous),'new_preflight_syntax_valid':True,
      'previous_cpu_regressions_rerun':False,'model_calls':0,'downloads':0})
    print(json.dumps({'artifact_validation':'PASS','protected_files':len(previous),'calls_used':2,'calls_remaining':5,'download_bytes_requested':manifest['necessary_transfer_bytes']}))

if __name__ == '__main__':
    main()
