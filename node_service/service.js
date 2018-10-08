var exec = require('child_process').exec;
var path = require('path');
const fs = require('fs');
var probe = require('node-ffprobe');

var filelocation;
let unique = []
var pyPath = '/home/ubuntu/vigilands/YOLO/';

let yolo = (filename,callback) => {

    console.log("Python service called. Filepath: ", filename);
    if(!fs.existsSync(filename)) {
        console.log("File does not exist");
        callback("File does not exist at the input location",{error: "error"})
    }
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

    // console.log(pyArgs);

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

    let outputfilename = '/vigilandsrecordings/recordings/processed/p-'+inputfilename+'.ts';
	console.log("Processing ended");
        let objectDetail;
        let rawData = fs.readFileSync(filelocation.toString());
        if(rawData) {
            try {
                objectDetail = JSON.parse(rawData);
            } catch(e) {
                console.log("JSON empty.", e);
                var empty_data={
                    list:[],
                    outputPath:outputfilename
                }
                return callback(null, empty_data)
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
        unique = [];

        for(i = 0; i<all.length; i++) {
            if (!unique.includes(all[i])) { unique.push(all[i])}
        }

        if (fs.existsSync(outputfilename)) {
            probe(outputfilename, function(err, probeData) {
                var data={
                    list:unique,
                    duration: probeData.streams[0].duration,
                    outputPath:outputfilename
                }
                console.log('------------------------------------------',data)
                callback(null,data)
            });
        }
        else (callback("No file", empty_data));

        // console.log(unique);
    })
};

//yolo('/home/ubuntu/YOLO-Keras/videoplaybacklq.mp4', function(err, data) {
//	console.log('aoisdfoijsdiofjaoisdc=======', err, data);});

module.exports = {
    yolo
}