import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context, CommandError
import datetime


async def setup(bot: Bot):
    await bot.add_cog(HelpCog(bot))


class HelpCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.embed_orange = discord.Colour(0xeab148)
        self.embed_dark_pink = discord.Colour(0x7d3243)

    def info_embed_gen(self, name: str) -> discord.Embed:
        """Generate an info embed."""
        embed = discord.Embed(
            title="Hello There!",
            description=(
                f"Hello, I'm {name}! You can type any command after typing my prefix "
                f"**`'{self.bot.command_prefix}'`** to activate them. Use **`!help`** to see some command options.\n\n"
                "Here is a link to my [source code](https://github.com/0wlport/0wlmusic.git) if you wanted to check it out!"
            ),
            colour=self.embed_orange
        )
        return embed

    def error_embed_gen(self, error: CommandError) -> discord.Embed:
        """Generate an error embed."""
        embed = discord.Embed(
            title="ERROR :(",
            description=(
                "There was an error. You can likely keep using the bot as is, or just to be safe, you can ask your server "
                "administrator to use !reboot to reboot the bot.\n\nError:\n**`{error}`**"
            ),
            colour=self.embed_dark_pink
        )
        return embed

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: CommandError):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return
        print(f"[{datetime.datetime.now()}] {error}")
        await ctx.send(embed=self.error_embed_gen(error))

    @commands.Cog.listener()
    async def on_ready(self):
        """Handle bot readiness."""
        send_to_channels = []
        bot_names = {}
        for guild in self.bot.guilds:
            channel = guild.text_channels[0]
            send_to_channels.append(channel)
            bot_member = await guild.fetch_member(self.bot.user.id)
            nickname = bot_member.nick or bot_member.name
            bot_names[guild.id] = nickname

    @commands.command(
        name="help",
        aliases=["h"],
        help=(
            "(command_name)\n"
            "Provides a description of all commands or a longer description of an inputted command\n"
            "Gives a description of a specified command (optional). If no command is specified, then gives a less detailed description of all commands."
        )
    )
    async def help(self, ctx: Context, arg: str = ""):
        """Provide help information for commands."""
        help_cog = self.bot.get_cog('HelpCog')
        music_cog = self.bot.get_cog('MusicCog')
        commands = help_cog.get_commands() + music_cog.get_commands()
        if arg:
            command = next((c for c in commands if c.name == arg), None)
            if command is None:
                await ctx.send("That is not a name of an available command.")
                return

            arguments = command.help.split("\n")[0]
            long_help = command.help.split("\n")[2]
            aliases = ", ".join(f"!{a}" for a in command.aliases)
            commands_embed = discord.Embed(
                title=f"!{command.name} Command Info",
                description=(
                    f"Arguments: **`{arguments}`**\n"
                    f"{long_help}\n\n"
                    f"Aliases: **`{aliases}`**"
                ),
                colour=self.embed_orange
            )
        else:
            command_description = "\n".join(
                f"**`!{c.name} {c.help.split('\n')[0]}`** - {c.help.split('\n')[1]}"
                for c in commands
            )
            commands_embed = discord.Embed(
                title="Command List",
                description=command_description,
                colour=self.embed_orange
            )

        command_key = (
            "**`Command Prefix`** - '!'\n\n"
            "**`!command <>`** - No arguments required\n"
            "**`!command ()`** - Optional argument\n"
            "**`!command []`** - Required argument\n"
            "**`!command [arg]`** - 'arg' specifies argument type (eg. 'url' or 'keywords')\n"
            "**`!command (this || that)`** - Options between mutually exclusive inputs (this or that)"
        )

        key_embed = discord.Embed(
            title="Key",
            description=command_key,
            colour=self.embed_orange
        )
        await ctx.send(embed=commands_embed)
        await ctx.send(embed=key_embed)

    @commands.command(
        name="reboot",
        aliases=["rb"],
        help=(
            "<>\n"
            "Completely restarts the bot.\n"
            "Gives a complete restart of the bot. This will also update the [code from GitHub](https://github.com/0wlport/0wlmusic.git). This command can only be called by the owner of the server."
        )
    )
    async def reboot(self, ctx: Context):
        """Reboot the bot."""
        if ctx.message.author.guild_permissions.administrator:
            await ctx.send("Rebooting application now!")
            await self.bot.close()
        else:
            await ctx.send("You do not have proper permissions to reboot me.")

    @commands.command(
        name='info',
        aliases=[],
        help=(
            "<>\n"
            "Gives info about the bot\n"
            "Gives info about the bot"
        )
    )
    async def info(self, ctx: Context):
        """Provide info about the bot."""
        await ctx.send(embed=self.info_embed_gen("0wlmusic"))
