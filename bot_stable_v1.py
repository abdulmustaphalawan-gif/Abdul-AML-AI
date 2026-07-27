from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from gemini import ask_gemini
from memory import (
    load_memory,
    save_memory,
    get_user,
    add_history,
    remember_fact,
    clear_user,
)
from commands import (
    start,
    help_command,
    about_command,
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.effective_user.id

    memory = load_memory()
    user = get_user(memory, user_id)

    # Remember name
    if user_message.lower().startswith("my name is "):
        name = user_message[11:].strip()

        user["name"] = name
        save_memory(memory)

        await update.message.reply_text(
            f"Nice to meet you, {name}! I will remember your name."
        )
        return

    # Remember facts
    if user_message.lower().startswith("remember that "):
        fact = user_message[14:].strip()

        facts = user.get("facts", {})

        fact_key = f"fact_{len(facts) + 1}"

        remember_fact(
            memory,
            user_id,
            fact_key,
            fact
        )

        await update.message.reply_text(
            "✅ I will remember that."
        )
        return

    if user_message.lower() in [
        "what is my name?",
        "what's my name?",
        "who am i?"
    ]:
        if user["name"]:
            await update.message.reply_text(
                f"Your name is {user['name']}."
            )
        else:
            await update.message.reply_text(
                "I don't know your name yet."
            )
        return

    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        history = user["history"]

        reply = ask_gemini(
            user_message,
            history,
            user
        )

        add_history(
            memory,
            user_id,
            f"User: {user_message}"
        )

        add_history(
            memory,
            user_id,
            f"Abdul AML: {reply}"
        )

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {e}"
        )

async def forget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    memory = load_memory()
    clear_user(memory, user_id)

    await update.message.reply_text(
        "🧹 Your memory has been cleared."
    )


async def show_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    memory = load_memory()
    user = get_user(memory, user_id)

    await update.message.reply_text(
        f"🧠 Memory\n\n"
        f"Name: {user['name']}\n"
        f"Facts: {user['facts']}\n"
        f"Preferences: {user['preferences']}"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("memory", show_memory))
    app.add_handler(CommandHandler("forget", forget))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("🤖 Abdul AML v3 is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
