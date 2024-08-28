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
# Name    : RemoveNodes.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Data import IndexSet
from Spotfire.Dxp.Data import RowSelection
from Spotfire.Dxp.Data import DataValueCursor
from Spotfire.Dxp.Data import RowSelection

#to delete the selected nodes from the table

SelectedNodeTable = Document.Data.Tables['SelectedNodes']
cursor = DataValueCursor.CreateFormatted(SelectedNodeTable.Columns["NodeName"])
markedNodes =  Document.Properties['SelectedNodes']

RowSelection = ''


for row in SelectedNodeTable.GetRows(cursor):
    value = cursor.CurrentValue
    if value in markedNodes:
        RowSelection = SelectedNodeTable.Select("NodeName = '%s'" % str(value))
        SelectedNodeTable.RemoveRows(RowSelection)

