import discord
from database.constants import DELETE_MATCH_TIMEOUT_IN_SEC
from services.lobby_service import delete_match_from_lobby, refresh_match_in_lobby
from services.match_service import delete_match, get_match_by_id, update_last_action

import asyncio

active_match_timers = {}
in_progress_match_timers = {}

async def start_enter_match_result_timer(match_id: int, channel: discord.TextChannel, timeout: int, callback):
    if match_id in active_match_timers:
        del active_match_timers[match_id]

    async def timer():
        await asyncio.sleep(timeout)
        await callback(match_id, channel)

    # Start a new timer
    in_progress_match_timers[match_id] = asyncio.create_task(timer())


async def enter_match_result_callback(match_id: int, channel: discord.TextChannel):
    match = get_match_by_id(match_id)

    if match is not None:
        await refresh_match_in_lobby(channel, match, match.team_a, match.team_b)

    if match_id in in_progress_match_timers:
        del in_progress_match_timers[match_id]

"""
Starts a timer for a match. If no new action occurs before the timeout, calls the callback.

Args:
    match_id (int): The ID of the match.
    timeout (int): Timeout in seconds.
    callback (function): The function to call when the timer expires.
"""
async def start_match_timer(match_id: int, channel: discord.TextChannel, timeout: int, callback):
    if match_id in active_match_timers:
        # Cancel the previous timer if it exists
        active_match_timers[match_id].cancel()

    async def timer():
        await asyncio.sleep(timeout)
        await callback(match_id, channel)

    # Start a new timer
    active_match_timers[match_id] = asyncio.create_task(timer())

"""
Callback function to handle match deletion when the timer expires.

Args:
    match_id (int): The ID of the match to delete.
"""
async def delete_match_callback(match_id: int, channel: discord.TextChannel):
    match = get_match_by_id(match_id)

    if match is not None:
        delete_match(match_id)
        await delete_match_from_lobby(channel, match)
    
    if match_id in active_match_timers:
        del active_match_timers[match_id]


"""
Handles match actions by updating the last action timestamp and restarting the timer.

Args:
    match_id (int): The ID of the match.
    timeout (int): Timeout in seconds before the match is deleted if no new actions occur.
"""
async def on_match_action(match_id: int, channel: discord.TextChannel):
    update_last_action(match_id)
    await start_match_timer(match_id, channel, DELETE_MATCH_TIMEOUT_IN_SEC, delete_match_callback)