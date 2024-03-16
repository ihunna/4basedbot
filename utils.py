# -*- coding: utf-8 -*-

from configs import *
from bot.app_configs import host


root_dir = os.path.dirname(__file__)
db_file = os.path.join(root_dir,'database.db')


class Utils:
	@staticmethod
	def load_proxies():
		proxies = []
		file = os.path.join(root_dir,'universals','proxies.txt')
		with open(file,"r") as f:
			for proxy in f.readlines():
				proxy = proxy.replace("\n","").split(":")
				ip = proxy[0]
				port = proxy[1]
				username = proxy[2]
				password = proxy[3] if len(proxy) > 3 else None
				if password is not None:
					proxy = {
						"http": f'http://{username}:{password}@{ip}:{port}',
						"https": f'http://{username}:{password}@{ip}:{port}'
					}
				else:
					proxy = {
						"http": f'http://{username}:@{ip}:{port}',
						"https": f'http://{username}:@{ip}:{port}'
					}
					
				proxies.append(proxy)

		return proxies
	
	@staticmethod
	def get_proxy_cert(proxy_cert):
		return os.path.join(root_dir,proxy_cert)

	@staticmethod
	def generate_android_version():
		major_version = random.randint(2, 10)
		minor_version = random.randint(0, 9)
		build_version = random.randint(0, 9999)
		return f"{major_version}.{minor_version}.{build_version}"
	
	@staticmethod
	def generate_android_device():
		devices = [
				"Samsung Galaxy S21",
				"Samsung Galaxy S6",
				"Samsung Galaxy S5",
				"Samsung Galaxy S7",
				"Samsung Galaxy S8",
				"Samsung Galaxy S8+",
				"Samsung Galaxy S9",
				"Samsung Galaxy S9+",
				"Samsung Galaxy S10",
				"Samsung Galaxy S20",
				"Samsung Galaxy Note8",
				"Samsung Galaxy Note9",
				"Samsung Galaxy Note8+",
				"Samsung Galaxy Note9+",
				"Samsung Galaxy Note10",
				"Samsung Galaxy Note10+",
				"Google Pixel 5",
				"Google Pixel 4",
				"Google Pixel 3",
				"OnePlus 9 Pro",
				"OnePlus 8T",
				"OnePlus 8",
				"Sony Xperia 1 III",
				"Sony Xperia 5 II",
				"Sony Xperia 10 III",
				"Motorola Edge+",
				"Motorola Razr",
				"Xiaomi Mi 11",
				"Xiaomi Mi 10",
				"Xiaomi Redmi Note 10",
				"Nokia 8.3",
				"Nokia 5.4",
				"Huawei Mate 40 Pro",
				"Huawei P40 Pro",
				"LG Wing",
				"LG Velvet",
		]
		return random.choice(devices)
	
	@staticmethod
	def generate_user_agent(device, count):
		if str(device).lower() == 'android':
			devices = Utils.generate_android_device()
			devices = devices * (count // len(devices)) + devices[:count % len(devices)]
			browsers = [
				{"name":"Chrome","version":f"{random.choice([90,120])}.0.{random.choice([0,4430])}.{random.choice([0,210])}"},
				{"name":"Firefox","version":f"{random.choice([90,121])}.0.{random.choice([0,4430])}.{random.choice([0,210])}"},
			]
			browser = random.choice(browsers)
			return f"Mozilla/5.0 (Linux; Android {Utils.generate_android_version()}; {Utils.generate_android_device()}) AppleWebKit/537.36 (KHTML, like Gecko) {browser['name']}/{browser['version']} Mobile Safari/537.36"
		else:
			return UserAgent(use_external_data=True)
	@staticmethod
	def create_tables():
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS admins (
					id TEXT PRIMARY KEY,
					email TEXT,
				  	password TEXT,
				 	plain_password TEXT,
				  	role TEXT,
				  	status TEXT,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )''')
			
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS creators (
					id TEXT PRIMARY KEY,
				  	email TEXT,
					data TEXT,
				  	admin TEXT,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )''')
			
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS tasks (
					id TEXT PRIMARY KEY,
					status TEXT,
				  	admin TEXT,
					action_count,
					message TEXT,
				  	type TEXT,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )''')
			
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS posts (
					id TEXT PRIMARY KEY,
					creator TEXT,
					creator_username TEXT,
					posted_images TEXT,
					post_link TEXT,
					task_id TEXT,
					type TEXT,
					schedule_date TEXT,
					price TEXT,
				  	caption TEXT,
				  	admin TEXT,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )''')
			
			conn.commit()
			
			success,msg = True, 'Tables created'
		except Exception as error:
			success,msg = False, error
		finally:
			conn.close()
			return success,msg

	
	@staticmethod
	def add_admin(admin_id,admin_data):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			email = admin_data['email']
			password = admin_data['password']
			plain_password = admin_data['plain_password']
			role = admin_data['role']
			status = admin_data['status']

			cursor.execute("""INSERT INTO admins 
				  (id, email, password, plain_password, role, status) 
				  VALUES (?, ?, ?, ?, ?, ?)""", 
				  (admin_id,email,password,plain_password,role,status))
			conn.commit()
			
			success,msg = True, 'Admin added successfully'
		except Exception as error:
			success,msg =  False, str(f'Error adding admin :{error}')
		finally:
			conn.close()
			return success,msg

	@staticmethod
	def delete_admin(admin_id):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			cursor.execute('DELETE FROM admins WHERE id = ?', (admin_id,))
			conn.commit()

			success,msg =  True,'Admin deleted successfully'

		except Exception as error:
			success,msg = False,str(error)
		finally:
			conn.close()
			return success,msg

	@staticmethod
	def update_admin(admin_id, admin_data):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			email = admin_data['email']
			password = admin_data['password']
			plain_password = admin_data['plain_password']
			role = admin_data['role']
			status = admin_data['status']

			
			cursor.execute(""" UPDATE admins 
				  SET email = ?, 
				  password = ?,
				  plain_password = ?,
				  role = ?,
				  status = ? WHERE id = ?""", 
				  (email,password,plain_password,role,status,admin_id))
			
			conn.commit()
			
			success,msg = True, 'Creator updated successfully'
		except Exception as error:
			success,msg = False, f'Error updating creator: {error}'
		finally:
			conn.close() 
			return success,msg   
		
	@staticmethod
	def get_admins(limit=20, offset=0,multiple=True,admin=None,keyword=None):
		success, admins, total_admins = True, [], 0
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			if multiple:
				cursor.execute("SELECT COUNT(*) FROM admins")
				total_admins = cursor.fetchone()[0]

				cursor.execute("SELECT * FROM admins ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
				rows = cursor.fetchall()

				admins = [{
					'id': row[0], 
					'email': row[1],
					'password':row[2],
					'plain_password':row[3],
					'role':row[4],
					'status':row[5],
					'created_at': row[6]
					} for row in rows]
			else:
				cursor.execute(f"SELECT * FROM admins WHERE {keyword} = ?", (admin,))
				row = cursor.fetchone()
				if row is None:raise Exception('admin not found')
				
				admins = {
					'id': row[0], 
					'email': row[1],
					'password':row[2],
					'plain_password':row[3],
					'role':row[4],
					'status':row[5],
					'created_at': row[6]
				}

		except Exception as error:
			success, admins = False, f'Error getting admins:{error}'

		finally:
			conn.close()
			return success, admins, total_admins


	@staticmethod
	def add_creator(creator_id,creator_email,creator_data,admin):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			cursor.execute("INSERT INTO creators (id, email, data, admin) VALUES (?, ?, ?, ?)", (creator_id,creator_email,json.dumps(creator_data),admin))
			conn.commit()
			
			success,msg = True, 'Creator added successfully'
		except Exception as error:
			success,msg =  False, str(f'Error adding creator :{error}')
		finally:
			conn.close()
			return success,msg

	@staticmethod
	def delete_creator(creator_id):
		success,msg = False	,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			cursor.execute('DELETE FROM creators WHERE id = ?', (creator_id,))
			conn.commit()

			success,msg =  True,'Creator deleted successfully'

		except Exception as error:
			success,msg = False,str(error)
		finally:
			conn.close()
			return success,msg

	@staticmethod
	def update_creator(creator_id,creator_email,creator_data):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			
			cursor.execute("UPDATE creators SET email = ?, data = ? WHERE id = ?", (creator_email,json.dumps(creator_data),creator_id))
			conn.commit()
			
			success,msg = True, 'Creator updated successfully'
		except Exception as error:
			success,msg = False, f'Error updating creator: {error}'
		finally:
			conn.close() 
			return success,msg   
		
	@staticmethod
	def get_creators(admin='',limit=20, offset=0,multiple=True,creator=None):
		success, creators, total_creators = False, [], 0
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			if multiple:
				cursor.execute("SELECT COUNT(*) FROM creators WHERE admin = ?",(admin,))
				total_creators = cursor.fetchone()[0]

				cursor.execute("SELECT * FROM creators  WHERE admin = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", (admin, limit, offset))
				rows = cursor.fetchall()

				creators = [{
					'id': row[0], 
					'email':row[1],
					'data': json.loads(row[2]),
					'created_at': row[4]
					} for row in rows]
			else:
				cursor.execute("SELECT * FROM creators WHERE id = ?", (creator,))
				row = cursor.fetchone()
				
				creators = {
					'id': row[0], 
					'email':row[1],
					'data': json.loads(row[2]),
					'created_at': row[4]
				} if row is not None else {}
				
			success = True
		except Exception as error:
			success, creators = False, f'Error getting creators:{error}'

		finally:
			conn.close()
			return success, creators, total_creators
		
	@staticmethod
	def check_creator(creator_email,admin):
		success, creator = False,{}
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			cursor.execute("SELECT * FROM creators WHERE email = ? AND admin = ?", (creator_email,admin))
			row = cursor.fetchone()
			creator = {
				'id': row[0], 
				'email':row[1],
				'data': json.loads(row[2]),
				'created_at': row[4]
			} if row is not None else {}
			success = True

		except Exception as error:
			success, creator = False, f'Error getting creators:{error}'

		finally:
			conn.close()
			return success, creator

	@staticmethod
	def add_task(task_id, task):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			admin = task['admin']
			status = task['status']
			action_count = task['action_count']
			message = task['message']
			task_type = task['type']

			
			cursor.execute("INSERT INTO tasks (id, status, admin, action_count, message, type) VALUES (?, ?, ?, ?, ?, ?)", 
						   (task_id, status, admin, action_count, message, task_type))
			conn.commit()
			
			success,msg = True, 'Task added successfully'
		except Exception as error:
			success,msg =  False, str(error)
		finally:
			conn.close()
			return success,msg

	@staticmethod
	def delete_task(task_id):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
			conn.commit()

			success,msg =  True,'Task deleted successfully'

		except Exception as error:
			success,msg = False,str(error)
		finally:
			conn.close()
			return success,msg

	@staticmethod
	def update_task(task_id, task):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			status,message = task['status'], task['message']
			
			cursor.execute("UPDATE tasks SET status = ?, message = ? WHERE id = ?", (status,message,task_id))
			conn.commit()
			
			success,msg = True, 'Task updated successfully'
		except Exception as error:
			success,msg = False, str(error)
		finally:
			conn.close() 
			return success,msg   

	@staticmethod
	def check_task_status(task_id):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
			row = cursor.fetchall()

			if not row:raise Exception(f'Task {task_id} not found')

			row = row[0]

			if row:success,msg = True,{
				'id': row[0], 
				'status': row[1], 
				'admin':row[2],
				'action_count':row[3],
				'message':row[4],
				'type':row[5],
				'created_at': row[6]}

			else:success,msg = False,f'Could not get task {task_id}'
		
		except Exception as error:
			success,msg = False, str(error)
		
		finally:
			conn.close()
			return success,msg
		
	@staticmethod
	def get_tasks(admin='', limit=20, offset=0):
		success, tasks, total_tasks = True, [], 0
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			cursor.execute("SELECT COUNT(*) FROM tasks WHERE admin = ?", (admin,))
			total_tasks = cursor.fetchone()[0]

			cursor.execute("SELECT * FROM tasks WHERE admin = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", (admin, limit, offset))
			rows = cursor.fetchall()

			tasks = [{
				'id': row[0], 
				'status': row[1], 
				'admin':row[2],
				'action_count':row[3],
				'message':row[4],
				'type':row[5],
				'created_at': row[6]} for row in rows]

		except Exception as error:
			success, tasks = False, str(error)

		finally:
			conn.close()
			return success, tasks, total_tasks

	@staticmethod
	def add_post(admin,post):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			post_id = post['id']
			creator = post['creator']
			creator_username = post['creator_username']
			task_id = post['task_id']
			posted_images = post['posted_images']
			post_link = post['post_link']
			post_type = post['type']
			schedule_date = post['schedule_date']
			price = post['price']
			caption = post['caption']


			cursor.execute(
				"""INSERT INTO posts (
				id, creator, 
				creator_username, 
				posted_images, 
				post_link, task_id,
				type,schedule_date,
				price,caption,admin) 
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
				(post_id, creator, creator_username, 
					posted_images, post_link, 
					task_id,post_type,schedule_date,price,caption,admin))
			conn.commit()
			
			success,msg = True, 'Post added successfully'
			
		except Exception as error:
			success,msg =  False, f'Error adding post {error}'
		finally:
			conn.close()
			return success,msg

	@staticmethod
	def delete_post(post_id):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
			conn.commit()

			success,msg =  True,'Post deleted successfully'

		except Exception as error:
			success,msg = False,str(error)
		finally:
			conn.close()
			return success,msg 

	@staticmethod
	def update_post(post_id, post):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			schedule_date = post['schedule_date']
			price = post['price']
			caption = post['caption']

			
			cursor.execute(
				"""UPDATE posts 
				SET schedule_date = ?,
				price = ?,
				caption = ? 
				WHERE id = ?""", (schedule_date,price,caption,post_id))
			conn.commit()
			
			success,msg = True, 'posts updated successfully'
		except Exception as error:
			success,msg = False, str(error)
		finally:
			conn.close() 
			return success,msg  
		
	@staticmethod
	def get_posts(admin='',limit=20, offset=0,constraint=None,keyword=None):
		success, posts, total_posts = True, [], 0
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			if constraint is not None and keyword is not None:
				cursor.execute(f"SELECT COUNT(*) FROM posts WHERE {constraint} = ? AND admin = ?", (keyword, admin))
				total_posts = cursor.fetchone()[0]
				
				cursor.execute(
					f"""SELECT * FROM posts 
					WHERE {constraint} = ? AND admin = ?
					ORDER BY created_at DESC 
					LIMIT ? OFFSET ?""", (keyword, admin, limit, offset))
			else:
				cursor.execute(f"SELECT COUNT(*) FROM posts WHERE admin = ?", (admin,))
				total_posts = cursor.fetchone()[0]
				cursor.execute("SELECT * FROM posts WHERE admin = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", (admin, limit, offset))
		 
			rows = cursor.fetchall()

			posts = [{
				'id': row[0], 
				'creator': row[1], 
				'creator_username': row[2], 
				'posted_images': row[3], 
				'post_link':row[4],
				'task_id': row[5],
				'type':row[6],
				'schedule_date':row[7],
				'price':row[8],
				'caption':row[9],
				'admin':row[10],
				'created_at':row[11]
				} for row in rows]
		except Exception as error:
			success, posts = False, str(error)

		finally:
			conn.close()
			return success, posts, total_posts
		
	@staticmethod
	def time_diff(timestamp):
		try:
			time_secs = timestamp / 1000
			datetime_object = datetime.utcfromtimestamp(time_secs)
			current_time = datetime.utcnow()
			return True,current_time > datetime_object

		except Exception as error:
			return False,error
		
	@staticmethod
	def get_schedule_date(schedule_date:str):
		try:
			schedule_time = schedule_date.split('T')[1]
			_schedule_date = schedule_date.split('T')[0]
			schedule_hour = int(schedule_time.split(':')[0])
			schedule_hour = schedule_hour - 1 if schedule_hour > 0 else 11
			schedule_minute = schedule_time.split(':')[1]

			schedule_time = f'{schedule_hour}:{schedule_minute}'
			_schedule_date = f'{_schedule_date} {schedule_time}:00'
			schedule_date = f"{schedule_date.replace('T',' ')}:00"
			return True,_schedule_date,schedule_date
		except Exception as error:
			return False, error,error

	@staticmethod
	def write_log(message, log_file_path=logs_file):
		current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		with open(log_file_path, 'a',encoding='utf-8') as log_file:
			log_file.write(f"[{current_datetime}] [LOG] {message}\n")

		print(message)

	@staticmethod
	def get_images(images_folder,all=True,image_count=0):
		try:
			if os.path.exists(images_folder):
				files = os.listdir(images_folder)

				image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
				if not all:
					images = [os.path.join(images_folder,file) for file in files if os.path.splitext(file)[1].lower() in image_extensions]
					images = images[:image_count]
				else:
					images = [file for file in files if os.path.splitext(file)[1].lower() in image_extensions]
				return True,images
			else:
				return False, f'Folder {images_folder} does not exists'
		
		except Exception as error:
			return False, error
		
	@staticmethod
	def share_images(days,images):
		try:
			image_iterator = itertools.cycle(images)
			for day in days:
				day["images"] = [next(image_iterator) for _ in range(day["image_count"])]
			return True,days
		except Exception as error:
			return False, f'Error sharing images {error}'
		
	@staticmethod
	def update_client(client_msg):
		try:
			response = requests.post(f'{host}/update-client',json=client_msg)
			update = response.json()
			if not response.ok:raise Exception(f'Error updating client: {update["msg"]}')
			return True,update['msg']
		except Exception as error:
			return False,error
		
	@staticmethod
	def check_values(values:list):
		for value in values:
			if value is None or not value or len(value) < 1:
				return False
		else:return True