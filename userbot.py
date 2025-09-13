import asyncio
import random
import json
import time
import os
from telethon import TelegramClient, events
from flask import Flask

# --------------------------
# CONFIG TELEGRAM USERBOT
# --------------------------
api_id = int(os.environ.get("API_ID", 19186443))
api_hash = os.environ.get("API_HASH", "8d60cedbb97c6bc03b20376ce8ef3b30")
session_name = 'session/userbot'
OWNER_ID = int(os.environ.get("OWNER_ID", 8081631178))

client = TelegramClient(session_name, api_id, api_hash)

# --------------------------
# DATA FILES
# --------------------------
KODE_FILE = "data/kode.json"
PRODUK_FILE = "data/produk.json"
REPLY_FILE = "data/reply.json"
START_TIME = time.time()

internal_cache = {
    "temp_transaksi": {},
    "temp_messages": [],
    "session_data": {}
}

# --------------------------
# HELPERS
# --------------------------
def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def get_uptime():
    seconds = int(time.time() - START_TIME)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s"

def get_latency():
    return 100

async def auto_delete(event, delay=2):
    try:
        await asyncio.sleep(delay)
        await event.delete()
    except:
        pass

async def only_owner(event):
    if event.sender_id != OWNER_ID:
        await event.reply("❌ Command ini hanya bisa diakses oleh owner.")
        await auto_delete(event)
        return False
    return True

# --------------------------
# FLASK WEBHOOK
# --------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Userbot aktif! 👍"

# --------------------------
# COMMANDS
# --------------------------

# Ping
@client.on(events.NewMessage(pattern="^!ping$"))
async def ping_handler(event):
    if not await only_owner(event): return
    await event.reply(f"🏓 Pong! Bot aktif.\n⏱ Latency: {get_latency()} ms")
    await auto_delete(event)

# Alive
@client.on(events.NewMessage(pattern="^!alive$"))
async def alive_handler(event):
    if not await only_owner(event): return
    banner = "╔═════════════════════╗\n      🌟 USERBOT 🌟      \n╚═════════════════════╝"
    info = f"\n🤖 Bot Status : ✅ Aktif\n💻 Owner : Kamu\n📦 Versi : 1.0\n⏰ Uptime : {get_uptime()}\n⚡ Latency : {get_latency()} ms"
    await event.reply(f"{banner}{info}")
    await auto_delete(event)

# Shutdown / Reload / Restart / Cache
@client.on(events.NewMessage(pattern="^!shutdown$"))
async def shutdown_handler(event):
    if not await only_owner(event): return
    await event.reply("⚠️ Userbot akan dimatikan...")
    await auto_delete(event)
    await client.disconnect()
    import sys; sys.exit(0)

@client.on(events.NewMessage(pattern="^!(reload|restart)$"))
async def restart_handler(event):
    if not await only_owner(event): return
    await event.reply("♻️ Userbot direstart...")
    await auto_delete(event)
    await client.disconnect()
    import sys, os; os.execv(sys.executable, ['python'] + sys.argv)

@client.on(events.NewMessage(pattern="^!cache$"))
async def cache_handler(event):
    if not await only_owner(event): return
    internal_cache["temp_transaksi"].clear()
    internal_cache["temp_messages"].clear()
    internal_cache["session_data"].clear()
    await event.reply("🧹 Sampah internal dibersihkan!")
    await auto_delete(event)

# Broadcast
@client.on(events.NewMessage(pattern="^!broadcast (.+)"))
async def broadcast_handler(event):
    if not await only_owner(event): return
    pesan = event.pattern_match.group(1)
    await event.reply("📡 Mulai broadcast ke semua grup...")
    await auto_delete(event)
    dialogs = await client.get_dialogs()
    total = sukses = gagal = 0
    for dialog in dialogs:
        if dialog.is_group or dialog.is_channel:
            total += 1
            try:
                await client.send_message(dialog.id, pesan)
                sukses += 1
                await asyncio.sleep(random.randint(2,5))
            except:
                gagal += 1
    await event.reply(f"✅ Broadcast selesai!\n📊 Total grup: {total}\n✅ Sukses: {sukses}\n❌ Gagal: {gagal}")

# --------------------------
# Produk & Kode Commands
# --------------------------
@client.on(events.NewMessage(pattern="^!addproduk (.+) (.+)"))
async def addproduk(event):
    if not await only_owner(event): return
    nama, harga = event.pattern_match.group(1), event.pattern_match.group(2)
    produk = load_json(PRODUK_FILE)
    produk[nama] = harga
    save_json(PRODUK_FILE, produk)
    await event.reply(f"✅ Produk *{nama}* berhasil ditambahkan!")
    await auto_delete(event)

@client.on(events.NewMessage(pattern="^!editproduk (.+) (.+) (.+)"))
async def editproduk(event):
    if not await only_owner(event): return
    nama_lama, nama_baru, harga_baru = event.pattern_match.group(1), event.pattern_match.group(2), event.pattern_match.group(3)
    produk = load_json(PRODUK_FILE)
    if nama_lama in produk:
        del produk[nama_lama]
        produk[nama_baru] = harga_baru
        save_json(PRODUK_FILE, produk)
        await event.reply(f"✏️ Produk *{nama_lama}* diubah jadi *{nama_baru}* dengan harga Rp {harga_baru}")
    else:
        await event.reply("❌ Produk tidak ditemukan!")
    await auto_delete(event)

@client.on(events.NewMessage(pattern="^!pricelist$"))
async def pricelist(event):
    if not await only_owner(event): return
    produk = load_json(PRODUK_FILE)
    msg = "💰 Daftar Harga Produk:\n"
    for nama, harga in produk.items():
        msg += f"{nama} → Rp {harga}\n"
    await event.reply(msg)
    await auto_delete(event)

@client.on(events.NewMessage(pattern="^!addkode (.+) (.+)"))
async def addkode(event):
    if not await only_owner(event): return
    kode, nama = event.pattern_match.group(1), event.pattern_match.group(2)
    data = load_json(KODE_FILE)
    if nama not in data:
        data[nama] = []
    data[nama].append(kode)
    save_json(KODE_FILE, data)
    await event.reply(f"✅ Kode `{kode}` siap dipakai di produk *{nama}*!")
    await auto_delete(event)

@client.on(events.NewMessage(pattern="^!hapuskode (.+) (.+)"))
async def hapuskode(event):
    if not await only_owner(event): return
    nama, kode = event.pattern_match.group(1), event.pattern_match.group(2)
    data = load_json(KODE_FILE)
    if nama in data and kode in data[nama]:
        data[nama].remove(kode)
        save_json(KODE_FILE, data)
        await event.reply(f"🗑️ Kode `{kode}` sudah dihapus dari produk *{nama}*")
    else:
        await event.reply("❌ Kode tidak ditemukan!")
    await auto_delete(event)

@client.on(events.NewMessage(pattern="^!listcode$"))
async def listcode(event):
    if not await only_owner(event): return
    data = load_json(KODE_FILE)
    msg = "📦 Kode yang tersedia:\n"
    for nama, codes in data.items():
        msg += f"{nama}: {', '.join(codes)}\n"
    await event.reply(msg)
    await auto_delete(event)

# --------------------------
# Payment & Send Code
# --------------------------
@client.on(events.NewMessage(pattern="^!dana (.+)"))
async def dana(event):
    if not await only_owner(event): return
    nama = event.pattern_match.group(1)
    produk = load_json(PRODUK_FILE)
    if nama in produk:
        total = int(produk[nama]) + random.randint(0,999)
        await event.reply(f"💳 Bayar via DANA\nProduk: *{nama}*\nTotal: Rp {total}")
    else:
        await event.reply("❌ Produk tidak ditemukan!")
    await auto_delete(event)

@client.on(events.NewMessage(pattern="^!qris (.+)"))
async def qris(event):
    if not await only_owner(event): return
    nama = event.pattern_match.group(1)
    produk = load_json(PRODUK_FILE)
    if nama in produk:
        total = int(produk[nama]) + random.randint(0,999)
        await event.reply(f"💳 Bayar via QRIS\nProduk: *{nama}*\nTotal: Rp {total}")
    else:
        await event.reply("❌ Produk tidak ditemukan!")
    await auto_delete(event)

@client.on(events.NewMessage(pattern="^!sendcode (.+)"))
async def sendcode(event):
    if not await only_owner(event): return
    nama = event.pattern_match.group(1)
    data = load_json(KODE_FILE)
    produk = load_json(PRODUK_FILE)
    
    if nama in data and data[nama]:
             kode = data[nama].pop(0)
        save_json(KODE_FILE, data)
        harga = produk.get(nama, "N/A")
        msg = (
            f"🎉 Transaksi sukses!\n\n"
            f"Produk: *{nama}*\n"
            f"Harga: Rp {harga}\n"
            f"🚨 Kode kamu: `{kode}`\n\n"
            f"💡 Cara menggunakan kode:\n"
            f"1. Salin kode di atas\n"
            f"2. Buka bot ini: @ordertmbot dan klik Start atau Mulai\n"
            f"3. Masukkan kode di sana"
        )
        await event.reply(msg)
    else:
        await event.reply("❌ Kode tidak tersedia!")
    
    await auto_delete(event)

# --------------------------
# Auto Reply
# --------------------------
@client.on(events.NewMessage)
async def auto_reply(event):
    if not await only_owner(event): return
    reply_data = load_json(REPLY_FILE)
    text = event.raw_text.lower()
    if text in reply_data:
        await event.reply(reply_data[text])

@client.on(events.NewMessage(pattern="^!addreply (.+) (.+)"))
async def addreply(event):
    if not await only_owner(event): return
    kata, balasan = event.pattern_match.group(1).lower(), event.pattern_match.group(2)
    data = load_json(REPLY_FILE)
    data[kata] = balasan
    save_json(REPLY_FILE, data)
    await event.reply(f"✅ Auto reply untuk `{kata}` berhasil ditambahkan!")
    await auto_delete(event)

@client.on(events.NewMessage(pattern="^!delreply (.+)"))
async def delreply(event):
    if not await only_owner(event): return
    kata = event.pattern_match.group(1).lower()
    data = load_json(REPLY_FILE)
    if kata in data:
        del data[kata]
        save_json(REPLY_FILE, data)
        await event.reply(f"🗑️ Auto reply `{kata}` dihapus!")
    else:
        await event.reply("❌ Kata tidak ditemukan!")
    await auto_delete(event)

@client.on(events.NewMessage(pattern="^!listreply$"))
async def listreply(event):
    if not await only_owner(event): return
    data = load_json(REPLY_FILE)
    if data:
        msg = "🤖 Daftar Auto Reply:\n"
        for k, v in data.items():
            msg += f"{k} → {v}\n"
    else:
        msg = "🤖 Belum ada auto reply."
    await event.reply(msg)
    await auto_delete(event)

# --------------------------
# Help Command
# --------------------------
@client.on(events.NewMessage(pattern="^!help$"))
async def help_handler(event):
    if not await only_owner(event): return
    commands = [
        "🏪 Produk & Kode",
        "!addproduk <nama> <harga>",
        "!editproduk <nama_lama> <nama_baru> <harga_baru>",
        "!pricelist",
        "!addkode <kode> <nama>",
        "!hapuskode <nama> <kode>",
        "!listcode",
        "",
        "💳 Pembayaran",
        "!dana <nama>",
        "!qris <nama>",
        "!sendcode <nama>",
        "",
        "🤖 Auto Reply",
        "!addreply <kata> <balasan>",
        "!delreply <kata>",
        "!listreply",
        "",
        "⚡ Utilitas & Status",
        "!ping",
        "!alive",
        "!shutdown",
        "!reload",
        "!restart",
        "!cache",
        "!broadcast <pesan>",
        "!help"
    ]
    await event.reply("📜 Daftar Command Userbot:\n\n" + "\n".join(commands))
    await auto_delete(event)

# --------------------------
# Start Client for Railway
# --------------------------
async def start_client():
    await client.start()
    print("Userbot siap!")
    await asyncio.Event().wait()  # agar tetap berjalan

# Jalankan Telethon client di background
loop = asyncio.get_event_loop()
loop.create_task(start_client())

# Flask app siap dipakai Railway
# PORT akan otomatis dari environment variable
PORT = int(os.environ.get("PORT", 5000))
# Jangan pakai app.run() di Railway