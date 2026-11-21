"""Regressions from captured actual outputs, NOT new inference or artistic approval."""
import json,unittest
from pathlib import Path
from redpad_pipeline.kaggle_benchmark import cases,technical_validation
ROOT=Path(__file__).resolve().parents[1]/'verification/approved_gpu_writing'
CASES={c['id']:c for c in cases()['cases']}

class ActualOutputValidation(unittest.TestCase):
 def check_actual(self,id):
  raw=(ROOT/('qwen_'+id+'_raw.txt')).read_text()
  return technical_validation(CASES[id],raw,{'truncated':False})
 def test_real_scene_array_is_not_the_requested_string(self):
  v=self.check_actual('natural_dialogue')
  self.assertTrue(v['json_valid']);self.assertFalse(v['contract_field_types_valid']);self.assertFalse(v['technical_pass'])
 def test_real_grounded_but_false_criticism_does_not_pass(self):
  v=self.check_actual('clean_abstention')
  self.assertEqual(v['unsupported_quotes'],0);self.assertEqual(v['false_positive_findings'],1)
  self.assertFalse(v['critic_control_pass']);self.assertFalse(v['technical_pass'])
 def test_real_correct_detection_and_scoped_rewrite_keep_technical_status(self):
  v=self.check_actual('director_criticism');self.assertTrue(v['technical_pass']);self.assertEqual(v['true_positive_defects'],1)
  self.assertTrue(self.check_actual('targeted_rewrite')['technical_pass'])
  self.assertFalse(v['professional_accepted']);self.assertIsNone(v['artistic_scores']);self.assertEqual(v['human_review'],'pending')
 def test_nonobject_json_fails_closed_without_crashing_critic(self):
  for raw in ('[]','null','42','"scene"'):
   self.assertFalse(technical_validation(CASES['clean_abstention'],raw,{'truncated':False})['technical_pass'])
 def test_clean_control_and_string_contract_are_distinct_from_artistic_acceptance(self):
  v=technical_validation(CASES['clean_abstention'],'{"findings":[]}',{'truncated':False})
  self.assertTrue(v['technical_pass']);self.assertFalse(v['professional_accepted'])
  for scene in ([],{},None,''):
   self.assertFalse(technical_validation(CASES['natural_dialogue'],json.dumps({'scene':scene}),{'truncated':False})['technical_pass'])

if __name__=='__main__':unittest.main()
