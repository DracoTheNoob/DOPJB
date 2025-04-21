import openpyxl

workbook = openpyxl.load_workbook('src/stats.xlsx', data_only=True)


def read_by_id(sheet_name: str, identifier: str, column: str, column_id='A'):
    sheet = workbook[sheet_name]

    for row in range(2, sheet.max_row+1):
        if sheet[f'{column_id}{row}'].value == identifier:
            return sheet[f'{column}{row}'].value

    return None


def read_cell(sheet_name: str, cell: str):
    sheet = workbook[sheet_name]
    return sheet[cell].value
