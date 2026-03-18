#!/usr/bin/env python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

TOKEN_FILE = 'token.json'
CONTAINER_FILE_PATH = '/home/runner/discos_manager.tar'
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

# Create the token file from the GH Secret
with open(TOKEN_FILE, 'w') as tokenfile:
    tokenfile.write(os.environ.get('GOOGLE_DRIVE_TOKEN'))

# Authenticate with the token and eventually update it
creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

# Prepare the files to be uploaded
service = build('drive', 'v3', credentials=creds)
container_media = MediaFileUpload(
    CONTAINER_FILE_PATH,
    mimetype='application/x-tar',
    resumable=True,
    chunksize=64*1024*1024
)
request = service.files().update(
    fileId=os.environ.get('PROVISIONED_CONTAINER_GDRIVE_ID'),
    media_body=container_media,
    fields='id'
)

response = None
while response is None:
    status, response = request.next_chunk()
    if status is not None:
        print(f'Upload progress: {int(status.progress() * 100)}%', flush=True)

# Finally update the token file
with open(TOKEN_FILE, 'w') as tokenfile:
    tokenfile.write(creds.to_json())
