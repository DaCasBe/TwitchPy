from dataclasses import dataclass


@dataclass
class AutoModSettings:
    """
    Represents the AutoMod settings

    Attributes:
        broadcaster_id (str): The broadcaster’s ID
        moderator_id (str): The moderator’s ID
        overall_level (int): The default AutoMod level for the broadcaster
        disability (int): The Automod level for discrimination against disability
        aggression (int): The Automod level for hostility involving aggression
        sexuality_sex_or_gender (int): The AutoMod level for discrimination based on sexuality, sex, or gender
        misogyny (int): The Automod level for discrimination against women
        bullying (int): The Automod level for hostility involving name calling or insults
        swearing (int): The Automod level for profanity
        race_ethnicity_or_religion (int): The Automod level for racial discrimination
        sex_based_terms (int): The Automod level for sexual content
    """

    broadcaster_id: str
    moderator_id: str
    overall_level: int
    disability: int
    aggression: int
    sexuality_sex_or_gender: int
    misogyny: int
    bullying: int
    swearing: int
    race_ethnicity_or_religion: int
    sex_based_terms: int
