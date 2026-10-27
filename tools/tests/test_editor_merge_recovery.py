"""Source contracts for browser-backed safe editor merge recovery.

Behavioral merge semantics are covered by the 40 Node tests; these checks
prevent wiring and CI opt-in regression without pretending to run Chromium.
"""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text()
MERGE=(ROOT/'apps/web/src/page-merge.ts').read_text()
BROWSER=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()

class EditorMergeRecovery(unittest.TestCase):
 def test_merge_is_pure_and_has_no_network_side_effects(self):
  self.assertNotIn('fetch(',MERGE)
  self.assertNotIn('request(',MERGE)
 def test_server_revision_is_still_required_for_save(self):
  self.assertIn('expected_design_revision:loadedDesignRevision.current',MAIN)
 def test_conflict_does_not_allow_direct_save(self):
  self.assertIn('pageSavePending||pageConflict',MAIN)
 def test_merge_preview_uses_saved_base_local_and_fresh_remote(self):
  self.assertIn('mergePageDrafts(mergeCandidate.base??JSON.parse(savedPageDraft.current) as EditablePageDraft,mergeCandidate.local??currentPageDraft(),mergeCandidate.remote,mergeChoices)',MAIN)
 def test_conflict_resolution_is_explicit(self):
  self.assertIn('unresolvedMergeConflicts.length>0||pageSavePending',MAIN)
  self.assertIn('Scegli una versione',MAIN)
 def test_rebase_never_calls_save(self):
  self.assertNotIn('updatePageDesign()',MAIN[MAIN.index('function applyPageRebase()'):MAIN.index('function downloadPageDraft()')])
 def test_rebase_retains_remote_revision(self):
  self.assertIn('loadedDesignRevision.current=mergeCandidate.revision',MAIN)
 def test_json_draft_export_is_user_initiated(self):
     self.assertIn('onClick={()=>{downloadPageDraftFor(a);setPageThumbMenu(',MAIN)
     self.assertIn('createPageDraftBackup(selected,designActivity',MAIN)
     self.assertIn('Esporta layout JSON',MAIN)
 def test_browser_acceptance_uses_real_database_not_mock(self):
     self.assertIn("resolved=await await_revision(context,sid,aid,7)",BROWSER)
     self.assertNotIn('page.route(',BROWSER)
     self.assertIn('expected_design_revision',BROWSER)
 def test_browser_checks_server_unchanged_until_explicit_save(self):
  self.assertIn("current['design_revision']==4",BROWSER)
  self.assertIn("get_by_role('button',name='Applica riconciliazione alla bozza')",BROWSER)
 def test_browser_checks_same_field_resolution_and_remote_disjoint_field(self):
     self.assertIn("choice.select_option('local')",BROWSER)
     self.assertIn("resolved['result_design']['header']=='Remote results heading'",BROWSER)
 def test_recovery_is_keyboard_and_mobile_operable(self):
  self.assertIn('.page-merge-panel :focus-visible',CSS)
  self.assertIn('.page-merge-choice select{width:100%',CSS)
  self.assertIn('min-height:44px',CSS)

if __name__=='__main__':unittest.main()
