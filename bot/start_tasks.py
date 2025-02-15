import json,uuid
from datetime import datetime
from actions import _4BASED
from utils import Utils, Scheduler
import time,random



def start (task_id):
    task_status,task_msg,current_day,posts = 'failed',f'Post creation started',0,[]
    try:
        success,task = Utils.get_task(task_id)
        if not success:raise Exception(f'The specified task {task_id} does not exist')

        task_data = {
            'id':task_id,
            'admin':task['admin'],
            'status':task['status'],
            'action_count':task['action_count'],
            'type':task['type'],
            'message':task['message']
        }

        task_config = json.loads(task['config'])
        task_status,current_day = task['status'],task_config['current_day']

        like_pattern:dict = task_config['like_pattern']
        comment_pattern:dict = task_config['comment_pattern']

        
        if task_status in ['pending','running']:
            task_status = 'posting'
            
            task.update({
                'message':f'Posting started on task {task_id} | day {current_day}',
                'status':task_status
            })
            success,msg = Utils.update_task(task_id,task)
            if not success:raise Exception(str(msg))
            
            task_data = task
            task_data.update({'updated':str(datetime.now())})

            success,msg = Utils.update_client({'task':task_data,'type':'task'})
            if not success: Utils.write_log(msg)

            success,task_status,msg,client_msg,posts = _4BASED().start_post(
                task_data,
                task_config['admin'],
                task_config['posts'],
                task_config['media_type'],
                task_config['max_workers'],
                selected_creators=task_config['selected_creators']
            )

            task_status = 'running' if success else task_status

            success,msg = Utils.update_client(client_msg)
            if not success:Utils.write_log(msg)

            success,msg = Utils.update_task(task_id,{
                'status':task_status,
                'message':msg
            })
            if not success:raise Exception(msg)
            
            task_data = task
            task_data.update({
                'status':task_status,
                'updated':str(datetime.now())
            })

            success,msg = Utils.update_client({'task':task_data,'type':'task'})
            if not success:Utils.write_log(msg)


            if task_status not in ['failed','canceled','cancelled','pending']:

                engagement_id = str(uuid.uuid4()).upper()[:8]
                engagement = {
                    'id':engagement_id,
                    'admin':task_config['admin'],
                    'task_id':task_id,
                    'status':'pending',
                    'like_pattern':like_pattern,
                    'comment_pattern':comment_pattern,
                    'current_day':current_day,
                    'message':f'Creating schdeules for task {task_id} | day {current_day}',
                    'post_ids':posts
                }

                success,msg,total_schedules = Scheduler.schedule_engagements(engagement)
                if not success:raise Exception(msg)

                Utils.write_log(msg)
                Utils.update_client({'msg':f'{msg} task:{task_id} | engagement {engagement_id}','status':'success','type':'message'})

                engagement.update({
                    'daily_total':total_schedules,
                    'completed_engagements':0
                })
                success,msg = Utils.add_engagement(engagement_id,engagement)
                if not success:raise Exception(msg)
                Utils.write_log(msg)
                Utils.update_client({'msg':f'{msg} task:{task_id} | engagement {engagement_id}','status':'success','type':'message'})
                
            success,msg = Utils.update_task(task_id,{
                'current_day':current_day + 1,
                'status':task_status
            })
            if not success:raise Exception(msg)

         
    except Exception as error:
        Utils.write_log(error)
        task_status = 'failed'
        task_msg = f'Error running post schedule on {task_id} | {error} | day {current_day}'

        success,msg = Utils.update_client({'msg':task_msg,'status':'error','type':'message'})
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



def engage(task_id, engagement_id, like_count, comment_count):
    try:
        Utils.write_log(f"Running scheduled engagement {engagement_id} on task {task_id}...")
        success, task = Utils.get_task(task_id)
        if not success:
            raise Exception(f'The specified task {task_id} does not exist')

        success, engagement = Utils.get_engagement(engagement_id)
        if not success:raise Exception(engagement)

        current_day, engagement_status = engagement['current_day'], engagement['status']
        task_status, task_config = task['status'], json.loads(task['config'])

        Utils.write_log(f'Engagement : {engagement}')
        print('\n')
        Utils.write_log(f'Task: {task}')

        total_engagements_for_day = engagement.get('daily_total',1)
        completed_engagements = engagement.get('completed_engagements', 0)

        if (task_status == 'running' and engagement_status in ['pending', 'running']) and like_count >= 1:
            engagement_status = 'liking'

            # print(task_status,engagement_status)

            success, msg = Utils.update_client({
                'msg': f'Liking started on task {task_id} | engagement {engagement_id} | day {current_day}',
                'status': 'success', 'type': 'message'
            })
            if not success:raise Exception(msg)

            engagement.update({'status': engagement_status})
            success, msg = Utils.update_engagement(engagement_id, engagement)
            if not success:raise Exception(str(msg))

            success, engagement_status, msg, client_msg = _4BASED().start_like_comment(
                engagement,
                task_config['admin'],
                like_count,
                task_config['max_workers']
            )

            success, msg = Utils.update_client(client_msg)
            if not success:raise Exception(msg)

            engagement_status = 'running' if success else engagement_status
            completed_engagements += like_count

            engagement.update({
                'status': engagement_status,
                'message': msg,
                'completed_engagements': completed_engagements,
                'current_day': current_day
            })
            success, msg = Utils.update_engagement(engagement_id, engagement)
            if not success:raise Exception(msg)

        if (task_status == 'running' and engagement_status in ['pending', 'running']) and comment_count >= 1:
            engagement_status = 'commenting'

            success, msg = Utils.update_client({
                'msg': f'Commenting started on task {task_id} | engagement {engagement_id} | day {current_day}',
                'status': 'success', 'type': 'message'
            })
            if not success:
                raise Exception(msg)

            engagement.update({'status': engagement_status})
            success, msg = Utils.update_engagement(engagement_id, engagement)
            if not success:
                raise Exception(str(msg))

            success, engagement_status, msg, client_msg = _4BASED().start_like_comment(
                engagement,
                task_config['admin'],
                comment_count,
                task_config['max_workers'],
                action='comment'
            )

            success, msg = Utils.update_client(client_msg)
            if not success:
                raise Exception(msg)

            engagement_status = 'running' if success else engagement_status
            completed_engagements += comment_count

            engagement.update({'status': engagement_status,
                'message': msg,
                'completed_engagements': completed_engagements,
                'current_day': current_day
            })
            success, msg = Utils.update_engagement(engagement_id, engagement)
            if not success:raise Exception(msg)

        # ** Check if the day's engagements are complete, then schedule the next day **
        if completed_engagements >= total_engagements_for_day:
            if current_day < len(engagement['like_pattern'].items()) and current_day < len(engagement['comment_pattern'].items()):
                current_day += 1  # Move to next day

                engagement.update({
                    'status': 'pending',
                    'current_day': current_day,
                    'completed_engagements': 0
                })
                success, msg, total_schedules = Scheduler.schedule_engagements(engagement)
                if not success:
                    raise Exception(msg)
                
                engagement['daily_total'] = total_schedules

                engagement.update({
                    'status': 'pending',
                    'message': f'New schedules added for day {current_day}',
                    'current_day': current_day,
                    'completed_engagements': 0
                })

                success, msg = Utils.update_engagement(engagement_id, engagement)
                if not success:
                    raise Exception(msg)

                success, msg = Utils.update_client({
                    'msg': f'New schedules added for day {current_day}',
                    'status': 'success',
                    'type': 'message'
                })

                if not success:raise Exception(msg)

    except Exception as error:
        Utils.write_log(error)
        success, msg = Utils.update_client({
            'msg': f'Error on engagement {engagement_id} | {error}',
            'status': 'error',
            'type': 'message'
        })
        if not success:Utils.write_log(error)
