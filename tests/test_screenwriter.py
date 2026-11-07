import copy
import unittest
from unittest.mock import patch
from redpad_pipeline.screenwriter import build_prompt, validate, generate, render, LocalWriter, WritingError


def sample():
    return {'title':'চাবি','hook':{'image':'খালি চেয়ার','question':'কে বসে?','payoff':'চেয়ার সরবে'},
            'characters':[{'name':'রাফি','want':'ঘর খোলা','voice':'সংযত'}],
            'scenes':[{'id':'s1','heading':'INT. ঘর — রাত','seconds':30,'objective':'চাবি খোঁজা',
                       'obstacle':'তালা বন্ধ','turn':'চাবি পাওয়া','consequence':'দরজা খুলবে',
                       'beats':[{'type':'action','text':'রাফি টেবিলের নিচে হাত বাড়ায়।'},
                                {'type':'dialogue','speaker':'রাফি','text':'এটা কার?'}],
                       'sound':{'music':'নেই','sfx':'চাবির ঝনঝন'}}]}

class WriterTests(unittest.TestCase):
    def test_context_contains_licensed_text_and_lessons(self):
        p=build_prompt('একটি ঘরের রহস্য','horror',30)
        for x in ['SINTEL','CC-BY-3.0','visual_first','horror','BRIEF DATA']:
            self.assertIn(x,p)
    def test_valid_and_render_order(self):
        s=sample(); self.assertEqual(validate(s,30),[])
        out=render(s); self.assertLess(out.index('হাত বাড়ায়'),out.index('**রাফি**'))
    def test_dialogue_before_action_rejected(self):
        s=sample(); s['scenes'][0]['beats'].reverse()
        self.assertTrue(any('visible action' in x for x in validate(s,30)))
    def test_bad_speaker_and_duration(self):
        s=sample(); s['scenes'][0]['beats'][1]['speaker']='অন্য'
        issues=validate(s,60)
        self.assertTrue(any('speaker' in x for x in issues)); self.assertTrue(any('Duration' in x for x in issues))
    def test_malformed_inputs_do_not_crash_validator(self):
        for s in [None,[],{'scenes':[None]},{'scenes':[{'beats':[None]}]}]:
            self.assertTrue(validate(s,30))
    def test_non_finite_duration_rejected(self):
        for seconds in [True,float('nan'),float('inf'),0]:
            with self.assertRaises(WritingError): build_prompt('গল্প','drama',seconds)
    def test_four_passes_and_review_never_approved(self):
        calls=[]
        def complete(system,prompt):
            calls.append(prompt)
            return copy.deepcopy(sample()) if len(calls) in (2,4) else {'issues':[]}
        result=generate('গল্প','horror',30,complete=complete)
        self.assertEqual(len(calls),4)
        self.assertEqual(result['status'],'needs_editorial_review')
        self.assertFalse(result['weight_training'])
        self.assertIn('EDITOR NOTES',calls[3])
    def test_invalid_rewrite_not_accepted(self):
        r=generate('গল্প','drama',30,complete=lambda *args: {})
        self.assertEqual(r['status'],'needs_revision')
    def test_no_config_and_cloud_blocked_before_network(self):
        with patch.dict('os.environ',{},clear=True):
            with self.assertRaises(WritingError): LocalWriter()
        with self.assertRaises(WritingError): LocalWriter('model:cloud')

if __name__=='__main__': unittest.main()
