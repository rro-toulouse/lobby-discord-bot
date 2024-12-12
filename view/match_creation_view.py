import discord
from discord.ui import Button, View

# Define the match creation menu after clicking the "Create Match" button
class CreateMatchView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Keep buttons persistent

        # Buttons for selecting match type and size
        self.add_item(Button(label="Realism", style=discord.ButtonStyle.primary, custom_id="obj_realism"))
        self.add_item(Button(label="Default", style=discord.ButtonStyle.primary, custom_id="obj_default"))
