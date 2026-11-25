from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
s=ParagraphStyle('x',fontSize=7.2,leading=8)
d=SimpleDocTemplate('paper-artifact/test-table.pdf',pagesize=A4)
data=[[Paragraph('Noise',s),Paragraph('Method',s),Paragraph('PSNR (dB)',s),Paragraph('SSIM',s)]]+[[Paragraph(v,s) for v in r] for r in [['5%','median','29','0.9'],['','adaptive','34','0.96'],['','gaussian','24','0.6']]]
t=Table(data,colWidths=[.48*inch,1.45*inch,.8*inch,.62*inch],repeatRows=1)
t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.4,colors.black)]))
d.build([t])
print('ok')
