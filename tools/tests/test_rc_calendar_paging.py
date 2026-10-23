import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]

class CalendarPagingContract(unittest.TestCase):
    def test_calendar_access_scoped(self):
        server=(ROOT/'apps/api/src/server.ts').read_text()
        self.assertIn("app.get('/api/calendar',requireAuth,requirePresenter",server)
        self.assertIn('session_appointments',server)
        self.assertIn('s.owner_id=$1 OR EXISTS',server)
        self.assertIn('time_zone',server)
    def test_appointment_validation(self):
        server=(ROOT/'apps/api/src/server.ts').read_text()
        self.assertIn('appointmentValid',server)
        self.assertIn('duration_minutes<=1440',server)
        self.assertIn("app.put('/api/sessions/:id/appointments'",server)
    def test_paging_cap(self):
        server=(ROOT/'apps/api/src/server.ts').read_text()
        self.assertIn('pageSize>100',server)
        self.assertIn('OFFSET $4',server)
        self.assertIn('OFFSET $5',server)
        ui=(ROOT/'apps/web/src/main.tsx').read_text()
        self.assertIn('page_size=${sessionPageSize}',ui)
        self.assertIn('page_size=${userPageSize}',ui)
    def test_paused_lifecycle(self):
        domain=(ROOT/'apps/api/src/domain.ts').read_text()
        schema=(ROOT/'apps/api/src/schema.sql').read_text()
        self.assertIn("paused:['active','closed']",domain)
        self.assertIn("'paused'",schema)
        self.assertIn('sessions_status_valid',schema)
    def test_calendar_ui(self):
        ui=(ROOT/'apps/web/src/main.tsx').read_text()
        self.assertIn('quorivio-calendar',ui)
        self.assertIn('session-tabs',ui)
        self.assertIn('Riprendi',ui)

if __name__=='__main__':unittest.main()
