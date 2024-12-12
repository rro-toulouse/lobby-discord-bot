import discord
from discord import Embed
from discord.ui import Button, View
from database.models import MatchState
from services.match_service import get_match_by_id, update_match, delete_match
from utils.team_utils import get_team_names
from services.lobby_service import refresh_match_in_lobby

# Lobby Functionality
class MatchLobbyView(View):
    def __init__(self, match_id, creator_id):
        super().__init__()
        self.match_id = match_id
        self.creator_id = creator_id

    @discord.ui.button(label="Join Match", style=discord.ButtonStyle.green)
    async def join_match(self, interaction: discord.Interaction, button: Button):
        """Handle joining a match."""
        user_id = interaction.user.id
        match = get_match_by_id(self.match_id)

        if not match:
            await interaction.response.send_message("❌ Match does not exist!", ephemeral=True)
            return

        team_a = match.team_a
        team_b = match.team_b

        if user_id in team_a or user_id in team_b:
            await interaction.response.send_message("❌ You are already in this match!", ephemeral=True)
            return

        # Add to Team A if it's smaller; else add to Team B
        if len(team_a) <= len(team_b):
            team_a.append(user_id)
        else:
            team_b.append(user_id)

        update_match(self.match_id, team_a_players=team_a, team_b_players=team_b)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b)
        await interaction.response.send_message(f"✅ {interaction.user.mention} joined the match!", ephemeral=True)
       
    @discord.ui.button(label="Switch Team", style=discord.ButtonStyle.gray)
    async def switch_team(self, interaction: discord.Interaction, button: Button):
        """Switch the player's team."""
        user_id = interaction.user.id
        match = get_match_by_id(self.match_id)

        if not match:
            await interaction.response.send_message("❌ Match does not exist!", ephemeral=True)
            return
        
        team_a = match.team_a
        team_b = match.team_b

        if user_id in team_a:
            team_a.remove(user_id)
            team_b.append(user_id)
            await refresh_match_in_lobby(interaction.channel, match, team_a, team_b)
            message = f"✅ {interaction.user.mention} switched to Team B!"
        elif user_id in team_b:
            team_b.remove(user_id)
            team_a.append(user_id)
            await refresh_match_in_lobby(interaction.channel, match, team_a, team_b)
            message = f"✅ {interaction.user.mention} switched to Team A!"
        else:
            await interaction.response.send_message("❌ You are not part of any team!", ephemeral=True)
            return

        update_match(self.match_id, team_a_players=team_a, team_b_players=team_b)
        await interaction.response.send_message(message, ephemeral=True)

    @discord.ui.button(label="Leave Match", style=discord.ButtonStyle.danger)
    async def leave_match(self, interaction: discord.Interaction, button: Button):
        """Allow a user to leave the match."""
        user_id = interaction.user.id
        match = get_match_by_id(self.match_id)

        if not match:
            await interaction.response.send_message("❌ Match does not exist!", ephemeral=True)
            return

        team_a = match.team_a
        team_b = match.team_b

        if user_id in team_a:
            team_a.remove(user_id)
        elif user_id in team_b:
            team_b.remove(user_id)
        else:
            await interaction.response.send_message("❌ You are not part of this match!", ephemeral=True)
            return

        if len(team_a) == 0 and len(team_b) == 0:
            delete_match(self.match_id)
            await interaction.response.send_message("✅ You left the match. The match has been deleted as no players remain.", ephemeral=True)
        else:
            if user_id == self.creator_id:
                new_creator = team_a[0] if len(team_a) else team_b[0]
                update_match(self.match_id, team_a_players=team_a, team_b_players=team_b, creator_id=new_creator)
                await interaction.response.send_message(f"✅ You left the match. Leadership has been transferred to <@{new_creator}>.", ephemeral=True)
            else:
                update_match(self.match_id, team_a_players=team_a, team_b_players=team_b)
                await interaction.response.send_message("✅ You left the match.", ephemeral=True)
        match = get_match_by_id(self.match_id)
        await refresh_match_in_lobby(interaction.channel, match, team_a, team_b)

    @discord.ui.button(label="Start Match", style=discord.ButtonStyle.primary)
    async def start_match(self, interaction: discord.Interaction, button: Button):
        """Handle starting a match."""
        if interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ Only the team leader can start the match!", ephemeral=True)
            return

        match = get_match_by_id(self.match_id)
        if not match:
            await interaction.response.send_message("❌ Match does not exist!", ephemeral=True)
            return

        # Business rules
        team_a = match.team_a
        team_b = match.team_b
        if (len(team_a) != len(team_b)):
            await interaction.response.send_message("❌ Not same number of players in both teams !", ephemeral=True)
            return
        elif (len(team_a) < 2):
            await interaction.response.send_message("❌ Need at least 2 players in both teams !", ephemeral=True)
            return
        else:
            update_match(self.match_id, state=MatchState.IN_PROGRESS)
            await interaction.response.send_message("✅ Match started! No more players can join.", ephemeral=True)
            await interaction.message.edit(content="The match has started!", view=None)

class MatchLobbyEmbed(Embed):

    description = ""
    def __init__(self, game_type, creator_name):
        super().__init__()

        self.description = f"Game Type: **{game_type}**\n"
        self.description  += f"Created by: **{creator_name}**\n"
        embed = discord.Embed(
            title="New Match Created!",
            description=self.description ,
            color=discord.Color.blue()
        )

    async def _init(self, team_a, team_b):
        team_a_names = await get_team_names(team_a)
        team_b_names = await get_team_names(team_b)

        self.description  += f"**Team A:** 👑{', '.join(team_a_names)}\n"
        self.description  += f"**Team B:** {', '.join(team_b_names)}"