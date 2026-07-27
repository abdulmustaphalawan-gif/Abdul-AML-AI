from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I am Abdul AML.\n\nHow can I help you today?"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Start Abdul AML\n"
        "/help - Show commands\n"
        "/about - About Abdul AML\n"
        "/memory - Show saved memory (coming soon)\n"
        "/forget - Clear memory (coming soon)"
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Abdul AML\n\n"
        "A personal AI assistant powered by Gemini."
    )
