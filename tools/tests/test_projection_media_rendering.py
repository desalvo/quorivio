from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

class ProjectionMediaRendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/'apps/web/src/main.tsx').read_text()
        cls.style=(ROOT/'apps/web/src/style.css').read_text()

    def test_session_scoped_media_urls(self):
        self.assertIn('function ProjectionWidgetContent(',self.source)
        self.assertIn('encodeURIComponent(sessionId)',self.source)
        self.assertIn('encodeURIComponent(assetId)',self.source)

    def test_media_and_document_have_real_rendering(self):
        for element in ('<img className="projection-media"','<video className="projection-media"','<iframe src={url}'):
            self.assertIn(element,self.source)
        self.assertIn('rel="noopener noreferrer"',self.source)
        self.assertIn('<ProjectionWidgetContent sessionId={sessionId} widget={w} activity={activity}/>',self.source)
        self.assertIn('.projection-media{',self.style)

if __name__=='__main__':unittest.main()
