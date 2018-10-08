var {mongoose} = require('./db/mongoose');
var {Camera} = require('./models/camera');

Camera.updateOne({_id:"5ba8e3a85d94932e9473a70f",'chunklist._id':"5ba8e3b02b66482ecdf90cbb"},{$set:{'chunklist.$.subStatus':'Done','chunklist.$.objectList':['gfgfxg'],'chunklist.$.processed_path':'hjbfsj'}},(err,cam)=>{
    console.log(err,cam)
})

