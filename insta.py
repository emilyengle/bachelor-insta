from __future__ import print_function
import json
import pickle
import os.path
import requests
from datetime import date
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# TO USE - fill in below with the correct spreadsheet ID
SPREADSHEET_ID = '1SyyRQQoWYEO74uSPehFiURmuR7wrWmlzaIBMjp6VY6c'

def get_creds():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_urls(ss):
    # TO USE - replace "Sheet1" below with the name of the specific sheet in
    # the given spreadsheet
    range = 'Sheet1!B2:AG2'
    raw_data = ss.values().get(spreadsheetId=SPREADSHEET_ID, range=range).execute()
    values = raw_data.get('values', [[]])
    return values[0]


def get_follower_counts(urls):
    count = []
    search_string = '"edge_followed_by":{"count":'
    for url in urls:
        response = requests.get(url)
        index1 = response.text.find(search_string) + len(search_string)
        index2 = response.text.find('}', index1)
        follower_count = response.text[index1:index2]
        count.append(follower_count)
    return count


def get_row(follower_counts):
    today = date.today().strftime('%m/%d/%Y')
    row = [today]
    row.extend(follower_counts)
    return row


def main():
    # Authenticate with Google Sheets API and set up connection to their service
    creds = get_creds()
    service = build('sheets', 'v4', credentials=creds)
    spreadsheets = service.spreadsheets()

    # Fetch the instagram handles to check from the spreadsheet
    urls = get_urls(spreadsheets)
    # Get the follower count for each handle
    follower_counts = get_follower_counts(urls)

    # Combine all of the data into a row to write to the spreadsheet
    row = get_row(follower_counts)
    body = {
        'values': [row]
    }

    # Write the data to the spreadsheet
    # TO USE - replace "Sheet1" below with the name of the specific subsheet
    # within the bigger spreadsheet
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID, range='Sheet1',
        valueInputOption='USER_ENTERED', body=body).execute()


if __name__ == '__main__':
    main()
