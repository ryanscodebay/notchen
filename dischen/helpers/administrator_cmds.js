require('dotenv').config();

var parent_id = process.env.PARENT_ID
var son_id = process.env.SON_ID
var prefix = process.env.PREFIX //still deciding on this one..

module.exports = {
  //General message handling. TODO: Needs to be split/organized
  admin_handler: function (msg,parent_id,son_id,prefix){
    //authorized
  }
};
