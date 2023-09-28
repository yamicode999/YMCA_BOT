from pyrogram.types import InlineKeyboardButton, CallbackQuery
import aiofiles
import json
import os


JSON_EXTENSION = ".json"


async def create_inline_keyboard(list_for_kb, course=None, chapter_id=None):
    keyboard_button = []
    row = []

    # Create buttons based on the conditions
    for idx, name in enumerate(list_for_kb, 1):
        if chapter_id:
            button = InlineKeyboardButton(text=name["vcap"],
                                          callback_data=f"lesson_one_{course}_{name['lid']}")
        elif course:
            button = InlineKeyboardButton(text=name["c_name"], callback_data=f"chapter_{course}_{name['c_id']}")
        else:
            button = InlineKeyboardButton(text=name, callback_data=f"course_{name}")

        row.append(button)

        if idx % 2 == 0 or idx == len(list_for_kb):
            keyboard_button.append(row)
            row = []

    # Append additional buttons based on conditions
    if chapter_id:
        await append_chapter_buttons(keyboard_button, course, chapter_id)
    elif course:
        await append_course_buttons(keyboard_button, course)

    return keyboard_button


async def append_chapter_buttons(keyboard, course, chapter_id):
    if keyboard and len(keyboard[-1]) % 2 != 0:
        keyboard[-1].append(InlineKeyboardButton(text="All lessons", callback_data=f"lesson_all_{course}_{chapter_id}"))
        row = [
            InlineKeyboardButton(text="Back", callback_data=f"_back_key_{course}"),
            InlineKeyboardButton(text="Main Menu", callback_data=f"_main_menu_{course}")
        ]
        keyboard.append(row)
    else:
        row = [InlineKeyboardButton(text="All lessons", callback_data=f"lesson_all_{course}_{chapter_id}")]
        keyboard.append(row)
        row = [
            InlineKeyboardButton(text="Back", callback_data=f"_back_key_{course}"),
            InlineKeyboardButton(text="Main Menu", callback_data=f"_main_menu_{course}")
        ]
        keyboard.append(row)


async def append_course_buttons(keyboard, course):
    if keyboard and len(keyboard[-1]) % 2 != 0:
        keyboard[-1].append(InlineKeyboardButton(text="Main Menu", callback_data=f"_main_menu_{course}"))
    else:
        row = [InlineKeyboardButton(text="Main Menu", callback_data=f"_main_menu_{course}")]
        keyboard.append(row)


async def get_chapter_list(course):
    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    chapter_names = []

    for chapter in data.get("chapters", []):
        temp_dict = {
            "c_name": chapter["chapter_name"],
            "c_id": chapter["chapter_id"]
        }
        chapter_names.append(temp_dict)

    return chapter_names


async def get_lesson_list(course, chapter_id):
    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    lesson_names = []

    for chapter in data.get("chapters", []):
        if chapter["chapter_id"] == chapter_id:
            for lesson in chapter["lessons"]:
                temp_dict = {
                    "vcap": lesson["video_caption"],
                    "lid": lesson["lesson_id"]
                }
                lesson_names.append(temp_dict)

            return lesson_names


async def get_lesson_details(course, lesson_id=None, chapter_id=None):
    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    result = []

    if chapter_id:
        for temp_chapter in data.get("chapters", []):
            if temp_chapter["chapter_id"] == chapter_id:
                for lesson in temp_chapter["lessons"]:
                    temp_dict = {
                        "video_id": lesson["video_id"],
                        "video_caption": lesson["video_caption"],
                        "video_description": lesson["video_description"]
                    }
                    result.append(temp_dict)

                return result

    if lesson_id:
        for temp_chapter in data.get("chapters", []):
            for lesson in temp_chapter["lessons"]:
                if lesson["lesson_id"] == lesson_id:
                    temp_dict = {
                        "video_id": lesson["video_id"],
                        "video_caption": lesson["video_caption"],
                        "video_description": lesson["video_description"]
                    }
                    result.append(temp_dict)

                    return result
