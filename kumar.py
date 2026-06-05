reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

# --- LİDERLİK TABLOSU ---
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
           f"• /bakiyever [Kullanıcı_ID] [Miktar] -> Oyuncuya altın ekler.\n" \
           f"• Örnek: `/bakiyever 8217991199 5000`"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("bakiyever"))
async def admin_give_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Yetkiniz yok!")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer("⚠️ Hatalı kullanım!\nDoğru Kullanım: `/bakiyever [Kullanıcı_ID] [Miktar]`", parse_mode="Markdown")
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
        await message.answer("⚠️ Lütfen ID ve miktar kısımlarına sadece sayı girin!")


# --- ÜCRETSİZ RENDER İÇİN WEB SUNUCUSU ---
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot aktif ve 7/24 calisiyor!")

async def main():
    init_db()
    
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())