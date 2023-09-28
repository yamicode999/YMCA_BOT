from database_handler import *
from texts import get_id_text

user_actions = {}


async def send_id(message):
    if message.reply_to_message:
        if message.reply_to_message.forward_from:
            user_id = message.reply_to_message.forward_from.id
            user_name = message.reply_to_message.forward_from.username or ""
            f_name = message.reply_to_message.forward_from.first_name or ""
            l_name = message.reply_to_message.forward_from.last_name or ""
            full_name = f"{f_name} {l_name}".strip()
        else:
            user_id = message.reply_to_message.from_user.id
            user_name = message.reply_to_message.from_user.username or ""
            f_name = message.reply_to_message.from_user.first_name or ""
            l_name = message.reply_to_message.from_user.last_name or ""
            full_name = f"{f_name} {l_name}".strip()
    else:
        user_id = message.from_user.id
        user_name = message.from_user.username or ""
        f_name = message.from_user.first_name or ""
        l_name = message.from_user.last_name or ""
        full_name = f"{f_name} {l_name}".strip()
    return await get_id_text(user_id, user_name, full_name)


async def send_video_id(message):
    if not message.reply_to_message:
        return "Please use this command as a reply to a video.", None

    if not message.reply_to_message.video:
        return "The replied-to message is not a video.", None

    vid = message.reply_to_message.video.file_id

    if message.reply_to_message.caption:
        v_caption = message.reply_to_message.caption
    else:
        v_caption = "This video doesn't have a caption."
    return vid, v_caption


async def add_course(message):
    if message.reply_to_message:
        course_name = message.reply_to_message.text.strip()
    else:
        course_name = message.text[11:].strip()

    if not course_name:
        return "Invalid format.\nUse: /add [course_name]\nOR Use as a reply to a message."

    like_provided = False
    like = 0
    if '|' in course_name:
        course_name, like = [item.strip() for item in course_name.split('|', 1)]
        like = int(like)
        like_provided = True

    if like_provided:
        return await create_course(course_name, like)
    else:
        return await create_course(course_name)


async def add_chapter(message):
    if message.reply_to_message:
        raw_data = message.reply_to_message.text.strip()
    else:
        raw_data = message.text[12:].strip()

    if '|' not in raw_data:
        return "Invalid format.\nUse: /add [course_name] | [chapter_name]\nOR Use as a reply to a message"

    course_name, chapter_name = [item.strip() for item in raw_data.split('|', 1)]
    if not course_name or not chapter_name:
        return "Both course name and chapter name are required."

    return await create_chapter(course_name, chapter_name)


async def add_lesson(message):
    if message.reply_to_message:
        raw_data = message.reply_to_message.text.strip()
    else:
        raw_data = message.text[11:].strip()

    if '|' not in raw_data:
        return None, "Invalid format.\nUse: /add [course_name] | [chapter_id]\nOR Use as a reply to a message"

    course_name, chapter_id = [item.strip() for item in raw_data.split('|', 1)]
    if not course_name or not chapter_id:
        return None, "Both course name and chapter ID are required."

    return course_name, chapter_id


async def get_chapter_id(message):
    if message.reply_to_message:
        course_name = message.reply_to_message.text.strip()
    else:
        course_name = message.text[8:].strip()
    if not course_name:
        return "Invalid format.\nUse: /getcid [course_name]\nOR Use as a reply to a message"

    cid, error_text = await get_cid_dict(course_name)
    if cid is None:
        return error_text
    else:
        cid_text = f"<b>{course_name} Chapter IDs</b>\n\n"
        for key in cid:
            cid_text += f"<b> ╭ {key}</b>\n"
            cid_text += f"<b> ╰ </b>{cid[key]}\n\n"
        return cid_text


async def get_lesson_id(message):
    if message.reply_to_message:
        raw_data = message.reply_to_message.text.strip()
    else:
        raw_data = message.text[8:].strip()

    if '|' not in raw_data:
        return "Invalid format.\nUse: /getlid [course_name] | [chapter_id]\nOR Use as a reply to a message"

    course_name, chapter_id = [item.strip() for item in raw_data.split('|', 1)]
    if not course_name or not chapter_id:
        return "Both course name and chapter ID are required."

    lid, error_text = await get_lid_dict(course_name, chapter_id)
    if lid is None:
        return error_text
    else:
        lid_text = f"<b>{course_name} Lesson IDs</b>\n\n"
        for key in lid:
            caption = key[:10]
            if caption == "no_caption":
                caption = "No Caption"
            lid_text += f"<b> ╭ {caption}</b>\n"
            lid_text += f"<b> ╰ </b>{lid[key]}\n\n"
        return lid_text


async def change_course_detail(message):
    if message.reply_to_message:
        raw_data = message.reply_to_message.text.strip()
    else:
        raw_data = message.text[14:].strip()

    if '|' not in raw_data:
        return "Invalid format.\nUse: /renamecourse [course_name] | [new_name]\nOR Use as a reply to a message"

    course_name, new_name = [item.strip() for item in raw_data.split('|', 1)]
    if not course_name or not new_name:
        return "Both course name and new course name are required."

    if '|' in new_name:
        new_name, like = [item.strip() for item in new_name.split('|', 1)]
        like = int(like)
        return await rename_course_details(course_name, new_name, like=like)

    return await rename_course_details(course_name, new_name)


async def change_chapter_detail(message):
    if message.reply_to_message:
        raw_data = message.reply_to_message.text.strip()
    else:
        raw_data = message.text[15:].strip()

    if '|' not in raw_data:
        return ("Invalid format.\n"
                "Use: /renamechapter [course_name] | [chapter_id] | [new_name] \nOR Use as a reply to a message")

    course_name, chapter_id = [item.strip() for item in raw_data.split('|', 1)]
    new_name = ""

    if '|' in chapter_id:
        chapter_id, new_name = [item.strip() for item in chapter_id.split('|', 1)]

    if not course_name or not chapter_id or not new_name:
        return "course name, chapter id and new chapter name are required."

    return await rename_chapter_details(course_name, chapter_id, new_name)


async def change_lesson_detail(message):
    if message.reply_to_message:
        raw_data = message.reply_to_message.text.strip()
    else:
        raw_data = message.text[14:].strip()

    if '|' not in raw_data:
        return ("Invalid format.\n\n"
                "Use: /renamelesson [course_name] | [chapter_id] | [new_caption] to change caption only\n\n"
                "Use: /renamelesson [course_name] | [chapter_id] | use_old | [new_description] "
                "to change description only.\n\n"
                "Use: /renamelesson [course_name] | [chapter_id] | [new_caption] | [new_description] "
                "to change both.\n\nOr Use as a reply to a message.")

    course_name, lesson_id = [item.strip() for item in raw_data.split('|', 1)]
    new_caption = ""
    new_des = ""

    if '|' in lesson_id:
        lesson_id, new_caption = [item.strip() for item in lesson_id.split('|', 1)]

    if '|' in new_caption:
        new_caption, new_des = [item.strip() for item in new_caption.split('|', 1)]

    if not course_name or not lesson_id or not new_caption:
        return "Course name, Lesson ID and New Caption or New Description are required."

    if new_caption == "use_old":
        return await rename_lesson_details(course_name, lesson_id, new_description=new_des)

    if not new_des:
        return await rename_lesson_details(course_name, lesson_id, new_caption=new_caption)

    return await rename_lesson_details(course_name, lesson_id, new_caption=new_caption, new_description=new_des)


async def get_detail_fixing_lesson(message):
    if message.reply_to_message:
        raw_data = message.reply_to_message.text.strip()
    else:
        raw_data = message.text[11:].strip()

    if '|' not in raw_data:
        return None, "Invalid format.\nUse: /add [course_name] | [lesson_id]\nOR Use as a reply to a message"

    course_name, lesson_id = [item.strip() for item in raw_data.split('|', 1)]
    if not course_name or not lesson_id:
        return None, "Both course name and lesson ID are required."

    return course_name, lesson_id


async def get_delete_course(message):
    if message.reply_to_message:
        course_name = message.reply_to_message.text.strip()
    else:
        course_name = message.text[14:].strip()

    if not course_name:
        return "Invalid format.\nUse: /deletecourse [course_name]\nOR Use as a reply to a message."

    return await delete_course(course_name)


async def get_delete_chapter(message):
    if message.reply_to_message:
        raw_data = message.reply_to_message.text.strip()
    else:
        raw_data = message.text[15:].strip()

    if '|' not in raw_data:
        return "Invalid format.\nUse: /deletechapter [course_name] | [chapter_id]\nOR Use as a reply to a message"

    course_name, chapter_id = [item.strip() for item in raw_data.split('|', 1)]
    if not course_name or not chapter_id:
        return "Both course name and chapter ID are required."

    return await delete_chapter(course_name, chapter_id)


async def get_delete_lesson(message):
    if message.reply_to_message:
        raw_data = message.reply_to_message.text.strip()
    else:
        raw_data = message.text[14:].strip()

    if '|' not in raw_data:
        return "Invalid format.\nUse: /deletelesson [course_name] | [lesson_id]\nOR Use as a reply to a message"

    course_name, lesson_id = [item.strip() for item in raw_data.split('|', 1)]
    if not course_name or not lesson_id:
        return "Both course name and lesson ID are required."

    return await delete_lesson(course_name, lesson_id)


async def get_search_result(message):
    if message.reply_to_message:
        search_text = message.reply_to_message.text.strip()
    else:
        search_text = message.text[8:].strip()

    if not search_text:
        return "Invalid format.\nUse: /search [course_name]\nOR Use as a reply to a message."

    results = await get_relevant_result(search_text)

    return results

    # if not results:
    #     return "Sorry, no result found."
    # else:
    #     return "\n".join(results)


if __name__ == "__main__":
    print("This is from commands_utilities.")
