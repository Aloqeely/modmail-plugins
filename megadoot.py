import discord
from discord.ext import commands
import random 
from random import randint,choice

fights = [
    '{0} tried to throw a snowball at {1} but it hits Dabbit\'s car, and Dabbit is not pleased!',
    '{0} tackled {1} down with a fish.',
    '{0} fought {1}, but it was not effective...',
    '{0} tried to throw a bucket of water at {1}, but accidentally threw it all over the server owner!',
    '{0} got tired of ks’ puns and tried to fight but accidentally hit {1}',
    '{0} tried to hit {1}, but {1} had a reverse card up their sleeve so {0} got hit instead',
    '{0} tried to fight {1}, but ended up being given cereal soup by Dabbit.',
    '{0} tried to attack {1}, but they slipped and crashed into Ghoul\'s car, making a huge cat shaped dent in the hood',
    '{0} tried to fight {1} but was attacked by a gang of kittens',
    '{0} challenged {1} to a race in Mario Kart but the CPU won instead!',
    '{1} dodged a mighty fine swing from {0}, and then backhanded {0} in self defense.',
    '{0} begged their pet to attack {1}, but the pet stared back with no indication of understanding.',
    '{0} fought like a dog, but {1} fought back like a bear, winning the fight!',
    'A wild {1} appears!\n{1} uses Bite! It\'s not very effective...\n{0} uses Mega Punch! It\'s very effective!\n{0} has won!',
    'As {0} ran all sweaty and tired reaching out for a last punch, {1} dashed to the side, leaving {0} tumbling onto the ground.',
    '{0} tried to modify the Dupe Bomber 3000 to take down {1} with tons of dupe reports, but Dannysaur got there first and denied them all... Which broke the machine.',
    '{0} Mega Evolved and tried to wipe out {0} with Hyper Beam! But {1} used Mimic and reversed it back onto {0} instead!',
    '{0} threw a snowball at {1} but unfortunately it hits a window at Discord HQ. Oops',
    '{0} tricked {1} into waking up the Sleeping Pizza. The Sleeping Pizza does not like being woken up, so it turned both {0} and {1} into Calzone Pizza. Rest In Pepperoni.',
    '{0} went to tackle {1}, but they did a dank meme and lowkey dabbed out of the way',
    '{0} hit the Smash ball, but fell off the stage before they could use it on {1}',
    '{0} threw a pokeball at {1}, but it was only a Goldeen'
        ]

        hugs = [
            '{0} gave {1} an awkward hug.',
            '{0} pretended to give {1} a hug, but put a "Kick Me" sign on them.',
            '{0} gave {1} a great bear hug!',
            '{1}, {0} just gave you the best hug of your life!',
            '{0} gave {1} a friendly little hug.',
            '{0} tried to give {1} a hug but was denied.',
            '{0} tackle-hugs {1}.',
            '{0} gave {1} a bog standard hug',
            '{1} accidentally reported the wrong thing so {0} gave them a hug to stop {1} from crying',
            '{0} gives {1} a cereal soupy hug',
            '{0} hugged {1} so hard, they exploded in a cloud of pepperonis',
            '{0} goes to hug {1}, what a good friendship.',
            '{0} successfully hugs {1} with the power of the Wumpus.',
            '{0} sent {1} some love, do I get some too?',
            '{1} ducked when {0} tried to hug them.',
            '{0} hugged {1} but {1} took it as an attack!',
            '{0} fills {1} with sweet love',
            '{0} gave {1} a Legacy Hug, in recognition of the legendary Dabbit Prime.',
            'Is {0} sure they want to hug {1}? Sure thing, as they just did!',
            '{0} attempts to hug {1} but Dannysaur threw a banana peel on the floor and made {0} slip',
            '{1} is confused if cereal is soup or salad, so {0} hugged {1} to calm them down'
                ]



@bot.command()
async def fight(ctx, user : discord.Member):
    await ctx.send(f"{choice(fights)}".format(ctx.message.author.name, user))
    ]


@bot.command()
async def hug(ctx, user : discord.Member):
    await ctx.send(f"{choice(hugs)}".format(ctx.message.author.name, user))
    ]

