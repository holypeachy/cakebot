# 🍰 CakeBot
A friend was starting a discord server and I wanted to make a custom bot for it. I add features based on what my friend wants and things I think would be neat to have.  
> 🙏 Huge thanks to [Krayon](https://github.com/lcsabi) for contributing from time to time, and for always helping me when I'm stuck with python or some issue I can't solve. I promise I'll learn to use a proper commit naming scheme soon.
### ⚠️ Warning: This bot has a few NSFW (18+) commands, do not use them if you are a minor.  

## Important Notes:
- For those who want to fork the code [click here](https://github.com/holypeachy/cakebot#for-reference-here-are-all-the-apis-im-currently-using).
- For OAuth2 / Bot Permissions [click here](https://github.com/holypeachy/cakebot#OAuth2).
- Keep in mind that this is a work in progress. The main branch is the "production" branch, the code here should be mostly bug free. If there is a bug it will quickly be caught because my bot is always running.  
- Even though the bot was only intended for 1 Discord server, it is written to support multiple servers.
- Every update that a property is added to the Server class, the bot will break and not start. You'll have to manually add the key and a value to the json file for it to load. I need to fix this soon because it has become quite a nuisance.

## Features (As of October 2, 2023)
For information on how some of these features can be modified read through the [commands list](https://github.com/holypeachy/cakebot#commands).
### Fun
- The bot can repeat something you say using command.
- Random Chuck Norris jokes.
- Random cat image.
- Cowboy standoff minigame.
- NSFW Commands (only available when you DM the bot):
  - Look up a adult film star, which will show you an image and some information about them.
  - Look up professional image from a category you type in.
- The bot will answer to a few "secret" phrases.
  - "hi cake" or "hello cake"
  - "cake help"
  - "good cake"

![2023-10-03_00-47](https://github.com/holypeachy/cakebot/assets/89674775/b35f1961-0202-4291-b326-cc2bea0144f2)

### Cool
- Get the current weather of anywhere in the world.
- "Confessions" through a slash command allows users to send an anonymous message to a pre-set channel.
- Can see all server roles by running a command.
- Get the best 10 Steam deals every Saturday.
- Can send admins suggestions on how to improve the server.
- Get the best current deals on Steam, or search game stores for the best deal on a game of your choosing.

![2023-10-03_00-46](https://github.com/holypeachy/cakebot/assets/89674775/032476ec-5eb8-433e-924b-b885604122f6)

### Admin Tools
- Can create embeds with a title and content (Meant for announcements and such).
- Slash command to create polls.
- Command to delete n number of messages.
- Role select. The bot sends out a message with all roles users can pick from, and using emojis they can select what roles they want. If any changes are done to the roles, the "role select" messages update automatically.
- Admins can run a command to get the best 10 steam deals. Running the command will set the bot to automatically send a message with 10 steam deals every Saturday at 10am. This can be disabled running another command.
- Welcome messages (37 unique messages).
- Goodbye messages (30 unique messages).
- Simple audit logs.

![2023-10-03_00-42](https://github.com/holypeachy/cakebot/assets/89674775/f74f7618-6bc3-42fd-a47f-2e5ae7a30426)

## Commands
Here is a list of all the commands available as of October 2, 2023. Non-admins will not see the admin command when they invoke the help command.
  
![image](https://github.com/holypeachy/cakebot/assets/89674775/78ccca68-a306-415d-96cb-edaea0d33bd8)


## Developer Commands
- dev_shutdown
- dev_saveservers

## Notes for anyone who wants to fork the code:
First I would like to apologize for the current state of this code base, the bot has grown quite a bit (as of writing this: 1300 lines) and I am yet to take steps to organize the code into separate files. Although I think you'll find that it is well organized.
- The major script is newbot.py not bot.py, the latter is depricated.
- Make sure to create a servers.json and a config.py. Add the following content to the config.py:
```
TOKEN = 'your_token_here' # Discord Bot's token
COMMAND_PREFIX = '!' # The prefix for the bot's commands
RAPIAPI_KEY = 'your_api_key_here'
```
- We use poetry to handle dependecies (thanks Krayon for letting me know this exists):
  - ```pip install poetry```
  - Then, in the project run ```poetry install``` to install all required dependencies.
- The way I determine if someone is an admin is if they can manage channels.
- I use RapiAPI for all APIs and all of the ones I use are free. So if you want to use the bot you can go to the [site](https://rapidapi.com/) and subscribe to all the APIs I used here, which you'll see in the beginning of the newbot.py script.
- The testing scripts contain some code I'm experimenting with. As of writing this, testing.py contains the beginnings of a music playing functionality (the file itself is its own standalone bot). testing2.py is where I test the APIs.

### For reference, here are all the APIs I'm currently using
![image](https://github.com/holypeachy/cakebot/assets/89674775/1e9c0204-8320-437f-a30f-48b72c486199)

## OAuth2
⚠️ Make sure to move the CakeBot role higher in the role list than the miscellaneous roles (age, games, etc.) because role select will not work properly.  

Here are all the permission the bot will need:
![image](https://github.com/holypeachy/cakebot/assets/89674775/51d04d44-9486-4428-8efd-ee38a75cadf5)
