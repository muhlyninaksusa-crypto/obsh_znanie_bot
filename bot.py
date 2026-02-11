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

# ========== ТЕМЫ С ПОДТЕМАМИ ==========
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
                "Рыночная экономика: США, страны Европы",
                "Командная экономика: СССР"
            ],
            "questions": [
                "Какие три основных вопроса решает экономика?",
                "Назовите типы экономических систем"
            ]
        },
        "Налоги и бюджет": {
            "definition": "Налоги — это обязательные платежи физических и юридических лиц государству.",
            "key_points": [
                "Прямые налоги: подоходный, налог на прибыль",
                "Косвенные налоги: НДС, акцизы",
                "Бюджет — план доходов и расходов"
            ],
            "examples": [
                "Прямой налог: НДФЛ 13%",
                "Косвенный налог: НДС 20%"
            ],
            "questions": [
                "Чем прямые налоги отличаются от косвенных?",
                "Что такое бюджет?"
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
        },
        "Семья как социальный институт": {
            "definition": "Семья — это малая социальная группа, основанная на браке или кровном родстве.",
            "key_points": [
                "Функции семьи: репродуктивная, воспитательная, хозяйственная, эмоциональная",
                "Типы семей: нуклеарная, расширенная",
                "Брак — юридически оформленный союз"
            ],
            "examples": [
                "Нуклеарная семья: родители + дети",
                "Расширенная семья: несколько поколений"
            ],
            "questions": [
                "Назовите функции семьи",
                "Чем нуклеарная семья отличается от расширенной?"
            ]
        }
    },
    "Политика": {
        "Государство и его функции": {
            "definition": "Государство — это организация политической власти, управляющая обществом на определенной территории.",
            "key_points": [
                "Признаки государства: территория, население, суверенитет, налоги",
                "Функции: внутренние (порядок) и внешние (оборона)",
                "Формы государства: монархия, республика"
            ],
            "examples": [
                "Монархия: Великобритания, Япония",
                "Республика: Россия, США, Франция"
            ],
            "questions": [
                "Назовите признаки государства",
                "Чем монархия отличается от республики?"
            ]
        },
        "Разделение властей": {
            "definition": "Разделение властей — принцип, согласно которому государственная власть делится на независимые ветви.",
            "key_points": [
                "Законодательная власть: парламент",
                "Исполнительная власть: правительство",
                "Судебная власть: суды"
            ],
            "examples": [
                "Законодательная: Федеральное Собрание РФ",
                "Исполнительная: Правительство РФ",
                "Судебная: Конституционный суд РФ"
            ],
            "questions": [
                "Какие ветви власти вы знаете?",
                "Что такое разделение властей?"
            ]
        }
    },
    "Право": {
        "Отрасли права": {
            "definition": "Отрасль права — совокупность правовых норм, регулирующих определенную сферу общественных отношений.",
            "key_points": [
                "Гражданское право: имущественные и личные неимущественные отношения",
                "Административное право: отношения в сфере управления",
                "Трудовое право: отношения между работником и работодателем"
            ],
            "examples": [
                "Гражданское право: договор купли-продажи",
                "Административное право: нарушение ПДД",
                "Трудовое право: трудовой договор"
            ],
            "questions": [
                "Что регулирует гражданское право?",
                "Что такое административное правонарушение?"
            ]
        },
        "Юридическая ответственность": {
            "definition": "Юридическая ответственность — применение мер государственного принуждения за правонарушение.",
            "key_points": [
                "Административная ответственность: штрафы",
                "Дисциплинарная ответственность: замечание, выговор",
                "Гражданско-правовая ответственность: возмещение ущерба"
            ],
            "examples": [
                "Административная: штраф за безбилетный проезд",
                "Дисциплинарная: выговор за опоздание",
                "Гражданско-правовая: возмещение ущерба имуществу"
            ],
            "questions": [
                "Какие виды юридической ответственности вы знаете?",
                "Чем административная ответственность отличается от дисциплинарной?"
            ]
        }
    },
    "Духовная культура": {
        "Культура и её формы": {
            "definition": "Культура — это все материальные и духовные ценности, созданные человечеством.",
            "key_points": [
                "Материальная культура: здания, техника, одежда",
                "Духовная культура: наука, искусство, религия, мораль",
                "Функции культуры: познавательная, воспитательная"
            ],
            "examples": [
                "Материальная культура: Эрмитаж, Кремль",
                "Духовная культура: роман «Война и мир»"
            ],
            "questions": [
                "Чем материальная культура отличается от духовной?",
                "Каковы функции культуры?"
            ]
        },
        "Образование": {
            "definition": "Образование — целенаправленный процесс воспитания и обучения в интересах человека и общества.",
            "key_points": [
                "Уровни образования: дошкольное, общее, профессиональное",
                "Общее образование: начальное, основное, среднее",
                "Профессиональное образование: среднее, высшее"
            ],
            "examples": [
                "Основное общее образование: 9 классов",
                "Среднее общее образование: 11 классов",
                "Высшее образование: бакалавриат, магистратура"
            ],
            "questions": [
                "Какие уровни образования существуют в России?",
                "Что такое основное общее образование?"
            ]
        }
    }
}

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
        "description": "Пройти все темы",
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

# ========== ТЕКСТ ДЛЯ ЗАДАНИЙ 21-24 ==========
COMMON_TEXT = """
«Под угрозой сейчас находится большинство оставшихся высших видов растений и животных. Те из них, которые человек избрал для удовлетворения своих потребностей, давно уже приспособлены к его требованиям, но дикие виды, для которых нет места в мире человека, обречены. Их погубят не только охота и истребление, но и сведение лесов под поля, шахты, дороги, а главное — превращение обширных участков дикой природы в города и промышленные комплексы.

Человек, придя в будущее, должен иметь возможность увидеть Землю не только как всеобщую стройплощадку и всеобщую ферму, но и как дикую природу, оставшуюся нетронутой. Она необходима и как среда обитания самого человека, поскольку он биологически сформировался в естественной, открытой среде. Она необходима и для этического воспитания человека: ничто так не воспитывает доброту, как контакт с дикой природой.

Забота о сохранении дикой природы — неотъемлемая часть развития цивилизации, обязательное условие прогресса.»
"""

# ========== ВСЕ 24 ЗАДАНИЯ ОГЭ В ПРАВИЛЬНОМ ПОРЯДКЕ ==========
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
    # ЗАДАНИЕ 2
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
    # ЗАДАНИЕ 3
    {
        "id": 3,
        "text": "Виталий учится в 8 классе гимназии. На какой образовательной ступени находится Виталий?\n\n1) среднее профессиональное образование\n2) основное общее образование\n3) среднее общее образование\n4) начальное общее образование",
        "options": ["среднее профессиональное образование", "основное общее образование", "среднее общее образование", "начальное общее образование"],
        "correct": 1,
        "explanation": "✅ Правильно: основное общее образование. 8 класс — это основное общее образование.",
        "topic": "Духовная культура",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 4
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
    # ЗАДАНИЕ 5
    {
        "id": 5,
        "text": "📸 ФОТОГРАФИЯ: Семья за праздничным столом: родители, двое детей, бабушка и дедушка.\n\nКакой тип семьи проиллюстрирован? Сформулируйте два суждения о роли семьи в жизни человека.",
        "correct_answers": ["Расширенная семья", "Эмоциональная поддержка", "Социализация детей"],
        "explanation": "✅ Расширенная семья. Роль семьи: эмоциональная поддержка и социализация детей.",
        "topic": "Социальная сфера",
        "points": 2,
        "type": "text"
    },
    # ЗАДАНИЕ 6
    {
        "id": 6,
        "text": "С Алексеем связался сотрудник банка и попросил назвать ПИН-код карты.\n\nОбъясните опасность ситуации. Как правильно поступить?",
        "correct_answers": ["Мошенничество", "Не сообщать ПИН-код", "Позвонить в банк"],
        "explanation": "✅ Это мошенники. Настоящие сотрудники банка никогда не спрашивают ПИН-код.",
        "topic": "Экономика",
        "points": 2,
        "type": "text"
    },
    # ЗАДАНИЕ 7
    {
        "id": 7,
        "text": "Вид косвенного налога, взимаемый с покупателя при приобретении некоторых товаров:\n\n1) НДФЛ\n2) таможенный сбор\n3) акциз\n4) дивиденд",
        "options": ["НДФЛ", "таможенный сбор", "акциз", "дивиденд"],
        "correct": 2,
        "explanation": "✅ Акциз — косвенный налог на алкоголь, табак, бензин.",
        "topic": "Экономика",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 8
    {
        "id": 8,
        "text": "Что относится к производству государством общественных благ?\n\n1) содержание армии\n2) выплата пенсий\n3) техрегламенты\n4) денежная эмиссия",
        "options": ["содержание армии", "выплата пенсий", "техрегламенты", "денежная эмиссия"],
        "correct": 0,
        "explanation": "✅ Общественные блага — оборона, охрана порядка, доступные всем.",
        "topic": "Экономика",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 9
    {
        "id": 9,
        "text": "Верны ли суждения об издержках?\n\nА. Переменные издержки зависят от объема производства.\nБ. Плата за энергию — переменные издержки.\n\n1) верно А\n2) верно Б\n3) оба верны\n4) оба неверны",
        "options": ["верно А", "верно Б", "оба верны", "оба неверны"],
        "correct": 2,
        "explanation": "✅ Оба суждения верны.",
        "topic": "Экономика",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 10
    {
        "id": 10,
        "text": "Какие термины относятся к «социальным нормам»?\n\n1) мышление, речь\n2) предупреждение, запрет\n3) воспитание, образование\n4) класс, сословие",
        "options": ["мышление, речь", "предупреждение, запрет", "воспитание, образование", "класс, сословие"],
        "correct": 1,
        "explanation": "✅ Предупреждение и запрет — санкции социальных норм.",
        "topic": "Социальная сфера",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 11
    {
        "id": 11,
        "text": "Верны ли суждения об этносах?\n\nА. Этнос сочетает биологические и социальные свойства.\nБ. Этносы формируются только после государства.\n\n1) верно А\n2) верно Б\n3) оба верны\n4) оба неверны",
        "options": ["верно А", "верно Б", "оба верны", "оба неверны"],
        "correct": 0,
        "explanation": "✅ Верно только А. Этносы существовали до государства.",
        "topic": "Социальная сфера",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 12
    {
        "id": 12,
        "text": "📊 ДИАГРАММА: Трудовое право - 65%, Гражданское право - 50%, Административное право - 30%, Уголовное право - 25%\n\nСформулируйте вывод о сходстве и различии. Объясните причины.",
        "correct_answers": ["Трудовое и гражданское право важнее", "Разные проценты", "Нужны в повседневной жизни", "Разный опыт людей"],
        "explanation": "✅ Трудовое и гражданское право важнее в повседневной жизни.",
        "topic": "Право",
        "points": 3,
        "type": "text"
    },
    # ЗАДАНИЕ 13
    {
        "id": 13,
        "text": "Членам парламента запрещено работать в правительстве. Это:\n\n1) верховенство парламента\n2) республика\n3) унитарное государство\n4) разделение властей",
        "options": ["верховенство парламента", "республика", "унитарное государство", "разделение властей"],
        "correct": 3,
        "explanation": "✅ Разделение властей: запрет совмещать должности в разных ветвях власти.",
        "topic": "Политика",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 14
    {
        "id": 14,
        "text": "Верны ли суждения о политических режимах?\n\nА. Недемократические режимы имеют альтернативные выборы.\nБ. В демократии — открытое голосование.\n\n1) верно А\n2) верно Б\n3) оба верны\n4) оба неверны",
        "options": ["верно А", "верно Б", "оба верны", "оба неверны"],
        "correct": 3,
        "explanation": "✅ Оба суждения неверны. В недемократиях выборы безальтернативны, в демократии — тайное голосование.",
        "topic": "Политика",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 15
    {
        "id": 15,
        "text": "Соответствие: правонарушение — ответственность\n\nА) безбилетный проезд\nБ) опоздание на работу\nВ) нарушение пожарной безопасности\nГ) увольнение без отработки\nД) ущерб имуществу фирмы\n\n1) административная\n2) дисциплинарная\n\nОтвет: А-_, Б-_, В-_, Г-_, Д-_",
        "correct_mapping": {"А": "1", "Б": "2", "В": "1", "Г": "2", "Д": "2"},
        "explanation": "✅ А-1, Б-2, В-1, Г-2, Д-2",
        "topic": "Право",
        "points": 2,
        "type": "text"
    },
    # ЗАДАНИЕ 16
    {
        "id": 16,
        "text": "Отрасль права, регулирующая имущественные отношения:\n\n1) семейное\n2) административное\n3) трудовое\n4) гражданское",
        "options": ["семейное", "административное", "трудовое", "гражданское"],
        "correct": 3,
        "explanation": "✅ Гражданское право регулирует имущественные отношения.",
        "topic": "Право",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 17
    {
        "id": 17,
        "text": "Рабочая неделя для работников 16-18 лет:\n\n1) 40 ч\n2) 35 ч\n3) 24 ч\n4) 12 ч",
        "options": ["40 ч", "35 ч", "24 ч", "12 ч"],
        "correct": 1,
        "explanation": "✅ 35 часов в неделю для несовершеннолетних 16-18 лет.",
        "topic": "Право",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 18
    {
        "id": 18,
        "text": "Верны ли суждения о федеративном устройстве РФ?\n\nА. Образование и здравоохранение — в совместном ведении.\nБ. Гражданство РФ — в совместном ведении.\n\n1) верно А\n2) верно Б\n3) оба верны\n4) оба неверны",
        "options": ["верно А", "верно Б", "оба верны", "оба неверны"],
        "correct": 0,
        "explanation": "✅ Верно только А. Гражданство — в исключительном ведении РФ.",
        "topic": "Политика",
        "points": 1,
        "type": "choice"
    },
    # ЗАДАНИЕ 19
    {
        "id": 19,
        "text": "Сравните выборы и референдум.\n\n1) тайное голосование\n2) одобрение закона\n3) голосование за кандидатов\n4) только совершеннолетние\n\nСходство: __\nРазличие: __",
        "correct_mapping": {"similarities": [0, 3], "differences": [1, 2]},
        "explanation": "✅ Сходство: 1,4. Различие: 2,3.",
        "topic": "Политика",
        "points": 2,
        "type": "text"
    },
    # ЗАДАНИЕ 20
    {
        "id": 20,
        "text": "Пропущенное слово в таблице:\n\nПравовые нормы | установлены государством\nНормы ________ | представления о добре и зле",
        "correct": "морали",
        "explanation": "✅ Нормы морали — представления о добре и зле.",
        "topic": "Право",
        "points": 1,
        "type": "text"
    },
    # ЗАДАНИЕ 21
    {
        "id": 21,
        "text": f"Прочитайте текст и выполните задания 21-24.\n\n<b>ТЕКСТ:</b>{COMMON_TEXT}\n\n<b>Задание 21.</b> Составьте план текста.",
        "correct_answers": ["Угроза природе", "Причины исчезновения", "Значение природы", "Условие прогресса"],
        "explanation": "✅ План: 1) Угроза дикой природе 2) Причины исчезновения 3) Значение природы 4) Забота о природе",
        "topic": "Человек и общество",
        "points": 2,
        "type": "text"
    },
    # ЗАДАНИЕ 22
    {
        "id": 22,
        "text": f"Прочитайте текст (задание 21).\n\n<b>Задание 22.</b> Назовите три глобальные проблемы, не упомянутые в тексте. В чем основная экономическая проблема?",
        "correct_answers": ["Терроризм", "Демография", "Север-Юг", "Ограниченность ресурсов", "Рост потребностей"],
        "explanation": "✅ Глобальные проблемы: терроризм, демография, разрыв в развитии. Экономическая проблема: ограниченность ресурсов.",
        "topic": "Человек и общество",
        "points": 3,
        "type": "text"
    },
    # ЗАДАНИЕ 23
    {
        "id": 23,
        "text": f"Прочитайте текст (задание 21).\n\n<b>Задание 23.</b> Объясните смысл фразы о НТР. Приведите три примера.",
        "correct_answers": ["Атомная энергия - оружие и аварии", "Интернет - доступ и зависимость", "ИИ - автоматизация и безработица"],
        "explanation": "✅ НТР дает технологии, но не мудрость. Примеры: атомная энергия, интернет, ИИ.",
        "topic": "Человек и общество",
        "points": 3,
        "type": "text"
    },
    # ЗАДАНИЕ 24
    {
        "id": 24,
        "text": f"Прочитайте текст (задание 21).\n\n<b>Задание 24.</b> Возможно ли преодолеть разрыв между развитыми и слаборазвитыми странами? Два аргумента.",
        "correct_answers": ["Невозможно полностью", "Разные стартовые условия", "Незаинтересованность развитых стран"],
        "explanation": "✅ Полностью преодолеть разрыв в ближайшем будущем невозможно.",
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
    for topic in THEORY_DETAILED.keys():
        builder.button(text=f"📘 {topic}", callback_data=f"topic_{topic}")
    builder.button(text="🔙 НАЗАД", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()

def get_subtopics_keyboard(topic):
    builder = InlineKeyboardBuilder()
    for subtopic in THEORY_DETAILED[topic].keys():
        builder.button(text=f"📖 {subtopic}", callback_data=f"subtopic_{topic}_{subtopic}")
    builder.button(text="◀️ НАЗАД", callback_data="theory")
    builder.adjust(1)
    return builder.as_markup()

def get_tasks_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(1, 25):
        builder.button(text=f"{i}", callback_data=f"task_{i}")
    builder.button(text="🎲 СЛУЧАЙНОЕ", callback_data="random")
    builder.button(text="🔙 НАЗАД", callback_data="menu")
    builder.adjust(6)
    return builder.as_markup()

def get_question_keyboard(qid, qtype, exam=False):
    builder = InlineKeyboardBuilder()
    if qtype == "choice":
        builder.button(text="🔘 ВЫБРАТЬ ОТВЕТ", callback_data=f"options_{qid}")
    else:
        builder.button(text="📝 НАПИСАТЬ ОТВЕТ", callback_data=f"write_{qid}")
    if not exam:
        builder.button(text="📚 ТЕОРИЯ", callback_data=f"topic_{OGE_QUESTIONS[qid-1]['topic']}")
        builder.button(text="🎲 СЛУЧАЙНОЕ", callback_data="random")
    else:
        builder.button(text="➡️ СЛЕДУЮЩЕЕ", callback_data="next")
    builder.adjust(1, 2)
    return builder.as_markup()

def get_options_keyboard(options, qid):
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(options):
        builder.button(text=f"{i+1}. {opt}", callback_data=f"answer_{qid}_{i}")
    builder.button(text="🔙 НАЗАД", callback_data=f"task_{qid}")
    builder.adjust(1)
    return builder.as_markup()

def get_achievements_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎖️ МОИ ДОСТИЖЕНИЯ", callback_data="my_ach")
    builder.button(text="📈 ПРОГРЕСС", callback_data="progress")
    builder.button(text="🔙 НАЗАД", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()

# ========== ОБРАБОТЧИКИ ==========
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user = get_user_state(message.from_user.id)
    user.update_daily_streak()
    prog = user.get_progress_summary()
    
    await message.answer(
        f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
        f"📚 <b>БОТ ДЛЯ ПОДГОТОВКИ К ОГЭ</b>\n\n"
        f"✅ Все 24 задания в правильном порядке\n"
        f"✅ Полные тексты для заданий 21-24\n"
        f"✅ Проверка ответов\n"
        f"✅ 6 тем теории\n"
        f"✅ Достижения и статистика\n\n"
        f"🏆 <b>Ваш прогресс:</b>\n"
        f"• Решено: {prog['total_questions']} ✅\n"
        f"• Точность: {prog['accuracy']}% 🎯\n"
        f"• Дней: {prog['days_streak']} 📅\n"
        f"• Достижений: {prog['achievements_unlocked']}/{prog['total_achievements']} 🏅",
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
    await m.answer("📝 <b>НАЧИНАЕМ ВАРИАНТ ОГЭ!</b>\n\n24 задания.\n\n<b>Задание 1/24:</b>")
    await send_question(m.from_user.id, user.current_exam[0], exam=True)

@dp.message(lambda m: m.text == "🏆 ДОСТИЖЕНИЯ")
async def achievements_menu(m: Message):
    await m.answer("🏆 <b>ДОСТИЖЕНИЯ</b>", reply_markup=get_achievements_keyboard())

@dp.message(lambda m: m.text == "📊 СТАТИСТИКА")
async def stats_menu(m: Message):
    user = get_user_state(m.from_user.id)
    prog = user.get_progress_summary()
    weak = user.get_weak_topics(2)
    
    text = f"📊 <b>СТАТИСТИКА</b>\n\n"
    text += f"✅ Заданий: {prog['total_questions']}\n"
    text += f"🎯 Правильных: {prog['correct_answers']} ({prog['accuracy']}%)\n"
    text += f"⭐ Баллов: {prog['total_score']}\n"
    text += f"📚 Освоено тем: {prog['topics_mastered']}/{prog['total_topics']}\n\n"
    text += f"🔥 Серия: {prog['perfect_answers_streak']}\n"
    text += f"📅 Дней подряд: {prog['days_streak']}\n"
    
    if weak:
        text += f"\n🔄 <b>Повторить:</b>\n"
        for t in weak:
            text += f"• {t['topic']} - {t['accuracy']:.0f}%\n"
    
    await m.answer(text)

@dp.message(lambda m: m.text == "🔄 ПОВТОРИТЬ")
async def repeat_menu(m: Message):
    user = get_user_state(m.from_user.id)
    weak = user.get_weak_topics(3)
    
    if weak:
        text = "📚 <b>РЕКОМЕНДУЕМ ПОВТОРИТЬ:</b>\n\n"
        kb = InlineKeyboardBuilder()
        for t in weak:
            text += f"• {t['topic']} - {t['accuracy']:.0f}%\n"
            kb.button(text=f"📘 {t['topic']}", callback_data=f"topic_{t['topic']}")
        kb.button(text="🔙 НАЗАД", callback_data="menu")
        kb.adjust(1)
        await m.answer(text, reply_markup=kb.as_markup())
    else:
        await m.answer("✅ <b>Все темы освоены!</b>")

# ========== CALLBACKS ==========
@dp.callback_query(lambda c: c.data == "menu")
async def cb_menu(c: CallbackQuery):
    await c.message.delete()
    await c.message.answer("Главное меню:", reply_markup=get_main_keyboard())
    await c.answer()

@dp.callback_query(lambda c: c.data == "theory")
async def cb_theory(c: CallbackQuery):
    await c.message.edit_text("📚 <b>ВЫБЕРИТЕ ТЕМУ:</b>", reply_markup=get_theory_keyboard())
    await c.answer()

@dp.callback_query(lambda c: c.data.startswith("topic_"))
async def cb_topic(c: CallbackQuery):
    topic = c.data.replace("topic_", "")
    if topic in THEORY_DETAILED:
        await c.message.edit_text(f"📚 <b>{topic}</b>\n\nВыберите подтему:", 
                                reply_markup=get_subtopics_keyboard(topic))
    await c.answer()

@dp.callback_query(lambda c: c.data.startswith("subtopic_"))
async def cb_subtopic(c: CallbackQuery):
    _, topic, subtopic = c.data.split("_", 2)
    if topic in THEORY_DETAILED and subtopic in THEORY_DETAILED[topic]:
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
        kb.button(text="◀️ НАЗАД", callback_data=f"topic_{topic}")
        await c.message.edit_text(text, reply_markup=kb.as_markup())
    await c.answer()

@dp.callback_query(lambda c: c.data.startswith("task_"))
async def cb_task(c: CallbackQuery):
    try:
        num = int(c.data.replace("task_", ""))
        q = OGE_QUESTIONS[num-1].copy()
        user = get_user_state(c.from_user.id)
        user.current_question = q
        await send_question(c.from_user.id, q, c.message)
    except:
        await c.answer("❌ Ошибка", True)
    await c.answer()

@dp.callback_query(lambda c: c.data == "random")
async def cb_random(c: CallbackQuery):
    q = random.choice(OGE_QUESTIONS).copy()
    user = get_user_state(c.from_user.id)
    user.current_question = q
    await send_question(c.from_user.id, q, c.message)
    await c.answer()

@dp.callback_query(lambda c: c.data.startswith("options_"))
async def cb_options(c: CallbackQuery):
    qid = int(c.data.replace("options_", ""))
    for q in OGE_QUESTIONS:
        if q["id"] == qid and "options" in q:
            await c.message.edit_reply_markup(reply_markup=get_options_keyboard(q["options"], qid))
            await c.answer()
            return

@dp.callback_query(lambda c: c.data.startswith("answer_"))
async def cb_answer(c: CallbackQuery):
    data = c.data.replace("answer_", "").split("_")
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
            
            if user.current_exam:
                user.exam_score += points
            user.add_result(correct, points, q["topic"])
            
            text = f"{'✅ ПРАВИЛЬНО!' if correct else '❌ НЕПРАВИЛЬНО'}\n\n"
            text += f"<b>Ваш ответ:</b> {ans+1}\n"
            text += f"<b>Правильный ответ:</b> {q['correct']+1}\n\n"
            text += f"<b>Объяснение:</b> {q['explanation']}\n\n"
            text += f"📊 Правильных: {user.correct_answers}\n"
            text += f"⭐ Баллы: {user.score}\n"
            text += f"🔥 Серия: {user.perfect_answers_streak}"
            
            await c.message.edit_text(text, reply_markup=get_question_keyboard(qid, q["type"], bool(user.current_exam)))
            await c.answer()
            return

@dp.callback_query(lambda c: c.data.startswith("write_"))
async def cb_write(c: CallbackQuery):
    qid = int(c.data.replace("write_", ""))
    user = get_user_state(c.from_user.id)
    user.waiting_for_answer = True
    
    for q in OGE_QUESTIONS:
        if q["id"] == qid:
            user.current_question = q
            await c.message.answer("📝 <b>Напишите ответ в чат:</b>")
            await c.answer()
            return

@dp.callback_query(lambda c: c.data == "next")
async def cb_next(c: CallbackQuery):
    user = get_user_state(c.from_user.id)
    if user.current_exam:
        if user.current_exam_index < len(user.current_exam) - 1:
            user.current_exam_index += 1
            await send_question(c.from_user.id, user.current_exam[user.current_exam_index], c.message, exam=True)
        else:
            total = sum(q["points"] for q in user.current_exam)
            acc = (user.exam_score / total * 100) if total > 0 else 0
            
            grade = "5" if user.exam_score >= 35 else "4" if user.exam_score >= 25 else "3" if user.exam_score >= 15 else "2"
            
            text = f"🏆 <b>ВАРИАНТ ЗАВЕРШЕН!</b>\n\n"
            text += f"✅ Баллов: {user.exam_score}/{total}\n"
            text += f"🎯 Точность: {acc:.1f}%\n"
            text += f"📈 Оценка: {grade}\n\n"
            
            if user.exam_score >= 25:
                user.achievements["oge_master"]["unlocked"] = True
                text += "🏅 РАЗБЛОКИРОВАНО: Мастер ОГЭ!\n"
            
            user.exam_results.append(user.exam_score)
            user.current_exam = None
            
            kb = InlineKeyboardBuilder()
            kb.button(text="📊 СТАТИСТИКА", callback_data="stats")
            kb.button(text="🏠 МЕНЮ", callback_data="menu")
            kb.adjust(1)
            
            await c.message.answer(text, reply_markup=kb.as_markup())
    await c.answer()

@dp.callback_query(lambda c: c.data == "my_ach")
async def cb_my_ach(c: CallbackQuery):
    user = get_user_state(c.from_user.id)
    text = "🏆 <b>ВАШИ ДОСТИЖЕНИЯ:</b>\n\n"
    unlocked = 0
    
    for ach in user.achievements.values():
        if ach["unlocked"]:
            text += f"{ach['icon']} <b>{ach['name']}</b> - ✅\n"
            text += f"<i>{ach['description']}</i>\n\n"
            unlocked += 1
        else:
            if "progress" in ach:
                text += f"🔒 {ach['name']} - {ach['progress']}/{ach['target']}\n"
            else:
                text += f"🔒 {ach['name']}\n"
            text += f"<i>{ach['description']}</i>\n\n"
    
    text += f"<b>Итого:</b> {unlocked}/{len(user.achievements)}"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 НАЗАД", callback_data="back_ach")
    await c.message.edit_text(text, reply_markup=kb.as_markup())
    await c.answer()

@dp.callback_query(lambda c: c.data == "progress")
async def cb_progress(c: CallbackQuery):
    user = get_user_state(c.from_user.id)
    prog = user.get_progress_summary()
    
    text = f"📊 <b>ПРОГРЕСС</b>\n\n"
    text += f"🎯 Точность: {prog['accuracy']}%\n"
    text += f"⭐ Баллы: {prog['total_score']}\n"
    text += f"✅ Решено: {prog['total_questions']}\n"
    text += f"🔥 Серия: {prog['perfect_answers_streak']}\n"
    text += f"📅 Дней: {prog['days_streak']}\n"
    text += f"📚 Освоено тем: {prog['topics_mastered']}/{prog['total_topics']}\n"
    text += f"🏆 Достижений: {prog['achievements_unlocked']}/{prog['total_achievements']}"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 НАЗАД", callback_data="back_ach")
    await c.message.edit_text(text, reply_markup=kb.as_markup())
    await c.answer()

@dp.callback_query(lambda c: c.data == "back_ach")
async def cb_back_ach(c: CallbackQuery):
    await c.message.edit_text("🏆 <b>ДОСТИЖЕНИЯ</b>", reply_markup=get_achievements_keyboard())
    await c.answer()

@dp.callback_query(lambda c: c.data == "stats")
async def cb_stats(c: CallbackQuery):
    await stats_menu(c.message)
    await c.answer()

# ========== ОТПРАВКА ВОПРОСА ==========
async def send_question(user_id, question, msg=None, exam=False):
    user = get_user_state(user_id)
    user.current_question = question
    user.waiting_for_answer = False
    
    if exam:
        num = user.current_exam_index + 1
        header = f"<b>📝 ВАРИАНТ | Задание {num}/24</b>\n\n"
    else:
        header = f"<b>🎯 ЗАДАНИЕ №{question['id']}</b>\n\n"
    
    text = header
    text += f"📚 Тема: {question['topic']}\n"
    text += f"⭐ Баллы: {question['points']}\n\n"
    text += question['text']
    
    kb = get_question_keyboard(question['id'], question['type'], exam)
    
    if msg:
        await msg.edit_text(text, reply_markup=kb)
    else:
        await bot.send_message(user_id, text, reply_markup=kb)

# ========== ПРОВЕРКА ТЕКСТОВЫХ ОТВЕТОВ ==========
def check_answer(q, ans):
    ans = ans.lower()
    
    if q["type"] == "choice":
        return False
    
    if q["type"] == "text":
        if q["id"] == 1:  # Политические понятия
            return "федерация" in ans and "государство" in ans
        elif q["id"] == 5:  # Семья
            return "расширен" in ans and ("эмоц" in ans or "социализ" in ans)
        elif q["id"] == 6:  # Финансы
            return "мошен" in ans and ("не сообщ" in ans or "банк" in ans)
        elif q["id"] == 12:  # Диаграмма
            return "трудов" in ans and "граждан" in ans
        elif q["id"] == 15:  # Соответствие
            return "1" in ans and "2" in ans and len(ans) >= 5
        elif q["id"] == 19:  # Сравнение
            return "1" in ans and "4" in ans and "2" in ans and "3" in ans
        elif q["id"] == 20:  # Таблица
            return "морал" in ans
        elif q["id"] == 21:  # План
            return len(ans.split("\n")) >= 3
        elif q["id"] == 22:  # Глобальные проблемы
            return len(ans.split()) >= 20
        elif q["id"] == 23:  # Примеры
            return len(ans.split()) >= 25
        elif q["id"] == 24:  # Аргументы
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
            correct = check_answer(q, ans)
            points = q["points"] if correct else 0
            
            if user.current_exam:
                user.exam_score += points
            
            user.add_result(correct, points, q["topic"])
            user.waiting_for_answer = False
            
            text = f"{'✅ ПРАВИЛЬНО!' if correct else '❌ НЕПРАВИЛЬНО'}\n\n"
            text += f"<b>Ваш ответ:</b> {ans[:200]}\n\n"
            text += f"<b>Объяснение:</b> {q['explanation']}\n\n"
            text += f"📊 Правильных: {user.correct_answers}\n"
            text += f"⭐ Баллы: {user.score}\n"
            text += f"🔥 Серия: {user.perfect_answers_streak}"
            
            await m.answer(text)
            
            if user.current_exam:
                if user.current_exam_index < len(user.current_exam) - 1:
                    kb = InlineKeyboardBuilder()
                    kb.button(text="➡️ СЛЕДУЮЩЕЕ", callback_data="next")
                    await m.answer("Продолжить?", reply_markup=kb.as_markup())
                else:
                    total = sum(q["points"] for q in user.current_exam)
                    acc = (user.exam_score / total * 100) if total > 0 else 0
                    
                    grade = "5" if user.exam_score >= 35 else "4" if user.exam_score >= 25 else "3" if user.exam_score >= 15 else "2"
                    
                    res = f"🏆 <b>ВАРИАНТ ЗАВЕРШЕН!</b>\n\n"
                    res += f"✅ Баллов: {user.exam_score}/{total}\n"
                    res += f"🎯 Точность: {acc:.1f}%\n"
                    res += f"📈 Оценка: {grade}\n\n"
                    
                    if user.exam_score >= 25:
                        user.achievements["oge_master"]["unlocked"] = True
                        res += "🏅 РАЗБЛОКИРОВАНО: Мастер ОГЭ!\n"
                    
                    user.exam_results.append(user.exam_score)
                    user.current_exam = None
                    
                    kb = InlineKeyboardBuilder()
                    kb.button(text="📊 СТАТИСТИКА", callback_data="stats")
                    kb.button(text="🏠 МЕНЮ", callback_data="menu")
                    kb.adjust(1)
                    
                    await m.answer(res, reply_markup=kb.as_markup())
        return
    
    if m.text.strip().isdigit():
        num = int(m.text.strip())
        if user.current_question and "options" in user.current_question:
            if 1 <= num <= len(user.current_question["options"]):
                q = user.current_question
                correct = (num - 1) == q["correct"]
                points = q["points"] if correct else 0
                
                if user.current_exam:
                    user.exam_score += points
                
                user.add_result(correct, points, q["topic"])
                
                text = f"{'✅ ПРАВИЛЬНО!' if correct else '❌ НЕПРАВИЛЬНО'}\n\n"
                text += f"<b>Ваш ответ:</b> {num}\n"
                text += f"<b>Правильный ответ:</b> {q['correct'] + 1}\n\n"
                text += f"<b>Объяснение:</b> {q['explanation']}\n\n"
                text += f"📊 Правильных: {user.correct_answers}\n"
                text += f"⭐ Баллы: {user.score}"
                
                user.waiting_for_answer = False
                await m.answer(text)
                
                if user.current_exam:
                    if user.current_exam_index < len(user.current_exam) - 1:
                        kb = InlineKeyboardBuilder()
                        kb.button(text="➡️ СЛЕДУЮЩЕЕ", callback_data="next")
                        await m.answer("Продолжить?", reply_markup=kb.as_markup())
                    else:
                        total = sum(q["points"] for q in user.current_exam)
                        acc = (user.exam_score / total * 100) if total > 0 else 0
                        
                        grade = "5" if user.exam_score >= 35 else "4" if user.exam_score >= 25 else "3" if user.exam_score >= 15 else "2"
                        
                        res = f"🏆 <b>ВАРИАНТ ЗАВЕРШЕН!</b>\n\n"
                        res += f"✅ Баллов: {user.exam_score}/{total}\n"
                        res += f"🎯 Точность: {acc:.1f}%\n"
                        res += f"📈 Оценка: {grade}\n\n"
                        
                        if user.exam_score >= 25:
                            user.achievements["oge_master"]["unlocked"] = True
                            res += "🏅 РАЗБЛОКИРОВАНО: Мастер ОГЭ!\n"
                        
                        user.exam_results.append(user.exam_score)
                        user.current_exam = None
                        
                        kb = InlineKeyboardBuilder()
                        kb.button(text="📊 СТАТИСТИКА", callback_data="stats")
                        kb.button(text="🏠 МЕНЮ", callback_data="menu")
                        kb.adjust(1)
                        
                        await m.answer(res, reply_markup=kb.as_markup())

# ========== ЗАПУСК ==========
async def main():
    print("=" * 50)
    print("🤖 ЗАПУСК БОТА ДЛЯ ОГЭ")
    print("=" * 50)
    print(f"✅ Токен: Установлен")
    print(f"📚 Теория: 6 тем")
    print(f"🎯 Задания: 24 задания")
    print(f"📝 Тексты: 21-24 с полными текстами")
    print(f"✅ Проверка ответов: ВКЛЮЧЕНА")
    print("=" * 50)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())



