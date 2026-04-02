import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import parser 

SCOPES = ['https://www.googleapis.com/auth/calendar'] #for auth to calendar
CAL_ID = '5ec0d4205d278ba14f659d7e1159672a24f2186a632da4d2c7d49d5c3827d14b@group.calendar.google.com' #id calendar

def get_calendar_service():
    
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def delete_events_on_date(service, target_date_str):
    # target_date_str: строка в формате "2026-03-30"
    # 1. Определяем временные границы дня (от 00:00:00 до 23:59:59)
    time_min = f"{target_date_str}T00:00:00Z"
    time_max = f"{target_date_str}T23:59:59Z"

    print(f"🔎 Ищу события на {target_date_str} для удаления...")

    # 2. Получаем список всех событий в этом диапазоне
    events_result = service.events().list(
        calendarId=CAL_ID,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True # Разворачивает повторяющиеся события в отдельные записи
    ).execute()

    events = events_result.get('items', [])

    if not events:
        print(f"📭 На {target_date_str} событий не найдено.")
        return

    # 3. Удаляем каждое найденное событие
    for event in events:
        event_id = event['id']
        event_summary = event.get('summary', 'Без названия')
        try:
            service.events().delete(calendarId=CAL_ID, eventId=event_id).execute()
            print(f"🗑️ Удалено: {event_summary}")
        except Exception as e:
            print(f"❌ Не удалось удалить {event_summary}: {e}")

    print(f"✨ Очистка даты {target_date_str} завершена.")

def add_university_event(service, subject: str, room: str, teachers: str, date_str: str, start_time: str, end_time: str):
    """
    Параметры:
    date_str: "2026-03-30" (из JSON)
    start_time: "09:00" (из JSON)
    end_time: "10:30" (из JSON)
    """
    
    # Собираем полные строки даты и времени в формате ISO 8601
    # Google ожидает: "YYYY-MM-DDTHH:MM:SS"
    start_iso = f"{date_str}T{start_time}:00"
    end_iso = f"{date_str}T{end_time}:00"
        
    event_body = {
        'summary': f"{subject}",
        'location': room,
        'description': teachers,
        'start': {
            'dateTime': start_iso,
            'timeZone': 'Asia/Tashkent',
        },
        'end': {
            'dateTime': end_iso,
            'timeZone': 'Asia/Tashkent',
        },
    }

    try:
        event = service.events().insert(calendarId=CAL_ID, body=event_body).execute()
        print(f"✅ Успешно добавлено: {subject} ({date_str} {start_time})")
        return event.get('htmlLink')
    except Exception as e:
        print(f"❌ Ошибка при добавлении {subject}: {e}")
        return None

if __name__ == '__main__':
    service = get_calendar_service()
    last_date = "0"
    for i in parser.shedule:
        
        if last_date != i['date']:
            last_date = i['date']
            delete_events_on_date(service, last_date)
        
        classrooms = ""
        if (parser.classroom[i['classroomids'][0]].isdigit()):
            classrooms = "Ауд. "
        classrooms += ", ".join(parser.classroom[c_id] for c_id in i['classroomids'])
        
        teachers = "Преподаватель: " + ", ".join(parser.teachers[c_id] for c_id in i['teacherids'])
        
        add_university_event(service, parser.lessons[i['subjectid']], classrooms, teachers, i['date'], i['starttime'], i['endtime'])
    