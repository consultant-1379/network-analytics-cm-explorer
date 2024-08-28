import xlrd

directory = './'
counterLists = [
    'sgsn_counters.xlsx'#,
    # 'sapc_counters.xlsx'
]

sheets = {
    'sgsn': 4,
    'sapc': 4
}

columnNums = {
    'sgsn': [5, 8, 12, 13, 14, 15, 16, 17]#,
    # 'sapc': [5, 8, 12, 13, 14, 15, 16]
}


def parseCounterlist(node):
    g = open(directory + node.replace('xlsx', 'csv'), 'w')
    wb = xlrd.open_workbook(directory + node)
    nodeKey = node.split('_')[0]
    sheet = wb.sheet_by_index(sheets[nodeKey])
    cols = columnNums[nodeKey]
    columns = []

    for i in cols:
        columns.append(sheet.cell_value(0, i).strip())
    g.write(';'.join(columns) + '\n')

    row = []
    for i in range(1, sheet.nrows):
        for j in cols:
            row.append(str(sheet.cell_value(i, j)).strip().replace('\n', ' ').replace('\r', ''))
        g.write(';'.join(row) + '\n')
        row = []
    g.close()


for file in counterLists:
    parseCounterlist(file)
