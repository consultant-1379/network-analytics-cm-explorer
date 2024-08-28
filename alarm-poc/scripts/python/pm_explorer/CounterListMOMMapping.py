g = open('./sgsn_counterlist_mom.csv', 'w')

momFile = './SGSN-MME_SgsnMmePmInstances_mom.csv'
counterListFile = './sgsn_counters.csv'
mom = open(momFile, 'r')
counterlist = open(counterListFile, 'r')

# columnsCounterListSGSN = '''Version
# Counter or Gauge Name
# Description
# GSM
# WCDMA
# LTE
# NR
# PM Group
# Counter or Gauge'''.split('\n')

# columnsMomSGSN = '''MoClass
# MeasurementType
# measurementTypeId
# measurementName
# collectionMethod
# description
# aggregation'''.split('\n')

mapColumnsSGSN = '''MoClass
MeasurementType
measurementTypeId
measurementName
collectionMethod
description
aggregation
Node Version
GSM
WCDMA
LTE
NR
PM Group
Counter or Gauge'''.split('\n')


# columnsCounterList = columnsCounterListSGSN
# columnsMom = columnsMomSGSN
# columns = columnsCounterList + columnsMom

mapColumns = mapColumnsSGSN

row = []
count = 0

g.write(';'.join(mapColumns) + '\n')

for momrow in mom:
    momvalues = momrow.split(';')
    counterlist = open(counterListFile, 'r')
    for counterrow in counterlist:
        countervalues = counterrow.split(';')
        if countervalues[1].upper() == momvalues[3].upper():
            counters = countervalues[0] + ';' + ';'.join([countervalues[i] for i in range(3, 6)]) + ';;' + countervalues[6] + ';' + countervalues[7]
            mapping = ';'.join(momvalues).replace('\n', '').replace('\r', '') + ';' + counters.replace('\n', '').replace('\r', '')
            g.write(mapping + '\n')

g.close()
