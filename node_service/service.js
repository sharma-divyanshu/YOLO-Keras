var exec = require('child_process').exec;
var path = require('path');
var express = require('express');

var app = express();

app.listen(3000, function() {
    console.log("Running on port 3000")
})

var filelocation;
var pyPath = '../';

app.get('/yolo', yolo);

function yolo(req, res) { 

    console.log("Request received");
    function flagGen(args) {
        var flags = '';
        for (var a in args) {
          if (args.hasOwnProperty(a)) {
            if (typeof(pyArgs[a]) == 'string'){
              flags += " --" + a + ' ' + pyArgs[a];
            }
            else {
              if (pyArgs[a] == true)
                flags += ' --' + a;
            }
          }
        }
        return flags;
      }

    var pyArgs = {
        "file_path": '/home/divyanshu/Desktop/YOLO/output/'+req.query.filepath,
        "input": '/home/divyanshu/Desktop/YOLO/'+req.query.input,
        "output": '/home/divyanshu/Desktop/YOLO/'+req.query.output,
      };

    filelocation = pyArgs.file_path;

    var execstr = 'python3 ' + path.join(pyPath, 'yolo_video.py') + flagGen(pyArgs);
    var child = exec(execstr, function(error, stdout, stderr) {
    if (error) {
        console.log(stderr)
    }
    res.sendStatus(200);
});
    child.stdout.on('data', function(data) { 
        console.log(data.toString());
    } );
};

app.get('/filepath', returnFilepath);

function returnFilepath(req, res) {
    res.send('/home/divyanshu/Desktop/YOLO/output/texty.json')
    // res.send(filelocation.toString());
}