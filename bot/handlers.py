
from ai.llm_client import llm_client
import json
from ai.prompt_templates import SCHEMA_PROMPT
from schema.validator import validate_and_fill
from dxf_gen.generator import create_plan
from preview.renderer import render_preview
from utils.files import unique_name
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .strings import STRINGS
from .keyboards import get_main_keyboard, get_language_keyboard, get_cancel_keyboard


class Questionnaire(StatesGroup):
    land_dims = State()
    floors = State()
    rooms = State()
    notes = State()


async def get_lang(state: FSMContext):
    data = await state.get_data()
    return data.get('lang', 'uz')


async def start(message: Message, state: FSMContext):
    lang = await get_lang(state)
    await message.answer(STRINGS[lang]['welcome'], reply_markup=get_main_keyboard(lang))


async def cmd_cancel(message: Message, state: FSMContext):
    lang = await get_lang(state)
    await state.clear()
    await state.update_data(lang=lang)
    await message.answer(STRINGS[lang]['canceled'], reply_markup=get_main_keyboard(lang))


async def create_project(message: Message, state: FSMContext):
    lang = await get_lang(state)
    await state.set_state(Questionnaire.land_dims)
    await message.answer(STRINGS[lang]['ask_dimensions'], reply_markup=get_cancel_keyboard(lang))


async def process_dims(message: Message, state: FSMContext):
    lang = await get_lang(state)
    if message.text == STRINGS[lang]['btn_cancel']:
        return await cmd_cancel(message, state)
    await state.update_data(land_dims=message.text)
    await state.set_state(Questionnaire.floors)
    await message.answer(STRINGS[lang]['ask_floors'], reply_markup=get_cancel_keyboard(lang))


async def process_floors(message: Message, state: FSMContext):
    lang = await get_lang(state)
    if message.text == STRINGS[lang]['btn_cancel']:
        return await cmd_cancel(message, state)
    await state.update_data(floors=message.text)
    await state.set_state(Questionnaire.rooms)
    await message.answer(STRINGS[lang]['ask_rooms'], reply_markup=get_cancel_keyboard(lang))


async def process_rooms(message: Message, state: FSMContext):
    lang = await get_lang(state)
    if message.text == STRINGS[lang]['btn_cancel']:
        return await cmd_cancel(message, state)
    await state.update_data(rooms=message.text)
    await state.set_state(Questionnaire.notes)
    await message.answer(STRINGS[lang]['ask_notes'], reply_markup=get_cancel_keyboard(lang))


async def process_notes_and_gen(message: Message, state: FSMContext):
    lang = await get_lang(state)
    if message.text == STRINGS[lang]['btn_cancel']:
        return await cmd_cancel(message, state)
    data = await state.get_data()
    await state.clear()
    await state.update_data(lang=lang)

    user_requirements = f"Land: {data['land_dims']}. Floors: {data['floors']}. Rooms: {data['rooms']}. Notes: {message.text}"
    prompt = f"{SCHEMA_PROMPT}\n\nUSER REQUIREMENTS:\n{user_requirements}"
    
    await message.answer(STRINGS[lang]['parsing'], reply_markup=get_main_keyboard(lang))
    
    max_retries = 2
    last_error = ""
    import logging
    logger = logging.getLogger(__name__)
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                retry_prompt = f"{prompt}\n\nERROR IN PREVIOUS ATTEMPT:\n{last_error}\nFIX THESE ERRORS AND RETURN VALID JSON."
                parsed = llm_client.parse_to_json(retry_prompt)
            else:
                parsed = llm_client.parse_to_json(prompt)
            
            # LOG THE RAW AI RESPONSE
            logger.info(f"AI Response (Attempt {attempt+1}):\n{json.dumps(parsed, indent=2)}")
                
            validated = validate_and_fill(parsed)
            break
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Validation failed (Attempt {attempt+1}): {last_error}")
            if attempt == max_retries:
                await message.answer(STRINGS[lang]['error_parse'].format(error=last_error))
                return
            continue

    # Generate files
    dxf_path = unique_name('dxf')
    png_path = unique_name('png')
    create_plan(validated, str(dxf_path))
    render_preview(validated, str(png_path))

    await message.answer(STRINGS[lang]['generating'])
    
    # Format report
    report = f"<b>{STRINGS[lang]['room_dims']}</b>\n"
    for r in validated['rooms']:
        name = r.get('name', r.get('type', 'room'))
        report += f"• {name}: {r['width']}m x {r['height']}m\n"
    
    await message.answer_document(FSInputFile(str(dxf_path)))
    await message.answer_photo(FSInputFile(str(png_path)), caption=report, parse_mode='HTML')


async def show_help(message: Message, state: FSMContext):
    lang = await get_lang(state)
    await message.answer(STRINGS[lang]['help'])

# ... (rest of the file simplified for replacement) ...

async def handle_message(message: Message, state: FSMContext):
    lang = await get_lang(state)
    
    # Check for keyboard buttons
    if message.text == STRINGS[lang]['btn_help']:
        return await show_help(message, state)
    if message.text == STRINGS[lang]['btn_settings']:
        return await settings_lang(message, state)
    if message.text == STRINGS[lang]['btn_create']:
        return await create_project(message, state)
    if message.text == STRINGS[lang]['btn_cancel']:
        return await cmd_cancel(message, state)
    if message.text == "🇺🇿 O'zbekcha":
        return await set_lang_uz(message, state)
    if message.text == "🇺🇸 English":
        return await set_lang_en(message, state)

    # Legacy handling or free text if not in state
    user_text = message.text or ''
    prompt = f"{SCHEMA_PROMPT}\nUser Request: {user_text}"
    await message.answer(STRINGS[lang]['parsing'])
    try:
        parsed = llm_client.parse_to_json(prompt)
        validated = validate_and_fill(parsed)
    except Exception as e:
        await message.answer(STRINGS[lang]['error_parse'].format(error=str(e)))
        return

    # Generate files
    dxf_path = unique_name('dxf')
    png_path = unique_name('png')
    create_plan(validated, str(dxf_path))
    render_preview(validated, str(png_path))

    await message.answer(STRINGS[lang]['generating'])
    await message.answer_document(FSInputFile(str(dxf_path)))
    await message.answer_photo(FSInputFile(str(png_path)))

