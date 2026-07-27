"""Seed Script for Symptom Follow-Up Questions."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.symptom import SymptomModel
from app.models.question import QuestionModel, QuestionType

logger = logging.getLogger(__name__)

# Defining a comprehensive set of questions for core symptoms
QUESTIONS_DATA = [
    # Headache
    {"symptom_slug": "headache", "node_id": "ha_onset", "question_text_en": "How quickly did the headache start?", "question_text_tw": "Ti pae no hyɛɛ aseɛ ntɛm ara?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": True, "order_index": 1},
    {"symptom_slug": "headache", "node_id": "ha_severity", "question_text_en": "How severe is the headache on a scale of 1-10?", "question_text_tw": "Sɛn na ti pae no mu yɛ den?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": False, "order_index": 2},
    {"symptom_slug": "headache", "node_id": "ha_associated", "question_text_en": "Are you experiencing any of these other symptoms?", "question_text_tw": "Wo hu sɛnkyerɛnne afoforo bi ka ho?", "question_type": QuestionType.MULTI_SELECT, "is_red_flag_trigger": True, "order_index": 3},
    
    # Fever
    {"symptom_slug": "fever", "node_id": "fv_duration", "question_text_en": "How many days have you had the fever?", "question_text_tw": "Abiyede no abɔ wo nnafua ahe?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": False, "order_index": 1},
    {"symptom_slug": "fever", "node_id": "fv_temp", "question_text_en": "What is your highest measured temperature?", "question_text_tw": "Wo nipadua ho hyeɛ a ɛsen biara yɛ sɛn?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": True, "order_index": 2},
    {"symptom_slug": "fever", "node_id": "fv_other", "question_text_en": "Do you have any of these additional symptoms?", "question_text_tw": "Wo hu sɛnkyerɛnne afoforo bi ka ho?", "question_type": QuestionType.MULTI_SELECT, "is_red_flag_trigger": False, "order_index": 3},

    # Cough
    {"symptom_slug": "cough", "node_id": "co_type", "question_text_en": "Is the cough dry or are you coughing up phlegm/mucus?", "question_text_tw": "Ɔfe no yɛ dry anaa wotu ntasu/hwenho?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": False, "order_index": 1},
    {"symptom_slug": "cough", "node_id": "co_duration", "question_text_en": "How long have you had this cough?", "question_text_tw": "Ɔfe no akyɛ sɛn?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": False, "order_index": 2},
    {"symptom_slug": "cough", "node_id": "co_blood", "question_text_en": "Are you coughing up any blood?", "question_text_tw": "Ɔfe no mu mogya ba?", "question_type": QuestionType.BOOLEAN, "is_red_flag_trigger": True, "order_index": 3},

    # Chest Pain
    {"symptom_slug": "chest-pain", "node_id": "cp_type", "question_text_en": "How does the chest pain feel?", "question_text_tw": "Kokoɔ mu yaw no te sɛn?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": True, "order_index": 1},
    {"symptom_slug": "chest-pain", "node_id": "cp_radiate", "question_text_en": "Does the pain spread to your arm, back, neck, or jaw?", "question_text_tw": "Yaw no trɛw kɔ wo nsa, akyi, kɔn, anaa abogye mu?", "question_type": QuestionType.BOOLEAN, "is_red_flag_trigger": True, "order_index": 2},
    {"symptom_slug": "chest-pain", "node_id": "cp_breathing", "question_text_en": "Does the pain get worse when you take a deep breath?", "question_text_tw": "Sɛ wogye ahome a, yaw no mu yɛ den?", "question_type": QuestionType.BOOLEAN, "is_red_flag_trigger": False, "order_index": 3},

    # Shortness of breath
    {"symptom_slug": "shortness-of-breath", "node_id": "sob_onset", "question_text_en": "Did the shortness of breath start suddenly or gradually?", "question_text_tw": "Ahomete no hyɛɛ aseɛ ntɛm ara anaa nkakrankakra?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": True, "order_index": 1},
    {"symptom_slug": "shortness-of-breath", "node_id": "sob_rest", "question_text_en": "Are you short of breath even when resting?", "question_text_tw": "Sɛ wote hɔ a, wo home te?", "question_type": QuestionType.BOOLEAN, "is_red_flag_trigger": True, "order_index": 2},
    {"symptom_slug": "shortness-of-breath", "node_id": "sob_wheeze", "question_text_en": "Do you hear a wheezing or whistling sound when you breathe?", "question_text_tw": "Sɛ wogye ahome a, ɛyɛ su?", "question_type": QuestionType.BOOLEAN, "is_red_flag_trigger": False, "order_index": 3},

    # Fatigue
    {"symptom_slug": "fatigue", "node_id": "fa_duration", "question_text_en": "How long have you felt extremely tired?", "question_text_tw": "Ɔbrɛ no akyɛ sɛn?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": False, "order_index": 1},
    {"symptom_slug": "fatigue", "node_id": "fa_impact", "question_text_en": "Is the fatigue preventing you from doing your normal daily activities?", "question_text_tw": "Ɔbrɛ no mma wo ntumi nyɛ wo dwumadi ahorow?", "question_type": QuestionType.BOOLEAN, "is_red_flag_trigger": False, "order_index": 2},
    {"symptom_slug": "fatigue", "node_id": "fa_other", "question_text_en": "Do you also have unexplained weight loss or night sweats?", "question_text_tw": "Wo hu sɛ wo mu atew anaa wonya ahurusi anadwo?", "question_type": QuestionType.BOOLEAN, "is_red_flag_trigger": True, "order_index": 3},

    # Abdominal pain
    {"symptom_slug": "abdominal-pain", "node_id": "ap_location", "question_text_en": "Where is the pain located?", "question_text_tw": "Yaw no wɔ he?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": True, "order_index": 1},
    {"symptom_slug": "abdominal-pain", "node_id": "ap_severity", "question_text_en": "How severe is the pain?", "question_text_tw": "Yaw no mu yɛ den sɛn?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": True, "order_index": 2},
    {"symptom_slug": "abdominal-pain", "node_id": "ap_vomiting", "question_text_en": "Are you vomiting, and if so, is there blood or does it look like coffee grounds?", "question_text_tw": "Worefe, na mogya anaa biribi a ɛte sɛ kɔfe wɔ mu?", "question_type": QuestionType.BOOLEAN, "is_red_flag_trigger": True, "order_index": 3},

    # Severe bleeding
    {"symptom_slug": "severe-bleeding", "node_id": "sb_location", "question_text_en": "Where is the bleeding coming from?", "question_text_tw": "Mogya no fi he?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": True, "order_index": 1},
    {"symptom_slug": "severe-bleeding", "node_id": "sb_control", "question_text_en": "Does the bleeding stop or slow down when you apply direct pressure?", "question_text_tw": "Sɛ wumia so a, mogya no gyae anaa ɛtew so?", "question_type": QuestionType.BOOLEAN, "is_red_flag_trigger": True, "order_index": 2},

    # Palpitations
    {"symptom_slug": "palpitations", "node_id": "pa_duration", "question_text_en": "How long do the palpitations usually last?", "question_text_tw": "Koma bɔ den no kyɛ sɛn?", "question_type": QuestionType.SINGLE_SELECT, "is_red_flag_trigger": False, "order_index": 1},
    {"symptom_slug": "palpitations", "node_id": "pa_associated", "question_text_en": "Are you also experiencing chest pain, dizziness, or shortness of breath?", "question_text_tw": "Kokoɔ mu yaw, ti ahuhuro, anaa ahomete ka ho?", "question_type": QuestionType.BOOLEAN, "is_red_flag_trigger": True, "order_index": 2},
]


async def seed_questions(session: AsyncSession) -> None:
    logger.info("Seeding follow-up questions...")
    count = 0
    for q_data in QUESTIONS_DATA:
        sym_res = await session.execute(
            select(SymptomModel).where(SymptomModel.slug == q_data["symptom_slug"])
        )
        sym = sym_res.scalar_one_or_none()
        if not sym:
            logger.warning(f"Symptom '{q_data['symptom_slug']}' not found, skipping question '{q_data['node_id']}'")
            continue

        res = await session.execute(
            select(QuestionModel).where(
                QuestionModel.symptom_id == sym.id,
                QuestionModel.node_id == q_data["node_id"]
            )
        )
        if not res.scalar_one_or_none():
            q = QuestionModel(
                symptom_id=sym.id,
                node_id=q_data["node_id"],
                question_text_en=q_data["question_text_en"],
                question_text_tw=q_data["question_text_tw"],
                question_type=q_data["question_type"],
                is_red_flag_trigger=q_data["is_red_flag_trigger"],
                order_index=q_data["order_index"]
            )
            session.add(q)
            count += 1
    await session.flush()
    logger.info(f"Follow-up questions seeded: {count} new records added.")
