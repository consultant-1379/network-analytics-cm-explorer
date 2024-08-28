#!/usr/bin/python 
import xml.etree.ElementTree as ET
import csv
from collections import defaultdict

systemAreaText = 'SystemArea'
nodeTypeColumn = 'NodeType'

moms = {}
moms['LTE Radio'] = {}
moms['LTE Radio']['Baseband'] = 'MOMs/Baseband-CXP2020014_1-R45A23-18Q2/mom.xml'
moms['LTE Radio']['DU'] = 'MOMs/NodeMomComplete_L18_Q1_R35A121.xml'

moms['RNC Radio'] = {}
moms['RNC Radio']['DU'] = 'MOMs/rnc_node_mim_V_9_1240.xml'

moms['RBS Radio'] = {}
moms['RBS Radio']['DU'] = 'MOMs/RbsNode_R161A_U_4_570.xml'

with open('MO to Table mapping.csv', mode='r') as mappingFile:
    reader = csv.reader(mappingFile)
    mappingToBulkCMTable = dict((rows[0], rows[1]) for rows in reader)


def getName(attribute, attrToFind):
    name = ''
    try:
        name = attribute.find('.//' + attrToFind).attrib['name']
    except:
        name = ''
    return name


def getValue(attribute, attrToFind):
    value = ''
    try:
        if attrToFind == 'max':
            value = attribute.find('.//{}[last()]'.format(attrToFind)).text.encode(encoding='UTF-8', errors='strict').replace('\r', '\\r').replace('\n', '\\n')
            # print('attribute = {} Attr={} '.format(attribute, attrToFind))
            # values = attribute.findAll('.//[{}]'.format(attrToFind)).text.encode(encoding='UTF-8',errors='strict').replace('\r', '\\r').replace('\n', '\\n')
            # print('Attr={} Values={}'.format(attrToFind, values))
            # value = max(values)
        else:
            value = attribute.find('.//' + attrToFind).text.encode(encoding='UTF-8', errors='strict').replace('\r', '\\r').replace('\n', '\\n')
    except Exception as e:
        #        print("Caught exception : {}".format(e))
        value = ''
    return value


#
# Handle Attributes
#

descriptionTags = ['description']

unitTags = '''
min
max
defaultValue
unit
'''.split()

dataTags = '''
multiplicationFactor
resolution
minLength
maxLength
undefinedValue
'''.split()

dataTypeTags = '''
boolean
lengthRange
long
longlong
range
seqDefaultValue
sequence
string
'''.split()

#
# Handle Structs
#

structTags = '''
dependencies
deprecated
specification
'''.split()

refTags = 'enumRef moRef'.split()

# Order of columns here must align with order in for loops below
structAttrs = [systemAreaText, nodeTypeColumn, 'struct', 'structMember'] + unitTags + descriptionTags + dataTags + dataTypeTags + refTags + structTags

structsFor = {}
fileName = 'Structs'

with open(fileName + '.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='@', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow([n[0].capitalize() + n[1:] for n in structAttrs])  # capitalise first char

    for systemArea in moms.keys():
        structsFor[systemArea] = {}
        for nodeType in moms[systemArea].keys():
            print('{}: System Area = {}, MOM file = {}'.format(fileName, systemArea, moms[systemArea][nodeType]))
            tree = ET.parse(moms[systemArea][nodeType])
            root = tree.getroot()
            structsFor[systemArea][nodeType] = {}

            for parent in root.iter('struct'):
                struct = parent.attrib['name']
                structsFor[systemArea][nodeType][struct] = {}

                for child in parent.iter('structMember'):
                    structMember = child.attrib['name']
                    attr = []
                    for tag in unitTags + descriptionTags + dataTags:
                        attr += [getValue(child, tag).replace('\\n', '')]  # remove trailing newline chars

                    for tag in dataTypeTags:
                        text = 'true' if len(getValue(child, tag)) > 0 else ''  # set to true if datatype has any value
                        attr += [text]

                    for ref in refTags:
                        attr += [getName(child, ref)]

                    structsFor[systemArea][nodeType][struct][structMember] = attr[:]  # take a copy by value, not by reference

                    for tag in structTags:
                        attr += [getValue(child, tag).replace('\\n', '')]  # remove trailing newline chars

                    csvwriter.writerow([systemArea, nodeType, struct, structMember] + attr)

#
# Handle Classes
#

refTags = 'enumRef moRef structRef'.split()

attrTags = '''
condition
counterReset
counterType
dependencies
deprecated
disturbances
lockBeforeModify
mandatory
noNotification
nonPersistent
obsolete
precondition
readOnly
restricted
samplingRate
scanner
specification
takesEffect
visibility
'''.split()

# Order of columns here must align with order in for loops below
attrs = [systemAreaText, nodeTypeColumn, 'MOClass', 'attribute'] + unitTags + descriptionTags + dataTags + dataTypeTags + refTags + attrTags + ['bulkCMTable']
attrsFillerList = [None] * (len(attrTags) - 1)  # -1 to account for removed visibility tag

rulesFile = open('SimpleRules.csv', 'w')
rulesColumns = 'SystemArea MOClass Attribute ID MinValue MaxValue Comment RuleName'.split()

fileName = 'Classes'

with open(fileName + '.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='@', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow([n[0].capitalize() + n[1:] for n in attrs if n != 'visibility'])  # capitalise first char, drop visibility attribute
    rulesWriter = csv.writer(rulesFile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    rulesWriter.writerow(rulesColumns)

    for systemArea in moms.keys():
        for nodeType in moms[systemArea].keys():
            print('{}: System Area = {}, MOM file = {}'.format(fileName, systemArea, moms[systemArea][nodeType]))
            tree = ET.parse(moms[systemArea][nodeType])
            root = tree.getroot()

            for parent in root.iter('class'):
                # moClass = parent.attrib['name']
                # if not moClass in mappingToBulkCMTable:
                #     print('No Bulk CM table for ' + moClass)
                #     break

                for child in parent.iter('attribute'):
                    moClass = parent.attrib['name']
                    if not moClass in mappingToBulkCMTable:
                        print('No Bulk CM table for ' + moClass)
                        break

                    structRefFound = getName(child, 'structRef')
                    defaultValueFound = getValue(child, 'defaultValue')
                    attributeName = child.attrib['name']

                    skipEricssonOnly = False
                    attr = []
                    for tag in unitTags + descriptionTags + dataTags:
                        attr += [getValue(child, tag) if tag != 'counterType' else getValue(child, tag).replace('\\n', '')]  # remove trailing newline chars from counterType

                    for tag in dataTypeTags:
                        text = 'true' if len(getValue(child, tag)) > 0 else ''  # set to true if datatype has any value
                        attr += [text]

                    for ref in refTags:
                        attr += [getName(child, ref)]

                    for tag in attrTags:
                        if tag == 'visibility':
                            if getValue(child, tag) == 'User category: Ericsson personnel':
                                skipEricssonOnly = True
                        else:
                            attr += [getValue(child, tag) if tag != 'counterType' else getValue(child, tag).replace('\\n', '')]  # remove trailing newline chars from counterType

                    if not skipEricssonOnly:
                        csvwriter.writerow([systemArea, nodeType, moClass, attributeName] + attr + [mappingToBulkCMTable[moClass]])

                    if defaultValueFound:
                        rulesWriter.writerow([systemArea, moClass, attributeName]
                                             + ['', defaultValueFound, defaultValueFound, '']
                                             + ['{} - {} should be {}'.format(moClass, attributeName, defaultValueFound)])

                    # Write all struct attribute information
                    if structRefFound:
                        for structMember in structsFor[systemArea][nodeType][structRefFound]:
                            structAttributeName = attributeName + '_' + structMember
                            csvwriter.writerow([systemArea, nodeType, moClass, structAttributeName]
                                               + structsFor[systemArea][nodeType][structRefFound][structMember]
                                               + [structRefFound] + attrsFillerList + [mappingToBulkCMTable[moClass]])
                            defaultValueFound = structsFor[systemArea][nodeType][structRefFound][structMember][2]
                            if defaultValueFound:
                                rulesWriter.writerow([systemArea, moClass, structAttributeName]
                                                     + ['', defaultValueFound, defaultValueFound, '']
                                                     + ['{} - {} should be {}'.format(moClass, structAttributeName, defaultValueFound)])

#
# Handle Enums
#
enumTags = '''
value 
description 
deprecated 
obsolete 
specification 
visibility
'''.split()

enumAttrs = [systemAreaText, nodeTypeColumn, 'enum', 'enumMember'] + enumTags

fileName = 'Enumerations'

with open(fileName + '.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='@', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow([n[0].capitalize() + n[1:] for n in enumAttrs if n != 'visibility'])  # capitalise first char

    for systemArea in moms.keys():
        for nodeType in moms[systemArea].keys():
            print('{}: System Area = {}, MOM file = {}'.format(fileName, systemArea, moms[systemArea][nodeType]))
            tree = ET.parse(moms[systemArea][nodeType])
            root = tree.getroot()

            for parent in root.iter('enum'):
                for child in parent.iter('enumMember'):
                    attr = [systemArea, nodeType, parent.attrib['name'], child.attrib['name']]
                    skipEricssonOnly = False
                    for tag in enumTags:
                        if tag == 'visibility':
                            if getValue(child, tag) == 'User category: Ericsson personnel':
                                skipEricssonOnly = True
                        else:
                            attr += [getValue(child, tag)]
                    if not skipEricssonOnly:
                        csvwriter.writerow(attr)

#
# Handle Relationships
#


#
# From StackOverflow
# https://stackoverflow.com/questions/19472530/representing-graphs-data-structure-in-python
#

class Graph(object):
    """ Graph data structure, undirected by default. """

    def __init__(self, connections, directed=False):
        self._graph = defaultdict(set)
        self._directed = directed
        self.add_connections(connections)

    def add_connections(self, connections):
        """ Add connections (list of tuple pairs) to graph """

        for node1, node2 in connections:
            self.add(node1, node2)

    def add(self, node1, node2):
        """ Add connection between node1 and node2 """

        self._graph[node1].add(node2)
        if not self._directed:
            self._graph[node2].add(node1)

    def is_connected(self, node1, node2):
        """ Is node1 directly connected to node2 """

        return node1 in self._graph and node2 in self._graph[node1]

    def find_path(self, node1, node2, path=[]):
        """ Find any path between node1 and node2 (may not be shortest) """

        path = path + [node1]
        if node1 == node2:
            return path
        if node1 not in self._graph:
            return None
        for node in self._graph[node1]:
            if node not in path:
                new_path = self.find_path(node, node2, path)
                if new_path:
                    return new_path
        return None

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, dict(self._graph))


relationshipAttrs = [systemAreaText, nodeTypeColumn, 'Parent', 'Child', 'Min', 'Max']

fileName = 'Relationships'

with open(fileName + '.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow([n[0].capitalize() + n[1:] for n in relationshipAttrs])  # capitalise first char

    for systemArea in moms.keys():
        for nodeType in moms[systemArea].keys():
            print('{}: System Area = {}, MOM file = {}'.format(fileName, systemArea, moms[systemArea][nodeType]))
            tree = ET.parse(moms[systemArea][nodeType])
            root = tree.getroot()

            for parent in root.iter('relationship'):
                for child in parent.iter('containment'):
                    parentNode = getName(child, 'parent/hasClass')
                    childNode = getName(child, 'child/hasClass')
                    attr = [systemArea, nodeType, parentNode, childNode, getValue(child, 'child/cardinality/min'), getValue(child, 'child/cardinality/max')]
                    csvwriter.writerow(attr)

fileName = 'Hierarchy'

with open(fileName + '.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow([systemAreaText, nodeTypeColumn, 'Parent', 'Child1', 'Child2', 'Child3', 'Child4', 'Child5', 'Child6', 'Child7', 'Child8'])

    for systemArea in moms.keys():
        for nodeType in moms[systemArea].keys():
            print('{}: System Area = {}, MOM file = {}'.format(fileName, systemArea, moms[systemArea][nodeType]))
            tree = ET.parse(moms[systemArea][nodeType])
            root = tree.getroot()

            connections = []
            classes = set()

            for parent in root.iter('relationship'):
                for child in parent.iter('containment'):
                    parentNode = getName(child, 'parent/hasClass')
                    childNode = getName(child, 'child/hasClass')
                    classes.add(parentNode)
                    classes.add(childNode)
                    connections.append((parentNode, childNode))

            g = Graph(connections, directed=True)
            classes.remove('ManagedElement')

            for mo in classes:
                #       print(g.find_path('ManagedElement', mo))
                csvwriter.writerow([systemArea, nodeType] + g.find_path('ManagedElement', mo))
