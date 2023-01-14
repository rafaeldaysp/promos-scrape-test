import requests

def send_message(post):
    token = '5955496494:AAGfKkWJSIIbd2HO5l9sH4wa3FXSSUj-Xu4'
    chat_id = '-1001409905513'
    
    print('Enviando mensagem...')
    try:
        data = {"chat_id": chat_id, 
                "photo": post[0],
                "caption": post[1]}
        url = "https://api.telegram.org/bot5955496494:AAGfKkWJSIIbd2HO5l9sH4wa3FXSSUj-Xu4/sendPhoto".format(token)
        requests.post(url, data)
    except Exception as e:
        print("Erro no sendMessage:", e)