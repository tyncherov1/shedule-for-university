import requests
import json
import datetime

def get_week():
    today = datetime.date.today()
    weekday = today.weekday()
    
    if weekday == 6 or weekday == 5:
        monday = today + datetime.timedelta(days=7-weekday)
    else:
        monday = today - datetime.timedelta(days=weekday)
    sunday = monday +  datetime.timedelta(days=6)
    return monday.isoformat(), sunday.isoformat()

url_shedule = "https://msu2006.edupage.org/timetable/server/currenttt.js?__func=curentttGetData"
url_data = "https://msu2006.edupage.org/rpr/server/maindbi.js?__func=mainDBIAccessor"


payload_shedule = {"__args": [None, {"year":2025,"datefrom": get_week()[0],"dateto": get_week()[1],"table":"classes","id":"-273","showColors":True,"showIgroupsInClasses":False,"showOrig":True,"log_module":"CurrentTTView"}],
                   "__gsh":"00000000"}

payload_data = {"__args": [None, 2025, {"vt_filter":{"datefrom": get_week()[0],"dateto": get_week()[1]}}, {"op":"fetch","needed_part": {"classrooms":["short"],"subjects":["name"], "teachers":["short", "name"]}}],
                "__gsh":"00000000"}

response = requests.post(url_shedule, json=payload_shedule)

shedule = response.json()
shedule = shedule['r']['ttitems']

if response.status_code == 200:
    # Сохраняем результат в файл, чтобы не листать бесконечную консоль
    with open("shedule.json", "w", encoding="utf-8") as f:
        json.dump(shedule, f, indent=4, ensure_ascii=False)
    print("ГОТОВО! Открой файл shedule.json в папке со скриптом.")
else:
    print(f"Ошибка {response.status_code}: {response.text}")

response = requests.post(url_data, json=payload_data)

data = response.json()
data = data['r']['tables']

lessons = {item['id']: item['name'] for item in data[1]['data_rows']}
classroom = {item['id']: item['short'] for item in data[2]['data_rows']}
teachers = {item['id']: item['short'] for item in data[0]['data_rows']}

data = [lessons, classroom, teachers]

if response.status_code == 200:
    # Сохраняем результат в файл, чтобы не листать бесконечную консоль
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("ГОТОВО! Открой файл data.json в папке со скриптом.")
else:
    print(f"Ошибка {response.status_code}: {response.text}")