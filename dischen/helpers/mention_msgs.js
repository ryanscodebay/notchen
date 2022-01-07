require('dotenv').config();

var parent_id = process.env.PARENT_ID;
var son_id = process.env.SON_ID;
var prefix = process.env.PREFIX || '!';
var yandex_api_key = process.env.YANDEX_API_KEY;
//const temp = require('../scratch/temp.js');

module.exports = {
  //General message handling. TODO: Needs to be split/organized
  mention_handler: function (msg,content,sender,db_cli){
    var in_loco = sender === parent_id ? 'Father' : '<@' + sender + '>'; 
  
    // General greeting
    //check if greeted; TODO: move to db; is it async? PROBABLY
    var g;
    var split_content = content.split(" ");
    //Greetings
    db_cli.smembers("greetings",function(err,res){
      if(!err){
        var greeted = false;
        for (g=0; g < res.length; g++){
          if (content.includes(res[g])) {
            greeted = true; 
            break;
          }
        }
        if(greeted){
          db_cli.srandmember("son_imgs",function(err,res){
             msg.channel.send("Hello " + in_loco + "! " + res);
          });
        }
       };
    });

//    if(sender === parent_id){} //only the owner can invoke the insult fx
    db_cli.smembers("insult_triggers",function(err,res){
      if(!err){
        var get_em = false;
        for (g=0; g < res.length; g++){
          if (content.includes(res[g])) {
            get_em = true; 
            break;
          }
        }
        if(get_em){ //GET EM, SON
          var victim_check = msg.mentions ? msg.mentions.users.first().id : "insult";
          if (victim_check == son_id || victim_check == parent_id){
            if(sender != parent_id){
              msg.channel.send("No, fuck you.");
            }
            return;
          }
          var victim = msg.mentions.users.first()+" ";
          db_cli.srandmember("insults",function(err,res){
            //using eval to interpolate more personalized insults
            msg.channel.send(eval('`'+res+'`'));
          });
        }
      };
    });
  

//        });

    //Profound thoughts
    db_cli.smembers("thought_array",function(err,res){
      if(!err){
        var thoughts = false;
        for (g=0; g < res.length; g++){
          if (content.includes(res[g])) {
            thoughts = true; 
            break;
          }
        }
        if(thoughts){
          db_cli.srandmember("kanye", function(err,res){
            if (err){
              console.log('Error in finding thoughts');
              throw error;
            }
            msg.channel.send(res);
          });
        }
      }
    });
  }
}
