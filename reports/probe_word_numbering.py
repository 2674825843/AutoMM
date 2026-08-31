from pathlib import Path
import zipfile
import copy
import sys
from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from automm.paper import export_docx_to_pdf
path = ROOT / 'reports/paper-upgrade-smoke-final/paper.docx'
with zipfile.ZipFile(path) as z:
    parts = {n: z.read(n) for n in z.namelist()}
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{' + ns['w'] + '}'
tree = ET.fromstring(parts['word/numbering.xml'])
for num in tree.findall('w:num', ns):
    if int(num.get(W + 'numId')) < 12:
        continue
    abstract_id = num.find('w:abstractNumId', ns).get(W + 'val')
    abstract = tree.xpath('w:abstractNum[@w:abstractNumId=$v]', namespaces=ns, v=abstract_id)[0]
    if abstract_id == '1':
        cloned = copy.deepcopy(abstract)
        new_id = str(100 + int(num.get(W + 'numId')))
        cloned.set(W + 'abstractNumId', new_id)
        nsid = cloned.find('w:nsid', ns)
        if nsid is not None:
            nsid.set(W + 'val', f'{int(new_id):08X}')
        for link in cloned.xpath('.//w:pStyle', namespaces=ns):
            link.getparent().remove(link)
        tree.insert(0, cloned)
        num.find('w:abstractNumId', ns).set(W + 'val', new_id)
parts['word/numbering.xml'] = ET.tostring(tree)
target = path.with_name('numbering-probe.docx')
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in parts.items():
        z.writestr(name, data)
export_docx_to_pdf(target, target.with_suffix('.pdf'), 60)
