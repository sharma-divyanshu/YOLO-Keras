var {mongoose} = require('./db/mongoose');
var {Camera} = require('./models/camera')
const AWS = require('aws-sdk');
var {yolo}=require('./service.js')

const config = {
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_DEFAULT_REGION,
  apiVersion: '2012-11-05',
};

const Consumer = require('sqs-consumer');

var sqs = new AWS.SQS({config}) ;

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
      cameraId=sp[3];
      console.log('--------------------',sp[0])
      console.log('#######################',sp[3])
      console.log(message.MessageAttributes.path.StringValue);
      yolo((message.MessageAttributes.path.StringValue),(err,data)=>{
      if (err){
        Camera.update({_id:cameraId,'chunklist._id':chunkId},
        {'$set':{'chunklist.$.subStatus':'Error'}},(err,cam)=>{
          done();
        })
      }
      else{
	console.log('++++++++++',cameraId);
	console.log('************',chunkId);
	      console.log('Dequeue Data: ----------------------------------------', data);
        Camera.updateOne({_id:cameraId,'chunklist._id':chunkId},
        {$set:{'chunklist.$.subStatus':'Done',
          'chunklist.$.objectList':data.list,
          'chunklist.$.processed_path':data.outputPath,
          'chunklist.$.duration':data.duration}},(err,cam)=>{
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
