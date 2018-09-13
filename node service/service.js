var express = require('express');
var app = express();

app.listen(3000, function() {
    console.log('Server running on port 3000')
})

app.get('/yolo', call_yolo);

function call_yolo(req, res, args) {
    var spawn = require("child_process").spawn;
    var process = spawn('python3', ["../yolo_video.py", args ])
}