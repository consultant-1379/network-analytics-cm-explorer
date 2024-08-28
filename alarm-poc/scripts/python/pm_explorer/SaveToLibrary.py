from Spotfire.Dxp.Framework.Library import LibraryManager, LibraryItemType, LibraryItemRetrievalOption

dataTable = Document.Data.Tables['Measures']

folder = '/Custom Library/PM Explorer'
fileName = 'Measures'
fullPath = str(folder + fileName)

lm = Application.GetService(LibraryManager)
(foundFile, fileItem) = lm.TryGetItem(fullPath, LibraryItemType.SbdfDataFile, LibraryItemRetrievalOption.IncludeProperties)
(foundFolder, folderItem) = lm.TryGetItem(folder, LibraryItemType.Folder, LibraryItemRetrievalOption.IncludeProperties)

if foundFile:
    dataTable.ExportDataToLibrary(fileItem, fileName)
    print 'File found and overwritten'
elif foundFolder:
    dataTable.ExportDataToLibrary(folderItem, fileName)
    print 'File not found but folder exists, writing the SDBF file there'
else:
    print 'File or Path not found. Please review settings'
