from pathlib import Path

from docxtpl import DocxTemplate

TEMPLATES_DIR = Path().absolute() / 'templates'

variables = {}

templates = TEMPLATES_DIR.iterdir()
for template in templates:
    doc = DocxTemplate(template)
    context_variables = doc.undeclared_template_variables
    variables[template] = context_variables

print(variables)


RESULT_DIR = Path().absolute() / 'results'
TEST_FILE = TEMPLATES_DIR / 'test.docx'
RESULT = RESULT_DIR / 'result.docx'

doc = DocxTemplate(TEST_FILE)
context = {
    'фио': "Петров М. М.",
    'дни': "14",
    'дата': "27.07.2023"
}
doc.render(context)
doc.save(RESULT)


# TODO:
#  1. БД
#  2. Разбить на модули
