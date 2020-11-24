import discord

bot_presences = (
    discord.Game(status=discord.Status.dnd, name="o zalur pela janela"),
    discord.Game(status=discord.Status.idle, name="osu!droid"),
    discord.Game(status=discord.Status.dnd, name="Jogando idosos na rua"),
    discord.Activity(type=discord.ActivityType.competing, name="Torneio inexistente da osu!droid brasil"),
    discord.Activity(type=discord.ActivityType.watching, name=(
        "Minecraft: Venom e os Aventureiros - Multiplayer #1 - Construindo o Abrigo"),
                     url="https://youtu.be/rB11hfPdtWk"
                     ),
    discord.Activity(type=discord.ActivityType.listening, name="ISOLADOS - BIBI TATTO (CLIPE OFICIAL)",
                     url="https://youtu.be/2Z7krZ7XHjo"),
    discord.Activity(type=discord.ActivityType.listening,
                     name="Vocêss são uns merdas! Não são todos, mas a maioria..."),
    discord.Activity(type=discord.ActivityType.listening, name="Alts do lywi se aproximando!!!"),
    discord.Activity(type=discord.ActivityType.listening, name="Felipon malhando")

)
