from discord import SyncWebhook
import discord
import json
with open("webhook_url.json","r") as f:
    webhook_urls=json.load(f)
    
INFO_WEBHOOK_URL=webhook_urls["info"]
WARNING_WEBHOOK_URL=webhook_urls["warning"]
EMBEDS_WEBHOOK_URL=webhook_urls["embeds"]

# print(WEBHOOK_URL)
info_webhook = SyncWebhook.from_url(INFO_WEBHOOK_URL)
warning_webhook = SyncWebhook.from_url(WARNING_WEBHOOK_URL)
embeds_webhook=SyncWebhook.from_url(EMBEDS_WEBHOOK_URL)
computer = "Computer Alexander"

#log discord stuff in seperate file
# logging.basicConfig(filename='discord.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
def send_notification(message:str,computer:str,type:str=["error","warning","info"]):
    def error_message(message,computer):
        warning_webhook.send(f'@everyone \n There was an error at **{computer}**:\n {message}')
    def warning_message(message,computer):
        warning_webhook.send(f'@everyone \n There was a warning at **{computer}**:\n {message}')
    def info_message(message,computer):
        info_webhook.send(f'Info  **{computer}**:\n {message}')
    if type == "error":
        error_message(message,computer)
    elif type == "warning":
        warning_message(message,computer)
    elif type == "info":
        info_message(message,computer)


def send_embedded_message_success(removed:str,changed:str,ppn:str):
    embed=discord.Embed(title="Commit to aDIS successfull", description="YAY", color=0x00ff00)
    embed.add_field(name="PPN", value=ppn, inline=False)
    embed.add_field(name="Removed", value=removed, inline=False)
    embed.add_field(name="Changed", value=changed, inline=True)
    
    embeds_webhook.send(embed=embed)

def send_embedded_message_error(removed:str,changed:str,ppn:str):
    embed=discord.Embed(title="Commit to aDIS failed", description="ERROR", color=discord.Color.red())
    embed.add_field(name="PPN", value=ppn, inline=False)
    embed.add_field(name="Removed", value=removed, inline=False)
    embed.add_field(name="Changed", value=changed, inline=True)
    
    embeds_webhook.send(embed=embed)

def create_thread():
    info_webhook.channel.create_thread(name="Test",auto_archive_duration=60)

if __name__ =="__main__":
    # send_notification("Test","Computer Alexander","warning")
    # send_notification("Test","Computer Alexander","error")
    # send_notification("Test","Computer Alexander","info")
    # create_thread()
    
    send_embedded_message_success("this","that", "123456789")
# send_notification("Test","Computer Alexander","info")