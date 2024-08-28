from Spotfire.Dxp.Application.Filters import *
import Spotfire.Dxp.Application.Filters as filters
from Spotfire.Dxp.Application import PanelTypeIdentifiers

imp = ['CollectionName']
for p in Document.Pages:
    if(p.Title =="Alarm Definitions"):
        for panel in p.Panels:
            if panel.TypeId == PanelTypeIdentifiers.FilterPanel:
                for group in panel.TableGroups:
                    if group.Name == "NodeCollection":
                        #group.AddNewSubGroup("Subgroup")
                        # for subGroup in group.SubGroups:
                        #     print subGroup
                            for fh in group.FilterHandles:
                                if fh.FilterReference.Name in imp:
                                    fh.FilterReference.TypeId=FilterTypeIdentifiers.ListBoxFilter
                                    thelistboxFilter = fh.FilterReference.As[filters.ListBoxFilter]()
                                    thelistboxFilter.IncludeAllValues = False
                                    aProp= Document.Properties["NeCollection"]
                                    thelistboxFilter.SetSelection(aProp)

