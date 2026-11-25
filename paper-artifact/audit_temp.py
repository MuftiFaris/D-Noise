from docx import Document
import re
D=Document(r'.\\paper-artifact\\paper_sanitized.docx')
for p in D.paragraphs:
 if p.text.startswith('['): print(repr(p.text[:8]))
print('cites', sorted(set(int(n) for p in D.paragraphs for n in re.findall(r'\[(\d+)\]',p.text))))
print('refs_count',sum(p.text.startswith('[') for p in D.paragraphs))
print('cols', [s._sectPr.xpath('./w:cols')[0].get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}num') for s in D.sections])
