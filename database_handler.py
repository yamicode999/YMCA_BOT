import json
import os
import random
import string
import aiofiles
import aiofiles.os
from fuzzywuzzy import process

JSON_EXTENSION = ".json"


async def initialize_update_course():
    if not await aiofiles.os.path.exists("AVAILABLE_COURSES.json"):
        async with aiofiles.open("AVAILABLE_COURSES.json", 'w') as file:
            await file.write(json.dumps({}))


async def update_course():
    await initialize_update_course()

    async with aiofiles.open("AVAILABLE_COURSES.json", 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    course_list = [
        os.path.splitext(f)[0] for f in os.listdir("database")
        if os.path.isfile(os.path.join("database", f)) and f.endswith('.json')
    ]
    course_list_dict = {
        "available courses": course_list
    }
    data.update(course_list_dict)

    async with aiofiles.open("AVAILABLE_COURSES.json", 'w') as file:
        await file.write(json.dumps(data, indent=4))


async def get_courses():
    async with aiofiles.open("AVAILABLE_COURSES.json", 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)
    return data.get("available courses", [])


async def get_relevant_result(user_input):
    courses = await get_courses()
    matches = process.extract(user_input, courses, limit=5)
    best_matches = [match[0] for match in matches if match[1] >= 65]
    return best_matches


async def generate_random_word(length=5):
    """Generate a random word with a mix of uppercase, lowercase, and digits."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


async def ensure_directory_exists(directory_name):
    """Ensure the given directory exists. If not, create it."""
    if not await aiofiles.os.path.exists(directory_name):
        await aiofiles.os.makedirs(directory_name)


async def initialize_json(name):
    if not await aiofiles.os.path.exists(name):
        async with aiofiles.open(name, 'w') as file:
            await file.write(json.dumps({}))


async def create_course(course, like=0):
    courses = await get_courses()
    if course in courses:
        return f"'{course}' is already in the list."

    full_path = os.path.join("database", course + JSON_EXTENSION)
    await initialize_json(full_path)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    new_course = {
        "course_name": course,
        "like": like,
        "chapters": []
    }
    data.update(new_course)

    async with aiofiles.open(full_path, 'w') as file:
        await file.write(json.dumps(data, indent=4))

    await update_course()
    return f"'{course}' has been added."


async def create_chapter(course, chapter):
    courses = await get_courses()
    if course not in courses:
        return f"'{course}' not found."

    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    chapters = data.get("chapters", [])
    for temp_chapter in chapters:
        if temp_chapter.get("chapter_name") == chapter:
            return f"'{chapter}' already exists in the '{course}'."

    chapter_id = await generate_random_word(11)
    chapter_id = "C" + chapter_id

    new_chapter = {
        "chapter_id": chapter_id,
        "chapter_name": chapter,
        "lessons": []
    }
    data["chapters"].append(new_chapter)

    async with aiofiles.open(full_path, 'w') as file:
        await file.write(json.dumps(data, indent=4))

    return f"'{chapter}' has been added to '{course}'.\n" + f"Chapter ID: {chapter_id}"


async def create_lesson(course, chapter_id, vid, caption, description):
    courses = await get_courses()
    if course not in courses:
        return f"'{course}' not found."

    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    for temp_chapter in data.get("chapters", []):
        if temp_chapter["chapter_id"] == chapter_id:
            lesson_id = await generate_random_word(11)
            lesson_id = "L" + lesson_id

            new_lesson = {
                "lesson_id": lesson_id,
                "video_id": vid,
                "video_caption": caption,
                "video_description": description
            }
            temp_chapter["lessons"].append(new_lesson)

            async with aiofiles.open(full_path, 'w') as file:
                await file.write(json.dumps(data, indent=4))
            return "lesson has been saved.\n" + f"Lesson ID: {lesson_id}"

    return f"There is no chapter with ID {chapter_id} in the {course}."


async def rename_course_details(course, new_name, like=None):
    courses = await get_courses()
    if course not in courses:
        return f"'{course}' not found."

    full_path = os.path.join("database", course + JSON_EXTENSION)
    new_path = os.path.join("database", new_name + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    data["course_name"] = new_name
    if like is not None:
        data["like"] = like

    async with aiofiles.open(full_path, 'w') as file:
        await file.write(json.dumps(data, indent=4))

    await aiofiles.os.rename(full_path, new_path)

    await update_course()
    return f"{course} has been renamed to {new_name}."


async def rename_chapter_details(course, chapter_id, new_chapter_name):
    courses = await get_courses()
    if course not in courses:
        return f"'{course}' not found."

    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    for chapter in data.get("chapters", []):
        if chapter["chapter_id"] == chapter_id:
            chapter["chapter_name"] = new_chapter_name
            async with aiofiles.open(full_path, 'w') as file:
                await file.write(json.dumps(data, indent=4))
            return f"Chapter with ID {chapter_id} has been renamed."

    return f"There is no chapter with ID {chapter_id} in the {course}."


async def rename_lesson_details(course, lesson_id, new_vid=None, new_caption=None, new_description=None):
    courses = await get_courses()
    if course not in courses:
        return f"'{course}' not found."

    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    for temp_chapter in data.get("chapters", []):
        for lesson in temp_chapter["lessons"]:
            if lesson["lesson_id"] == lesson_id:
                if new_vid is not None:
                    lesson["video_id"] = new_vid
                if new_caption is not None:
                    lesson["video_caption"] = new_caption
                if new_description is not None:
                    lesson["video_description"] = new_description

                async with aiofiles.open(full_path, 'w') as file:
                    await file.write(json.dumps(data, indent=4))

                return f"Lesson with ID {lesson_id} has been updated."

    return f"There is no lesson with ID {lesson_id} in the course {course}."


async def delete_course(course):
    courses = await get_courses()
    if course not in courses:
        return f"'{course}' not found."

    full_path = os.path.join("database", course + JSON_EXTENSION)

    if await aiofiles.os.path.exists(full_path):
        await aiofiles.os.remove(full_path)
        await update_course()
        return f"'{course}' was successfully deleted."
    else:
        return f"'{course}' not found."


async def delete_chapter(course, chapter_id):
    courses = await get_courses()
    if course not in courses:
        return f"'{course}' not found."

    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    chapter_deleted = False
    for chapter in data.get("chapters", []):
        if chapter["chapter_id"] == chapter_id:
            data["chapters"].remove(chapter)
            async with aiofiles.open(full_path, 'w') as file:
                await file.write(json.dumps(data, indent=4))
            return f"Chapter with ID '{chapter_id}' was successfully deleted."

    return f"Chapter with ID '{chapter_id}' was not found."


async def delete_lesson(course, lesson_id):
    courses = await get_courses()
    if course not in courses:
        return f"'{course}' not found."

    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    for chapter in data.get("chapters", []):
        for lesson in chapter["lessons"]:
            if lesson["lesson_id"] == lesson_id:
                chapter["lessons"].remove(lesson)
                async with aiofiles.open(full_path, 'w') as file:
                    await file.write(json.dumps(data, indent=4))
                return f"Lesson with ID '{lesson_id}' was successfully deleted."

    return f"Lesson with ID '{lesson_id}' was not found."


async def get_cid_dict(course):
    courses = await get_courses()
    if course not in courses:
        return None, f"'{course}' not found."

    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    cid = {}
    for temp_chapter in data.get("chapters", []):
        cid[temp_chapter["chapter_name"]] = temp_chapter["chapter_id"]

    return cid, None


async def get_lid_dict(course, chapter_id):
    courses = await get_courses()
    if course not in courses:
        return None, f"'{course}' not found."

    full_path = os.path.join("database", course + JSON_EXTENSION)

    async with aiofiles.open(full_path, 'r') as file:
        data_str = await file.read()
        data = json.loads(data_str)

    for temp_chapter in data.get("chapters", []):
        if temp_chapter["chapter_id"] == chapter_id:
            lid = {}
            num = 1
            for temp_lesson in temp_chapter.get("lessons", []):
                if temp_lesson["video_caption"] is None:
                    lid[f"no_caption{num}"] = temp_lesson["lesson_id"]
                    num += 1
                else:
                    lid[temp_lesson["video_caption"]] = temp_lesson["lesson_id"]
            return lid, None

    return None, f"Chapter with ID '{chapter_id}' was not found."


if __name__ == "__main__":
    print("This is from database_handler.")
