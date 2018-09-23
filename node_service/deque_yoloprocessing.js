var {mongoose} = require('./db/mongoose');
var {Camera} = require('./models/camera')
const AWS = require('aws-sdk');
var {yolo}=require('./service.js')


var sqs = new AWS.SQS({
    apiVersion: '2012-11-05',
    region:'us-west-2'
}) ;

AWS.config.update({accessKeyId: 'AKIAJLMYENI54EXJS7AA', secretAccessKey: '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'}) ;
const Consumer = require('sqs-consumer');

const app = Consumer.create({
  queueUrl: "https://sqs.us-west-2.amazonaws.com/398441892527/vigilandsqueue",
  AttributeNames:[
    "All"
  ],
  messageAttributeNames:[
    "All"
  ],
  // terminateVisibilityTimeout:true,
  handleMessage: (message, done) => {

      //done(err);
      //console.log(message.MessageAttributes.path.StringValue);
      chunkId=message.MessageAttributes.chunkId.StringValue;
      path=message.MessageAttributes.path.StringValue;
      sp=path.split('/');
      cameraId=sp[0];
      yolo((message.MessageAttributes.path.StringValue),(err,data)=>{
      if (err){
        Camera.update({_id:cameraId,'chunklist._id':chunkId},
        {'$set':{'chunklist.$.subStatus':'Error'}},(err,cam)=>{
          done();
        })
      }
      else{
	console.log('Dequeue Data: ----------------------------------------', data);
        Camera.update({_id:cameraId,'chunklist._id':chunkId},
        {'$set':{'chunklist.$.subStatus':'Done',
          'chunklist.$.objectList':data.list,
          'chunklist.$.processed_path':data.outputPath}},(err,cam)=>{
          console.log('Dequeue Done:=====================', cam, err);
	  done();
        })
        }
    })

   }
});

app.on('error', (err) => {
  console.log("Error",err);
});
app.on('processing_error',(err)=>{
  console.log("Processing Error",err);
})

app.start();
