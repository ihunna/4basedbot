# -*- coding: utf-8 -*-

from app_configs import creators_file,configs_folder
from utils import Utils
from configs import *
import io


class Creator:
	def __init__(self):
		self.proxies = Utils.load_proxies()
		self.headers = {
			'authority': 'rest.4based.com',
			'accept': 'application/json',
			'accept-language': 'en-US,en;q=0.9',
			'content-type': 'application/json',
			'origin': 'https://4based.com',
			'referer': 'https://4based.com/',
			'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
			'sec-ch-ua-mobile': '?1',
			'sec-ch-ua-platform': '"Android"',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site'
		}

	def generate_sensor_data(self,type='x-auth-resource'):
		if type == 'x-auth-resource':
			return ''.join(random.choices(string.ascii_letters.upper() + string.digits + string.ascii_letters, k=len('2NTN5vEez9')))
		
	def login(self,admin,email,password,reuse_ip=True,task_id=None):
		try:
			success,result,user,new_user = False,'Login failed',{},True
			
			if task_id is not None:
				success,task_status = Utils.check_task_status(task_id)
				if not success:raise Exception(task_status)
				if task_status['status'].lower() in ['cancelled','canceled']:return False,  'Task canceled'

			self.headers.update({
				'user-agent': Utils.generate_user_agent('android',1),
				'x-auth-resource': self.generate_sensor_data(),
			})
				
			json_data = {
				'identifier': email,
				'password': password,
				'locale': 'en',
			}

			success,user = Utils.check_creator(email,admin)
			if not success:raise Exception(user)

			creator_id = user.get('id',None)
			user = user.get('data',{})

			if len(user.items()) >= 1:new_user = False

			if reuse_ip and 'proxies' in user.keys():
				proxies = user['proxies']
			else: proxies = random.choice(self.proxies)

			response = requests.post(
				'https://rest.4based.com/api/1.0/auth/login', 
				headers=self.headers, 
				json=json_data,
				proxies=proxies)
			
			if response.status_code == 400:
				if 'password not correct' in response.json().values():
					success,result = True,'password not correct'
			
			elif not response.ok:
				user['status'] = 'Offline'
				success,result = False,response.text
			else:
				user['status'] = 'Online'
				user['details'] = response.json()
				user['details']['user']['password'] = password
				avatar = user['details']['user']['avatar']

				if avatar is not None:
					image_url = f'https://pic.4based.com/preview/{avatar["code"]}/{avatar["_id"]}/300x300.{avatar["extension"]}'
					user['details']['user']['picture'] = image_url

				user['proxies'] = proxies
				user['reuse_ip'] = reuse_ip

			if new_user:
				creator_id = str(uuid.uuid4()).upper()[:8]
				success,msg = Utils.add_creator(creator_id,email,user,admin)

				images_folder = os.path.join(configs_folder,creator_id,'images')
				captions_file = os.path.join(configs_folder,creator_id,'captions.txt')
				
				os.makedirs(images_folder,exist_ok=True)
				with open(captions_file, 'w') as file:file.write("")

			else:
				success,msg = Utils.update_creator(creator_id,email,user)
			if not success:raise Exception(msg)

			user['id'] = creator_id
			success,result = True,user
			return success,result
		
		except Exception as error:
			error = f'Error logging in {error} on {email}'
			Utils.write_log(error)
			return False,error
		

	def creat_post(self,task_id,user:dict,images:str,image_count:int,caption:str,captions:list,caption_source:str,post_type:str='post',schedule_date:str='',price:int=0,reuse_ip:bool=True):
		try:
			Utils.write_log('+++ creating post +++')
			success,task_status = Utils.check_task_status(task_id)
			if not success:raise Exception(task_status)
			if task_status['status'].lower() in ['cancelled','canceled']:return False,  'Task canceled'
			
			success,msg,post,user_agent = False,'Error creating post',{},Utils.generate_user_agent('android',1)
			token,auth_resource = user['details']['credentials']['token'],user['details']['credentials']['resource']
			username = user['details']['user']['name']
			email = user['details']['user']['identifier']
			user_id = user['details']['user']['_id']

			if caption_source == 'creator':caption = str(random.choice(captions)).replace('\n','')

			if post_type == 'schedule':
				success,_schedule_date,schedule_date = Utils.get_schedule_date(schedule_date)
				if not success:raise Exception(_schedule_date)
			
			tax = (price / 100) * 20
			_price = (price + tax) * 100 if price > 1 else price

			self.headers.update({
				'user-agent': user_agent,
				'x-auth-resource': auth_resource,
				'x-auth-token':token
			})

			if reuse_ip and 'proxies' in user.keys():
				proxies = user['proxies']
			else: proxies = random.choice(self.proxies)

			if len(images) < image_count:raise Exception(f'Not enough images for {username} to match total images {image_count}')
			
			json_data = {
				'object_count': len(images),
			}

			response = requests.post(
				'https://rest.4based.com/api/1.0/transfer', 
				headers=self.headers, 
				json=json_data,
				proxies=proxies
			)

			if not response.ok: raise Exception(response.text)
			transfer_id = response.json()['_id']

			headers = {
				'Accept': 'application/json',
				'Referer': 'https://4based.com/',
				'x-auth-token':token, 
				'User-Agent': user_agent,
				'x-auth-resource': auth_resource,
			}
			
			post,posted = {},0
			for i in range(image_count):
				success,task_status = Utils.check_task_status(task_id)
				if not success:raise Exception(task_status)
				if task_status['status'].lower() in ['cancelled','canceled']:return False,  'Task canceled'
				
				image_path = images[i]

				img = Image.open(image_path)
				img_bytes = io.BytesIO()
				img.save(img_bytes, format='JPEG')
				image_data = img_bytes.getvalue()

				image_len = len(img_bytes.getvalue())
				
				if post_type == 'schedule':
					data = '{"model":"iPhone 15 Plus","make":"Apple","orientation":1,"thumbnail":null,"categories":["media","vault","image"],"private":false,'+f'"description":"{caption}","name":'+f'"{transfer_id}-{i}.jpg"'+',"tag":[],'+f'"price":{_price},"to_be_posted_at":"{_schedule_date}","status":"to_be_posted"'+'}'
				else:
					data = '{"model":"iPhone 15 Plus","make":"Apple","orientation":1,"thumbnail":null,"categories":["media","vault","image"],"private":false,'+f'"description":"{caption}","name":'+f'"{transfer_id}-{i}.jpg"'+',"tag":[],'+f'"price":{_price}'+'}'
				
				files = {
					'chunk': (f'{uuid.uuid4()}', image_data, 'application/octet-stream'),
					'chunkId': (None, f'{i}'),
					'chunkSizeStart': (None, '0'),
					'chunkSizeEnd': (None, f'{image_len}'),
					'chunkCount': (None, '1'),
					'fileSize': (None, f'{image_len}'),
					'fileType': (None, 'image/jpeg'),
					'guid': (None, f'{uuid.uuid4()}'),
					'transferId': (None,transfer_id),
					'position': (None, f'{i}'),
					'exIf': (None, data),
				}

				response = requests.post(
					f'https://storage.4based.com/api/1.0/user/{user_id}/file-stack',
					headers=headers,
					files=files,
					proxies=proxies
				)

				if response.ok:
					os.remove(image_path)
					posted += 1
				else:raise Exception(f'Error creating post on {username}, task {task_id}: {response.text}')

				post = response.json()

			if posted < 1:success,msg = False, f'No images uploaded on {username}, task {task_id}'
			elif post.get('complete',False):success,msg = True, {
				'id':post['_id'],
				'creator':user['id'],
				'creator_username':username,
				'posted_images':f'{posted} of {image_count}',
				'post_link':f'https://4based.com/file-stack/{post["_id"]}',
				'task_id':task_id,
				'type':post_type,
				'schedule_date':schedule_date,
				'price':price,
				'caption':caption
				}
			else:success,msg = False,f'Error creating post on {username}, task {task_id}'

			print(msg)
			return success,msg
		
		except Exception as error:
			Utils.write_log(error)
			return False,f'Error uploading post data {error}, {username}, task {task_id}'
		
	def update(self,user:dict,data:dict):
		try:
			user_id,user = user['id'],user['data']
			for key,value in data.items():
				user[key] = value
			success,msg = Utils.update_creator(user_id,user)
			if not success:raise Exception(msg)
			return True,user
		except Exception as error:
			return False, error
		

class _4BASED:

	def __init__(self):
		self.proxies = Utils.load_proxies()
		self.headers = {
			'authority': 'rest.4based.com',
			'accept': 'application/json',
			'accept-language': 'en-US,en;q=0.9',
			'content-type': 'application/json',
			'origin': 'https://4based.com',
			'referer': 'https://4based.com/',
			'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
			'sec-ch-ua-mobile': '?1',
			'sec-ch-ua-platform': '"Android"',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site'
		}

	def start(self,task_id,task,admin,days,max_workers):
		creators,task_status,task_msg,completed,fails = [],'failed',f'Post creation started',0,0
		try:
			Utils.write_log(f'=== Logging in creators ===')
			
			client_msg = {'msg':f'Logging all creators before posting on {task_id}','status':'success','type':'message'}
			success,msg = Utils.update_client(client_msg)
			if not success:Utils.write_log(msg)

			success,creators,total_creators = Utils.get_creators(admin=admin,limit=100)
			if not success:raise Exception(creators)
			
			len_creators = len(creators)
			if len_creators < total_creators:
				for i in range(total_creators - len_creators):
					offset = len_creators + i
					success,msg,total_creators = Utils.get_creators(admin=admin,limit=100,offset=offset)
					if not success:raise Exception(msg)
					creators += msg

			creators = [creator for creator in creators if 'verified' in creator['data']['details']['user'].keys()]
			if len(creators) < 1: raise Exception('No creator added, please add 1 or more creators first')

			with ThreadPoolExecutor(max_workers=max_workers) as executor:
				args = [(
					task,
					admin,
					creator,
					days,
					max_workers
				) for creator in creators] 

				futures = []
				for arg in args:
					success,task_status = Utils.check_task_status(task_id)
					if not success:raise Exception(task_status)
					if task_status['status'].lower() in ['cancelled','canceled']:break

					future = executor.submit(self.post, *arg)
					futures.append(future)

				for future in as_completed(futures):
					success,task_status = Utils.check_task_status(task_id)
					if not success:raise Exception(task_status)

					if task_status['status'].lower() in ['cancelled','canceled']:
						for remaining_future in futures:
							remaining_future.cancel()
						break

					success,task_status,result = future.result()
					if success:
						completed += 1

						client_msg = {'msg':result,'status':'success','type':'message'}
						success,msg = Utils.update_client(client_msg)
						if not success:Utils.write_log(msg)


					elif not success and task_status == 'Task canceled':
						task_status = 'canceled'
						client_msg = {'msg':result,'status':'error','type':'message'}
						
						success,msg = Utils.update_client(client_msg)
						if not success:Utils.write_log(msg)
						break
					
					else:
						fails += 1
						client_msg = {'msg':result,'status':'error','type':'message'}
						
						success,msg = Utils.update_client(client_msg)
						if not success:Utils.write_log(msg)

					task_msg = result

		except Exception as error:
			Utils.write_log(error)
			task_status = 'failed'
			task_msg = f'Error starting posts on {task_id} : {error}'
		
		finally:
			if task_status == 'canceled':
				client_msg = {'msg':f'{task_id} was canceled ','status':'error','type':'message'}
				task_msg = client_msg['msg']

			elif completed == len(creators) and len(creators) > 0:
				task_status = 'success'
				client_msg = {'msg':f'{task_id} successful ','status':'success','type':'message'}
				
			elif  fails > len(creators) // 2:
				client_msg = {'msg':f'{task_id} failed ','status':'error','type':'message'}
				task_status = 'failed'
				task_msg = client_msg['msg']
			
			elif task_status == 'failed':
				client_msg = {'msg':f'{task_id} failed ','status':'error','type':'message'}
			
			else:
				task_status = 'completed'
				client_msg = {'msg':f'{completed} items successful task:{task_id}','status':'success','type':'message'}
				task_msg = client_msg['msg']

			success,msg = Utils.update_client(client_msg)
			if not success:Utils.write_log(msg)

			success,msg = Utils.update_task(task_id,{
				'status':task_status,
				'message':task_msg
			})
			if not success:Utils.write_log(msg)
			
			task_data = task
			task_data.update(
				{'updated':str(datetime.now()),
				'status':task_status})

			success,msg = Utils.update_client({'task':task_data,'type':'task'})
			if not success:Utils.write_log(msg)
		
	def post(self,task:dict,admin:str,creator:dict,post_data:dict,max_workers):
		task_status,task_msg,completed,fails = 'failed',f'Post creation started',0,0
		try:
			task_id = task['id']

			Utils.write_log(f'=== Post creation started for {task["id"]} ===')

			creator_name = creator['data']['details']['user']['name']
			creator_email = creator['data']['details']['user']['identifier']
			creator_password = creator['data']['details']['user']['password']

			success,creator = Creator().login(admin,creator_email,creator_password,task_id=task_id)
			if not success:raise Exception(creator)

			images_folder = os.path.join(configs_folder,creator['id'],'images')
			total_images = sum([post['image_count'] for post in post_data])
			total_sfw_images = sum([post['image_count'] for post in post_data  if post['image_source']  == 'sfw'])
			total_nsfw_images = sum([post['image_count'] for post in post_data  if post['image_source']  == 'nsfw'])

			success,post_data = Utils.share_images(post_data,images_folder,total_images,total_sfw_images,total_nsfw_images)
			if not success:raise Exception(post_data)

			captions_file = os.path.join(configs_folder,creator['id'],'captions.txt')
			if not isfile(captions_file):raise Exception(f'Captions file does not exist for {creator_name}')

			captions = []
			with open(captions_file,'r',encoding='utf-8') as f:
				captions = f.readlines()

			with ThreadPoolExecutor(max_workers=max_workers) as executor:
				args = [(
					task_id,
					creator,
					day['images'],
					day['image_count'],
					day['caption'],
					captions,
					day['caption_source'],
					day['run_type'],
					day['schedule_date'],
					int(day['price']),
					creator['reuse_ip']
					) for day in post_data]
				
				futures = []
				for arg in args:
					success,task_status = Utils.check_task_status(task_id)
					if not success:raise Exception(task_status)
					if task_status['status'].lower() in ['cancelled','canceled']:break

					future = executor.submit(Creator().creat_post, *arg)
					futures.append(future)

				for future in as_completed(futures):
					success,task_status = Utils.check_task_status(task_id)
					if not success:raise Exception(task_status)
					
					if task_status['status'].lower() in ['cancelled','canceled']:
						for remaining_future in futures:
							remaining_future.cancel()
						break

					success,result = future.result()
					if success:
						completed += 1
						success,msg = Utils.add_post(admin,result)
						if not success:raise Exception(result)

						client_msg = {'msg':f'{completed} posts created so far on task:{task_id},{creator_name}','status':'success','type':'message'}
						success,msg = Utils.update_client(client_msg)
						if not success:Utils.write_log(msg)


					elif not success and result == 'Task canceled':
						task_status = 'canceled'
						client_msg = {'msg':f'{result} task:{task_id},{creator_name}','status':'error','type':'message'}
						
						success,msg = Utils.update_client(client_msg)
						if not success:Utils.write_log(msg)
						break
					
					else:
						fails += 1
						client_msg = {'msg':f'{fails} posts created so far on task:{task_id},{creator_name}','status':'error','type':'message'}
						
						success,msg = Utils.update_client(client_msg)
						if not success:Utils.write_log(msg)
						task_msg = result

		except Exception as error:
			Utils.write_log(error)
			task_status = 'failed'
			task_msg = f'Error creating post on {task_id} : {error}'

		finally:
			if task_status == 'canceled':
				client_msg = {'msg':f'{task_id} was canceled ','status':'error','type':'message'}
				task_msg = client_msg['msg']

			elif completed == len(post_data) and len(post_data) > 0:
				task_status = 'success'
				client_msg = {'msg':f'{task_id} successful ','status':'success','type':'message'}
				
			elif  fails > len(post_data) // 2:
				client_msg = {'msg':f'{task_id} failed ','status':'error','type':'message'}
				task_status = 'failed'
				task_msg = client_msg['msg']
			
			elif task_status == 'failed':
				client_msg = {'msg':f'{task_id} failed ','status':'error','type':'message'}
			
			else:
				task_status = 'completed'
				client_msg = {'msg':f'{completed} items successful task:{task_id},{creator_name} ','status':'success','type':'message'}
				task_msg = client_msg['msg']

			success,msg = Utils.update_client(client_msg)
			if not success:Utils.write_log(msg)

			if task_status == 'success':return True,task_status,task_msg
			return False,task_status,task_msg

	def add_creators(self,admin,task,creators):
		task_status,task_msg,completed,fails = 'failed',f'Post creation started',0,0
		try:
			Utils.write_log(f'=== Add creators started for {task["id"]} ===')
			task_id = task['id']

			with ThreadPoolExecutor(max_workers=10) as executor:
				args = [(
					admin,
					creator['email'],
					creator['password']
					) for creator in creators]
				kwargs = [{'task_id':task_id} for creator in creators]
				
				futures = []
				for arg,kwarg in zip(args,kwargs):
					success,task_status = Utils.check_task_status(task_id)
					if not success:raise Exception(task_status)
					if task_status['status'].lower() in ['cancelled','canceled']:break

					future = executor.submit(Creator().login, *arg, **kwarg)
					futures.append(future)

				for future in as_completed(futures):
					success,task_status = Utils.check_task_status(task_id)
					if not success:raise Exception(task_status)
					
					if task_status['status'].lower() in ['cancelled','canceled']:
						for remaining_future in futures:
							remaining_future.cancel()
						break

					success,result = future.result()
					if success:
						completed += 1

						client_msg = {'msg':f'{completed} creators added so far on task:{task_id}','status':'success','type':'message'}
						success,msg = Utils.update_client(client_msg)
						if not success:Utils.write_log(msg)


					elif not success and result == 'Task canceled':
						task_status = 'canceled'
						client_msg = {'msg':f'{result} task:{task_id}','status':'error','type':'message'}
						
						success,msg = Utils.update_client(client_msg)
						if not success:Utils.write_log(msg)
						break
					
					else:
						fails += 1
						client_msg = {'msg':f'{fails} creators added so far on task:{task_id}','status':'error','type':'message'}
						
						success,msg = Utils.update_client(client_msg)
						if not success:Utils.write_log(msg)
						task_msg = result

		except Exception as error:
			Utils.write_log(error)
			task_status = 'failed'
			task_msg = f'Error adding creators on {task_id} : {error}'

		finally:
			if task_status == 'canceled':
				client_msg = {'msg':f'{task_id} was canceled','status':'error','type':'message'}
				task_msg = client_msg['msg']

			elif completed == len(creators) and len(creators) > 0:
				task_status = 'success'
				client_msg = {'msg':f'{task_id} successful','status':'success','type':'message'}
				
			elif  fails > len(creators) // 2:
				client_msg = {'msg':f'{task_id} failed','status':'error','type':'message'}
				task_status = 'failed'
				task_msg = client_msg['msg']
			
			elif task_status == 'failed':
				client_msg = {'msg':f'{task_id} failed','status':'error','type':'message'}
			
			else:
				task_status = 'completed'
				client_msg = {'msg':f'{completed} items successful task:{task_id}','status':'success','type':'message'}
				task_msg = client_msg['msg']

			success,msg = Utils.update_client(client_msg)
			if not success:Utils.write_log(msg)

			success,msg = Utils.update_task(task_id,{
				'status':task_status,
				'message':task_msg
			})
			if not success:Utils.write_log(msg)
			
			task_data = task
			task_data.update(
				{'updated':str(datetime.now()),
				'status':task_status})

			success,msg = Utils.update_client({'task':task_data,'type':'task'})
			if not success:Utils.write_log(msg)


	def update_post(self,user:dict,post_id:str,post_data:dict={},edit=True):
		try:
			user_agent = Utils.generate_user_agent('android',1)
			token,auth_resource = user['details']['credentials']['token'],user['details']['credentials']['resource']
			username = user['details']['user']['name']
			email = user['details']['user']['identifier']
			user_id = user['details']['user']['_id']

			self.headers.update({
				'user-agent': user_agent,
				'x-auth-resource': auth_resource,
				'x-auth-token':token
			})

			if user['reuse_ip'] and 'proxies' in user.keys():
				proxies = user['proxies']
			else: proxies = random.choice(self.proxies)

			if edit:
				schedule_date = post_data['schedule_date']
				price = post_data['price']

				tax = (price / 100) * 20
				_price = round((price + tax) * 100 if price > 1 else price)

				success,_schedule_date,schedule_date = Utils.get_schedule_date(schedule_date)
				if not success:raise Exception(_schedule_date)

				json_data = {
					'description': post_data['caption'],
					'tag': [],
					'price': _price,
					'to_be_posted_at': _schedule_date,
				}

				response = requests.put(
					f'https://rest.4based.com/api/1.0/user/{user_id}/file-stack/{post_id}',
					headers=self.headers,
					proxies=proxies,
					json=json_data
				)

				if not response.ok:raise Exception(response.text)

				post_data['schedule_date'] = schedule_date
				success,msg = Utils.update_post(post_id,post_data)
				if not success:raise Exception(msg)

				return True, f'{post_id} on {username} updated successfully'
			
			else:
				response = requests.delete(
					f'https://rest.4based.com/api/1.0/user/{user_id}/file-stack/{post_id}',
					headers=self.headers,
					proxies=proxies
				)
				if not response.ok and response.status_code != 404:raise Exception(response.text)
				
				success,msg = Utils.delete_post(post_id)
				if not success:raise Exception(msg)

				return True, f'{post_id} on {username} deleted successfully'

		except Exception as error:
			return False,error