from pathlib import Path
from pypdf import PdfReader
p=Path(r'.\\paper-artifact\\Analisis_Perbandingan_Filter_Denoising_Set12.pdf')
r=PdfReader(str(p))
for i,page in enumerate(r.pages):
 t=page.extract_text() or ''
 print('PAGE',i+1,'TABLE I', 'TABLE I. EXPERIMENTAL' in t,'TABLE II','TABLE II. FILTER' in t,'TABLE III','TABLE III. MEAN' in t,'refs',[f'[{j}]' for j in range(1,9) if f'[{j}]' in t], 'tail',t[-120:].replace('\n',' '))
