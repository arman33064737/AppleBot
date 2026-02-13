import logging
import asyncio
import os
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)
from telegram.error import BadRequest

# -------------------- Keep-Alive with Self-Ping (Render) --------------------
# This keeps your bot alive even after you close the browser tab.
# It pings your Render URL every 5 minutes so Render never puts the service to sleep.
import aiohttp

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# Get your public Render URL from environment (set it manually if not on Render)
PUBLIC_URL = os.environ.get("RENDER_EXTERNAL_URL", None)
if not PUBLIC_URL:
    # ⚠️ Replace with your actual Render URL or leave empty – the ping will be skipped
    PUBLIC_URL = "https://signaapplel_bot.render.com"  # change this!

async def self_ping():
    """Ping the public URL every 5 minutes to prevent Render from sleeping."""
    if not PUBLIC_URL or PUBLIC_URL == "https://your-app-name.onrender.com":
        logging.warning("Self-ping disabled: PUBLIC_URL not set correctly.")
        return
    while True:
        await asyncio.sleep(300)  # 5 minutes
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(PUBLIC_URL, timeout=10) as resp:
                    logging.info(f"Self-ping to {PUBLIC_URL} → {resp.status}")
        except Exception as e:
            logging.error(f"Self-ping failed: {e}")

# -------------------- Configuration --------------------
BOT_TOKEN = "8511299158:AAHJL-7NTPcc0Dt4rGt3ixHcpOwUGAQ1lQA"
ADMIN_ID = 7406442919  
REQUIRED_CHANNEL_ID = "-1001481593780"

LINK_REGISTRATION = "https://bit.ly/BLACK220" 
PROMO_CODE = "BLACK220" 

CHANNEL_INVITE_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"
ADMIN_USER_LINK = "https://t.me/SUNNY_BRO1"

# Images
IMG_START = "https://i.ibb.co.com/23VVWgSS/file-00000000d21472088a8b84f9b1faa902.png"
IMG_LANG = "https://i.ibb.co.com/23VVWgSS/file-00000000d21472088a8b84f9b1faa902.png"
IMG_CHOOSE_PLATFORM = "https://i.ibb.co.com/NdFDsT4P/file-000000005308720880754a5daa131c74.png"
IMG_REGISTRATION = "https://i.ibb.co.com/NdFDsT4P/file-000000005308720880754a5daa131c74.png"
FINAL_IMAGE_URL = "https://i.ibb.co.com/vxfM0vv5/file-00000000f15071fa8c883abb1421fa69.png"

WEBAPP_URL = "https://1xbet-melbet-apple.unaux.com/"
USER_FILE = "users.txt"

# -------------------- Texts --------------------
TEXTS = {
    'en': { ... },   # unchanged, omitted for brevity
    'bn': { ... }    # unchanged
}

# -------------------- States --------------------
CHECK_JOIN, SELECT_LANGUAGE, CHOOSE_PLATFORM, WAITING_FOR_ID = range(4)
ADMIN_MENU, ADMIN_GET_CONTENT, ADMIN_GET_LINK, ADMIN_GET_BTN_NAME, ADMIN_CONFIRM = range(10, 15)

# -------------------- Database helpers --------------------
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def save_user(user_id):
    if not os.path.exists(USER_FILE): open(USER_FILE, "w").close()
    with open(USER_FILE, "r") as f: users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f: f.write(f"{str(user_id)}\n")

def get_users():
    if not os.path.exists(USER_FILE): return []
    with open(USER_FILE, "r") as f: return f.read().splitlines()

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL_ID, user_id=user_id)
        return member.status in ['creator', 'administrator', 'member']
    except BadRequest: return False
    except Exception: return False

# -------------------- User Handlers --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    
    if not await check_membership(update, context):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_INVITE_LINK)],
            [InlineKeyboardButton("✅ I Have Joined", callback_data='check_join_status')]
        ]
        welcome_text = f"👋 <b>Hello {user.first_name}!</b>\nJoin our channel to use this bot."
        try:
            await update.message.reply_photo(photo=IMG_START, caption=welcome_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return CHECK_JOIN
    
    await show_language_menu(update, context)
    return SELECT_LANGUAGE

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await check_membership(update, context):
        await show_language_menu(update, context)
        return SELECT_LANGUAGE
    else:
        await query.message.reply_text("❌ You haven't joined yet. Please join and try again.")
        return CHECK_JOIN

async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'),
         InlineKeyboardButton("🇧🇩 বাংলা", callback_data='lang_bn')]
    ]
    text = "🌐 <b>Select Language / ভাষা নির্বাচন করুন:</b>"
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.delete()
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMG_LANG, caption=text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.effective_chat.send_photo(photo=IMG_LANG, caption=text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['lang'] = query.data.split('_')[1]
    await show_platform_menu(update, context)
    return CHOOSE_PLATFORM

async def show_platform_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # important!
    lang = context.user_data.get('lang', 'en')
    t = TEXTS[lang]
    keyboard = [
        [InlineKeyboardButton("🔵 1XBET", callback_data='platform_1xbet'),
         InlineKeyboardButton("🟡 MELBET", callback_data='platform_melbet')],
        [InlineKeyboardButton(t['btn_help'], url=ADMIN_USER_LINK)]
    ]
    await query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMG_CHOOSE_PLATFORM,
                                 caption=t['choose_platform_caption'], parse_mode='HTML',
                                 reply_markup=InlineKeyboardMarkup(keyboard))

async def platform_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    lang = context.user_data.get('lang', 'en')
    t = TEXTS[lang]
    p_name = "1XBET" if choice == 'platform_1xbet' else "MELBET"
    
    text = f"{t['reg_title'].format(platform=p_name)}\n\n{t['reg_msg'].format(promo=PROMO_CODE)}"
    
    keyboard = [
        [InlineKeyboardButton(t['btn_reg_link'].format(platform=p_name), url=LINK_REGISTRATION)],
        [InlineKeyboardButton(t['btn_next'], callback_data='account_created')],
        [InlineKeyboardButton(t['btn_contact'], url=ADMIN_USER_LINK)]
    ]
    
    await query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMG_REGISTRATION,
                                 caption=text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_PLATFORM

async def wait_and_ask_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # <-- FIX: answer immediately
    lang = context.user_data.get('lang', 'en')
    msg = await query.message.reply_text(TEXTS[lang]['wait_msg'], parse_mode='HTML')
    await asyncio.sleep(4)
    try:
        await msg.delete()
    except:
        pass
    await query.message.reply_text(TEXTS[lang]['ask_id'], parse_mode='HTML')
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    lang = context.user_data.get('lang', 'en')
    t = TEXTS[lang]
    
    if not uid.isdigit():
        await update.message.reply_text(t['error_digit'], parse_mode='HTML')
        return WAITING_FOR_ID
    
    if len(uid) < 9 or len(uid) > 10:
        await update.message.reply_text(t['error_length'], parse_mode='HTML')
        return WAITING_FOR_ID
    
    keyboard = [
        [InlineKeyboardButton(t['btn_open_hack'], web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(t['btn_contact'], url=ADMIN_USER_LINK)]
    ]
    
    try:
        await update.message.reply_photo(
            photo=FINAL_IMAGE_URL,
            caption=t['success_caption'].format(uid=uid, promo=PROMO_CODE),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except BadRequest:
        # fallback if photo fails
        keyboard = [[InlineKeyboardButton(t['btn_open_hack'].replace("(WebApp)", "(Link)"), url=WEBAPP_URL)]]
        await update.message.reply_text(
            f"✅ Verified ID: {uid}\n⬇️ Open Hack:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    return ConversationHandler.END

# -------------------- Admin Panel --------------------
# ... (unchanged, but ensure query.answer() is added where missing)
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    keyboard = [
        [InlineKeyboardButton("📸 Photo + Text", callback_data='mode_photo_text')],
        [InlineKeyboardButton("🎥 Video + Text + Btn", callback_data='mode_video_text_btn')],
        [InlineKeyboardButton("🎥 Video + Btn", callback_data='mode_video_btn')],
        [InlineKeyboardButton("📝 Text + Btn", callback_data='mode_text_btn')],
        [InlineKeyboardButton("❌ Cancel", callback_data='admin_cancel')]
    ]
    await update.message.reply_text("👑 <b>ADMIN PANEL</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_MENU

async def admin_mode_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data
    context.user_data['bc_mode'] = mode
    if mode == 'admin_cancel':
        await query.message.delete()
        return ConversationHandler.END
    await query.message.edit_text("Send your Content now:", parse_mode='HTML')
    return ADMIN_GET_CONTENT

async def admin_get_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data['bc_mode']
    if update.message.photo:
        context.user_data['file_id'] = update.message.photo[-1].file_id
        context.user_data['caption'] = update.message.caption
    elif update.message.video:
        context.user_data['file_id'] = update.message.video.file_id
        context.user_data['caption'] = update.message.caption
    elif update.message.text:
        context.user_data['text'] = update.message.text
    else:
        await update.message.reply_text("❌ Invalid Format!")
        return ADMIN_GET_CONTENT

    if 'btn' in mode:
        await update.message.reply_text("🔗 Enter Button URL:", parse_mode='HTML')
        return ADMIN_GET_LINK
    return await admin_broadcast_confirm(update, context)

async def admin_get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['btn_url'] = update.message.text.strip()
    await update.message.reply_text("🔤 Enter Button Name:", parse_mode='HTML')
    return ADMIN_GET_BTN_NAME

async def admin_get_btn_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['btn_name'] = update.message.text.strip()
    return await admin_broadcast_confirm(update, context)

async def admin_broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 SEND", callback_data='confirm_send'),
         InlineKeyboardButton("❌ CANCEL", callback_data='confirm_cancel')]
    ]
    await update.message.reply_text("✅ Confirm Send?", reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_CONFIRM

async def admin_perform_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # <-- FIX: missing answer
    if query.data == 'confirm_cancel':
        await query.message.edit_text("❌ Cancelled.")
        return ConversationHandler.END
    
    users = get_users()
    await query.message.edit_text(f"🚀 Sending to {len(users)} users...")
    mode = context.user_data['bc_mode']
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(context.user_data['btn_name'], url=context.user_data['btn_url'])]]) if 'btn' in mode else None
    
    count = 0
    for uid in users:
        try:
            if 'photo' in mode:
                await context.bot.send_photo(uid, photo=context.user_data['file_id'], caption=context.user_data['caption'])
            elif 'video' in mode:
                await context.bot.send_video(uid, video=context.user_data['file_id'], caption=context.user_data.get('caption'), reply_markup=markup)
            elif 'text' in mode:
                await context.bot.send_message(uid, text=context.user_data['text'], reply_markup=markup)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
            
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Sent to {count} users.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔ Cancelled.")
    return ConversationHandler.END

# -------------------- Main --------------------
if __name__ == '__main__':
    # Start the dummy Flask server in a separate thread
    keep_alive()

    # Build bot application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation: User flow
    user_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHECK_JOIN: [CallbackQueryHandler(check_join_callback, pattern='^check_join_status$')],
            SELECT_LANGUAGE: [CallbackQueryHandler(set_language, pattern='^lang_')],
            CHOOSE_PLATFORM: [
                CallbackQueryHandler(platform_choice, pattern='^platform_'),
                CallbackQueryHandler(wait_and_ask_id, pattern='^account_created$')
            ],
            WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Conversation: Admin broadcast
    admin_conv = ConversationHandler(
        entry_points=[CommandHandler('admin', admin_start)],
        states={
            ADMIN_MENU: [CallbackQueryHandler(admin_mode_select, pattern='^mode_|admin_cancel')],
            ADMIN_GET_CONTENT: [MessageHandler(filters.PHOTO | filters.VIDEO | filters.TEXT, admin_get_content)],
            ADMIN_GET_LINK: [MessageHandler(filters.TEXT, admin_get_link)],
            ADMIN_GET_BTN_NAME: [MessageHandler(filters.TEXT, admin_get_btn_name)],
            ADMIN_CONFIRM: [CallbackQueryHandler(admin_perform_broadcast, pattern='^confirm_')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(admin_conv)
    application.add_handler(user_conv)

    # Start the self-ping background task (keeps Render awake)
    loop = asyncio.get_event_loop()
    loop.create_task(self_ping())

    print("✅ Bot started with self‑ping enabled. It will stay alive 24/7!")
    application.run_polling()
