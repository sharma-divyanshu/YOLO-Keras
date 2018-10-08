var mongoose = require('mongoose');

mongoose.Promise = global.Promise;
//mongoose.connect('mongodb://localhost:27017/Vigilands');
mongoose.connect('mongodb://52.33.188.212:27017/Vigilands');

module.exports = {mongoose};
