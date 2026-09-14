# ============================================================
# Font Generator Bot
# Powered by ProviderBotz
# Font source: font_string.py
# ============================================================

import logging

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from plugins.Dreamxfutures.font_string import Fonts


logger = logging.getLogger(__name__)


# ============================================================
# FONT STYLES
# Powered by ProviderBotz
# ============================================================

FONT_STYLES = {
    "typewriter": Fonts.typewriter,
    "outline": Fonts.outline,
    "serif": Fonts.serief,
    "bold_cool": Fonts.bold_cool,
    "cool": Fonts.cool,
    "small_cap": Fonts.smallcap,
    "script": Fonts.script,
    "script_bolt": Fonts.bold_script,
    "tiny": Fonts.tiny,
    "comic": Fonts.comic,
    "sans": Fonts.san,
    "slant_sans": Fonts.slant_san,
    "slant": Fonts.slant,
    "sim": Fonts.sim,
    "circles": Fonts.circles,
    "circle_dark": Fonts.dark_circle,
    "gothic": Fonts.gothic,
    "gothic_bolt": Fonts.bold_gothic,
    "cloud": Fonts.cloud,
    "happy": Fonts.happy,
    "sad": Fonts.sad,

    "special": Fonts.special,
    "squares": Fonts.square,
    "squares_bold": Fonts.dark_square,
    "andalucia": Fonts.andalucia,
    "manga": Fonts.manga,
    "stinky": Fonts.stinky,
    "bubbles": Fonts.bubbles,
    "underline": Fonts.underline,
    "ladybug": Fonts.ladybug,
    "rays": Fonts.rays,
    "birds": Fonts.birds,
    "slash": Fonts.slash,
    "stop": Fonts.stop,
    "skyline": Fonts.skyline,
    "arrows": Fonts.arrows,
    "qvnes": Fonts.rvnes,
    "strike": Fonts.strike,
    "frozen": Fonts.frozen,
}


# ============================================================
# PAGE 1
# PRIMARY + SUCCESS + DANGER BUTTONS
# Powered by ProviderBotz
# ============================================================

def first_page_buttons():

    buttons = [

        [
            InlineKeyboardButton(
                "𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛",
                callback_data="style+typewriter",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "𝕆𝕦𝕥𝕝𝕚𝕟𝕖",
                callback_data="style+outline",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "𝐒𝐞𝐫𝐢𝐟",
                callback_data="style+serif",
                style=enums.ButtonStyle.PRIMARY
            ),
        ],

        [
            InlineKeyboardButton(
                "𝑺𝒆𝒓𝒊𝒇",
                callback_data="style+bold_cool",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "𝑆𝑒𝑟𝑖𝑓",
                callback_data="style+cool",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "Sᴍᴀʟʟ Cᴀᴘs",
                callback_data="style+small_cap",
                style=enums.ButtonStyle.SUCCESS
            ),
        ],

        [
            InlineKeyboardButton(
                "𝓈𝒸𝓇𝒾𝓅𝓉",
                callback_data="style+script",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "𝓼𝓬𝓻𝓲𝓹𝓽",
                callback_data="style+script_bolt",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "ᵗⁱⁿʸ",
                callback_data="style+tiny",
                style=enums.ButtonStyle.PRIMARY
            ),
        ],

        [
            InlineKeyboardButton(
                "ᑕOᗰIᑕ",
                callback_data="style+comic",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "𝗦𝗮𝗻𝘀",
                callback_data="style+sans",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "𝙎𝙖𝙣𝙨",
                callback_data="style+slant_sans",
                style=enums.ButtonStyle.SUCCESS
            ),
        ],

        [
            InlineKeyboardButton(
                "𝘚𝘢𝘯𝘴",
                callback_data="style+slant",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "𝖲𝖺𝗇𝗌",
                callback_data="style+sim",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎",
                callback_data="style+circles",
                style=enums.ButtonStyle.PRIMARY
            ),
        ],

        [
            InlineKeyboardButton(
                "🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎",
                callback_data="style+circle_dark",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "𝔊𝔬𝔱𝔥𝔦𝔠",
                callback_data="style+gothic",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "𝕲𝖔𝖙𝖍𝖎𝖈",
                callback_data="style+gothic_bolt",
                style=enums.ButtonStyle.SUCCESS
            ),
        ],

        [
            InlineKeyboardButton(
                "C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡",
                callback_data="style+cloud",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "H̆̈ă̈p̆̈p̆̈y̆̈",
                callback_data="style+happy",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "S̑̈ȃ̈d̑̈",
                callback_data="style+sad",
                style=enums.ButtonStyle.PRIMARY
            ),
        ],

        [
            InlineKeyboardButton(
                "Next ➡️",
                callback_data="nxt",
                style=enums.ButtonStyle.PRIMARY
            )
        ],

        [
            InlineKeyboardButton(
                "✖️ Close",
                callback_data="font_close",
                style=enums.ButtonStyle.DANGER
            )
        ]
    ]

    return InlineKeyboardMarkup(buttons)


# ============================================================
# PAGE 2
# PRIMARY + SUCCESS + DANGER BUTTONS
# Powered by ProviderBotz
# ============================================================

def second_page_buttons():

    buttons = [

        [
            InlineKeyboardButton(
                "🇸 🇵 🇪 🇨 🇮 🇦 🇱 ",
                callback_data="style+special",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "🅂🅀🅄🄰🅁🄴🅂",
                callback_data="style+squares",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎",
                callback_data="style+squares_bold",
                style=enums.ButtonStyle.PRIMARY
            ),
        ],

        [
            InlineKeyboardButton(
                "ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ",
                callback_data="style+andalucia",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "爪卂几ᘜ卂",
                callback_data="style+manga",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "S̾t̾i̾n̾k̾y̾",
                callback_data="style+stinky",
                style=enums.ButtonStyle.SUCCESS
            ),
        ],

        [
            InlineKeyboardButton(
                "B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ",
                callback_data="style+bubbles",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "U͟n͟d͟e͟r͟l͟i͟n͟e͟",
                callback_data="style+underline",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "꒒ꍏꀷꌩꌃꀎꁅ",
                callback_data="style+ladybug",
                style=enums.ButtonStyle.PRIMARY
            ),
        ],

        [
            InlineKeyboardButton(
                "R҉a҉y҉s҉",
                callback_data="style+rays",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "B҈i҈r҈d҈s҈",
                callback_data="style+birds",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "S̸l̸a̸s̸h̸",
                callback_data="style+slash",
                style=enums.ButtonStyle.SUCCESS
            ),
        ],

        [
            InlineKeyboardButton(
                "s⃠t⃠o⃠p⃠",
                callback_data="style+stop",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆",
                callback_data="style+skyline",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "A͎r͎r͎o͎w͎s͎",
                callback_data="style+arrows",
                style=enums.ButtonStyle.PRIMARY
            ),
        ],

        [
            InlineKeyboardButton(
                "ዪሀክቿነ",
                callback_data="style+qvnes",
                style=enums.ButtonStyle.SUCCESS
            ),

            InlineKeyboardButton(
                "S̶t̶r̶i̶k̶e̶",
                callback_data="style+strike",
                style=enums.ButtonStyle.PRIMARY
            ),

            InlineKeyboardButton(
                "F༙r༙o༙z༙e༙n༙",
                callback_data="style+frozen",
                style=enums.ButtonStyle.SUCCESS
            ),
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="nxt+0",
                style=enums.ButtonStyle.PRIMARY
            )
        ],

        [
            InlineKeyboardButton(
                "✖️ Close",
                callback_data="font_close",
                style=enums.ButtonStyle.DANGER
            )
        ]
    ]

    return InlineKeyboardMarkup(buttons)


# ============================================================
# /font COMMAND
# Powered by ProviderBotz
# ============================================================

@Client.on_message(filters.private & filters.command("font"))
async def font_command(client, message):

    try:

        if not message.text:
            return

        # Get text after /font
        parts = message.text.split(None, 1)

        if len(parts) < 2 or not parts[1].strip():

            await message.reply_text(
                "❌ <b>Please enter some text.</b>\n\n"
                "<b>Example:</b>\n"
                "<code>/font ProviderBotz</code>"
            )

            return

        title = parts[1].strip()

        # Use client.send_message because this Pyrogram version
        # does not support reply_to_message_id in Message.reply()
        await client.send_message(
            chat_id=message.chat.id,
            text=title,
            reply_markup=first_page_buttons(),
            reply_to_message_id=message.id
        )

    except Exception as e:

        logger.exception(
            "Font command error: %s",
            e
        )

        try:
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Something went wrong while opening the font generator."
            )
        except Exception:
            pass


# ============================================================
# NEXT / BACK BUTTON
# Powered by ProviderBotz
# ============================================================

@Client.on_callback_query(filters.regex(r"^nxt"))
async def next_page(client, callback_query):

    try:

        if callback_query.data == "nxt":

            await callback_query.answer()

            await callback_query.message.edit_reply_markup(
                second_page_buttons()
            )

        elif callback_query.data == "nxt+0":

            await callback_query.answer()

            await callback_query.message.edit_reply_markup(
                first_page_buttons()
            )

    except Exception as e:

        logger.exception(
            "Next/Back button error: %s",
            e
        )

        try:
            await callback_query.answer(
                "❌ Something went wrong.",
                show_alert=True
            )
        except Exception:
            pass


# ============================================================
# FONT STYLE CALLBACK
# Powered by ProviderBotz
# ============================================================

@Client.on_callback_query(filters.regex(r"^style\+"))
async def style(client, callback_query):

    try:

        await callback_query.answer()

        # style+typewriter
        _, style_name = callback_query.data.split("+", 1)

        # Find selected font
        cls = FONT_STYLES.get(style_name)

        if cls is None:

            await callback_query.answer(
                "❌ Invalid font style.",
                show_alert=True
            )

            return

        # ----------------------------------------------------
        # Get original text
        # Powered by ProviderBotz
        # ----------------------------------------------------

        if (
            callback_query.message.reply_to_message
            and callback_query.message.reply_to_message.text
        ):

            try:

                old_text = (
                    callback_query
                    .message
                    .reply_to_message
                    .text
                    .split(None, 1)[1]
                )

            except IndexError:

                old_text = callback_query.message.text

        else:

            old_text = callback_query.message.text

        # ----------------------------------------------------
        # Generate font
        # ----------------------------------------------------

        new_text = cls(old_text)

        # ----------------------------------------------------
        # Keep existing buttons
        # ----------------------------------------------------

        await callback_query.message.edit_text(
            f"<code>{new_text}</code>\n\n"
            "👆 <b>Click To Copy</b>\n\n"
            "<i>Powered by ProviderBotz</i>",
            reply_markup=callback_query.message.reply_markup
        )

    except Exception as e:

        logger.exception(
            "Font style error: %s",
            e
        )

        try:

            await callback_query.answer(
                "❌ Unable to generate this font.",
                show_alert=True
            )

        except Exception:
            pass


# ============================================================
# CLOSE BUTTON
# Powered by ProviderBotz
# ============================================================

@Client.on_callback_query(filters.regex(r"^font_close$"))
async def close_font(client, callback_query):

    try:

        await callback_query.answer()

        await callback_query.message.delete()

    except Exception as e:

        logger.exception(
            "Font close error: %s",
            e
        )

        try:

            await callback_query.answer(
                "❌ Unable to close.",
                show_alert=True
            )

        except Exception:
            pass
