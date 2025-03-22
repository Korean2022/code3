import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# 📦 설정 로드
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config["token"]
ADMIN_ID = int(config["adminId"])
INTENTS = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=INTENTS)
tree = bot.tree

# ⚠️ 경고 데이터 저장/불러오기
WARNING_FILE = "warnings.json"
if os.path.exists(WARNING_FILE):
    with open(WARNING_FILE, "r", encoding="utf-8") as f:
        warnings = json.load(f)
else:
    warnings = {}

def save_warnings():
    with open(WARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(warnings, f, ensure_ascii=False, indent=2)

# ✅ 봇 준비 시
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ 로그인됨: {bot.user}")
    print(f"✅ 슬래시 명령어 등록 완료 ({len(await tree.sync())}개)")

# 📩 DM 수신 → 관리자 전달
@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        await message.channel.send("📬 상담사를 연결중입니다 잠시만 기다려주세요.")
        admin = await bot.fetch_user(ADMIN_ID)
        await admin.send(f"📩 **DM 수신**\n보낸 사람: {message.author} ({message.author.id})\n내용: {message.content}")
    await bot.process_commands(message)

# 💬 모든 슬래시 명령어
@tree.command(name="kick", description="Kick a user from the server")
@app_commands.describe(user="User to kick")
async def kick(interaction: discord.Interaction, user: discord.Member):
    await user.kick()
    await interaction.response.send_message(f"✅ {user.mention} 추방됨")

@tree.command(name="ban", description="Ban a user from the server")
@app_commands.describe(user="User to ban", reason="Reason for ban")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "사유 없음"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"✅ {user.mention} 차단됨. 사유: {reason}")

@tree.command(name="unban", description="Unban a user by ID")
@app_commands.describe(user_id="ID of user to unban")
async def unban(interaction: discord.Interaction, user_id: str):
    await interaction.guild.unban(discord.Object(id=int(user_id)))
    await interaction.response.send_message(f"✅ <@{user_id}> 차단 해제됨")

@tree.command(name="addrole", description="Give a role to a user")
@app_commands.describe(user="User to give role", role="Role to assign")
async def addrole(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    await user.add_roles(role)
    await interaction.response.send_message(f"✅ {user.mention}에게 {role.name} 역할 부여됨")

@tree.command(name="removerole", description="Remove a role from a user")
@app_commands.describe(user="User to remove role", role="Role to remove")
async def removerole(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    await user.remove_roles(role)
    await interaction.response.send_message(f"✅ {user.mention}의 {role.name} 역할 제거됨")

@tree.command(name="warn", description="Warn a user")
@app_commands.describe(user="User to warn", reason="Reason for warning")
async def warn(interaction: discord.Interaction, user: discord.User, reason: str):
    uid = str(user.id)
    if uid not in warnings:
        warnings[uid] = []
    warnings[uid].append(reason)
    save_warnings()
    await interaction.response.send_message(f"⚠️ {user.mention}에게 경고 부여됨. 사유: {reason}")

@tree.command(name="warnings", description="View warnings for a user")
@app_commands.describe(user="User to view warnings")
async def warnings_cmd(interaction: discord.Interaction, user: discord.User):
    user_warnings = warnings.get(str(user.id), [])
    if user_warnings:
        await interaction.response.send_message(f"⚠️ {user.mention} 경고 목록:\n" + "\n".join(user_warnings))
    else:
        await interaction.response.send_message(f"✅ {user.mention} 경고 없음")

@tree.command(name="clearwarnings", description="Clear all warnings for a user")
@app_commands.describe(user="User to clear warnings for")
async def clear_warnings(interaction: discord.Interaction, user: discord.User):
    warnings.pop(str(user.id), None)
    save_warnings()
    await interaction.response.send_message(f"✅ {user.mention}의 경고를 모두 삭제했습니다")

@tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! 지연 시간: {round(bot.latency * 1000)}ms")

@tree.command(name="userinfo", description="Get info about a user")
@app_commands.describe(user="User to get info")
async def userinfo(interaction: discord.Interaction, user: discord.User):
    member = interaction.guild.get_member(user.id)
    joined = member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member else "정보 없음"
    await interaction.response.send_message(f"👤 사용자: {user}\nID: {user.id}\n서버 가입일: {joined}")

# 🔌 봇 실행
bot.run(TOKEN)