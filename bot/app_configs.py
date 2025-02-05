import os, json, sys,uuid,sqlite3,base64,io,ast,httpx,time,re,shutil,random,requests,socket,math,schedule
from urllib.parse import urlencode, urljoin
from os import listdir
from os.path import isfile
from datetime import datetime, timedelta

from threading import Thread,Event
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from functools import wraps

from flask import Flask, flash, redirect, render_template,send_file, abort, url_for,request,session,jsonify,g,send_from_directory,make_response
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from flask_socketio import SocketIO
from flask_cors import CORS
import webview


# adding the folder to path
root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(root, '..'))

# defining the neccessary folders
parent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(parent_folder, '..'))

app_folder = os.path.join(parent_folder,'bot')
env_path = os.path.join(parent_folder, '.env')

creators_file = os.path.join(app_folder,'creators.json')
configs_folder = os.path.join(app_folder,'settings')
logs_file = os.path.join(parent_folder,'logs.txt')

universal_folder = os.path.join(parent_folder,'universals')
universal_files = {
    'proxies':os.path.join(universal_folder,'proxies.txt'),
    'captions':os.path.join(universal_folder,'captions.txt'),
    'comments':os.path.join(universal_folder,'comments.txt')
}

TASK_SCHEDULES = {}


# loading environment variables
load_dotenv(env_path)
session_key = os.getenv('SECRET_KEY')
server_key = os.getenv('SERVER_KEY')

# Configure application
app = Flask(__name__)
app.debug = True
host = 'http://127.0.0.1:5000'
CORS(app,origins=host)
socketio = SocketIO(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SERVER_KEY'] = server_key
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024


app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = session_key.encode()
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
Session(app)

@app.template_filter('date')
def date_filter(value):
    return value.strftime('%Y-%m-%d')

@app.template_filter('date_time')
def date_time_filter(value):
    return value.strftime('%Y-%m-%d %H:%M:%S')


@app.template_filter('len_or_val')
def len_or_val(value):
    if isinstance(value,list):return len(value)
    else:return value

@app.template_filter('time_ago')
def last_seen(value):
    timestamp = value.strftime('%Y-%m-%d %H:%M:%S')
    last_seen_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    current_time = datetime.now()
    
    time_difference = current_time - last_seen_time

    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if time_difference.days > 0:
        return f"{time_difference.days} days ago"
    elif hours > 0:
        return f"{hours} hours ago"
    elif minutes > 0:
        return f"{minutes} minutes ago"
    else:
        return f"{seconds} seconds ago"
    

@app.template_filter('urlencode')
def urlencode_filter(value):
    if isinstance(value, str):
        return urlencode({'param': value}).split('=')[-1]  # URL encode and extract the value
    return value

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user = session.get('USER')
        if 'USER' not in session or user['status'] == 'blocked':
            if request.method == 'GET':
                return redirect(url_for('login'))
            elif request.method in ['POST', 'DELETE', 'PUT', 'PATCH']:
                return jsonify({'msg': 'you have to be logged in and active'}), 403
        return func(*args, **kwargs)
    return decorated_function

def check_role(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user = session.get('USER')
        if user['role'] != 'super-admin':
            if request.method == 'GET':
                return redirect(url_for('admins'))
            elif request.method in ['POST', 'DELETE', 'PUT', 'PATCH']:
                return jsonify({'msg': 'You must be a super admin to update a user'}), 403
        return func(*args, **kwargs)
    return decorated_function
    

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def validate_password(password):
    pattern = r'^(?=.*\d)(?=.*[a-zA-Z]).+$'
    return re.match(pattern, password)

def logout():
    try:
        for key in list(session.keys()):
            session.pop(key, None)
        session.modified = True
        return session.modified,'Logout successful'
    except Exception as error:
        return False,error
    

def share_engagement_by_24_hours(like_count, comment_count):
    """
    Distributes like and comment actions randomly across 24 hours.
    Returns a dictionary where keys are execution times, and values are (likes, comments).
    """
    def distribute_actions(total_count):
        time_slots = {}
        total_hours = 24
        remaining = total_count

        for hour in range(total_hours):
            if remaining <= 0:
                break
            actions_at_this_hour = random.randint(1, min(3, remaining))  # 1 to 3 actions per hour
            remaining -= actions_at_this_hour
            execution_time = (datetime.now() + timedelta(hours=hour)).strftime("%H:%M")  # Schedule within the hour
            if execution_time in time_slots:
                time_slots[execution_time] += actions_at_this_hour
            else:
                time_slots[execution_time] = actions_at_this_hour

        return time_slots  # Returns {execution_time: count}

    likes_schedule = distribute_actions(like_count)
    comments_schedule = distribute_actions(comment_count)

    # Merge the schedules to ensure both actions happen at the same times
    combined_schedule = {}
    for time in set(likes_schedule.keys()).union(comments_schedule.keys()):
        combined_schedule[time] = (
            likes_schedule.get(time, 0),  # Likes at this time
            comments_schedule.get(time, 0)  # Comments at this time
        )

    return combined_schedule  # Returns {execution_time: (likes, comments)}
    
    
def schedule_task(task_id, schedule_time):
    from start_tasks import start
    """
    Schedule a task to run daily at a specific time.
    """
    def run_task():
        print(f"Running scheduled task {task_id}...")
        start(task_id)

    try:
        # Schedule the task
        schedule.every().day.at(schedule_time).do(run_task)
        TASK_SCHEDULES[task_id] = schedule_time
        print(f"Task {task_id} scheduled at {schedule_time}.")
        return True, "Task scheduled successfully"
    except Exception as e:
        return False, f"Error scheduling task: {e}"
    

def schedule_engagements(engagement):
    from start_tasks import engage
    """
    Schedules both likes and comments at the same execution time, ensuring they run together.
    """

    total_schedules = 0

    try:
        task_id,engagement_id = engagement['task_id'],engagement['id']
        current_day = engagement["current_day"]
        like_count = engagement["like_pattern"].get(f'{current_day}', 0)
        comment_count = engagement["comment_pattern"].get(f'{current_day}', 0)

        if like_count > 0 or comment_count > 0:
            schedules = share_engagement_by_24_hours(like_count, comment_count)

            exec_times = []
            # Schedule combined engagement function
            for execution_time, (likes, comments) in schedules.items():
                schedule.every().day.at(execution_time).do(
                    engage, task_id, engagement_id, likes, comments
                ).tag(engagement_id, "engagement")
                exec_times.append(execution_time)
                total_schedules += 1

                print(f"Engagements scheduled for {task_id} on day {current_day} | execution time {execution_time}")

            TASK_SCHEDULES[engagement_id] = exec_times
            return True, f"Engagements scheduled for {task_id} on day {current_day} | execution time {exec_times}", total_schedules

        return False, f'Not enough likes or comments on task {task_id} | engagement {engagement_id} | day {current_day}', total_schedules

    except Exception as error:
        return False, str(error), total_schedules
    

# Background thread to run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


    