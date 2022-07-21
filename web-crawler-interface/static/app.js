class UI {
    static runBtn = document.getElementById("run-btn");
    static scrollContent = document.getElementById("scroll-content");

    static updateLastRun(response, websiteId) {
        if (response.Condition === 1) {
            const completedRow = document.getElementById(websiteId);
            completedRow.children[2].innerHTML = "Completed";
            completedRow.style.color = 'green';
            completedRow.style.background = '#d3f9d8';
        }
        else if (response.Condition === -1) {
            const errorRow = document.getElementById(websiteId);
            errorRow.children[2].innerHTML = "Error";
            errorRow.children[4].innerHTML = UI.createSkipInputHTML();
            errorRow.style.color = 'red';
            errorRow.style.background = '#ffe3e3';
        }
    }

    static updateIncrement(res, websiteId) {
        const row = document.getElementById(websiteId);
        if(res.Increment === -1){
            row.children[4].innerHTML = "Inc. Feature Unavailable";
        }
        else {
            row.children[4].innerHTML = res.Increment;
        }

        let statusStr = `${res.State}`;
        if(res.City != '-'){
            statusStr += `, ${res.City}`;
        }
        if(res.Pin != '-'){
            statusStr += `, ${res.Pin}`;
        }
        console.log(statusStr);
        row.children[3].innerHTML = statusStr;
    }

    static createSkipInputHTML() {
        return `<input type="text" class="skip-input" name="skip" value="0">
        <div class="text-link">
            <a class="continue-text-link" href="#">Continue</a> / 
            <a class="stop-text-link" href="#">Stop</a>
        </div>`;
    }
}


class myAPI {
    static async post(url, data) {
        const response = await fetch(url,
            {
                method: 'POST',
                headers: { 'Content-type': 'application/json' },
                body: JSON.stringify(data)
            }
        );
        const json = await response.json();
        return json;
    }
    static async get(url) {
        const response = await fetch(url);
        const json = await response.json();
        return json;
    }
}


async function getData(url, websiteId) {
    let maxUpdateAttempt = 3;
    let updateAttempt = 0;

    while (true) {
        try {
            let res = await myAPI.get(url);
            console.log(res);
            if (res.Condition === 1 || res.Condition === -1) {
                console.log(`stopping update ${websiteId}`);
                break;
            }
            UI.updateIncrement(res, websiteId);
            updateAttempt = 0;
        }
        catch {
            updateAttempt += 1;
            console.log('kabhi bolde!');
            if(updateAttempt === maxUpdateAttempt){
                console.log(`stopping update ${websiteId}`);
                break;
            }
        }
    }
}


UI.runBtn.addEventListener('click', e => {

    let tickList = document.getElementsByClassName("row-tick");
    tickList = Array.from(tickList);
    let ran = false;
    tickList.forEach((checkBox) => {
        if (checkBox.checked) {
            const rowTicked = checkBox.parentElement.parentElement;
            const websiteId = rowTicked.id;
            const lastRun = rowTicked.children[2];

            if(!checkBox.disabled){
                ran = true;
                rowTicked.children[2].innerHTML = "Running..";
                // websites.website.push(tickedRowId);
                myAPI.post(`http://localhost:5000/run/${websiteId}`, { id: websiteId })
                    .then(res => UI.updateLastRun(res, websiteId));
                getData(`http://localhost:5000/update/${websiteId}`, websiteId);
                console.log("in forEach");
            }
            checkBox.disabled = true;
        }
    });

    if (ran === true) {

        tickList = document.getElementsByClassName("row-tick");
        tickList = Array.from(tickList);
        tickList.forEach((checkBox) => {
            if(!checkBox.disabled){
                const row = checkBox.parentElement.parentElement;
                row.children[3].innerHTML = '-';
            }
        });

        let tickHeadList = document.getElementsByClassName("table-tick");
        tickHeadList = Array.from(tickHeadList);
        tickHeadList.forEach((checkBox) => {
            const rowHead = checkBox.parentElement.parentElement;
            rowHead.children[3].innerHTML = 'Status';
        });
    }

    e.preventDefault();
});



UI.scrollContent.addEventListener('click', e => {
    if(e.target.className === 'stop-text-link'){
        const row = e.target.parentElement.parentElement.parentElement;
        console.log(row);
        row.children[0].children[0].disabled = false;
        row.children[0].children[0].checked = false;
        row.style.color = "";
        row.style.background = "";
        const websiteId = row.id;
        myAPI.get(`http://localhost:5000/rerender/${websiteId}`)
            .then(res => {
                row.children[2].innerHTML = res.LastRun;
                row.children[3].innerHTML = res.RowCount;
                row.children[4].innerHTML = '0';
            });
        e.preventDefault();
    }
    else if(e.target.className === 'continue-text-link'){

        const skip = e.target.parentElement.previousElementSibling.value;
        const row = e.target.parentElement.parentElement.parentElement;
        row.style.color = "";
        row.style.background = "";
        row.children[4].innerHTML = '0';
        row.children[2].innerHTML = "Running..";

        const websiteId = row.id;

        myAPI.post(`http://localhost:5000/continue/${websiteId}`, { skip: skip })
            .then(res => UI.updateLastRun(res, websiteId));
        getData(`http://localhost:5000/update/${websiteId}`, websiteId);
        
        e.preventDefault();
    }
    else if(e.target.className === 'table-tick') {
        const checkedState = e.target.checked;
        const tableElement = e.target.parentElement.parentElement.parentElement;
        const tickList = Array.from(tableElement.children);
        tickList.forEach((row) => {
            let checkbox = row.children[0].firstElementChild;
            if ((checkbox.className === 'row-tick') && !(checkbox.disabled)){
                if(checkedState)
                    checkbox.checked = true;
                else
                    checkbox.checked = false;
            }
        });
    }
});
