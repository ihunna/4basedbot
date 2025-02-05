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
				  	category TEXT DEFAULT 'creator',
				  	task_id TEXT,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )''')
			
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS tasks (
					id TEXT PRIMARY KEY,
					status TEXT NOT NULL,
				  	admin TEXT NOT NULL,
					action_count NOT NULL,
					message TEXT NULL,
				  	type TEXT NOT NULL,
				  	config TEXT NULL DEFAULT '{}',
				  	current_day INTEGER NOT NULL DEFAULT 1,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )''')
			
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS posts (
					id TEXT PRIMARY KEY,
					creator TEXT,
					creator_username TEXT,
					posted_medias TEXT,
					post_link TEXT,
					task_id TEXT,
					type TEXT,
					schedule_date TEXT,
					price TEXT,
				  	caption TEXT,
				  	admin TEXT,
				  	media_type TEXT,
				  	user_engagement_ids TEXT,
					created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )''')
			
			cursor.execute(''' CREATE TABLE IF NOT EXISTS engagements (
					id TEXT PRIMARY KEY,
				  	task_id TEXT NOT NULL,
					status TEXT NOT NULL,
				  	admin TEXT NOT NULL,
					like_pattern TEXT NOT NULL,
					comment_pattern TEXT NULL,
				  	current_day INTEGER NOT NULL,
				  	message TEXT NULL,
				  	post_ids TEXT NOT NULL,
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
	def add_creator(creator_id,creator_email,creator_data,admin,category='creators',task_id=None):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			if len(creator_data.items()) > 0:
				category = 'creator' if category == 'creators' else 'user'
				cursor.execute("INSERT INTO creators (id, email, data, admin, category, task_id) VALUES (?, ?, ?, ?, ?, ?)", (creator_id,creator_email,json.dumps(creator_data),admin,category,task_id))
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
	def get_creators(admin='', limit=20, offset=0, multiple=True, creator=None, category='creator', constraint=None, keyword=None, selected_creators=[], exclude_from_posts=None):
		"""
		Fetch creators with various filters and options.
		
		Parameters:
			exclude_from_posts: str (optional) - The column name to exclude creators from (e.g., 'like_user_ids', 'comment_user_ids').
		"""
		success, creators, total_creators = False, [], 0
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			if exclude_from_posts:  # Dynamically exclude creators based on the provided column
				cursor.execute(
					f"""
					SELECT COUNT(*) 
					FROM creators 
					WHERE id NOT IN (
						SELECT DISTINCT {exclude_from_posts}
						FROM posts
					) AND admin = ?
					""",
					(admin,)
				)
				total_creators = cursor.fetchone()[0]

				cursor.execute(
					f"""
					SELECT * 
					FROM creators 
					WHERE id NOT IN (
						SELECT DISTINCT {exclude_from_posts}
						FROM posts
					) AND admin = ?
					ORDER BY created_at DESC 
					LIMIT ? OFFSET ?
					""",
					(admin, limit, offset)
				)
				rows = cursor.fetchall()

				creators = [{
					'id': row[0], 
					'email': row[1],
					'data': json.loads(row[2]),
					'created_at': row[4]
				} for row in rows]
			elif selected_creators:  # Check if selected_creators is not empty
				placeholders = ','.join('?' for _ in selected_creators)  # Create placeholders for the IN clause
				cursor.execute(
					f"SELECT COUNT(*) FROM creators WHERE id IN ({placeholders}) AND admin = ?",
					(*selected_creators, admin)
				)
				total_creators = cursor.fetchone()[0]

				cursor.execute(
					f"""SELECT * FROM creators 
					WHERE id IN ({placeholders}) AND admin = ? 
					ORDER BY created_at DESC 
					LIMIT ? OFFSET ?""",
					(*selected_creators, admin, limit, offset)
				)
				rows = cursor.fetchall()

				creators = [{
					'id': row[0], 
					'email': row[1],
					'data': json.loads(row[2]),
					'created_at': row[4]
				} for row in rows]
			else:
				# Fallback to the original logic if no selected_creators

				if multiple:
					category = {'users':'user','creators':'creator','creator':'creator'}[category]
					cursor.execute(
						"SELECT COUNT(*) FROM creators WHERE admin = ? AND category = ?",
						(admin, category)
					)
					total_creators = cursor.fetchone()[0]

					cursor.execute(
						"SELECT * FROM creators WHERE admin = ? AND category = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
						(admin, category, limit, offset)
					)
					rows = cursor.fetchall()

					creators = [{
						'id': row[0], 
						'email': row[1],
						'data': json.loads(row[2]),
						'created_at': row[4]
					} for row in rows]
				else:
					cursor.execute("SELECT * FROM creators WHERE id = ?", (creator,))
					row = cursor.fetchone()

					creators = {
						'id': row[0], 
						'email': row[1],
						'data': json.loads(row[2]),
						'created_at': row[4]
					} if row is not None else {}

			success = True
		except Exception as error:
			success, creators = False, f'Error getting creators: {error}'
		finally:
			conn.close()
			return success, creators, total_creators


		
	@staticmethod
	def check_creator(creator_email,admin):
		print(creator_email,admin)
		success, creator = False,{}
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			cursor.execute("SELECT * FROM creators WHERE email = ? AND admin = ?", (creator_email,admin))
			row = cursor.fetchone()
			print(row)
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
	def add_task(task_id, task:dict):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			admin = task['admin']
			status = task['status']
			action_count = task['action_count']
			message = task['message']
			task_type = task['type']
			config = json.dumps(task.get('config',{}))

			
			cursor.execute("INSERT INTO tasks (id, status, admin, action_count, message, type, config) VALUES (?, ?, ?, ?, ?, ?, ?)", 
						   (task_id, status, admin, action_count, message, task_type, config))
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
			current_day = task.get('current_day',None)
			if current_day:
				cursor.execute("UPDATE tasks SET current_day = ? WHERE id = ?", (current_day,task_id))
			else:
				status,message = task['status'], task['message']
				cursor.execute("UPDATE tasks SET status = ?, message = ? WHERE id = ?", (status,message,task_id))
			
			conn.commit()
			
			success,msg = True, 'Task updated successfully'
		except Exception as error:
			success,msg = False, f'Error updating task {task_id} : {error}'
		finally:
			conn.close() 
			return success,msg   

	@staticmethod
	def get_task(task_id):
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
				'config':row[6],
				'created_at': row[7]}

			else:success,msg = False,f'Could not get task {task_id}'
		
		except Exception as error:
			success,msg = False, str(error)
		
		finally:
			conn.close()
			return success,msg 

	@staticmethod
	def check_task_status(task_id):
		return Utils.get_task(task_id)
	
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
				'config':row[6],
				'created_at': row[7]} for row in rows]

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
			posted_medias = post['posted_medias']
			post_link = post['post_link']
			post_type = post['type']
			schedule_date = post['schedule_date']
			price = post['price']
			caption = post['caption']
			media_type = post['media_type']
			user_engagement_ids = json.dumps(post.get('user_engagement_ids',{'like_user_ids':[],'comment_user_ids':[]}))


			cursor.execute(
				"""INSERT INTO posts (
				id, creator, 
				creator_username, 
				posted_medias, 
				post_link, task_id,
				type,schedule_date,
				price,caption,admin,media_type,user_engagement_ids) 
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
				(post_id, creator, creator_username, 
					posted_medias, post_link, 
					task_id,post_type,schedule_date,price,caption,admin,media_type,user_engagement_ids))
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
	def update_post(post_id, post, user_engagement_ids=False):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			if not user_engagement_ids:
				schedule_date = post['schedule_date']
				price = post['price']
				caption = post['caption']
				
				cursor.execute(
					"""UPDATE posts 
					SET schedule_date = ?,
					price = ?,
					caption = ? 
					user_engagement_ids = ?
					WHERE id = ?""", (schedule_date,price,caption,user_engagement_ids,post_id))
			else:
				user_engagement_ids = json.dumps(post['user_engagement_ids'],{'like_user_ids':[],'comment_user_ids':[]})
				
				cursor.execute(
					"""UPDATE posts 
					SET user_engagement_ids = ?,
					WHERE id = ?""", (user_engagement_ids,post_id))
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
				'posted_medias': row[3], 
				'post_link':row[4],
				'task_id': row[5],
				'type':row[6],
				'schedule_date':row[7],
				'price':row[8],
				'caption':row[9],
				'admin':row[10],
				'media_type':row[11],
				'user_engagement_ids':row[12],
				'created_at':row[13]
				} for row in rows]
		except Exception as error:
			success, posts = False, str(error)

		finally:
			conn.close()
			return success, posts, total_posts
		
	@staticmethod
	def get_post(post):
		success, msg = False, ''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			cursor.execute("SELECT * FROM posts WHERE id = ? ", (post))
			row = cursor.fetchall()

			if not row: raise Exception(f'Post {post} not found')
			row = row[0]
			success,msg = True,{
				'id': row[0], 
				'creator': row[1], 
				'creator_username': row[2], 
				'posted_medias': row[3], 
				'post_link':row[4],
				'task_id': row[5],
				'type':row[6],
				'schedule_date':row[7],
				'price':row[8],
				'caption':row[9],
				'admin':row[10],
				'media_type':row[11],
				'user_engagement_ids':row[12],
				'created_at':row[13]
				}
			
		except Exception as error:
			success, msg = False, str(error)

		finally:
			conn.close()
			return success, msg
		
	@staticmethod
	def add_engagement(engagement_id, engagement:dict):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		
		try:
			admin = engagement['admin']
			status = engagement['status']
			task_id = engagement['task_id']
			like_pattern = json.dumps(engagement['like_pattern'])
			comment_pattern = json.dumps(engagement['comment_pattern'])
			current_day = engagement['current_day']
			message = engagement['message']
			post_ids = json.dumps(engagement['post_ids'])

			
			cursor.execute("INSERT INTO engagements (id, task_id, status, admin, like_pattern, comment_pattern, current_day, message, post_ids) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
						   (engagement_id, task_id, status, admin, like_pattern, comment_pattern, current_day, message, post_ids))
			conn.commit()
			
			success,msg = True, 'Engagement added successfully'
		except Exception as error:
			success,msg =  False, f'Error adding engagement {engagement_id} | {error}'
		finally:
			conn.close()
			return success,msg

	@staticmethod
	def delete_engagement(engagement_id):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			cursor.execute('DELETE FROM engagements WHERE id = ?', (engagement_id,))
			conn.commit()

			success,msg =  True,'Engagement deleted successfully'

		except Exception as error:
			success,msg = False,str(error)
		finally:
			conn.close()
			return success,msg

	@staticmethod
	def update_engagement(engagement_id, engagement):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:
			status,current_day,message = engagement['status'], engagement['current_day'],engagement['message']
			
			cursor.execute("UPDATE engagements SET status = ?, current_day = ? message = ? WHERE id = ?", (status,current_day,message,engagement_id))
			conn.commit()
			
			success,msg = True, 'Engagement updated successfully'
		except Exception as error:
			success,msg = False, f'Error updating engagement | {error}'
		finally:
			conn.close() 
			return success,msg   

	@staticmethod
	def get_engagement(engagement_id):
		success,msg = False,''
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			cursor.execute("SELECT * FROM engagements WHERE id = ?", (engagement_id,))
			row = cursor.fetchall()

			if not row:raise Exception(f'Engagement {engagement_id} not found')

			row = row[0]

			if row:success,msg = True,{
				'id': row[0],
				'task_id':row[1] ,
				'status': row[2], 
				'admin':row[3],
				'like_pattern':row[4],
				'comment_pattern':row[5],
				'current_day':row[6],
				'message':row[7],
				'post_ids':row[8],
				'created_at': row[9]}

			else:success,msg = False,f'Could not get engagement {engagement_id}'
		
		except Exception as error:
			success,msg = False, f'Error getting engagement | {error}'
		
		finally:
			conn.close()
			return success,msg 
	
	@staticmethod
	def get_engagements(admin='', limit=20, offset=0):
		success, engagements, total_engagements = True, [], 0
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		try:

			cursor.execute("SELECT COUNT(*) FROM engagements WHERE admin = ?", (admin,))
			total_engagements = cursor.fetchone()[0]

			cursor.execute("SELECT * FROM engagements WHERE admin = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", (admin, limit, offset))
			rows = cursor.fetchall()

			engagements = [{
				'id': row[0],
				'task_id':row[1] ,
				'status': row[2], 
				'admin':row[3],
				'like_pattern':row[4],
				'comment_pattern':row[5],
				'current_day':row[6],
				'message':row[7],
				'post_ids':row[8],
				'created_at': row[9]} for row in rows]

		except Exception as error:
			success, engagements = False, str(error)

		finally:
			conn.close()
			return success, engagements, total_engagements
		
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
	def get_medias(folder,all=True,media_count=0,tag=None,full_link=False,media_type='images'):
		try:
			if os.path.exists(folder):
				files = os.listdir(folder)

				extensions = ['.mp4','.mov'] if media_type == 'videos' else ['.jpg', '.jpeg', '.png', '.gif']
				if not all and full_link:
					medias = [file for file in files if os.path.splitext(file)[1].lower() in extensions]
					if tag is not None:medias = [media for media in medias if media.startswith(f'{tag}-')]
					videos = videos[:media_count]
				
				else:
					medias = [file for file in files if os.path.splitext(file)[1].lower() in extensions]
					if tag is not None:medias = [media for media in medias if media.startswith(f'{tag}-')]
				
				if full_link:medias = [os.path.join(folder,media) for media in medias]
				return True,medias
			else:
				return False, f'Folder {folder} does not exists'
		
		except Exception as error:
			return False, error
		
	@staticmethod
	def share_medias(posts,folder,media_type,total_medias,total_sfw_medias,total_nsfw_medias):
		try:
			success,medias = Utils.get_medias(folder,media_type=media_type)
			if not success:raise Exception(medias)

			sfw_medias = [os.path.join(folder,media) for media in medias if media.startswith(f'sfw-')][:total_sfw_medias]
			nsfw_medias = [os.path.join(folder,media) for media in medias if media.startswith(f'nsfw-')][:total_nsfw_medias]
			any_medias = [os.path.join(folder,media) for media in medias][:total_medias]

			media_configs = {
				'sfw':{
					'iter':itertools.cycle(sfw_medias),
					'total':total_sfw_medias,
					'available':len(sfw_medias)
		   		},
				'nsfw':{
					'iter':itertools.cycle(nsfw_medias),
					'total':total_nsfw_medias,
					'available':len(nsfw_medias)
		   		},
				'all':{
					'iter':itertools.cycle(any_medias),
					'total':total_medias,
					'available':len(any_medias)
		   		}
			}
			
			for post in posts:
				medias_tag = post['media_source']
				medias = media_configs[medias_tag]
				
				if medias['available'] < medias['total']:raise Exception(f'Not enough {medias_tag} medias')
				post["medias"] = [next(medias['iter']) for _ in range(post["media_count"])]
			return True,posts
		except Exception as error:
			return False, f'Error sharing medias, {error}'
		
	@staticmethod
	def read_bytes(media_type,media_path):
		try:
			result = {
				'config':'image/jpeg',
				'type':'image'
			}
			if media_type == 'images':
				img = Image.open(media_path)
				media_bytes = io.BytesIO()
				img.save(media_bytes, format='JPEG')
			else:
				with VideoFileClip(media_path) as video:
					with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
						video.write_videofile(temp_file.name, codec='libx264', audio_codec='aac')

						media_bytes = io.BytesIO()
						with open(temp_file.name, 'rb') as f:media_bytes.write(f.read())
				
				result.update({
					'config':'video/mp4',
					'type':'video'
				})

			media_data = media_bytes.getvalue()
			media_len = len(media_bytes.getvalue())

			result.update({
				'bytes':media_data,
				'len':media_len
			})
			return True,result
		except Exception as error:
			return False,f'Error reading bytes {error}'
		
	@staticmethod
	def move_posted_media(media_path: str):
		try:
			if not os.path.exists(media_path):
				return f"Error: File {media_path} does not exist."

			path_parts = media_path.split(os.sep)

			try:
				user_id = path_parts[-3] 
				media_type = path_parts[-2] 
				main_path = '/'.join(path_parts[:-3])
			
			except IndexError:raise Exception("Error: Path structure is incorrect.")

			target_dir = os.path.join(main_path, user_id, f"used_{media_type}")
			os.makedirs(target_dir, exist_ok=True)

			filename = os.path.basename(media_path)
			destination_path = os.path.join(target_dir, filename)

			shutil.move(media_path, destination_path)

			return True,f"File moved to: {destination_path}"
		
		except Exception as error:
			return False,error
		
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