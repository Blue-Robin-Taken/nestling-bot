import cryptography.fernet
import discord
from discord.ext import commands
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64


class encryption(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_key(self, key_):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt= b'8\xa8+h(\x10\xe1s\x13\xc0\xf9/?\xa3\\\xc0%X\xd1\xe9\xee\xd101\xbd\x0b}h\x16]\\\x8e',
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
        await ctx.respond(encrypted_message.decode(), ephemeral=True)

    @commands.slash_command(name="decrypt", description="Decrypts a message")
    async def decrypt(self, ctx,
                      message: discord.Option(str, description="Token that you want to decrypt. (Returned by /encrypt)", required=True),
                      key: discord.Option(str, description="Key that was used to encrypt the message.",
                                          required=True)):
        try:
            key = self.get_key(key)
            fernet = Fernet(key)
            decrypted_message = fernet.decrypt(message.encode())
            await ctx.respond(decrypted_message.decode(), ephemeral=True)
        except cryptography.fernet.InvalidToken as e:
            await ctx.respond(f"Invalid token", ephemeral=True)