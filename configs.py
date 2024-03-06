import requests,httpx,json,csv,time,uuid,string,random,time,json,imaplib,email,re,os,itertools
import http.client,shutil
from os.path import isfile
http.client._MAXHEADERS = 1000
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from itertools import chain
import sqlite3
from dotenv import load_dotenv
from PIL import Image 

parent_folder = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(parent_folder, '.env')
logs_file = os.path.join(parent_folder,'logs.txt')