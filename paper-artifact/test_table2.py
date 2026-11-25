from docx import Document
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
D=Document(r'.\\paper-artifact\\paper_sanitized.docx')
t=D.tables[2]
data=[[c.text for c in row.cells] for row in t.rows]
for widths in [[.48,1.45,.8,.62],[.48,1.45,.8,.62]]:
 try:
  x=Table(data,colWidths=widths,repeatRows=1)
  x.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.4,colors.black),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)]))
  x.wrapOn(None,100,100); print('ok',widths)
 except Exception as e: print('fail',e)
