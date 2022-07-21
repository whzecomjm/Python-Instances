from pdfrw import PdfReader, PdfWriter

def run_stage(src, out):
  i = PdfReader(src)
  o = PdfWriter()
  sum_i = len(i.pages)
  num_i = i.Root.PageLabels.Nums
  for r in range(1, len(num_i) // 2):
    o.addpage(i.pages[int(num_i[r * 2]) - 1])
  o.addpage(i.pages[sum_i - 1])
  o.write(out)

run_stage("slide1.pdf", "res.pdf")
