from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, CallbackQuery
from pyrogram import enums
import random
import asyncio
from texts import START_MESSAGE, CMDs
from database_handler import *
from commands_utilities import *
from callback_utilities import *
from config import *

app = Client(
    name="mybot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)


@app.on_message(filters.command("start"))
async def starting(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    await ensure_directory_exists("database")
    await update_course()
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(random.choice(START_MESSAGE))


@app.on_message(filters.command("cmds"))
async def get_cmds(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(CMDs)


@app.on_message(filters.command("getid"))
async def get_id(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    id_text = await send_id(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(id_text)


@app.on_message(filters.command("getvid"))
async def get_vid(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    vid, v_caption = await send_video_id(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(vid)
    if v_caption is not None:
        await message.reply_text(v_caption)


@app.on_message(filters.command("getcid"))
async def get_cid(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    cid = await get_chapter_id(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(cid)


@app.on_message(filters.command("getlid"))
async def get_lid(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    lid = await get_lesson_id(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(lid)


@app.on_message(filters.command("addcourse"))
async def get_course_name(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    result_text = await add_course(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(result_text)


@app.on_message(filters.command("addchapter"))
async def get_chapter_name(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    result_text = await add_chapter(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(result_text)


@app.on_message(filters.command("addlesson"))
async def get_lesson(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text("Please start forwarding video to me one by one.\n"
                             "Use /stop when you're done adding lessons.")
    course_name, chapter_id = await add_lesson(message)
    if course_name is None:
        await message.reply_text(chapter_id)
    else:
        user_actions[message.chat.id] = {}
        user_actions[message.chat.id]["is_adding"] = True
        user_actions[message.chat.id]["course_name"] = course_name
        user_actions[message.chat.id]["chapter_id"] = chapter_id


@app.on_message(filters.command("stop"))
async def stop_getting_lesson(client, message):
    if message.chat.id not in user_actions:
        return
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text("Adding lesson has been stopped.")
    user_actions.pop(message.chat.id)


@app.on_message(filters.command("cancel"))
async def cancel_saving_lesson(client, message):
    if message.chat.id not in user_actions:
        return
    user_actions[message.chat.id].pop("video_id")
    user_actions[message.chat.id].pop("video_caption")
    user_actions[message.chat.id].pop("video_description")
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text("Above video has been cancel to save.")


@app.on_message(filters.command("addcaption"))
async def get_caption_for_lesson(client, message):
    if message.chat.id not in user_actions:
        return
    caption_text = message.text[12:].strip()
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    if not caption_text:
        await message.reply_text("Invalid format.\nUse: /addcaption [name]")
    else:
        user_actions[message.chat.id]["video_caption"] = caption_text
        await message.reply_text("Caption has been saved.")


@app.on_message(filters.command("adddescription"))
async def get_description_for_lesson(client, message):
    if message.chat.id not in user_actions:
        return
    description_text = message.text[16:].strip()
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    if not description_text:
        await message.reply_text("Invalid format.\nUse: /adddescription [name]")
    else:
        user_actions[message.chat.id]["video_description"] = description_text
        await message.reply_text("Description has been saved.")


@app.on_message(filters.command("save"))
async def save_lesson(client, message):
    if message.chat.id not in user_actions:
        return
    t = user_actions[message.chat.id]
    result_text = await create_lesson(
        t["course_name"],
        t["chapter_id"],
        t["video_id"],
        t["video_caption"],
        t["video_description"]
    )
    t.pop("video_id")
    t.pop("video_caption")
    t.pop("video_description")
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(result_text)


@app.on_message(filters.command("renamecourse"))
async def rename_course(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    result_text = await change_course_detail(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(result_text)


@app.on_message(filters.command("renamechapter"))
async def rename_chapter(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    result_text = await change_chapter_detail(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(result_text)


@app.on_message(filters.command("renamelesson"))
async def rename_lesson(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    result_text = await change_lesson_detail(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(result_text)


@app.on_message(filters.command("fixlesson"))
async def fix_lesson(client, message):
    if message.chat.id in user_actions:
        user_actions.pop(message.chat.id)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text("Please start forwarding video to me.\n"
                             "Use /stop when you're done fixing lessons.")
    course_name, lesson_id = await get_detail_fixing_lesson(message)
    if course_name is None:
        await message.reply_text(lesson_id)
    else:
        user_actions[message.chat.id] = {}
        user_actions[message.chat.id]["is_fixing"] = True
        user_actions[message.chat.id]["course_name"] = course_name
        user_actions[message.chat.id]["lesson_id"] = lesson_id


@app.on_message(filters.command("cancelfix"))
async def cancel_fix(client, message):
    if message.chat.id not in user_actions:
        return
    user_actions[message.chat.id].pop("video_id")
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text("Above video has been cancel to save.")


@app.on_message(filters.command("savefix"))
async def save_fixed_lesson(client, message):
    if message.chat.id not in user_actions:
        return
    t = user_actions[message.chat.id]
    result_text = await rename_lesson_details(
        t["course_name"],
        t["lesson_id"],
        new_vid=t["video_id"],
    )
    t.pop("video_id")
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(result_text)


@app.on_message(filters.command("deletecourse"))
async def tg_delete_course(client, message):
    result_text = await get_delete_course(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(result_text)


@app.on_message(filters.command("deletechapter"))
async def tg_delete_chapter(client, message):
    result_text = await get_delete_chapter(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(result_text)


@app.on_message(filters.command("deletelesson"))
async def tg_delete_lesson(client, message):
    result_text = await get_delete_lesson(message)
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await message.reply_text(result_text)


@app.on_message(filters.video & ~filters.command(["addlesson", "fixlesson"]))
async def get_video_info(client, message):
    if message.chat.id in user_actions:
        if user_actions[message.chat.id].get("is_adding"):
            user_actions[message.chat.id]["video_id"] = message.video.file_id
            if message.caption:
                user_actions[message.chat.id]["video_caption"] = message.caption
                user_actions[message.chat.id]["video_description"] = None
            else:
                user_actions[message.chat.id]["video_caption"] = None
                user_actions[message.chat.id]["video_description"] = None
                await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
                await message.reply_text("This video has no caption.\nUse: /addcaption [name]\nOR Leave it Blank.")
                await message.reply_text("If you want to add description,\nUse: /adddescription [name].")
            await message.reply_text("Use: /save to confirm saving.\nUse: /cancel to cancel this video.")

        elif user_actions[message.chat.id].get("is_fixing"):
            user_actions[message.chat.id]["video_id"] = message.video.file_id
            await message.reply_text("Use: /savefix to confirm saving.\nUse: /cancelfix to cancel this video.")


@app.on_message(filters.command("search"))
async def show_course(client, message):
    results = await get_search_result(message)
    if not results:
        await message.reply_text("Sorry, no result found.")
        return

    course_buttons = await create_inline_keyboard(results)
    await message.reply(
        text="Please choose course.",
        reply_markup=InlineKeyboardMarkup(course_buttons)
    )


@app.on_callback_query(filters.regex("^course_"))
async def handle_callback_course(client, callback_query):
    course_name = callback_query.data.split("_")[1]
    results = await get_chapter_list(course_name)
    if not results:
        await callback_query.edit_message_text(
            text="There is no chapter in this course.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="Main Menu", callback_data=f"_main_menu_{course_name}")
            ]])
        )

    else:
        chapter_buttons = await create_inline_keyboard(results, course=course_name)
        await callback_query.edit_message_text(
            text="Please choose chapter.",
            reply_markup=InlineKeyboardMarkup(chapter_buttons)
        )


@app.on_callback_query(filters.regex("^_main_menu_"))
async def go_back_main_menu(client, callback_query):
    course_name = callback_query.data.split("_")[-1]
    results = await get_relevant_result(course_name)
    if not results:
        await callback_query.edit_message_text("Sorry, no result found.")
        return

    course_buttons = await create_inline_keyboard(results)
    await callback_query.edit_message_text(
        text="Please choose course.",
        reply_markup=InlineKeyboardMarkup(course_buttons)
    )


@app.on_callback_query(filters.regex("^chapter_"))
async def handle_callback_chapter(client, callback_query):
    course_name, chapter_id = callback_query.data.split("_")[1], callback_query.data.split("_")[-1]
    results = await get_lesson_list(course_name, chapter_id)

    if not results:
        await callback_query.edit_message_text(
            text="There is no lesson in this chapter.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="Back", callback_data=f"_back_key_{course_name}"),
                InlineKeyboardButton(text="Main Menu", callback_data=f"_main_menu_{course_name}")
            ]])
        )

    else:
        lesson_buttons = await create_inline_keyboard(results, course=course_name, chapter_id=chapter_id)
        await callback_query.edit_message_text(
            text="Please choose lesson.",
            reply_markup=InlineKeyboardMarkup(lesson_buttons)
        )


@app.on_callback_query(filters.regex("^_back_key_"))
async def handle_callback_back(client, callback_query):
    course_name = callback_query.data.split("_")[-1]
    results = await get_chapter_list(course_name)
    if not results:
        await callback_query.edit_message_text(
            text="There is no chapter in this course.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="Main Menu", callback_data=f"_main_menu_{course_name}")
            ]])
        )

    else:
        chapter_buttons = await create_inline_keyboard(results, course=course_name)
        await callback_query.edit_message_text(
            text="Please choose course.",
            reply_markup=InlineKeyboardMarkup(chapter_buttons)
        )


@app.on_callback_query(filters.regex("^lesson"))
async def handle_callback_lesson(client, callback_query):
    split_data = callback_query.data.split("_")
    check_all = split_data[1]
    if check_all == "all":
        course_name, chapter_id = split_data[2], split_data[-1]
        results = await get_lesson_details(course_name, chapter_id=chapter_id)
    else:
        course_name, lesson_id = split_data[2], split_data[-1]
        results = await get_lesson_details(course_name, lesson_id=lesson_id)

    try:
        logo = "<b>Yami Code Academy</b>"
        for result in results:
            description = result.get("video_description", "")
            if description:
                caption = f"<b>{result.get('video_caption', 'No caption')}</b>\n\n{description}\n{logo}"
            else:
                caption = f"<b>{result.get('video_caption', 'No caption')}</b>\n\n{logo}"
            video = result.get("video_id")
            await client.send_video(
                chat_id=callback_query.message.chat.id,
                video=video,
                caption=caption,
                protect_content=True
            )
            await asyncio.sleep(0.5)
        await callback_query.message.delete()

    except Exception as e:
        await client.send_message(callback_query.message.chat.id, f"An error occurred: {str(e)}")


if __name__ == "__main__":
    print("Yami Code Academy.")
    print("Bot Started!")
    app.run()
