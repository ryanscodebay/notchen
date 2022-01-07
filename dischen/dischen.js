const Discord = require('discord.js');
const redis = require('redis');
const _ = require("lodash");

const bot = new Discord.Client();
const db_cli = redis.createClient(); //(port,host) to move from default

const mention_msg = require('./helpers/mention_msgs.js');
const reg_msg = require('./helpers/reg_msgs.js');
const invoked_cmd = require('./helpers/invoked_cmds.js');
const adm_cmd = require('./helpers/administrator_cmds.js');
//const utils = require('./helpers/utils.js');
const temp = require('./scratch/temp.js');

temp.lazy_script(db_cli);

require('dotenv').config();

var parent_id = process.env.PARENT_ID;
var son_id = process.env.SON_ID;
var prefix = process.env.PREFIX; //still deciding on this one..
var judge_call = false;

// move to persistent db
var elevated_roles = ['S.T.U.P.I.D','Second Admin','Moderator'];
const modules = ['card','hangman','judge_help'];
const module_names = ['card','hangman','judge_help'];

// SCRATCHPAD:
// if (!msg.channel.guild){return;}; //ignore private messages

//judge init
const handlers = {};
const commands = {};
const userMessageTimes = {};
modules.forEach((module, index) => {
    const moduleObject = new (require("./helpers/judge/" + module + '.js'))(modules);
    if(moduleObject) {
        console.log("Successfully initialized module", module);
        modules[index] = moduleObject;
        _.forEach(moduleObject.getCommands(), (commandObj, command) => {
            handlers[command] = moduleObject;
            commands[command] = commandObj;
            // map aliases to handlers as well
            if (commandObj.aliases) {
                commandObj.aliases.forEach(alias => {
                    handlers[alias] = moduleObject;
                    commands[alias] = commandObj;
                });
            }
        });
    } else {
        log.error("Couldn't initialize module", module);
    }
});

// Example: ((^|\s)!(card|price|mtr)|^!(hangman|standard|jar|help))( .*?)?(![^a-z0-9]|$)
const charPattern = _.escapeRegExp(prefix);
// split inline and non-inline commands into 2 patterns
const commandPattern = '(^|\\s)' + charPattern + '(' +
    Object.keys(commands).filter(cmd => commands[cmd].inline).map(_.escapeRegExp).join('|')
    + ')|^' + charPattern + '(' +
    Object.keys(commands).filter(cmd => !commands[cmd].inline).map(_.escapeRegExp).join('|')
    + ')';
const regExpPattern = `(${commandPattern})( .*?)?(${charPattern}[^a-z0-9]|$)`;
const regExpObj = new RegExp(regExpPattern, 'ig');

bot.on('ready', () => {
    console.log(`Logged in as ${bot.user.tag}!`);
});

//////// Database check-in 
db_cli.on('connect', function() {
  console.log('Connected to redis db');
});
db_cli.on('error', function(err) {
  console.log('Connection to redis db failed: ' + err);
});

//////// HANDLERS

//////// Invoke message helper
bot.on('message', msg => {
  // Don't loop
  // TODO: handlers for null content scenarios
  if (msg.author.id === son_id || !msg.content){
    //console.log('Dad said not to talk to myself or when I hear ghosts');
    return;
  }

  //mentions
  var content = msg.content;
  var sender = msg.author.id;

  if (content.includes(son_id)){
    mention_msg.mention_handler(msg,content,sender,db_cli);
  }

//////// TODO: Invoke command helper (need to solidify split on prefix)
  cmd_args = msg.content.match(/(?:[^\s"]+|"[^"]*")+/g);
  cmd = cmd_args.shift().toLowerCase();

  if (!cmd.startsWith(prefix)){
    return; //no command here
  }
 
  //clean up
  cmd = cmd.replace(prefix,''); //seems like someone made a better way

//////// Invoke administrative functions; will work on later
//  if (elevated_roles.includes(msg.member.highestRole.name)) {
//      // allowed
//      adm_cmd.admin_handler(cmd);
//  } else {
//      // not allowed
//  }

  function isJudgeCall(mod_name){
    if (msg.content.includes(mod_name)){judge_call = true;}
  }
  module_names.forEach(isJudgeCall);

  if (judge_call){
    reg_msg.judgebot(msg,cmd,charPattern,regExpObj,handlers,commands);
  }
  else {
    reg_msg.message_handler(msg,cmd,cmd_args,db_cli);
  }
});
 
bot.on('disconnected',() => {
  bot.login(process.env.BOT_TOK);
  console.log(`Disconnected. Relogging as ${bot.user.tag}!`);
});

bot.login(process.env.BOT_TOK);
