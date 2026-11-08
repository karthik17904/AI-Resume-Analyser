import io, os, tempfile, unittest
from pathlib import Path
from fastapi.testclient import TestClient
from docx import Document
from app.main import app
from app.repositories import analyses
from app.services.nlp import extract_skills,flatten,similarity
from app.services.resume_sections import parse_resume,tune_local
from app.services.documents import new_resume,replace_placeholders
SAMPLE="""Jane Doe
jane@example.com
+91 9876543210
SUMMARY
Python engineer with web application experience.
SKILLS
Python, SQL, FastAPI, Docker and React.
PROJECTS
- Built a FastAPI service with 150 users.
- Improved SQL queries by 30 percent.
EXPERIENCE
- Worked on database integrations at an internship.
EDUCATION
BTech Computer Science"""
class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.old=analyses.DB;analyses.DB=Path(self.temp.name)/'test.sqlite3'
        self.client=TestClient(app)
    def tearDown(self):analyses.DB=self.old;self.temp.cleanup()
    def test_skills(self):self.assertIn('Python',flatten(extract_skills(SAMPLE)))
    def test_similarity(self):self.assertGreater(similarity('python pandas machine learning','python machine learning'),0)
    def test_analyse_and_history(self):
        r=self.client.post('/api/analyse',json={'resume_text':SAMPLE,'job_description':'Python SQL Docker AWS'})
        self.assertEqual(r.status_code,200,r.text)
        data=r.json();self.assertIn('AWS',data['missing_skills'])
        self.assertEqual(self.client.get('/api/history').json()[0]['id'],data['id'])
        self.assertEqual(self.client.delete('/api/history/'+data['id']).status_code,200)
    def test_parser_and_conservative(self):
        fields=parse_resume(SAMPLE);edited,_=tune_local(fields,'Kubernetes engineer')
        self.assertNotIn('Kubernetes',edited['SKILLS'])
    def test_studio_and_word_export(self):
        r=self.client.post('/api/studio/improve',json={'resume_text':SAMPLE,'mode':'local'})
        self.assertEqual(r.status_code,200,r.text)
        form={'payload_json':__import__('json').dumps({'fields':r.json()['fields'],'design':'modern'})}
        exported=self.client.post('/api/studio/export',data=form)
        self.assertEqual(exported.status_code,200,exported.text)
        doc=Document(io.BytesIO(exported.content));self.assertIn('Jane Doe',' '.join(p.text for p in doc.paragraphs))
    def test_custom_template(self):
        doc=Document();p=doc.add_paragraph();p.add_run('{{NA');p.add_run('ME}}');doc.add_paragraph('{{SKILLS}}')
        b=io.BytesIO();doc.save(b)
        r=self.client.post('/api/studio/export',data={'payload_json':__import__('json').dumps({'fields':{'NAME':'Jane Doe','SKILLS':'Python'}})},files={'template':('mine.docx',b.getvalue(),'application/vnd.openxmlformats-officedocument.wordprocessingml.document')})
        self.assertEqual(r.status_code,200,r.text)
        new=Document(io.BytesIO(r.content));self.assertEqual(new.paragraphs[0].text,'Jane Doe')
    def test_extract_docx(self):
        doc=Document();doc.add_paragraph(SAMPLE);b=io.BytesIO();doc.save(b)
        r=self.client.post('/api/extract',files={'file':('resume.docx',b.getvalue(),'application/vnd.openxmlformats-officedocument.wordprocessingml.document')})
        self.assertEqual(r.status_code,200,r.text)
    def test_health_and_roles(self):
        self.assertEqual(self.client.get('/api/health').status_code,200)
        self.assertIn('Backend Developer',self.client.get('/api/roles').json())
if __name__=='__main__':unittest.main()
