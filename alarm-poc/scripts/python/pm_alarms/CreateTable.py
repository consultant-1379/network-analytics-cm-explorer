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
# Name    : CreateTable.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Data import *
from Spotfire.Dxp.Data.Import import *
from Spotfire.Dxp.Application import PanelTypeIdentifiers
from Spotfire.Dxp.Application.Filters import *
import Spotfire.Dxp.Application.Filters as filters

srcTable = Document.Data.Tables["KPI Tables"]
if Document.Data.Tables.Contains("FilteredKPITable"):
    dataSelection = Document.ActiveFilteringSelectionReference
    dataSource = DataTableDataSource(srcTable,dataSelection)
    desTable = Document.Data.Tables["FilteredKPITable"]
    desTable.ReplaceData(dataSource)
else:
    dataSelection = Document.ActiveFilteringSelectionReference
    dataSource = DataTableDataSource(srcTable,dataSelection)
    desTable = Document.Data.Tables.Add("FilteredKPITable", dataSource)



imp = ['MeasureType']
for p in Document.Pages:
    if(p.Title =="Alarm Definitions"):
        for panel in p.Panels:
                if panel.TypeId == PanelTypeIdentifiers.FilterPanel:
                    for group in panel.TableGroups:
                        if group.Name == "KPI Tables":
                            for fh in group.FilterHandles:
                                if fh.FilterReference.Name in imp:
                                    print fh.FilterReference.TypeId
                                    if fh.FilterReference.TypeId==FilterTypeIdentifiers.CheckBoxFilter:
                                        checkboxFilter = fh.FilterReference.As[filters.CheckBoxFilter]()
                                    for item in checkboxFilter.Values:
                                        if checkboxFilter.IsChecked('Counter') and not checkboxFilter.IsChecked('KPI'):
                                            Document.Properties["MeasureType"] = 'Counter'
                                        if checkboxFilter.IsChecked('KPI') and not checkboxFilter.IsChecked('Counter'):
                                            Document.Properties["MeasureType"] = 'KPI'
                                        if not checkboxFilter.IsChecked('KPI') and not checkboxFilter.IsChecked('Counter'):
                                            Document.Properties["MeasureType"] = 'None'