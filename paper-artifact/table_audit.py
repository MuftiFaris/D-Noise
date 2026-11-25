from docx import Document
D=Document(r'.\\paper-artifact\\paper_sanitized.docx')
for ti,t in enumerate(D.tables):
 print('TABLE',ti)
 for r in t.rows[:2]:
  print([(c.width/914400 if c.width else None, repr(c.text[:30])) for c in r.cells])
