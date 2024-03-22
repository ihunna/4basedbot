from app_configs import *
from utils import Utils
from actions import Creator,_4BASED

@socketio.on('connect')
def handle_connect():
	socketio.emit('connection','connection successful')
	# Utils.write_log('websocket connected')
	
@app.before_request
def before_request():
	g.host = host

@app.after_request
def after_request(response):
	"""Ensure responses aren't cached"""
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	response.headers["Expires"] = 0
	response.headers["Pragma"] = "no-cache"
	return response

@app.route('/',methods=['GET','POST'])
@login_required
def index():
	g.page = 'dashboard'
	admin = session['USER']['id']

	success, creators, total_creators = Utils.get_creators(admin=admin,limit=5)
	if not success:raise Exception(creators)

	success, posts, total_posts = Utils.get_posts(admin=admin,limit=5)
	if not success:raise Exception(posts)

	success, tasks, total_tasks = Utils.get_tasks(admin=admin,limit=5)
	if not success:raise Exception(tasks)

	success, schedules, total_schedules = Utils.get_posts(
				admin=admin,limit=5,
				constraint='type',keyword='schedule')
	
	if not success:raise Exception(schedules)

	stats = {
		'schedules':total_schedules,
		'tasks':total_tasks,
		'posts':total_posts,
		'creators':total_creators}
	
	return render_template(
		'index.html',
		stats=stats,
		tasks=tasks,
		posts=posts,
		creators=creators)

@app.route('/admins',methods=['GET'])
@login_required
def admins():
	try:
		g.page = 'admins'
		action = request.args.get('action')
		page = request.args.get('page',1, type=int)
		tab = request.args.get('tab','all')

		per_page = 20
		offset = (page - 1) * per_page
		
		if action == 'view-item':
			item = request.args.get('admin')
			
			success, admin,_ = Utils.get_admins(multiple=False,keyword='id',admin=item)
			if success:return render_template('view-item.html', type='admin', item=admin)

			Utils.write_log(posts)
			return render_template('view-item.html', action=404)
		
		if action == 'edit-admin':
			g.page = action
			admin_id = request.args.get('admin')
			success, admin,_ = Utils.get_admins(multiple=False,keyword='id',admin=admin_id)
			
			if not success:
				Utils.write_log(posts)
				return render_template('view-item.html', action=404)
			
			return render_template('admins.html',action=action,admin=admin)
		
		if tab and tab == 'me':
			item = session['USER']['id']
			success, admin,_ = Utils.get_admins(multiple=False,keyword='id',admin=item)
			admins,total_admins = [admin],1

		else:success,admins,total_admins = Utils.get_admins(limit=per_page,offset=offset)
		
		next_page = page + 1 if page  < total_admins / per_page else page
		prev_page = page - 1 if page  > 1 else page
		current_page = offset + len(admins)

		if success:return render_template('admins.html', 
					action=action, 
					tab=tab,
					admins=admins,
					session_admin=session['USER'],
					total_admins=total_admins,
					next_page=next_page,
					prev_page=prev_page,
					current_page=current_page)
		
	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/admins/<action>',methods=['POST'])
@login_required
@check_role
def handle_admin(action):
	try:
		if action == 'update':
			data = request.get_json()
			email = data['email']
			password = data['password']
			role = data['role']
			status = data['status']
			admin_id = data['admin']

			password_hash = generate_password_hash(password)

			success,msg = Utils.update_admin(admin_id,{
				'email':email,
				'password':password_hash,
				'plain_password':password,
				'role':role,
				'status':status
			})

			if not success:
				Utils.write_log(msg)
				return jsonify({'msg':'Error updating admin'}),400
			
			success,user,_ = Utils.get_admins(multiple=False,keyword='email',admin=email)
			if not success: return jsonify({'msg':'User does not exists'}),400

			session['USER'] = user
			return jsonify({'msg':'Admin updated successfully'}),200

		else:return jsonify({'msg':'No action specified'}),400
	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/creators',methods=['GET'])
@login_required
def creators():
	try:
		g.page = 'creators'
		page = request.args.get('page', 1, type=int)
		per_page = 20

		admin = session['USER']['id']

		offset = (page - 1) * per_page
		success, creators, total_creators = Utils.get_creators(admin=admin,limit=per_page, offset=offset)
	
		if success:
			next_page = page + 1 if page  < total_creators / per_page else page
			prev_page = page - 1 if page  > 1 else page
			current_page = offset + len(creators)
			return render_template('creators.html', 
					creators=creators,
					total_creators=total_creators,
					next_page=next_page,
					prev_page=prev_page,
					current_page=current_page)
		else:
			Utils.write_log(creators)
			return render_template('view-item.html', action=404)
	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/creators/<action>',methods=['POST'])
@login_required
def handle_creators(action):
	try:
		if action == 'add':
			admin = session['USER']['id']

			creators = request.form.get('configs','')
			if creators == '':return jsonify({'msg':'No creators to add'}),400
			creators = creators.replace('\r','').split('\n')
			
			creators = [{
				'email':creator.split(':')[0],
				'password':creator.split(':')[1]} for creator in creators if ':' in creator]
			
			task_id = str(uuid.uuid4()).capitalize()[:8]

			task_data = {
				'id':task_id,
				'admin':admin,
				'status':'running',
				'action_count':len(creators),
				'type':'creators',
				'message':f'Creating task on {admin}'
				}
			
			success,msg = Utils.add_task(task_id,task_data)
			if not success:raise Exception(msg)

			task = Thread(target=_4BASED().add_creators, 
				args=(
					admin,
					task_data,
					creators
				))
				
			task.start()
			
			if task.is_alive():
				success,msg = Utils.update_client({'msg':f'{task_id} successfully created','status':'success','type':'message'})
				if not success:Utils.write_log(msg)
				
				else:
					Utils.write_log(msg)
					Utils.write_log(f'Task successflly created')
			
					return jsonify({'msg': 'Add creators task successfully started'}), 200
				
			else:return jsonify({'msg': f'Could not start task {task_id}'}), 400
		else:return jsonify({'msg':'No action specified'}),400
	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/creator',methods=['GET','POST'])
@login_required
def creator():
	try:
		if request.method == 'GET':
			g.page = 'creators'
			creator = request.args.get('creator')
			success, creator, _ = Utils.get_creators(multiple=False,creator=creator)
			if not success:raise Exception(creator)
			elif len(creator) < 1:return render_template('view-item.html',action=404)
			
			creator = creator['data']
			reuse_ip = creator['reuse_ip']

			return render_template(
				'creator.html',
				creator=creator['details']['user'],
				reuse_ip=reuse_ip)
		
		elif request.method == 'POST':
			data = request.get_json()
			action = data['action']
			status = data['status']
			key = data['key']
			creator = data['creator']

			success, creator, _ = Utils.get_creators(multiple=False,creator=creator)
			if not success:raise Exception(creator)
			elif len(creator) < 1:return jsonify({'msg':'No such creator'}),404

			if key == 'reuse_ip' and status in ['yes','Yes','YES']:status = True 
			elif key == 'reuse_ip' and status in ['no','No','NO']: status = False

			data = {key:status}

			if action == 'edit':
				success,msg = Creator().update(creator,data)
				if not success:
					Utils.write_log(msg)
					return jsonify({'msg':'Error updating user'}), 400
				else:
					return jsonify({'msg':'user udated successfully'}),200
				
			return jsonify({'msg':'action not specified'}),400

		else:raise Exception('Method not allowed')

	except Exception as error:
		print(error)
		abort(500)


@app.route('/posts',methods=['GET'])
@login_required
def posts():
	try:
		action = request.args.get('action','posts')
		g.page = action

		page = request.args.get('page', 1, type=int)
		per_page = 20
		offset = (page - 1) * per_page

		admin = session['USER']['id']

		if action == 'add-post':
			with open(universal_files['captions'],'r',encoding='utf-8') as f:
				captions = [caption for caption in f.readlines() if caption != '\n']

			return render_template('posts.html',action=action,captions=captions)
		
		elif action == 'get-items':
			item = request.args.get('item')
			constraint = request.args.get('key')

			if constraint == 'admin':
				constraint,item = None,None

			g.page = 'schedules' if item == 'schedule' else 'posts'

			success, posts, total_posts = Utils.get_posts(
				admin=admin,
				limit=per_page, 
				offset=offset,
				constraint=constraint,keyword=item)
			
			next_page = page + 1 if page  < total_posts / per_page else page
			prev_page = page - 1 if page  > 1 else page
			current_page = offset + len(posts)

			params = f'action=get-items&item={item}&key={constraint}'

			next_page = f'{next_page}&{params}'
			prev_page = f'{prev_page}&{params}'

			if success:return render_template('posts.html', 
						action=action, 
						posts=posts,
						total_posts=total_posts,
						next_page=next_page,
						prev_page=prev_page,
						current_page=current_page)
			
			Utils.write_log(posts)
			return render_template('view-item.html', action=404)
		
		elif action == 'view-item':
			g.page = 'posts'
			item = request.args.get('post')
			success, posts, total_posts = Utils.get_posts(admin=admin,constraint='id',keyword=item)
			if not success or len(posts) < 1:
				return render_template('view-item.html',action=404)
			
			elif success:return render_template('view-item.html', type='post', item=posts[0],total_posts=total_posts)

			Utils.write_log(posts)
			return render_template('view-item.html', action=404)
		
		elif action == 'edit-post':
			g.page = 'edit-post'
			item = request.args.get('post')

			success, posts, total_posts = Utils.get_posts(admin=admin,constraint='id',keyword=item)
			if not success:raise Exception(posts)

			post = posts[0]

			with open(universal_files['captions'],'r',encoding='utf-8') as f:
				captions = [caption for caption in f.readlines() if caption != '\n']
			
			return render_template('posts.html',action=action,captions=captions,post=post)


		success, posts, total_posts = Utils.get_posts(admin=admin,limit=per_page, offset=offset)
		next_page = page + 1 if page  < total_posts / per_page else page
		prev_page = page - 1 if page  > 1 else page
		current_page = offset + len(posts)

		if success:return render_template('posts.html', 
					action=action, 
					posts=posts,
					total_posts=total_posts,
					next_page=next_page,
					prev_page=prev_page,
					current_page=current_page)
		
		Utils.write_log(posts)
		return render_template('view-item.html', action=404)

	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/posts/<action>', methods=['POST'])
@login_required
def handle_posts(action):
	try:
		data = request.get_json()
		total_posts,max_workers,posts = data['total_posts'],data.get('max-workers'),[]

		if action == 'add-post':
			for post in range(1, total_posts + 1):
				post_data = {
					f'image_source':data[f'post-{post}-image-source'],
					f'image_count': int(data[f'post-{post}-image-count']),
					# f'paid_count': int(data[f'post-{post}-paid-count']),
					f'price': data[f'post-{post}-price'],
					f'caption': str(data.get(f'post-{post}-caption','')).replace('\n',''),
					# f'paid_caption': str(data.get(f'day-{post}-paid-caption','')).replace('\n',''),
					f'caption_source':data[f'post-{post}-caption-source'],
					f'run_type': data[f'post-{post}-run-type'],
					f'schedule_date':data.get(f'post-{post}-schedule-date',None)
				}

				# if post_data['paid_count'] > 0:
				# 	paid_post = {
				# 		'image_count':post_data['paid_count'],
				# 		'price':post_data['price'],
				# 		'caption':post_data['paid_caption'] if post_data['paid_caption'] != '' else post_data['caption'],
				# 		'caption_source':post_data['caption_source'],
				# 		'run_type':post_data['run_type'],
				# 		'schedule_date':post_data['schedule_date']
				# 	}
				# 	posts.append(paid_post)
				
				# free_post = {
				# 	'image_count':post_data["image_count"] - post_data["paid_count"] if post_data['paid_count'] > 0 else post_data['image_count'],
				# 	'price':0,
				# 	'caption':post_data['caption'],
				# 	'caption_source':post_data['caption_source'],
				# 	'run_type':post_data['run_type'],
				# 	'schedule_date':post_data['schedule_date']
				# }
				# if free_post['image_count'] > 0:posts.append(free_post)
				posts.append(post_data)
			
			admin = session['USER']['id']

			task_id = str(uuid.uuid4()).upper()[:8]

			task_data = {
				'id':task_id,
				'admin':admin,
				'status':'running',
				'action_count':len(posts),
				'type':'posts',
				'message':f'Creating task on {admin}'
			}
			
			success,msg = Utils.add_task(task_id,task_data)
			if not success:raise Exception(msg)

			task = Thread(target=_4BASED().start, 
				args=(
					task_id,
					task_data,
					admin,
					posts,
					int(max_workers) if max_workers != '' else 20
				))
			
			task.start()
			
			if task.is_alive():
				success,msg = Utils.update_client({'msg':f'{task_id} successfully created','status':'success','type':'message'})
				if not success:Utils.write_log(msg)
					
				else:
					Utils.write_log(msg)
					Utils.write_log(f'Task successflly created')
			
				return jsonify({'days': posts, 'msg': 'Post created successfully'}), 200
				
			else:return jsonify({'msg': f'Could not start task {task_id}'}), 400
		
		elif action == 'edit-post':
			creator_id = data['creator']
			success,creator,_ = Utils.get_creators(multiple=False,creator=creator_id)
			if not success:raise Exception(creator)

			post_data =  {
					'price': int(data['post-price']),
					'caption': str(data['caption']).replace('\n',''),
					'schedule_date':data.get(f'schedule-date',None)
				}
			post_id = data['post-id']
			
			success,msg = _4BASED().update_post(creator['data'],post_id,post_data=post_data)
			if not success:raise Exception(msg)

			return jsonify({'msg':'Post updated successfully'}),200

			
		else:return jsonify({'msg':'No action and category specified'}),400
	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/tasks', methods=['GET'])
@login_required
def tasks():
	try:
		g.page = 'tasks'
		action = request.args.get('action')

		admin = session['USER']['id']

		if action and action == 'view-item':
			task_id = request.args.get('task')
			success,task = Utils.check_task_status(task_id)

			if not success:return render_template('view-item.html',action=404)
			return render_template('view-item.html',type='task',item=task)
			
		page = request.args.get('page', 1, type=int)
		per_page = 20

		offset = (page - 1) * per_page
		success, tasks, total_tasks = Utils.get_tasks(admin=admin,limit=per_page, offset=offset)
		
		if success:
			next_page = page + 1 if page  < total_tasks / per_page else page
			prev_page = page - 1 if page  > 1 else page
			current_page = offset + len(tasks)
			return render_template('tasks.html', 
					tasks=tasks,
					total_tasks=total_tasks,
					next_page=next_page,
					prev_page=prev_page,
					current_page=current_page)
		else:
			return render_template('view-item.html', action=404)

	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/task/<action>',methods=['POST'])
@login_required
def update_task(action):
	try:
		data = request.get_json().get('data')
		if not Utils.check_values([data]):raise ValueError('data not provided')

		data = data[0]
		_,task_id = data.get('target'),data.get('item')

		if action == 'stop':
			success,task = Utils.check_task_status(task_id)
			if not success:return jsonify({'msg':'The specified task does not exist'}),400

			task_status = task.get('status')
			
			if task_status.lower() in ['running','pending']:
				task['status'] = 'cancelling'
				task['message'] = f'Stopping task {task_id}'
				success,msg = Utils.update_task(task_id,task)
				if not success:raise Exception(str(msg))

				success,msg = Utils.update_client({'msg':f'Stopping task {task_id}, it might take a while.','status':'success','type':'message'})
				if not success: raise Exception(msg)

				task_msg = task
				task_msg.update({'updated':str(datetime.now())})

				success,msg = Utils.update_client({'task':task_msg,'type':'task'})
				if not success: raise Exception(msg)

				Utils.write_log(msg)
				return jsonify({'msg':f'Stopping task {task_id}, it might take a while.'})
			
			else:return jsonify({'msg':'Task is not running'}),400
			
		return jsonify({'msg':'No action specified'}),400


	except Exception as error:
		Utils.write_log(error)
		abort (500)

@app.route('/configs',methods=['GET'])
@login_required
def configs():
	try:
		g.page = 'configs'

		tab = request.args.get('tab','proxies')
		creator = request.args.get('creator','universal')
		images_folder = os.path.join(configs_folder,creator,'images')
		
		if tab == 'images' and creator != 'universal':
			category = request.args.get('category',None)
			items_per_page = 20
			page = int(request.args.get('page', 1))

			images = []
			success,msg = Utils.get_images(images_folder,tag=category)
			
			if not success:Utils.write_log(msg)
			
			else:
				images = msg
				start_idx = (page - 1) * items_per_page
				end_idx = start_idx + items_per_page

				total_pages = (len(images) + items_per_page - 1) // items_per_page
				page = total_pages if page > total_pages else page
				images = images[start_idx:end_idx]

				return render_template(
					'configs.html',creator=creator,
					tab=tab,images=images,
					total_pages=total_pages,
					page=page,category=category)
			
			return render_template('configs.html',creator=creator,images=images)
		
		elif tab == 'upload-images':
			return render_template('configs.html',creator=creator,tab=tab)
		
		elif tab == 'captions' and creator != 'universal':
			captions_file = os.path.join(configs_folder,creator,'captions.txt')
			if not os.path.exists(captions_file):
				with open(captions_file, 'w') as file:file.write("")
			
			with open(captions_file,'r',encoding='utf-8') as f:
				captions = f.readlines()

			return render_template(
				'configs.html',tab='captions',
				creator=creator,captions=captions
				)
		
		else:return redirect(url_for('files',category=tab))
		

	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/image/<creator>/<folder>/<filename>',methods=['GET'])
def serve_image(creator,folder,filename):
	image_folder = os.path.join(configs_folder,creator,folder)
	image_path = os.path.join(configs_folder,creator,folder,filename)
	if not os.path.isfile(image_path):abort(404)
	return send_from_directory(image_folder,filename)

@app.route('/images/<action>/<creator>/<category>',methods=['POST'])
@login_required
def images(action,creator,category):
	try:
		if action == 'upload':
			images_folder = os.path.join(configs_folder, creator, 'images')
			os.makedirs(images_folder, exist_ok=True)

			saved = 0

			for i in range(len(request.files)):
				file = request.files[f'file{i}']

				if file.filename == '':
					return jsonify({'msg': 'No selected file'}), 400

				file_path = os.path.join(images_folder, f'{category}-{file.filename}')
				file.save(file_path)

				saved+=1
			if saved >= 1:return jsonify({'msg': 'Images uploaded successfully'}), 200
			else:return jsonify({'msg': f'{saved} images saved'}), 400

		else:return jsonify({'msg':'No action specified'}),400
	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/config/<tab>/<action>/<creator>', methods=['POST'])
@login_required
def config(tab, action,creator):
	try:
		captions_file = os.path.join(configs_folder, creator, 'captions.txt')
		if tab == 'captions' and action == 'update':
			captions = request.form.get('configs','')
			captions = captions.replace('\n','')

			with open(captions_file,'w',encoding='utf-8') as f:
				f.writelines(captions)
			return jsonify({'msg':'captions added successfully'}),200
		
		else:return jsonify({'msg':'No tab specified'}),400
	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/files/<category>',methods=['GET'])
@login_required
def files(category):
	try:
		g.page = 'configs'
		configs = []
		if category in ['proxies','captions']:
			file = universal_files[category]
			with open(file,'r',encoding='utf-8') as f:
					configs = f.readlines()

		return render_template(
			'configs.html',
			tab='files',
			configs=configs,
			category=category
		)

	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/files/<category>/update',methods=['POST'])
@login_required
def handle_files(category):
	try:
		g.page = 'configs'
		
		configs = request.form.get('configs','')
		configs = configs.replace('\n','')

		file = universal_files[category]

		with open(file,'w',encoding='utf-8') as f:
			f.writelines(configs)
		return jsonify({'msg':f'{category} added successfully'}),200

	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/delete-items/<category>',methods=['POST'])
@login_required
def delete(category):
	try:
		data = request.get_json()['data']
		deleted = 0

		if category == 'images':
			for item in data:
				target,filename = item['target'],item['item']
				image_folder = os.path.join(configs_folder,target,'images')
				image_path = os.path.join(image_folder,filename)
				
				if not os.path.isfile(image_path):
					return jsonify({'msg':f'{filename} does not exist, {deleted} images deleted'}),400
				os.remove(image_path)

				deleted += 1
		
		elif category == 'tasks':
			for item in data:
				task_id = item['item']
				
				success,task = Utils.check_task_status(task_id)
				if not success:return jsonify({'msg':'The specified task does not exist'}),400
				
				task_status = task.get('status')
				
				if task_status.lower() in ['running','pending']:
					success,msg = Utils.update_client({'msg':f"Cannot delete {task_id} while it's still running",'status':'success','type':'message'})
					continue
				
				success,msg = Utils.delete_task(task_id)
				if not success:raise Exception(msg)

				deleted += 1

		elif category == 'posts':
			for item in data:
				post_id = item['item']
				creator = item['target']
				success, creator, _ = Utils.get_creators(multiple=False,creator=creator)
				if not success:raise Exception(creator)
				
				success,msg = _4BASED().update_post(creator['data'],post_id,edit=False)
				if not success:raise Exception(msg)
				deleted += 1

		elif category == 'creators':
			for item in data:
				creator_id,creator_email = item['item'],item['target']

				success, msg = Utils.delete_creator(creator_id)
				if not success:raise Exception(creator)
				
				creator_folder = os.path.join(configs_folder,creator_email)
				Utils.write_log(creator_folder)
				if os.path.exists(creator_folder):shutil.rmtree(creator_folder)
				deleted += 1
		
		elif category == 'admins':
			user = session['USER']
			if user['role'] != 'super-admin' or user['status'] == 'blocked':
				return jsonify({'msg':'You are not authorized to delete an account'}),400
			
			for item in data:
				admin_id = item['item']
				if admin_id == user['id']:return jsonify({'msg':'Cannot delete self'}),400

				success,msg = Utils.delete_admin(admin_id)
				if not success:raise Exception(msg)

				deleted += 1
		
		return jsonify({'msg':f'Deleted {deleted} {category} successfully'}),200
	
	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/signup',methods=['GET','POST'])
def signup():
	try:
		if request.method == 'GET':
			return render_template('signup.html')
		
		elif request.method == 'POST':
			email = request.form.get('email')
			password = request.form.get('password')
			role = request.form.get('role')
			secret_key = request.form.get('secret-key')

			msg = Utils.check_values([email,password,role,secret_key])
			if not (msg):return jsonify({'msg':'Some values are empty'}),400


			if secret_key != app.config['SERVER_KEY']:
				print(app.config['SERVER_KEY'])
				return jsonify({'msg':'You are not authorized to create an account'}), 400
			
			if not validate_email(email):return jsonify({'msg':'Not a valid email format'}),400
			if len(password) < 8:return jsonify({'msg':'Password must more than 7 chars'}),400

			success,msg,_ = Utils.get_admins(multiple=False,keyword='email',admin=email)
			if success: return jsonify({'msg':'email already exists'}),400

			password_hash = generate_password_hash(password)

			admin = {
				'email':email,
				'password':password_hash,
				'plain_password':password,
				'role':role,
				'status':'active'
			}

			admin_id = str(uuid.uuid4())
			success,msg = Utils.add_admin(admin_id,admin)

			if not success:
				Utils.write_log(msg)
				return jsonify({'msg':'Error creating admin'}),400
			else: return jsonify({'msg':'Admin created successfully','admin':admin_id})

		else:raise Exception('method not allowed')
	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/login',methods=['GET','POST'])
def login():
	try:
		if request.method == 'GET':return render_template('login.html')

		elif request.method == 'POST':
			email = request.form.get('email')
			password = request.form.get('password')

			msg = Utils.check_values([email,password])
			if not (msg):return jsonify({'msg':'Some values are empty'}),400
			
			success,user,_ = Utils.get_admins(multiple=False,keyword='email',admin=email)
			if not success: return jsonify({'msg':'User does not exists'}),400
			
			password_hash = user['password']
			if not check_password_hash(password_hash,password):
				return jsonify({'msg':'Incorrect password'}),400

			session['USER'] = user
			return jsonify({'msg':'Login successful'}), 200

		else:return jsonify({'msg':'No request method provided'}),400

	except Exception as error:
		Utils.write_log(error)
		abort(500)


@app.route('/update-client',methods=['POST'])
def handle_client_update():
	try:
		client_msg = request.get_json()
		socketio.emit('update-client', client_msg,callback=True)
		return jsonify({'msg':'client updated'}),200
	except Exception as error:
		return jsonify({'msg':f'{error}'}),400
	

@app.route('/logout',methods=['GET','POST'])
@login_required
def do_logout():
	try:
		if request.method == 'GET':
			success,msg = logout()
			if success: 
				response = make_response(jsonify({'msg': msg}), 200)
				response.delete_cookie('session')
				return response
			
			Utils.write_log(msg)
			return jsonify({'msg':'logout unsuccessful'}), 400
		
		elif request.method == 'POST':
			success,msg = logout()
			if success: 
				response = make_response(jsonify({'msg': msg}), 200)
				response.delete_cookie('session')
				return response
			
			Utils.write_log(msg)
			return jsonify({'msg':'logout unsuccessful'}), 400
		
		else: raise Exception('Not a valid mothod')
	
	except Exception as error:
		Utils.write_log(error)
		return jsonify({'msg':'logout unsuccessful'}), 500
	
@app.route('/logs',methods=['GET'])
@login_required
@check_role
def logs():
	try:
		with open(logs_file,'r',encoding='utf-8') as f:
				logs = f.readlines()
				logs = list(reversed(logs))
		return render_template('logs.html',logs=logs)
	except Exception as error:
		Utils.write_log(error)
		abort(500)

@app.route('/logs/<action>',methods=['POST'])
@login_required
@check_role
def handle_logs(action):
	try:
		if action == 'clear':
			with open(logs_file,'w',encoding='utf-8') as f:f.write('')
			return jsonify({'msg':'Logs cleared successfully'}),200
		else:return jsonify({'msg':'No action specified'}),400

	except Exception as error:
		Utils.write_log(error)
		abort (500)















if __name__ == "__main__":
	try:
		success,msg = Utils.create_tables()
		if not success:raise Exception(msg)
		socketio.run(app)
	except Exception as error:
		Utils.write_log(error)