var exec = require('child_process').exec;
var path = require('path');
const fs = require('fs');

var filelocation;
let unique = []
var pyPath = '/home/ubuntu/YOLO-Keras/';

let yolo = (filename,callback) => {

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

    let inputfile = path.basename(filename);
    let extension = path.extname(inputfile);
    let inputfilename = path.basename(inputfile, extension)

    var pyArgs = {
        "file_path": __dirname+'/output/'+inputfilename+'.json',
        "input": filename,
        "output": '/vigilandsrecordings/recordings/'+inputfilename+'.avi',
      };

    filelocation = pyArgs.file_path;

    var execstr = 'sudo python3 ' + path.join(pyPath, 'yolo_video.py') + flagGen(pyArgs);
    var child = exec(execstr, function(error, stdout, stderr) {
        if (error) {
            return stderr;
        }
    });

    child.stdout.on('data', function(data) {
        console.log(data.toString());
    } );

    child.stdout.on('end', function() {
	console.log("Processing ended");
        let objectDetail;
        let rawData = fs.readFileSync(filelocation.toString());
        if(rawData) {
            try {
                objectDetail = JSON.parse(rawData);
            } catch(e) {
		console.log(e);
            }
        };
        let keys = Object.keys(objectDetail).toString();
        let values = objectDetail[keys];
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
        console.log(unique);
        var data={
            list:unique,
            outputPath:pyArgs.output
        }
	console.log('------------------------------------------',data)
        callback(null,data)
    })
};

yolo('/home/ubuntu/YOLO-Keras/colourtag1.avi', function(err, data) {
	console.log('aoisdfoijsdiofjaoisdc=======', err, data);	
});

module.exports = {
    yolo
}
