var mongoose = require('mongoose');
var Schema = mongoose.Schema;
// var bycrypt = require('bycrypt') ; todo

var chunk=new Schema({
  path:{
    type:String,
    trim:true
  },
  time:{
    type:Number
  },
  objectList:{
    type:[{type:String}],
    default:[]
  },
  processed_path:{
    type:String,
    trim:true
  },
  subStatus:{
    type:String,
    default:"recorded"
  }
})

var Camera = mongoose.model('Camera',{
  name:{
    type: String,
    required: true,
    minlength: 1,
    trim: true
  },
  url:{
    type: String,
    required: true,
    minlength: 1,
    trim: true
  },
  uid:{
    type: Schema.Types.ObjectId,
    require: true,
    trim: true
  },
  privacy:{
    type:String,
    default : "private"
  },
  typeOfCam:{
    type: String,
    default: "Nest"
  },
  username:{
    type:String,
    trim: true
  },
  password:{
    type:String
  },
  chunklist:{
    type:[chunk],
    default:[]
  }
})
// {
// usePushEach:true
// });

module.exports = {Camera};
