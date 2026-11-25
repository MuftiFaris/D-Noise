from reportlab.platypus import Table,TableStyle,Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
s=ParagraphStyle('x',fontSize=7,leading=8)
data=[[Paragraph('Factor',s),Paragraph('setting',s)],[Paragraph('Image set',s),Paragraph('Set12',s)]]
for w in [[1.42,5.15],[1.42,5.15]]:
 try:
  t=Table(data,colWidths=w,repeatRows=1); t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.4,colors.black),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)])); print(t.wrap(400,700))
 except Exception as e: print(type(e),e)
