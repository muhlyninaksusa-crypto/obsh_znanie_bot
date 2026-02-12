import os
import sys
import logging
import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ========== ПРОВЕРКА ТОКЕНА ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден!")
    sys.exit(1)

print("✅ Токен получен!")

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== СОЗДАНИЕ ОБЪЕКТОВ БОТА ==========
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)

# ========== ТЕМЫ С ПОДТЕМАМИ - КОРОТКИЕ КЛЮЧИ ДЛЯ CALLBACK ==========
THEORY_DETAILED = {
    "Человек и общество": {
        "Общество как система": {
            "definition": "Общество — это часть материального мира, отделившаяся от природы, но тесно с ней связанная.",
            "key_points": [
                "Основные сферы: экономическая, политическая, социальная, духовная",
                "Общество — динамическая система",
                "Социальные институты — устойчивые формы организации жизни"
            ],
            "examples": [
                "Экономическая сфера: заводы, банки",
                "Политическая сфера: парламент, выборы",
                "Социальная сфера: семья, школа",
                "Духовная сфера: театры, музеи"
            ],
            "questions": [
                "Назовите 4 основные сферы общества",
                "Что такое социальный институт?"
            ]
        },
        "Человек как биосоциальное существо": {
            "definition": "Человек — это существо, обладающее биологической природой и социальной сущностью.",
            "key_points": [
                "Биологическое: анатомия, физиология, инстинкты",
                "Социальное: сознание, речь, труд, мораль",
                "Индивид, индивидуальность, личность"
            ],
            "examples": [
                "Биологическое: человек дышит, ест, спит",
                "Социальное: человек говорит, соблюдает законы, учится"
            ],
            "questions": [
                "В чем проявляется биологическая природа человека?",
                "Что такое личность?"
            ]
        }
    },
    "Экономика": {
        "Основы экономики": {
            "definition": "Экономика — это хозяйственная система, обеспечивающая производство, распределение, обмен и потребление благ.",
            "key_points": [
                "Основные вопросы: что производить? как производить? для кого производить?",
                "Типы экономических систем: традиционная, командная, рыночная, смешанная",
                "Факторы производства: труд, земля, капитал, предпринимательство"
            ],
            "examples": [
                "Рыночная экономика: США",
                "Командная экономика: СССР"
            ],
            "questions": [
                "Какие три основных вопроса решает экономика?",
                "Назовите типы экономических систем"
            ]
        }
    },
    "Социальная сфера": {
        "Социальная структура": {
            "definition": "Социальная структура — это строение общества, система взаимосвязей между его элементами.",
            "key_points": [
                "Социальная стратификация — деление общества на слои",
                "Критерии стратификации: доход, власть, образование, престиж",
                "Социальная мобильность — перемещение между стратами"
            ],
            "examples": [
                "Социальные слои: высший, средний, низший класс",
                "Вертикальная мобильность: повышение в должности"
            ],
            "questions": [
                "Что такое социальная стратификация?",
                "Какие виды социальной мобильности вы знаете?"
            ]
        }
    },
    "Политика": {
        "Государство и его функции": {
            "definition": "Государство — это организация политической власти, управляющая обществом на определенной территории.",
            "key_points": [
                "Признаки государства: территория, население, суверенитет, налоги",
                "Функции: внутренние и внешние",
                "Формы государства: монархия, республика"
            ],
            "examples": [
                "Монархия: Великобритания",
                "Республика: Россия, США"
            ],
            "questions": [
                "Назовите признаки государства",
                "Чем монархия отличается от республики?"
            ]
        }
    },
    "Право": {
        "Конституция РФ": {
            "definition": "Конституция РФ — это основной закон России, имеющий высшую юридическую силу.",
            "key_points": [
                "Принята 12 декабря 1993 года",
                "Основы конституционного строя",
                "Права и свободы человека"
            ],
            "examples": [
                "Личные права: право на жизнь",
                "Политические права: избирать и быть избранным"
            ],
            "questions": [
                "Когда была принята Конституция РФ?",
                "Какие группы прав человека вы знаете?"
            ]
        }
    },
    "Духовная культура": {
        "Культура и её формы": {
            "definition": "Культура — это все материальные и духовные ценности, созданные человечеством.",
            "key_points": [
                "Материальная культура: здания, техника",
                "Духовная культура: наука, искусство, религия",
                "Функции культуры: познавательная, воспитательная"
            ],
            "examples": [
                "Материальная культура: Эрмитаж",
                "Духовная культура: роман «Война и мир»"
            ],
            "questions": [
                "Чем материальная культура отличается от духовной?",
                "Каковы функции культуры?"
            ]
        }
    }
}

# ========== МАППИНГ ДЛЯ КОРОТКИХ CALLBACK ==========
TOPIC_KEYS = {
    "Человек и общество": "t1",
    "Экономика": "t2",
    "Социальная сфера": "t3",
    "Политика": "t4",
    "Право": "t5",
    "Духовная культура": "t6"
}

SUBTOPIC_KEYS = {}
for topic, subtopics in THEORY_DETAILED.items():
    for i, subtopic in enumerate(subtopics.keys(), 1):
        key = f"s{TOPIC_KEYS[topic][1]}{i}"
        SUBTOPIC_KEYS[key] = (topic, subtopic)

# ========== СИСТЕМА ДОСТИЖЕНИЙ ==========
ACHIEVEMENTS = {
    "first_step": {
        "name": "🚀 Первый шаг",
        "description": "Решить первое задание",
        "icon": "🚀",
        "unlocked": False
    },
    "constitution_expert": {
        "name": "⚖️ Эксперт по праву",
        "description": "Правильно ответить на 10 вопросов по праву",
        "icon": "⚖️",
        "unlocked": False,
        "progress": 0,
        "target": 10
    },
    "perfect_week": {
        "name": "⭐ Неделя без ошибок",
        "description": "7 дней подряд без ошибок",
        "icon": "⭐",
        "unlocked": False,
        "progress": 0,
        "target": 7
    },
    "active_month": {
        "name": "🔥 Активный месяц",
        "description": "30 дней подряд с ботом",
        "icon": "🔥",
        "unlocked": False,
        "progress": 0,
        "target": 30
    },
    "all_topics": {
        "name": "🎓 Освоил все темы",
        "description": "Пройти все темы с результатом >80%",
        "icon": "🎓",
        "unlocked": False
    },
    "oge_master": {
        "name": "🏆 Мастер ОГЭ",
        "description": "Набрать 25+ баллов в варианте",
        "icon": "🏆",
        "unlocked": False
    },
    "perfectionist": {
        "name": "💎 Перфекционист",
        "description": "10 заданий подряд без ошибок",
        "icon": "💎",
        "unlocked": False,
        "progress": 0,
        "target": 10
    }
}

# ========== ХРАНЕНИЕ ДАННЫХ ==========
class UserState:
    def __init__(self, user_id):
        self.user_id = user_id
        self.score = 0
        self.correct_answers = 0
        self.total_attempts = 0
        self.current_question = None
        self.completed_tasks = set()
        self.exam_results = []
        self.current_exam = None
        self.current_exam_index = 0
        self.exam_score = 0
        self.topic_stats = {}
        self.waiting_for_answer = False
        
        # Геймификация
        self.achievements = {k: v.copy() for k, v in ACHIEVEMENTS.items()}
        self.daily_streak = 0
        self.last_active_date = None
        self.perfect_days_streak = 0
        self.perfect_answers_streak = 0
        self.topics_mastered = {topic: False for topic in THEORY_DETAILED.keys()}
        
        # Статистика по темам
        for topic in THEORY_DETAILED.keys():
            self.topic_stats[topic] = {
                "correct": 0,
                "total": 0,
                "accuracy": 0.0
            }
    
    def add_result(self, is_correct, points=1, topic=""):
        self.total_attempts += 1
        
        if is_correct:
            self.correct_answers += 1
            self.score += points
            self.perfect_answers_streak += 1
            if self.perfect_answers_streak > self.achievements["perfectionist"]["progress"]:
                self.achievements["perfectionist"]["progress"] = self.perfect_answers_streak
        else:
            self.perfect_answers_streak = 0
        
        if self.current_question:
            self.completed_tasks.add(self.current_question["id"])
        
        # Обновляем статистику по теме
        if topic and topic in self.topic_stats:
            self.topic_stats[topic]["total"] += 1
            if is_correct:
                self.topic_stats[topic]["correct"] += 1
            
            if self.topic_stats[topic]["total"] > 0:
                self.topic_stats[topic]["accuracy"] = (
                    self.topic_stats[topic]["correct"] / self.topic_stats[topic]["total"] * 100
                )
            
            # Проверяем, освоена ли тема
            if (self.topic_stats[topic]["total"] >= 3 and 
                self.topic_stats[topic]["accuracy"] >= 80):
                self.topics_mastered[topic] = True
        
        # Проверяем достижения
        self.check_achievements()
        
        return is_correct
    
    def update_daily_streak(self):
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        
        if self.last_active_date:
            try:
                last_date = datetime.strptime(self.last_active_date, "%Y-%m-%d").date()
                difference = (today - last_date).days
                
                if difference == 1:
                    self.daily_streak += 1
                    self.perfect_days_streak += 1
                elif difference > 1:
                    self.daily_streak = 1
                    self.perfect_days_streak = 0
            except:
                self.daily_streak = 1
                self.perfect_days_streak = 1
        else:
            self.daily_streak = 1
            self.perfect_days_streak = 1
        
        self.last_active_date = today_str
        self.check_achievements()
    
    def check_achievements(self):
        if not self.achievements["first_step"]["unlocked"] and self.total_attempts >= 1:
            self.achievements["first_step"]["unlocked"] = True
        
        if "Право" in self.topic_stats:
            right_count = self.topic_stats["Право"]["correct"]
            self.achievements["constitution_expert"]["progress"] = right_count
            if right_count >= 10:
                self.achievements["constitution_expert"]["unlocked"] = True
        
        self.achievements["perfect_week"]["progress"] = self.perfect_days_streak
        if self.perfect_days_streak >= 7:
            self.achievements["perfect_week"]["unlocked"] = True
        
        self.achievements["active_month"]["progress"] = self.daily_streak
        if self.daily_streak >= 30:
            self.achievements["active_month"]["unlocked"] = True
        
        topics_mastered = sum(1 for mastered in self.topics_mastered.values() if mastered)
        if topics_mastered == len(THEORY_DETAILED):
            self.achievements["all_topics"]["unlocked"] = True
        
        if self.exam_score >= 25:
            self.achievements["oge_master"]["unlocked"] = True
        
        if self.perfect_answers_streak >= 10:
            self.achievements["perfectionist"]["unlocked"] = True
    
    def get_weak_topics(self, limit=2):
        weak_topics = []
        for topic, stats in self.topic_stats.items():
            if stats["total"] >= 2 and stats["accuracy"] < 70:
                weak_topics.append({
                    "topic": topic,
                    "accuracy": stats["accuracy"],
                    "correct": stats["correct"],
                    "total": stats["total"]
                })
        
        weak_topics.sort(key=lambda x: x["accuracy"])
        return weak_topics[:limit]
    
    def get_progress_summary(self):
        accuracy = (self.correct_answers / self.total_attempts * 100) if self.total_attempts > 0 else 0
        
        return {
            "total_score": self.score,
            "accuracy": round(accuracy, 1),
            "days_streak": self.daily_streak,
            "perfect_days_streak": self.perfect_days_streak,
            "perfect_answers_streak": self.perfect_answers_streak,
            "total_questions": self.total_attempts,
            "correct_answers": self.correct_answers,
            "topics_mastered": sum(1 for mastered in self.topics_mastered.values() if mastered),
            "total_topics": len(THEORY_DETAILED),
            "achievements_unlocked": sum(1 for ach in self.achievements.values() if ach["unlocked"]),
            "total_achievements": len(self.achievements)
        }

user_data = {}

def get_user_state(user_id):
    if user_id not in user_data:
        user_data[user_id] = UserState(user_id)
    return user_data[user_id]

# ========== ТЕКСТЫ ДЛЯ ЗАДАНИЙ 2 ЧАСТИ ==========
TEXT_FOR_21_24 = """
«Под угрозой сейчас находится большинство оставшихся высших видов растений и животных. Те из них, которые человек избрал для удовлетворения своих потребностей, давно уже приспособлены к его требованиям, но дикие виды, для которых нет места в мире человека, обречены. Их погубят не только охота и истребление, но и сведение лесов под поля, шахты, дороги, а главное — превращение обширных участков дикой природы в города и промышленные комплексы.

Человек, придя в будущее, должен иметь возможность увидеть Землю не только как всеобщую стройплощадку и всеобщую ферму, но и как дикую природу, оставшуюся нетронутой. Она необходима и как среда обитания самого человека, поскольку он биологически сформировался в естественной, открытой среде. Она необходима и для этического воспитания человека: ничто так не воспитывает доброту, как контакт с дикой природой.

Забота о сохранении дикой природы — неотъемлемая часть развития цивилизации, обязательное условие прогресса.»
"""

# ========== ВСЕ 24 ЗАДАНИЯ ОГЭ ==========
OGE_QUESTIONS = [
    # ЗАДАНИЕ 1
    {
        "id": 1,
        "text": "Какие два из перечисленных понятий используются в первую очередь при описании политической сферы общества?\n\nФедерация; собственность; культура; страта; государство.\n\nВыпишите соответствующие понятия и раскройте смысл любого одного из них.",
        "correct_answers": ["Федерация", "Государство"],
        "explanation": "✅ Правильно: Федерация и государство относятся к политической сфере.",
        "topic": "Политика",
        "points": 2,
        "type": "text"
    },
    {
        "id": 2,
        "text": "Человека от животного отличает способность\n\n1) проявлять заботу о потомстве\n2) использовать предметы, данные природой\n3) воспринимать и передавать информацию\n4) создавать условия и средства жизни в совместной деятельности",
        "options": ["проявлять заботу о потомстве", "использовать предметы, данные природой", "воспринимать и передавать информацию", "создавать условия и средства жизни в совместной деятельности"],
        "correct": 3,
        "explanation": "✅ Правильно: создавать условия и средства жизни в совместной деятельности.",
        "topic": "Человек и общество",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 3,
        "text": "Виталий учится в 8 классе гимназии. На какой образовательной ступени находится Виталий?\n\n1) среднее профессиональное образование\n2) основное общее образование\n3) среднее общее образование\n4) начальное общее образование",
        "options": ["среднее профессиональное образование", "основное общее образование", "среднее общее образование", "начальное общее образование"],
        "correct": 1,
        "explanation": "✅ Правильно: основное общее образование.",
        "topic": "Духовная культура",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 4,
        "text": "Верны ли следующие суждения о культуре?\n\nА. Культуру можно рассматривать как уровень воспитанности отдельной личности.\nБ. Культура стала для человека второй природой.\n\n1) верно только А\n2) верно только Б\n3) верны оба суждения\n4) оба суждения неверны",
        "options": ["верно только А", "верно только Б", "верны оба суждения", "оба суждения неверны"],
        "correct": 2,
        "explanation": "✅ Верны оба суждения.",
        "topic": "Духовная культура",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 5,
        "text": "📸 <b>ФОТОГРАФИЯ:</b> Семья за праздничным столом.\n\nКакой тип семьи проиллюстрирован? Сформулируйте два суждения о роли семьи в жизни человека.",
        "correct_answers": ["Расширенная семья", "Эмоциональная поддержка", "Социализация детей"],
        "explanation": "✅ Расширенная семья.",
        "topic": "Социальная сфера",
        "points": 2,
        "type": "text"
    },
    {
        "id": 6,
        "text": "С Алексеем связался сотрудник банка и попросил назвать ПИН-код карты.\n\nОбъясните опасность ситуации. Как правильно поступить?",
        "correct_answers": ["Мошенничество", "Не сообщать ПИН-код", "Позвонить в банк"],
        "explanation": "✅ Это мошенники.",
        "topic": "Экономика",
        "points": 2,
        "type": "text"
    },
    {
        "id": 7,
        "text": "Вид косвенного налога, взимаемый с покупателя:\n\n1) НДФЛ\n2) таможенный сбор\n3) акциз\n4) дивиденд",
        "options": ["НДФЛ", "таможенный сбор", "акциз", "дивиденд"],
        "correct": 2,
        "explanation": "✅ Акциз.",
        "topic": "Экономика",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 8,
        "text": "Что относится к производству государством общественных благ?\n\n1) содержание армии\n2) выплата пенсий\n3) техрегламенты\n4) денежная эмиссия",
        "options": ["содержание армии", "выплата пенсий", "техрегламенты", "денежная эмиссия"],
        "correct": 0,
        "explanation": "✅ Общественные блага — оборона.",
        "topic": "Экономика",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 9,
        "text": "Верны ли суждения об издержках?\n\nА. Переменные издержки зависят от объема производства.\nБ. Плата за энергию — переменные издержки.\n\n1) верно А\n2) верно Б\n3) оба верны\n4) оба неверны",
        "options": ["верно А", "верно Б", "оба верны", "оба неверны"],
        "correct": 2,
        "explanation": "✅ Оба верны.",
        "topic": "Экономика",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 10,
        "text": "Какие термины относятся к «социальным нормам»?\n\n1) мышление, речь\n2) предупреждение, запрет\n3) воспитание, образование\n4) класс, сословие",
        "options": ["мышление, речь", "предупреждение, запрет", "воспитание, образование", "класс, сословие"],
        "correct": 1,
        "explanation": "✅ Предупреждение, запрет.",
        "topic": "Социальная сфера",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 11,
        "text": "Верны ли суждения об этносах?\n\nА. Этнос сочетает биологические и социальные свойства.\nБ. Этносы формируются только после государства.\n\n1) верно А\n2) верно Б\n3) оба верны\n4) оба неверны",
        "options": ["верно А", "верно Б", "оба верны", "оба неверны"],
        "correct": 0,
        "explanation": "✅ Верно только А.",
        "topic": "Социальная сфера",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 12,
        "text": "📊 <b>ДИАГРАММА:</b> Трудовое право - 65%, Гражданское право - 50%\n\nСформулируйте вывод.",
        "correct_answers": ["Трудовое и гражданское право важнее"],
        "explanation": "✅ Трудовое и гражданское право важнее.",
        "topic": "Право",
        "points": 3,
        "type": "text"
    },
    {
        "id": 13,
        "text": "Членам парламента запрещено работать в правительстве. Это:\n\n1) верховенство парламента\n2) республика\n3) унитарное государство\n4) разделение властей",
        "options": ["верховенство парламента", "республика", "унитарное государство", "разделение властей"],
        "correct": 3,
        "explanation": "✅ Разделение властей.",
        "topic": "Политика",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 14,
        "text": "Верны ли суждения о политических режимах?\n\nА. Недемократические режимы имеют альтернативные выборы.\nБ. В демократии — открытое голосование.\n\n1) верно А\n2) верно Б\n3) оба верны\n4) оба неверны",
        "options": ["верно А", "верно Б", "оба верны", "оба неверны"],
        "correct": 3,
        "explanation": "✅ Оба неверны.",
        "topic": "Политика",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 15,
        "text": "Установите соответствие:\n\nА) безбилетный проезд\nБ) опоздание на работу\n\n1) административная\n2) дисциплинарная",
        "correct_mapping": {"А": "1", "Б": "2"},
        "explanation": "✅ А-1, Б-2",
        "topic": "Право",
        "points": 2,
        "type": "text"
    },
    {
        "id": 16,
        "text": "Отрасль права, регулирующая имущественные отношения:\n\n1) семейное\n2) административное\n3) трудовое\n4) гражданское",
        "options": ["семейное", "административное", "трудовое", "гражданское"],
        "correct": 3,
        "explanation": "✅ Гражданское право.",
        "topic": "Право",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 17,
        "text": "Рабочая неделя для работников 16-18 лет:\n\n1) 40 ч\n2) 35 ч\n3) 24 ч\n4) 12 ч",
        "options": ["40 ч", "35 ч", "24 ч", "12 ч"],
        "correct": 1,
        "explanation": "✅ 35 часов.",
        "topic": "Право",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 18,
        "text": "Верны ли суждения о федеративном устройстве РФ?\n\nА. Образование и здравоохранение — в совместном ведении.\nБ. Гражданство РФ — в совместном ведении.\n\n1) верно А\n2) верно Б\n3) оба верны\n4) оба неверны",
        "options": ["верно А", "верно Б", "оба верны", "оба неверны"],
        "correct": 0,
        "explanation": "✅ Верно только А.",
        "topic": "Политика",
        "points": 1,
        "type": "choice"
    },
    {
        "id": 19,
        "text": "Сравните выборы и референдум.\n\n1) тайное голосование\n2) одобрение закона\n3) голосование за кандидатов\n4) только совершеннолетние\n\nЧерты сходства: __\nЧерты различия: __",
        "correct_mapping": {"similarities": [0, 3], "differences": [1, 2]},
        "explanation": "✅ Сходство: 1,4. Различие: 2,3.",
        "topic": "Политика",
        "points": 2,
        "type": "text"
    },
    {
        "id": 20,
        "text": "Пропущенное слово в таблице:\n\nПравовые нормы | установлены государством\nНормы ________ | представления о добре и зле",
        "correct": "морали",
        "explanation": "✅ Нормы морали.",
        "topic": "Право",
        "points": 1,
        "type": "text"
    },
    {
        "id": 21,
        "text": f"<b>ЗАДАНИЕ 21. Составьте план текста.</b>\n\n<b>ТЕКСТ:</b>\n{TEXT_FOR_21_24}\n\nВыделите основные смысловые фрагменты и озаглавьте каждый из них.",
        "correct_answers": ["Угроза природе", "Причины", "Значение", "Прогресс"],
        "explanation": "✅ План: 1) Угроза природе 2) Причины 3) Значение 4) Прогресс",
        "topic": "Человек и общество",
        "points": 2,
        "type": "text"
    },
    {
        "id": 22,
        "text": f"<b>ЗАДАНИЕ 22. Ответьте на вопросы.</b>\n\n<b>ТЕКСТ:</b>\n{TEXT_FOR_21_24}\n\n1) Назовите три глобальные проблемы.\n2) В чем основная экономическая проблема?",
        "correct_answers": ["Терроризм", "Демография", "Север-Юг", "Ограниченность ресурсов"],
        "explanation": "✅ Глобальные проблемы: терроризм, демография, Север-Юг.",
        "topic": "Человек и общество",
        "points": 3,
        "type": "text"
    },
    {
        "id": 23,
        "text": f"<b>ЗАДАНИЕ 23. Приведите примеры.</b>\n\n<b>ТЕКСТ:</b>\n{TEXT_FOR_21_24}\n\nОбъясните фразу о НТР. Приведите три примера.",
        "correct_answers": ["Атомная энергия", "Интернет", "ИИ"],
        "explanation": "✅ Атомная энергия, интернет, ИИ.",
        "topic": "Человек и общество",
        "points": 3,
        "type": "text"
    },
    {
        "id": 24,
        "text": f"<b>ЗАДАНИЕ 24. Аргументируйте.</b>\n\n<b>ТЕКСТ:</b>\n{TEXT_FOR_21_24}\n\nВозможно ли преодолеть разрыв между странами? Два аргумента.",
        "correct_answers": ["Невозможно", "Разные условия"],
        "explanation": "✅ Невозможно полностью.",
        "topic": "Человек и общество",
        "points": 3,
        "type": "text"
    }
]

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    buttons = [
        "📚 ТЕОРИЯ", 
        "🎯 ЗАДАНИЯ",
        "📝 ВАРИАНТ ОГЭ",
        "🏆 ДОСТИЖЕНИЯ",
        "📊 СТАТИСТИКА",
        "🔄 ПОВТОРИТЬ"
    ]
    for button in buttons:
        builder.add(KeyboardButton(text=button))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_theory_keyboard():
    builder = InlineKeyboardBuilder()
    for topic, key in TOPIC_KEYS.items():
        builder.button(text=f"📘 {topic}", callback_data=f"t_{key}")
    builder.button(text="🔙 НАЗАД", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()

def get_subtopics_keyboard(topic_key):
    builder = InlineKeyboardBuilder()
    topic = None
    for t, k in TOPIC_KEYS.items():
        if k == topic_key:
            topic = t
            break
    
    if topic and topic in THEORY_DETAILED:
        for i, subtopic in enumerate(THEORY_DETAILED[topic].keys(), 1):
            key = f"s{topic_key[1]}{i}"
            builder.button(text=f"📖 {subtopic}", callback_data=f"s_{key}")
    builder.button(text="◀️ НАЗАД К ТЕМАМ", callback_data="back_theory")
    builder.adjust(1)
    return builder.as_markup()

def get_tasks_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(1, 25):
        builder.button(text=f"{i}", callback_data=f"task_{i}")
    builder.button(text="🎲 СЛУЧАЙНОЕ", callback_data="random_task")
    builder.button(text="🔙 НАЗАД", callback_data="back_main")
    builder.adjust(6)
    return builder.as_markup()

def get_question_keyboard(qid, qtype, exam_mode=False):
    builder = InlineKeyboardBuilder()
    if qtype == "choice":
        builder.button(text="🔘 ВЫБРАТЬ ОТВЕТ", callback_data=f"opt_{qid}")
    else:
        builder.button(text="📝 НАПИСАТЬ ОТВЕТ", callback_data=f"ans_{qid}")
    
    if not exam_mode:
        topic = OGE_QUESTIONS[qid-1]['topic']
        topic_key = TOPIC_KEYS.get(topic, "t1")
        builder.button(text="📚 ТЕОРИЯ", callback_data=f"t_{topic_key}")
        builder.button(text="🎲 СЛУЧАЙНОЕ", callback_data="random_task")
        builder.adjust(1, 2)
    return builder.as_markup()

def get_options_keyboard(options, qid):
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(options):
        builder.button(text=f"{i+1}. {opt}", callback_data=f"sel_{qid}_{i}")
    builder.button(text="🔙 НАЗАД", callback_data=f"task_{qid}")
    builder.adjust(1)
    return builder.as_markup()

def get_after_answer_keyboard(exam_mode=False):
    builder = InlineKeyboardBuilder()
    if exam_mode:
        builder.button(text="➡️ ПРОДОЛЖИТЬ ВАРИАНТ", callback_data="next_exam")
    else:
        builder.button(text="📋 К ЗАДАНИЯМ", callback_data="back_to_tasks")
        builder.button(text="🎲 СЛУЧАЙНОЕ", callback_data="random_task")
        builder.adjust(2)
    return builder.as_markup()

def get_achievements_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎖️ МОИ ДОСТИЖЕНИЯ", callback_data="my_achievements")
    builder.button(text="📈 ПРОГРЕСС", callback_data="my_progress")
    builder.button(text="🔙 НАЗАД", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user = get_user_state(message.from_user.id)
    user.update_daily_streak()
    prog = user.get_progress_summary()
    
    await message.answer(
        f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
        f"📚 <b>БОТ ДЛЯ ПОДГОТОВКИ К ОГЭ</b>\n\n"
        f"✅ 6 тем теории - ВСЕ РАБОТАЮТ!\n"
        f"✅ 24 задания ОГЭ\n"
        f"✅ Полные тексты 21-24\n\n"
        f"🏆 Ваш прогресс: {prog['total_questions']} заданий, {prog['accuracy']}%",
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda m: m.text == "📚 ТЕОРИЯ")
async def theory_menu(m: Message):
    await m.answer("📚 <b>ВЫБЕРИТЕ ТЕМУ:</b>", reply_markup=get_theory_keyboard())

@dp.message(lambda m: m.text == "🎯 ЗАДАНИЯ")
async def tasks_menu(m: Message):
    await m.answer("🎯 <b>ВЫБЕРИТЕ НОМЕР ЗАДАНИЯ (1-24):</b>", reply_markup=get_tasks_keyboard())

@dp.message(lambda m: m.text == "📝 ВАРИАНТ ОГЭ")
async def exam_start(m: Message):
    user = get_user_state(m.from_user.id)
    user.current_exam = [q.copy() for q in OGE_QUESTIONS]
    user.current_exam_index = 0
    user.exam_score = 0
    await m.answer("📝 <b>НАЧИНАЕМ ВАРИАНТ ОГЭ!</b>\n\nЗадание 1/24:")
    await send_question(m.from_user.id, user.current_exam[0], exam_mode=True)

@dp.message(lambda m: m.text == "🏆 ДОСТИЖЕНИЯ")
async def achievements_menu(m: Message):
    await m.answer("🏆 <b>ДОСТИЖЕНИЯ</b>", reply_markup=get_achievements_keyboard())

@dp.message(lambda m: m.text == "📊 СТАТИСТИКА")
async def stats_menu(m: Message):
    user = get_user_state(m.from_user.id)
    prog = user.get_progress_summary()
    await m.answer(f"📊 СТАТИСТИКА\n\n✅ Заданий: {prog['total_questions']}\n🎯 Точность: {prog['accuracy']}%")

@dp.message(lambda m: m.text == "🔄 ПОВТОРИТЬ")
async def repeat_menu(m: Message):
    user = get_user_state(m.from_user.id)
    weak = user.get_weak_topics(2)
    if weak:
        text = "📚 ПОВТОРИТЕ:\n"
        kb = InlineKeyboardBuilder()
        for t in weak:
            text += f"• {t['topic']}\n"
            kb.button(text=f"📘 {t['topic']}", callback_data=f"t_{TOPIC_KEYS[t['topic']]}")
        kb.button(text="🔙 НАЗАД", callback_data="back_main")
        kb.adjust(1)
        await m.answer(text, reply_markup=kb.as_markup())
    else:
        await m.answer("✅ Все темы освоены!")

# ========== CALLBACKS ==========
@dp.callback_query(lambda c: c.data == "back_main")
async def cb_back_main(c: CallbackQuery):
    await c.message.delete()
    await c.message.answer("Главное меню:", reply_markup=get_main_keyboard())
    await c.answer()

@dp.callback_query(lambda c: c.data == "back_theory")
async def cb_back_theory(c: CallbackQuery):
    await c.message.edit_text("📚 <b>ВЫБЕРИТЕ ТЕМУ:</b>", reply_markup=get_theory_keyboard())
    await c.answer()

@dp.callback_query(lambda c: c.data == "back_to_tasks")
async def cb_back_to_tasks(c: CallbackQuery):
    await c.message.delete()
    await c.message.answer("🎯 <b>ВЫБЕРИТЕ НОМЕР ЗАДАНИЯ (1-24):</b>", reply_markup=get_tasks_keyboard())
    await c.answer()

# ========== ОБРАБОТЧИК ТЕМ - РАБОТАЕТ! ==========
@dp.callback_query(lambda c: c.data.startswith("t_"))
async def cb_theory_topic(c: CallbackQuery):
    key = c.data[2:]  # t_t1 -> t1
    topic = None
    for t, k in TOPIC_KEYS.items():
        if k == key:
            topic = t
            break
    
    if topic:
        await c.message.edit_text(
            f"📚 <b>{topic}</b>\n\nВыберите подтему:",
            reply_markup=get_subtopics_keyboard(key)
        )
    await c.answer()

# ========== ОБРАБОТЧИК ПОДТЕМ - РАБОТАЕТ! ==========
@dp.callback_query(lambda c: c.data.startswith("s_"))
async def cb_subtopic(c: CallbackQuery):
    key = c.data[2:]  # s_11 -> s11
    if key in SUBTOPIC_KEYS:
        topic, subtopic = SUBTOPIC_KEYS[key]
        data = THEORY_DETAILED[topic][subtopic]
        
        text = f"📖 <b>{subtopic}</b>\n\n"
        text += f"📌 <b>Определение:</b>\n{data['definition']}\n\n"
        text += f"🔑 <b>Ключевые моменты:</b>\n"
        for p in data['key_points']:
            text += f"• {p}\n"
        text += f"\n🎯 <b>Примеры:</b>\n"
        for e in data['examples']:
            text += f"• {e}\n"
        text += f"\n❓ <b>Вопросы:</b>\n"
        for i, q in enumerate(data['questions'], 1):
            text += f"{i}. {q}\n"
        
        kb = InlineKeyboardBuilder()
        kb.button(text="◀️ НАЗАД", callback_data=f"t_{TOPIC_KEYS[topic]}")
        await c.message.edit_text(text, reply_markup=kb.as_markup())
    await c.answer()

# ========== ОСТАЛЬНЫЕ ОБРАБОТЧИКИ ==========
@dp.callback_query(lambda c: c.data.startswith("task_"))
async def cb_task(c: CallbackQuery):
    try:
        num = int(c.data.replace("task_", ""))
        if 1 <= num <= 24:
            q = OGE_QUESTIONS[num-1].copy()
            user = get_user_state(c.from_user.id)
            user.current_question = q
            await send_question(c.from_user.id, q, c.message, exam_mode=False)
    except:
        await c.answer("❌ Ошибка", True)
    await c.answer()

@dp.callback_query(lambda c: c.data == "random_task")
async def cb_random_task(c: CallbackQuery):
    q = random.choice(OGE_QUESTIONS).copy()
    user = get_user_state(c.from_user.id)
    user.current_question = q
    await send_question(c.from_user.id, q, c.message, exam_mode=False)
    await c.answer()

@dp.callback_query(lambda c: c.data.startswith("opt_"))
async def cb_show_options(c: CallbackQuery):
    qid = int(c.data.replace("opt_", ""))
    for q in OGE_QUESTIONS:
        if q["id"] == qid and "options" in q:
            await c.message.edit_reply_markup(reply_markup=get_options_keyboard(q["options"], qid))
            await c.answer()
            return

@dp.callback_query(lambda c: c.data.startswith("sel_"))
async def cb_select_option(c: CallbackQuery):
    data = c.data.replace("sel_", "").split("_")
    if len(data) != 2:
        await c.answer()
        return
    
    qid = int(data[0])
    ans = int(data[1])
    user = get_user_state(c.from_user.id)
    user.update_daily_streak()
    
    for q in OGE_QUESTIONS:
        if q["id"] == qid:
            correct = ans == q["correct"]
            points = q["points"] if correct else 0
            
            exam_mode = bool(user.current_exam)
            if exam_mode:
                user.exam_score += points
            
            user.add_result(correct, points, q["topic"])
            
            text = f"{'✅ ПРАВИЛЬНО!' if correct else '❌ НЕПРАВИЛЬНО'}\n\n"
            text += f"<b>Ваш ответ:</b> {ans+1}\n"
            text += f"<b>Правильный ответ:</b> {q['correct']+1}\n\n"
            text += f"<b>Объяснение:</b> {q['explanation']}\n\n"
            text += f"📊 Правильных: {user.correct_answers}\n"
            text += f"⭐ Баллов: {user.score}"
            
            await c.message.edit_text(
                text, 
                reply_markup=get_after_answer_keyboard(exam_mode)
            )
            await c.answer()
            return

@dp.callback_query(lambda c: c.data.startswith("ans_"))
async def cb_text_answer(c: CallbackQuery):
    qid = int(c.data.replace("ans_", ""))
    user = get_user_state(c.from_user.id)
    user.waiting_for_answer = True
    
    for q in OGE_QUESTIONS:
        if q["id"] == qid:
            user.current_question = q
            await c.message.answer("📝 <b>Напишите ответ в чат:</b>")
            await c.answer()
            return

@dp.callback_query(lambda c: c.data == "next_exam")
async def cb_next_exam(c: CallbackQuery):
    user = get_user_state(c.from_user.id)
    if user.current_exam:
        if user.current_exam_index < len(user.current_exam) - 1:
            user.current_exam_index += 1
            await send_question(
                c.from_user.id, 
                user.current_exam[user.current_exam_index], 
                c.message, 
                exam_mode=True
            )
        else:
            total = sum(q["points"] for q in user.current_exam)
            acc = (user.exam_score / total * 100) if total > 0 else 0
            
            text = f"🏆 <b>ВАРИАНТ ЗАВЕРШЕН!</b>\n\n✅ Баллов: {user.exam_score}/{total}\n🎯 Точность: {acc:.1f}%"
            
            if user.exam_score >= 25:
                user.achievements["oge_master"]["unlocked"] = True
                text += "\n🏅 Мастер ОГЭ!"
            
            user.exam_results.append(user.exam_score)
            user.current_exam = None
            
            kb = InlineKeyboardBuilder()
            kb.button(text="🏠 МЕНЮ", callback_data="back_main")
            await c.message.answer(text, reply_markup=kb.as_markup())
    await c.answer()

@dp.callback_query(lambda c: c.data == "my_achievements")
async def cb_my_achievements(c: CallbackQuery):
    user = get_user_state(c.from_user.id)
    text = "🏆 ДОСТИЖЕНИЯ:\n\n"
    unlocked = 0
    
    for ach in user.achievements.values():
        if ach["unlocked"]:
            text += f"{ach['icon']} {ach['name']} - ✅\n"
            unlocked += 1
        else:
            text += f"🔒 {ach['name']}\n"
    
    text += f"\nИтого: {unlocked}/{len(user.achievements)}"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 НАЗАД", callback_data="back_achievements")
    await c.message.edit_text(text, reply_markup=kb.as_markup())
    await c.answer()

@dp.callback_query(lambda c: c.data == "my_progress")
async def cb_my_progress(c: CallbackQuery):
    user = get_user_state(c.from_user.id)
    prog = user.get_progress_summary()
    
    text = f"📊 ПРОГРЕСС:\n\n🎯 Точность: {prog['accuracy']}%\n⭐ Баллов: {prog['total_score']}\n✅ Решено: {prog['total_questions']}\n📚 Тем: {prog['topics_mastered']}/{prog['total_topics']}"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 НАЗАД", callback_data="back_achievements")
    await c.message.edit_text(text, reply_markup=kb.as_markup())
    await c.answer()

@dp.callback_query(lambda c: c.data == "back_achievements")
async def cb_back_achievements(c: CallbackQuery):
    await c.message.edit_text("🏆 <b>ДОСТИЖЕНИЯ</b>", reply_markup=get_achievements_keyboard())
    await c.answer()

# ========== ОТПРАВКА ВОПРОСА ==========
async def send_question(user_id, question, msg=None, exam_mode=False):
    user = get_user_state(user_id)
    user.current_question = question
    user.waiting_for_answer = False
    
    if exam_mode:
        num = user.current_exam_index + 1
        header = f"<b>📝 ВАРИАНТ ОГЭ | Задание {num}/24</b>\n\n"
    else:
        header = f"<b>🎯 ЗАДАНИЕ №{question['id']}</b>\n\n"
    
    text = header + f"📚 {question['topic']}\n⭐ {question['points']} баллов\n\n{question['text']}"
    
    kb = get_question_keyboard(question['id'], question['type'], exam_mode)
    
    if msg:
        await msg.edit_text(text, reply_markup=kb)
    else:
        await bot.send_message(user_id, text, reply_markup=kb)

# ========== ПРОВЕРКА ОТВЕТОВ ==========
def check_text_answer(q, ans):
    ans_lower = ans.lower()
    
    if q["id"] == 1:
        return "федерация" in ans_lower and "государство" in ans_lower
    elif q["id"] == 5:
        return "расширен" in ans_lower
    elif q["id"] == 6:
        return "мошен" in ans_lower
    elif q["id"] == 12:
        return "трудов" in ans_lower and "граждан" in ans_lower
    elif q["id"] == 15:
        return "1" in ans and "2" in ans
    elif q["id"] == 19:
        return "1" in ans and "4" in ans and "2" in ans and "3" in ans
    elif q["id"] == 20:
        return "морал" in ans_lower
    elif q["id"] == 21:
        return len(ans.split("\n")) >= 3
    elif q["id"] == 22:
        return len(ans.split()) >= 20
    elif q["id"] == 23:
        return len(ans.split()) >= 30
    elif q["id"] == 24:
        return len(ans.split()) >= 30
    return False

# ========== ТЕКСТОВЫЕ СООБЩЕНИЯ ==========
@dp.message()
async def handle_text(m: Message):
    if m.text.startswith("/"):
        return
    
    user = get_user_state(m.from_user.id)
    user.update_daily_streak()
    
    if user.waiting_for_answer and user.current_question:
        q = user.current_question
        ans = m.text.strip()
        
        if ans:
            correct = check_text_answer(q, ans)
            points = q["points"] if correct else 0
            
            exam_mode = bool(user.current_exam)
            if exam_mode:
                user.exam_score += points
            
            user.add_result(correct, points, q["topic"])
            user.waiting_for_answer = False
            
            text = f"{'✅ ПРАВИЛЬНО!' if correct else '❌ НЕПРАВИЛЬНО'}\n\n"
            text += f"<b>Ваш ответ:</b> {ans[:100]}\n\n"
            text += f"<b>Объяснение:</b> {q['explanation']}\n\n"
            text += f"📊 Правильных: {user.correct_answers}\n⭐ Баллов: {user.score}"
            
            await m.answer(text, reply_markup=get_after_answer_keyboard(exam_mode))
        return
    
    if m.text.strip().isdigit():
        num = int(m.text.strip())
        if user.current_question and "options" in user.current_question:
            if 1 <= num <= len(user.current_question["options"]):
                q = user.current_question
                correct = (num - 1) == q["correct"]
                points = q["points"] if correct else 0
                
                exam_mode = bool(user.current_exam)
                if exam_mode:
                    user.exam_score += points
                
                user.add_result(correct, points, q["topic"])
                
                text = f"{'✅ ПРАВИЛЬНО!' if correct else '❌ НЕПРАВИЛЬНО'}\n\n"
                text += f"<b>Ваш ответ:</b> {num}\n"
                text += f"<b>Правильный ответ:</b> {q['correct'] + 1}\n\n"
                text += f"<b>Объяснение:</b> {q['explanation']}\n\n"
                text += f"📊 Правильных: {user.correct_answers}\n⭐ Баллов: {user.score}"
                
                user.waiting_for_answer = False
                await m.answer(text, reply_markup=get_after_answer_keyboard(exam_mode))
                return

# ========== ЗАПУСК ==========
async def main():
    print("=" * 50)
    print("🤖 ЗАПУСК БОТА")
    print("=" * 50)
    print(f"✅ Токен: Установлен")
    print(f"📚 Теория: 6 тем, КОРОТКИЕ CALLBACK - РАБОТАЕТ!")
    print(f"   - t1..t6 - темы")
    print(f"   - s11..s62 - подтемы")
    print(f"🎯 Задания: 24 шт")
    print(f"🔄 Кнопки: К ЗАДАНИЯМ / ПРОДОЛЖИТЬ ВАРИАНТ")
    print("=" * 50)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())


