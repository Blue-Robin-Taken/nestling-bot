import cryptography.fernet
import discord
from discord.ext import commands
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64
import requests

pastebin_key = "G71h0ycVCp0LDtxH011w8i7oqKQa1ki5"


class encryption(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_key(self, key_):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'e,\x9f\xbfA\xfd\xa7\t U\xc5\xc7\x11\xde\xae6e\x14\xe0\xd7N\xc4*\xabe0\x8f\xb8y\xa3\xa2\xdf',
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_.encode()))
        return key

    @commands.slash_command(name="encrypt", description="Encrypts a message")
    async def encrypt(self, ctx,
                      message: discord.Option(str, description="Message that you want to encrypt", required=True),
                      key: discord.Option(str, description="Key that you want to use. This is also used to decrypt.",
                                          required=True)):
        key = self.get_key(key)
        fernet = Fernet(key)
        encrypted_message = fernet.encrypt(message.encode())
        url = requests.post(url="https://pastebin.com/api/api_post.php", data={'api_dev_key': pastebin_key, 'api_option':'paste', 'api_paste_code':encrypted_message.decode(), 'api_paste_private':'1', 'api_paste_expire_date':'1H'}).text
        embed = discord.Embed(title="Encrypted Message", description=encrypted_message.decode() + f'\n \n Pastebin URL: [here]({url})',
                              color=discord.Color.random(), url=url)
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(name="decrypt", description="Decrypts a message")
    async def decrypt(self, ctx,
                      message: discord.Option(str, description="Token that you want to decrypt. (Returned by /encrypt)",
                                              required=True),
                      key: discord.Option(str, description="Key that was used to encrypt the message.",
                                          required=True)):
        try:
            key = self.get_key(key)
            fernet = Fernet(key)
            decrypted_message = fernet.decrypt(message.encode())
            embed = discord.Embed(title="Decrypted Message", description=decrypted_message.decode(),
                                  color=discord.Color.random())
            await ctx.respond(embed=embed, ephemeral=True)
        except cryptography.fernet.InvalidToken as e:
            await ctx.respond(f"Invalid token", ephemeral=True)
