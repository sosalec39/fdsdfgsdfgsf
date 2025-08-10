import asyncio
import json
import os
import random
import string
from collections import defaultdict

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

ChannelId = -1002546059199
AdminId = 6343410878
BotToken = '8072654116:AAEabYzPWHfXFMqaZHV8SbesvIZEuB3omUc'


class AdvStates(StatesGroup):
    adv = State()
    city = State()
    brand = State()
    model = State()
    year = State()
    price = State()
    bargain = State()
    condition = State()
    malfunctions = State()
    broken_state = State()
    broken_details = State()
    contacts = State()
    engine = State()
    engine_capacity = State()
    power = State()
    gearbox = State()
    wheel = State()
    mileage = State()
    drive = State()
    moderation = State()


bot = Bot(BotToken, parse_mode="HTML")
router = Router()

def generate_random_id(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add('➕ Загрузить объявление')
    username = f'@{message.from_user.username}' if message.from_user.username else message.from_user.first_name
    await message.answer_photo(photo=open('img/main.jpg', 'rb'),
                              caption=f'<b>Здравствуйте, {username}, мы рады видеть вас у нас в комьюнити автоSale.</b>',
                              reply_markup=kb)


@router.message(Command("adv"))
@router.message(Text('➕ Загрузить объявление'))
async def upload_adv(message: types.Message, state: FSMContext):
    state_info = await state.get_state()
    data = await state.get_data()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add('🏙️ Город')
    kb.add('🚗 Модель авто', '💸 Цена авто')
    kb.add('📝 Характеристики')
    kb.add('⚙️ Состояние', '⚠️ Неисправности')
    if len(data) >= 0 and data.get('contacts'):
        kb.add('➡️ Опубликовать')
    if not message.from_user.username:
        kb.add('📲 Контакты')
    else:
        await state.update_data(contacts=f"@{message.from_user.username}")
    if state_info:
        await message.answer('✅', reply_markup=kb)
    else:
        await message.answer('🚗')
        await message.answer('<b>Заполните объявление.</b>', reply_markup=kb)
    await state.set_state(AdvStates.adv)


@router.message(Text('🏙️ Город'))
async def adv_city(message: types.Message, state: FSMContext):
    await message.answer('🏙️')
    await message.answer('<b>Введите ваш город/поселок.</b>')
    await state.set_state(AdvStates.city)


@router.message(Text('🚗 Модель авто'))
async def adv_model(message: types.Message, state: FSMContext):
    await message.answer('🚗')
    await message.answer('<b>Введите марку вашего автомобиля.</b>')
    await state.set_state(AdvStates.brand)


@router.message(Text('💸 Цена авто'))
async def adv_price(message: types.Message, state: FSMContext):
    await message.answer('💸')
    await message.answer('<b>Введите цену для вашего автомобиля.</b>')
    await state.set_state(AdvStates.price)


@router.message(Text('⚙️ Состояние'))
async def adv_condition(message: types.Message, state: FSMContext):
    await message.answer('⚙️')
    await message.answer('<b>Введите описание состояния вашего автомобиля.</b>')
    await state.set_state(AdvStates.condition)


@router.message(Text('⚠️ Неисправности'))
async def adv_malfunctions(message: types.Message, state: FSMContext):
    await message.answer('⚠️')
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Отсутствуют', callback_data='Отсутствуют'))
    await message.answer('<b>Введите описание неисправностей вашего автомобиля.</b>', reply_markup=kb)
    await state.set_state(AdvStates.malfunctions)


@router.message(Text('📲 Контакты'))
async def adv_contacts(message: types.Message, state: FSMContext):
    await message.answer('📲')
    await message.answer('<b>Введите ваши контакты для связи, так же можете указать контакт ссылкой.</b>')
    await state.set_state(AdvStates.contacts)


@router.message(Text('📝 Характеристики'))
async def adv_engine(message: types.Message, state: FSMContext):
    await message.answer('📝')
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Бензин', callback_data='Бензин'),
           types.InlineKeyboardButton(text='Дизель', callback_data='Дизель'))
    kb.add(types.InlineKeyboardButton(text='Электродвигатель', callback_data='Электродвигатель'))
    await message.answer('<b>Какой у вас двигатель?</b>', reply_markup=kb)
    await state.set_state(AdvStates.engine)


@router.message(Text('➡️ Опубликовать'))
async def adv_publish(message: types.Message, state: FSMContext):
    await message.answer('➡️')
    await message.answer('<b>Отправьте мне фото/видео в 1 сообщении.</b>\nМожно загрузить до 10 фото.', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AdvStates.moderation)


@router.message(AdvStates.city)
async def adv_city_state(message: types.Message, state: FSMContext):
    await state.update_data(citi=message.text)
    await message.answer('<b>Город обновлен.</b>')
    await upload_adv(message, state)


@router.message(AdvStates.brand)
async def adv_brand_state(message: types.Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer(f'<b>Введите модель автомобиля марки {message.text}.</b>')
    await state.set_state(AdvStates.model)


@router.message(AdvStates.model)
async def adv_model_state(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer(f'<b>Введите год вашей модели машины {message.text}.</b>')
    await state.set_state(AdvStates.year)


@router.message(AdvStates.year)
async def adv_year_state(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('<b>Это не год машины</b>')
        return
    if 1940 <= int(message.text) <= 2025:
        await state.update_data(year=message.text)
        await message.answer('<b>Ваше объявление обновленно.</b>')
        await upload_adv(message, state)
    else:
        await message.answer('<b>Такого года машины еще не изобрели.</b>')


@router.message(AdvStates.price)
async def adv_price_state(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('<b>Цена должна быть в формате числа:</b>')
        return
    await state.update_data(price=message.text)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Да', callback_data='Да'),
           types.InlineKeyboardButton(text='Нет', callback_data='Нет'))
    await message.answer('<b>Будет ли торг?</b>', reply_markup=kb)
    await state.set_state(AdvStates.bargain)


@router.callback_query(AdvStates.bargain)
async def adv_price_call(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(auction=call.data)
    await call.message.edit_text('<b>Ваше объявление обновленно.</b>', reply_markup=None)
    await upload_adv(call.message, state)


@router.message(AdvStates.condition)
async def adv_condition_state(message: types.Message, state: FSMContext):
    if len(message.text) < 30:
        await message.answer('<b>Описание слишком маленькое.</b>')
        return
    await state.update_data(condition=message.text)
    await message.answer('<b>Ваше объявление обновленно.</b>')
    await upload_adv(message, state)


@router.callback_query(Text('Отсутствуют'), AdvStates.malfunctions)
async def adv_malfunctions_none(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(malfunctions=call.data)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Да', callback_data='Да'),
           types.InlineKeyboardButton(text='Нет', callback_data='Нет'))
    await call.message.edit_text('<b>Битый ли у вас автомобиль?</b>', reply_markup=kb)
    await state.set_state(AdvStates.broken_state)


@router.message(AdvStates.malfunctions)
async def adv_malfunctions_state(message: types.Message, state: FSMContext):
    await state.update_data(malfunctions=message.text)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Да', callback_data='Да'),
           types.InlineKeyboardButton(text='Нет', callback_data='Нет'))
    await message.answer('<b>Битый ли у вас автомобиль.</b>', reply_markup=kb)
    await state.set_state(AdvStates.broken_state)


@router.callback_query(AdvStates.broken_state)
async def adv_broken_state(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'Нет':
        await state.update_data(broken=call.data)
        await call.message.edit_text('<b>Ваше объявление обновленно.</b>', reply_markup=None)
        await upload_adv(call.message, state)
    else:
        await call.message.edit_text('<b>Что бито на вашем автомобиле, напишите списком.</b>', reply_markup=None)
        await state.set_state(AdvStates.broken_details)


@router.message(AdvStates.broken_details)
async def adv_broken_details(message: types.Message, state: FSMContext):
    await state.update_data(broken=message.text)
    await message.answer('<b>Ваше объявление обновленно.</b>')
    await upload_adv(message, state)


@router.message(AdvStates.contacts)
async def adv_contacts_state(message: types.Message, state: FSMContext):
    await state.update_data(contacts=message.text)
    await message.answer('<b>Ваше объявление обновленно.</b>')
    await upload_adv(message, state)


@router.callback_query(AdvStates.engine)
async def adv_engine_call(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(engine=call.data)
    await call.message.edit_text('<b>Какой объем вашего двигателя?</b>', reply_markup=None)
    await state.set_state(AdvStates.engine_capacity)


@router.message(AdvStates.engine_capacity)
async def adv_engine_capacity(message: types.Message, state: FSMContext):
    try:
        qty = float(message.text)
    except ValueError:
        return await message.answer('<b>Это не объем двигателя.</b>')
    await state.update_data(engine_capacity=qty)
    await message.answer('<b>Какая мощность вашего автомобиля.</b>')
    await state.set_state(AdvStates.power)


@router.message(AdvStates.power)
async def adv_power(message: types.Message, state: FSMContext):
    await state.update_data(horses=message.text)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Автомат', callback_data='Автомат'),
           types.InlineKeyboardButton(text='Робот', callback_data='Робот'))
    kb.add(types.InlineKeyboardButton(text='Вариатор', callback_data='Вариатор'),
           types.InlineKeyboardButton(text='Механика', callback_data='Механика'))
    await message.answer('<b>Какая у вас коробка?</b>', reply_markup=kb)
    await state.set_state(AdvStates.gearbox)


@router.callback_query(AdvStates.gearbox)
async def adv_gearbox(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(engine_box=call.data)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Левый', callback_data='Руль левый'),
           types.InlineKeyboardButton(text='Правый', callback_data='Правый руль'))
    await call.message.edit_text('<b>Какой у вас руль?</b>', reply_markup=kb)
    await state.set_state(AdvStates.wheel)


@router.callback_query(AdvStates.wheel)
async def adv_wheel(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(wheel=call.data)
    await call.message.edit_text('<b>Какой у вас пробег?</b>', reply_markup=None)
    await state.set_state(AdvStates.mileage)


@router.message(AdvStates.mileage)
async def adv_mileage(message: types.Message, state: FSMContext):
    await state.update_data(mileage=message.text)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Передний', callback_data='Передний'),
           types.InlineKeyboardButton(text='Задний', callback_data='Задний'))
    kb.add(types.InlineKeyboardButton(text='Полный', callback_data='Полный'))
    await message.answer('<b>Какой у вас привод?</b>', reply_markup=kb)
    await state.set_state(AdvStates.drive)


@router.callback_query(AdvStates.drive)
async def adv_drive(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(drive=call.data)
    await call.message.edit_text('<b>Ваше объявление обновленно.</b>', reply_markup=None)
    await upload_adv(call.message, state)


@router.message(AdvStates.moderation, F.content_type.in_({'photo', 'video'}))
async def adv_moderation_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    albom = data.get('albom', [])
    album_data = defaultdict(list)
    album_locks = {}
    album_data[message.media_group_id].append(message)
    if message.media_group_id not in album_locks:
        album_locks[message.media_group_id] = asyncio.Lock()
        async with album_locks[message.media_group_id]:
            for msg in sorted(album_data[message.media_group_id], key=lambda m: m.message_id):
                if msg.photo:
                    albom.append(types.InputMediaPhoto(media=msg.photo[-1].file_id))
                elif msg.video:
                    albom.append(types.InputMediaVideo(media=msg.video.file_id))
            del album_data[message.media_group_id]
            del album_locks[message.media_group_id]
    await state.update_data(albom=albom)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Отправить на модерацию', callback_data='Закончить'))
    await message.answer('<b>Загрузили.</b>', reply_markup=kb)


@router.callback_query(Text('Закончить'), AdvStates.moderation)
async def adv_moderation_finish(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    albom = data['albom'][:10]
    город = data.get('citi', 'не указано')
    марка = data.get('brand', 'не указано')
    модель = data.get('model', 'не указано')
    год = data.get('year', 'не указано')
    цена = data.get('price', 'не указано')
    торг = 'Торг уместен' if data.get('auction') == 'Да' else 'Без торга'
    двигатель = data.get('engine', 'не указано')
    объем = data.get('engine_capacity', 'не указано')
    лс = data.get('horses', 'не указано')
    коробка = data.get('engine_box', 'не указано')
    привод = data.get('drive', 'не указано')
    руль = data.get('wheel', 'не указано')
    пробег = data.get('mileage', 'не указано')
    состояние = data.get('condition', 'не указано')
    неисправности = data.get('malfunctions', 'не указано')
    бит = data.get('broken', 'не указано')
    if бит == 'нет':
        битый = '<b>Не битый</b>'
    else:
        битый = f'<b>Битый:</b> {бит}'
    контакты = data.get('contacts', '')
    username = call.from_user.username
    if username:
        контакт = f"@{username}"
    else:
        контакт = контакты
    albom[0].caption = (f"<b>🏙️ Город:</b> #{город}\n\n"
                        f"<b>🚗 Продаю {марка} {модель}</b>\n"
                        f"<b>📍 Год выпуска:</b> {год}\n"
                        f"<b>🏃‍♂️ Пробег:</b> {пробег}\n"
                        f"<b>💰 Цена:</b> {цена} ₽\n"
                        f"📉 {торг}\n\n"
                        f"<b>📝 Характеристики:</b>\n"
                        f"{двигатель}, {объем} л, {лс} л.с.\n"
                        f"{коробка}, {привод}, {руль}\n\n"
                        f"<b>📌 Состояние:</b>\n"
                        f"{состояние}\n\n"
                        f"<b>⚠️ Неисправности:</b>\n"
                        f"{неисправности}\n"
                        f"{битый}\n\n"
                        f"<b>📲 Контакты:</b> {контакт}")
    await bot.send_media_group(chat_id=AdminId, media=albom)
    media_id = generate_random_id()
    if os.path.exists('media.json'):
        with open('media.json', 'r', encoding='utf-8') as f:
            data_to_save = json.load(f)
    else:
        data_to_save = {}
    data_to_save[media_id] = [m.to_python() for m in albom]
    with open('media.json', 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🚀 Опубликовать", callback_data=f"publish_copy:{media_id}"))
    await bot.send_message(chat_id=AdminId,
                           text=f"🔎 Проверь объявление от <a href='tg://user?id={call.from_user.id}'>пользователя</a>:",
                           reply_markup=kb)
    kb2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb2.add('➕ Загрузить объявление')
    await call.message.answer('<b>Ваше объявление отправлено на модерацию.</b>', reply_markup=kb2)


@router.message(AdvStates.moderation)
async def adv_moderation_other(message: types.Message, state: FSMContext):
    await message.answer('<b>Отправьте мне фото/видео в 1 сообщении.</b>')


@router.callback_query(F.data.startswith("publish_copy:"))
async def publish_from_copy(call: types.CallbackQuery):
    msg_id = call.data.split(":", 2)[1]
    with open('media.json', 'r', encoding='utf-8') as f:
        media_data = json.load(f)
    media_dicts = media_data.get(msg_id)
    media_group = []
    for item in media_dicts:
        if item.get('type') == 'video':
            media_group.append(types.InputMediaVideo(**item))
        else:
            media_group.append(types.InputMediaPhoto(**item))
    try:
        await bot.send_media_group(chat_id=ChannelId, media=media_group)
        await call.answer("✅ Объявление опубликовано.")
        await call.message.reply("✅ Объявление отправлено в канал.")
    except Exception as e:
        await call.answer("Ошибка при публикации.")
        await call.message.reply(f"⚠️ Ошибка: {e}")


async def on_startup(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="adv", description="Новое объявление"),
    ])


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
