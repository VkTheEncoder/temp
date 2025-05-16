# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
from pyrogram import filters, Client
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, LOG_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE, FORWARD_MODE
from plugins.users_api import get_user, get_short_link
import os
import json
import base64

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

@Client.on_message((filters.document | filters.video | filters.audio) & filters.private & filters.create(allowed))
async def incoming_gen_link(bot, message):
    username = (await bot.get_me()).username

    # choose forward vs. copy, and protect content
    if FORWARD_MODE:
        post = await message.forward(LOG_CHANNEL, protect_content=True)
    else:
        post = await message.copy(LOG_CHANNEL, protect_content=True)

    file_id = str(post.id)
    token = base64.urlsafe_b64encode(f"file_{file_id}".encode()).decode().strip("=")
    user = await get_user(message.from_user.id)

    if WEBSITE_URL_MODE:
        share_link = f"{WEBSITE_URL}?Tech_VJ={token}"
    else:
        share_link = f"https://t.me/{username}?start={token}"

    if user["base_site"] and user["shortener_api"] is not None:
        short = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")


@Client.on_message(filters.command(['link']) & filters.create(allowed))
async def gen_link_s(bot, message):
    username = (await bot.get_me()).username
    replied = message.reply_to_message
    if not replied:
        return await message.reply('Reply to a message to get a shareable link.')

    # choose forward vs. copy, and protect content
    if FORWARD_MODE:
        post = await replied.forward(LOG_CHANNEL, protect_content=True)
    else:
        post = await replied.copy(LOG_CHANNEL, protect_content=True)

    file_id = str(post.id)
    token = base64.urlsafe_b64encode(f"file_{file_id}".encode()).decode().strip("=")
    user = await get_user(message.from_user.id)

    if WEBSITE_URL_MODE:
        share_link = f"{WEBSITE_URL}?Tech_VJ={token}"
    else:
        share_link = f"https://t.me/{username}?start={token}"

    if user["base_site"] and user["shortener_api"] is not None:
        short = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")


@Client.on_message(filters.command(['batch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    username = (await bot.get_me()).username
    if " " not in message.text:
        return await message.reply("Use correct format.\nExample /batch https://t.me/vj_botz/10 https://t.me/vj_botz/20.")
    links = message.text.strip().split(" ")
    if len(links) != 3:
        return await message.reply("Use correct format.\nExample /batch https://t.me/vj_botz/10 https://t.me/vj_botz/20.")
    cmd, first, last = links
    regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?([\dA-Za-z_]+)/(\d+)$")

    match = regex.match(first)
    if not match:
        return await message.reply('Invalid link')
    f_chat_id, f_msg_id = match.group(4), int(match.group(5))
    if f_chat_id.isnumeric():
        f_chat_id = int(f"-100{f_chat_id}")

    match = regex.match(last)
    if not match:
        return await message.reply('Invalid link')
    l_chat_id, l_msg_id = match.group(4), int(match.group(5))
    if l_chat_id.isnumeric():
        l_chat_id = int(f"-100{l_chat_id}")

    if f_chat_id != l_chat_id:
        return await message.reply("Chat IDs do not match.")

    try:
        _ = (await bot.get_chat(f_chat_id)).id
    except ChannelInvalid:
        return await message.reply('Make me admin in that channel to index files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid link specified.')
    except Exception as e:
        return await message.reply(f'Error: {e}')

    sts = await message.reply("**Generating links... this may take a while.**")
    FRMT = (
        "**Generating links...**\n"
        "**Total:** {total}\n"
        "**Done:** {current}\n"
        "**Remaining:** {rem}\n"
        "**Status:** {sts}"
    )

    outlist, og, tot = [], 0, 0
    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        tot += 1
        if og % 20 == 0:
            try:
                await sts.edit(FRMT.format(
                    total=l_msg_id - f_msg_id,
                    current=tot,
                    rem=(l_msg_id - f_msg_id) - tot,
                    sts="Saving"
                ))
            except:
                pass
        if msg.empty or msg.service:
            continue
        outlist.append({"channel_id": f_chat_id, "msg_id": msg.id})
        og += 1

    batch_file = f"batchmode_{message.from_user.id}.json"
    with open(batch_file, "w+") as f:
        json.dump(outlist, f)
    post = await bot.send_document(LOG_CHANNEL, batch_file, file_name="Batch.json", caption="⚠️ Batch Generated.")
    os.remove(batch_file)

    token = base64.urlsafe_b64encode(str(post.id).encode()).decode().strip("=")
    user = await get_user(message.from_user.id)

    if WEBSITE_URL_MODE:
        share_link = f"{WEBSITE_URL}?Tech_VJ=BATCH-{token}"
    else:
        share_link = f"https://t.me/{username}?start=BATCH-{token}"

    if user["base_site"] and user["shortener_api"] is not None:
        short = await get_short_link(user, share_link)
        await sts.edit(f"<b>⭕ Here is your link (contains {og} files):\n\n🖇️ Short Link: {short}</b>")
    else:
        await sts.edit(f"<b>⭕ Here is your link (contains {og} files):\n\n🔗 Original Link: {share_link}</b>")
