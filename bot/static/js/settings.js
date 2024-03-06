const showHide = (action='show',e=Array) =>{
  if (action === 'show'){
      e.forEach(el => {
          el.classList.remove('no-show')
          el.classList.add(action);
      });
  }

  else if (action === 'show-menu'){
      e.forEach(el => {
          el.classList.remove('no-show');
          el.classList.add(action);
      });
  }

  else if (action === 'no-show'){
      e.forEach(el => {
          el.classList.remove('show');
          el.classList.remove('show-menu');
          el.classList.add(action);
      });
  }
}

const selectAll = (checkbox, tableId, view, items) => {
    const table = document.getElementById(tableId);
    let rowCheckboxes;
    if (view === 'grid'){
        rowCheckboxes = table.querySelectorAll('li .item-header span .checkbox-row')
    }
    else{rowCheckboxes = table.querySelectorAll('.checkbox-row');}
   
    const updateHeaderCheckbox = () => {
      const areAllRowsChecked = Array.from(rowCheckboxes).every((rowCheckbox) => rowCheckbox.checked);
      if (view === 'grid'){
        Array.from(rowCheckboxes).forEach((rowCheckbox) => {
            if (rowCheckbox.checked){
                rowCheckbox.parentNode.style.zIndex = '3';
            }else{ 
                rowCheckbox.parentNode.style.zIndex = '-100';
            }
        });
      }
      checkbox.checked = areAllRowsChecked;
    };
  
    checkbox.addEventListener('change', function () {
      const isChecked = this.checked;
      for (const rowCheckbox of rowCheckboxes) {
        rowCheckbox.checked = isChecked;
      }
      updateHeaderCheckbox();
    });
  
    for (const rowCheckbox of rowCheckboxes) {
      rowCheckbox.addEventListener('change', updateHeaderCheckbox);
    }
  };

const selectSingle = (checkbox,view) => {
    if (view === 'grid'){
        const header = checkbox.parentNode.parentNode;
        const actions = header.querySelector('.actions-list');
        if (checkbox.checked){
            actions.classList.remove('no-show');
            actions.classList.add('show');
            checkbox.parentNode.style.zIndex = '3';
        }else{ 
            actions.classList.remove('show');
            actions.classList.add('no-show');
            checkbox.parentNode.style.zIndex = '-100';
        }
    }
}

const toogleGridActions = (toolTip) => {
    const header = toolTip.parentNode.parentNode;
    const actions = header.querySelector('.actions-list');
    if (actions.classList.contains('show')){
        actions.classList.remove('show');
        actions.classList.add('no-show');
    }else{
        actions.classList.remove('no-show');
        actions.classList.add('show');
    }
}

const handleAction = (btn,parent, actionType,view) => {
    const items = [];
    if (actionType === 'download'){
        const section = document.getElementById(parent);
        const hoverList = section.querySelector('.hover-list');
        const ul = hoverList.querySelector('.ul');

        ul.innerHTML = ``;

        const data = JSON.parse(btn.getAttribute('data-action-data').replace(/'/g, '"')) || {};
        
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                const value = data[key];
                
                const listItem = document.createElement('a');
                listItem.classList.add('list-item');
                listItem.setAttribute('href',value);
                listItem.innerHTML = key
                ul.appendChild(listItem);
            }
        }
  
        if (Object.keys(data).length > 0){
            showHide('show',[hoverList]);
    
            const close = hoverList.querySelector('.close');
            close.addEventListener('click',()=>{
                showHide('no-show',[hoverList])
            },{once:true})
        }
    }else{

        if (actionType === 'multiple'){
            const table = document.getElementById(parent);
            let rows;
            if (view === 'grid'){
                rows = table.querySelectorAll('.grid-row');
                for (const row of rows){
                    const checkbox = row.querySelector('.checkbox-row');
                    if (checkbox.checked){
                        items.push({
                            'item':row.getAttribute('data-item'),
                            'target':row.getAttribute('data-action-target'),
                            'grouped':row.getAttribute('data-grouped'),
                            'action-data':row.getAttribute('data-action-data'),
                            'action-category':row.getAttribute('data-action-category')
                        });
                    }
                }
            }
            else{
                rows = table.querySelectorAll('.table-body .table-row');
                for (const row of rows){
                    if (!row.classList.contains('table-bottom')){
                        const checkbox = row.querySelector('.table-cell .checkbox-row');
                        if (checkbox.checked){
                            items.push({
                                'item':row.getAttribute('data-item'),
                                'target':row.getAttribute('data-action-target'),
                                'grouped':row.getAttribute('data-grouped'),
                                'action-data':row.getAttribute('data-action-data'),
                                'action-category':row.getAttribute('data-action-category')
                            });
                        }
                    }
                }
            }

        }else{
            items.push({
                'item':btn.getAttribute('data-item'),
                'target':btn.getAttribute('data-action-target'),
                'grouped':btn.getAttribute('data-grouped'),
                'action-data':btn.getAttribute('data-action-data'),
                'action-category':btn.getAttribute('data-action-category')
            });
        }
        
        const action = btn.getAttribute('data-action');
        const actionUrl = btn.getAttribute('data-action-url');
        const actionMsg = btn.getAttribute('data-action-message');
        const auth =  document.getElementById(parent).getAttribute('data-auth')
        if (items.length > 0){
            let dialogue = actionType == 'single'? `Do you really want to ${action} this item?`
            : `Do you really want to ${action} ${items.length} items?`
           showDialogue(dialogue,action,actionUrl,items,actionMsg,auth);
        }
    }

};

const rows = document.querySelectorAll('.table-row');
rows.forEach(row => {
    row.addEventListener('click', e => {
        if (!e.target.closest('.actions') && !e.target.closest('.check-box')) {
            const actionUrl = row.getAttribute('data-action-url');
            if (actionUrl) {
                window.location.href = actionUrl;
            }
        }
    });
});

const showDialogue = (dialogue,action=String,actionUrl=String,items=Array,actionMsg=String,auth=String) => {
  const dialogueHolder = document.getElementById('dialogue-holder');
  const dialogueMsg = dialogueHolder.querySelector('.dialogue-msg');
  const dialogueAction = dialogueHolder.querySelector('.dialogue-action');
  
    for (const item of items){
        if (item.grouped === 'true'){
            toogleLoader('show', `Deleting of grouped items not allowed, change to individual items firs!`,'error');
            setTimeout(()=> toogleLoader('no-show'),3000);
            return;
        }
    }

    dialogueMsg.textContent = dialogue;
    dialogueAction.textContent = 'Yes';
  
    showHide('show',[dialogueHolder]);
    
    const closeButton = dialogueHolder.querySelector('.close');
    closeButton.addEventListener('click', () => {
        showHide('no-show',[dialogueHolder]);
    },{once:true});
    
    dialogueAction.addEventListener('click', () => {
        const nextAction = action === 'stop'? 'no-reload':'reload'
        sendRequest('POST',action,actionUrl,actionMsg,{'data':items},auth,nextAction)
        showHide('no-show',[dialogueHolder]);
    },{once:true});
}

const sendRequest = async(method,action,actionUrl,actionMsg,body,auth,nextAction,nextActionUrl,
    headers={'content-type':'application/json'}) =>{
  toogleLoader('show', `${actionMsg}  &nbsp;<i class="fas fa fa-gear icon spinner"></i>`);
  try {
    let responseData;
    if (auth){headers.authorization=`Bearer ${auth}`};
    const requestParams = method === 'POST'? {
        method: method,
        body: JSON.stringify(body),
        headers:headers
    }:{
        method: method
    }
    const response = await fetch(actionUrl, requestParams);

    if (response.ok) {
        responseData = await response.json();
        toogleLoader('show', `${responseData.msg}  &nbsp;<i class="fas fa-check icon"></i>`,'success');
        
        setTimeout(() => {
            setTimeout(()=> toogleLoader('no-show'),2000);
            if (nextAction && nextAction == 'reload'){
                window.location.reload();
            }
            else if (nextAction && nextAction == 'redirect'){
                window.location.href = nextActionUrl;
            }
        } , 1000);
    } else {
        if (response.status < 401) {
            responseData = await response.json();
            console.error(`${action} failed:`, responseData.msg);
            toogleLoader('show', `${responseData.msg}`,'error');
        } else {
            toogleLoader('show', `${action} failed, internal server error`,'error');
            console.error(`${action} failed:`, response.statusText);
        }
        setTimeout(()=> toogleLoader('no-show'),3000);
    }
    
} catch (error) {
    console.error('Error occurred:', error);
}
}

const toogleLoader = (type,msg=String,status=String) =>{
    const loader = document.querySelector('#loader');
    const msgBox = loader.querySelector('.message');
    if (type == 'show'){
        msgBox.innerHTML = ``;
        msgBox.style.color = '#f1f1f1'
        if(status == 'success'){msgBox.style.color = '#03ab8c'}
        else if(status == 'error'){msgBox.style.color = '#fa1e59'}
        msgBox.innerHTML = msg;
        loader.style.top = '10px';
    }else{
        loader.style.top = '-1000px';
    }
} 



const searchInit = (btn) => {
    const page = btn.getAttribute('data-page');
    const order = btn.getAttribute('data-order');
    
    const searchDisplay = document.querySelector('#search-display');
    searchDisplay.classList.add('show');

    const searchForm = searchDisplay.querySelector('#search-form');
    const searchSelect = searchForm.querySelector('select');
    const more = searchForm.parentNode.querySelector('.search-content .bottom .actions #more');

    searchSelect.addEventListener('change',(e)=>{
        const searchInput = searchForm.querySelector('input');
        const prompt = e.target.value === 'sku'? `Enter an ${e.target.value}`:`Enter a ${e.target.value}`
        searchInput.setAttribute('placeholder',`${prompt} here and click search`);
        
        const dataList = searchForm.parentNode.querySelector('.search-content .contents ul');
        dataList.innerHTML = '';
        dataList.classList.remove('show');

        more.classList.remove('show');
        more.setAttribute('data-offset','0')
    })

    searchForm.addEventListener('submit', async (e)=>{
        e.preventDefault();
        const searchOffset = 0;
        await search(searchForm,searchOffset,page,order);
    })

    more.addEventListener('click',async(e)=>{
        const searchOffset = parseInt(e.target.getAttribute('data-offset')) || 0;
        await search(searchForm,searchOffset,page,order);
    })

    const cancelBtn = searchDisplay.querySelector('.search-content #cancel');
    cancelBtn.addEventListener('click',()=>{
        searchDisplay.classList.remove('show');
    },{once : true})
}

const search = async (searchForm,searchOffset,page,order) =>{
    let responseData;

    const formData = new FormData(searchForm);
    const searchContent = formData.get('search-content');
    const searchField = formData.get('search-field');

    const loader = searchForm.parentNode.querySelector('.search-content .bottom .loading');
    const more = searchForm.parentNode.querySelector('.search-content .bottom .actions #more');
    const dataList = searchForm.parentNode.querySelector('.search-content .contents ul');

    if (searchOffset === 0){
        dataList.innerHTML = ''
        dataList.classList.remove('show');
    }

    let collection = page;
    if (page === 'price-drops'){
        collection = 'price_drops'
    }

    // const {success,result} = await getSearch(collection,searchField,searchContent,order);
    // console.log(result)

    loader.classList.add('show');
    if (searchField === 'date' && !['/', '-'].some(char => searchContent.includes(char))) {
        loader.innerHTML = 'Wrong date format: supported format (yyyy-mm-dd)';
        return;
    }

    const requestParams = {
        method:'POST',
        body:JSON.stringify({data:{
            searchType:collection,
            searchField:searchField,
            searchContent:searchContent,
            order:order,
            searchOffset:searchOffset
        }}),
        headers:{
            'Content-Type':'application/json'
        }
    }

    const response = await fetch('/search', requestParams);
    if (response.ok) {
        responseData = await response.json();
        const results = responseData.results;
        searchOffset = responseData.nextOffset;

        loader.innerHTML = `Retrieved ${results.length} items from ${searchContent}`
        
        if (searchOffset === 0){
            dataList.innerHTML = ''
        };
            
        for (const data of results){
            const li = document.createElement('li');

            for (const e of [{class:'title',element:'div',text:data[`${searchField}`]},
            {class:'sub-title',element:'div',text:data.location},
            {class:'sub-text',element:'div',text:data.store},
            {class:'action',element:'a',text:'view price drop'}]){

                const element = document.createElement(e.element);
                element.classList.add(e.class);
                element.innerHTML = e.text;

                if( e.class === 'action'){
                    element.setAttribute('href',`/price-drops?action=view-item&store=${data.store}&item=${data.id}`);
                    element.setAttribute('target','blank')
                }
                li.appendChild(element);
            }

            dataList.appendChild(li);
        }

        setTimeout(()=>{

            setTimeout(()=>{loader.classList.remove('show')},1000);
            dataList.classList.add('show');
            if (searchOffset > 0) {
                more.classList.add('show');
                more.setAttribute('data-offset',searchOffset);
            }else{
                more.classList.remove('show');
            }

        },1100);
        console.log(responseData);
    }else{
        if (response.status < 401){
            responseData = await response.json();
            console.error(`${action} failed:`, responseData.msg);
            loader.innerHTML = `${responseData.msg}`
        }else{
            loader.innerHTML = `Error getting data`;
            console.error(response.statusText);
        }
    }
}


async function toggleButton(destination) {
    const button = document.querySelector('.toggle-btn');
    
    if (destination == 'external'){
        const action = button.getAttribute('data-action');
        const action_url = button.getAttribute('data-action-url');
        const action_status = button.getAttribute('data-action-status');
        const action_key = button.getAttribute('data-action-key');
        const creator = button.getAttribute('data-action-creator');

        const requestParams = {
            method:'POST',
            body:JSON.stringify({
                'action':action,
                'status':action_status,
                'key':action_key,
                'creator':creator
            }),
            headers:{
                'Content-Type':'application/json'
            }
        }
        const response = await fetch(action_url, requestParams);
        if (response.ok){
            button.classList.toggle('active');
        }
        console.log(response.body)

        if (button.classList.contains('negative')){
            button.setAttribute('data-action-status','no');
        }else{
            button.setAttribute('data-action-status','yes');
        }
        button.classList.toggle('negative');

    }else{
        button.classList.toggle('active');
    }
  }


