"""Static UI contracts for consolidating scheduled session dates."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
WEB = (ROOT / "apps/web/src/main.tsx").read_text()

class SessionDatesConsolidationTests(unittest.TestCase):
    def test_explicit_time_zone(self):
        self.assertIn('Fuso orario IANA', WEB)
        self.assertIn('time_zone:appointmentZone', WEB)
        self.assertIn("Intl.DateTimeFormat('en',{timeZone:appointmentZone})", WEB)

    def test_legacy_dates_are_importable_not_edited_in_parallel(self):
        self.assertIn('Importa date dal calendario precedente', WEB)
        self.assertNotIn('Calendario legacy (sole date)', WEB)
        self.assertIn('setAppointments(await request', WEB)

    def test_deduplication_and_sorting(self):
        self.assertIn('a.some(x=>x.date===appointmentDate&&x.start_time===appointmentTime', WEB)
        self.assertIn('.sort((x,y)=>', WEB)
        self.assertIn('Salva date della sessione', WEB)

if __name__ == '__main__':
    unittest.main()
