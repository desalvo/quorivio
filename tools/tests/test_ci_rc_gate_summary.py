import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ci_rc_gate_summary import render

class RCSummary(unittest.TestCase):
    def sample(self):
        return {'score':48.,'accepted_gates':1,'gate_count':18,'release_candidate_ready':False,
                'missing_required_files':[],
                'unaccepted_gates':[{'id':'D3','status':'open','remaining':'ARM64 | Podman\nKubernetes'}]}

    def test_score_and_status(self):
        summary=render(self.sample())
        self.assertIn('48.00%',summary)
        self.assertIn('1/18 gates',summary)
        self.assertIn('NOT RC READY',summary)
        self.assertIn('ARM64 \\| Podman Kubernetes',summary)

    def test_bounded_untrusted_markdown(self):
        d=self.sample();d['unaccepted_gates'][0]['remaining']='secret\n | overwritten'+'x'*2000
        s=render(d)
        self.assertNotIn('\n | overwritten',s)
        self.assertLess(len(s),1100)

    def test_invalid_scores_rejected(self):
        for score in (True,-1,101,'48'):
            d=self.sample();d['score']=score
            with self.assertRaises(ValueError):render(d)

    def test_ready_message_only_when_evidence_is_present(self):
        d=self.sample();d['release_candidate_ready']=True;d['unaccepted_gates']=[]
        self.assertIn('**RC READY**',render(d))

if __name__=='__main__':unittest.main()
