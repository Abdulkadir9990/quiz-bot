import re
import asyncio
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from keep_alive import keep_alive
import os
BOT_TOKEN = os.getenv("7837186188:AAH6kanY3TElNPT91wa-SmWhdN2VTqBnhmg")

def parse_multiple_questions(text):
    question_blocks = re.split(r'\n(?=\d+\.\s)', text.strip())
    questions_data = []

    for block in question_blocks:
        if not block.strip():
            continue

        lines = block.strip().split('\n')

        try:
            if len(lines) < 7:
                continue  # تجاهل الأسئلة غير المكتملة

            question_number_match = re.match(r'^(\d+)\.\s*(.*)', lines[0])
            if question_number_match:
                question_number = question_number_match.group(1)
                question_en = question_number_match.group(2).strip()
            else:
                question_number = "?"
                question_en = lines[0].strip()

            question_ar = lines[1].strip()
            question_full = f"{question_number}. {question_en}\n{question_ar}"

            options = []
            correct_option_letter = ""
            correct_option_index = -1

            for line in lines[2:]:
                if line.lower().startswith('answer:'):
                    correct_option_letter = line.split(':')[1].strip().lower()
                elif re.match(r'^[a-dA-D]\)', line.strip()):
                    option_text = line[2:].strip()
                    options.append(option_text)

            option_letters = ['a', 'b', 'c', 'd']
            if correct_option_letter in option_letters:
                correct_option_index = option_letters.index(correct_option_letter)

            if question_full and len(options) == 4 and correct_option_index != -1:
                questions_data.append({
                    'question': question_full,
                    'options': options,
                    'correct_index': correct_option_index
                })

        except Exception:
            continue

    return questions_data

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        questions_data = parse_multiple_questions(text)

        if not questions_data:
            await update.message.reply_text("⚠️ لم يتم العثور على أسئلة بصيغة صحيحة. تأكد من التنسيق.")
            return

        await update.message.reply_text(f"✅ تم العثور على {len(questions_data)} سؤال/أسئلة. سيتم إرسالها الآن...")

        for question_data in questions_data:
            await update.message.chat.send_poll(
                question=question_data['question'],
                options=question_data['options'],
                type=Poll.QUIZ,
                correct_option_id=question_data['correct_index'],
                is_anonymous=False
            )
            await asyncio.sleep(1)

        await update.message.reply_text(f"🎉 تم إرسال جميع الأسئلة ({len(questions_data)}) بنجاح!")

    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء المعالجة: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبًا! أرسل الأسئلة بهذا التنسيق:\n\n"
        "1. What is the capital of France?\n"
        "ما هي عاصمة فرنسا؟\n"
        "a) London\n"
        "b) Berlin\n"
        "c) Paris\n"
        "d) Madrid\n"
        "Answer: c\n\n"
        "📌  ملاحظات:\n"
        "اذا كنت تريد ان تضيف سؤال يجب ان يكون بنفس تنسيق السؤال الي فوق \n"
    )

if __name__ == "__main__":
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    print("✅ Bot is running...")
    app.run_polling()
