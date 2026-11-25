from docx import Document
D=Document(r'.\\paper-artifact\\paper_sanitized.docx')
for i,p in enumerate(D.paragraphs):
 if p.text.startswith('TABLE'): print(i,p.text, 'pageBreaks',p._p.xml.count('w:type="page"'),'sect', 'sectPr' in p._p.xml)
