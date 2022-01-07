const _ = require('lodash');
const Discord = require('discord.js');
require('dotenv').config();
var prefix = process.env.PREFIX;

class Help {
    constructor(modules) {
        this.commands = {
            judge_help: {
                aliases: [],
                inline: false,
                description: "Show this help text",
                help: 'This command allows you to explore the different functions and ' +
                    'features of your beloved judgebot. You can look up detailed descriptions ' +
                    'for a command by using `!help <command>`, like `!help card`.',
                examples: ["!help", "!help card"]
            }
        };
        this.location = 'https://github.com/bra1n/judgebot';
        this.modules = modules;
    }

    getCommands() {
        return this.commands;
    }

    handleMessage(command, parameter, msg) {
        let param = parameter.trim().toLowerCase().split(" ")[0];

        const embed = new Discord.RichEmbed({
            title: 'List of available commands',
            // thumbnail: {url: this.thumbnail},
            url: this.location
        });

        const commands = {};
        this.modules.forEach(module => {
            _.forEach(module.getCommands(), (commandObj, command) => {
                commandObj.name = command;
                commands[command] = commandObj;
                commandObj.aliases.forEach(alias => {
                    commands[alias] = commandObj;
                });
            })
        })

        if (parameter && commands[parameter]) {
            embed.setTitle('Command "'+prefix+commands[parameter].name+'"');
            embed.setDescription(commands[parameter].help);
            embed.addField('Examples', '`' + commands[parameter].examples.join('`\n`') + '`', true)
            if (commands[parameter].aliases && commands[parameter].aliases.length) {
                embed.addField('Aliases', '`!' + commands[parameter].aliases.join('`\n`!') + '`', true);
            }
        } else {
            let description = '';
            _.forEach(commands, (commandObj, command) => {
                if (command !== commandObj.name) return;
                description += ':small_blue_diamond: **!'+command+'**  '+commandObj.description+'\n';
            });
            embed.setDescription(description+'\n To learn more about a command, use `'+prefix+'help <command>`');
            embed.addField('Took the original code from here', 'Code was kinda bad and outdated, but there is good stuff\n :link: https://bots.discord.pw/bots/240537940378386442');
            embed.addField('Judgebot Source Code', ':link: https://github.com/bra1n/judgebot');
        }

        return msg.author.send('', {embed});
    }
}
module.exports = Help;
