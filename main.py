from pathlib import Path

from docxtpl import DocxTemplate

TEMPLATES_DIR = Path().absolute() / 'templates'
RESULT_DIR = Path().absolute() / 'results'
TEST_FILE = TEMPLATES_DIR / 'test.docx'
RESULT = RESULT_DIR / 'result.docx'

doc = DocxTemplate(TEST_FILE)
# context_variables = doc.undeclared_template_variables

context = {
    'фио': "Петров М. М.",
    'дни': "14",
    'дата': "27.07.2023"
}
doc.render(context)
doc.save(RESULT)
