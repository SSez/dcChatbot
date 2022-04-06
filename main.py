# coding=utf-8
import data_controller as d
import discord
import asyncio
import random
import pickle
import trainer as trl
from discord.ext import commands

import numpy
import pandas as pd
import tensorflow as tf

# Use GPU
from tensorflow.python.client import device_lib
tf.config.experimental.list_physical_devices('GPU')
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

DISCORD_SECRET_KEY = ''
client = commands.Bot(command_prefix="-")

def reloadList():
    load_data = d.get_data()
    return load_data

data = reloadList()
probability = 0

@client.event
async def on_ready():
    print('logged in as')
    print(client.user.name)
    print(client.user.id)
    print('----------')

@client.command(pass_context=True)
async def name(ctx):
    await ctx.channel.send("{} is your name".format(ctx.message.author.mention))

@client.command(pass_context=True)
async def myid(ctx):
    await ctx.channel.send("{} is your id".format(ctx.message.author.id))

@client.command()
async def reload(ctx):
    global data
    data = reloadList()
    await ctx.channel.send("Reloaded")

@client.command(pass_context=True)
async def who(ctx, *args):
    arg = args[0]
    id = str(ctx.message.mentions[0].id)
    name = str(ctx.message.mentions[0].name)
    mention = str(ctx.message.mentions[0].mention)
    await ctx.send( str("id: " + id + " name: " + name + " mention: " + mention) )

@client.command(pass_context=True)
async def register(ctx, user: discord.User):
    id =  str(user.id)
    name = str(user.name)
    mention = str(user.mention)

    if d.check_user(id) > 0:
        await ctx.send( str(mention + " " + "is already registered") )
    else:
        d.register(id=id, name=name)
        await ctx.send( str(mention + " " + "is now registered") )

@client.command()
async def trainer(ctx, *args):
    myid = str(ctx.message.author.id)
    status = int(d.getStatus(myid))
    if status == 1:
        if len(args) == 3:
            epoch = int(args[0])
            batch = int(args[1])
            option = int(args[2])
        elif len(args) == 2:
            epoch = int(args[0])
            batch = int(args[1])
            option = 0
        else:
            epoch = int(1000)
            batch = int(10)
            option = 0
        sizeTxt = discord.Embed(title = str("Epochs: " + str(epoch)  + " and " + "Batch Size: " + str(batch) ), colour = discord.Colour.blue() )
        response = discord.Embed(title = str(" :woman_in_manual_wheelchair: Starting training please wait... :woman_in_manual_wheelchair: "), colour = discord.Colour.blue() )
        
        await ctx.channel.send( embed=sizeTxt )
        await ctx.channel.send( embed=response )
        
        trl.retrain(epoch, batch, option)
        response = discord.Embed(title = str("Training complete! :woman_in_motorized_wheelchair: "), colour = discord.Colour.green() )
    else:
        response = discord.Embed(title = str("You do not have permission to use this command."), colour = discord.Colour.red() )
    await ctx.channel.send( embed=response )

def checkMentions(count_mentions, bot_msg, check_auth_answer, name, auth_name):
    if count_mentions > 0:
        check_answer = bot_msg.replace(name, ':replace_name:')
    elif auth_name in bot_msg and check_auth_answer == True:
        check_answer = bot_msg.replace(auth_name, ':replace_name:')
    else:
        check_answer = bot_msg
    return check_answer

@client.command()
async def pattern(ctx, *args):
    global data
    output = ''
    points = 0

    auth_id = ctx.message.author.id
    auth_name = ctx.message.author.name

    count = 0
    for word in args:
        output += word
        output += ' '
        count += 1
    output = output[:-1]

    out_split = output.split("tag:")
    tag_id = out_split[1]
    output = out_split[0]
    output = output.replace('?', '').replace('!', '')
    output = " ".join(output.split())

    countSQL = d.check_pattern(output)
    if countSQL > 0:
        response = discord.Embed(title = str("Already exists"), colour = discord.Colour.red() )
    elif count > 2 and count < 64:
        #tag_id = d.createTag()
        d.createPattern(output, tag_id)

        #points += 50
        #d.addPoints(auth_id, points)

        response = discord.Embed(title = str("New pattern added to Tag id: " + str(tag_id) ), colour = discord.Colour.blue() )
        data = reloadList()
    else:
        response = discord.Embed(title = str("You must use more than 3 and less than 64 words for the accuracy ;) "), colour = discord.Colour.red() )
    await ctx.channel.send( embed=response )

@client.command()
async def teach(ctx, *args):
    global data
    global probability
    output = ''
    rcount = -1
    points = 0

    index_response = 0.80

    auth_id = ctx.message.author.id
    auth_name = ctx.message.author.name

    check_auth_answer = False

    id = str("")
    name = str("")
    mention = str("")
    count_mentions = 0
    for member in ctx.message.mentions:
        id = str(member.id)
        name = str(member.name)
        mention = str(member.mention)
        count_mentions += 1
    
    count = 0
    for word in args:
        output += word
        output += ' '
        count += 1
    output = output[:-1]
    
    if count_mentions > 0:
        output = output.replace('?', '').replace('!', '').replace(mention, ':replace_name:').replace(id, ':replace_name:').replace(name, ':replace_name:').replace('<', '').replace('@', '').replace('>', '')
    else:
        output = output.replace('?', '').replace('!', '')

    countSQL = d.check_response(output)
    if countSQL > 0:
        response = discord.Embed(title = str("Already exists"), colour = discord.Colour.red() )
    elif count > 2 and count < 64:
        tag_id = d.createTag()
        d.createResponse(output, tag_id)

        #points += 100
        #addPoints(auth_id, points)

        response = discord.Embed(title = str("New response added! Tag id: " + str(tag_id) ), colour = discord.Colour.blue() )
        data = reloadList()
    else:
        response = discord.Embed(title = str("You must use more than 4 and less than 64 words for the accuracy ;) "), colour = discord.Colour.red() )
    await ctx.channel.send( embed=response )

def reply(msg, rcount, index_num, option):
    global data
    global probability
    bot_msg = ""
    responses_list = []

    pickle_name = ""
    model_name = ""
    if option == 0:
        type = "patterns"
        pickle_name = "models/data_patterns.pickle"
        model_name = "models/model_patterns.h5"
    elif option == 1:
        type = "responses"
        pickle_name = "models/data_responses.pickle"
        model_name = "models/model_responses.h5"

    try:
        with open(pickle_name, "rb") as f:
            words, labels, training, output = pickle.load(f)
    except:
        print("[error] loading pickle file")
    model = tf.keras.models.load_model(model_name)

    result = pd.DataFrame([trl.predict(msg, words)], dtype=float, index=['input'])
    results = model.predict([result])[0]
    resultList = numpy.argsort(results)

    results_index = resultList[rcount]
    tag = int(labels[results_index])
    msg_len = len(msg.split())
    probability = results[results_index]

    print ("----------")
    print ( str(probability) )
    print ( str(type) + str(" Tag id: ") + str(tag) )
    print ("----------")

    if probability > index_num:
        for tg in data:
            if tg["tag"] == tag:
                responses = tg["responses"]
                patterns = tg["patterns"]
                for res in responses:
                    responses_list.append(res)
                if len(responses_list) > 3 and msg_len > 2:
                    bot_msg = trl.responseModel(responses_list, msg)
                else:
                    bot_msg = random.choice(responses)
    else:
        bot_msg = ""

    return bot_msg

@client.command()
async def ask(ctx, *args):
    global probability
    msg = ""
    pred = ""
    first_msg = ""
    first_pred = ""

    count_patters = -1
    count_responses = -1
    index_pattern = 0.70
    index_response = 0.00

    auth_id = ctx.message.author.id
    auth_name = ctx.message.author.name
    bot_id = client.user.id
    check_auth_answer = False

    success = True
    guess = ""
    check_answer = ""
    points = 0

    id = str("")
    name = str("")
    mention = str("")
    count_mentions = 0
    for member in ctx.message.mentions:
        id = str(member.id)
        name = str(member.name)
        mention = str(member.mention)
        count_mentions += 1

    output = ''
    count = 0
    for word in args:
        output += word
        output += ' '
        count += 1
    output = output[:-1]

    if count_mentions > 0:
        output = output.replace('?', '').replace('!', '').replace(mention, ':replace_name:').replace(id, ':replace_name:').replace(name, ':replace_name:').replace('<', '').replace('@', '').replace('>', '')
    else:
        output = output.replace('?', '').replace('!', '').replace(',', '')

    output = output.lower()
    output = " ".join(output.split())
    
    bot_msg = reply( str(output), int(count_patters), index_pattern, 0 )
    if not bot_msg:
        success = False
        bot_msg = reply( str(output), int(count_responses), index_response, 1 )
        if not bot_msg:
            success = False
        bot_msg = "I did not understand the question."

    if ":replace_name:" in bot_msg:
        if count_mentions > 0:
            bot_msg = bot_msg.replace(':replace_name:', name)
        else:
            check_auth_answer = True
            bot_msg = bot_msg.replace(':replace_name:', auth_name)

    answer = discord.Embed(title = str(bot_msg), colour = discord.Colour.blue() )
    first_msg = await ctx.channel.send( embed=answer )

    if success == True:
        # Check response #
        check_answer = checkMentions(count_mentions, bot_msg, check_auth_answer, name, auth_name)
        countSQL = d.getResCount( str(check_answer), str(output) )
        
        if countSQL > 0:
            #print("Already exists")
            success = False
        else:
            xx = probability * 100
            probability = round(xx, 2)
            askYN = discord.Embed(description = str("[{}%] Did this answer satisfy you? type: yes/no").format(probability), colour = discord.Colour.blue() )
            first_pred = await ctx.channel.send( embed=askYN )
    
    def is_correct(m):
        if m.author.id == auth_id:
            if m.content.lower() == 'no' or m.content.lower() == 'yes':
                return True

    while True:
        r = False
        try:
            guess = await client.wait_for('message', check=is_correct, timeout=5.0)
            #guess = await client.wait_for('message', check=(lambda message: message.author.id == auth_id), timeout=15.0)
        except asyncio.TimeoutError:
            if success == True:
                took_long = discord.Embed(description = str("{} You took too long to reply.").format(auth_name), colour = discord.Colour.red() )
                await ctx.channel.send( embed=took_long )
                if msg and pred:
                    await msg.delete()
                    await pred.delete()
                    msg = ""
                    pred = ""
                break
        else:
            if success == True:
                check_answer = checkMentions(count_mentions, bot_msg, check_auth_answer, name, auth_name)
                
                clientAns = str(guess.content)
                if clientAns.lower() == "yes":
                    countSQL = d.getResCount( str(check_answer), str(output) )
                    if countSQL > 0:
                        print("Already exists")
                    else:
                        SQL_id = d.getResponseID( str(check_answer) )
                        d.insert( str(output), int(SQL_id) )
                        data = reloadList()
                        points += 5
                    #break
                    r = True
                if clientAns.lower() == "no":
                    r = True
                    
                    count_responses -= 1
                    if count_responses == -8:
                        r = True
                    #bot_msg = reply( str(output), int(count_responses), index_response, 1 )
                    if not bot_msg:
                        r = True
                    else:
                        if ":replace_name:" in bot_msg:
                            if count_mentions > 0:
                                bot_msg = bot_msg.replace(':replace_name:', name)
                            else:
                                check_auth_answer = True
                                bot_msg = bot_msg.replace(':replace_name:', auth_name)
                        xx = probability * 100
                        probability = round(xx, 2)

                        if msg and pred:
                            await msg.delete()
                            await pred.delete()
                            msg = ""
                            pred = ""
                        if first_msg and first_pred:
                            await first_msg.delete()
                            await first_pred.delete()
                            first_msg = ""
                            first_pred = ""
                        
                        answer = discord.Embed(title = str(bot_msg), colour = discord.Colour.blue() )
                        msg = await ctx.channel.send( embed=answer )

                    askYN = discord.Embed(description = str("[{}%] Did this answer satisfy you? type: yes/no").format(probability), colour = discord.Colour.blue() )
                    pred = await ctx.channel.send( embed=askYN )
                    points += 5
                
                if r:
                    botReply = discord.Embed(title = str("Thank you for your answer {.author.name}" ).format(guess), colour = discord.Colour.green() )
                    await ctx.channel.send( embed=botReply )
                    break

client.run(DISCORD_SECRET_KEY)