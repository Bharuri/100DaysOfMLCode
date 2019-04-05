from mailmerge import MailMerge
import pyodbc as odbc
import pandas as pd
import numpy as np
import datetime as dt
import xlrd
import os
import shutil 
import comtypes.client
import zipfile


# Create the connection string for MS SQL Database 
conn = odbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=xxx;"
                      "Database=xxx;"
                      "Trusted_Connection=yes;")

# Get the details from Member_Header
FaxDetails = pd.read_sql_query("SELECT * from Table", conn)  
os.chdir('D:')
def create_pdf(in_file,out_file):
    wdFormatPDF = 17
    in_file = in_file
    out_file = out_file
    word = comtypes.client.CreateObject('Word.Application')
    doc = word.Documents.Open(in_file)
    doc.SaveAs(out_file, FileFormat=wdFormatPDF)
    doc.Close()
    word.Quit()
def zip(src, dst):
    zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            zf.write(absname, arcname)
    zf.close()
FaxDetails = FaxDetails.applymap(str)

def create_folder(df):
    df_1 = df[['Provider_Fax','Organization_Name']]
    df_1 = df_1.drop_duplicates()
    templatename = 'D:Patient Reques.docx'
    main_path = 'D:'
   
    
    
    for index, row in df_1.iterrows():
        
        # prepare the folder name
        full_folder_path = main_path + str(row['Organization_Name'])+ '_'+str(row['Provider_Fax'])
        
        #create the folder
        os.mkdir(full_folder_path)
        
        #Copy the provider letter to folders
        #shutil.copy(provider_letter_file, full_folder_path)
                
        #create the excel file inside the folder
        df_2 = df.loc[(df['Provider_Fax'] == row['Provider_Fax']) & (df['Organization_Name'] == row['Organization_Name'])]
        df_2 = df_2.applymap(str)
        excel_folderpath = full_folder_path+'/'+str(row['Organization_Name'])+ '_'+str(row['Provider_Fax'])+'.xlsx'
        writer = pd.ExcelWriter(excel_folderpath)
        df_2.to_excel(writer, index = False)
        writer.save()
        
        #look for template file Prepare the MailMerge File 
        document = MailMerge(templatename)
        src = excel_folderpath
        book = xlrd.open_workbook(src)
        work_sheet = book.sheet_by_index(0)
        finalList = []
        headers = []
        num_rows = work_sheet.nrows
        current_row = 0
        while current_row < num_rows:
            dictVal = dict()
            if(current_row == 0):
                for col in range(work_sheet.ncols):
                    headers.append(work_sheet.cell_value(current_row,col))
            else:
                for col in range(work_sheet.ncols):
                    dictVal.update({headers[col]:work_sheet.cell_value(current_row,col)})
            if(current_row!=0):
                finalList.append(dictVal)
            current_row+=1
        document.merge_pages(finalList)
        document.write(full_folder_path+'/'+ str(row['Organization_Name'])+ '_'+str(row['Provider_Fax'])+'.docx')
        
        in_file = os.path.abspath(full_folder_path+'/'+ str(row['Organization_Name'])+ '_'+str(row['Provider_Fax'])+'.docx')
        out_file = os.path.abspath('D:'+ str(row['Organization_Name'])+ '_'+str(row['Provider_Fax'])+'.pdf')
        create_pdf(in_file,out_file)  
        
        #remove the excel and word document
        #os.remove(excel_folderpath)
        #os.remove(in_file)
        
        #create zip files
#         zip(full_folder_path,'C:/Users/sanketg/Desktop/Fax Blast/CHI_Cardio_Zip_Files/'+str(row['Organization_Name'])+ '_'+str(row['Provider_Fax']) )    
            
            
