# GameMusicalChairs
## About bot
This bot is designed for games like "musical chairs", that's why I called it that. It helps to organise games in private TG Groups(creating result table, banning, mutting and other)
## Where can I watch?
You can find it in Telegram https://t.me/StayLastbot (but all functions available only for admins)   
Or setup on your local machine
## Instrcutions for setupping
### First step
Clone this repository, create config.py in the root of project.  
Example for config.py:
```py
token = "asffanjakfn1312412nklasfnakf21414"
admins = [1181124378, 241532331]
```
### Second step
Install all libraries by this command in the root:
```
pip3 install -r requirements.txt
```
### Third step
Create directory "db" in the root and run this code, to create DataBase
```py
from data import db_session
from data.games import Game

db_session.global_init('db/bot.db')
db_ses = db_session.create_session()
game = Game()
db_ses.add(game)
db_ses.commit()
```
### Fourth step
Run project by this command in the root:
```
python3 app.py
```  
Great! The bot is running and you can check on your bot(whos token is used)
## Feedback
If you want to talk with me(who created this bot) or suggest changes you can find me in TG: https://t.me/Zeifert_Alex 
