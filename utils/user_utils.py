import discord

async def get_member_name_by_id(channel: discord.TextChannel, id: int):
    guild = channel.guild
    if (guild is None):
        print(f"Player id {id} (Not Found)")
        return str(id)
    member = await guild.fetch_member(id)
    if (member is None):
        print(f"Player id {id} (Not Found)")
        return str(id)
    return member.display_name