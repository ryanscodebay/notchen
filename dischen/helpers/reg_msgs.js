const api_reqs = require('./basic_api_reqs.js');
const _ = require('lodash');

require('dotenv').config();

var parent_id = process.env.PARENT_ID;
var son_id = process.env.SON_ID;
var prefix = process.env.PREFIX || '!'; //still deciding on this one..
var yandex_api_key = process.env.YANDEX_API_KEY;
//const temp = require('../scratch/temp.js');

module.exports = {
  //General message handling. TODO: Needs to be split/organized
  message_handler: function (msg,cmd,cmd_args,db_cli){
  
    var content = msg.content;
 
//////////// General user functions
    // Storing functions (testing)
    var func_db; //TODO: decide if using. which data we're dealing with
    var given_key; //user provided key
    var given_val; //TODO: decide if using. user provided value
    const cmdHandler = {}; //TODO: this seems hefty. will investigate
  
    //TODO: dear god find a way to make this better
    if (cmd === 'help'){
      var help_str = "Here's where I'd put my help manual.. IF I HAD ONE.\n(please contact my father, <@" + parent_id + ">, for more information for now)\n--------\nCurrent prefix: " + prefix + "\n--------\nCurrent commands:\n- help\n- ping\n- trn (translate)\n- ind (decision maker) (WIP)\n- card (card oracle)\n- hangman (mtg card hangman)\n- judge_help (mtg help blurb)\n\n\n\ne.g. " + prefix + "help brings up this blurb";
      msg.reply(help_str);
    }
  
    // Veto functionality (ham handed implementation atm)
    if (cmd === 'ind'){
      given_key = cmd_args.shift();

      //guard against no key given
      if (!given_key) {
        msg.reply('Please specify what type of decision. e.g. ind food');
        return;
      };

      //TODO: flesh this out you lazy fuck
      if (given_key === 'help') {
        msg.reply('cmds: add, remove, list, decide; e.g. food add <food>');
        return;
      }

      // TODO: add flag to specify if loaded to limit requests (?)
      // var loaded_key = ''; //move outside call
      // if(loaded_key == given_key){already loaded, just call functionality};
      // var loaded_key = given_key;

      // veto related variables
      var tmp_veto = []; //local array (not necessary atm since it's per call)
      var choice_list = ""; //string interpretation of list
      var choice; //stores the randomly generated choice
      var c; //iterator

      //wrapping functionality in a single members call for now
      //TODO: check for better solutions; clean this
      db_cli.smembers(given_key, function(err,res){
        if (err){
          console.log('Error in retrieving the veto data');
          throw error;
        }
        // console.log('Retrieved ' + given_key + ': ' + res);
        tmp_veto = res;

        for (c=0;c<tmp_veto.length;c++){
          choice_list += "- " + tmp_veto[c] + "\n";
        }

        //lazy, just grabbing the 3rd argument in the string
        switch(cmd_args[0]){
          //dirty; parse internal command
          //add value to the given set
          case 'add':
            db_cli.sadd(given_key,val=cmd_args[1].replace(/['"]+/g,''), function(err,res){
              if (err){
                console.log('Error in adding to the veto data');
                throw error;
              }
              if (res == 1){
                console.log('Added ' + val + ' to ' + given_key);
                msg.channel.send('Added ' + val + ' to ' + given_key);
              } else {
                msg.channel.send('Already in the list, ya doof');
              }
            });
            break;

          //remove value from the given set
          case 'remove':
            db_cli.srem(given_key,val=cmd_args[1].replace(/['"]+/g,''), function(err,res){
              if (err){
                console.log('Error in removing from the veto data');
                throw error;
              }
              if (res == 1){
                console.log('Removed ' + val + ' from ' + given_key);
                msg.channel.send('Removed ' + val + ' from ' + given_key);
              } else {
                msg.channel.send('Not in the list, ya doof');
              }
            });
            break;

          //list the set based on the given key
          case 'list':
            msg.channel.send("\nHere's the list of choices:\n" + choice_list);
            break;

          //simple random picker for the set retrieved with key
          case 'decide':
            choice = tmp_veto[Math.floor(Math.random() * tmp_veto.length)];
            msg.channel.send('You should go with ' + choice);
            break;

          //lists the set retrieved by key and makes a decision
          default:
            choice = tmp_veto[Math.floor(Math.random() * tmp_veto.length)];
            msg.channel.send("\nHere's the list of choices:\n" + choice_list);
            msg.channel.send('You should go with ' + choice);
            return;
        }
      });
    }
    // he's multilingual!
    // TODO: gonna replace with google translate prolly
    //if (content.includes("please translate")){
    if (cmd === 'trn') {
      //remove the command text from the translation
      content = content.substr(prefix.length + cmd.length + 1);
      api_reqs.translate(yandex_api_key,content,msg);
    }
  
    // test if he's awake
    if (cmd === 'ping') {
      msg.reply('a bit racist, but okay (pong)')
    }
//    if (cmd === 'lazy_exec') {
//      temp.lazy_script(db_cli);
//    }
//////// Data functions
  },

  judgebot: function (msg,cmd,charPattern,reg_exp_obj,handlers,commands){
    // generate RegExp pattern for message parsing
    const queries = msg.content.match(reg_exp_obj);
    //const lastMessage = userMessageTimes[msg.author.id] || 0;

    // check if the message...
    if (queries && // ...contains at least one command
        !msg.author.bot)// ...is not from a bot
    {
      // store the time to prevent spamming from this user
      //userMessageTimes[msg.author.id] = new Date().getTime();
  
      // only use the first 3 commands in a message, ignore the rest
      queries.slice(0, 3).forEach(query => {
          const command = query.trim().split(" ")[0].substr(prefix.length).toLowerCase();
          const parameter = query.trim().split(" ").slice(1).join(" ").replace(new RegExp(charPattern + '[^a-z0-9]?$', 'i'), '');
    
          const ret = handlers[command].handleMessage(command, parameter, msg);
          // if ret is undefined or not a thenable this just returns a resolved promise and the callback won't be called
          Promise.resolve(ret).catch(e => console.log('An error occured while handling', msg.content, ":", e.message));
      });
    }
  }
};
