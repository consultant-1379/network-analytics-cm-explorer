# import pyodbc
import os
import xml.etree.ElementTree as ET

sapdir = './MOMs/SAPC_1.7.1_2019_w29/Counters/'

moms = [
    './MOMs/SGSN/MOMxmls/SgsnMmePmInstances_mp.xml',
    sapdir
]

momMapping = {}
momMapping['ERBS'] = 'ERBS'
momMapping['RNC'] = 'RAN'
momMapping['RBS'] = 'RBS'
momMapping['SgsnMmePmInstances'] = 'SGSN-MME'
momMapping['CDiaPmInstances'] = 'SAPC'
momMapping['DbsPmInstances'] = 'SAPC'
momMapping['LdePmCounters'] = 'SAPC'
momMapping['SapcInstancesCounters'] = 'SAPC'
momMapping['Ss7CafBackEndPmModel'] = 'SAPC'
momMapping['Ss7CafFrontEndPmModel'] = 'SAPC'

attribs = {}
attribs['SGSN-MME'] = '''
MeasurementType
measurementTypeId
measurementName
collectionMethod
description
aggregation
'''.split()

attribs['SAPC'] = '''
MeasurementType
measurementTypeId
measurementName
collectionMethod
description
aggregation
'''.split()


def parseMom(str):
    tree = ET.parse(str)
    root = tree.getroot()

    for child in root.iter('mib'):
        nodeType = (child.attrib['name'])
        for node in momMapping:
            if nodeType == node:
                nodeType = momMapping[node]

    g.write('MoClass;' + ';'.join(attribs[nodeType]) + '\n')
    attribsfound = []
    for classTag in root.iter('object'):
        className = classTag.attrib['parentDn']
        row = []
        attributes = {}
        moClass = ''
        if 'PMGROUP' in className.upper():
            moClass = className.upper().split('PMGROUP=')[1]
            if ',' in moClass:
                moClass = moClass.split(',')[0]
            row.append(moClass)
            attribsfound = []
            for item in classTag:
                tagName = item.attrib['name']
                attribsfound.append(tagName)
                for i in item:
                    if tagName in attribs[nodeType]:
                        attributes[tagName] = i.text.replace('\n', '').replace('\r', '').replace('&#xA;', '').replace(';', '')
            for attcol in attribs[nodeType]:
                if attcol in attributes.keys():
                    row.append(attributes[attcol])
                else:
                    row.append(' ')
            g.write(';'.join(row) + '\n')
    if momnodetype != 'SAPC':
        g.close()


for mom in moms:
    if '.xml' in mom:
        momnodetype = mom.replace('.xml', '')
        g = open('./' + momnodetype + '_mom.csv', 'w')
        parseMom(mom)
    else:
        if 'SAP' in mom:
            g = open('./SAPC_mom.csv', 'w')
            for momfile in os.listdir(mom):
                parseMom(sapdir + momfile)
            g.close()        
