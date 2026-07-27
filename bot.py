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
    user_message = update.message.text.strip()
    text = user_message.lower()
    user_id = update.effective_user.id

    memory = load_memory()
    user = get_user(memory, user_id)

    # ==========================
    # Remember user's name
    # ==========================
    if text.startswith("my name is "):
        name = user_message[11:].strip()

        user["name"] = name
        save_memory(memory)

        await update.message.reply_text(
            f"Nice to meet you, {name}! I will remember your name."
        )
        return

    # ==========================
    # Remember where user lives
    # ==========================
    if text.startswith("i live in "):
        remember_fact(
            memory,
            user_id,
            "location",
            user_message[10:].strip()
        )

    # ==========================
    # Remember origin
    # ==========================
    if text.startswith("i'm from "):
        remember_fact(
            memory,
            user_id,
            "origin",
            user_message[9:].strip()
        )

    elif text.startswith("i am from "):
        remember_fact(
            memory,
            user_id,
            "origin",
            user_message[10:].strip()
        )

    # ==========================
    # Remember education
    # ==========================
    if (
        "i study" in text
        or "studying" in text
        or "i'm studying" in text
        or "i am studying" in text
    ):
        remember_fact(
            memory,
            user_id,
            "education",
            user_message
        )

    # ==========================
    # Remember job
    # ==========================
    if (
        "i work at" in text
        or "i work with" in text
        or "working with" in text
        or "i'm working at" in text
        or "i'm working with" in text
    ):
        remember_fact(
            memory,
            user_id,
            "job",
            user_message
        )

    # ==========================
    # Remember favourite language
    # ==========================
    if (
        "my favorite language is " in text
        or "my favourite language is " in text
        or "i prefer " in text
    ):
        if "my favorite language is " in text:
            value = user_message[24:].strip()
        elif "my favourite language is " in text:
            value = user_message[25:].strip()
        else:
            value = user_message[9:].strip()

        remember_fact(
            memory,
            user_id,
            "preferred_language",
            value
        )

    # ==========================
    # Remember custom facts
    # ==========================
    if text.startswith("remember that "):
        fact = user_message[14:].strip()

        facts = user.get("facts", {})
        fact_key = f"fact_{len(facts)+1}"

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

    # ==========================
    # Recall user's name
    # ==========================
    if text in [
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

    if text in [
        "what do you know about me?",
        "what do you know about me",
        "tell me about me",
    ]:
        facts = user.get("facts", {})

        reply = "🧠 Here's what I know about you:\n\n"

        if user.get("name"):
            reply += f"👤 Name: {user['name']}\n"

        if facts.get("location"):
            reply += f"📍 Lives in: {facts['location']}\n"

        if facts.get("origin"):
            reply += f"🏠 From: {facts['origin']}\n"

        if facts.get("education"):
            reply += f"🎓 Education: {facts['education']}\n"

        if facts.get("job"):
            reply += f"💼 Job: {facts['job']}\n"

        if facts.get("preferred_language"):
            reply += (
                f"🗣️ Preferred language: "
                f"{facts['preferred_language']}\n"
            )

        if reply == "🧠 Here's what I know about you:\n\n":
            reply += "I don't know much about you yet."

        await update.message.reply_text(reply)
        return

    # ==========================
    # Show typing indicator
    # ==========================
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
