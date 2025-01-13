import discord
from discord.ui import Button, View

# Define the view with buttons for the main menu
class MainMenuView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Buttons persist until explicitly removed

        # Add buttons to the view
        self.add_item(Button(label="Create Match", style=discord.ButtonStyle.primary, custom_id="create_match"))
        #self.add_item(Button(label="View Profile", style=discord.ButtonStyle.secondary, custom_id="view_profile"))
        #self.add_item(Button(label="Help", style=discord.ButtonStyle.link, url="https://your-help-url.com"))  # Link button
        self.add_item(Button(label="Help", style=discord.ButtonStyle.secondary, custom_id="help"))  # Help button
        #self.add_item(Button(label="Test", style=discord.ButtonStyle.secondary, custom_id="test"))  # Dev purposes only
