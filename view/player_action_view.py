from discord.ui import View

from view.buttons.ban_player_button import BanButton
from view.buttons.kick_player_button import KickButton

class PlayerActionConfirm(View):
    def __init__(self, match_id, player_id):
        super().__init__(timeout=None)
        self.match_id = match_id
        self.player_id = player_id

        # Add kick and ban buttons
        self.add_item(KickButton(match_id, player_id))
        self.add_item(BanButton(match_id, player_id))