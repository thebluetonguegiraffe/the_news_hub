"""Canonical news categories.

The stable axis of the classification. A document is assigned exactly one of
these by comparing its embedding against the category prototypes below, so the
same story lands in the same category every day and `topics_per_day` becomes a
series that can actually be compared over time.

The prototype text is what gets embedded, not the label, so it is written as a
dense bag of the vocabulary that category's articles use. Editing a prototype
changes future assignments; the embeddings are cached per process only.
"""

NEWS_CATEGORIES = {
    "politics": (
        "government, parliament, elections, political parties, ministers, prime minister, "
        "president, coalition, vote, electoral campaign, televised leaders debate, candidate, "
        "opinion poll, legislation, policy, public administration, diplomacy, referendum, "
        "opposition, congress, senate, cabinet reshuffle, international summit, state visit, "
        "bilateral meeting between leaders, welfare and benefits reform, party leadership"
    ),
    "economy": (
        "inflation, interest rates, central bank, gross domestic product, taxes, budget, "
        "wages, cost of living, unemployment, pensions, public spending, deficit, "
        "economic growth, recession, consumer prices, energy bills, purchasing power"
    ),
    "business": (
        "company quarterly results, earnings and profits, mergers and acquisitions, takeover "
        "bid, stock market shares, initial public offering, investors and shareholders, board "
        "of directors, chief executive appointment, startup funding round, bankruptcy and "
        "administration, layoffs and job cuts at a company, corporate strategy, profit warning"
    ),
    "technology": (
        "artificial intelligence, software, semiconductors and chips, smartphones, internet "
        "platforms, social networks, data centres, cybersecurity, hacking, privacy and data "
        "protection, cloud computing, apps, robotics, telecommunications, digital services"
    ),
    "science": (
        "scientific research, study published, space and astronomy, physics, chemistry, "
        "biology, archaeology, palaeontology, genetics, mathematics, laboratory experiment, "
        "discovery, satellites, telescope, scientific journal"
    ),
    "health": (
        "hospitals, doctors and nurses, patients, disease and illness, virus and epidemic, "
        "vaccines, medicines and drugs, public health system, mental health, surgery, "
        "cancer, nutrition and diet, healthcare waiting lists, medical treatment"
    ),
    "environment": (
        "climate change, global warming, emissions, drought, flooding, wildfire, heatwave, "
        "biodiversity and wildlife, pollution, recycling and waste, water supply, renewable "
        "energy, solar and wind power, conservation, natural disaster, earthquake"
    ),
    "justice": (
        "court ruling, trial, judge, prosecutor, sentence and prison, police investigation, "
        "arrest, crime, murder, fraud and corruption, lawsuit, appeal, supreme court, "
        "constitutional court, criminal charges, verdict"
    ),
    "conflict": (
        "war, military offensive, ceasefire, troops and soldiers, missile and drone strikes, "
        "bombing, invasion, armed forces, peace talks, sanctions, genocide, refugees fleeing, "
        "humanitarian crisis in a war zone, insurgency, terrorism"
    ),
    "society": (
        "protests and demonstrations, strikes, inequality and poverty, immigration and "
        "migrants, racism and discrimination, religion, gender and feminism, lgbt rights, "
        "family life, ageing population, social services, charity, volunteering, generations, "
        "disability rights, people with disabilities, survey of public opinion on daily life"
    ),
    "sports": (
        "football match result, league table and championship, goals scored, coach and manager, "
        "player transfer, basketball game, tennis tournament, formula one grand prix, cycling "
        "race, athletics meeting, olympic games, world cup qualifier, injury of a player, team "
        "squad and line-up, title race, referee decision, fixture and kick-off"
    ),
    "culture": (
        "cinema and film, television series, music and concerts, album release, books and "
        "literature, novel, theatre, museum and exhibition, art, painting, music festival, "
        "film and arts awards ceremony, celebrity, fashion, gastronomy and restaurants, heritage"
    ),
    "education": (
        "schools, pupils and students, teachers, university, curriculum, exams and grades, "
        "tuition fees, vocational training, scholarships, academic research funding, "
        "classroom, education ministry, school places"
    ),
    "housing": (
        "housing market, rent prices, mortgages, property and real estate, tenants, "
        "landlords, evictions, social housing, construction of homes, urban development, "
        "planning permission, squatting, housing shortage"
    ),
    "transport": (
        "trains and railways, metro and underground, buses, airlines and flights, airport, "
        "roads and motorways, traffic, cars and electric vehicles, cycling lanes, ports and "
        "shipping, commuters, delays and cancellations, infrastructure works"
    ),
    "media": (
        "newspapers, journalism, broadcaster, television channel, radio, press freedom, "
        "misinformation and fake news, advertising, streaming platform, audience ratings, "
        "editorial, communication group, influencers"
    ),
}

# Used when no category is a confident match for a document.
UNCLASSIFIED_CATEGORY = "general"

CATEGORY_LABELS = tuple(NEWS_CATEGORIES.keys())

# Display names per language. The taxonomy is a fixed, known list, so the names
# are stated rather than machine-translated: asking the translation endpoint for
# a bare word is unreliable (it returned "politica" without the accent, and
# "negocio" for the business desk) and there is nothing to gain from guessing at
# a label that only has to be written once.
CATEGORY_NAMES = {
    "politics": {"es": "política", "ca": "política"},
    "economy": {"es": "economía", "ca": "economia"},
    "business": {"es": "empresas", "ca": "empreses"},
    "technology": {"es": "tecnología", "ca": "tecnologia"},
    "science": {"es": "ciencia", "ca": "ciència"},
    "health": {"es": "salud", "ca": "salut"},
    "environment": {"es": "medio ambiente", "ca": "medi ambient"},
    "justice": {"es": "justicia", "ca": "justícia"},
    "conflict": {"es": "conflictos", "ca": "conflictes"},
    "society": {"es": "sociedad", "ca": "societat"},
    "sports": {"es": "deportes", "ca": "esports"},
    "culture": {"es": "cultura", "ca": "cultura"},
    "education": {"es": "educación", "ca": "educació"},
    "housing": {"es": "vivienda", "ca": "habitatge"},
    "transport": {"es": "transporte", "ca": "transport"},
    "media": {"es": "medios de comunicación", "ca": "mitjans de comunicació"},
    UNCLASSIFIED_CATEGORY: {"es": "general", "ca": "general"},
}

assert set(CATEGORY_NAMES) == set(CATEGORY_LABELS) | {UNCLASSIFIED_CATEGORY}, (
    "every category needs a display name in both languages"
)
