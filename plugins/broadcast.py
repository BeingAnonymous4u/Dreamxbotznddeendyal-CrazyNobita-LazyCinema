import datetime
import time
import os
import asyncio
import logging
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from database.users_chats_db import db
from info import ADMINS
from utils import users_broadcast, groups_broadcast, temp, get_readable_time, clear_junk, junk_group
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

logger = logging.getLogger(__name__)

lock = asyncio.Lock()

@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, target = query.data.split("#", 1)
    if target == 'users':
        temp.B_USERS_CANCEL = True
        await query.message.edit("🛑 ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ᴜꜱᴇʀꜱ ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...")
    elif target == 'groups':
        temp.B_GROUPS_CANCEL = True
        await query.message.edit("🛑 ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ɢʀᴏᴜᴘꜱ ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...")

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.private)
async def broadcast_users(bot, message):
    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to broadcast.</b>", parse_mode=enums.ParseMode.HTML)
    
    if lock.locked():
        return await message.reply("⚠️ Another broadcast is in progress. Please wait...")
    
    ask = await message.reply(
        "<b>Do you want to pin this message in users?</b>",
        reply_markup=ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True, resize_keyboard=True)
    )
    
    try:
        dreamxbotz_user_response = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id, timeout=60)
    except asyncio.TimeoutError:
        await ask.delete()
        return await message.reply("❌ Timed out. Broadcast cancelled.")
    
    await ask.delete()
    
    if dreamxbotz_user_response.text not in ("Yes", "No"):
        return await message.reply("❌ Invalid input. Broadcast cancelled.")

    is_pin = dreamxbotz_user_response.text == "Yes"
    b_msg = message.reply_to_message
    
    # ✅ FIX: সঠিকভাবে - cursor সরাসরি async for এ ব্যবহার করুন
    try:
        users_cursor = db.get_all_users()  # Direct cursor, don't await!
        users_list = []
        async for user in users_cursor:
            users_list.append(user)
        
        total_users = len(users_list)
        
        if total_users == 0:
            return await message.reply("❌ No users found in database!")
            
    except Exception as e:
        logger.error(f"❌ Error fetching users: {e}", exc_info=True)
        return await message.reply(f"❌ Error fetching users: {e}")
    
    dreamxbotz_status_msg = await message.reply_text("📤 <b>Broadcasting your message...</b>")
    success = blocked = deleted = failed = 0
    start_time = time.time()
    cancelled = False

    async def send(user):
        try:
            status, result = await users_broadcast(int(user["id"]), b_msg, is_pin)
            if status:
                return "Success"
            else:
                return result  # Returns: "Blocked", "Deleted", "Error"
        except Exception as e:
            logger.error(f"❌ Error sending broadcast to user {user['id']}: {e}")
            return "Error"

    async with lock:
        for i in range(0, total_users, 100):
            if temp.B_USERS_CANCEL:
                temp.B_USERS_CANCEL = False
                cancelled = True
                break
            
            batch = users_list[i:i + 100]
            results = await asyncio.gather(*[send(user) for user in batch], return_exceptions=True)

            for res in results:
                if isinstance(res, Exception):
                    failed += 1
                    continue
                
                if res == "Success":
                    success += 1
                elif res == "Blocked":
                    blocked += 1
                elif res == "Deleted":
                    deleted += 1
                elif res == "Error":
                    failed += 1

            done = i + len(batch)
            elapsed = get_readable_time(time.time() - start_time)
            
            try:
                await dreamxbotz_status_msg.edit(
                    f"📣 <b>Broadcast Progress....:</b>\n\n"
                    f"👥 Total: <code>{total_users}</code>\n"
                    f"✅ Done: <code>{done}</code>\n"
                    f"📬 Success: <code>{success}</code>\n"
                    f"⛔ Blocked: <code>{blocked}</code>\n"
                    f"🗑️ Deleted: <code>{deleted}</code>\n"
                    f"❌ Failed: <code>{failed}</code>\n"
                    f"⏱️ Time: {elapsed}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("❌ CANCEL", callback_data="broadcast_cancel#users")]
                    ])
                )
            except Exception as e:
                logger.error(f"❌ Error updating status: {e}")
            
            await asyncio.sleep(0.1)
    
    elapsed = get_readable_time(time.time() - start_time)
    final_status = (
        f"{'❌ <b>Broadcast Cancelled.</b>' if cancelled else '✅ <b>Broadcast Completed.</b>'}\n\n"
        f"🕒 Time: {elapsed}\n"
        f"👥 Total: <code>{total_users}</code>\n"
        f"📬 Success: <code>{success}</code>\n"
        f"⛔ Blocked: <code>{blocked}</code>\n"
        f"🗑️ Deleted: <code>{deleted}</code>\n"
        f"❌ Failed: <code>{failed}</code>"
    )
    
    try:
        await dreamxbotz_status_msg.edit(final_status)
    except Exception as e:
        logger.error(f"❌ Error editing final status: {e}")


@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.private)
async def broadcast_group(bot, message):
    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to group broadcast.</b>", parse_mode=enums.ParseMode.HTML)
    
    ask = await message.reply(
        "<b>Do you want to pin this message in groups?</b>",
        reply_markup=ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True, resize_keyboard=True)
    )
    
    try:
        dreamxbotz_user_response = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id, timeout=60)
    except asyncio.TimeoutError:
        await ask.delete()
        return await message.reply("❌ Timed out. Broadcast cancelled.")
    
    await ask.delete()
    
    if dreamxbotz_user_response.text not in ("Yes", "No"):
        return await message.reply("❌ Invalid input. Broadcast cancelled.")
    
    is_pin = dreamxbotz_user_response.text == "Yes"
    b_msg = message.reply_to_message
    
    # ✅ FIX: সঠিকভাবে - cursor সরাসরি async for এ ব্যবহার করুন
    try:
        chats_cursor = db.get_all_chats()  # Direct cursor, don't await!
        chats_list = []
        async for chat in chats_cursor:
            chats_list.append(chat)
        
        total_chats = len(chats_list)
        
        if total_chats == 0:
            return await message.reply("❌ No groups found in database!")
            
    except Exception as e:
        logger.error(f"❌ Error fetching chats: {e}", exc_info=True)
        return await message.reply(f"❌ Error fetching chats: {e}")
    
    dreamxbotz_status_msg = await message.reply_text("📤 <b>Broadcasting your message to groups...</b>")
    start_time = time.time()
    done = success = failed = 0
    cancelled = False

    async with lock:
        for chat in chats_list:
            time_taken = get_readable_time(time.time() - start_time)
            
            if temp.B_GROUPS_CANCEL:
                temp.B_GROUPS_CANCEL = False
                cancelled = True
                break
            
            try:
                sts = await groups_broadcast(int(chat['id']), b_msg, is_pin)
                if sts == "Success":
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"❌ Error broadcasting to group {chat['id']}: {e}")
                failed += 1
            
            done += 1
            
            if done % 10 == 0:
                btn = [[InlineKeyboardButton("❌ CANCEL", callback_data="broadcast_cancel#groups")]]
                try:
                    await dreamxbotz_status_msg.edit(
                        f"📣 <b>Group broadcast progress:</b>\n\n"
                        f"👥 Total Groups: <code>{total_chats}</code>\n"
                        f"✅ Completed: <code>{done} / {total_chats}</code>\n"
                        f"📬 Success: <code>{success}</code>\n"
                        f"❌ Failed: <code>{failed}</code>\n"
                        f"⏱️ Time: {time_taken}",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                except Exception as e:
                    logger.error(f"❌ Error updating group broadcast status: {e}")
    
    time_taken = get_readable_time(time.time() - start_time)
    dreamxbotz_text = (
        f"{'❌ <b>Groups broadcast cancelled!</b>' if cancelled else '✅ <b>Group broadcast completed.</b>'}\n"
        f"⏱️ Completed in {time_taken}\n\n"
        f"👥 Total Groups: <code>{total_chats}</code>\n"
        f"✅ Completed: <code>{done} / {total_chats}</code>\n"
        f"📬 Success: <code>{success}</code>\n"
        f"❌ Failed: <code>{failed}</code>"
    )
    
    try:
        await dreamxbotz_status_msg.edit(dreamxbotz_text)
    except MessageTooLong:
        with open("reason.txt", "w+") as outfile:
            outfile.write(dreamxbotz_text)
        await message.reply_document("reason.txt", caption="Group broadcast completed!")
        os.remove("reason.txt")
    except Exception as e:
        logger.error(f"❌ Error editing final group broadcast status: {e}")

@Client.on_message(filters.command("clear_junk") & filters.user(ADMINS))
async def remove_junkuser__db(bot, message):
    try:
        users_cursor = db.get_all_users()  # Direct cursor!
        b_msg = message 
        sts = await message.reply_text('ɪɴ ᴘʀᴏɢʀᴇss.... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ')   
        start_time = time.time()
        total_users = await db.total_users_count()
        blocked = 0
        deleted = 0
        failed = 0
        done = 0
        
        async for user in users_cursor:
            pti, sh = await clear_junk(int(user['id']), b_msg)
            if not pti:
                if sh == "Blocked":
                    blocked += 1
                elif sh == "Deleted":
                    deleted += 1
                elif sh == "Error":
                    failed += 1
            done += 1
            if done % 50 == 0:
                await sts.edit(f"In Progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nBlocked: {blocked}\nDeleted: {deleted}")    
        
        time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
        await sts.delete()
        await bot.send_message(message.chat.id, f"✅ Completed:\nCompleted in {time_taken}.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}")
    except Exception as e:
        logger.error(f"❌ Error in clear_junk: {e}", exc_info=True)
        await message.reply(f"❌ Error: {e}")

@Client.on_message(filters.command(["junk_group", "clear_junk_group"]) & filters.user(ADMINS))
async def junk_clear_group(bot, message):
    try:
        chats_cursor = db.get_all_chats()  # Direct cursor!
        groups_list = []
        async for group in chats_cursor:
            groups_list.append(group)
        
        if not groups_list:
            grp = await message.reply_text("❌ Nᴏ ɢʀᴏᴜᴘs ғᴏᴜɴᴅ ғᴏʀ ᴄʟᴇᴀʀ Jᴜɴᴋ ɢʀᴏᴜᴘs.")
            await asyncio.sleep(60)
            await grp.delete()
            return
        
        b_msg = message
        sts = await message.reply_text(text='ɪɴ ᴘʀᴏɢʀᴇss..... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ')
        start_time = time.time()
        total_groups = len(groups_list)
        done = 0
        failed = ""
        deleted = 0
        
        for group in groups_list:
            pti, sh, ex = await junk_group(int(group['id']), b_msg)        
            if not pti:
                if sh == "deleted":
                    deleted += 1 
                    failed += ex + "\n"
                    try:
                        await bot.leave_chat(int(group['id']))
                    except Exception as e:
                        logger.warning(f"Error leaving group {group['id']}: {e}")
            done += 1
            if done % 50 == 0:
                await sts.edit(f"in progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nDeleted: {deleted}")    
        
        time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
        await sts.delete()
        
        try:
            await bot.send_message(message.chat.id, f"✅ Completed:\nCompleted in {time_taken}.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nDeleted: {deleted}")
        except MessageTooLong:
            with open('junk.txt', 'w+') as outfile:
                outfile.write(failed)
            await message.reply_document('junk.txt', caption=f"Completed:\nCompleted in {time_taken}.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nDeleted: {deleted}")
            os.remove("junk.txt")
    except Exception as e:
        logger.error(f"❌ Error in junk_clear_group: {e}", exc_info=True)
        await message.reply(f"❌ Error: {e}")
