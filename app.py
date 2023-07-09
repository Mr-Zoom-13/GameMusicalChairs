from aiogram import Bot, Dispatcher, executor, types
from config import *
from data import db_session
from data.games import Game
from data.members import Member
from data.banned import Banned
import asyncio

bot = Bot(token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['get_result'])
async def get_result(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        result = 'Рейтинговая таблица:\n'
        num = 0
        retired = ['' for i in range(game.current_retired)]
        for member in game.members:
            if member.status == "Retired" or member.status == 'Last':
                if member.reason != 'Время на выбор истекло':
                    retired[
                        member.retired_number - 1] = '@' + member.username + ' | Причина поражения: ' + member.reason + ' | Выбрано: ' + str(
                        member.chosen_number)
                else:
                    retired[
                        member.retired_number - 1] = '@' + member.username + ' | Причина поражения: ' + member.reason
            else:
                num += 1
                result += str(num) + '. ' + member.username + '\n'
        retired = retired[::-1]
        for i in range(len(retired)):
            if retired[i]:
                num += 1
                result += str(num) + '. ' + retired[i] + '\n'
        await message.answer(result)


@dp.message_handler(commands=['info'])
async def info(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        await message.answer(
            f"Лимит чисел: {game.x}\nВремя, отведенное на раунд: {game.time_per_round}\nСчастливое число(-1 - нет): {game.lucky_number}\nМакс. кол-во выбывших: {game.limit_retired}\nСтатус игры: {game.status}")


@dp.message_handler(commands=['unmute_all'])
async def unmute_all(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        for member in game.members:
            if member.tg_id:
                await bot.restrict_chat_member(game.group_id, member.tg_id,
                                               can_send_messages=True)
        await message.reply("Со всех пользователей был снят мут!")


@dp.message_handler(commands=['set_limit_numbers'])
async def set_limit_numbers(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        x = int(message.text.split()[1])
        if x > len(game.members) - 1:
            await message.reply(
                f"Введен недопустимый лимит! (Текущее число выживших: {len(game.members) - game.current_retired})!")
        else:
            game.x = x
            db_ses.commit()
            await message.reply("Новый лимит успешно установлен!")


@dp.message_handler(commands=['add_members'])
async def add_members(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        persons = message.text.split()[1:]
        for username in persons:
            member = Member()
            member.username = username[1:]
            game.members.append(member)
            db_ses.add(member)
            db_ses.commit()
        game.set_x()
        db_ses.commit()
        await message.reply("Текущие пользователи были успешно добавлен(-ы) в игру!")


@dp.message_handler(commands=['del_members'])
async def del_members(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        persons = message.text.split()[1:]
        for username in persons:
            for member in game.members:
                if member.username == username[1:]:
                    db_ses.delete(member)
                    db_ses.commit()
        game.set_x()
        db_ses.commit()
        await message.reply("Текущие пользователи были успешно удален(-ы) из игры!")


@dp.message_handler(commands=['clear_members'])
async def clear_members(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        for member in game.members:
            db_ses.delete(member)
            db_ses.commit()
        game.set_x()
        db_ses.commit()
        await message.reply("Все участники были удалены из игры!")


@dp.message_handler(commands=['ban'])
async def ban_members(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        persons = message.text.split()[1:]
        for username in persons:
            banned = Banned()
            banned.username = username[1:]
            db_ses.add(banned)
            db_ses.commit()
        await message.reply("Текущие пользователи были успешно заблокирован(-ы)!")


@dp.message_handler(commands=['unban'])
async def unban_members(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        persons = message.text.split()[1:]
        for username in persons:
            persons = db_ses.query(Banned).filter(Banned.username == username[1:]).all()
            for person in persons:
                db_ses.delete(person)
            db_ses.commit()
        await message.reply("Текущие пользователи были успешно разблокирован(-ы)!")


@dp.message_handler(commands=['set_lucky_number'])
async def set_lucky_number(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        game.lucky_number = int(message.text.split()[1])
        db_ses.commit()
        await message.reply("Счастливое число установлено!")


@dp.message_handler(commands=['set_time'])
async def set_time(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        game.time_per_round = int(message.text.split()[1])
        db_ses.commit()
        await message.reply("Время, отведенное на раунд, установлено!")


@dp.message_handler(commands=['set_limit_retired'])
async def set_limit(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        game.limit_retired = int(message.text.split()[1])
        db_ses.commit()
        await message.reply("Максимальное число выбывших игроков установлено!")


@dp.message_handler(commands=['echo'])
async def echo_bot(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        db_ses.commit()
        try:
            await bot.send_message(game.group_id, ' '.join(message.text.split()[1:]))
        except BaseException as error:
            game.group_id = int(error.args[0].split()[-1][:-1])
            db_ses.commit()
            await bot.send_message(message.from_user.id, "Бот готов к работе!")


@dp.message_handler(content_types=['new_chat_members'])
async def add_to_group_id(message: types.Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id
    db_ses = db_session.create_session()
    game = db_ses.query(Game).all()[-1]
    for chat_member in message.new_chat_members:
        if chat_member.id == bot_id:
            if message.from_user.id in admins:
                game.group_id = message.chat.id
                db_ses.commit()
            else:
                await bot.leave_chat(message.chat.id)
        elif db_ses.query(Banned).filter(Banned.username == chat_member.username).first() or (
                not db_ses.query(Member).filter(
                    Member.username == chat_member.username and Member.game_id == game.id).first()):
            await bot.kick_chat_member(message.chat.id, chat_member.id)
        else:
            member = db_ses.query(Member).filter(
                Member.username == chat_member.username and Member.game_id == game.id).first()
            member.tg_id = chat_member.id
            db_ses.commit()


@dp.message_handler(commands=['start_round'])
async def start_round(message: types.Message):
    if message.from_user.id in admins:
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        if not game.x or not game.limit_retired or not game.time_per_round:
            await message.answer('Заполнены не все параметры!')
            return
        game.status = 'active'
        db_ses.commit()
        await bot.send_message(game.group_id, "Начали!")
        await asyncio.sleep(game.time_per_round)
        db_ses = db_session.create_session()
        game = db_ses.query(Game).all()[-1]
        if game.status == 'active':
            game.status = 'inactive'
            db_ses.commit()
            for member in game.members:
                if not member.chosen_number:
                    member.status = "Retired"
                    member.reason = 'Время на выбор истекло'
                    game.current_retired += 1
                    member.retired_number = game.current_retired
                    await bot.restrict_chat_member(game.group_id, member.tg_id,
                                                   can_send_messages=False)
                    db_ses.commit()
            await bot.send_message(game.group_id, make_results())
            game.set_x()
            game.lucky_number = -1
            game.time_per_round = None
            game.limit_retired = None
            db_ses.commit()
            db_ses.commit()


@dp.message_handler()
async def get_answers(message: types.Message):
    db_ses = db_session.create_session()
    game = db_ses.query(Game).all()[-1]
    if game.status == 'active' and message.chat.id == game.group_id:
        for member in game.members:
            if member.username == message.from_user.username:
                if member.chosen_number:
                    member.status = "Retired"
                    member.reason = "Больше одного ответа"
                else:
                    try:
                        chosen_number = int(message.text)
                        if chosen_number < 1 or chosen_number > game.x:
                            member.chosen_number = message.text
                            member.status = "Retired"
                            member.reason = "Номер недоступен"
                        elif not game.check_number(chosen_number):
                            member.chosen_number = message.text
                            member.status = "Retired"
                            member.reason = "Номер уже занят"
                        else:
                            member.chosen_number = message.text
                            game.current_alives += 1
                            member.retired_number = game.current_alives
                        db_ses.commit()
                    except ValueError:
                        member.chosen_number = message.text
                        member.status = 'Retired'
                        member.reason = "Некорректный ответ"
                        db_ses.commit()

                if member.status == 'Retired':
                    if member.reason != "Время на выбор истекло":
                        game.current_retired += 1
                        member.retired_number = game.current_retired
                    db_ses.commit()
                    if game.current_retired >= game.limit_retired:
                        game.status = 'inactive'
                        db_ses.commit()
                        await bot.send_message(game.group_id, make_results(auto=True))
                        game.set_x()
                        game.lucky_number = -1
                        game.time_per_round = None
                        game.limit_retired = None
                        db_ses.commit()
                    await bot.restrict_chat_member(game.group_id, message.from_user.id,
                                                   can_send_messages=False)


def make_results(auto=False):
    db_ses = db_session.create_session()
    game = db_ses.query(Game).all()[-1]
    if game.lucky_number != -1:
        lucky_number = ''
    if auto:
        alives = []
    else:
        alives = ['' for i in range(game.current_alives)]
    retired = ['' for i in range(game.current_retired)]
    for member in game.members:
        if member.status == 'Alive':
            if game.lucky_number != -1 and int(member.chosen_number) == game.lucky_number:
                lucky_number = member.username
            if auto:
                alives.append('@' + member.username)
            else:
                alives[member.retired_number - 1] = '@' + member.username
        elif member.status == 'Retired':
            if member.reason != 'Время на выбор истекло':
                retired[
                    member.retired_number - 1] = '@' + member.username + ' | Причина поражения: ' + member.reason + ' | Выбрано: ' + str(
                    member.chosen_number)
            else:
                retired[
                    member.retired_number - 1] = '@' + member.username + ' | Причина поражения: ' + member.reason
            member.status = 'Last'
        member.chosen_number = None
        member.retired_number = None
        db_ses.commit()
    if game.lucky_number != -1:
        result = 'Итоги раунда:\nСчастливый номер выбрал: @' + lucky_number + '\nВыжившие: \n'
    else:
        result = 'Итоги раунда:\nВыжившие: \n'
    num = 0
    for i in range(len(alives)):
        if alives[i]:
            num += 1
            result += str(num) + '. ' + alives[i] + '\n'
    result += "Выбывшие: \n"
    num = 0
    for i in range(len(retired)):
        if retired[i]:
            num += 1
            result += str(num) + '. ' + retired[i] + '\n'
    return result


if __name__ == '__main__':
    db_session.global_init('db/bot.db')
    executor.start_polling(dp)
