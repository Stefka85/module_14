from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = "7687027126:AAETT9HHr9J24acv5YImFmExj4pBnNQiJTo"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Создание клавиатуры
kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(text='Рассчитать'),
    KeyboardButton(text='Информация'),
    KeyboardButton(text='Купить')
)

kb2 = InlineKeyboardMarkup().row(
    InlineKeyboardButton(text='Рассчитать норму калорий', callback_data = 'calories'),
    InlineKeyboardButton(text='Формулы расчёта', callback_data = 'formulas')
)

kb_gender = ReplyKeyboardMarkup(resize_keyboard=True).row(
    KeyboardButton(text='М'),
    KeyboardButton(text='Ж')
)

# В главную (обычную) клавиатуру меню добавьте кнопку "Купить".
kb_prod = InlineKeyboardMarkup().row(
    InlineKeyboardButton(text="Product1", callback_data="product_buying"),
    InlineKeyboardButton(text="Product2", callback_data="product_buying"),
    InlineKeyboardButton(text="Product3", callback_data="product_buying"),
    InlineKeyboardButton(text="Product4", callback_data="product_buying")
)



@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"привет! я бот помагающий твоему здоровью."
                         "Чтобы посчитать суточную норму калорий, нажмите ниже", reply_markup=kb2)
    # оставил calories, вместо рассчитать, т.к. иначе приходиться вводить "рассчитать", а не нажимать в боте тг.

@dp.message_handler(text='Информация')
async def inform(message: types.Message):
    await message.answer('Этот бот рассчитывает суточную норму калорий на основе введенных данных.')

@dp.callback_query_handler(text="formulas")
async def get_formulas(call: types.callback_query):
    await call.message.answer(
        "Упрощенная формула Миффлина-Сан Жеора: "
        "\n-для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5 "
        "\n-для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161"
    )
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call: types.callback_query):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()
# 
# @dp.message_handler(text='male')
# async def male(message: types.Message):
#     await message.answer('М')
# 
# 
# 
# @dp.callback_query_handler(text='male')
# async def male(call: types.callback_query, state: FSMContext):
#     await state.update_data(gender='М')
#     data = await state.get_data()
#     weight = int(data["weight"])
#     growth = int(data["growth"])
#     age = int(data["age"])
#     calories = (weight * 10 + growth * 6.25 - age * 5 + 5)
#     await call.message.answer(f'Ваша суточная норма калорий: {calories} (ккал)')
#     await state.finish()
#     await call.answer()

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный возраст.")
        return
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост (см):")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный рост.")
        return
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес (кг):")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_gender(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный вес.")
        return
    await state.update_data(weight=message.text)
    await message.answer('Выберите свой пол:', reply_markup=kb_gender)
    await UserState.gender.set()

@dp.callback_query_handler(text='male')
async def male(call: types.callback_query):
    await call.message.answer('М')
    await call.answer()
    await state.finish()

# @dp.callback_query_handler(text='Ж')
# async def female(call: types.callback_query):
#     await call.message.answer('Введите свой возраст:')
#     await call.answer()
#     await UserState.age.set()

# @dp.callback_query_handler(text='male')
# async def male(call: types.callback_query, state: FSMContext):
#     await state.update_data(gender='М')
#     data = await state.get_data()
#     weight = int(data["weight"])
#     growth = int(data["growth"])
#     age = int(data["age"])
#     calories = (weight * 10 + growth * 6.25 - age * 5 + 5)
#     await call.message.answer(f'Ваша суточная норма калорий: {calories} (ккал)')
#     await state.finish()
#     await call.answer()

@dp.message_handler(state=UserState.gender)
async def calculate_calories(message: types.Message, state: FSMContext):
    if message.data not in ['М', 'Ж']:
        await message.answer("Пожалуйста, выберите корректный пол (М или Ж).")
    return
    await state.update_data(gender=message.text)
    data = await state.get_data()


    # Сохраняем пол в состоянии
    gender = 'М' if call.data == 'male' else 'Ж'
    await state.update_data(gender=gender)

    # Расчет калорий
    data = await state.get_data()
    weight = int(data["weight"])
    growth = int(data["growth"])
    age = int(data["age"])

    if gender == "М":
        calories = (weight * 10 + growth * 6.25 - age * 5 + 5)
    else:  # gender == "Ж"
        calories = (weight * 10 + growth * 6.25 - age * 5 - 161)
    await message.answer(f'Ваша суточная норма калорий: {calories} (ккал)')
    await state.finish()

@dp.message_handler(text="Купить")
async def get_buying_list(message):
    pictures = ["Витамин А.jpg", "Глютамин.jpg", "Омега-3.jpg", "Протеин.jpg"]
    number = 1
    for picture in pictures:
        with open(picture, "rb") as p:
            await message.answer_photo(
                p, f"Название: Product {number} | Орисание: описание {number} | Цена: {number * 100}"
            )
        number += 1
    await message.answer("Выберите продукт для покупки:", reply_markup=kb_prod)

@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

@dp.message_handler()
async def all_messages(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




# @dp.callback_query_handler(text='male')
# async def male(call: types.callback_query, state: FSMContext):
#     await state.update_data(gender='М')
#     data = await state.get_data()
#     weight = int(data["weight"])
#     growth = int(data["growth"])
#     age = int(data["age"])
#     calories = (weight * 10 + growth * 6.25 - age * 5 + 5)
#     await call.message.answer(f'Ваша суточная норма калорий: {calories} (ккал)')
#     await state.finish()
#     await call.answer()
#
# @dp.callback_query_handler(text='female')
# async def female(call: types.callback_query, state: FSMContext):
#     await state.update_data(gender='Ж')
#     data = await state.get_data()
#     weight = int(data["weight"])
#     growth = int(data["growth"])
#     age = int(data["age"])
#     calories = (weight * 10 + growth * 6.25 - age * 5 - 161)
#     await call.message.answer(f'Ваша суточная норма калорий: {calories} (ккал)')
#     await state.finish()
#     await call.answer()