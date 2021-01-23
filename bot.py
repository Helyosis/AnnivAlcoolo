# coding: utf-8
import discord, asyncio
import sqlite3, atexit
from discord.ext import commands
import datetime, schedule
from threading import Timer
import threading, time
import random, os

bot = commands.Bot(command_prefix = "a!")

DEBUG = False # Passer en False pour utiliser le bon token

correspondance_mois = {
    '01': '📆 === 𝓙𝓪𝓷𝓿𝓲𝓮𝓻',
    '02': '💪 === 𝓕é𝓿𝓻𝓲𝓮𝓻',
    '03': '🍀 === 𝓜𝓪𝓻𝓼',
    '04': '🐟 === 𝓐𝓿𝓻𝓲𝓵',
    '05': '🌸 === 𝓜𝓪𝓲',
    '06': '🍍 === 𝓙𝓾𝓲𝓷',
    '07': '🌞 === 𝓙𝓾𝓲𝓵𝓵𝓮𝓽',
    '08': '🏖️ === 𝓐𝓸û𝓽',
    '09': '🍂 === 𝓢𝓮𝓹𝓽𝓮𝓶𝓫𝓻𝓮',
    '10': '🎃 === 𝓞𝓬𝓽𝓸𝓫𝓻𝓮',
    '11': '❄️ === 𝓝𝓸𝓿𝓮𝓶𝓫𝓻𝓮',
    '12': '🎄 === 𝓓é𝓬𝓮𝓶𝓫𝓻𝓮'
}


def how_many_seconds_until_midnight():
    """Get the number of seconds until midnight."""
    tomorrow = datetime.datetime.now() + datetime.timedelta(1)
    midnight = datetime.datetime(year=tomorrow.year, month=tomorrow.month, 
                        day=tomorrow.day, hour=0, minute=0, second=1)
    return (midnight - datetime.datetime.now()).seconds


async def logging(ctx):
    log_msg = f"{ctx.author} a écrit sur le serveur {ctx.guild.name} sur le channel #{ctx.channel.name}:\n```{ctx.message.content}```"
    if DEBUG: print(log_msg)
    await LOG_CHANNEL.send(log_msg)


@bot.group(name = 'anniversaire', aliases = ['anniv', 'a'], description = "Pour ajouter son anniversaire: a!anniversaire add JOUR MOIS\nPour le supprimer: a!anniversaire delete\n")
async def anniversaire(ctx):
    """
    Permet d'ajouter et de supprimer son anniversaire à la base de données.
    Utilise les sub-commands pour fonctionner.
    """
    await logging(ctx)


@anniversaire.command(name = "add", description = "Permet d'ajouter un anniversaire à la base de données.")
async def add(ctx, *args):
    """
    Permet d'ajouter son anniversaire à la base de données
    """
    if len(args) == 2:
        day, month = args
        if len(day) == 1: day = '0' + day #Toutes les dates doivent être de taille deux
        if len(month) == 1: month = '0' + month
        date = str(day) + str(month)
    elif len(args) == 1: #Si de la forme JOUR/MOIS (= un seul argument utilisé, à séparer)
        try:
            day, month = args[0].split('/')
        except:
            await ctx.send("Une erreur s'est produite. Veuillez verifiez la syntaxe")
            return
        else:
            if len(day) == 1: day = '0' + day
            if len(month) == 1: month = '0' + month
            date = str(day) + str(month)
        
    if len(date) != 4: #Si il y a eu une erreur quelque part. eg. a!anniversaire add 123 45
        await ctx.send("Une erreur s'est produite. Veuillez verifiez la syntaxe")
        return

    author = ctx.author
    server_id = ctx.guild.id

    if cursor.execute("SELECT * from users where server_id=? AND id=?", (server_id, author.id)).fetchall():
        await ctx.send(f"L'anniversaire de {ctx.guild.get_member(author.id).display_name} est déjà dans la liste des anniversaires. Tu dois le supprimer pour pouvoir en ajouter un autre.")
        return
    cursor.execute("""INSERT INTO users(id, date, server_id) VALUES(?, ?, ?)""", (author.id, date, server_id))
    db_anniversaire.commit()
    await ctx.send(f"L'anniversaire de {ctx.guild.get_member(author.id).display_name} a bien été rajouté avec la date {date}")


@anniversaire.command(name = 'delete', aliases = ['remove'], description = "Permet de retirer son anniversaire de la base de données.")
async def delete(ctx):
    cursor.execute("""DELETE FROM users WHERE id=?""", (ctx.message.author.id,))
    db_anniversaire.commit()
    await ctx.send("L'anniversaire a bien été supprimé.")


@anniversaire.command(description = "Force le souhait des anniversaires d'aujourd'hui")
async def today(ctx):
    print('[+] Check anniv once')
    msg = "Les anniversaires aujourd'hui sont:\n**"
    date = datetime.datetime.today()
    day = str(date.day)
    month = str(date.month)

    if len(month) != 2: month = '0' + month
    if len(day) != 2: day = '0' + day
    date = day + month

    ch = bot.get_channel(anniv_channel_id[ctx.guild.id])
    if ch is not None:
        cursor.execute("""SELECT id FROM users WHERE date=? AND server_id=?""", (date,server_id))
        all_users = cursor.fetchall()
        if len(all_users) >= 1:
            for row in all_users:
                print(row)
                nick = ch.guild.get_member(int(row[0])).display_name
                msg += f"{nick}\n"
                print(row)
            msg += "**"
            message = await ch.send(msg, file=discord.File( fp = os.path.join("Images", random.choice(os.listdir("Images"))) ) )
            await message.add_reaction('🎉')
        else:
            await ch.send("Ce n'est l'anniversaire de personne aujourd'hui :(")
    else:
        ctx.send


@bot.command(description = "Permet d'ajouter un certain type de channel")
async def new(ctx, type_: str, value: str):
    if type_ == "ANNIV_CHANNEL_ID" or "REPORTING_USERS":
        if cursor.execute("""SELECT * FROM server_specific_infos WHERE name=? AND server_id=?""", (type_, ctx.guild.id)).fetchone() is None:
            cursor.execute("""INSERT INTO server_specific_infos(name, server_id, value) VALUES(?, ?, ?)""", ( type_, ctx.guild.id, int(value) ))
            db_anniversaire.commit()
            await ctx.send(f"{type_} a bien été ajouté sur la base de données pour ce serveur avec comme valeur {value}")
            return

    await ctx.send("Une erreur s'est produite. La valeur existe déjà pour ce serveur ou le type n'existe pas")

@bot.command(name = 'anniversaires', aliases = ['annivs'])
async def print_all_annivs(ctx, *args):
    """
    Affiche la liste des anniversaires des personnes de ce serveur et qui l'ont ajouté ici.
    Il est possible de filtrer et de ne récupérer que les mois voulus en indiquant les nombres après (ex: "a!annivs 07" permet de n'afficher que les anniversaires du mois de Juillet)
    Il est possible de mettre plusieurs filtres à la suite.
    """

    await logging(ctx)

    server_id = ctx.guild.id
    cursor.execute("""SELECT id, date FROM users WHERE server_id=?""", (server_id,))
    all_users = cursor.fetchall()
    i = 0
    if len(all_users) >= 1:
        sorted_users = sorted(all_users, key = lambda x: (int(x[1][2:]), int(x[1][:2])))
        temp_dict = {}
        for row in sorted_users:
            print(row)
            nick = bot.get_user(int(row[0]))
            if nick is not None:
                if str(row[1][2:]) not in temp_dict.keys():
                    temp_dict[str(row[1][2:])] =  [f"{row[1][:2]} {nick.display_name}",]
                    #print('Nouveau truc', row[1][2:])
                else:
                    temp_dict[str(row[1][2:])].append(f"{row[1][:2]} {nick.display_name}")
                    #print('jE rajoute au mois', row[1][2:])
                #print(temp_dict)
            else:
                #print("Quelqu'un manque à l'appel", i)
                i += 1
        print("Il y a", i, "personne ayant quitté le serveur (ou autre problèmes, qui sait)")
        embed = discord.Embed(title = "Liste des anniversaires")
        print(temp_dict)
        for key in sorted(temp_dict.keys()):
            #print("Bonjour")
            try:
                mois = correspondance_mois[key]
                if len(args) == 0 or key in args or mois in args:
                    embed.add_field(name = mois, value = "\n".join(temp_dict[key]), inline = False)
            except Exception as e:
                print(e)
                continue

        await ctx.send(embed = embed)
    else:
        await ctx.send("Personne n'est actuellement enregistré dans la base de données")

async def check_anniv_loop():
    while True:
        print('[+] Check anniv loop')
        msg = "Les anniversaires aujourd'hui sont:\n"
        date = datetime.datetime.today()
        day = str(date.day)
        month = str(date.month)
        if len(month) != 2: month = '0' + month
        if len(day) != 2: day = '0' + day
        date = day + month

        for server_id in list(anniv_channel_id.keys()):
            cursor.execute("""SELECT id FROM users WHERE date=? AND server_id=?""", (str(date), server_id))
            all_users = cursor.fetchall()
            if len(all_users) >= 1:
                ch = bot.get_channel(anniv_channel_id[server_id])
                if ch is not None:
                    for row in all_users:
                        print(row)
                        nick = ch.guild.get_member( int(row[0]) ).display_name
                        msg += f"{nick}\n"
                    message = await ch.send(msg, file=discord.File( fp = os.path.join("Images", random.choice(os.listdir("Images"))) ) )
                    await message.add_reaction('🎉')
        time_to_wait = how_many_seconds_until_midnight()
        await asyncio.sleep(time_to_wait)


@bot.event
async def on_ready():
    global LOG_CHANNEL

    print("-------")
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

    LOG_CHANNEL_ID = cursor.execute("""SELECT value FROM global_infos WHERE name=?""", ('LOG_CHANNEL_ID',)).fetchone()[0]
    print("LOG_CHANNEL_ID :", LOG_CHANNEL_ID)
    LOG_CHANNEL = bot.get_channel(int(LOG_CHANNEL_ID))
    print("LOG_CHANNEL existe ?", LOG_CHANNEL)
    bot.loop.create_task(check_anniv_loop())




@bot.command()
async def report(ctx):
    user_to_report = reporting_users[ ctx.guild.id ]
    x = bot.get_user(user_to_report)
    message = ctx.message.content[2:]
    if len(ctx.message.mentions) == 1:
        user_id = ctx.message.mentions[0].id
    else:
        await ctx.send("Il faut mettre une et une seule mention d'utilisateur afin de pouvoir traiter le message correctement")
        return

    print(user_id)

    user = bot.get_user(user_id)
    reason = " ".join(message)

    await x.send(f"""**{ctx.author.display_name}** a demandé a reporté **{user.display_name}** pour la raison suivante :\n```{reason}```""")
    await ctx.send(f"L'utilisateur a bien été reporté à **{x.display_name}**")


if __name__ == '__main__':
    print("Launching AlcooloAnniv in", "debug" if DEBUG else "prod","mode.")
    db_anniversaire = sqlite3.connect('anniversaires.db' if not DEBUG else 'debug.db')
    cursor = db_anniversaire.cursor()
    cursor.execute( """CREATE TABLE IF NOT EXISTS users(id INTEGER, date TEXT, server_id INTEGER)""" )
    cursor.execute( """CREATE TABLE IF NOT EXISTS global_infos(name TEXT, value TEXT)""" )
    cursor.execute( """CREATE TABLE IF NOT EXISTS server_specific_infos(name TEXT, server_id INTEGER, value TEXT)""" )
    db_anniversaire.commit()

    LOG_CHANNEL = None

    token = cursor.execute("""SELECT value FROM global_infos WHERE name=?""", ('TOKEN',)).fetchone()[0]

    reporting_users = {}
    liste = cursor.execute( """SELECT server_id, value FROM server_specific_infos WHERE name=?""", ("REPORTING_USERS",)).fetchall()
    for server_id, value in liste:
        print('REPORTING_USERS :', server_id, value)
        reporting_users[int(server_id)] = int(value)

    anniv_channel_id = {}
    liste = cursor.execute( """SELECT server_id, value FROM server_specific_infos WHERE name=?""", ("ANNIV_CHANNEL_ID",)).fetchall()
    for server_id, value in liste:
        print('ANNIV_CHANNEL_ID :', server_id, value)
        anniv_channel_id[int(server_id)] = int(value)
    print(anniv_channel_id)

    bot.run(token)