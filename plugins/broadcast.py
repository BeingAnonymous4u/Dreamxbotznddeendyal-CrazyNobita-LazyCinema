import datetime
import time
import os
import asyncio
import logging

from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)

from database.users_chats_db import db
from info import ADMINS
from utils import (
    users_broadcast,
    groups_broadcast,
    temp,
    get_readable_time,
    clear_junk,
    junk_group
)


logger = logging.getLogger(__name__)

# Prevent multiple broadcasts at the same time
lock = asyncio.Lock()


# ============================================================
# BROADCAST CANCEL
# ============================================================

@Client.on_callback_query(filters.regex(r"^broadcast_cancel"))
async def broadcast_cancel(bot, query):

    try:
        _, target = query.data.split("#", 1)
    except ValueError:
        await query.answer(
            "Invalid cancel request.",
            show_alert=True
        )
        return

    if target == "users":

        temp.B_USERS_CANCEL = True

        await query.answer(
            "Trying to cancel users broadcast..."
        )

        try:
            await query.message.edit(
                "🛑 <b>ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ᴜꜱᴇʀꜱ "
                "ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...</b>",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.warning(
                "Failed to edit users cancel message: %s",
                e
            )

    elif target == "groups":

        temp.B_GROUPS_CANCEL = True

        await query.answer(
            "Trying to cancel groups broadcast..."
        )

        try:
            await query.message.edit(
                "🛑 <b>ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ɢʀᴏᴜᴘꜱ "
                "ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...</b>",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.warning(
                "Failed to edit groups cancel message: %s",
                e
            )


# ============================================================
# USER BROADCAST
# ============================================================

@Client.on_message(
    filters.command("broadcast")
    & filters.user(ADMINS)
    & filters.private
)
async def broadcast_users(bot, message):

    # --------------------------------------------------------
    # CHECK REPLY
    # --------------------------------------------------------

    if not message.reply_to_message:
        return await message.reply(
            "<b>Reply to a message to broadcast.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    # --------------------------------------------------------
    # CHECK LOCK
    # --------------------------------------------------------

    if lock.locked():
        return await message.reply(
            "⚠️ <b>Another broadcast is already in progress.</b>\n"
            "Please wait until it finishes.",
            parse_mode=enums.ParseMode.HTML
        )

    # Reset cancellation flag
    temp.B_USERS_CANCEL = False

    # --------------------------------------------------------
    # ASK PIN
    # --------------------------------------------------------

    ask = await message.reply(
        "<b>Do you want to pin this message in users?</b>",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(
            [
                ["Yes", "No"]
            ],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )

    try:

        response = await bot.listen(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            timeout=60
        )

    except asyncio.TimeoutError:

        try:
            await ask.delete()
        except Exception:
            pass

        return await message.reply(
            "❌ <b>Timed out. Broadcast cancelled.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:

        try:
            await ask.delete()
        except Exception:
            pass

        logger.error(
            "Error while waiting for broadcast response: %s",
            e,
            exc_info=True
        )

        return await message.reply(
            "❌ <b>Failed to get your response.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    finally:

        try:
            await ask.delete()
        except Exception:
            pass

    # --------------------------------------------------------
    # VALIDATE RESPONSE
    # --------------------------------------------------------

    if not response or not response.text:
        return await message.reply(
            "❌ <b>Invalid input. Broadcast cancelled.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    if response.text not in ("Yes", "No"):
        return await message.reply(
            "❌ <b>Invalid input. Broadcast cancelled.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    is_pin = response.text == "Yes"
    b_msg = message.reply_to_message

    # --------------------------------------------------------
    # FETCH USERS
    #
    # IMPORTANT:
    # get_all_users() is async and returns a cursor.
    #
    # WRONG:
    # users_cursor = db.get_all_users()
    #
    # CORRECT:
    # users_cursor = await db.get_all_users()
    # --------------------------------------------------------

    try:

        users_cursor = await db.get_all_users()

        users_list = []

        async for user in users_cursor:
            users_list.append(user)

        total_users = len(users_list)

        if total_users == 0:
            return await message.reply(
                "❌ <b>No users found in database!</b>",
                parse_mode=enums.ParseMode.HTML
            )

    except Exception as e:

        logger.error(
            "Error fetching users for broadcast: %s",
            e,
            exc_info=True
        )

        return await message.reply(
            "❌ <b>Error fetching users:</b>\n"
            f"<code>{str(e)[:3000]}</code>",
            parse_mode=enums.ParseMode.HTML
        )

    # --------------------------------------------------------
    # STATUS MESSAGE
    # --------------------------------------------------------

    status_msg = await message.reply_text(
        "📤 <b>Broadcasting your message...</b>",
        parse_mode=enums.ParseMode.HTML
    )

    success = 0
    blocked = 0
    deleted = 0
    failed = 0

    start_time = time.time()
    cancelled = False

    # --------------------------------------------------------
    # BROADCAST
    # --------------------------------------------------------

    async with lock:

        for i in range(0, total_users, 100):

            # Check cancellation
            if temp.B_USERS_CANCEL:

                temp.B_USERS_CANCEL = False
                cancelled = True
                break

            batch = users_list[i:i + 100]

            # ------------------------------------------------
            # SEND ONE USER
            # ------------------------------------------------

            async def send_user(user):

                try:

                    user_id = int(user["id"])

                    status, result = await users_broadcast(
                        user_id,
                        b_msg,
                        is_pin
                    )

                    if status:
                        return "Success"

                    return result

                except Exception as e:

                    logger.error(
                        "Error sending broadcast to user %s: %s",
                        user.get("id", "unknown"),
                        e,
                        exc_info=True
                    )

                    return "Error"

            # ------------------------------------------------
            # SEND BATCH
            # ------------------------------------------------

            results = await asyncio.gather(
                *(send_user(user) for user in batch),
                return_exceptions=True
            )

            # ------------------------------------------------
            # COUNT RESULTS
            # ------------------------------------------------

            for result in results:

                if isinstance(result, Exception):
                    failed += 1
                    continue

                if result == "Success":
                    success += 1

                elif result == "Blocked":
                    blocked += 1

                elif result == "Deleted":
                    deleted += 1

                else:
                    failed += 1

            done = min(
                i + len(batch),
                total_users
            )

            elapsed = get_readable_time(
                time.time() - start_time
            )

            # ------------------------------------------------
            # UPDATE STATUS
            # ------------------------------------------------

            try:

                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "❌ CANCEL",
                                callback_data="broadcast_cancel#users"
                            )
                        ]
                    ]
                )

                await status_msg.edit(
                    f"📣 <b>Broadcast Progress</b>\n\n"
                    f"👥 Total: <code>{total_users}</code>\n"
                    f"📊 Done: <code>{done}/{total_users}</code>\n"
                    f"📬 Success: <code>{success}</code>\n"
                    f"⛔ Blocked: <code>{blocked}</code>\n"
                    f"🗑️ Deleted: <code>{deleted}</code>\n"
                    f"❌ Failed: <code>{failed}</code>\n"
                    f"⏱️ Time: <code>{elapsed}</code>",
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=keyboard
                )

            except Exception as e:

                logger.warning(
                    "Error updating user broadcast status: %s",
                    e
                )

            # Give event loop some time
            await asyncio.sleep(0.1)

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    elapsed = get_readable_time(
        time.time() - start_time
    )

    if cancelled:
        title = "❌ <b>Broadcast Cancelled.</b>"
    else:
        title = "✅ <b>Broadcast Completed.</b>"

    final_status = (
        f"{title}\n\n"
        f"🕒 Time: <code>{elapsed}</code>\n"
        f"👥 Total: <code>{total_users}</code>\n"
        f"📬 Success: <code>{success}</code>\n"
        f"⛔ Blocked: <code>{blocked}</code>\n"
        f"🗑️ Deleted: <code>{deleted}</code>\n"
        f"❌ Failed: <code>{failed}</code>"
    )

    try:

        await status_msg.edit(
            final_status,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=None
        )

    except Exception as e:

        logger.error(
            "Error editing final user broadcast status: %s",
            e,
            exc_info=True
        )


# ============================================================
# GROUP BROADCAST
# ============================================================

@Client.on_message(
    filters.command("grp_broadcast")
    & filters.user(ADMINS)
    & filters.private
)
async def broadcast_group(bot, message):

    # --------------------------------------------------------
    # CHECK REPLY
    # --------------------------------------------------------

    if not message.reply_to_message:
        return await message.reply(
            "<b>Reply to a message to group broadcast.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    # --------------------------------------------------------
    # CHECK LOCK
    # --------------------------------------------------------

    if lock.locked():
        return await message.reply(
            "⚠️ <b>Another broadcast is already in progress.</b>\n"
            "Please wait.",
            parse_mode=enums.ParseMode.HTML
        )

    temp.B_GROUPS_CANCEL = False

    # --------------------------------------------------------
    # ASK PIN
    # --------------------------------------------------------

    ask = await message.reply(
        "<b>Do you want to pin this message in groups?</b>",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(
            [
                ["Yes", "No"]
            ],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )

    try:

        response = await bot.listen(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            timeout=60
        )

    except asyncio.TimeoutError:

        try:
            await ask.delete()
        except Exception:
            pass

        return await message.reply(
            "❌ <b>Timed out. Broadcast cancelled.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:

        try:
            await ask.delete()
        except Exception:
            pass

        logger.error(
            "Error while waiting for group broadcast response: %s",
            e,
            exc_info=True
        )

        return await message.reply(
            "❌ <b>Failed to get your response.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    finally:

        try:
            await ask.delete()
        except Exception:
            pass

    # --------------------------------------------------------
    # VALIDATE RESPONSE
    # --------------------------------------------------------

    if not response or not response.text:
        return await message.reply(
            "❌ <b>Invalid input. Broadcast cancelled.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    if response.text not in ("Yes", "No"):
        return await message.reply(
            "❌ <b>Invalid input. Broadcast cancelled.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    is_pin = response.text == "Yes"
    b_msg = message.reply_to_message

    # --------------------------------------------------------
    # FETCH GROUPS
    #
    # IMPORTANT FIX:
    # --------------------------------------------------------

    try:

        chats_cursor = await db.get_all_chats()

        chats_list = []

        async for chat in chats_cursor:
            chats_list.append(chat)

        total_chats = len(chats_list)

        if total_chats == 0:
            return await message.reply(
                "❌ <b>No groups found in database!</b>",
                parse_mode=enums.ParseMode.HTML
            )

    except Exception as e:

        logger.error(
            "Error fetching chats for group broadcast: %s",
            e,
            exc_info=True
        )

        return await message.reply(
            "❌ <b>Error fetching groups:</b>\n"
            f"<code>{str(e)[:3000]}</code>",
            parse_mode=enums.ParseMode.HTML
        )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status_msg = await message.reply_text(
        "📤 <b>Broadcasting your message to groups...</b>",
        parse_mode=enums.ParseMode.HTML
    )

    start_time = time.time()

    done = 0
    success = 0
    failed = 0
    cancelled = False

    # --------------------------------------------------------
    # GROUP BROADCAST
    # --------------------------------------------------------

    async with lock:

        for chat in chats_list:

            # Check cancellation
            if temp.B_GROUPS_CANCEL:

                temp.B_GROUPS_CANCEL = False
                cancelled = True
                break

            try:

                chat_id = int(chat["id"])

                result = await groups_broadcast(
                    chat_id,
                    b_msg,
                    is_pin
                )

                if result == "Success":
                    success += 1
                else:
                    failed += 1

            except Exception as e:

                logger.error(
                    "Error broadcasting to group %s: %s",
                    chat.get("id", "unknown"),
                    e,
                    exc_info=True
                )

                failed += 1

            done += 1

            # ------------------------------------------------
            # UPDATE EVERY 10 GROUPS
            # ------------------------------------------------

            if done % 10 == 0 or done == total_chats:

                elapsed = get_readable_time(
                    time.time() - start_time
                )

                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "❌ CANCEL",
                                callback_data="broadcast_cancel#groups"
                            )
                        ]
                    ]
                )

                try:

                    await status_msg.edit(
                        f"📣 <b>Group Broadcast Progress</b>\n\n"
                        f"👥 Total Groups: <code>{total_chats}</code>\n"
                        f"📊 Completed: <code>{done}/{total_chats}</code>\n"
                        f"📬 Success: <code>{success}</code>\n"
                        f"❌ Failed: <code>{failed}</code>\n"
                        f"⏱️ Time: <code>{elapsed}</code>",
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=keyboard
                    )

                except Exception as e:

                    logger.warning(
                        "Error updating group broadcast status: %s",
                        e
                    )

            await asyncio.sleep(0)

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    elapsed = get_readable_time(
        time.time() - start_time
    )

    if cancelled:
        title = "❌ <b>Groups broadcast cancelled!</b>"
    else:
        title = "✅ <b>Group broadcast completed.</b>"

    final_text = (
        f"{title}\n"
        f"⏱️ Completed in <code>{elapsed}</code>\n\n"
        f"👥 Total Groups: <code>{total_chats}</code>\n"
        f"✅ Completed: <code>{done}/{total_chats}</code>\n"
        f"📬 Success: <code>{success}</code>\n"
        f"❌ Failed: <code>{failed}</code>"
    )

    # --------------------------------------------------------
    # FINAL MESSAGE
    # --------------------------------------------------------

    try:

        await status_msg.edit(
            final_text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=None
        )

    except MessageTooLong:

        file_name = "group_broadcast_result.txt"

        try:

            with open(
                file_name,
                "w",
                encoding="utf-8"
            ) as outfile:
                outfile.write(final_text)

            await message.reply_document(
                file_name,
                caption="Group broadcast completed!"
            )

        finally:

            try:
                os.remove(file_name)
            except OSError:
                pass

    except Exception as e:

        logger.error(
            "Error editing final group broadcast status: %s",
            e,
            exc_info=True
        )


# ============================================================
# CLEAR JUNK USERS
# ============================================================

@Client.on_message(
    filters.command("clear_junk")
    & filters.user(ADMINS)
)
async def remove_junkuser__db(bot, message):

    try:

        # IMPORTANT FIX
        users_cursor = await db.get_all_users()

        b_msg = message

        status_msg = await message.reply_text(
            "ɪɴ ᴘʀᴏɢʀᴇss.... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ"
        )

        start_time = time.time()

        total_users = await db.total_users_count()

        blocked = 0
        deleted = 0
        failed = 0
        done = 0

        # ----------------------------------------------------
        # PROCESS USERS
        # ----------------------------------------------------

        async for user in users_cursor:

            try:

                pti, sh = await clear_junk(
                    int(user["id"]),
                    b_msg
                )

                if not pti:

                    if sh == "Blocked":
                        blocked += 1

                    elif sh == "Deleted":
                        deleted += 1

                    elif sh == "Error":
                        failed += 1

            except Exception as e:

                logger.error(
                    "Error clearing junk user %s: %s",
                    user.get("id", "unknown"),
                    e,
                    exc_info=True
                )

                failed += 1

            done += 1

            # ------------------------------------------------
            # UPDATE EVERY 50 USERS
            # ------------------------------------------------

            if done % 50 == 0:

                try:

                    await status_msg.edit(
                        f"<b>In Progress:</b>\n\n"
                        f"Total Users: <code>{total_users}</code>\n"
                        f"Completed: <code>{done}/{total_users}</code>\n"
                        f"Blocked: <code>{blocked}</code>\n"
                        f"Deleted: <code>{deleted}</code>\n"
                        f"Failed: <code>{failed}</code>",
                        parse_mode=enums.ParseMode.HTML
                    )

                except Exception as e:

                    logger.warning(
                        "Failed to update clear_junk status: %s",
                        e
                    )

    except Exception as e:

        logger.error(
            "Error in clear_junk: %s",
            e,
            exc_info=True
        )

        return await message.reply(
            f"❌ <b>Error:</b>\n"
            f"<code>{str(e)[:3000]}</code>",
            parse_mode=enums.ParseMode.HTML
        )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    time_taken = datetime.timedelta(
        seconds=int(time.time() - start_time)
    )

    try:
        await status_msg.delete()
    except Exception:
        pass

    try:

        await bot.send_message(
            message.chat.id,
            f"✅ <b>Completed</b>\n\n"
            f"Completed in: <code>{time_taken}</code>\n\n"
            f"Total Users: <code>{total_users}</code>\n"
            f"Completed: <code>{done}/{total_users}</code>\n"
            f"Blocked: <code>{blocked}</code>\n"
            f"Deleted: <code>{deleted}</code>\n"
            f"Failed: <code>{failed}</code>",
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:

        logger.error(
            "Error sending clear_junk result: %s",
            e,
            exc_info=True
        )


# ============================================================
# CLEAR JUNK GROUPS
# ============================================================

@Client.on_message(
    filters.command(
        ["junk_group", "clear_junk_group"]
    )
    & filters.user(ADMINS)
)
async def junk_clear_group(bot, message):

    try:

        # IMPORTANT FIX
        chats_cursor = await db.get_all_chats()

        groups_list = []

        async for group in chats_cursor:
            groups_list.append(group)

        if not groups_list:

            grp = await message.reply_text(
                "❌ Nᴏ ɢʀᴏᴜᴘs ғᴏᴜɴᴅ ғᴏʀ ᴄʟᴇᴀʀ ᴊᴜɴᴋ ɢʀᴏᴜᴘs."
            )

            await asyncio.sleep(60)

            try:
                await grp.delete()
            except Exception:
                pass

            return

        b_msg = message

        status_msg = await message.reply_text(
            "ɪɴ ᴘʀᴏɢʀᴇss..... ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ"
        )

        start_time = time.time()

        total_groups = len(groups_list)

        done = 0
        deleted = 0

        failed_messages = []

        # ----------------------------------------------------
        # PROCESS GROUPS
        # ----------------------------------------------------

        for group in groups_list:

            group_id = group.get("id", "unknown")

            try:

                pti, sh, ex = await junk_group(
                    int(group_id),
                    b_msg
                )

                if not pti and sh == "deleted":

                    deleted += 1

                    if ex:
                        failed_messages.append(
                            str(ex)
                        )

                    # Leave invalid/deleted group
                    try:

                        await bot.leave_chat(
                            int(group_id)
                        )

                    except Exception as e:

                        logger.warning(
                            "Error leaving group %s: %s",
                            group_id,
                            e
                        )

            except Exception as e:

                logger.error(
                    "Error processing junk group %s: %s",
                    group_id,
                    e,
                    exc_info=True
                )

                failed_messages.append(
                    str(e)
                )

            done += 1

            # ------------------------------------------------
            # UPDATE EVERY 50 GROUPS
            # ------------------------------------------------

            if done % 50 == 0:

                try:

                    await status_msg.edit(
                        f"<b>In Progress:</b>\n\n"
                        f"Total Groups: <code>{total_groups}</code>\n"
                        f"Completed: <code>{done}/{total_groups}</code>\n"
                        f"Deleted: <code>{deleted}</code>",
                        parse_mode=enums.ParseMode.HTML
                    )

                except Exception as e:

                    logger.warning(
                        "Failed to update junk group status: %s",
                        e
                    )

    except Exception as e:

        logger.error(
            "Error in junk_clear_group: %s",
            e,
            exc_info=True
        )

        return await message.reply(
            f"❌ <b>Error:</b>\n"
            f"<code>{str(e)[:3000]}</code>",
            parse_mode=enums.ParseMode.HTML
        )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    time_taken = datetime.timedelta(
        seconds=int(time.time() - start_time)
    )

    try:
        await status_msg.delete()
    except Exception:
        pass

    final_text = (
        f"✅ <b>Completed</b>\n"
        f"Completed in: <code>{time_taken}</code>\n\n"
        f"Total Groups: <code>{total_groups}</code>\n"
        f"Completed: <code>{done}/{total_groups}</code>\n"
        f"Deleted: <code>{deleted}</code>"
    )

    if failed_messages:

        final_text += (
            f"\n\n⚠️ Errors: "
            f"<code>{len(failed_messages)}</code>"
        )

    # --------------------------------------------------------
    # SEND FINAL RESULT
    # --------------------------------------------------------

    try:

        await bot.send_message(
            message.chat.id,
            final_text,
            parse_mode=enums.ParseMode.HTML
        )

        # ----------------------------------------------------
        # SEND ERROR DETAILS
        # ----------------------------------------------------

        if failed_messages:

            error_file = "junk.txt"

            try:

                with open(
                    error_file,
                    "w",
                    encoding="utf-8"
                ) as outfile:

                    outfile.write(
                        "\n".join(failed_messages)
                    )

                await message.reply_document(
                    error_file,
                    caption="Junk group processing details."
                )

            finally:

                try:
                    os.remove(error_file)
                except OSError:
                    pass

    except MessageTooLong:

        error_file = "junk.txt"

        try:

            with open(
                error_file,
                "w",
                encoding="utf-8"
            ) as outfile:

                outfile.write(final_text)

            await message.reply_document(
                error_file,
                caption="Junk group processing completed."
            )

        finally:

            try:
                os.remove(error_file)
            except OSError:
                pass

    except Exception as e:

        logger.error(
            "Error sending junk group final result: %s",
            e,
            exc_info=True
    )
