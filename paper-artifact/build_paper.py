from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUT = Path(__file__).parent
DOCX = OUT / "Analisis_Perbandingan_Filter_Denoising_Set12.docx"

authors = "Muhamad Nabil F., Mufti Faris M., Zendinan Okbah H., Revan Alifian Z."
affiliation = "Faculty of Information Technology and Data Science, Universitas Sebelas Maret"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)
sec.top_margin, sec.bottom_margin = Inches(.72), Inches(.72)
sec.left_margin, sec.right_margin = Inches(.65), Inches(.65)
sec.header_distance, sec.footer_distance = Inches(.3), Inches(.3)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
normal.font.size = Pt(9.3)
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
normal.paragraph_format.space_after = Pt(2)
normal.paragraph_format.line_spacing = 1.03

def set_columns(section, count=2, space=360):
    sectPr = section._sectPr
    cols = sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        sectPr.append(cols)
    cols.set(qn("w:num"), str(count))
    cols.set(qn("w:space"), str(space))

set_columns(sec, 1)

def fmt_run(run, size=None, bold=None, italic=None):
    run.font.name = "Times New Roman"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Times New Roman")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Times New Roman")
    if size is not None: run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    if italic is not None: run.italic = italic
    return run

def add_p(text="", *, align=None, size=None, bold=False, italic=False, before=0, after=2,
          keep=False, indent=None):
    p = doc.add_paragraph()
    p.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.03
    if keep: p.paragraph_format.keep_with_next = True
    if indent is not None: p.paragraph_format.first_line_indent = Inches(indent)
    if text.startswith("TABLE "):
        p.paragraph_format.keep_with_next = True
    fmt_run(p.add_run(text), size or 9.3, bold, italic)
    return p

def heading(roman, label):
    p = doc.add_paragraph()
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(4), Pt(2)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    prefix = f"{roman}. " if roman else ""
    fmt_run(p.add_run(f"{prefix}{label.upper()}"), 10, True)
    return p

def subhead(label):
    p = doc.add_paragraph()
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(2), Pt(1)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fmt_run(p.add_run(label), 9.2, True)
    return p

def add_table(headers, rows, widths=None, font=8.0):
    table = doc.add_table(rows=1, cols=len(headers))
    table.autofit = False
    table.style = "Table Grid"
    if widths:
        for col, width in zip(table.columns, widths): col.width = Inches(width)
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        if widths: cell.width = Inches(widths[i])
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        fmt_run(p.add_run(h), font, True)
    trPr = table.rows[0]._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    trPr.append(repeat)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            if widths: cells[i].width = Inches(widths[i])
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            fmt_run(p.add_run(str(value)), font)
    return table

def caption(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(1), Pt(2)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fmt_run(p.add_run(text), 8.5)
    return p

def start_two_columns():
    section = doc.add_section(WD_SECTION.CONTINUOUS)
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    section.top_margin, section.bottom_margin = Inches(.72), Inches(.72)
    section.left_margin, section.right_margin = Inches(.65), Inches(.65)
    section.header_distance, section.footer_distance = Inches(.3), Inches(.3)
    set_columns(section, 2, 360)

def add_section_break(section_type, num_cols):
    section = doc.add_section(section_type)
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    section.top_margin, section.bottom_margin = Inches(.72), Inches(.72)
    section.left_margin, section.right_margin = Inches(.65), Inches(.65)
    section.header_distance, section.footer_distance = Inches(.3), Inches(.3)
    set_columns(section, num_cols, 360)
    return section

# IEEE-style title block across full page width.
add_p("Analisis Pengaruh Tingkat Salt-and-Pepper Noise terhadap Kinerja Median Filter dan Adaptive Median Filter Berdasarkan PSNR dan SSIM", align=WD_ALIGN_PARAGRAPH.CENTER, size=15, bold=True, after=4)
add_p(authors, align=WD_ALIGN_PARAGRAPH.CENTER, size=10.2, after=1)
add_p("1 " + affiliation, align=WD_ALIGN_PARAGRAPH.CENTER, size=9.2, after=4)
add_p("Abstract.", align=WD_ALIGN_PARAGRAPH.LEFT, size=9.4, bold=True, after=1)
abstract = ("This study analyzes how salt-and-pepper noise density affects fixed Median Filter and Adaptive Median Filter performance on the 12 grayscale images in Set12. Noise densities of 5%, 10%, 20%, and 30% were generated with a deterministic seed schedule. The fixed median window was 3×3, while the adaptive window expanded from 3×3 to a maximum of 7×7. Restoration quality was measured using peak signal-to-noise ratio (PSNR) and an implementation-specific block-averaged structural similarity index (SSIM). Across the 12-image mean, Adaptive Median Filter achieved higher PSNR and SSIM at every tested density. At 30% noise, it reached 29.125 dB and 0.92779 SSIM, compared with 22.299 dB and 0.69362 for Median Filter. Both methods degraded as noise density increased, but the adaptive method retained more of the original image quality in this experiment. The findings are limited to the stated images, deterministic noise realization, filter windows, boundary handling, and metric implementation.")
add_p(abstract, size=9.15, after=4)
add_p("Keywords—salt-and-pepper noise, image denoising, median filter, adaptive median filter, PSNR, SSIM, Set12.", size=8.7, after=2)

heading("I", "Introduction")
add_p("Digital images may be degraded during acquisition, storage, or transmission. Salt-and-pepper noise is an impulse-noise model in which affected pixels take extreme values, commonly 0 and 255 in an 8-bit grayscale image. Since these impulses differ sharply from their local neighborhoods, they can damage visual detail and interfere with subsequent image analysis [1], [2].")
add_p("Median filtering is a nonlinear order-statistic method: each pixel is replaced by the median value in a local window. It is widely used for impulse noise, but a fixed window can leave residual impulses when many values inside the neighborhood are corrupted, while also changing legitimate image details [2], [3]. Adaptive median filtering responds to local conditions by expanding its window until the median is distinguishable from the local minimum and maximum, subject to a maximum window size [4], [5].")
add_p("The objective is to quantify how four salt-and-pepper noise densities affect Median Filter 3×3 and Adaptive Median Filter 3×3–7×7 using PSNR and SSIM. The study evaluates all 12 images in the local Set12 folder using reproducible per-image seeds. Its contribution is a controlled comparison grounded in the project's implemented algorithms, explicit metric settings, and transparent limitations.")

heading("II", "Materials and Methodology")
subhead("A. Dataset Description")
add_p("The evaluation uses the 12 grayscale PNG files stored in data/Set12. Set12 is distributed as a test-image collection in the FFDNet repository and is commonly used in image-denoising evaluation [6]. The folder contains seven 256×256 images and five 512×512 images, for 1,572,864 pixels in total. PNG data are decoded to 8-bit grayscale by the project's own reader. The image identity and source repository are recorded to support reproducibility; this study does not use a learned model or training split.")
caption("TABLE I. EXPERIMENTAL DATA AND CONTROLLED FACTORS")
add_table(["Factor", "Setting"], [
    ("Image set", "Set12, 12 grayscale images"),
    ("Spatial dimensions", "7 images 256×256; 5 images 512×512"),
    ("Noise model", "Salt-and-pepper impulses at 0 and 255"),
    ("Noise densities", "5%, 10%, 20%, and 30%"),
    ("Noise locations", "Unique pixel positions; fixed deterministic seed schedule"),
    ("Evaluation", "Mean of per-image PSNR and block-averaged SSIM"),
], [1.5, 5.25], 8.2)

subhead("B. Noise Generation")
add_p("For an image of height H and width W, the implementation selects N=round(HWρ) unique positions, where ρ is the requested density as a fraction. Selected values are assigned alternately to 0 and 255. Because a selected source pixel can already equal the assigned extreme value, the requested percentage describes selected positions, not necessarily the percentage of pixel values that visibly change. A separate reproducible seed is used for each image and density: s=42+1000i+10p, where i=0,…,11 is the sorted file index and p is the noise percentage (5, 10, 20, or 30).")

subhead("C. Denoising Methods")
add_p("Median Filter (3×3): for each output location, the nine values in the replicated-edge neighborhood are sorted and the fifth value is selected. Each output pixel is computed from the same noisy input, so raster order does not feed back filtered pixels.")
add_p("Adaptive Median Filter (3×3–7×7): the window starts at 3×3 and expands in odd increments up to 7×7. At each size, let zmin, zmed, and zmax denote the local minimum, median, and maximum, and let zxy be the center input. Stage A accepts the median when zmin<zmed<zmax. If accepted, Stage B retains zxy when zmin<zxy<zmax; otherwise it substitutes zmed. If Stage A fails at the maximum size, the final window median is used. This is the project's classical adaptive-median implementation and should not be conflated with noise-detection or selective adaptive-median variants in other publications [4], [5].")
caption("TABLE II. FILTER CONFIGURATION USED IN THE EXPERIMENT")
add_table(["Method", "Window", "Boundary", "Output rule"], [
    ("Median", "3×3", "Replicate", "Middle order statistic"),
    ("Adaptive median", "3×3 to 7×7", "Replicate", "Two-stage tests; expand as needed"),
], [1.2, 1.1, 1.2, 3.25], 8.0)

subhead("D. Quality Metrics")
add_p("For reference image I and restored image Î with M pixels, mean squared error is MSE=(1/M)Σ(I−Î)². Peak signal-to-noise ratio is PSNR=10 log₁₀(255²/MSE) dB; larger values indicate lower squared error relative to the reference. If MSE is zero, PSNR is infinite [7].")
add_p("Structural similarity compares luminance, contrast, and structure between local image signals [8]. The implementation uses the standard luminance/structure expression with C₁=(0.01·255)² and C₂=(0.03·255)², sample variances/covariance, non-overlapping 8×8 blocks, and the arithmetic mean of block scores. This block-averaged variant is the project's defined metric; it is not identical to every commonly used sliding-window SSIM implementation. A higher value indicates greater structural similarity to the clean reference.")

subhead("E. Experimental Procedure")
add_p("For each of the 12 images and each density, the clean image was read once, a noisy version was generated using the seed schedule, and each of the two filters was applied independently to that noisy image. PSNR and block-averaged SSIM were computed between each restored image and the original clean image. The reported values are arithmetic means over the 12 per-image metric values; no pooled pixel-level metric or per-image selection was used. The experiment was executed with the project's manual Python implementations in rumus_manual/filters.py, noise.py, and metrics.py.")
add_p("The evaluation script used the following reproducibility settings: image order was lexicographically sorted by PNG filename; noise density was applied to the number of unique locations; all methods used replicate padding; median used an insertion sort implemented by the project; and the adaptive maximum window was 7×7. The SSIM block size was 8×8. No parameter was tuned separately for a test image.")

heading("III", "Experiments and Result")
add_p("Adaptive Median Filter achieved higher mean PSNR and SSIM than the fixed Median Filter at all four tested noise densities. Both methods' scores declined as density increased. The gap widened at higher densities, consistent with the adaptive method's ability to enlarge its neighborhood when a 3×3 window does not provide a valid local median.")
caption("TABLE III. MEAN QUALITY SCORES OVER 12 SET12 IMAGES")
add_table(["Noise", "Method", "PSNR (dB)", "SSIM"], [
    ("5%", "Median 3×3", "29.979", "0.90423"),
    ("", "Adaptive median 3–7", "34.174", "0.96137"),
    ("10%", "Median 3×3", "29.046", "0.89419"),
    ("", "Adaptive median 3–7", "33.182", "0.95851"),
    ("20%", "Median 3×3", "26.123", "0.83903"),
    ("", "Adaptive median 3–7", "30.927", "0.94632"),
    ("30%", "Median 3×3", "22.299", "0.69362"),
    ("", "Adaptive median 3–7", "29.125", "0.92779"),
], [.75, 2.55, 1.7, 1.35], 8.0)
add_p("At 30% noise, Adaptive Median Filter exceeded the fixed median by 6.826 dB in mean PSNR and 0.23417 in mean SSIM. At 5% noise, the respective advantages were 4.195 dB and 0.05714. The growing gap suggests that adaptive window expansion was increasingly useful as impulse density rose. These aggregate values summarize this seed-controlled test only; individual images can behave differently.")

heading("IV", "Discussion")
add_p("The observed ranking is consistent with the filter mechanisms and prior studies. Median-based methods suppress isolated extreme values without averaging those values into the output, which makes them a natural baseline for salt-and-pepper corruption [1], [2]. Adaptive window expansion provides additional uncontaminated neighbors when a small neighborhood is dominated by impulses. Earlier adaptive-median work likewise studies variable windows for impulse removal and sharpness preservation [4], while selective and local-distribution approaches show that algorithm details matter [5]. The present results do not establish that this implementation outperforms those more specialized algorithms, because they were not implemented or compared here.")
add_p("PSNR and SSIM provide complementary evidence. PSNR reflects pixelwise squared error, whereas SSIM evaluates local luminance, contrast, and structural relationships [7], [8]. Their consistent ranking here strengthens the comparison, although neither metric alone proves subjective visual preference. In particular, block-averaged SSIM can yield a different value from a sliding Gaussian-window SSIM. Readers should therefore compare these numbers only when the metric implementation and parameters are compatible.")
add_p("Several limitations bound interpretation. First, Set12 contains only 12 test images and does not represent all image content. Second, the corruption is synthetic and the four levels are tested with one deterministic realization per image and level; repeated seeds would quantify variation due to random placement. Third, 8-bit values already equal to the assigned salt/pepper value may remain unchanged, so realized corruption can differ slightly from the nominal count. Fourth, only one fixed median window and one adaptive maximum window were tested. Finally, compute time was not included as an outcome. Future work should report per-image distributions, repeat noise seeds, include additional image sets, and compare selective adaptive variants under matched implementations.")

heading("V", "Conclusion")
add_p("This controlled evaluation compared Median Filter 3×3 and Adaptive Median Filter 3×3–7×7 on all 12 local Set12 grayscale images at 5%, 10%, 20%, and 30% synthetic salt-and-pepper noise. Adaptive Median Filter produced higher 12-image mean PSNR and block-averaged SSIM at every tested density. At 30% noise, its mean scores were 29.125 dB and 0.92779, compared with 22.299 dB and 0.69362 for the fixed median filter. Both methods degraded as density increased, while the adaptive method retained stronger metric scores in the tested range.")
add_p("The conclusion is restricted to the specified Set12 images, deterministic noise schedule, filter windows, replicate boundary handling, and block-averaged SSIM. A broader claim requires repeated noise realizations, additional test images, per-image analysis, and evaluation of computation cost and further adaptive filters.")

heading("", "References")
refs = [
    "Z. M. Ramadan, “Optimum image filters for various types of noise,” TELKOMNIKA (Telecommunication, Computing, Electronics and Control), vol. 16, no. 5, pp. 2458–2464, Oct. 2018, doi: 10.12928/TELKOMNIKA.v16i5.10508. [Online]. Available: https://telkomnika.uad.ac.id/index.php/TELKOMNIKA/article/view/10508",
    "V. Jayaraj and D. Ebenezer, “A new switching-based median filtering scheme and algorithm for removal of high-density salt and pepper noise in images,” EURASIP J. Adv. Signal Process., vol. 2010, Art. no. 690218, 2010, doi: 10.1155/2010/690218. [Online]. Available: https://link.springer.com/article/10.1155/2010/690218",
    "T. S. Huang, G. J. Yang, and G. Y. Tang, “A fast two-dimensional median filtering algorithm,” IEEE Trans. Acoust., Speech, Signal Process., vol. ASSP-27, no. 1, pp. 13–18, Feb. 1979, doi: 10.1109/TASSP.1979.1163188. [Online]. Available: https://files-cdn.cnblogs.com/files/Imageshop/AFastTwo-DimensionalMedianFilteringAlgorithm.pdf",
    "H. Hwang and R. A. Haddad, “Adaptive median filters: New algorithms and results,” IEEE Trans. Image Process., vol. 4, no. 4, pp. 499–502, Apr. 1995, doi: 10.1109/83.370679. [Online]. Available: https://www.icst.pku.edu.cn/mipl/docs/Hwang.pdf",
    "Z. Gao, “An adaptive median filtering of salt and pepper noise based on local pixel distribution,” in Proc. 2018 Int. Conf. Transportation & Logistics, Information & Communication, Smart City (TLICSC), 2018, pp. 473–483, doi: 10.2991/tlicsc-18.2018.77. [Online]. Available: https://www.atlantis-press.com/proceedings/tlicsc-18/25907284",
    "K. Zhang, W. Zuo, Y. Chen, D. Meng, and L. Zhang, “FFDNet: Toward a fast and flexible solution for CNN-based image denoising,” IEEE Trans. Image Process., vol. 27, no. 9, pp. 4608–4622, Sep. 2018, doi: 10.1109/TIP.2018.2839891. [Online]. Available: https://doi.org/10.1109/TIP.2018.2839891; Set12 images: https://github.com/cszn/FFDNet/tree/master/testsets/Set12",
    "A. Hore and D. Ziou, “Image quality metrics: PSNR vs. SSIM,” in Proc. 20th Int. Conf. Pattern Recognition, Istanbul, Turkey, 2010, pp. 2366–2369, doi: 10.1109/ICPR.2010.579. [Online]. Available: https://doi.org/10.1109/ICPR.2010.579",
    "Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli, “Image quality assessment: From error visibility to structural similarity,” IEEE Trans. Image Process., vol. 13, no. 4, pp. 600–612, Apr. 2004, doi: 10.1109/TIP.2003.819861. [Online]. Available: https://live.ece.utexas.edu/publications/2004/zwang_ssim_ieeeip2004.pdf",
]
for i, ref in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Inches(.25)
    p.paragraph_format.first_line_indent = Inches(-.25)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    fmt_run(p.add_run(f"[{i}] {ref}"), 7.4)

# Set language metadata and ensure no empty content placeholders remain.
doc.core_properties.title = "Analisis Pengaruh Tingkat Salt-and-Pepper Noise terhadap Kinerja Median Filter dan Adaptive Median Filter Berdasarkan PSNR dan SSIM"
doc.core_properties.subject = "Median, adaptive median, salt-and-pepper noise, PSNR, SSIM"
doc.core_properties.author = authors
doc.save(DOCX)
print(DOCX)






