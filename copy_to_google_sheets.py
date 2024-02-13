import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Google Sheets credentials and ID
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(eval("json.loads('" + os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY') + "')"), scope)
client = gspread.authorize(creds)
sheet_id = os.getenv('GOOGLE_SHEET_ID')

# Read CSV and remove duplicates based on link_visit
df = pd.read_csv('data/overall.csv')
df = df.drop_duplicates(subset=['link_visit'])

# Connect to Google Sheets and paste data
sheet = client.open_by_key(sheet_id).sheet1
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())
