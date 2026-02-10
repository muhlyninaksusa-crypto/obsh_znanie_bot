import os
import sys
import logging
import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ParseMode

# ========== НАСТРОЙКА ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ ОШИБКА: Нет токена! Добавь BOT_TOKEN в Railway Variables")
    sys.exit(1)

print("✅ Токен получен")
print("🚀 Запускаю бота...")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание объектов бота
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ========== ДАННЫЕ ПОЛЬЗОВАТЕЛЯ ==========
users_data = {}

def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {
            "score": 0,
            "correct": 0,
            "total": 0,
            "current_question": None,
            "waiting_answer": False
        }
    return users_data[user_id]

# ========== ВСЕ 49 ВОПРОСОВ ОГЭ ==========
QUESTIONS = {
    1: {
        "text": "Какие два из перечисленных понятий используются в первую очередь при описании духовной сферы общества?\n\nРелигия; доход; наука; демократия; социальная мобильность.\n\nНапишите два понятия:",
        "answer": "религия наука",
        "topic": "Духовная культура",
        "points": 2
    },
    2: {
        "text": "Какие два из перечисленных понятий используются в первую очередь при описании духовной сферы общества?\n\nЖизненные ориентиры; безработица; банковский кредит; авторитаризм; образование.\n\nНапишите два понятия:",
        "answer": "жизненные ориентиры образование",
        "topic": "Духовная культура",
        "points": 2
    },
    3: {
        "text": "Какие два из перечисленных понятий используются в первую очередь при описании духовной сферы общества?\n\nМораль; факторы производства; товар; авторитаризм; искусство.\n\nНапишите два понятия:",
        "answer": "мораль искусство",
        "topic": "Духовная культура",
        "points": 2
    },
    4: {
        "text": "Какие два из перечисленных понятий используются в первую очередь при описании духовной сферы общества?\n\nМировоззрение; страта; познание; деньги; референдум.\n\nНапишите два понятия:",
        "answer": "мировоззрение познание",
        "topic": "Духовная культура",
        "points": 2
    },
    5: {
        "text": "📸 ФОТОГРАФИЯ: Семья за праздничным столом\n\nКакая функция семьи проиллюстрирована? Назовите ещё две функции семьи.\n\nОтвет:",
        "answer": "воспитательная репродуктивная хозяйственная",
        "topic": "Социальная сфера",
        "points": 2
    },
    6: {
        "text": "Человека от животного отличает:\n1) инстинкт самосохранения\n2) использование природных объектов\n3) стремление понять окружающий мир\n4) способность приспосабливаться к условиям среды\n\nВведите номер правильного ответа (1-4):",
        "answer": "3",
        "topic": "Человек и общество",
        "points": 1
    },
    7: {
        "text": "О какой потребности человека: «...главная страсть человека — это быть, исполниться, состояться»?\n1) в самоконтроле\n2) в самореализации\n3) в самопознании\n4) во власти\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Человек и общество",
        "points": 1
    },
    8: {
        "text": "Социальной сущностью человека обусловлена его потребность в:\n1) самореализации\n2) самосохранении\n3) дыхании\n4) питании\n\nВведите номер (1-4):",
        "answer": "1",
        "topic": "Человек и общество",
        "points": 1
    },
    9: {
        "text": "Общество в широком смысле слова означает:\n1) естественную среду обитания человека\n2) группу людей, объединенных общими интересами\n3) стадию исторического развития народа\n4) все человечество в прошлом, настоящем и будущем\n\nВведите номер (1-4):",
        "answer": "4",
        "topic": "Человек и общество",
        "points": 1
    },
    10: {
        "text": "Какие термины используются при описании социальной сферы общества?\n1) искусство, наука\n2) производство, распределение\n3) выборы, референдум\n4) группа, этнос\n\nВведите номер (1-4):",
        "answer": "4",
        "topic": "Социальная сфера",
        "points": 1
    },
    11: {
        "text": "Под обществом в широком смысле понимают:\n1) все население Земли\n2) единство живой и неживой природы\n3) весь мир в многообразии\n4) определенный этап исторического развития\n\nВведите номер (1-4):",
        "answer": "1",
        "topic": "Человек и общество",
        "points": 1
    },
    12: {
        "text": "📊 ДИАГРАММА: Результаты опроса в странах Z и Y о налогах\n\nСформулируйте вывод о сходстве и различии:\n\nОтвет:",
        "answer": "сходство в обеих странах различие в стране",
        "topic": "Политика",
        "points": 3
    },
    13: {
        "text": "Что характеризует демократический режим?\n1) верховенство исполнительной власти\n2) командно-административные методы\n3) господство одной идеологии\n4) защита прав и свобод граждан\n\nВведите номер (1-4):",
        "answer": "4",
        "topic": "Политика",
        "points": 1
    },
    14: {
        "text": "Что является признаком любого государства?\n1) верховенство права\n2) выборность властей\n3) суверенитет\n4) многопартийность\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Политика",
        "points": 1
    },
    15: {
        "text": "Что относится к признакам государства?\n1) партии и движения\n2) общественные организации\n3) налоги и сборы\n4) средства массовой информации\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Политика",
        "points": 1
    },
    16: {
        "text": "Бабушка с внуком нарвали цветы из Красной книги. Нормы какой отрасли права?\n1) уголовного права\n2) административного права\n3) гражданского права\n4) трудового права\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Право",
        "points": 1
    },
    17: {
        "text": "📸 ФОТОГРАФИЯ: Женщина покупает товары\n\nКакой вид экономической деятельности? Два правила потребителя:\n\nОтвет:",
        "answer": "розничная торговля изучать состав сохранять чеки",
        "topic": "Экономика",
        "points": 2
    },
    18: {
        "text": "Верны ли суждения об юридической ответственности?\nА. Восстанавливает нарушенные права\nБ. Выражается в мерах госпринуждения\n1) верно только А\n2) верно только Б\n3) верны оба\n4) оба неверны\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Право",
        "points": 1
    },
    19: {
        "text": "Сравните учебу и игру. Черты сходства и различия:\n\nОтвет:",
        "answer": "сходство деятельность различия цель знания",
        "topic": "Человек и общество",
        "points": 2
    },
    20: {
        "text": "Заполните пропуск в таблице:\nОрган власти: ... РФ\nПолномочия: Разработка и исполнение бюджета\n\nОтвет:",
        "answer": "правительство",
        "topic": "Политика",
        "points": 1
    },
    21: {
        "text": "Составьте план текста об экологических проблемах:\n\nОтвет:",
        "answer": "угроза природе влияние человека рост потребления",
        "topic": "Человек и общество",
        "points": 2
    },
    22: {
        "text": "Прочитайте текст о социализации.\n1) Что такое социализация?\n2) От чего зависят методы?\n3) Что такое социальные нормы?\n\nОтвет:",
        "answer": "усвоение норм от ценностей ожидания поведения",
        "topic": "Социальная сфера",
        "points": 3
    },
    23: {
        "text": "Объясните «гражданское общество». Два примера:\n\nОтвет:",
        "answer": "сфера самодеятельности экодвижение благотворительность",
        "topic": "Политика",
        "points": 3
    },
    24: {
        "text": "Природа необходима для духовной жизни. Два объяснения:\n\nОтвет:",
        "answer": "вдохновляет творчество восстанавливает силы",
        "topic": "Человек и общество",
        "points": 2
    },
    25: {
        "text": "Верны ли суждения о политической власти?\nА. Распространяется на всё общество\nБ. Опирается на силу закона\n1) верно только А\n2) верно только Б\n3) верны оба\n4) оба неверны\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Политика",
        "points": 1
    },
    26: {
        "text": "Что является примером гражданского общества?\n1) работа администрации\n2) заседание правительства\n3) благотворительный фонд\n4) сессия парламента\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Политика",
        "points": 1
    },
    27: {
        "text": "Что характеризует рыночную экономику?\n1) централизованное планирование\n2) свобода предпринимательства\n3) государственная собственность\n4) директивное ценообразование\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Экономика",
        "points": 1
    },
    28: {
        "text": "Что является примером прямых налогов?\n1) НДС\n2) акцизы\n3) подоходный налог\n4) таможенные пошлины\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Экономика",
        "points": 1
    },
    29: {
        "text": "Что является социальной потребностью?\n1) в пище\n2) в безопасности\n3) в общении\n4) в отдыхе\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Человек и общество",
        "points": 1
    },
    30: {
        "text": "Что относится к институтам социализации?\n1) семья и школа\n2) банки и биржи\n3) армия и полиция\n4) заводы и фабрики\n\nВведите номер (1-4):",
        "answer": "1",
        "topic": "Социальная сфера",
        "points": 1
    },
    31: {
        "text": "Что является примером вертикальной мобильности?\n1) переезд в город\n2) смена работы\n3) повышение в должности\n4) выход на пенсию\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Социальная сфера",
        "points": 1
    },
    32: {
        "text": "Что является признаком правового государства?\n1) сильная армия\n2) разделение властей\n3) развитая экономика\n4) большая территория\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Право",
        "points": 1
    },
    33: {
        "text": "Что относится к личным правам человека?\n1) право на труд\n2) право на образование\n3) право на жизнь\n4) право участвовать в управлении\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Право",
        "points": 1
    },
    34: {
        "text": "Что является административным правонарушением?\n1) кража\n2) причинение вреда здоровью\n3) переход в неположенном месте\n4) неуплата налогов\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Право",
        "points": 1
    },
    35: {
        "text": "Что относится к духовной культуре?\n1) строительство завода\n2) принятие закона\n3) научное открытие\n4) выплата зарплаты\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Духовная культура",
        "points": 1
    },
    36: {
        "text": "Что является функцией искусства?\n1) производство благ\n2) регулирование отношений\n3) эстетическое освоение мира\n4) поддержание порядка\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Духовная культура",
        "points": 1
    },
    37: {
        "text": "Что характеризует традиционное общество?\n1) развитая промышленность\n2) сельское хозяйство\n3) урбанизация\n4) технологическое развитие\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Человек и общество",
        "points": 1
    },
    38: {
        "text": "Что является глобальной проблемой?\n1) безработица\n2) экологический кризис\n3) инфляция\n4) политический кризис\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Человек и общество",
        "points": 1
    },
    39: {
        "text": "Что характеризует гражданское общество?\n1) сильное государство\n2) общественные организации\n3) единая идеология\n4) централизованная экономика\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Политика",
        "points": 1
    },
    40: {
        "text": "Что является признаком правового государства?\n1) многопартийность\n2) верховенство закона\n3) развитая экономика\n4) большая территория\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Право",
        "points": 1
    },
    41: {
        "text": "Что относится к политическим правам?\n1) право на жилище\n2) право на образование\n3) право избирать\n4) право на медпомощь\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Право",
        "points": 1
    },
    42: {
        "text": "Что является экономическим ресурсом?\n1) деньги\n2) законы\n3) традиции\n4) моральные нормы\n\nВведите номер (1-4):",
        "answer": "1",
        "topic": "Экономика",
        "points": 1
    },
    43: {
        "text": "Что характеризует рыночную цену?\n1) устанавливается государством\n2) зависит от спроса и предложения\n3) одинакова везде\n4) не меняется\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Экономика",
        "points": 1
    },
    44: {
        "text": "Что является социальным конфликтом?\n1) спор покупателя\n2) разногласия партий\n3) забастовка рабочих\n4) все перечисленные\n\nВведите номер (1-4):",
        "answer": "4",
        "topic": "Социальная сфера",
        "points": 1
    },
    45: {
        "text": "Что относится к функциям семьи?\n1) политическая\n2) экономическая\n3) законодательная\n4) судебная\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Социальная сфера",
        "points": 1
    },
    46: {
        "text": "Что характеризует индустриальное общество?\n1) сельское хозяйство\n2) промышленность\n3) низкая мобильность\n4) религиозная культура\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Человек и общество",
        "points": 1
    },
    47: {
        "text": "Что является массовой культурой?\n1) народные сказки\n2) телесериалы\n3) классическая музыка\n4) религиозные обряды\n\nВведите номер (1-4):",
        "answer": "2",
        "topic": "Духовная культура",
        "points": 1
    },
    48: {
        "text": "Верны ли суждения о политических партиях?\nА. Представляют интересы групп\nБ. Борются за власть\n1) верно только А\n2) верно только Б\n3) верны оба\n4) оба неверны\n\nВведите номер (1-4):",
        "answer": "3",
        "topic": "Политика",
        "points": 1
    },
    49: {
        "text": "Что является международной организацией?\n1) ООН\n2) Совет Безопасности РФ\n3) Госдума РФ\n4) Правительство РФ\n\nВведите номер (1-4):",
        "answer": "1",
        "topic": "Политика",
        "points": 1
    }
}

# ========== КЛАВИАТУРА ==========
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    buttons = [
        "📚 ТЕОРИЯ", 
        "🎯 ЗАДАНИЯ",
        "📝 ПОЛНЫЙ ОГЭ",
        "📊 СТАТИСТИКА",
        "🆘 ПОМОЩЬ"
    ]
    for button in buttons:
        builder.add(KeyboardButton(text=button))
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    welcome = f"""
👋 <b>Привет, {message.from_user.first_name}!</b>

📚 <b>БОТ ДЛЯ ПОДГОТОВКИ К ОГЭ</b>
Всего 49 заданий из реальных вариантов ОГЭ

🏆 <b>Твоя статистика:</b>
• Решено: {user['total']} заданий
• Правильно: {user['correct']}
• Баллы: {user['score']}

🎯 <b>Выбери действие:</b>
"""
    await message.answer(welcome, reply_markup=get_main_keyboard())

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = """
🆘 <b>ПОМОЩЬ</b>

<b>Как использовать бота:</b>
1. Нажми "🎯 ЗАДАНИЯ" - выбирай номер задания
2. Отправь ответ текстом или цифрой
3. Получи объяснение и баллы

<b>Типы вопросов:</b>
• С выбором ответа (1-4) - пиши номер
• Текстовые вопросы - пиши ответ словами

<b>Команды:</b>
/start - перезапуск бота
/help - эта справка
/stats - твоя статистика
"""
    await message.answer(help_text)

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    accuracy = (user['correct'] / user['total'] * 100) if user['total'] > 0 else 0
    
    stats = f"""
📊 <b>ТВОЯ СТАТИСТИКА</b>

🎯 <b>Результаты:</b>
• Всего заданий: {user['total']}
• Правильных: {user['correct']}
• Точность: {accuracy:.1f}%
• Баллы: {user['score']}

📈 <b>Прогресс:</b>
• Освоено: {len([q for q in QUESTIONS if q <= user['total']])}/49 заданий
"""
    await message.answer(stats)

@dp.message(F.text == "🆘 ПОМОЩЬ")
async def help_button(message: types.Message):
    await cmd_help(message)

@dp.message(F.text == "📊 СТАТИСТИКА")
async def stats_button(message: types.Message):
    await cmd_stats(message)

@dp.message(F.text == "📚 ТЕОРИЯ")
async def theory_button(message: types.Message):
    theory = """
📚 <b>ОСНОВНЫЕ ТЕМЫ ОГЭ</b>

<b>1. ЧЕЛОВЕК И ОБЩЕСТВО</b>
• Общество как система
• Человек как биосоциальное существо
• Деятельность, познание

<b>2. ЭКОНОМИКА</b>
• Основы экономики
• Рыночная экономика
• Деньги, банки, налоги

<b>3. СОЦИАЛЬНАЯ СФЕРА</b>
• Социальная структура
• Семья, молодежь
• Социальные нормы

<b>4. ПОЛИТИКА</b>
• Государство, власть
• Демократия, выборы
• Политические партии

<b>5. ПРАВО</b>
• Право в обществе
• Конституция РФ
• Права и обязанности

<b>6. ДУХОВНАЯ КУЛЬТУРА</b>
• Культура, искусство
• Наука, образование
• Мораль, религия
"""
    await message.answer(theory)

@dp.message(F.text == "🎯 ЗАДАНИЯ")
async def tasks_button(message: types.Message):
    tasks_menu = """
🎯 <b>ВЫБЕРИ ЗАДАНИЕ</b>

<b>Группы заданий:</b>
1-10: Задания на определение понятий
11-20: Вопросы с выбором ответа
21-30: Анализ диаграмм, фотографий
31-40: Текстовые задания
41-49: Сложные вопросы

<b>Как выбрать:</b>
Просто напиши номер задания от 1 до 49
Например: "12" или "35"
"""
    await message.answer(tasks_menu)

@dp.message(F.text == "📝 ПОЛНЫЙ ОГЭ")
async def full_oge_button(message: types.Message):
    user = get_user_data(message.from_user.id)
    user["exam_mode"] = True
    user["exam_questions"] = list(range(1, 50))
    user["exam_current"] = 1
    user["exam_score"] = 0
    
    await message.answer(
        "📝 <b>НАЧИНАЕМ ПОЛНЫЙ ВАРИАНТ ОГЭ!</b>\n\n"
        "Тебе предстоит ответить на 49 вопросов.\n"
        "Пиши ответы как обычно - цифрой или текстом.\n\n"
        f"<b>Задание 1 из 49:</b>\n{QUESTIONS[1]['text']}"
    )

# ========== ОБРАБОТКА ОТВЕТОВ ==========
@dp.message()
async def handle_all_messages(message: types.Message):
    user = get_user_data(message.from_user.id)
    text = message.text.strip().lower()
    
    # Если в режиме экзамена
    if user.get("exam_mode"):
        await handle_exam_answer(message, user, text)
        return
    
    # Если ждем ответ на вопрос
    if user.get("waiting_answer") and user.get("current_question"):
        await check_answer(message, user, text)
        return
    
    # Если ввели номер задания (1-49)
    if text.isdigit():
        num = int(text)
        if 1 <= num <= 49:
            await send_question(message, user, num)
            return
    
    # Если не поняли сообщение
    await message.answer(
        "🤔 <b>Не понял запрос</b>\n\n"
        "Можно:\n"
        "• Нажать кнопку меню\n"
        "• Написать номер задания (1-49)\n"
        "• Использовать /help"
    )

async def send_question(message, user, question_num):
    if question_num not in QUESTIONS:
        await message.answer("❌ Такого задания нет")
        return
    
    question = QUESTIONS[question_num]
    user["current_question"] = question_num
    user["waiting_answer"] = True
    
    text = f"<b>🎯 ЗАДАНИЕ №{question_num}</b>\n\n"
    text += f"📚 Тема: {question['topic']}\n"
    text += f"⭐ Баллы: {question['points']}\n\n"
    text += question['text']
    
    await message.answer(text)

async def check_answer(message, user, answer):
    question_num = user["current_question"]
    question = QUESTIONS[question_num]
    
    # Сбрасываем флаг
    user["waiting_answer"] = False
    
    # Проверяем ответ
    is_correct = False
    correct_answer = str(question["answer"]).lower()
    
    if answer.isdigit():
        # Для вопросов с выбором ответа
        is_correct = (answer == correct_answer)
    else:
        # Для текстовых вопросов - проверяем наличие ключевых слов
        user_words = answer.split()
        correct_words = correct_answer.split()
        matched = sum(1 for word in correct_words if word in answer)
        is_correct = (matched >= 2)  # Хотя бы 2 ключевых слова
    
    # Обновляем статистику
    user["total"] += 1
    if is_correct:
        user["correct"] += 1
        user["score"] += question["points"]
    
    # Формируем ответ
    if is_correct:
        result = "✅ <b>ПРАВИЛЬНО!</b>"
        points = f"+{question['points']} баллов"
    else:
        result = "❌ <b>НЕПРАВИЛЬНО</b>"
        points = "0 баллов"
    
    response = f"""
{result}

<b>Ваш ответ:</b> {message.text}
<b>Баллы:</b> {points}

<b>Правильный ответ:</b> {question['answer']}

<b>Твоя статистика:</b>
• Всего: {user['total']} заданий
• Правильно: {user['correct']}
• Баллы: {user['score']}
"""
    
    # Предлагаем следующее действие
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="🎯 СЛЕДУЮЩЕЕ ЗАДАНИЕ"))
    keyboard.add(KeyboardButton(text="📊 СТАТИСТИКА"))
    keyboard.add(KeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ"))
    keyboard.adjust(1, 2)
    
    await message.answer(response, reply_markup=keyboard.as_markup(resize_keyboard=True))

async def handle_exam_answer(message, user, answer):
    current = user["exam_current"]
    question = QUESTIONS[current]
    
    # Проверяем ответ
    is_correct = False
    correct_answer = str(question["answer"]).lower()
    
    if answer.isdigit():
        is_correct = (answer == correct_answer)
    else:
        user_words = answer.split()
        correct_words = correct_answer.split()
        matched = sum(1 for word in correct_words if word in answer)
        is_correct = (matched >= 2)
    
    if is_correct:
        user["exam_score"] += question["points"]
    
    # Переход к следующему вопросу или завершение
    if current < 49:
        user["exam_current"] += 1
        next_q = user["exam_current"]
        next_question = QUESTIONS[next_q]
        
        response = f"""
{'✅' if is_correct else '❌'} <b>Задание {current}</b>
Текущий счет: {user['exam_score']} баллов

<b>Задание {next_q} из 49:</b>
{next_question['text']}
"""
        await message.answer(response)
    else:
        # Завершение экзамена
        await finish_exam(message, user)

async def finish_exam(message, user):
    total_possible = sum(QUESTIONS[i]["points"] for i in range(1, 50))
    accuracy = (user["exam_score"] / total_possible * 100) if total_possible > 0 else 0
    
    if user["exam_score"] >= 35:
        grade = "5 (ОТЛИЧНО) 🏆"
    elif user["exam_score"] >= 25:
        grade = "4 (ХОРОШО) ⭐"
    elif user["exam_score"] >= 15:
        grade = "3 (УДОВЛЕТВОРИТЕЛЬНО) ✅"
    else:
        grade = "2 (НЕУДОВЛЕТВОРИТЕЛЬНО) ❌"
    
    result = f"""
🏁 <b>ЭКЗАМЕН ЗАВЕРШЕН!</b>

📊 <b>ИТОГИ:</b>
• Набрано баллов: {user['exam_score']}/{total_possible}
• Точность: {accuracy:.1f}%
• Оценка: {grade}

{"🎉 Отличный результат! Ты готов к ОГЭ!" if accuracy >= 80 else 
 "👍 Хороший результат! Повтори сложные темы." if accuracy >= 60 else 
 "📚 Средний результат. Нужно больше практики." if accuracy >= 40 else 
 "🔄 Низкий результат. Повтори теорию и попробуй снова."}
"""
    
    # Обновляем общую статистику
    user["total"] += 49
    user["correct"] += int(user["exam_score"] / 2)  # Примерный перевод баллов в правильные ответы
    user["score"] += user["exam_score"]
    
    # Сбрасываем режим экзамена
    user["exam_mode"] = False
    
    await message.answer(result, reply_markup=get_main_keyboard())

@dp.message(F.text == "🎯 СЛЕДУЮЩЕЕ ЗАДАНИЕ")
async def next_question_button(message: types.Message):
    user = get_user_data(message.from_user.id)
    
    # Находим следующее нерешенное задание
    solved = user.get("solved_questions", [])
    available = [q for q in range(1, 50) if q not in solved]
    
    if available:
        next_q = random.choice(available)
        await send_question(message, user, next_q)
    else:
        await message.answer(
            "🎉 <b>Ты решил все задания!</b>\n\n"
            "Попробуй полный вариант ОГЭ или повтори теорию.",
            reply_markup=get_main_keyboard()
        )

@dp.message(F.text == "🏠 ГЛАВНОЕ МЕНЮ")
async def main_menu_button(message: types.Message):
    await message.answer("Главное меню:", reply_markup=get_main_keyboard())

# ========== ЗАПУСК БОТА ==========
async def main():
    print("=" * 50)
    print("🤖 БОТ ДЛЯ ПОДГОТОВКИ К ОГЭ")
    print("=" * 50)
    print(f"✅ Токен: {'ЕСТЬ' if BOT_TOKEN else 'НЕТ!'}")
    print(f"📚 Вопросов: {len(QUESTIONS)}")
    print("🚀 Запускаю бота...")
    
    try:
        # Удаляем вебхук
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запускаем поллинг
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Для Railway
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Порт: {port}")
    
    # Простой HTTP сервер для health checks
    async def health_check():
        from aiohttp import web
        
        app = web.Application()
        
        async def handle(request):
            return web.Response(text="Bot is running")
        
        app.router.add_get('/', handle)
        app.router.add_get('/health', handle)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        return runner
    
    # Запускаем бота и HTTP сервер
    async def run_all():
        runner = await health_check()
        try:
            await main()
        finally:
            await runner.cleanup()
    
    asyncio.run(run_all())



