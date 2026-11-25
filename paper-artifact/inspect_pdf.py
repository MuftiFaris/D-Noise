from pathlib import Path
from pypdf import PdfReader, PdfWriter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Frame, PageTemplate
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import black
import re
ROOT=Path(__file__).parent
SRC=ROOT/'Analisis_Perbandingan_Filter_Denoising_Set12.pdf'
OUT=ROOT/'paper_final.pdf'
reader=PdfReader(str(SRC))
texts=[p.extract_text() or '' for p in reader.pages]
alltext='\n'.join(texts)
print('pages',len(reader.pages),'title',texts[0][:120])
