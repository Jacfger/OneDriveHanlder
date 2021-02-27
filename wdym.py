'''
    What do you mean it doesn't fucking work?
'''
import os
import requests
import json
import msal

import pickle

with open('credentials.dict', 'rb') as f:
    _dict = pickle.load(f)

AUTHORITY_URL = 'https://login.microsoftonline.com/{}'.format(_dict['tenant_id'])
RESOURCE_URL = 'https://graph.microsoft.com'
API_VERSION = 'v1.0'
SCOPES = ['Sites.ReadWrite.All', 'Files.ReadWrite.All']  # Add other scopes/permissions as needed.

cognos_to_onedrive = msal.PublicClientApplication(_dict['client_id'], authority=AUTHORITY_URL)
token = cognos_to_onedrive.acquire_token_by_username_password(_dict['username'], _dict['password'], SCOPES)
# headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
onedrive_destination = '{}/{}/me/drive/root:/'.format(RESOURCE_URL, API_VERSION)


def upload(files):
    for _file in files:
        file_size = os.stat(_file).st_size
        file_data = open(_file, 'rb')
        print(_file)
        # _, file_name = os.path.split(_file)
        file_name = _file
        if file_size < 4100000:
            # Perform is simple upload to the API
            headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
            r = requests.put(onedrive_destination+"/"+file_name+":/content", data=file_data, headers=headers)
        else:
            # Creating an upload session
            headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
            upload_session = requests.post(onedrive_destination+"/"+file_name+":/createUploadSession", headers=headers).json()

            with open(_file, 'rb') as f:
                total_file_size = os.path.getsize(_file)
                chunk_size = 62914560
                chunk_number = total_file_size//chunk_size
                chunk_leftover = total_file_size - chunk_size * chunk_number
                i = 0
                while True:
                    print('    {}/{}'.format(chunk_size * i, total_file_size))
                    chunk_data = f.read(chunk_size)
                    start_index = i*chunk_size
                    end_index = start_index + chunk_size
                    # If end of file, break
                    if not chunk_data:
                        break
                    if i == chunk_number:
                        end_index = start_index + chunk_leftover
                    # Setting the header with the appropriate chunk data location in the file
                    headers = {'Content-Length': '{}'.format(chunk_size), 'Content-Range': 'bytes {}-{}/{}'.format(start_index, end_index-1, total_file_size)}
                    # Upload one chunk at a time
                    chunk_data_upload = requests.put(upload_session['uploadUrl'], data=chunk_data, headers=headers)
                    i = i + 1
        file_data.close()


def download(files):
    headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
    for _file in files:
        url = os.path.join(onedrive_destination, _file)
        url += ':/content'
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print('Error: ' + str(r.status_code))
        _, file_name = os.path.split(_file)
        with open(file_name, 'wb') as f:
            f.write(r.content)

import argparse
import glob

parser = argparse.ArgumentParser()
parser.add_argument('-u')
parser.add_argument('-d')
parser.add_argument('-f', nargs='+')
parser.add_argument('-g')
args = parser.parse_args()

if args.f:
    files = args.f
elif args.g:
    files = glob.glob(args.g)

if args.u:
    upload(args.f)

if args.d:
    download(args.f)
