from .._utils import http
from ..dataclasses import (
    Channel,
    CharityCampaign,
    CharityCampaignAmount,
    CharityCampaignDonation,
    User,
)


def get_charity_campaign(
    token: str, client_id: str, broadcaster_id: str
) -> CharityCampaign:
    url = "https://api.twitch.tv/helix/charity/campaigns"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    charity_campaign = http.send_get(url, headers, params)[0]

    return CharityCampaign(
        charity_campaign["id"],
        Channel(
            User(
                charity_campaign["broadcaster_id"],
                charity_campaign["broadcaster_login"],
                charity_campaign["broadcaster_name"],
            )
        ),
        charity_campaign["charity_name"],
        charity_campaign["charity_description"],
        charity_campaign["charity_logo"],
        charity_campaign["charity_website"],
        CharityCampaignAmount(
            charity_campaign["current_amount"]["value"],
            charity_campaign["current_amount"]["decimal_places"],
            charity_campaign["current_amount"]["currency"],
        ),
        CharityCampaignAmount(
            charity_campaign["target_amount"]["value"],
            charity_campaign["target_amount"]["decimal_places"],
            charity_campaign["target_amount"]["currency"],
        ),
    )


def get_charity_campaign_donations(
    token: str, client_id: str, broadcaster_id: str, first: int = 20
) -> list[CharityCampaignDonation]:
    url = "https://api.twitch.tv/helix/charity/donations"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    donations = http.send_get_with_pagination(url, headers, params, first, 20)

    return [
        CharityCampaignDonation(
            donation["id"],
            donation["campaign_id"],
            User(donation["user_id"], donation["user_login"], donation["user_name"]),
            CharityCampaignAmount(
                donation["amount"]["value"],
                donation["amount"]["decimal_places"],
                donation["amount"]["currency"],
            ),
        )
        for donation in donations
    ]
