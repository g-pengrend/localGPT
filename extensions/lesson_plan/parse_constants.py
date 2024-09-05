import os
from lxml import etree

SOURCE_FOLDER = './extensions/lesson_plan/Lesson_plan(Template 1)'
OUTPUT_FILENAME = './extensions/lesson_plan/outputs/Lesson_plan.docx'
# Define the namespaces used in your XML document
NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'wpc': 'http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas',
    'cx': 'http://schemas.microsoft.com/office/drawing/2014/chartex',
    'cx1': 'http://schemas.microsoft.com/office/drawing/2015/9/8/chartex',
    'cx2': 'http://schemas.microsoft.com/office/drawing/2015/10/21/chartex',
    'cx3': 'http://schemas.microsoft.com/office/drawing/2016/5/9/chartex',
    'cx4': 'http://schemas.microsoft.com/office/drawing/2016/5/10/chartex',
    'cx5': 'http://schemas.microsoft.com/office/drawing/2016/5/11/chartex',
    'cx6': 'http://schemas.microsoft.com/office/drawing/2016/5/12/chartex',
    'cx7': 'http://schemas.microsoft.com/office/drawing/2016/5/13/chartex',
    'cx8': 'http://schemas.microsoft.com/office/drawing/2016/5/14/chartex',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'aink': 'http://schemas.microsoft.com/office/drawing/2016/ink',
    'am3d': 'http://schemas.microsoft.com/office/drawing/2017/model3d',
    'o': 'urn:schemas-microsoft-com:office:office',
    'oel': 'http://schemas.microsoft.com/office/2019/extlst',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'v': 'urn:schemas-microsoft-com:vml',
    'wp14': 'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
    'w16cex': 'http://schemas.microsoft.com/office/word/2018/wordml/cex',
    'w16cid': 'http://schemas.microsoft.com/office/word/2016/wordml/cid',
    'w16': 'http://schemas.microsoft.com/office/word/2018/wordml',
    'w16sdtdh': 'http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash',
    'w16se': 'http://schemas.microsoft.com/office/word/2015/wordml/symex',
    'wpg': 'http://schemas.microsoft.com/office/word/2010/wordprocessingGroup',
    'wpi': 'http://schemas.microsoft.com/office/word/2010/wordprocessingInk',
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
    'mc:Ignorable': 'w14 w15 w16se w16cid w16 w16cex w16sdtdh wp14',
}

# Load the XML document
xml_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'document.xml'))
TREE = etree.parse(xml_file_path)
ROOT = TREE.getroot()

# Find the placeholders
PLACEHOLDER_LO = ROOT.xpath('//comment()[contains(., "Placeholder for start of LO")]')
PLACEHOLDER_EVENT1 = ROOT.xpath('//comment()[contains(., "Placeholder for start of Event 1")]')
PLACEHOLDER_EVENT2 = ROOT.xpath('//comment()[contains(., "Placeholder for start of Event 2")]')
PLACEHOLDER_EVENT3 = ROOT.xpath('//comment()[contains(., "Placeholder for start of Event 3")]')
PLACEHOLDER_EVENT4 = ROOT.xpath('//comment()[contains(., "Placeholder for start of Event 4")]')
PLACEHOLDER_EVENT5 = ROOT.xpath('//comment()[contains(., "Placeholder for start of Event 5")]')

PLACEHOLDERS_DICT = {
    'event 1': PLACEHOLDER_EVENT1,
    'event 2': PLACEHOLDER_EVENT2,
    'event 3': PLACEHOLDER_EVENT3,
    'event 4': PLACEHOLDER_EVENT4,
    'event 5': PLACEHOLDER_EVENT5
}

# Define the fixed portion of XML with namespaces
PROFESSIONAL_ATTRIBUTES_XML = f"""
    <w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
            w14:paraId="4FE64598" w14:textId="7022EF89" w:rsidR="00AD0810" w:rsidRPr="00B62852" w:rsidRDefault="00A71EB0" w:rsidP="003A6883">
        <w:pPr>
            <w:rPr>
                <w:sz w:val="22"/>
                <w:szCs w:val="22"/>
                <w:u w:val="single"/>
            </w:rPr>
        </w:pPr>
        <w:r w:rsidRPr="00B62852">
            <w:rPr>
                <w:sz w:val="22"/>
                <w:szCs w:val="22"/>
                <w:u w:val="single"/>
            </w:rPr>
            <w:t xml:space="preserve">Related </w:t>
        </w:r>
        <w:r w:rsidR="00547371" w:rsidRPr="00B62852">
            <w:rPr>
                <w:sz w:val="22"/>
                <w:szCs w:val="22"/>
                <w:u w:val="single"/>
            </w:rPr>
            <w:t>Professional Attributes</w:t>
        </w:r>
        <w:r w:rsidR="00AD0810" w:rsidRPr="00B62852">
            <w:rPr>
                <w:sz w:val="22"/>
                <w:szCs w:val="22"/>
                <w:u w:val="single"/>
            </w:rPr>
            <w:t>:</w:t>
        </w:r>
    </w:p>
"""