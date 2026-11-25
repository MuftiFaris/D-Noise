from pypdf import PdfReader
r=PdfReader(r'.\\paper-artifact\\Analisis_Perbandingan_Filter_Denoising_Set12.pdf')
for i,p in enumerate(r.pages):
 t=p.extract_text() or ''
 print(i+1, 'III', 'EXPERIMENTS AND RESULT' in t,'IV','DISCUSSION' in t,'V','CONCLUSION' in t,'REFS','REFERENCES' in t)
