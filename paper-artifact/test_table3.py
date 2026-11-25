from docx import Document
from reportlab.platypus import Table,TableStyle,Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
D=Document(r'.\\paper-artifact\\paper_sanitized.docx')
s=ParagraphStyle('x',fontSize=7,leading=8)
for ti,t in enumerate(D.tables):
 data=[[Paragraph(c.text,s) for c in row.cells] for row in t.rows]
 widths=[[1.42,5.15],[.82,.82,.72,1.36],[.48,1.45,.8,.62]][ti]
 try:
  x=Table(data,colWidths=widths,repeatRows=1); x.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.4,colors.black),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)])); print(ti,x.wrap(400,700))
 except Exception as e: print('fail',ti,e)
