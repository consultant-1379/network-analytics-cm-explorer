from xml.dom import minidom
import csv


moms = {}

moms['LTE Radio'] = {}
moms['LTE Radio']['Baseband'] = 'MOMs/Baseband-CXP2020014_1-R51B02-18Q3/mom.xml'
moms['LTE Radio']['DU'] = 'MOMs/NodeMomComplete_L18_Q3_R28F01.xml'

moms['RNC Radio'] = {}
moms['RNC Radio']['DU'] = 'MOMs/rnc_node_mim_V_9_1240.xml'

moms['RBS Radio'] = {}
moms['RBS Radio']['DU'] = 'MOMs/RbsNode_R161A_U_4_570.xml'


classes_table = open('Classes.csv', 'r')
mo_classes = []
for line in classes_table:

    if '@' in line:
       mo_classes.append(line.split('@')[2].strip())
mo_classes=set(mo_classes)

def get_text(element):
    return " ".join(t.nodeValue for t in element[0].childNodes
                    if t.nodeType == t.TEXT_NODE)


Header = 'MOClass Description NodeType SystemArea'.split()
with open('MOClassDescription.csv', 'wb') as csvfile:
    classes_csv = csv.writer(csvfile,delimiter='@', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    classes_csv.writerow(Header)

    for systemArea in moms.keys():
     for nodeType in moms[systemArea].keys():
        xmldoc = minidom.parse(moms[systemArea][nodeType])
        itemlist = xmldoc.getElementsByTagName('class')
        for s in itemlist:
            class_name = s.attributes['name'].value.strip().replace('\n','').replace('\r\n','')+''
            desc_list = s.getElementsByTagName('description')
            desc_text = ''
            if class_name in mo_classes :

                if len(desc_list) > 0:
                    desc_text = desc_text + (get_text(desc_list).strip().replace('\n', ' ').replace('\r\n', '') + '')
                    classes_csv.writerow([class_name,desc_text.encode("utf-8"),nodeType,systemArea])
                else :
                    classes_csv.writerow([class_name, desc_text.encode("utf-8"), nodeType, systemArea])

classes_table.close()
csvfile.close()




