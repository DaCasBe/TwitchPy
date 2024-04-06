from .._utils import http
from ..dataclasses import CharityCampaign, CharityCampaignDonation


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
        charity_campaign["broadcaster_id"],
        charity_campaign["broadcaster_name"],
        charity_campaign["broadcaster_login"],
        charity_campaign["charity_name"],
        charity_campaign["charity_description"],
        charity_campaign["charity_logo"],
        charity_campaign["charity_website"],
        charity_campaign["current_amount"],
        charity_campaign["target_amount"],
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
            donation["user_id"],
            donation["user_login"],
            donation["user_name"],
            donation["amount"],
        )
        for donation in donations
    ]
