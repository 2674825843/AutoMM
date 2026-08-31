"""生成 AutoMM 数学建模论文 reference.docx。"""

from automm.common import ROOT, relative
from automm.paper import create_reference_doc

if __name__ == "__main__":
    output = create_reference_doc(ROOT / "templates" / "cumcm_reference.docx")
    print(relative(output))
