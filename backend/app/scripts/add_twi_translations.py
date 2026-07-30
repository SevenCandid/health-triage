import asyncio
import os
import sys

# Set up path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.infrastructure.database.session import async_session_factory
from app.models.recommendation import RecommendationModel
from app.models.recommendation_translation import RecommendationTranslationModel
from app.models.language import LanguageModel

translations_map = {
    "Call emergency services (112 or local equivalent) immediately. Do not drive yourself to the hospital.": "Frɛ ateetee nhyehyɛeɛ (112 anaa nea ɛbɛn wo) ntɛm ara. Nka kado nkɔ asopiti.",
    "Sit down, rest, and try to remain calm. Chew a standard aspirin tablet if you are not allergic.": "Tena ase, gye w'ahome, na bɔ mmɔden sɛ w'ani bɛda hɔ. We aspirin aduro sɛ wunya ho nyarewa a.",
    "Seek immediate emergency care. Sit upright and loosen tight clothing.": "Kɔ pɛ ateetee ayaresa ntɛm ara. Tena ase teẽẽ na pagya wo ntamadeɛ.",
    "Rest, drink plenty of fluids, and monitor your temperature.": "Gye w'ahome, nom nsuo bebree, na hwɛ wo nipadua mu hyeɛ."
}

async def add_translations():
    async with async_session_factory() as session:
        # ensure 'tw' language exists
        tw_lang = (await session.execute(select(LanguageModel).where(LanguageModel.code == 'tw'))).scalar_one_or_none()
        if not tw_lang:
            tw_lang = LanguageModel(code='tw', name='Twi', is_active=True)
            session.add(tw_lang)
            await session.commit()
            print("Added Twi language")

        recs = (await session.execute(select(RecommendationModel))).scalars().all()
        for rec in recs:
            tw_trans = translations_map.get(rec.content_en)
            if tw_trans:
                # check if exists
                existing = (await session.execute(
                    select(RecommendationTranslationModel)
                    .where(
                        RecommendationTranslationModel.recommendation_id == rec.id,
                        RecommendationTranslationModel.language_code == 'tw'
                    )
                )).scalar_one_or_none()
                
                if not existing:
                    trans = RecommendationTranslationModel(
                        recommendation_id=rec.id,
                        language_code='tw',
                        content=tw_trans,
                        voice_content=tw_trans
                    )
                    session.add(trans)
        
        await session.commit()
        print("Done adding translations")

if __name__ == "__main__":
    asyncio.run(add_translations())
