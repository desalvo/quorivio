"""RC186: secure keyboard submission for presenter second-factor challenge."""
from pathlib import Path
import unittest

UI = (Path(__file__).resolve().parents[2] / 'apps/web/src/main.tsx').read_text(encoding='utf-8')


def mfa_markup(ui: str) -> str:
    start = ui.index('{emailChallenge&&<form className="panel login"')
    end = ui.index('{!emailChallenge&&<form className="panel login"', start)
    return ui[start:end]


class TotpKeyboard(unittest.TestCase):
    def test_enter_uses_native_form_submit(self):
        mfa = mfa_markup(UI)
        self.assertIn('onSubmit={e=>{e.preventDefault();void verifyEmailLogin()}}', mfa)
        self.assertIn('type="submit" disabled={mfaVerifyPending', mfa)
        self.assertIn('>Verifica / Verify</button>', mfa)
        self.assertNotIn('onClick={verifyEmailLogin}', mfa)
        self.assertEqual(mfa.count('<form '), 1)
        self.assertEqual(mfa.count('</form>'), 1)
        self.assertNotIn('</section>', mfa)

    def test_switching_or_cancelling_cannot_submit_a_code(self):
        mfa = mfa_markup(UI)
        self.assertIn('<button type="button" className="small outline" onClick={()=>setShowRecovery', mfa)
        self.assertIn('key={method} className={mfaMethod===method?', mfa)
        self.assertIn('<button type="button" className="outline small" onClick={()=>{setEmailChallenge', mfa)
        self.assertEqual(mfa.count('type="submit"'), 1)

    def test_one_time_code_is_validated_and_not_replayed(self):
        mfa = mfa_markup(UI)
        self.assertIn('value={totpCode} maxLength={6}', mfa)
        self.assertIn('e.target.value.replace(/\\D/g,\'\')', mfa)
        self.assertIn('totpCode.length!==6', mfa)
        self.assertIn('emailCode.length!==6', mfa)
        self.assertIn('!recoveryCode.trim()', mfa)
        self.assertIn('if(mfaVerifyLock.current||!emailChallenge)return;', UI)
        self.assertIn('mfaVerifyLock.current=true;', UI)
        self.assertIn('setMfaVerifyPending(true);', UI)
        self.assertIn('finally{mfaVerifyLock.current=false;setMfaVerifyPending(false)}', UI)

    def test_failure_retries_and_button_still_work(self):
        self.assertIn('}catch(e){notify(e)}finally{mfaVerifyLock.current=false;', UI)
        self.assertIn("request('/auth/mfa/challenge/verify','POST'", UI)
        self.assertIn("request('/auth/email-mfa/verify','POST'", UI)
        self.assertIn("showRecovery?'recovery':'totp'", UI)

    def test_form_regressions_are_detected(self):
        mfa = mfa_markup(UI)
        self.assertNotIn('type="button" disabled={mfaVerifyPending', mfa)
        self.assertNotIn('onClick={verifyEmailLogin}', mfa)
        changed = UI.replace('type="submit" disabled={mfaVerifyPending', 'type="button" disabled={mfaVerifyPending', 1)
        self.assertNotEqual(changed, UI)
        self.assertNotIn('type="submit" disabled={mfaVerifyPending', mfa_markup(changed))
        changed = UI.replace('onSubmit={e=>{e.preventDefault();void verifyEmailLogin()}}', '', 1)
        self.assertNotEqual(changed, UI)
        self.assertNotIn('onSubmit={e=>{e.preventDefault();void verifyEmailLogin()}}', mfa_markup(changed))


if __name__ == '__main__':
    unittest.main()
