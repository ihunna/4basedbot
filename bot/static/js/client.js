const updateClient = (data) => {
    if (data.type === 'task'){
        try{
            const task = data.task
            const status = task.status;
            const row = document.querySelector(`#tasks-table [id="${task.id}"]`);
            
            if (!row){
                return
            }

            const span = row.querySelector('.task_status span');
            const actions = row.querySelector('.actions .actions-list');

            const deleteBtn = document.createElement('li');
            deleteBtn.setAttribute('data-action','delete');
            deleteBtn.setAttribute('data-action-url','/delete-items/tasks');
            deleteBtn.setAttribute('data-action-message',`Deleting Task ${task.id}`);
            deleteBtn.setAttribute('data-item',`${task.id}`);
            deleteBtn.setAttribute('data-action-target',`${task.creator}`);
            deleteBtn.setAttribute('onclick',"handleAction(this,'tasks-table','single')");

            const deleteIcon = document.createElement('i');
            deleteIcon.classList.add('fas', 'fa-trash', 'text-danger');
            deleteBtn.appendChild(deleteIcon);

            const action_btn = document.createElement('li');
            action_btn.classList.add(`tags`);

            const action_link = document.createElement('a');
            action_link.setAttribute('href',`/${task.type}?action=get-items&item=${task.id}&key=task_id`);
            action_link.classList.add('bg-primary','light');
            
            const action_icon = document.createElement('i');
            action_link.innerHTML = `
                <i class="fas fa-eye"></i>
                ${task.type}
            `

            action_btn.appendChild(action_link);

            const status_str = status[0].toUpperCase() + status.slice(1);
            span.innerHTML = status_str

            if (status === 'pending'){
                span.classList.remove('bg-danger','bg-success');
                span.classList.add('bg-warning');
            }
            else if (status === 'running' || status === 'completed' || status === 'success' || status === 'posting'){
                span.classList.remove('bg-danger','bg-warning');
                span.classList.add('bg-success');
            }else {
                span.classList.remove('bg-success','bg-warning');
                span.classList.add('bg-danger');
            }

            actions.innerHTML = ``;
            actions.appendChild(action_btn)
            actions.appendChild(deleteBtn);

            if (status === 'running'){
                const stopBtn = document.createElement('li');
                stopBtn.setAttribute('data-action','stop');
                stopBtn.setAttribute('data-action-url','/task/stop');
                stopBtn.setAttribute('data-action-message',`Stopping Task ${task.id}`);
                stopBtn.setAttribute('data-item',`${task.id}`);
                stopBtn.setAttribute('data-action-target',`${task.creator}`);
                stopBtn.setAttribute('onclick',"handleAction(this,'tasks-table','single')");

                const stopIcon = document.createElement('i');
                stopIcon.classList.add('fas', 'fa-stop', 'text-danger');
                stopBtn.appendChild(stopIcon);

                actions.appendChild(stopBtn);
            }

        }catch(error){console.log(error)}
        // console.log("Received data from tasks:", data);
    }else if (data.type === 'message'){
        const _console = document.getElementById("console");
        
        const li = document.createElement("li");
        const msgType = data.status;
        
        li.innerHTML = data.msg;
        li.classList.add(msgType)
        
        
        const firstChild = _console.firstChild;
        _console.appendChild(li); 
        _console.scrollTop = _console.scrollHeight;
    }
}

socket.on('update-client',(data)=>{
    updateClient(data);
})