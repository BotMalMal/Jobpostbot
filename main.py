import json
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/save", "/spend"], ["/summary", "/edit"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("💰 Welcome to your Finance Tracker Bot!", reply_markup=reply_markup)

async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        amount = float(context.args[0])
    except:
        await update.message.reply_text("Please provide a valid amount. Usage: /save 5000")
        return

    data = load_data()
    data["users"].setdefault(user_id, {"save": 0, "spend": 0})
    data["users"][user_id]["save"] += amount
    save_data(data)

    await update.message.reply_text(f"✅ Saved {amount} ks!")

async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        amount = float(context.args[0])
    except:
        await update.message.reply_text("Please provide a valid amount. Usage: /spend 3000")
        return

    data = load_data()
    data["users"].setdefault(user_id, {"save": 0, "spend": 0})
    data["users"][user_id]["spend"] += amount
    save_data(data)

    await update.message.reply_text(f"💸 Spent {amount} ks!")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    user = data["users"].get(user_id)

    if not user:
        await update.message.reply_text("No records found yet.")
        return

    save_amt = user.get("save", 0)
    spend_amt = user.get("spend", 0)
    balance = save_amt - spend_amt

    await update.message.reply_text(
        f"📊 Summary:\nSaved: {save_amt} ks\nSpent: {spend_amt} ks\nBalance: {balance} ks"
    )

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /edit save/spend amount\nExample: /edit save 10000")
        return

    category = context.args[0].lower()
    try:
        amount = float(context.args[1])
    except:
        await update.message.reply_text("Invalid amount.")
        return

    if category not in ["save", "spend"]:
        await update.message.reply_text("Only 'save' or 'spend' can be edited.")
        return

    data = load_data()
    data["users"].setdefault(user_id, {"save": 0, "spend": 0})
    data["users"][user_id][category] = amount
    save_data(data)

    await update.message.reply_text(f"✏️ Edited {category} to {amount} ks.")

if __name__ == "__main__":
    import asyncio
    from telegram.ext import Application

    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("save", save))
    app.add_handler(CommandHandler("spend", spend))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("edit", edit))

    print("🤖 Bot is running...")
    app.run_polling()
