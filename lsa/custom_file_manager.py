import frappe,requests,boto3,os,re,socket
import datetime,time
import mimetypes
from frappe.model.document import Document
import frappe
from frappe import _
from werkzeug.utils import secure_filename
from frappe.exceptions import TimestampMismatchError
import random
import string
import filetype
import base64
import magic,json
import traceback


def get_base_directory():
    # Get the local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Define local and production base directories
    test_base_dir = "Test_ERP_LSAOFFICE_S3"
    production_base_dir = "ERP_LSAOFFICE_S3"
    
    # Determine if the IP address is local
    if local_ip.startswith('127.') or local_ip.startswith('10.') or local_ip.startswith('192.168.') or local_ip.startswith('172.16.'):
        return test_base_dir
    else:
        return production_base_dir

path_map={
            "Lead":("Core","/Lead/{name}/Signed_Copy/"),
            "Customer":("Core","/Customer/{name}/"),
            
            "Assessee":("Custom","/Customer/{customer_id}/Assessee/{name}/"),

            "IT Assessee File":("Custom","/Customer/{customer_id}/Assessee/{pan}/Files/ITR/{name}/"),
            "IT Assessee Filing Data":("Custom","/Customer/{customer_id}/Assessee/{pan}/Files/ITR/{it_assessee_file}/{ay}/"),

            "Gstfile":("Custom","/Customer/{customer_id}/Assessee/{pan}/Files/GST/{name}/"),

            "Sales Order":("Core","/Customer/{customer}/Accounts/Signed_Copy/SO_{name}_"),
            "Recurring Service Pricing":("Custom","/Customer/{customer_id}/Accounts/RSP/{name}/"), 


            "Expense Claim":("Core","/Employee/{employee}/Expense_Claim/{name}/"),
            
          }

def store_in_s3_cloud(doc, method):
    
    if doc.attached_to_doctype in path_map:
        if doc.attached_to_field=="image":
            frappe.log_error("Cannot Upload unremovable attachment from the Doctype like Profile Picture etc",f"Failed to upload file to S3: {doc.attached_to_doctype}, {doc.attached_to_doc_name}, {doc.attached_to_doctype_field}")
            return{"status": False, "msg": "Cannot Upload unremovable attachment from the Doctype like Profile Picture etc"}
        
        if frappe.db.exists(doc.attached_to_doctype,doc.attached_to_name):
            attached_to_doc = frappe.get_doc(doc.attached_to_doctype, doc.attached_to_name)
            
            if path_map[doc.attached_to_doctype][0]=="Custom":
                attached_to_doctype_structure = frappe.get_doc("DocType",doc.attached_to_doctype)
                field_names = [field.fieldname for field in attached_to_doctype_structure.fields]
                if ("file_name" not in field_names or "file_type" not in field_names or "attachment_notes" not in field_names):
                    frappe.throw(f"You have configured {doc.attached_to_doctype} for cloud storage but it is missing fields File Name and File Type")

                if not(attached_to_doc.file_name and attached_to_doc.file_type):
                    frappe.throw(f"You need to set File Name and File Type fields before attaching document to {doc.attached_to_doctype}")
            else:
                custom_fields = frappe.get_all("Custom Field", filters={"dt": doc.attached_to_doctype}, fields=["fieldname"])
                custom_field_names = [field['fieldname'] for field in custom_fields]
                if ("custom_file_name" not in custom_field_names or "custom_file_type" not in custom_field_names or "custom_attachment_notes" not in custom_field_names):
                    frappe.throw(f"You have configured {doc.attached_to_doctype} for cloud storage but it is missing fields File Name and File Type")

                if not(attached_to_doc.custom_file_type and attached_to_doc.custom_file_name):
                    frappe.throw(f"You need to set Custom File Name and Custom File Type fields before attaching document to {doc.attached_to_doctype}")

        frappe.enqueue(
            'lsa.custom_file_manager.delayed_store_in_s3_cloud',
            queue='default',  # Specify the queue, default is 'default'
            timeout=30,  # Timeout in seconds
            doc_name=doc.name,  # Arguments to the function
        )

def delayed_store_in_s3_cloud(doc_name, retries=3, backoff_factor=1):

    doc = frappe.get_doc("File", doc_name)
    
    attached_to_doctype = doc.attached_to_doctype
    attached_to_doc_name = doc.attached_to_name
    attached_to_doctype_field = doc.attached_to_field
    file_url = doc.file_url

    attached_to_doc = frappe.get_doc(attached_to_doctype, attached_to_doc_name)

    local_file_resp = get_file_from_link(file_url, doc.is_private)
    local_file_content = local_file_resp["file_content"]
    if not local_file_content:
        return {"status": False, "msg": "Failed to fetch file from link."}
    if attached_to_doctype_field=="name":
        frappe.log_error("Cannot Upload unremovable attachment from the Doctype like Profile Picture etc",f"Failed to upload file to S3: {attached_to_doctype}, {attached_to_doc_name}, {attached_to_doctype_field}")
        return{"status": False, "msg": "Cannot Upload unremovable attachment from the Doctype like Profile Picture etc"}
    
    file_size = local_file_resp["file_size"]
    file_mime_type = local_file_resp["mime_type"]

    formatted_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    base_dir=get_base_directory()
    s3_file_path, s3_file_name = generate_dynamic_path(base_dir, path_map, attached_to_doc, attached_to_doctype_field, file_mime_type, formatted_datetime)
    # s3_file_path=f"{s3_folder_name}/{s3_file_name}"
    
    
    s3cloud_new_doc = frappe.new_doc('S3 Cloud Documents')
    s3cloud_new_doc.doctype_name = attached_to_doctype
    s3cloud_new_doc.doctype_id = attached_to_doc_name
    s3cloud_new_doc.doctype_document_subtype = attached_to_doctype_field
    s3cloud_new_doc.s3_filename = s3_file_name
    s3cloud_new_doc.s3_filepath = s3_file_path
    s3cloud_new_doc.s3_filesize = file_size
    s3cloud_new_doc.s3_file_mime_type = file_mime_type
    s3cloud_new_doc.uploaded_by = frappe.session.user
    s3cloud_new_doc.file_ref=doc.name

    if path_map[doc.attached_to_doctype][0]=="Custom":
        s3cloud_new_doc.file_name=attached_to_doc.file_name
        s3cloud_new_doc.file_type=attached_to_doc.file_type
        s3cloud_new_doc.notes=attached_to_doc.attachment_notes
    else:
        s3cloud_new_doc.file_name=attached_to_doc.custom_file_name
        s3cloud_new_doc.file_type=attached_to_doc.custom_file_type
        s3cloud_new_doc.notes=attached_to_doc.custom_attachment_notes
    s3cloud_new_doc.insert()
    file_uploaded=False
    local_file_deleted=False
    attached_to_doc_updated=False
    attempt = 0
    if (file_size/1024)>30:
        frappe.log_error(f"Can't upload attachent of {attached_to_doc.doctype} {attached_to_doc.name} to s3", \
                         f"Can't upload attachment of {attached_to_doc.doctype} {attached_to_doc.name} to s3 as size limit exceeded {file_size}kb, S3 Cloud Documents Ref: {doc_name}, File Ref: {doc.name}" )
        s3cloud_new_doc.notes=f"Can't upload attachment of {attached_to_doc.doctype} {attached_to_doc.name} to s3 as size limit exceeded {file_size}kb, S3 Cloud Documents Ref: {doc_name}, File Ref: {doc.name}"
        s3cloud_new_doc.save()
        return {"status": False, "message": f"Can't upload attachent of {attached_to_doc.doctype} {attached_to_doc.name} to s3 due to file size limit exceeded"}
    while attempt < retries:
        try:
            if not file_uploaded:
                response = store_in_s3(attached_to_doc, attached_to_doctype_field, s3_file_name,s3_file_path,local_file_content)
                if not response["status"]:
                    frappe.log_error(f"Failed to upload file to S3",f"Failed to upload file to S3: {response['msg']},{response['error']}")
                else:
                    file_uploaded=True
                    s3cloud_new_doc.uploaded_to_s3=1
                    
                
            if not local_file_deleted and file_uploaded:
                try:
                    doc.delete()
                    local_file_deleted=True
                    s3cloud_new_doc.deleted_from_local=1
                    s3cloud_new_doc.file_ref=None
                except Exception as e:
                    frappe.log_error(f"Error deleting local file", f"Error deleting local file: {str(e)}", )
                    # return {"status": False, "message": f"Error deleting local file {response['file_url']}"}
            if not attached_to_doc_updated and local_file_deleted and file_uploaded:
                try:
                    attached_to_doc.reload()
                    attached_to_doc.set(attached_to_doctype_field, None)
                    if path_map[doc.attached_to_doctype][0]=="Custom":
                        attached_to_doc.file_name=None
                        attached_to_doc.file_type=None
                        attached_to_doc.attachment_notes=None
                        

                    else:
                        attached_to_doc.custom_file_name=None
                        attached_to_doc.custom_file_type=None
                        attached_to_doc.custom_attachment_notes=None
                    attached_to_doc.save()
                    attached_to_doc_updated=True
                    s3cloud_new_doc.removed_reference_from_attached_doc=1
                    s3cloud_new_doc.file_ref=None
                except Exception as e2:
                    frappe.log_error(f"Error updating attached document", f"Error updating attached document in doc {attached_to_doctype}: {str(e2)}", )
                    
            s3cloud_new_doc.save()
            frappe.db.commit()
            if attached_to_doc_updated and local_file_deleted and file_uploaded:
                return {"status": True, "message": "File processed successfully"}

            

        except frappe.exceptions.TimestampMismatchError:
            # Retry on TimestampMismatchError
            attempt += 1
            wait_time = backoff_factor * (2 ** (attempt - 1))  # Exponential backoff
            frappe.log_error(f"Timestamp mismatch for document: {doc_name}", f"Timestamp mismatch for document: {doc_name}. Retrying {attempt}/{retries} after {wait_time} seconds. Summary: attached_to_doc_updated={attached_to_doc_updated}, local_file_deleted={local_file_deleted}, file_uploaded={file_uploaded}", )
            time.sleep(wait_time)  # Wait before retrying

        except Exception as e:
            frappe.log_error(f"Error in delayed_store_in_s3_cloud for doc_name {doc_name}", f"Error in delayed_store_in_s3_cloud for doc_name {doc_name}: {str(e)} Summary: attached_to_doc_updated={attached_to_doc_updated}, local_file_deleted={local_file_deleted}, file_uploaded={file_uploaded}", )


    # If all retries failed
    frappe.log_error(f"Failed to process file after {retries} attempts", f"Failed to process file after {retries} attempts: {doc_name} Summary: attached_to_doc_updated={attached_to_doc_updated}, local_file_deleted={local_file_deleted}, file_uploaded={file_uploaded}", )
    return {"status": False, "message": "Failed to process file after multiple attempts"}


@frappe.whitelist()
def store_in_s3(attached_to_doc, attached_to_doctype_field, file_name,s3_file_path,local_file_content):


    s3_doc = frappe.get_doc("S3 360 Dev Test")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_doc.access_key,
        aws_secret_access_key=s3_doc.secret_key,
        region_name=s3_doc.region_name,
    )
    bucket_name = s3_doc.bucket
    
    try:
        response = s3_client.put_object(Bucket=bucket_name, Key=s3_file_path, Body=local_file_content)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            try:
                s3_client.head_object(Bucket=bucket_name, Key=s3_file_path)
                return {"status": True,
                        "msg": "File Uploaded Successfully",
                        }
            except Exception as er1:
                return {"status": False, "msg": "Verification of the file upload Failed", "error": str(er1)}
        else:
            return {"status": False, "msg": f"Failed to upload file to S3: {response['ResponseMetadata']['HTTPStatusCode']}"}
    except Exception as e:
        return {"status": False, "msg": f"Error uploading file to S3: {e}", "file_content": str(local_file_content)}
    
   

def generate_dynamic_path(base_dir, path_map, attached_to_doc, attached_to_doctype_field, file_mime_type, formatted_datetime):
    if attached_to_doc.doctype in path_map:
        folder_name = base_dir + path_map[attached_to_doc.doctype][1]
        fields = re.findall(r'\{(\w+)\}', folder_name)
        for field in fields:
            field_expression = '{' + str(field) + '}'
            folder_name = folder_name.replace(field_expression, str(getattr(attached_to_doc, field)))
        
        try:
            file_name_prefix= "_".join([fnw.lower() for fnw in attached_to_doc.file_type.split(" ")])
        except:
            file_name_prefix= "_".join([fnw.lower() for fnw in attached_to_doc.custom_file_type.split(" ")])

        file_name_suffix = f"{file_name_prefix}_{formatted_datetime}.{file_mime_type.split('/')[1]}"
        file_path = folder_name+file_name_suffix
        file_name = file_path.split("/")[-1]
        return file_path, file_name

def get_file_from_link(file_url, is_private):
    try:
        site_path = frappe.utils.get_site_path()
        if not is_private:
            full_file_path = os.path.join(site_path, 'public', file_url.lstrip('/'))
        else:
            full_file_path = os.path.join(site_path, file_url.lstrip('/'))

        if not os.path.exists(full_file_path):
            frappe.throw(f"The file at path {full_file_path} does not exist.")

        file_size = os.path.getsize(full_file_path)
        file_size = file_size / 1024
        mime_type, _ = mimetypes.guess_type(full_file_path)

        with open(full_file_path, 'rb') as file:
            file_content = file.read()

        return {
            'file_content': file_content,
            'file_size': file_size,
            'mime_type': mime_type
        }
    except Exception as e:
        frappe.log_error("Error in geting file from URL",f"Error fetching file from link: {e}")
        return None

@frappe.whitelist()
def generate_presigned_url(file_name):
    s3_doc = frappe.get_doc("S3 360 Dev Test")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_doc.access_key,
        aws_secret_access_key=s3_doc.secret_key,
        region_name=s3_doc.region_name,
    )

    bucket_name = s3_doc.bucket

    try:
        presigned_url = s3_client.generate_presigned_url('get_object',
                                                          Params={'Bucket': bucket_name, 'Key': file_name},
                                                          ExpiresIn=3600)
        return presigned_url
    except Exception as e:
        frappe.throw(f'Failed to generate presigned URL: {e}')




@frappe.whitelist()
def delete_s3_document(docname):
    s3_doc = frappe.get_doc("S3 360 Dev Test")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_doc.access_key,
        aws_secret_access_key=s3_doc.secret_key,
        region_name=s3_doc.region_name,
    )

    bucket_name = s3_doc.bucket


    s3_file_doc = frappe.get_doc("S3 Cloud Documents", docname)
    s3_filepath = s3_file_doc.s3_filepath

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=s3_filepath)
        frappe.delete_doc("S3 Cloud Documents", docname)
        return True
    except Exception as e:
        frappe.throw(f'Failed to delete S3 document: {e}')
        return False




@frappe.whitelist()
def get_s3_documents(doctype_name, doctype_id):
    # Fetch records from S3 Cloud Documents doctype based on doctype_name and doctype_id
    s3_docs = frappe.get_all(
        "S3 Cloud Documents",
        filters={
            "doctype_name": doctype_name,
            "doctype_id": doctype_id
        },
        fields=["name", "docname", "s3_filename", "s3_filepath", "s3_filesize", "s3_file_mime_type","file_type","file_name", "uploaded_by", "creation"]
    )

    return s3_docs


@frappe.whitelist()
def update_document_fields(doc_type, docname, file_type, file_type_value, file_name, file_name_value, attachment_notes, attachment_notes_value=None):
    try:
        # Fetch the document by type and name
        doc = frappe.get_doc(doc_type, docname)
        
        # Update the fields with the provided values
        setattr(doc, file_type, file_type_value)
        setattr(doc, file_name, file_name_value)
        setattr(doc, attachment_notes, attachment_notes_value)
        
        # Save the document
        doc.save()
        
        # Commit the changes to the database
        frappe.db.commit()
        
        # Optionally, you can return some success message or data
        return {"status":True,"msg": "Document fields updated successfully."}
    except Exception as e:
        return {"status":False,"msg": "Failed to updated document fields."}


################################### App S3 with multi files ####################################################################

@frappe.whitelist()
def s3_file_upload_for_app_muliple(doctype,file_dict,docname=None):
    count = 1
    success_count = 0
    file_status = {"success":[], "failed":[]}


    try:
        file_dict_converted = json.loads(file_dict)  # Parse the JSON string into a Python object
        # frappe.log_error(f"Post request areguments", f"post string: {file_dict} type{type(file_dict)},\n converted json: {file_dict_converted} type{type(file_dict_converted)}," )
    except Exception as e:
        return {"status": False, "msg": f"Error parsing file_dict: {str(e)}"}

    s3_file_doc_ref = []
    for file in file_dict_converted:

        file_name = file["file_name"]
        file_type = file["file_type"]
        file_note = file["file_note"]


        if doctype not in path_map:
            return {"status":False,"msg": f"{doctype} is not configured for file upload"}
        
        attached_to_doctype = doctype
        attached_to_doc_name = None
        attached_to_doc = None
        if docname:
            attached_to_doc_name = docname
            attached_to_doc = frappe.get_doc(attached_to_doctype, attached_to_doc_name)
        
        # frappe.log_error(f"Post request iteration {count}", f"file_name: {file_name} file_type{file_type}, file_note: {file_note}" )
        file_content = frappe.request.files[f'file{count}'].read()
        # if file_content:
        #     frappe.log_error(f"Post request iteration {count}", f"File Content present" )
        
        if not (file_content and file_name and file_type):

            return {"status": False, "msg": "File content or File Type or File Name not found"}
        
        file_sepcs = get_file_mime_size(file_content)

        file_size = file_sepcs["file_size"]
        file_mime_type = file_sepcs["mime_type"]

        formatted_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        base_dir=get_base_directory()
        s3_file_path, s3_file_name = generate_dynamic_path_from_app(base_dir, path_map, file_mime_type,file_type, formatted_datetime,attached_to_doctype ,attached_to_doc )
        # s3_file_path=f"{s3_folder_name}/{s3_file_name}"
        
        
        s3cloud_new_doc = frappe.new_doc('S3 Cloud Documents')
        s3cloud_new_doc.doctype_name = attached_to_doctype
        s3cloud_new_doc.doctype_id = attached_to_doc_name
        # s3cloud_new_doc.doctype_document_subtype = attached_to_doctype_field
        s3cloud_new_doc.s3_filepath = s3_file_path
        s3cloud_new_doc.s3_filename = s3_file_name
        s3cloud_new_doc.s3_filesize = file_size
        s3cloud_new_doc.s3_file_mime_type = file_mime_type
        s3cloud_new_doc.uploaded_by = frappe.session.user
        # s3cloud_new_doc.file_ref=doc.name

        
        s3cloud_new_doc.file_name=file_name
        s3cloud_new_doc.file_type=file_type
        s3cloud_new_doc.notes=file_note

        
        
        s3cloud_new_doc.insert()
        file_uploaded=False
        attempt = 0
        retries=3
        backoff_factor=1
        success_upload=False
        while attempt < retries and not success_upload:
            try:
                if not file_uploaded:
                    response = store_in_s3_from_app(s3_file_path,file_content)
                    if not response["status"]:
                        frappe.log_error(f"Failed to upload file to S3",f"Failed to upload file to S3: {response['msg']},{response['error']}")
                    else:
                        file_uploaded=True
                        s3cloud_new_doc.uploaded_to_s3=1
                        s3cloud_new_doc.save()
                        s3cloud_new_doc.reload()
                        frappe.db.commit()
                        success_count+=1
                        success_upload=True
                        file_status["success"]+=[file]
                        s3_file_doc_ref += [s3cloud_new_doc.name]
                        break
                        

                        
                        
            except frappe.exceptions.TimestampMismatchError:
                # Retry on TimestampMismatchError
                attempt += 1
                wait_time = backoff_factor * (2 ** (attempt - 1))  # Exponential backoff
                frappe.log_error(f"Timestamp mismatch for document: {s3cloud_new_doc.name}", f"Timestamp mismatch for document: {attached_to_doc_name}. Retrying {attempt}/{retries} after {wait_time} seconds. Summary: file_uploaded={file_uploaded}", )
                time.sleep(wait_time)  # Wait before retrying

            except Exception as e:
                frappe.log_error(f"Error in delayed_store_in_s3_cloud for doc_name {s3cloud_new_doc.name}", f"Error in delayed_store_in_s3_cloud for doc_name {s3cloud_new_doc.name}: {str(e)} Summary:  file_uploaded={file_uploaded}", )

        # If all retries failed
        if success_upload==False:
            frappe.log_error(f"Failed to process file after {retries} attempts", f"Failed to process file after {retries} attempts: {s3cloud_new_doc.name} Summary:  file_uploaded={file_uploaded}", )
            file_status["failed"]+=[file]
        count+=1
        
    return {"status":True,"msg":f"{success_count} Files Uploaded Successfully","s3_file_doc_ref":s3_file_doc_ref,"file_upload_status":file_status,"file_dict":file_dict}



######################################  App S3 with single file ####################################################################



@frappe.whitelist()
def s3_file_upload_for_app(doctype,file_name,file_type,file_note,docname=None):


    if doctype not in path_map:
        return {"status":False,"msg": f"{doctype} is not configured for file upload"}
    
    # try:
    #     # If file_array is a string, convert it into a dictionary (JSON parsing)
    #     if isinstance(file_details, str):
    #         file_details = json.loads(file_details)
    # except json.JSONDecodeError as e:
    #     return {"status": False, "msg": f"Invalid JSON format in file_array: {str(e)}"}

    
    
        
    attached_to_doctype = doctype
    attached_to_doc_name = None
    attached_to_doc = None
    if docname:
        attached_to_doc_name = docname
        attached_to_doc = frappe.get_doc(attached_to_doctype, attached_to_doc_name)

    # for file in file_array:
        
    # file_content = file["file_content"]
    
    # If the file is uploaded through Postman (multipart/form-data)
    file_content = frappe.request.files[f'file'].read()

    # if isinstance(file_content, str) and file_content.startswith("data:"):
    #     # This is a Base64 encoded string (e.g., 'data:image/png;base64,...')
    #     try:
    #         # Remove the base64 prefix (if present) and decode
    #         file_content = file_content.split(",")[1]
    #         file_content = base64.b64decode(file_content)
    #     except Exception as e:
    #         frappe.throw(f"Failed to decode filedata: {str(e)}")
    # else:
    #     frappe.throw("Invalid filedata format. Expected Base64 string.")


    # file_name=file_details["file_name"]
    # file_type=file_details["file_type"]
    if not (file_content and file_name and file_type):

        return {"status": False, "msg": "File content or File Type or File Name not found"}
    
    file_sepcs = get_file_mime_size(file_content)

    file_size = file_sepcs["file_size"]
    file_mime_type = file_sepcs["mime_type"]

    formatted_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    base_dir=get_base_directory()
    s3_file_path, s3_file_name = generate_dynamic_path_from_app(base_dir, path_map, file_mime_type,file_type, formatted_datetime,attached_to_doctype ,attached_to_doc )
    # s3_file_path=f"{s3_folder_name}/{s3_file_name}"
    
    
    s3cloud_new_doc = frappe.new_doc('S3 Cloud Documents')
    s3cloud_new_doc.doctype_name = attached_to_doctype
    s3cloud_new_doc.doctype_id = attached_to_doc_name
    # s3cloud_new_doc.doctype_document_subtype = attached_to_doctype_field
    s3cloud_new_doc.s3_filepath = s3_file_path
    s3cloud_new_doc.s3_filename = s3_file_name
    s3cloud_new_doc.s3_filesize = file_size
    s3cloud_new_doc.s3_file_mime_type = file_mime_type
    s3cloud_new_doc.uploaded_by = frappe.session.user
    # s3cloud_new_doc.file_ref=doc.name

    
    s3cloud_new_doc.file_name=file_name
    s3cloud_new_doc.file_type=file_type
    s3cloud_new_doc.notes=file_note

    
    
    s3cloud_new_doc.insert()
    file_uploaded=False
    local_file_deleted=False
    # attached_to_doc_updated=False
    attempt = 0
    # if (file_size/1024)>30:
    #     frappe.log_error(f"Can't upload attachent of {attached_to_doc.doctype} {attached_to_doc.name} to s3", \
    #                     f"Can't upload attachment of {attached_to_doc.doctype} {attached_to_doc.name} to s3 as size limit exceeded {file_size}kb, S3 Cloud Documents Ref: {doc_name}, File Ref: {doc.name}" )
    #     s3cloud_new_doc.notes=f"Can't upload attachment of {attached_to_doc.doctype} {attached_to_doc.name} to s3 as size limit exceeded {file_size}kb, S3 Cloud Documents Ref: {doc_name}, File Ref: {doc.name}"
    #     s3cloud_new_doc.save()
    #     return {"status": False, "message": f"Can't upload attachent of {attached_to_doc.doctype} {attached_to_doc.name} to s3 due to file size limit exceeded"}
    retries=3
    backoff_factor=1
    while attempt < retries :
        try:
            if not file_uploaded:
                response = store_in_s3_from_app(s3_file_path,file_content)
                if not response["status"]:
                    frappe.log_error(f"Failed to upload file to S3",f"Failed to upload file to S3: {response['msg']},{response['error']}")
                else:
                    file_uploaded=True
                    s3cloud_new_doc.uploaded_to_s3=1
                    s3cloud_new_doc.save()
                    s3cloud_new_doc.reload()
                    frappe.db.commit()
                    return {"status":True,"msg":"File Uploaded Successfully","file_id":s3cloud_new_doc.name}
                    
        except frappe.exceptions.TimestampMismatchError:
            # Retry on TimestampMismatchError
            attempt += 1
            wait_time = backoff_factor * (2 ** (attempt - 1))  # Exponential backoff
            frappe.log_error(f"Timestamp mismatch for document: {s3cloud_new_doc.name}", f"Timestamp mismatch for document: {attached_to_doc_name}. Retrying {attempt}/{retries} after {wait_time} seconds. Summary: file_uploaded={file_uploaded}", )
            time.sleep(wait_time)  # Wait before retrying

        except Exception as e:
            frappe.log_error(f"Error in delayed_store_in_s3_cloud for doc_name {s3cloud_new_doc.name}", f"Error in delayed_store_in_s3_cloud for doc_name {s3cloud_new_doc.name}: {str(e)} Summary:  file_uploaded={file_uploaded}", )

    # If all retries failed
    frappe.log_error(f"Failed to process file after {retries} attempts", f"Failed to process file after {retries} attempts: {s3cloud_new_doc.name} Summary:  file_uploaded={file_uploaded}", )
    return {"status": False, "message": "Failed to process file after multiple attempts"}


@frappe.whitelist()
def store_in_s3_from_app(s3_file_path,file_content):


    s3_doc = frappe.get_doc("S3 360 Dev Test")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_doc.access_key,
        aws_secret_access_key=s3_doc.secret_key,
        region_name=s3_doc.region_name,
    )
    bucket_name = s3_doc.bucket
    
    try:
        response = s3_client.put_object(Bucket=bucket_name, Key=s3_file_path, Body=file_content)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            try:
                s3_client.head_object(Bucket=bucket_name, Key=s3_file_path)
                return {"status": True,
                        "msg": "File Uploaded Successfully",
                        }
            except Exception as er1:
                return {"status": False, "msg": "Verification of the file upload Failed", "error": str(er1)}
        else:
            return {"status": False, "msg": f"Failed to upload file to S3: {response['ResponseMetadata']['HTTPStatusCode']}"}
    except Exception as e:
        return {"status": False, "msg": f"Error uploading file to S3: {e}", "file_content": str(file_content)}
    
   

def generate_dynamic_path_from_app(base_dir, path_map, file_mime_type,file_type, formatted_datetime,attached_to_doctype ,attached_to_doc):
    if attached_to_doc and attached_to_doc.doctype in path_map:
        random_str = generate_random_string(3)
        folder_name = base_dir + path_map[attached_to_doc.doctype][1]
        fields = re.findall(r'\{(\w+)\}', folder_name)
        for field in fields:
            field_expression = '{' + str(field) + '}'
            folder_name = folder_name.replace(field_expression, str(getattr(attached_to_doc, field)))
        

        file_name_prefix= "_".join([fnw.lower() for fnw in file_type.split(" ")])

        file_name_suffix = f"{file_name_prefix}_{formatted_datetime}_{random_str}.{file_mime_type.split('/')[1]}"
        file_path = folder_name+file_name_suffix
        file_name = file_path.split("/")[-1]
        return file_path, file_name
    elif not attached_to_doc:
        random_str = generate_random_string(3)

        # folder_name = base_dir + "/"+ attached_to_doctype +"/"+f"{random_str}"
        folder_name = base_dir + "/"+ attached_to_doctype +"/Unassigned"
        
        file_name_prefix= "_".join([fnw.lower() for fnw in file_type.split(" ")])

        file_name_suffix = f"{file_name_prefix}_{formatted_datetime}_{random_str}.{file_mime_type.split('/')[1]}"
        file_path = folder_name+file_name_suffix
        file_name = file_path.split("/")[-1]
        return file_path, file_name
    




def generate_random_string(length=12):
    # Define the character pool (uppercase and lowercase letters)
    characters = string.ascii_letters  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    
    # Generate a random string of the specified length
    random_string = ''.join(random.choice(characters) for _ in range(length))
    
    return random_string




# def get_file_mime_size(file_content):
#     # Decode the base64 string to binary data
#     file_data = base64.b64decode(file_content)
    
#     # Get MIME type using python-magic
#     mime = magic.Magic(mime=True)
#     mime_type = mime.from_buffer(file_data)

#     # Get file size
#     file_size = len(file_data)

#     file_sepcs={}
#     file_sepcs["file_size"]=file_size
#     file_sepcs["mime_type"]=mime_type

#     return file_sepcs
def get_file_mime_size(file_content):
    # Use python-magic to detect MIME type directly from the binary data
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file_content)  # Directly use the binary content

    # Get file size
    size_in_bytes = len(file_content)
    file_size = human_readable_file_size(size_in_bytes)


    return {
        "file_size": file_size,
        "mime_type": mime_type
    }


def human_readable_file_size(size_in_bytes):
        if size_in_bytes < 1024:
            return f"{size_in_bytes} bytes"
        elif size_in_bytes < 1024**2:
            return f"{size_in_bytes / 1024:.1f} kB"
        else:
            return f"{size_in_bytes / 1024**2:.1f} MB"

# def get_file_mime_size(file_content):
#     file_data = base64.b64decode(file_content)
#     mime = magic.Magic(mime=True)
#     mime_type = mime.from_buffer(file_data[:4096])  # Use a larger buffer size

#     if mime_type == "application/octet-stream":
#         mime_type, _ = mimetypes.guess_type("file.name")  # Replace with actual filename if available

#     file_size = len(file_data)
#     return {"file_size": file_size, "mime_type": mime_type}

@frappe.whitelist()
def update_reference_doc_in_attachment(attachment_ids,reference_id):
    try:
        attachment_ids_converted = json.loads(attachment_ids)  # Parse the JSON string into a Python object
        # frappe.log_error(f"Post request areguments", f"post string: {file_dict} type{type(file_dict)},\n converted json: {file_dict_converted} type{type(file_dict_converted)}," )
    except Exception as e:
        return {"status": False, "msg": f"Error parsing attachment_ids: {str(e)}"}
    updation_status = {"success":[],"failed":[]}
    for attachment_id in attachment_ids_converted:
        try:
            attachment_doc = frappe.get_doc("S3 Cloud Documents", attachment_id)
            attachment_doc.doctype_id = reference_id
            
            old_path = attachment_doc.s3_filepath
            old_path_component=old_path.split("/")


            pattern = r'(\d{8}_\d{6})'
            match = re.search(pattern, old_path)
            formatted_datetime=""
            if match:
                formatted_datetime = match.group(1)
            else:
                formatted_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

            attached_to_doc = frappe.get_doc(attachment_doc.doctype_name, reference_id)

            file_path, file_name = generate_dynamic_path_from_app(old_path_component[0], path_map, attachment_doc.s3_file_mime_type,attachment_doc.file_type, formatted_datetime,attachment_doc.doctype_name ,attached_to_doc)

            resp = modify_s3_file_path_and_name( attachment_doc.s3_filepath, file_path)

            if resp["status"]:
                attachment_doc.s3_filepath = file_path
                attachment_doc.s3_filename = file_name
                attachment_doc.save()
                frappe.db.commit()
                updation_status["success"] += [attachment_id]
            else:
                updation_status["failed"] += [attachment_id]
                
            
        except Exception as e:
            updation_status["failed"] += [attachment_id]
            traceback_str = traceback.format_exc()
            frappe.log_error(f"Error updating file path", f"Error updating file path for {attachment_id} for {attachment_doc.doctype_name} doctype reference {reference_id} {attachment_doc.s3_filepath} to {file_path}: {str(e)} {traceback_str}", )
            
    return {"status": True, "msg": "Reference Doc updated","updation_status":updation_status}
    

def modify_s3_file_path_and_name( old_key, new_key):

    s3_doc = frappe.get_doc("S3 360 Dev Test")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_doc.access_key,
        aws_secret_access_key=s3_doc.secret_key,
        region_name=s3_doc.region_name,
    )
    bucket_name = s3_doc.bucket

    try:
        # Step 1: Copy the file to the new path with the new filename
        s3_client.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': old_key},
            Key=new_key
        )
        

        # Step 2: Delete the original file
        s3_client.delete_object(Bucket=bucket_name, Key=old_key)
        return {"status":True,"msg":"File path updated successfully"}

    except Exception as e:
        frappe.log_error(f"Error updating file path in s3", f"Error updating file path in s3 {old_key} to {new_key}: {str(e)}", )
        return{"status":False,"msg":"File path updated failed"}
    
######################################  App S3 with file in base64 ####################################################################

# @frappe.whitelist()
# def s3_file_upload_for_app(doctype,file_array,docname=None):

#     if doctype not in path_map:
#         return {"status":False,"msg": f"{doctype} is not configured for file upload"}
    
#     try:
#         # If file_array is a string, convert it into a dictionary (JSON parsing)
#         if isinstance(file_array, str):
#             file_array = json.loads(file_array)
#     except json.JSONDecodeError as e:
#         return {"status": False, "msg": f"Invalid JSON format in file_array: {str(e)}"}

    
    
        
#     attached_to_doctype = doctype
#     attached_to_doc_name = None
#     attached_to_doc = None
#     if docname:
#         attached_to_doc_name = docname
#         attached_to_doc = frappe.get_doc(attached_to_doctype, attached_to_doc_name)
#     count = 1
#     for file in file_array:
        
#         # file_content = file["file_content"]
        
#         # If the file is uploaded through Postman (multipart/form-data)
#         file_content = frappe.request.files[f'file{count}'].read()
#         file_content = frappe.request.files[f'file{count}'].read()

#         # if isinstance(file_content, str) and file_content.startswith("data:"):
#         #     # This is a Base64 encoded string (e.g., 'data:image/png;base64,...')
#         #     try:
#         #         # Remove the base64 prefix (if present) and decode
#         #         file_content = file_content.split(",")[1]
#         #         file_content = base64.b64decode(file_content)
#         #     except Exception as e:
#         #         frappe.throw(f"Failed to decode filedata: {str(e)}")
#         # else:
#         #     frappe.throw("Invalid filedata format. Expected Base64 string.")


#         file_name=file["file_name"]
#         file_type=file["file_type"]
#         if not (file_content and file_name and file_type):

#             return {"status": False, "msg": "File content or File Type or File Name not found"}
        
#         file_sepcs = get_file_mime_size(file_content)

#         file_size = file_sepcs["file_size"]
#         file_mime_type = file_sepcs["mime_type"]

#         formatted_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
#         base_dir=get_base_directory()
#         s3_file_path, s3_file_name = generate_dynamic_path_from_app(base_dir, path_map, file_mime_type,file_type, formatted_datetime,attached_to_doctype ,attached_to_doc )
#         # s3_file_path=f"{s3_folder_name}/{s3_file_name}"
        
        
#         s3cloud_new_doc = frappe.new_doc('S3 Cloud Documents')
#         s3cloud_new_doc.doctype_name = attached_to_doctype
#         s3cloud_new_doc.doctype_id = attached_to_doc_name
#         # s3cloud_new_doc.doctype_document_subtype = attached_to_doctype_field
#         # s3cloud_new_doc.s3_filename = s3_file_name
#         s3cloud_new_doc.s3_filepath = s3_file_path
#         s3cloud_new_doc.s3_filesize = file_size
#         s3cloud_new_doc.s3_file_mime_type = file_mime_type
#         s3cloud_new_doc.uploaded_by = frappe.session.user
#         # s3cloud_new_doc.file_ref=doc.name

        
#         s3cloud_new_doc.file_name=file["file_name"]
#         s3cloud_new_doc.file_type=file["file_type"]
#         s3cloud_new_doc.notes=file["file_note"]
        
        
#         s3cloud_new_doc.insert()
#         file_uploaded=False
#         local_file_deleted=False
#         # attached_to_doc_updated=False
#         attempt = 0
#         # if (file_size/1024)>30:
#         #     frappe.log_error(f"Can't upload attachent of {attached_to_doc.doctype} {attached_to_doc.name} to s3", \
#         #                     f"Can't upload attachment of {attached_to_doc.doctype} {attached_to_doc.name} to s3 as size limit exceeded {file_size}kb, S3 Cloud Documents Ref: {doc_name}, File Ref: {doc.name}" )
#         #     s3cloud_new_doc.notes=f"Can't upload attachment of {attached_to_doc.doctype} {attached_to_doc.name} to s3 as size limit exceeded {file_size}kb, S3 Cloud Documents Ref: {doc_name}, File Ref: {doc.name}"
#         #     s3cloud_new_doc.save()
#         #     return {"status": False, "message": f"Can't upload attachent of {attached_to_doc.doctype} {attached_to_doc.name} to s3 due to file size limit exceeded"}
#         retries=3
#         backoff_factor=1
#         while attempt < retries :
#             try:
#                 if not file_uploaded:
#                     response = store_in_s3_from_app(s3_file_path,file_content)
#                     if not response["status"]:
#                         frappe.log_error(f"Failed to upload file to S3",f"Failed to upload file to S3: {response['msg']},{response['error']}")
#                     else:
#                         file_uploaded=True
#                         s3cloud_new_doc.uploaded_to_s3=1
#                         s3cloud_new_doc.save()
#                         frappe.db.commit()
                        
#             except frappe.exceptions.TimestampMismatchError:
#                 # Retry on TimestampMismatchError
#                 attempt += 1
#                 wait_time = backoff_factor * (2 ** (attempt - 1))  # Exponential backoff
#                 frappe.log_error(f"Timestamp mismatch for document: {s3cloud_new_doc.name}", f"Timestamp mismatch for document: {attached_to_doc_name}. Retrying {attempt}/{retries} after {wait_time} seconds. Summary: file_uploaded={file_uploaded}", )
#                 time.sleep(wait_time)  # Wait before retrying

#             except Exception as e:
#                 frappe.log_error(f"Error in delayed_store_in_s3_cloud for doc_name {s3cloud_new_doc.name}", f"Error in delayed_store_in_s3_cloud for doc_name {s3cloud_new_doc.name}: {str(e)} Summary:  file_uploaded={file_uploaded}", )

#         count+=1
#         # If all retries failed
#         frappe.log_error(f"Failed to process file after {retries} attempts", f"Failed to process file after {retries} attempts: {s3cloud_new_doc.name} Summary:  file_uploaded={file_uploaded}", )
#         return {"status": False, "message": "Failed to process file after multiple attempts"}


# @frappe.whitelist()
# def store_in_s3_from_app(s3_file_path,file_content):


#     s3_doc = frappe.get_doc("S3 360 Dev Test")
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=s3_doc.access_key,
#         aws_secret_access_key=s3_doc.secret_key,
#         region_name=s3_doc.region_name,
#     )
#     bucket_name = s3_doc.bucket
    
#     try:
#         response = s3_client.put_object(Bucket=bucket_name, Key=s3_file_path, Body=file_content)
#         if response['ResponseMetadata']['HTTPStatusCode'] == 200:
#             try:
#                 s3_client.head_object(Bucket=bucket_name, Key=s3_file_path)
#                 return {"status": True,
#                         "msg": "File Uploaded Successfully",
#                         }
#             except Exception as er1:
#                 return {"status": False, "msg": "Verification of the file upload Failed", "error": str(er1)}
#         else:
#             return {"status": False, "msg": f"Failed to upload file to S3: {response['ResponseMetadata']['HTTPStatusCode']}"}
#     except Exception as e:
#         return {"status": False, "msg": f"Error uploading file to S3: {e}", "file_content": str(file_content)}
    
   

# def generate_dynamic_path_from_app(base_dir, path_map, file_mime_type,file_type, formatted_datetime,attached_to_doctype ,attached_to_doc):
#     if attached_to_doc and attached_to_doc.doctype in path_map:
#         folder_name = base_dir + path_map[attached_to_doc.doctype][1]
#         fields = re.findall(r'\{(\w+)\}', folder_name)
#         for field in fields:
#             field_expression = '{' + str(field) + '}'
#             folder_name = folder_name.replace(field_expression, str(getattr(attached_to_doc, field)))
        

#         file_name_prefix= "_".join([fnw.lower() for fnw in file_type.split(" ")])

#         file_name_suffix = f"{file_name_prefix}_{formatted_datetime}.{file_mime_type.split('/')[1]}"
#         file_path = folder_name+file_name_suffix
#         file_name = file_path.split("/")[-1]
#         return file_path, file_name
#     elif not attached_to_doc:
#         # random_str = generate_random_string(12)

#         # folder_name = base_dir + "/"+ attached_to_doctype +"/"+f"{random_str}"
#         folder_name = base_dir + "/"+ attached_to_doctype +"/Unassigned"
        
#         file_name_prefix= "_".join([fnw.lower() for fnw in file_type.split(" ")])

#         file_name_suffix = f"{file_name_prefix}_{formatted_datetime}.{file_mime_type.split('/')[1]}"
#         file_path = folder_name+file_name_suffix
#         file_name = file_path.split("/")[-1]
#         return file_path, file_name
    




# def generate_random_string(length=12):
#     # Define the character pool (uppercase and lowercase letters)
#     characters = string.ascii_letters  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    
#     # Generate a random string of the specified length
#     random_string = ''.join(random.choice(characters) for _ in range(length))
    
#     return random_string








# # def get_file_mime_size(file_content):
# #     try:
# #         # Get file size
# #         file_size = len(file_content)  # Size in bytes
        
# #         # Get MIME type using filetype library
# #         kind = filetype.guess(file_content)
        
# #         if kind:
# #             mime_type = kind.mime  # Extract MIME type (e.g., 'image/png')
# #         else:
# #             mime_type = "unknown/unknown"  # Fallback if type can't be determined

# #         return {
# #             'file_content': file_content,
# #             'file_size': file_size,  # Size in bytes
# #             'mime_type': mime_type
# #         }
# #     except Exception as e:
# #         frappe.log_error("Error in geting file from URL", f"Error fetching file from link: {e}")
# #         return None



# def get_file_mime_size(file_content):
#     # Decode the base64 string to binary data
#     file_data = base64.b64decode(file_content)
    
#     # Get MIME type using python-magic
#     mime = magic.Magic(mime=True)
#     mime_type = mime.from_buffer(file_data)

#     # Get file size
#     file_size = len(file_data)

#     file_sepcs={}
#     file_sepcs["file_size"]=file_size
#     file_sepcs["mime_type"]=mime_type

    # return file_sepcs



