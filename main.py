from docxtpl import DocxTemplate

from database import DataBaseInterface
from const import TEMPLATES_DIR


class GenDocs:

    def __init__(self):
        self.db = DataBaseInterface()
        templates = self.get_templates()
        variables = self.get_variables(templates)
        self.db.add_templates(variables)

    @staticmethod
    def get_templates():
        return TEMPLATES_DIR.glob('*.docx')

    @staticmethod
    def get_variables(template_list):
        variables = {}

        for template_path in template_list:
            doc = DocxTemplate(template_path)
            template_variables = doc.undeclared_template_variables
            variables[template_path.name] = list(template_variables)

        return variables


# RESULT_DIR = Path().absolute() / 'results'
# TEST_FILE = TEMPLATES_DIR / 'test.docx'
# RESULT = RESULT_DIR / 'result.docx'
#
# doc = DocxTemplate(TEST_FILE)
# context = {
#     'фио': "Петров М. М.",
#     'дни': "14",
#     'дата': "27.07.2023"
# }
# doc.render(context)
# doc.save(RESULT)


if __name__ == '__main__':
    gen = GenDocs()

# TODO:
#  1. БД
#  2. Qt
