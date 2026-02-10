import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ERROR: No BOT_TOKEN!")
    exit(1)

print("✅ Bot starting...")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Вопросы ОГЭ (только 5 для примера, добавь остальные)
QUESTIONS = {
    1: "❓ Задание 1: Какие два понятия относятся к духовной сфере?\nа) Религия\nб) Деньги\nв) Наука\nг) Завод\n\nОтвет (например: а в):",
    2: "❓ Задание 2: Человека от животного отличает:\n1) Инстинкт\n2) Сознание\n3) Питание\n4) Сон\n\nВведи номер:",
    3: "❓ Задание 3: Что такое демократия?\nОтвет:",
    4: "❓ Задание 4: Государственные налоги - это:\n1) Добровольные платежи\n2) Обязательные платежи\n3) Пожертвования\n4) Займы\n\nВведи номер:",
    5: "❓ Задание 5: Конституция РФ принята в:\n1) 1991\n2) 1993\n3) 2000\n4) 2003\n\nВведи номер:"
}

ANSWERS = {
    1: "а в",
    2: "2",
    3: "власть народа",
    4: "2",
    5: "2"
}

user_data = {}

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"question": 1, "score": 0}
    
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "📚 Бот для подготовки к ОГЭ по обществознанию\n\n"
        "🎯 Чтобы решить задание - просто пиши ответ\n"
        "🔄 Для след. задания - /next\n"
        "📊 Статистика - /stats\n\n"
        f"Начинаем!\n\n{QUESTIONS[1]}"
    )

@dp.message(lambda message: message.text and message.text.lower() == "/next")
async def next_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"question": 1, "score": 0}
    
    current = user_data[user_id]["question"]
    if current < 5:
        user_data[user_id]["question"] += 1
        next_q = user_data[user_id]["question"]
        await message.answer(f"📝 Задание {next_q}:\n\n{QUESTIONS[next_q]}")
    else:
        await message.answer("🎉 Ты прошел все задания! /start - начать заново")

@dp.message(lambda message: message.text and message.text.lower() == "/stats")
async def stats_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"question": 1, "score": 0}
    
    score = user_data[user_id]["score"]
    current = user_data[user_id]["question"]
    
    await message.answer(
        f"📊 Твоя статистика:\n"
        f"• Баллы: {score}\n"
        f"• Текущее задание: {current}/5\n"
        f"• Прогресс: {current*20}%\n\n"
        "/next - следующее задание"
    )

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"question": 1, "score": 0}
    
    current_q = user_data[user_id]["question"]
    user_answer = message.text.strip().lower()
    correct_answer = str(ANSWERS.get(current_q, "")).lower()
    
    # Проверка ответа
    if user_answer == correct_answer:
        user_data[user_id]["score"] += 1
        response = f"✅ ПРАВИЛЬНО!\n+1 балл\nВсего баллов: {user_data[user_id]['score']}"
    else:
        response = f"❌ НЕПРАВИЛЬНО\nПравильный ответ: {correct_answer}\nБаллы: {user_data[user_id]['score']}"
    
    await message.answer(response)
    
    # Автоматически предлагаем следующее
    if current_q < 5:
        await message.answer("Нажми /next для след. задания")
    else:
        await message.answer("🎉 Все задания пройдены! /start - начать заново")

async def main():
    print("🤖 Bot is running...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Для Railway health check
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
    
    def run_health():
        server = HTTPServer(('0.0.0.0', 8000), HealthHandler)
        server.serve_forever()
    
    # Запускаем health check в отдельном потоке
    health_thread = threading.Thread(target=run_health, daemon=True)
    health_thread.start()
    
    # Запускаем бота
    asyncio.run(main())



