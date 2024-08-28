# ********************************************************************
# Ericsson Inc.                                                 SCRIPT
# ********************************************************************
#
#
# (c) Ericsson Inc. 2019 - All rights reserved.
#
# The copyright to the computer program(s) herein is the property
# of Ericsson Inc. The programs may be used and/or copied only with
# the written permission from Ericsson Inc. or in accordance with the
# terms and conditions stipulated in the agreement/contract under
# which the program(s) have been supplied.
#
# ********************************************************************
# Name    : Filter.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Application.Filters import *
from Spotfire.Dxp.Application import PanelTypeIdentifiers
invisible = ['MeasureType (2)', 'KEYS', 'ELEMENT', 'TIMEAGGREGATION', 'GROUPAGGREGATION', 'FilteredNodeType', 'TABLENAME', 'COUNTERS', 'MeasureName', 'MeasureType', 'NODETYPE']
makevisible = ['SYSTEMAREA']
imp = ['SYSTEMAREA', 'NODETYPE', 'MeasureType', 'MeasureName', 'COUNTERS']
for p in Document.Pages:
    if(p.Title =="Alarm Definitions"):
        for panel in p.Panels:
            if panel.TypeId == PanelTypeIdentifiers.FilterPanel:
                for group in panel.TableGroups:
                    if group.Name == "KPI Tables":
                        #group.AddNewSubGroup("Subgroup")
                        # for subGroup in group.SubGroups:
                        #     print subGroup
                            for fh in group.FilterHandles:
                                if fh.FilterReference.Name in imp:
                                    if fh.FilterReference.Name == 'SYSTEMAREA' and fh.FilterReference.Modified:
                                        makevisible = ['SYSTEMAREA', 'NODETYPE']
                                    if fh.FilterReference.Name == 'NODETYPE' and fh.FilterReference.Modified:
                                        makevisible = ['SYSTEMAREA', 'NODETYPE', 'MeasureType']
                                    if fh.FilterReference.Name == 'KPITYPE' and fh.FilterReference.Modified:
                                        print fh.FilterReference.ToString()
                                        if fh.FilterReference.ToString().Contains('Counter'):
                                            makevisible = ['SYSTEMAREA', 'NODETYPE', 'MeasureType', 'COUNTERS']
                                        if fh.FilterReference.ToString().Contains('(KPI)'):
                                            makevisible = ['SYSTEMAREA', 'NODETYPE', 'MeasureType', 'MeasureName']
                                        if fh.FilterReference.ToString().Contains('(KPI)') and fh.FilterReference.ToString().Contains('Counter'):
                                            makevisible = ['SYSTEMAREA', 'NODETYPE', 'MeasureType', 'MeasureName', 'COUNTERS']

                                        print makevisible
                            for fh in group.FilterHandles:
                                if fh.FilterReference.Name not in makevisible:

                                    fh.Visible = False
                                else:
                                    fh.Visible = True




                                    #print fh.FilterReference.Name
                    else:
                        group.Visible = False

