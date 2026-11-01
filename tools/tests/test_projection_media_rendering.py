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
        for element in ('<CroppedImage className="projection-media"','<video className="projection-media"','<iframe src={url}'):
            self.assertIn(element,self.source)
        self.assertIn('rel="noopener noreferrer"',self.source)
        self.assertIn('<ProjectionWidgetContent sessionId={sessionId} widget={w} activity={activity} joinCode={snapshot.session.join_code} sessionTitle={snapshot.session.title} pageNumber={slidePageNumber(snapshot.activities,activity.id)} masterTitleStyle={snapshot.session.theme?.master?.titleStyle}/>',self.source)
        self.assertIn('.projection-media{',self.style)
        self.assertIn('function CroppedImage(',self.source)
        self.assertIn('.pptx-cropped-image{',self.style)

if __name__=='__main__':unittest.main()
