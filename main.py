import discord
from discord import app_commands
from discord.ext import commands

# ---------- CONFIG: REPLACE THESE ----------
TOKEN = "MTUyMzU1ODczNTExMTUyNDQzNQ.G8FEIa.5CFs9DvPMc1Hbt_tTFmfcP8QGMSnuAdjFaM4WI"
GUILD_ID = 1273371437817790514       # Guild ID where command registers

ROLE_SCRIM_PING = 1523559711767527644       # @Scrim Ping
ROLE_SUB_PING   = 1523559741245358233       # @Sub Ping
ROLE_REF_PING   = 1273382013730160730       # @Unofficial Referee Ping

SCRIM_CHANNEL_ID = 1273371437817790521      # channel where posts should go
# -------------------------------------------

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ===== Modals =====
class FindRefereeModal(discord.ui.Modal, title="Find Referee"):
    teams = discord.ui.TextInput(
        label="Teams (e.g. Team 1 vs Team 2)",
        style=discord.TextStyle.short,
        required=True,
    )
    size = discord.ui.TextInput(
        label="Scrim Size (e.g. 3v3)",
        style=discord.TextStyle.short,
        required=True,
    )
    scrim_code = discord.ui.TextInput(
        label="Scrim Code",
        style=discord.TextStyle.short,
        required=True,
    )

    def __init__(self, author: discord.User):
        super().__init__()
        self.author = author

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Find Referee",
            color=discord.Color.gold()
        )
        embed.add_field(name="Teams:", value=str(self.teams), inline=False)
        embed.add_field(name="Size:", value=str(self.size), inline=False)
        embed.set_footer(text=f"Posted by {self.author}")

        view = AcceptView(type_="find-referee", scrim_code=str(self.scrim_code))

        channel = interaction.client.get_channel(SCRIM_CHANNEL_ID)
        if channel is None:
            await interaction.response.send_message(
                "Configured scrim channel not found. Please contact an admin.",
                ephemeral=True
            )
            return

        # Acknowledge modal submission ephemerally, then send to scrim channel
        await interaction.response.send_message(
            "Your find-referee post has been sent.",
            ephemeral=True
        )
        await channel.send(
            content=f"<@&{ROLE_REF_PING}>",
            embed=embed,
            view=view
        )


class FindScrimModal(discord.ui.Modal, title="Find Scrim"):
    size = discord.ui.TextInput(
        label="Size (e.g. 3v3)",
        style=discord.TextStyle.short,
        required=True,
    )
    rank = discord.ui.TextInput(
        label="Rank",
        style=discord.TextStyle.short,
        required=True,
    )
    note = discord.ui.TextInput(
        label="Note (optional)",
        style=discord.TextStyle.paragraph,
        required=False,
    )
    referee = discord.ui.TextInput(
        label="Referee (Yes/No/Needed/etc.)",
        style=discord.TextStyle.short,
        required=True,
    )
    scrim_code = discord.ui.TextInput(
        label="Scrim Code",
        style=discord.TextStyle.short,
        required=True,
    )

    def __init__(self, author: discord.User):
        super().__init__()
        self.author = author

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Find Scrim",
            color=discord.Color.teal()
        )
        embed.add_field(name="Teams:", value="To be decided with opponent", inline=False)
        embed.add_field(name="Size:", value=str(self.size), inline=False)
        embed.add_field(name="Rank:", value=str(self.rank), inline=False)
        embed.add_field(name="Referee:", value=str(self.referee), inline=False)
        embed.add_field(name="Note:", value=str(self.note) if self.note else "None", inline=False)
        embed.set_footer(text=f"Posted by {self.author}")

        view = AcceptView(type_="find-scrim", scrim_code=str(self.scrim_code))

        channel = interaction.client.get_channel(SCRIM_CHANNEL_ID)
        if channel is None:
            await interaction.response.send_message(
                "Configured scrim channel not found. Please contact an admin.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Your find-scrim post has been sent.",
            ephemeral=True
        )
        await channel.send(
            content=f"<@&{ROLE_SCRIM_PING}>",
            embed=embed,
            view=view
        )


class FindSubModal(discord.ui.Modal, title="Find Sub"):
    scrim_code = discord.ui.TextInput(
        label="Scrim Code",
        style=discord.TextStyle.short,
        required=True,
    )
    teams = discord.ui.TextInput(
        label="Teams",
        style=discord.TextStyle.short,
        required=True,
    )
    sub_for = discord.ui.TextInput(
        label="Team that the person is subbing for",
        style=discord.TextStyle.short,
        required=True,
    )
    size = discord.ui.TextInput(
        label="Size (e.g. 3v3)",
        style=discord.TextStyle.short,
        required=True,
    )

    def __init__(self, author: discord.User):
        super().__init__()
        self.author = author

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Find Sub",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Teams:",
            value=f"{self.teams}\n(Subbing for: {self.sub_for})",
            inline=False
        )
        embed.add_field(name="Size:", value=str(self.size), inline=False)
        embed.set_footer(text=f"Posted by {self.author}")

        view = AcceptView(type_="find-sub", scrim_code=str(self.scrim_code))

        channel = interaction.client.get_channel(SCRIM_CHANNEL_ID)
        if channel is None:
            await interaction.response.send_message(
                "Configured scrim channel not found. Please contact an admin.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Your find-sub post has been sent.",
            ephemeral=True
        )
        await channel.send(
            content=f"<@&{ROLE_SUB_PING}>",
            embed=embed,
            view=view
        )


# ===== Accept Button View =====
class AcceptView(discord.ui.View):
    def __init__(self, type_: str, scrim_code: str):
        super().__init__(timeout=None)
        self.add_item(
            AcceptButton(
                custom_id=f"scrim_accept_{type_}_{scrim_code}"
            )
        )


class AcceptButton(discord.ui.Button):
    def __init__(self, custom_id: str):
        super().__init__(
            label="Accept",
            style=discord.ButtonStyle.success,
            custom_id=custom_id,
        )

    async def callback(self, interaction: discord.Interaction):
        # custom_id format: scrim_accept_<type>_<scrimCode...>
        parts = self.custom_id.split("_")
        scrim_code = "_".join(parts[3:])

        await interaction.response.send_message(
            content=f"Scrim Code: **{scrim_code}**",
            ephemeral=True
        )


# ===== Select menu for /scrim =====
class ScrimTypeSelect(discord.ui.Select):
    def __init__(self, author: discord.User):
        self.author = author
        options = [
            discord.SelectOption(
                label="Find Referee",
                value="find-referee",
                description="Post to find a referee for your scrim"
            ),
            discord.SelectOption(
                label="Find Scrim",
                value="find-scrim",
                description="Post to find another team to scrim"
            ),
            discord.SelectOption(
                label="Find Sub",
                value="find-sub",
                description="Post to find a substitute player"
            ),
        ]
        super().__init__(
            placeholder="Select what you need...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="scrim_type_select"
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]

        if choice == "find-referee":
            await interaction.response.send_modal(FindRefereeModal(self.author))
        elif choice == "find-scrim":
            await interaction.response.send_modal(FindScrimModal(self.author))
        elif choice == "find-sub":
            await interaction.response.send_modal(FindSubModal(self.author))


class ScrimSelectView(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=60)
        self.add_item(ScrimTypeSelect(author))


# ===== Slash Command =====
@bot.tree.command(name="scrim", description="Create scrim-related posts (find scrim, ref, sub).")
async def scrim(interaction: discord.Interaction):
    view = ScrimSelectView(author=interaction.user)
    await interaction.response.send_message(
        content="Choose what you want to create:",
        view=view,
        ephemeral=True
    )


# ===== Bot events =====
@bot.event
async def on_ready():
    print("on_ready fired")

    app_id = bot.application_id
    # get global commands
    global_cmds = await bot.http.request(discord.http.Route("GET", f"/applications/{app_id}/commands"))
    print("Global REST:", [c["name"] for c in global_cmds])

    # take local tree command objects and convert to minimal payloads for guild
    payloads = []
    for c in bot.tree.get_commands():
        payload = {"name": c.name, "description": c.description or "no desc", "options": []}
        # only simple top-level option handling (most slash usage here is simple)
        for opt in getattr(c, "parameters", []):
            pass
        payloads.append(payload)

    # Force overwrite guild commands with local names (no options)
    await bot.http.request(
        discord.http.Route("PUT", f"/applications/{app_id}/guilds/{GUILD_ID}/commands"),
        json=payloads
    )
    print("WROTE guild commands:", [p["name"] for p in payloads])

    synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print("SYNCED:", [c.name for c in synced])
    await bot.close()


bot.run(TOKEN)
