"""Seed Script for Symptom Question Options."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.question import QuestionModel
from app.models.question_option import QuestionOptionModel

logger = logging.getLogger(__name__)

OPTIONS_DATA = [
    # Headache Onset
    {"node_id": "ha_onset", "option_value": "sudden", "label_en": "Suddenly (Thunderclap)", "label_tw": "Ntɛm ara (Te sɛ apra)", "order_index": 1, "is_red_flag": True},
    {"node_id": "ha_onset", "option_value": "gradual", "label_en": "Gradually over hours/days", "label_tw": "Nkakrankakra akyɛ", "order_index": 2, "is_red_flag": False},

    # Headache Severity
    {"node_id": "ha_severity", "option_value": "mild", "label_en": "Mild (1-3)", "label_tw": "Ketewa (1-3)", "order_index": 1, "is_red_flag": False},
    {"node_id": "ha_severity", "option_value": "moderate", "label_en": "Moderate (4-7)", "label_tw": "Ɔyɛ (4-7)", "order_index": 2, "is_red_flag": False},
    {"node_id": "ha_severity", "option_value": "severe", "label_en": "Severe (8-10)", "label_tw": "Dendeenden (8-10)", "order_index": 3, "is_red_flag": True},

    # Headache Associated
    {"node_id": "ha_associated", "option_value": "vision_changes", "label_en": "Vision changes or loss", "label_tw": "Aniwa mu nsakrae", "order_index": 1, "is_red_flag": True},
    {"node_id": "ha_associated", "option_value": "stiff_neck", "label_en": "Stiff neck", "label_tw": "Kɔn a ayɛ den", "order_index": 2, "is_red_flag": True},
    {"node_id": "ha_associated", "option_value": "fever", "label_en": "Fever", "label_tw": "Abiyede", "order_index": 3, "is_red_flag": False},
    {"node_id": "ha_associated", "option_value": "none", "label_en": "None of the above", "label_tw": "Emu biara nni hɔ", "order_index": 4, "is_red_flag": False},

    # Fever Duration
    {"node_id": "fv_duration", "option_value": "less_than_3", "label_en": "Less than 3 days", "label_tw": "Nnafua a ennu mmiɛnsa", "order_index": 1, "is_red_flag": False},
    {"node_id": "fv_duration", "option_value": "3_to_7", "label_en": "3 to 7 days", "label_tw": "Nnafua mmiɛnsa kosi nson", "order_index": 2, "is_red_flag": False},
    {"node_id": "fv_duration", "option_value": "more_than_7", "label_en": "More than 7 days", "label_tw": "Kyɛn nnafua nson", "order_index": 3, "is_red_flag": True},

    # Fever Temp
    {"node_id": "fv_temp", "option_value": "low", "label_en": "Under 39°C (102.2°F)", "label_tw": "Nnu 39°C", "order_index": 1, "is_red_flag": False},
    {"node_id": "fv_temp", "option_value": "high", "label_en": "39°C (102.2°F) or higher", "label_tw": "39°C anaa nea ɛkyɛn sa", "order_index": 2, "is_red_flag": True},
    {"node_id": "fv_temp", "option_value": "unknown", "label_en": "I haven't measured it", "label_tw": "Mensusuwii", "order_index": 3, "is_red_flag": False},

    # Fever Other
    {"node_id": "fv_other", "option_value": "rash", "label_en": "New skin rash", "label_tw": "Honam ho hare foforo", "order_index": 1, "is_red_flag": True},
    {"node_id": "fv_other", "option_value": "confusion", "label_en": "Confusion or extreme sleepiness", "label_tw": "Adwene mu nsɛm anaa nna pii", "order_index": 2, "is_red_flag": True},
    {"node_id": "fv_other", "option_value": "none", "label_en": "None of the above", "label_tw": "Emu biara nni hɔ", "order_index": 3, "is_red_flag": False},

    # Cough Type
    {"node_id": "co_type", "option_value": "dry", "label_en": "Dry cough", "label_tw": "Ɔfe a nsu nnim", "order_index": 1, "is_red_flag": False},
    {"node_id": "co_type", "option_value": "productive", "label_en": "Coughing up phlegm", "label_tw": "Ɔfe a hwenho wom", "order_index": 2, "is_red_flag": False},

    # Cough Duration
    {"node_id": "co_duration", "option_value": "less_than_3_weeks", "label_en": "Less than 3 weeks", "label_tw": "Nnawɔtwe mmiɛnsa nnu", "order_index": 1, "is_red_flag": False},
    {"node_id": "co_duration", "option_value": "3_to_8_weeks", "label_en": "3 to 8 weeks", "label_tw": "Nnawɔtwe mmiɛnsa kosi awotwe", "order_index": 2, "is_red_flag": False},
    {"node_id": "co_duration", "option_value": "more_than_8_weeks", "label_en": "More than 8 weeks", "label_tw": "Kyɛn nnawɔtwe awotwe", "order_index": 3, "is_red_flag": True},

    # Cough Blood
    {"node_id": "co_blood", "option_value": "yes", "label_en": "Yes", "label_tw": "Aane", "order_index": 1, "is_red_flag": True},
    {"node_id": "co_blood", "option_value": "no", "label_en": "No", "label_tw": "Daabi", "order_index": 2, "is_red_flag": False},

    # Chest Pain Type
    {"node_id": "cp_type", "option_value": "crushing", "label_en": "Crushing, pressure, or tightness", "label_tw": "Sɛnea wɔrehi wo", "order_index": 1, "is_red_flag": True},
    {"node_id": "cp_type", "option_value": "sharp", "label_en": "Sharp or stabbing", "label_tw": "Yaw a ɛwɔ mu", "order_index": 2, "is_red_flag": False},
    {"node_id": "cp_type", "option_value": "burning", "label_en": "Burning (like heartburn)", "label_tw": "Yaw a ɛhyehye", "order_index": 3, "is_red_flag": False},

    # Chest Pain Radiate
    {"node_id": "cp_radiate", "option_value": "yes", "label_en": "Yes", "label_tw": "Aane", "order_index": 1, "is_red_flag": True},
    {"node_id": "cp_radiate", "option_value": "no", "label_en": "No", "label_tw": "Daabi", "order_index": 2, "is_red_flag": False},

    # Chest Pain Breathing
    {"node_id": "cp_breathing", "option_value": "yes", "label_en": "Yes", "label_tw": "Aane", "order_index": 1, "is_red_flag": False},
    {"node_id": "cp_breathing", "option_value": "no", "label_en": "No", "label_tw": "Daabi", "order_index": 2, "is_red_flag": False},

    # Shortness of Breath Onset
    {"node_id": "sob_onset", "option_value": "sudden", "label_en": "Suddenly", "label_tw": "Ntɛm ara", "order_index": 1, "is_red_flag": True},
    {"node_id": "sob_onset", "option_value": "gradual", "label_en": "Gradually over days/weeks", "label_tw": "Nkakrankakra", "order_index": 2, "is_red_flag": False},

    # Shortness of Breath Rest
    {"node_id": "sob_rest", "option_value": "yes", "label_en": "Yes", "label_tw": "Aane", "order_index": 1, "is_red_flag": True},
    {"node_id": "sob_rest", "option_value": "no", "label_en": "No (only with activity)", "label_tw": "Daabi (sɛ meyɛ adwuma a)", "order_index": 2, "is_red_flag": False},

    # Shortness of Breath Wheeze
    {"node_id": "sob_wheeze", "option_value": "yes", "label_en": "Yes", "label_tw": "Aane", "order_index": 1, "is_red_flag": False},
    {"node_id": "sob_wheeze", "option_value": "no", "label_en": "No", "label_tw": "Daabi", "order_index": 2, "is_red_flag": False},

    # Fatigue Duration
    {"node_id": "fa_duration", "option_value": "recent", "label_en": "A few days or weeks", "label_tw": "Nnafua anaa nnawɔtwe kakra", "order_index": 1, "is_red_flag": False},
    {"node_id": "fa_duration", "option_value": "chronic", "label_en": "Several months", "label_tw": "Abosome pii", "order_index": 2, "is_red_flag": False},

    # Fatigue Impact
    {"node_id": "fa_impact", "option_value": "yes", "label_en": "Yes", "label_tw": "Aane", "order_index": 1, "is_red_flag": False},
    {"node_id": "fa_impact", "option_value": "no", "label_en": "No", "label_tw": "Daabi", "order_index": 2, "is_red_flag": False},

    # Fatigue Other
    {"node_id": "fa_other", "option_value": "yes", "label_en": "Yes", "label_tw": "Aane", "order_index": 1, "is_red_flag": True},
    {"node_id": "fa_other", "option_value": "no", "label_en": "No", "label_tw": "Daabi", "order_index": 2, "is_red_flag": False},

    # Abdominal Pain Location
    {"node_id": "ap_location", "option_value": "right_lower", "label_en": "Lower right side", "label_tw": "Nifa fam ase", "order_index": 1, "is_red_flag": True},
    {"node_id": "ap_location", "option_value": "upper", "label_en": "Upper stomach", "label_tw": "Yam atifi", "order_index": 2, "is_red_flag": False},
    {"node_id": "ap_location", "option_value": "all_over", "label_en": "All over the stomach", "label_tw": "Yam nyinaa", "order_index": 3, "is_red_flag": False},

    # Abdominal Pain Severity
    {"node_id": "ap_severity", "option_value": "severe", "label_en": "Severe, I can't stand up straight", "label_tw": "Dendeenden, mintumi ngyina tee", "order_index": 1, "is_red_flag": True},
    {"node_id": "ap_severity", "option_value": "moderate", "label_en": "Moderate, manageable but painful", "label_tw": "Ɔyɛ, ɛyaw nanso metumi agyina", "order_index": 2, "is_red_flag": False},
    {"node_id": "ap_severity", "option_value": "mild", "label_en": "Mild, mostly dull ache", "label_tw": "Ketewa", "order_index": 3, "is_red_flag": False},

    # Abdominal Pain Vomiting
    {"node_id": "ap_vomiting", "option_value": "blood", "label_en": "Yes, there is blood or it looks like coffee grounds", "label_tw": "Aane, mogya wom anaa ɛte sɛ kɔfe", "order_index": 1, "is_red_flag": True},
    {"node_id": "ap_vomiting", "option_value": "yes_no_blood", "label_en": "Yes, but no blood", "label_tw": "Aane, nanso mogya nnim", "order_index": 2, "is_red_flag": False},
    {"node_id": "ap_vomiting", "option_value": "no", "label_en": "No vomiting", "label_tw": "Menfe", "order_index": 3, "is_red_flag": False},

    # Severe Bleeding Location
    {"node_id": "sb_location", "option_value": "limb", "label_en": "Arm or leg", "label_tw": "Nsa anaa nan", "order_index": 1, "is_red_flag": True},
    {"node_id": "sb_location", "option_value": "torso", "label_en": "Chest, stomach, or back", "label_tw": "Kokoɔ, yam, anaa akyi", "order_index": 2, "is_red_flag": True},
    {"node_id": "sb_location", "option_value": "head", "label_en": "Head or neck", "label_tw": "Ti anaa kɔn", "order_index": 3, "is_red_flag": True},

    # Severe Bleeding Control
    {"node_id": "sb_control", "option_value": "yes", "label_en": "Yes, it stops or slows", "label_tw": "Aane, egyae anaa ɛtew so", "order_index": 1, "is_red_flag": False},
    {"node_id": "sb_control", "option_value": "no", "label_en": "No, it keeps bleeding heavily", "label_tw": "Daabi, ɛtu pii ara", "order_index": 2, "is_red_flag": True},

    # Palpitations Duration
    {"node_id": "pa_duration", "option_value": "minutes", "label_en": "A few minutes", "label_tw": "Simma kakra", "order_index": 1, "is_red_flag": False},
    {"node_id": "pa_duration", "option_value": "hours", "label_en": "Hours at a time", "label_tw": "Dɔnhwerew pii", "order_index": 2, "is_red_flag": False},
    {"node_id": "pa_duration", "option_value": "constant", "label_en": "Constant / won't stop", "label_tw": "Ɛnkɔ da", "order_index": 3, "is_red_flag": True},

    # Palpitations Associated
    {"node_id": "pa_associated", "option_value": "yes", "label_en": "Yes", "label_tw": "Aane", "order_index": 1, "is_red_flag": True},
    {"node_id": "pa_associated", "option_value": "no", "label_en": "No", "label_tw": "Daabi", "order_index": 2, "is_red_flag": False},
]

async def seed_question_options(session: AsyncSession) -> None:
    logger.info("Seeding question options...")
    count = 0
    for opt_data in OPTIONS_DATA:
        q_res = await session.execute(
            select(QuestionModel).where(QuestionModel.node_id == opt_data["node_id"])
        )
        question = q_res.scalar_one_or_none()
        if not question:
            continue

        res = await session.execute(
            select(QuestionOptionModel).where(
                QuestionOptionModel.question_id == question.id,
                QuestionOptionModel.option_value == opt_data["option_value"]
            )
        )
        if not res.scalar_one_or_none():
            opt = QuestionOptionModel(
                question_id=question.id,
                option_value=opt_data["option_value"],
                label_en=opt_data["label_en"],
                label_tw=opt_data["label_tw"],
                order_index=opt_data["order_index"],
                is_red_flag=opt_data["is_red_flag"]
            )
            session.add(opt)
            count += 1
    await session.flush()
    logger.info(f"Question options seeded: {count} new records added.")
