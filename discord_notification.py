from discord import SyncWebhook


WEBHOOK_URL = "https://discord.com/api/webhooks/1065363714649358406/19SohbHFamqRMK9HTWmNdZ_TAx2TSyibNxjLoXNUIId38XApZS64qd0RnZOXpWHMrAGn"
webhook = SyncWebhook.from_url(WEBHOOK_URL)
webhook.send("Hello World")


