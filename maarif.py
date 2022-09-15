from bs4 import BeautifulSoup
from win10toast import ToastNotifier
import requests, os, time, sys, json
from infi.systray import SysTrayIcon

toast = ToastNotifier()

session = requests.Session()
session.verify = os.path.abspath('consolidate.pem')

with open('request_data.json', 'r') as file:
    request_data = json.loads(file.read())    

cookies, headers, data = [v[1] for v in request_data.items()]

def notify(info):
    try:
        session.post('https://dashboard.maarif.com.sa/Account/LoginWeb', headers=headers, cookies=cookies, data=data)    
        response = session.get('https://smartems-dash.maarif.com.sa/home.work/#!#rel')
        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
        exams = soup.find_all('div', {"class": "ExamItemContainer"})

        if len(exams) > 0:
            toast.show_toast(f"You have {len(exams)} exams", info, duration=5, icon_path="favicon.ico")
        else:
            toast.show_toast(f"You have no exams", info, duration=5, icon_path="favicon.ico")
        
        return True
    except Exception as e:
        with open("log.txt", "a") as file:
            file.write(f'\nERROR: Notify with info "{info}":\nTraceback:' + str(e))
        return False

def on_quit_callback(systray):    
    toast.show_toast("Exitting in 5 seconds", "Manual tray exit", duration=5, icon_path="favicon.ico")
    time.sleep(5)
    sys.exit()

def manual(systray):
    try:
        notify("Manual tray scan")
    except Exception as e:
        with open("log.txt", "a") as file:            
            file.write(f'\nERROR: Manual tray scan:\nTraceback:' + str(e))
        pass

menu_options = (("Manual Scan", None, manual), )
systray = SysTrayIcon("logo.ico", "Maarif Exam Informant", menu_options, on_quit=on_quit_callback)
systray.start()

toast.show_toast("Started maarif notifier", "​On startup notification", duration=5, icon_path="favicon.ico")

time.sleep(1)
notify('30 second initial delay')

while True:
    while True:        
        if notify('6 hour interval'):
            break
        time.sleep(30)
    
    time.sleep(21600) # every 6 hours, notify if there are any exams
    

