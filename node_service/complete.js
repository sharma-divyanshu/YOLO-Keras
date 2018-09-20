const axios = require('axios');
const fs = require('fs');

var filelocation;

axios.get('http://localhost:3000/filepath')
    .then(function (response) {
    // handle success
    console.log(response.data);
    filelocation = response.data;
    let rawData = fs.readFileSync(filelocation.toString());
    let objectDetail = JSON.parse(rawData);
    let keys = Object.keys(objectDetail).toString();
    let values = objectDetail[keys];
    let unique = []
    let all = []
    for(let i=0; i<values.length; i++) {
        
        if (Object.keys(values[i]).length > 1) {
            for (let j = 0; j < Object.keys(values[i]).length; j++) {
                all.push(Object.keys(values[i])[j]);
            }
        }
        else {
            all.push(Object.keys(values[i]).toString())
        }
    }

    for(i = 0; i<all.length; i++) {
        if (!unique.includes(all[i])) { unique.push(all[i])}
    }

    console.log(all, " ------YOLO-------- ", unique);
    })
    .catch(function (error) {
    // handle error
    console.log(error);
    })
    .then(function () {
    // always executed
    });
