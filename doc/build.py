import sys,os,glob,re
import markdown

dir = os.path.dirname(sys.argv[0]) or '.'
os.chdir(dir)
for f in glob.glob('*.md') + glob.glob('*.txt'):
  base = re.search(r'([^\.]*)',f).group(1)
  print base
  markdown.markdownFromFile(f, base+'.html')
  
#if sys.platform=='darwin':
#  os.system("open /0-table_of_contents.html" % dir)
