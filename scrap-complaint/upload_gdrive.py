from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
def upload_to_drive(file_path, folder_id):
    try:
        gauth = GoogleAuth()
        gauth.settings['client_config_file'] = r""
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
        file_name = os.path.basename(file_path)
        
        # Search for an existing file in the folder
        query = f"title = '{file_name}' and '{folder_id}' in parents and trashed = false"
        file_list = drive.ListFile({'q': query}).GetList()

        if file_list:
            # If file exists, overwrite it (update content)
            file_drive = file_list[0]  # Get the first matching file
            print(f"Overwriting existing file: {file_drive['title']} (ID: {file_drive['id']})")
        else:
            # If file doesn't exist, create a new one
            file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
            print(f"Uploading new file: {file_name}")

        # Set new content and upload (overwrite)
        file_drive.SetContentFile(file_path)
        file_drive.Upload()

    except Exception as e:
        print(f"Error uploading file: {e}")
