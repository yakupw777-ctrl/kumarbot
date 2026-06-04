import logging
import sqlite3
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8617431009:AAES477jErU7Ynarl4RuVXlRdXA4ACSFU1Q"

# !!! KENDİ TELEGRAM ID'Nİ BURAYA YAZ !!!
# Telegram'da @userinfobot 'a mesaj atarak kendi ID'ni (sayılardan oluşur) öğrenebilirsin.
ADMIN_ID = 8217991199  # Buradaki sayıları kendi ID'nle değiştir

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- VERİBATANI İŞLEMLERİ ---
def init_db():
    conn = sqlite3.connect("game_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 1000,
            level INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def get_player(user_id, username):
    conn = sqlite3.connect("game_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance, level FROM players WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row is None:
        cursor.execute("INSERT INTO players (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        row = (1000, 1)
        
    conn.close()
    return row

def update_balance(user_id, amount):
    conn = sqlite3.connect("game_database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect("game_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, balance FROM players ORDER BY balance DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- BUTONLAR VE KLAVYELER ---
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Profilim", callback_data="menu_profile")
    builder.button(text="🎲 Zar At (Kumar)", callback_data="menu_gamble")
    builder.button(text="🏆 Liderlik Tablosu", callback_data="menu_leaderboard")
    builder.adjust(2)
    return builder.as_markup()

# --- KOMUTLAR ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Oyuncu"
    get_player(user_id, username)
    
    await message.answer(
        f"🎮 **Oyun Botuna Hoş Geldin!**\n\nBakiyeni katlamak ve sıralamada yükselmek için aşağıdaki butonları kullan.",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

# --- BUTON ETKİLEŞİMLERİ (CALLBACK) ---
@dp.callback_query(lambda c: c.data == "menu_profile")
async def show_profile(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.first_name or "Oyuncu"
    balance, level = get_player(user_id, username)
    
    text = f"👤 **PROFİLİN**\n\n🏅 Seviye: {level}\n💰 Bakiye: {balance} Altın"
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Geri Dön", callback_data="menu_main")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "menu_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        f"🎮 **Ana Menü**\n\nNe yapmak istersin?",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "menu_gamble")
async def gamble_game(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    win = random.choice([True, False])
    if win:
        update_balance(user_id, 200)
        text = "🎉 Kazandın! Hesabına 200 Altın eklendi."
    else:
        update_balance(user_id, -200)
        text = "📉 Kaybettin! Hesabından 200 Altın düştü."
        
    builder = InlineKeyboardBuilder()
    builder.button(text="🎲 Tekrar Dene", callback_data="menu_gamble")
    builder.button(text="⬅️ Ana Menü", callback_data="menu_main")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "menu_leaderboard")
async def show_leaderboard(callback: types.CallbackQuery):
    leaders = get_leaderboard()
    text = "🏆 **EN ZENGİN OYUNCULAR (TOP 10)**\n\n"
    
    if not leaders:
        text += "Henüz kayıtlı oyuncu bulunmuyor."
    else:
        for index, (username, balance) in enumerate(leaders, start=1):
            if index == 1: medal = "🥇"
            elif index == 2: medal = "🥈"
            elif index == 3: medal = "🥉"
            else: medal = f"{index}."
            text += f"{medal} {username} — {balance} Altın\n"
            
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Ana Menü", callback_data="menu_main")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# --- ADMİN PANELİ FONKSİYONLARI VE KOMUTLARI ---

def get_total_players():
    conn = sqlite3.connect("game_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM players")
    count = cursor.fetchone()[0]
    conn.close()
    return count

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Bu komutu kullanmaya yetkiniz yok!")
        return

    total_players = get_total_players()
    text = f"⚙️ **ADMİN YÖNETİM PANELİ**\n\n" \
           f"📊 Toplam Kayıtlı Oyuncu: {total_players}\n\n" \
           f"🔧 **Kullanabileceğiniz Komutlar:**\n" \
           f"• /bakiye_ver [Kullanıcı_ID] [Miktar] -> Oyuncuya altın ekler.\n" \
           f"• Örnek: `/bakiye_ver 8217991199 5000`"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("bakiyever"))
async def admin_give_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Yetkiniz yok!")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer("⚠ Hatalı kullanım!\nDoğru Kullanım: `/bakiye_ver [Kullanıcı_ID] [Miktar]`", parse_mode="Markdown")
        return

    try:
        target_user_id = int(args[1])
        amount = int(args[2])
        update_balance(target_user_id, amount)
        await message.answer(f"✅ {target_user_id} ID'li oyuncunun hesabına {amount} altın başarıyla eklendi!")
        try:
            await bot.send_message(target_user_id, f"🎁 **Admin tarafından hesabınıza {amount} Altın eklendi!**", parse_mode="Markdown")
        except Exception:
            pass
    except ValueError:
        await message.answer("⚠ Lütfen ID ve miktar kısımlarına sadece sayı girin!")


# --- BOTU BAŞLATMA (HER ZAMAN EN ALTTA KALMALI) ---# --- ÜCRETSİZ RENDER İÇİN WEB SUNUCUSU ---
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot aktif ve 7/24 calisiyor!")

async def main():
    init_db()
    
    # Web sunucusunu arka planda başlatıyoruz
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()
    
    # Botu başlatıyoruz
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())