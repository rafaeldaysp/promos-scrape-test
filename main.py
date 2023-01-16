from __future__ import print_function

import os.path
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1S0FRNJoXLwKUbat35EagzmCuTCFdz89OTfNVDBP1Ovk'
SAMPLE_RANGE_NAME = 'Notebooks Amazon!B3:K60'

import requests
from bs4 import BeautifulSoup
import time

import teste4

#url = {'helios': 'https://amzn.to/3H4b3Uz',
    #    'strix': 'https://amzn.to/3QFRzZI',
    #    'nitro_3060_r5': 'https://amzn.to/3w7eJys'}

#notebooks =['helios', 'strix', 'nitro_3060_r5']

from fake_useragent import UserAgent

def criador_de_post(dados, op=0):
    print('Criando o post...')
    print(dados)
    data = {'photo': dados[3],
               'header': dados[5],
               'title': dados[6],
               'description': dados[7],
               'price': dados[1],
               'link': dados[3],
               'comment': dados[8]}
    message = ''
    
    if dados[5] == '-':
        if op == 1:
            message += '⭐️ VOLTOU O ESTOQUE! ⭐️\n\n'
        elif op == 2:
            message += '⭐️ ABAIXOU! ⭐️\n\n'
    else:
        message += '⭐️ ' + dados[5] + ' ⭐️\n\n'
    message += '🔥 ' + dados[6] + ' 🔥' + '\n\n🔴 ' + dados[7] + ' 🔴' + '\n\n💸 R$ ' + dados[1] + ' (Em 10x Sem Juros)' + '\n\n🔗 ' + dados[3] + '\n\n'
    if dados[8] != '-':
        message += '⭐️ ' + dados[8]
    print(dados)
    post = [dados[3], message]
    print(post)
    teste4.send_message(post)
    
    
def scraping(values, notebooks, url, i):
    ua = UserAgent()
    headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
                "Accept-Encoding": "gzip, deflate", 
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
                "Dnt": "1", 
                "User-Agent": str(ua.random), 
            }
    print(str(ua.random))
    try:
        response = requests.get(url[notebooks[i]], headers=headers)
        site = BeautifulSoup(response.text, 'html.parser')
        price = site.find('span', class_='a-price-whole').text + '00'
        availability = site.find('span', class_='a-size-medium a-color-price').text
        
        if 'Não disponível' in availability:
            print(f'{notebooks[i]} não disponível')
            values[i+1][1] = price
            values[i+1][4] = 'Não'
        else:
            print(values[i+1][1])
            try:
                preco_antigo = [float(a) for a in values[i+1][1].split(',')[:-1]][0]
            except:
                preco_antigo = 0
            preco_atual = [float(a) for a in price.split(',')[:-1]][0]
            referencia = float(values[i+1][9])/1000
        
            if str(values[i+1][4]) == 'Não' and preco_atual < referencia:
                values[i+1][1] = price
                criador_de_post(values[i+1], 1) # volta de estoque
            elif preco_atual < preco_antigo < referencia:
                values[i+1][1] = price
                criador_de_post(values[i+1], 2) # abaixou
            elif preco_atual < referencia < preco_antigo:
                values[i+1][1] = price
                criador_de_post(values[i+1]) # preço bom
            values[i+1][1] = price
            values[i+1][4] = 'Sim'
    except Exception as e:
        print('Acesso bloqueado pela Amazon em ' + notebooks[i])
    return values
    


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    
    while True:
        notebooks = []
        url = {}
        row = ''
        try:
            service = build('sheets', 'v4', credentials=creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values', [])
            
            for i in range (1, len(values)):
                try:
                    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME).execute()
                    values = result.get('values', [])
                    notebook = values[i][0]
                    notebooks.append(notebook)
                    url[notebook] = values[i][3]
                    values = scraping(values, notebooks, url, i - 1)
                    print(f'{values[i][0]}: {values[i][1]}')
                    row = 'Notebooks Amazon!B' + str(3+i) + ':F' + str(3+i)
                    sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                            range=row, valueInputOption="USER_ENTERED",
                                            body={'values': [values[i][:-5]]}).execute()
                except Exception as e:
                    print(e)
            
        except HttpError as err:
            print(err)
        
        print('Timeout...')
        time.sleep(1)
        


if __name__ == '__main__':
    
    main()