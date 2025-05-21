import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import nest_asyncio
import random

nest_asyncio.apply()

PDF_FOLDER = 'pdf_files'
EXCEL_FILE = 'student_codes.xlsx'

questions = {
    "What is the capital of France?": "Paris",
    "What is 2 + 2?": "4",
    "Name the largest planet in our solar system.": "Jupiter",
    "What is the boiling point of water in Celsius?": "100",
    "Who wrote 'Romeo and Juliet'?": "Shakespeare",
    "What is the currency of Japan?": "Yen",
    "How many continents are there?": "7",
    "Who painted the Mona Lisa?": "Leonardo da Vinci",
    "What is the chemical symbol for gold?": "Au",
    "Translate to English: 'مرحبا'": "Hello",
    "Translate to Arabic: 'Good morning'": "صباح الخير",
    "What is the synonym of 'happy'?": "Joyful",
    "What is the antonym of 'easy'?": "Hard",
    "What is the plural form of 'child'?": "Children",
    "What is the past tense of 'go'?": "Went",
    "What is the meaning of 'verbose'?": "Using more words than necessary",
    "Which word is a synonym of 'quick'?": "Fast",
    "What is the opposite of 'accept'?": "Reject",
    "What is the past tense of 'run'?": "Ran",
    "Fill in the blank: 'She _____ to the store yesterday.' (go/goes/went)": "Went",
    "What is the capital of Japan?": "Tokyo",
    "Which of these is a verb: 'apple', 'run', 'quick'": "Run",
    "What is the comparative form of 'good'?": "Better",
    "What is the superlative form of 'bad'?": "Worst",
    "Translate to Arabic: 'I am learning English'": "أنا أتعلم الإنجليزية",
    "What is the opposite of 'brave'?": "Cowardly",
    "What is the synonym of 'beautiful'?": "Attractive",
    "Translate to English: 'أين أنت؟'": "Where are you?",
    "What does 'bilingual' mean?": "Able to speak two languages",
    "Which of the following is a noun: 'quickly', 'happiness', 'running'": "Happiness",
    "What is the plural of 'mouse'?": "Mice",
    "Which of the following words is an adjective: 'quickly', 'loud', 'sitting'": "Loud",
    "What is the opposite of 'arrive'?": "Depart",
    "What is the synonym of 'angry'?": "Furious",
    "Translate to Arabic: 'I am going to the park'": "أنا ذاهب إلى الحديقة",
    "What does 'ambiguous' mean?": "Unclear or inexact",
    "What is the opposite of 'early'?": "Late",
    "What is the synonym of 'intelligent'?": "Smart",
    "Translate to English: 'كيف حالك؟'": "How are you?",
    "What is the antonym of 'interesting'?": "Boring",
    "What is the past tense of 'speak'?": "Spoke",
    "What is the plural form of 'tooth'?": "Teeth",
    "What is the meaning of 'exquisite'?": "Extremely beautiful and delicate",
    "Fill in the blank: 'They _____ to the cinema last night.' (go/goes/went)": "Went",
    "What is the comparative form of 'bad'?": "Worse",
    "Translate to Arabic: 'I am studying English grammar'": "أنا أدرس قواعد اللغة الإنجليزية",
    "What is the synonym of 'friendly'?": "Sociable",
    "What is the opposite of 'rich'?": "Poor",
    "What does 'accomplish' mean?": "To achieve or complete successfully",
    "Which of the following is a preposition: 'in', 'run', 'fast'": "In",
    "What is the opposite of 'clean'?": "Dirty",
    "What is the past tense of 'eat'?": "Ate",
    "What is the plural of 'child'?": "Children",
    "What is the superlative form of 'good'?": "Best",
    "What does 'fragile' mean?": "Easily broken or damaged",
    "Translate to Arabic: 'How much is this?'": "كم ثمن هذا؟",
    "Which of these is an adverb: 'quick', 'quickly', 'quickness'": "Quickly"
}

def load_codes():
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            if 'Code' in df.columns and 'Name' in df.columns:
                return dict(zip(df['Code'].astype(str), df['Name']))
            else:
                print("Error: الأعمدة المطلوبة غير موجودة في ملف Excel.")
                return {}
        else:
            print(f"Error: ملف Excel غير موجود: {EXCEL_FILE}")
            return {}
    except Exception as e:
        print(f"Error loading codes from Excel: {e}")
        return {}

def get_student_info(user_code):
    try:
        df = pd.read_excel(EXCEL_FILE)
        student_data = df[df['Code'].astype(str) == user_code]

        if not student_data.empty:
            student_name = student_data['Name'].values[0]
            subjects_grades = ""
            for i in range(1, 14):
                subject = student_data[f'Subject {i}'].values[0]
                grade = student_data[f'Grade {i}'].values[0]
                subjects_grades += f"{subject}: {grade}\n"
            return f"اسم الطالب: {student_name}\n{subjects_grades}"
        else:
            return "لم يتم العثور على الطالب."
    except Exception as e:
        return f"حدث خطأ أثناء استرجاع البيانات: {e}"

async def check_code(update: Update, context: CallbackContext) -> None:
    user_code = update.message.text.strip()
    codes = load_codes()

    if user_code in codes:
        name = codes[user_code]
        student_info = get_student_info(user_code)
        await update.message.reply_text(f"الكود صحيح! اسم الطالب: {name}\n\n{student_info}")
    else:
        await update.message.reply_text("الكود غير صحيح. حاول مرة أخرى.")

async def show_files(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)

    files = os.listdir(PDF_FOLDER)
    if not files:
        await query.message.reply_text("لا توجد ملفات PDF حاليا.")
        return

    keyboard = [[InlineKeyboardButton(file, callback_data=f"file:{file}")] for file in files]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text('اختر الملف الذي تريد تحميله:', reply_markup=reply_markup)

async def send_file(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("file:"):
        file_name = query.data.split("file:")[1]
        file_path = os.path.join(PDF_FOLDER, file_name)

        if os.path.exists(file_path):
            await query.message.reply_document(document=open(file_path, 'rb'))
        else:
            await query.message.reply_text("هذا الملف غير موجود.")

async def send_quiz(update: Update, context: CallbackContext) -> None:
    question, answer = random.choice(list(questions.items()))
    context.user_data['quiz_answer'] = answer
    context.user_data['awaiting_quiz_answer'] = True
    await update.message.reply_text(f"السؤال: {question}")

async def handle_quiz_answer(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_quiz_answer', False):
        user_answer = update.message.text.strip()
        correct_answer = context.user_data.get('quiz_answer', '').lower()

        if user_answer.lower() == correct_answer:
            await update.message.reply_text("إجابة صحيحة! 🌟")
        else:
            await update.message.reply_text(f"إجابة خاطئة. الإجابة الصحيحة هي: {correct_answer}")

        context.user_data['awaiting_quiz_answer'] = False
    else:
        await check_code(update, context)

# ✅ دالة start بدون التحقق من الاشتراك
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("عرض الملفات", callback_data='files')],
        [InlineKeyboardButton("التحقق من الكود", callback_data='check_code')],
        [InlineKeyboardButton("تحدي الأسئلة", callback_data='quiz')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('خادم للطيبين اختار حبيبي', reply_markup=reply_markup)

async def handle_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'check_code':
        await query.message.reply_text("دز الكود الخاص بكً")
    elif query.data == 'files':
        await show_files(update, context)
    elif query.data == 'quiz':
        await send_quiz(query, context)
    elif query.data.startswith("file:"):
        await send_file(update, context)

async def main():
    token = '7488830368:AAEH33gtHYxuIIUOP01zNs5FKPBggWcsR2c'
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_answer))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
