import json
import os
import random
from datetime import datetime, timedelta
from nextcord.ext import commands
import nextcord

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = 'users.json'
        self.codes_file_path = 'codes.json'
        self.init_files()

    def init_files(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
        if not os.path.exists(self.codes_file_path):
            with open(self.codes_file_path, 'w') as f:
                json.dump({}, f)

    def get_users(self):
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def save_users(self, users):
        with open(self.file_path, 'w') as f:
            json.dump(users, f, indent=4)

    def get_codes(self):
        with open(self.codes_file_path, 'r') as f:
            return json.load(f)

    def save_codes(self, codes):
        with open(self.codes_file_path, 'w') as f:
            json.dump(codes, f, indent=4)

    def format_currency(self, amount):
        return "{:,}".format(amount)

    @commands.command(name="daily")
    async def daily(self, ctx):
        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users:
            users[user_id] = {"balance": 20000000, "last_daily": str(datetime.utcnow())}
            await ctx.send(f"🎉 Bạn đã nhận được 20,000,000 VND. Số dư hiện tại của bạn là {self.format_currency(users[user_id]['balance'])} VND.")
        else:
            last_daily = datetime.fromisoformat(users[user_id].get("last_daily", "1970-01-01T00:00:00"))
            if datetime.utcnow() - last_daily < timedelta(days=1):
                next_daily = last_daily + timedelta(days=1)
                time_remaining = next_daily - datetime.utcnow()
                hours, remainder = divmod(time_remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                await ctx.send(f"⏳ Bạn đã nhận phần thưởng hàng ngày. Vui lòng thử lại sau {hours} giờ, {minutes} phút, và {seconds} giây.")
                return

            users[user_id]["balance"] += 5000000
            users[user_id]["last_daily"] = str(datetime.utcnow())
            await ctx.send(f"🎁 Bạn đã nhận được 5,000,000 VND. Số dư hiện tại của bạn là {self.format_currency(users[user_id]['balance'])} VND.")
        
        self.save_users(users)

    @commands.command(name="give")
    async def give(self, ctx, member: commands.MemberConverter, amount: int):
        if amount <= 0:
            await ctx.send("⚠️ Số tiền chuyển phải là một số nguyên dương.")
            return

        giver_id = str(ctx.author.id)
        receiver_id = str(member.id)
        users = self.get_users()

        if giver_id not in users:
            users[giver_id] = {"balance": 0}
        if receiver_id not in users:
            users[receiver_id] = {"balance": 0}

        if users[giver_id]["balance"] < amount:
            await ctx.send("🚫 Bạn không có đủ tiền để chuyển.")
            return

        users[giver_id]["balance"] -= amount
        users[receiver_id]["balance"] += amount
        self.save_users(users)
        
        await ctx.send(
            f"💸 Bạn đã chuyển {self.format_currency(amount)} VND cho {member.display_name}.\n"
            f"Số dư hiện tại của bạn là {self.format_currency(users[giver_id]['balance'])} VND."
        )
        await member.send(f"🎉 Bạn đã nhận được {self.format_currency(amount)} VND từ {ctx.author.display_name}.\nSố dư hiện tại của bạn là {self.format_currency(users[receiver_id]['balance'])} VND.")

    @commands.command(name="top")
    async def top(self, ctx):
        users = self.get_users()

        # Sắp xếp người dùng theo số dư giảm dần
        sorted_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)
        top_users = sorted_users[:10]  # Lấy top 10

        embed = nextcord.Embed(title="🏆 Top 10 người dùng có nhiều tiền nhất", color=0x00ff00)
        for i, (user_id, data) in enumerate(top_users, 1):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(name=f"{i}. {user.display_name}", value=f"{self.format_currency(data['balance'])} VND", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="cash")
    async def cash(self, ctx):
        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users:
            users[user_id] = {"balance": 0}
            self.save_users(users)

        balance = users[user_id]["balance"]
        await ctx.send(f"💰 Số dư hiện tại của bạn là {self.format_currency(balance)} VND.")

    @commands.command(name="work")
    async def work(self, ctx):
        user_id = str(ctx.author.id)
        users = self.get_users()

        if user_id not in users:
            users[user_id] = {"balance": 0, "last_work": str(datetime.utcnow() - timedelta(minutes=25))}

        last_work = datetime.fromisoformat(users[user_id].get("last_work", "1970-01-01T00:00:00"))
        if datetime.utcnow() - last_work < timedelta(minutes=20):
            next_work = last_work + timedelta(minutes=20)
            time_remaining = next_work - datetime.utcnow()
            minutes, seconds = divmod(time_remaining.seconds, 60)
            await ctx.send(f"⏳ Bạn đã làm việc gần đây. Vui lòng thử lại sau {minutes} phút và {seconds} giây.")
            return

        reward = random.randint(800000, 5000000)
        users[user_id]["balance"] += reward
        users[user_id]["last_work"] = str(datetime.utcnow())

        jokes = [
            f"{ctx.author.mention} ,chúc mừng thangdaden đã nhận được {self.format_currency(reward)} VND.",
            f"{ctx.author.mention} đòi tiền nuôi con và nhận được {self.format_currency(reward)} VND.",
            f"{ctx.author.mention} bán vốn tự có và nhận được {self.format_currency(reward)} VND.",
            f"{ctx.author.mention} ngủ với phú bà và nhận được {self.format_currency(reward)} VND.",
            f"{ctx.author.mention} ăn chặn tiền từ thiện và đớp được {self.format_currency(reward)} VND."
        ]

        members = [member for member in ctx.guild.members if not member.bot and member.id != ctx.author.id]
        if members:  # Kiểm tra nếu danh sách members không trống
            random_user = random.choice(members)
            joke = random.choice(jokes).replace("@random_user", random_user.mention)
        else:
            joke = random.choice(jokes)
        
        self.save_users(users)

        await ctx.send(joke)

    @commands.command(name="redeem")
    async def redeem(self, ctx, code: str):
        user_id = str(ctx.author.id)
        users = self.get_users()
        codes = self.get_codes()

        if code not in codes:
            await ctx.send(f"❌ Mã **{code}** không hợp lệ.")
            return

        if "redeemed_codes" not in users[user_id]:
            users[user_id]["redeemed_codes"] = []

        if code in users[user_id]["redeemed_codes"]:
            await ctx.send(f"⚠️ Bạn đã sử dụng mã **{code}** trước đó.")
            return

        reward = codes[code]["reward"]
        users[user_id]["balance"] += reward
        users[user_id]["redeemed_codes"].append(code)
        self.save_users(users)

        await ctx.send(f"🎉 Bạn đã nhận được {self.format_currency(reward)} VND từ mã **{code}**. Số dư hiện tại của bạn là {self.format_currency(users[user_id]['balance'])} VND.")

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)  # Độ trễ tính bằng milliseconds
        await ctx.send(f"🏓 Pong! Độ trễ hiện tại là {latency}ms.")

def setup(bot):
    bot.add_cog(Economy(bot))
