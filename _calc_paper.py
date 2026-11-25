from pathlib import Path
from denoise_manual import read_png_gray
from rumus_manual import add_salt_pepper, median_filter, adaptive_median_filter, gaussian_filter, psnr, ssim_block_average
files=sorted(Path('data/Set12').glob('*.png'))
methods=[('Median 3x3',lambda a:median_filter(a,3)),('Adaptive Median 3-7',lambda a:adaptive_median_filter(a,7)),('Gaussian 3x3',lambda a:gaussian_filter(a))]
for level in [5,10,20,30]:
 vals={n:[] for n,_ in methods}
 for i,p in enumerate(files):
  clean=read_png_gray(p); noisy=add_salt_pepper(clean,level,42+i*1000+int(level*10))
  for n,f in methods:
   out=f(noisy); vals[n].append((psnr(clean,out),ssim_block_average(clean,out)))
 print(level,*(f'{n}: {sum(x[0] for x in v)/len(v):.3f} dB, {sum(x[1] for x in v)/len(v):.5f}' for n,v in vals.items()), flush=True)
