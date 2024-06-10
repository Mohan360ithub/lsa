# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt
from frappe.utils.file_manager import get_file
import frappe,requests,boto3,os
from frappe.model.document import Document
import datetime
from urllib.parse import quote


class JobApplication(Document):
    
    def before_insert(self):
        if self.resume:
            response=store_rsp_in_s3(self.full_name,self.resume)
            if response["status"]:
                self.resume=None
                self.s3_url=response["s3_url"]

            # frappe.throw(f"{str(self.resume)}")
    # def on_update(self):
    #     if self.resume:
    #         store_rsp_in_s3(self.name)
    # pass


@frappe.whitelist()
def store_rsp_in_s3(full_name,file_url=None):
    s3_doc=frappe.get_doc("S3 360 Dev Test")
    # Configure boto3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_doc.access_key,
        aws_secret_access_key=s3_doc.secret_key,
        region_name=s3_doc.region_name,
    )

    # file_link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Recurring%20Service%20Pricing&name={rsp_id}&format=Recurring%20Service%20Pricing%20default&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{rsp_id}.pdf"

    # Fetch file content from link
    file_content = get_file_from_link(file_url)
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H_%M")

    if file_url:
        # job_application = frappe.get_doc("Job Application", str(japp_id))
        # Bucket name and file name
        bucket_name = s3_doc.bucket
        folder_name = f'360ITHUB/HR/Recruitment'
        file_name = f'{full_name+formatted_datetime}.pdf'
        # print(file_content)
        # Upload file to S3
        
        
        try:
            response = s3_client.put_object(Bucket=bucket_name, Key=f"{folder_name}/{file_name}", Body=file_content)
            # print(response)
            # print(response.json())
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                # return "File uploaded successfully"
                try:
                    s3_client.head_object(Bucket=bucket_name, Key=f"{folder_name}/{file_name}")

                    resume_file = frappe.get_all("File", 
                                                      filters={"file_url":file_url,
                                                               },
                                                      )
                    if file_url:
                        frappe.delete_doc("File",resume_file[0].name)

                    # job_application.resume=None
                    # job_application.s3_url=f"{folder_name}/{file_name}"
                    # job_application.save()

                    return {"status":True ,"msg":"File Uploaded Successfully","s3_url":f"{folder_name}/{file_name}"}
                except Exception as er1:
                    # frappe.throw("Verification of the file upload Failed")
                    return {"status":False,"msg":"Verification of the file upload Failed","error":f"{str(er1)}"}  
            else:
                # frappe.throw("Failed to upload Resume to Cloud")
                return {"status":False,"msg":f"Failed to upload file to S3: {response['ResponseMetadata']['HTTPStatusCode']}"}
            
        except Exception as e:
            # print(e)
            return {"status":False,"msg":f"Error uploading file to S3: {e}","file_content":str(file_content)}
    else:
        return {"status":False,"msg":f"Failed to fetch file from link."}



def get_file_from_link(file_url):
    try:
        # job_application = frappe.get_doc("Job Application", str(japp_id))
        # attachment = job_application.resume  # Assuming only one attachment is present
        
        file_list = frappe.get_all("File", filters={"file_url":file_url})
        if not file_list:
            # frappe.throw("No file attached to the document.")
            pass
            # Check if file_url is available
        file_doc = frappe.get_doc("File", file_list[0].name)

        file_url = file_doc.file_url
        
        site_path = frappe.utils.get_site_path()
        if not file_doc.is_private:
            full_file_path = site_path + '/public' + file_url
        else:
            full_file_path = site_path + file_url
    
        # Ensure the file exists
        if not os.path.exists(full_file_path):
            frappe.throw(f"The file at path {full_file_path} does not exist.")
        
        # Open and read the PDF file
        with open(full_file_path, 'rb') as file:
            if file:
                file_content = file.read()
                return file_content
            else:
                print(f"Failed to fetch file from link.")
                return None
    except Exception as e:
        print(f"Error fetching file from link: {e}")
        return None



@frappe.whitelist()
def generate_presigned_url(file_name):
    s3_doc=frappe.get_doc("S3 360 Dev Test")
    # Configure boto3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_doc.access_key,
        aws_secret_access_key=s3_doc.secret_key,
        region_name=s3_doc.region_name,
    )
    
    bucket_name = s3_doc.bucket

    try:
        # Generate a presigned URL for the file
        presigned_url = s3_client.generate_presigned_url('get_object',
                                                          Params={'Bucket': bucket_name, 'Key': file_name},
                                                          ExpiresIn=3600)  # URL expires in 1 hour (3600 seconds)
        return presigned_url
    except Exception as e:
        frappe.throw(f'Failed to generate presigned URL: {e}')



@frappe.whitelist()
def delete_file(japp_id):
    job_application = frappe.get_doc("Job Application", str(japp_id))
    s3_doc=frappe.get_doc("S3 360 Dev Test")
    # Configure boto3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_doc.access_key,
        aws_secret_access_key=s3_doc.secret_key,
        region_name=s3_doc.region_name,
    )
    
    bucket_name = s3_doc.bucket

    try:
        response = s3_client.delete_object(
            Bucket=bucket_name,
            Key=job_application.s3_url
        )
        if 'DeleteMarker' in response:
            job_application.s3_url=None
            job_application.save()
            return "File deleted successfully"
        else:
            return "Failed to delete file from S3"
    except Exception as e:
        return {"error": f"Error deleting file from S3: {e}"}
# import os
# import frappe
# from PyPDF2 import PdfReader
 
# @frappe.whitelist()
# def fetch_and_open_file(docname):
#     # Get the document
#     doc = frappe.get_doc("Test Resume Upload", docname)
    
#     # Get the file details from the File doctype
#     file_doc = frappe.get_doc("File", {"attached_to_name": docname, "attached_to_doctype": "Test Resume Upload"})
    
#     # Check if file_url is available
#     file_url = file_doc.file_url
#     if not file_url:
#         frappe.throw("No file attached to the document.")
    
#     site_path = frappe.utils.get_site_path()
#     if not file_doc.is_private:
#         full_file_path = site_path + '/public' + file_url
#     else:
#         full_file_path = site_path + file_url
 
#     # Ensure the file exists
#     if not os.path.exists(full_file_path):
#         frappe.throw(f"The file at path {full_file_path} does not exist.")
    
#     # Open and read the PDF file
#     with open(full_file_path, 'rb') as file:
#         reader = PdfReader(file)
#         text = ""
#         for page in reader.pages:
#             text += page.extract_text()
    
#     # Now you have the text content of the PDF, you can process it further
#     # For demonstration, let's just print it
#     print(text)
    
#     return text


# @frappe.whitelist()
# def store_rsp_in_s3_from_html(japp_id=None,file=None):
#     s3_doc=frappe.get_doc("S3 360 Dev Test")
#     # Configure boto3 client
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=s3_doc.access_key,
#         aws_secret_access_key=s3_doc.secret_key,
#         region_name=s3_doc.region_name,
#     )

#     # file_link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Recurring%20Service%20Pricing&name={rsp_id}&format=Recurring%20Service%20Pricing%20default&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{rsp_id}.pdf"

#     # Fetch file content from link
#     file_content = file.read()
#     current_datetime = datetime.datetime.now()
#     formatted_datetime = current_datetime.strftime("%Y%m%d_%H_%M")

#     if file_content:
#         # Bucket name and file name
#         bucket_name = s3_doc.bucket
#         folder_name = f'360ITHUB/HR/Recruitment'
#         file_name = f'{str(japp_id)+"_"+formatted_datetime}.pdf'
#         # print(file_content)
#         # Upload file to S3
        
#         try:
#             response = s3_client.put_object(Bucket=bucket_name, Key=f"{folder_name}/{file_name}", Body=file_content)
#             print(response)
#             # print(response.json())
#             if response['ResponseMetadata']['HTTPStatusCode'] == 200:
#                 return "File uploaded successfully"
#             else:
#                 return f"Failed to upload file to S3: {response['ResponseMetadata']['HTTPStatusCode']}"
#         except Exception as e:
#             # print(e)
#             return {"error":f"Error uploading file to S3: {e}","file_content":str(file_content)}
#     else:
#         return f"Failed to fetch file from link."



