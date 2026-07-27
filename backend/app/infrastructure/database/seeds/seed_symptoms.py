"""Comprehensive Seed Script for 30+ Common Symptoms across all body systems.

Covers cardiovascular, respiratory, neurological, digestive, musculoskeletal,
dermatological, mental health, ENT, urological, endocrine, obstetric, and
pediatric categories.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.symptom_category import SymptomCategoryModel
from app.models.symptom import SymptomModel, SymptomSeverityHint
from app.models.symptom_translation import SymptomTranslationModel

logger = logging.getLogger(__name__)

SYMPTOMS_DATA = [
    # ─── CARDIOVASCULAR ──────────────────────────────────────────────────────
    {"category_slug": "cardiovascular", "slug": "chest-pain", "name_en": "Chest Pain",
     "description_en": "Pain, pressure, tightness, or squeezing in the center or left of the chest.",
     "severity_hint": SymptomSeverityHint.CRITICAL, "is_red_flag": False, "icd10_code": "R07.9",
     "translations": {"tw": {"name": "Kokoɔ mu yaw", "description": "Yaw a ɛwɔ wo bo mu."}}},

    {"category_slug": "cardiovascular", "slug": "palpitations", "name_en": "Palpitations",
     "description_en": "Sensation of rapid, strong, fluttering, or irregular heartbeats.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R00.2",
     "translations": {"tw": {"name": "Koma a ɛbɔ denneen", "description": "Koma bɔ den anaa ntɛm."}}},

    {"category_slug": "cardiovascular", "slug": "leg-swelling", "name_en": "Leg Swelling",
     "description_en": "Swelling of one or both legs, ankles, or feet due to fluid retention.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R60.0",
     "translations": {"tw": {"name": "Nan ho foforo", "description": "Nan anaa nan ase ho foforo."}}},

    {"category_slug": "cardiovascular", "slug": "fainting", "name_en": "Fainting / Syncope",
     "description_en": "Brief loss of consciousness due to inadequate blood flow to the brain.",
     "severity_hint": SymptomSeverityHint.HIGH, "is_red_flag": True, "icd10_code": "R55",
     "translations": {"tw": {"name": "Ahwere", "description": "Adwene tue kakra wɔ n'ase."}}},

    # ─── RESPIRATORY ─────────────────────────────────────────────────────────
    {"category_slug": "respiratory", "slug": "shortness-of-breath", "name_en": "Shortness of Breath",
     "description_en": "Difficulty breathing, feeling winded, or tight chest causing breathlessness.",
     "severity_hint": SymptomSeverityHint.HIGH, "is_red_flag": False, "icd10_code": "R06.0",
     "translations": {"tw": {"name": "Ahomete kakra", "description": "Ahomegyeɛ a ɛyɛ den."}}},

    {"category_slug": "respiratory", "slug": "cough", "name_en": "Cough",
     "description_en": "Sudden, noisy expulsion of air from the lungs, dry or producing phlegm.",
     "severity_hint": SymptomSeverityHint.LOW, "is_red_flag": False, "icd10_code": "R05",
     "translations": {"tw": {"name": "Wabo / Ɔfe", "description": "Ɔfe a ɛyɛ den."}}},

    {"category_slug": "respiratory", "slug": "coughing-blood", "name_en": "Coughing up Blood",
     "description_en": "Hemoptysis — blood or blood-streaked mucus coughed up from the lungs.",
     "severity_hint": SymptomSeverityHint.CRITICAL, "is_red_flag": True, "icd10_code": "R04.2",
     "translations": {"tw": {"name": "Ɔfe a mogya ba", "description": "Mogya ba sɛ wufe."}}},

    {"category_slug": "respiratory", "slug": "wheezing", "name_en": "Wheezing",
     "description_en": "High-pitched whistling sound when breathing, especially when exhaling.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R06.2",
     "translations": {"tw": {"name": "Ahomegyeɛ a ɛtwee", "description": "Ahomegyeɛ a ɛyɛ su."}}},

    # ─── NEUROLOGICAL ────────────────────────────────────────────────────────
    {"category_slug": "neurological", "slug": "headache", "name_en": "Headache",
     "description_en": "Pain or aching in the head or upper neck region.",
     "severity_hint": SymptomSeverityHint.LOW, "is_red_flag": False, "icd10_code": "R51",
     "translations": {"tw": {"name": "Ti pae", "description": "Yaw a ɛwɔ ti mu."}}},

    {"category_slug": "neurological", "slug": "dizziness", "name_en": "Dizziness / Vertigo",
     "description_en": "Sensation of spinning, unsteadiness, or lightheadedness.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R42",
     "translations": {"tw": {"name": "Ti ahuhuro", "description": "Sɛ wiim a wo ti ahuhuro."}}},

    {"category_slug": "neurological", "slug": "seizure", "name_en": "Seizure / Convulsion",
     "description_en": "Sudden uncontrolled electrical disturbance in the brain causing shaking or loss of consciousness.",
     "severity_hint": SymptomSeverityHint.CRITICAL, "is_red_flag": True, "icd10_code": "R56.9",
     "translations": {"tw": {"name": "Gyen / Tamfoɔ yareɛ", "description": "Tafoɔ yareɛ a ɛba ntɛm."}}},

    {"category_slug": "neurological", "slug": "numbness-tingling", "name_en": "Numbness or Tingling",
     "description_en": "Loss of sensation or pins-and-needles feeling in limbs or face.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R20.2",
     "translations": {"tw": {"name": "Ahurɔ anaa nkyerɛmu", "description": "Sɛ wo nsa anaa wo nan nnya bi."}}},

    {"category_slug": "neurological", "slug": "confusion", "name_en": "Confusion / Altered Mental Status",
     "description_en": "Sudden changes in awareness, orientation, or thinking ability.",
     "severity_hint": SymptomSeverityHint.CRITICAL, "is_red_flag": True, "icd10_code": "R41.3",
     "translations": {"tw": {"name": "Adwene mu nsɛm", "description": "Adwene mu tete a ɛba ntɛm."}}},

    # ─── DIGESTIVE ───────────────────────────────────────────────────────────
    {"category_slug": "digestive", "slug": "abdominal-pain", "name_en": "Abdominal Pain",
     "description_en": "Pain or discomfort felt anywhere in the stomach or belly region.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R10.9",
     "translations": {"tw": {"name": "Yam yaw", "description": "Yaw a ɛwɔ wo yam fa baabi."}}},

    {"category_slug": "digestive", "slug": "nausea-vomiting", "name_en": "Nausea and Vomiting",
     "description_en": "Feeling of sickness in the stomach with or without actual vomiting.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R11",
     "translations": {"tw": {"name": "Ahoyaa ne ɛfunu", "description": "Sɛ wo pɛ sɛ wu funu."}}},

    {"category_slug": "digestive", "slug": "diarrhea", "name_en": "Diarrhea",
     "description_en": "Loose, watery stools occurring more than three times in a day.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "A09",
     "translations": {"tw": {"name": "Ɛsoro-wo / Ntanta", "description": "Efunu a ɛhyɛ nsu a ɛba."}}},

    {"category_slug": "digestive", "slug": "blood-in-stool", "name_en": "Blood in Stool",
     "description_en": "Presence of blood in feces — bright red, dark, or black tarry stools.",
     "severity_hint": SymptomSeverityHint.HIGH, "is_red_flag": True, "icd10_code": "K92.1",
     "translations": {"tw": {"name": "Mogya wɔ efunu mu", "description": "Mogya a ɛwɔ efunu mu."}}},

    {"category_slug": "digestive", "slug": "jaundice", "name_en": "Jaundice",
     "description_en": "Yellowing of the skin and whites of the eyes due to high bilirubin.",
     "severity_hint": SymptomSeverityHint.HIGH, "is_red_flag": False, "icd10_code": "R17",
     "translations": {"tw": {"name": "Sunyani / Hian Yareɛ", "description": "Honam ne aniwa tenten."}}},

    # ─── GENERAL ─────────────────────────────────────────────────────────────
    {"category_slug": "general", "slug": "fever", "name_en": "Fever",
     "description_en": "Body temperature elevated above normal (typically 38°C / 100.4°F or higher).",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R50.9",
     "translations": {"tw": {"name": "Ahohyehyee / Abiyede", "description": "Nipadua ho hyeɛ."}}},

    {"category_slug": "general", "slug": "fatigue", "name_en": "Fatigue / Extreme Tiredness",
     "description_en": "Extreme tiredness, weariness, or lack of energy that does not improve with rest.",
     "severity_hint": SymptomSeverityHint.LOW, "is_red_flag": False, "icd10_code": "R53.83",
     "translations": {"tw": {"name": "Ɔbrɛ a ɛtra so", "description": "Ɔbrɛ ne ahoɔden a ɛsa."}}},

    {"category_slug": "general", "slug": "unintended-weight-loss", "name_en": "Unintended Weight Loss",
     "description_en": "Significant unintentional weight loss (more than 5% of body weight in 6 months).",
     "severity_hint": SymptomSeverityHint.HIGH, "is_red_flag": False, "icd10_code": "R63.4",
     "translations": {"tw": {"name": "Onyaa pisuu a wantie", "description": "Onyaa pisuu kwa."}}},

    {"category_slug": "general", "slug": "night-sweats", "name_en": "Night Sweats",
     "description_en": "Repeated episodes of excessive sweating during sleep.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R61",
     "translations": {"tw": {"name": "Ahurusi anadwo", "description": "Anadwo ahurusi."}}},

    # ─── MUSCULOSKELETAL ─────────────────────────────────────────────────────
    {"category_slug": "musculoskeletal", "slug": "back-pain", "name_en": "Back Pain",
     "description_en": "Pain, stiffness, or discomfort located in the upper, middle, or lower back.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "M54.9",
     "translations": {"tw": {"name": "Akyi yaw", "description": "Yaw a ɛwɔ akyi."}}},

    {"category_slug": "musculoskeletal", "slug": "joint-pain", "name_en": "Joint Pain",
     "description_en": "Pain, swelling, or stiffness in any joint — knee, hip, shoulder, wrist, or ankle.",
     "severity_hint": SymptomSeverityHint.LOW, "is_red_flag": False, "icd10_code": "M25.5",
     "translations": {"tw": {"name": "Ntoasoo yaw", "description": "Ntoasoo ho yaw."}}},

    {"category_slug": "musculoskeletal", "slug": "muscle-weakness", "name_en": "Muscle Weakness",
     "description_en": "Sudden or progressive loss of muscle strength, especially in limbs.",
     "severity_hint": SymptomSeverityHint.HIGH, "is_red_flag": False, "icd10_code": "M62.81",
     "translations": {"tw": {"name": "Honam ahoɔden a ɛyera", "description": "Honam ahoɔden sɛe."}}},

    # ─── MENTAL HEALTH ───────────────────────────────────────────────────────
    {"category_slug": "mental-health", "slug": "anxiety", "name_en": "Anxiety / Panic Attack",
     "description_en": "Intense worry, fear, or physical symptoms like racing heart and shortness of breath.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "F41.9",
     "translations": {"tw": {"name": "Ahohia / Hwehwɛ ahohia", "description": "Hu sɛ ahohia wɔ wo so."}}},

    {"category_slug": "mental-health", "slug": "depression", "name_en": "Depression / Low Mood",
     "description_en": "Persistent feelings of sadness, emptiness, hopelessness, or loss of interest in daily activities.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "F32.9",
     "translations": {"tw": {"name": "Awerɛhow", "description": "Awerɛhow a ɛtena so."}}},

    {"category_slug": "mental-health", "slug": "suicidal-thoughts", "name_en": "Suicidal Thoughts",
     "description_en": "Thoughts of harming or killing oneself.",
     "severity_hint": SymptomSeverityHint.CRITICAL, "is_red_flag": True, "icd10_code": "R45.851",
     "translations": {"tw": {"name": "Adwene fa wo ho", "description": "Adwene fa sɛ wo pɛ sɛ wu."}}},

    # ─── ENT ─────────────────────────────────────────────────────────────────
    {"category_slug": "ent", "slug": "sore-throat", "name_en": "Sore Throat",
     "description_en": "Pain, scratchiness, or irritation in the throat, often worsened by swallowing.",
     "severity_hint": SymptomSeverityHint.LOW, "is_red_flag": False, "icd10_code": "J02.9",
     "translations": {"tw": {"name": "Kɔn yaw", "description": "Kɔn mu yaw."}}},

    {"category_slug": "ent", "slug": "ear-pain", "name_en": "Ear Pain",
     "description_en": "Pain or discomfort inside or around the ear.",
     "severity_hint": SymptomSeverityHint.LOW, "is_red_flag": False, "icd10_code": "H92.0",
     "translations": {"tw": {"name": "Aso yaw", "description": "Aso mu yaw."}}},

    {"category_slug": "ent", "slug": "hearing-loss", "name_en": "Hearing Loss",
     "description_en": "Partial or complete inability to hear in one or both ears.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "H91.9",
     "translations": {"tw": {"name": "Aso a ɛnte", "description": "Aso nnte yie."}}},

    # ─── UROLOGICAL ──────────────────────────────────────────────────────────
    {"category_slug": "urinary", "slug": "painful-urination", "name_en": "Painful Urination",
     "description_en": "Burning, stinging, or discomfort when urinating.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R30.9",
     "translations": {"tw": {"name": "Nsa ko a ɛyaw", "description": "Nsa ko a ɛhyehye."}}},

    {"category_slug": "urinary", "slug": "blood-in-urine", "name_en": "Blood in Urine",
     "description_en": "Presence of blood in urine (hematuria), making it pink, red, or brown.",
     "severity_hint": SymptomSeverityHint.HIGH, "is_red_flag": False, "icd10_code": "R31",
     "translations": {"tw": {"name": "Mogya wɔ nsa mu", "description": "Mogya a ɛwɔ nsa mu."}}},

    # ─── DERMATOLOGICAL ──────────────────────────────────────────────────────
    {"category_slug": "skin", "slug": "rash", "name_en": "Skin Rash",
     "description_en": "Change in skin appearance — redness, itching, swelling, or blisters.",
     "severity_hint": SymptomSeverityHint.LOW, "is_red_flag": False, "icd10_code": "R21",
     "translations": {"tw": {"name": "Honam ho hare", "description": "Honam ho hare a ɛhome."}}},

    {"category_slug": "skin", "slug": "severe-allergic-reaction", "name_en": "Severe Allergic Reaction (Anaphylaxis)",
     "description_en": "Life-threatening allergic reaction with swelling, hives, breathing difficulty, and low blood pressure.",
     "severity_hint": SymptomSeverityHint.CRITICAL, "is_red_flag": True, "icd10_code": "T78.2",
     "translations": {"tw": {"name": "Honam yareɛ a ɛyɛ hu", "description": "Honam yareɛ a ɛyɛ hu pii."}}},

    # ─── ENDOCRINE ───────────────────────────────────────────────────────────
    {"category_slug": "general", "slug": "excessive-thirst", "name_en": "Excessive Thirst / Polydipsia",
     "description_en": "Abnormally increased thirst even after drinking adequate amounts of fluid.",
     "severity_hint": SymptomSeverityHint.MODERATE, "is_red_flag": False, "icd10_code": "R63.1",
     "translations": {"tw": {"name": "Osu pa ara", "description": "Osu a ɛtena so."}}},

    {"category_slug": "urinary", "slug": "frequent-urination", "name_en": "Frequent Urination",
     "description_en": "Needing to urinate more often than usual, including at night.",
     "severity_hint": SymptomSeverityHint.LOW, "is_red_flag": False, "icd10_code": "R35",
     "translations": {"tw": {"name": "Nsa ko pii", "description": "Nsa ko ntɛmntɛm."}}},

    # ─── INJURIES & EMERGENCIES ──────────────────────────────────────────────
    {"category_slug": "injuries-emergencies", "slug": "severe-bleeding", "name_en": "Severe Bleeding",
     "description_en": "Uncontrolled active bleeding that does not stop with direct pressure.",
     "severity_hint": SymptomSeverityHint.CRITICAL, "is_red_flag": True, "icd10_code": "R58",
     "translations": {"tw": {"name": "Mogya a ɛtu pii", "description": "Mogya a ɛresen."}}},

    {"category_slug": "injuries-emergencies", "slug": "stroke-symptoms", "name_en": "Stroke Symptoms (FAST)",
     "description_en": "Sudden face drooping, arm weakness, speech difficulty — possible stroke.",
     "severity_hint": SymptomSeverityHint.CRITICAL, "is_red_flag": True, "icd10_code": "I64",
     "translations": {"tw": {"name": "Ɔkra yareɛ (stroke)", "description": "Anim tɔ, nsa ahoɔden sɛe ntɛm."}}},

    {"category_slug": "injuries-emergencies", "slug": "burn-injury", "name_en": "Burn Injury",
     "description_en": "Tissue damage caused by heat, chemicals, electricity, or radiation.",
     "severity_hint": SymptomSeverityHint.HIGH, "is_red_flag": False, "icd10_code": "T30.0",
     "translations": {"tw": {"name": "Ogyanan / Honam hyeɛ", "description": "Ogyanan a ɛma honam yɛ hu."}}},

    # ─── OBSTETRIC / GYNECOLOGICAL ───────────────────────────────────────────
    {"category_slug": "womens-health", "slug": "vaginal-bleeding", "name_en": "Abnormal Vaginal Bleeding",
     "description_en": "Unexpected or heavy vaginal bleeding outside of normal menstrual period.",
     "severity_hint": SymptomSeverityHint.HIGH, "is_red_flag": False, "icd10_code": "N93.9",
     "translations": {"tw": {"name": "Mogya a ɛba ɛfante", "description": "Mogya a ɛba bere a ɛnsɛ."}}},

    # ─── PEDIATRIC ───────────────────────────────────────────────────────────
    {"category_slug": "child-health", "slug": "child-fever", "name_en": "Child Fever",
     "description_en": "Fever in a child under 12, especially critical in infants under 3 months.",
     "severity_hint": SymptomSeverityHint.HIGH, "is_red_flag": False, "icd10_code": "R50.9",
     "translations": {"tw": {"name": "Abofra abiyede", "description": "Abofra a ne ho hyeɛ."}}},
]


async def seed_symptoms(session: AsyncSession) -> None:
    logger.info("Seeding comprehensive symptoms database...")
    count = 0
    for sym_data in SYMPTOMS_DATA:
        cat_res = await session.execute(
            select(SymptomCategoryModel).where(SymptomCategoryModel.slug == sym_data["category_slug"])
        )
        cat = cat_res.scalar_one_or_none()
        if not cat:
            logger.warning(f"Category '{sym_data['category_slug']}' not found, skipping '{sym_data['slug']}'")
            continue

        res = await session.execute(
            select(SymptomModel).where(SymptomModel.slug == sym_data["slug"])
        )
        sym = res.scalar_one_or_none()
        if not sym:
            sym = SymptomModel(
                category_id=cat.id,
                slug=sym_data["slug"],
                name_en=sym_data["name_en"],
                description_en=sym_data["description_en"],
                severity_hint=sym_data["severity_hint"],
                is_red_flag=sym_data["is_red_flag"],
                icd10_code=sym_data["icd10_code"],
                is_active=True
            )
            session.add(sym)
            await session.flush()
            count += 1

        for lang_code, tr_data in sym_data.get("translations", {}).items():
            tr_res = await session.execute(
                select(SymptomTranslationModel).where(
                    SymptomTranslationModel.symptom_id == sym.id,
                    SymptomTranslationModel.language_code == lang_code
                )
            )
            if not tr_res.scalar_one_or_none():
                tr = SymptomTranslationModel(
                    symptom_id=sym.id,
                    language_code=lang_code,
                    name=tr_data["name"],
                    description=tr_data["description"]
                )
                session.add(tr)

    await session.flush()
    logger.info(f"Symptoms seeded: {count} new records added.")
