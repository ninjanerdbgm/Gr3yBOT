#!/usr/bin/env python

# FIGHTBOT, by bgm
# https://greynoi.se
#
# This is the brains of the fighting script contained withing
# Gr3yBOT.py.  All of the algorithms contained below were 
# developed solely by bgm, with the exception of the XOrShift
# function. If you end up using these, please give me credit
# somewhere in your comments.  

from gr3ybot_settings import FIGHT_VERBOSE, FIGHTLOG, LOGFILE, LOCALTZ
import random
import sys
from pytz import timezone
import pytz
import os
from time import strftime, sleep, localtime
import time
import datetime
from collections import OrderedDict
import math

#-- Exit this program if called by itself
if __name__ == "__main__":
	print "You can't run this as its own program!"
	sys.exit()
#--

#-- Logging...
timeformat = "%m/%d/%y %H:%M:%S"
def log(p1=None,p2=None,text=None):
	if text is not None:
		if FIGHTLOG is not None: LOGFILE = FIGHTLOG
		localnow = datetime.datetime.now(timezone(LOCALTZ))
	        with open(LOGFILE, 'a+') as f:
	                f.write("{0} --==-- {1}\r\n".format(strftime(timeformat),text))
	        f.close()
		if p1 is not None and p2 is not None:
			writeHistory(p1,p2,text)
#--

def writeHistory(p1,p2,text):
	if p1 is None and p2 is None: return False
	localnow = datetime.datetime.now(timezone(LOCALTZ))
	wroteline = 0
	with open('fights.log', 'r+') as f:
		lines = f.readlines()
		f.seek(0)
		for line in lines:
			thisline = line.split('[-]')
			thisline[len(thisline)-1] = thisline[len(thisline)-1].strip('\r\n')
			try:
				if thisline[0] == p1 or thisline[1] == p1:
					thisline = "[-]".join(thisline)
					f.write("{0}[-]{1} --==-- {2}\r\n".format(thisline,strftime(timeformat),text))
					wroteline = 1
				else:
					f.write(line)
			except:
				continue
		if wroteline == 0:
			f.write("{0}[-]{1}[-]{2} --==-- {3}\r\n".format(p1,p2,strftime(timeformat),text))
		f.truncate()
		f.close()

def getHistory(name):
	if not FIGHT_VERBOSE: return False
	with open('fights.log', 'r') as f:
		lines = f.readlines()
		f.seek(0)
		for line in lines:
			thisline = line.split('[-]')
			if thisline[0] == name or thisline[1] == name:
				thisline = "[-]".join(thisline)
				return thisline
		f.close()
	return False
#--				

#-- Init globals...
XA = int(round(time.time()))
XB = 246246246246
XC = random.getrandbits(12)
XD = os.getpgid(0)
#--

#-- Init actions.  Thanks to the Seventh Sanctum (http://www.seventhsanctum.com) for giving me large lists of words and phrases...
verbage = ["utilizes a","performs a","executes a","drops a","throws a","surprises everyone with a","expertly attempts a","somehow does a","stuns the world with a"]
qualifiers = [" perfect"," mediocre"," good"," passable"," terrible"," really bad"," pretty good"," kind of shitty"," really shitty"," not good but not bad","n excellent","n amazing","n incredible"," pazowzing"]
attackVerbs = [
	"Black Lock of the Unfriendly Seekers","Blue Palm","Chariot Hold of the Soldiers","Choke of the Placid Theif","Defensive Nine Immortals Snap","Defensive Roll of the Snake","Drunk Lift of Holes",
	"Eighteen Stalkers Pinch of Purple Palms","Fierce Eighteen Queens Tornado","Goddess Clap of the Penetrating Knee","Groom's Claw of Lead Amethysts","High Underhook of the Poor Madmen","King Fang of Masks",
	"Mighty Bloody Leg","One Million Kind Pigs Elbow of Platinum Anvils","Phantom Demon Meteor","Sapphire Stretch of the Searcher","Southwestern Madman's Noose of Destructions","Squirrel Hand of Firey Glaciers",
	"Terrible Thoughtful Stalker Sacrifice","Thrust of the Invisible Bear","Thunder of Fortuitous Aged Dogs","Tiger Toe of the Sacred Victory","Toss of the Fortuitous Phoenixes","Triumphant Finger of the Rabbits",
	"Advanced Foot of the Stalkers","Battler's Perfect Leg","Bite of the Flying Fire","Blessed Underhook of the Generous Rats","Boastful Charioteer Strike of Deaths","Bull Toe of the Diamond","Chop of the Penetrating Stream",
	"Dragon Clap of the Amethyst Rain","Ethereal Beetle Press","Fatal Tornado of the Fear-ridden Gods","Fist of the Guardian","Flying Toe of the Cowardly Horse","Ghastly Thirteen Rings Knuckle","Golden Chop of the Aged Bandits",
	"Grab of the Sitting Groom","Intelligent Theif's Chop of the Hazard","Invincible Drunken Dance","Leg of the Persuasive Shamans","Madman's Tooth of Barbarian Idols","Northwestern Drag","Southern Crane's Trap of the Secret",
	"Subterranian Shield of the Hopes","Theif Strike of Meditations","True Saintly Blade Flip","Unknown Nine Annihilations Cyclone","Angel Lift of Straight Lutes","Angry Monk's Pull of the Raid","Badger's Press of the Insanity",
	"Boastful Automaton Blow of the Frost","Boastful Buddha's Smash of Stones","Brave Charioteer's Toss","Candle Roll of the Boastful Shamans","Clap of the Nineteen Battlers","Dragon Slam of Inescapable Rings","Drunk Ant's Roll",
	"Fang of the Clever Devils","Flip of the Just Monks","Kick of the Sunrise","Leaping Assasin Clap","Phoenix Drop of the Blasphemous Cross","Rabbit's Spin of the Unholy Providence","Roll of the Eighty Searchers","Shaman's Ebony Throw",
	"Sixteen Boars Spin","Snare Underhook of the One Million Madmen","Spectral Underhook of the Eccentric Mouse","Strike of the Ninety Fortunes","Unknowable Dog Leg of the Grimoire","Uppercut of the Crane","Wild Savage Torture ",
	"Ambitious Shaman Clap of Grounds","Aquatic Sixty Squirrels Strike","Buddha Block","Cowardly Monk Bite of Boulders","Fist of Ethereal Gods","Fist of the One Hundred Queen Birds","Floating One Hundred Protectors Sweep",
	"Forty Lazy Priests Leg of Diamond Sacrifices","Green Torture","Heavenly Savage Badger Rake of Crowns","Heroic Demon Palm","King Shield Clutch","Lie Roll of the Kings","Lock of the Priestesses","Melancholy Drunk's Stomp",
	"Mine Leg of the Panda","Murderer's Knuckle of the Defensive Sapphire","Nineteen Dogs Stomp of Automatons","Phantom Fang of the Blessing","Pull of Blue Providences","Silent Battler's Hold of Sunsets","Southeastern Awkward Snake Stretch",
	"Squirrel Pinch of Seals","Twisted Sitting Bird Stretch of Tornadoes","Whirlwind of the Crippled Horse","Abdominal Roll","Bear Snap","Chin Flurry","Crucifix Headbutt","Elbow Stretch","Force Foot","Giant Heel Drive","Rana Vice",
	"Russian Apron Sleeper","Schoolboy Jaw Jawbreaker","Shooting Bite","Slide Clip","Stump Carry","Stump Drop","Super Breaker","Tag-Team Buster","Team Bell Spin","Team Sleeper","The People's Ring Rope Attack","Vengeance Uppercut","Victory Armbar",
	"Victory Handspring Lift","Wheel Attack","Wheel Flip","Wing Drive","Baseball Suffering Scissors","Brainbuster Gutwrench","Cartwheel Scissors","Chin Vice","Cross Guillotine","Crucifix Mare Hair Pull","DDT Uppercut","Dual Crab Kick","Entanglement Guillotine",
	"Flapjack Axe Sweep","Guillotine Drop","Inverted Suffering Gutbuster","Jaw Armbar","Jumping Monkey Knee","Mare Flip","Monkey Gutbuster","Mounted Smash","Nelson Hammer","Rolling Entanglement Breaker","Senton Mare Smash","Surfboard Scorpion Jawbreaker",
	"Team Axe Puller","Trapezius Driver","Vertical Rack Uppercut","Victory Vengeance Twist","Arm Powerbomb","Backflip Elbow","Baseball Hold","Chicken Stomp","Corner Blow","Crossed Clutch","Fireman's Body Bomb","Grounded Clutch","Guillotine Vice",
	"Hammerlock Whip","Heel Twist","Inverted Entanglement Drop","Koppu Headbutt","Lifting Vice","Mounted Lift","Overhead Power Clip","Schoolboy Suicida","Scorpion Spin","Slide Butt Spin","Slide Driver","Somersault Driver","Special Stomach Jawbreaker",
	"Spinning Shoulder Slam","Swinging Rake","Victory Throw","Achilles Tendon Swing","Cartwheel Guillotine Rake","Chicken Breaker","Crab Takedown","Cradle Eye Driver","Death Guillotine","Double Whip","Face Clutch","Half Suicida","Irish Powerbomb",
	"Japanese Crab Elbow","Japanese Mat Stomp","Knife Jawbreaker","Lifting Brain Stomp","Mandible Achilles Tendon Hug","Neck Hug","Ring Rope Buster","Shooting Chicken Knee","Single Body Takedown","Slingshot Butt Throw","Tag-Team Clip","Team Entanglement",
	"Tilt-a-whirl Entanglement","Turnbuckle Wheel Bite","Victory Wringer","Blade Coffee Firewall Arrogant Enchantment","Brush Dominator","Carburator Ray","Cold Empowered Edge Diarrhea","Day Bureaucratic Shine","Domination MST3K Rebirth",
	"Electronica Spin","Elixir Halitosis","Far Itching","Hokey-Pokey Orbit","Howl Automotive Queen Haribrush","Immortal Vanilla Mash H.R. Lightning","Janitorial Scan","Master Spoon","Mental Tricycle Murdering Snot Grab","Nuclear Complaint",
	"Planetary Insulation Blow","Posedion Reviewer Snare","Quark Stitch","Restraining Snot Circulation","Sage Fork Jungle Insulation","Salvation Soap Health Jalepino Cancellation","Seductress Moronic Modification","Seeing Suppository",
	"Vitality Arrogant Hymn Nailfile","Apex ISO 9001 Tooth","Battling Hairspray","Bodyguard Arrogant Hour Suppository","Brain Automotive Nebula Coffee Kill","Brave Telegraph Bruising Brush","Database Sewing","Deluding Tile Defender Stir-fry",
	"Face-Time Crash","Finger Mascara","Hairspray Device","Hellish Vomit Blazing Cheese Maelstrom","Mashing Accounting Omni Java Avalanche","Mineral Wheelie","Neptune Spoon","Net Jalepino Atom Onion Hypnotism","Obliteration Diarrhea",
	"Roto Stapler","Scan Face-Time Chill Vomit","Seeker Bicycle Floral Souffle","Shearing Stitch","Spy Wheelie","Time Stir-fry","Tooth Annoyance","Walkie-Talkie Carapace","Warding Algebra Root","Bewitching Heavy-Metal Trembling Knitting",
	"Blessed Cufflink","Bolt Nasal Tooth","Delerium Annoyance","Empowered Grapple","Fart Detection","Firey Nostril Cyclone","Fossil Rap Kicking Eyeliner Therapy","Fusion Vanilla Artificial Derivitive Shell","Gleam Arrogant Fissure Surfboard",
	"Heavy-Metal Twist","Hot Spoon Chop","Infinity Garlic Dusk Tape","Kicking Hockey Enlightening Irritation","Leaf Ignorant Boxing Tile Conversion","MST3K Mash","Meteor Tape","Neutron Spit Geo Fork","Rap Carapace","Rap Petrification",
	"Sage Surfboard","Seed Nasal Fight Souffle","Shining Brush Transformation","Vanilla Slaughter","View Annoying Murderer Raspberry Trapper","Bloody Math Sorcery","Cancel Electronica Pitfall Pencil","Crucifix Hokey-Pokey Bastion",
	"Detection Fuzzy-Wuzzy Queen Chocolate Whirlwind","Fire Disorganized Witchcraft Nailfile","Hacking Accounting Pulsing Scotch Submerge","Hankerchief Battery","Hunter Tile Devil Annoyance","Hydro Potato Shiver","Icy Square Blood Fuzzy-Wuzzy Correction",
	"Intergalactic Hairline Ultrasound Java Bash","Invigorating Pencil Club","Laser Nailclipper Medical Division Network","Lovely Mail","Mecha Varicose Meteor Tape","Past Rice Gleaming Kneepad Pulse","Penetrating Coffee Hunter Halitosis",
	"Photon Cocoa Minute Face-Time Eclipse","Repairing Diarrhea Negation","Second Pencil","Slice Massage","Sound Stupid Spiral","Spy Flowchart","Suitor Irritating Influence","Warp Chocolate Mash"
	]
attackPreps = [
	"'s cum deflectors","'s face","'s butt","'s weird, fleshy bit of skin on an otherwise pointy elbow","'s afro","'s taint","'s grundle","'s fleshy fun bridge","'s mom, who then punches their kid in the feels","'s grill","'s balls","'s lack of balls",
	"'s bazongas","'s tittyboobs","'s nosehair","'s discolored underarm flesh","'s ego","'s dickbutt","'s sense of well-being","'s moral judgement","'s 100% all-beef thermometer","'s 70s bush","'s Alabama black snake","'s Alabama mudflap","'s anaconda",
	"'s anal impaler","'s arse","'s arsehole","'s ass","'s ass crack","'s asshole","'s aviation blonde","'s axe wound","'s baby arm","'s baby maker","'s back door","'s back end","'s badly wrapped kebab","'s badonkadonk","'s bald-headed yogurt slinger",
	"'s bald man in a boat","'s ball bag","'s balloon knot","'s ball sack","'s baloney pony","'s bang hole","'s banus","'s baps","'s bat cave","'s bearded clam","'s bearded oyster","'s beaver","'s beefcurtain","'s beef flap","'s Big Booty Judy",
	"'s big Dick and the twins","'s Italian salami","'s birth cannon","'s bittie","'s blower","'s blue waffle","'s bobby dangler","'s bologna pony","'s bolt-ons","'s bon-bon","'s bone","'s boner","'s boob","'s boobage","'s booby","'s boom stick","'s booty",
	"'s bottle blonde","'s box","'s bratwurst","'s bread","'s breasticle","'s broad in the beam","'s broner","'s brown eye","'s brown spider","'s brown star","'s bubble butt","'s bud","'s buju","'s bum","'s bun","'s bunghole","'s buns","'s bush","'s business class",
	"'s bust","'s butt","'s butt crack","'s butt hole","'s caboose","'s cack","'s cake","'s cake hole","'s camel's foot","'s camel toe","'s can","'s candy","'s cans","'s carpet","'s chach","'s cha cha","'s chap","'s charleys","'s charlies","'s cherry",
	"'s chesticles","'s chest puppies","'s chiclets","'s choad","'s choade","'s chocha","'s cho-cho","'s chocolate starfish","'s chode","'s chonch","'s choot","'s chopper","'s chub","'s chubbie","'s chup","'s chut","'s clickers","'s clit","'s clock",
	"'s clown hole","'s clunge","'s cock","'s cock pocket","'s cock rocket","'s cock socket","'s cock tickler","'s coin purse","'s cojones","'s coo","'s cooch","'s coochie","'s cookie","'s coosie","'s cooter","'s cornhole","'s corn hole","'s cornholer",
	"'s cottage cheese","'s cotton mouth","'s crack","'s crispy critter","'s crotchal","'s crotchal area","'s crotchal region","'s crown jewels","'s cuder","'s cum deflectors","'s cum dumpster","'s cunny","'s cunt","'s cunt hole","'s cunt punt","'s cut",
	"'s cuts","'s cutty","'s cut up","'s 'c' word","'s D","'s dangler","'s D&B","'s deez nutz","'s dick","'s dick beaters","'s dick smalls","'s ding","'s ding-a-ling","'s ding dong","'s dingis","'s dinker","'s dinky","'s dipstick","'s disco stick",
	"'s do","'s doder","'s does the carpet match the drapes","'s dogs","'s doinker","'s dome","'s domepiece","'s dong","'s donk","'s dookie maker","'s dork","'s downstairs","'s drapes","'s DSL","'s D, the","'s D train","'s duff","'s dunlop","'s earboob",
	"'s e-peen","'s equipment","'s family jewels","'s fanny","'s fatty","'s faux hawk","'s feeder","'s femmullet","'s finger","'s fire belly","'s fire crotch","'s fish taco","'s five o'clock shadow","'s flange","'s flavor-saver","'s fleshy fun bridge",
	"'s floater","'s freckle","'s fringe","'s FRO","'s front","'s front bottom","'s fuck hole","'s funbags","'s fun bags","'s FUPA","'s fur burger","'s fur pie","'s gam","'s gap","'s garbage","'s Gary","'s gash","'s gazonga","'s gazongas","'s gazunga","'s gear",
	"'s gender bits","'s general, two colonels","'s get it up","'s ghetto booty","'s ghetto booty brush","'s giggleberry","'s giggle stick","'s girls","'s girls, the","'s glute","'s gob","'s gock","'s gonad","'s gooch","'s gouch","'s gourd","'s grapes",
	"'s grass on the field","'s grill","'s growler","'s grundel","'s grundle","'s guns","'s gunt","'s gut scuff","'s gut wrench","'s hail damage","'s hair burger","'s hair pie","'s hairy axe wound","'s ham flap","'s ham flower","'s ham wallet","'s hanger",
	"'s happy trail","'s hard-on","'s hat","'s hatch","'s hatchet wound","'s hatch, the","'s hat hair","'s head","'s headlights","'s head top","'s helmet","'s Hershey Highway, the","'s high-beams","'s hockey cocky","'s hog","'s honker","'s hooded",
	"'s hooded lady","'s hoo-hoo","'s hooter","'s horse's petute","'s hotdog","'s hot pocket","'s hung","'s IBT","'s ill na-na","'s incision","'s jimmy","'s johnson","'s John Thomas","'s joystick","'s jug","'s juggies","'s juggy tits","'s juicy","'s junk",
	"'s junk in the trunk","'s jute","'s kahuna","'s keister","'s kielbasa","'s kitty","'s Kiwi","'s knackers","'s knap sack","'s knob","'s kooch","'s kooter","'s kuder","'s lady boner","'s lady garden","'s landing strip","'s lid","'s lip","'s lock",
	"'s locks","'s love cave","'s love muscle","'s love shaft","'s love stick","'s love taco","'s lunchbox","'s lunchmeat","'s lungs","'s main vein","'s mammaries","'s man boob","'s mangina","'s manhood","'s man in the boat","'s man in the boat, the",
	"'s man muscle","'s map","'s master of ceremonies","'s matako","'s meat and two veg","'s meat curtains","'s meat flap","'s meat popsicle","'s meat thermometer","'s meatwallet","'s meat wallet","'s melon","'s member","'s merkin","'s middle leg","'s mind",
	"'s minge","'s mipple","'s Missouri Compromise","'s mo","'s moneymaker","'s money maker","'s monster","'s moob","'s moose knuckle","'s mosquito bites","'s mow the lawn","'s Mr. Happy","'s Mr. Winky","'s muff","'s muffin","'s muffin top","'s mug","'s mullet",
	"'s mussy","'s naa-naa","'s nads","'s na-na","'s nappy","'s nappy dugout","'s nard","'s nards","'s naturals","'s naughty pillow","'s neden","'s ninja foot","'s nip","'s nookie","'s nose job","'s nuggets","'s nut","'s nuts","'s nut sack","'s old dirt road, the",
	"'s ol' one-eye","'s one-eyed monster","'s one-eyed snake","'s one-eyed trouser snake","'s (one's) ass","'s (one's) face","'s onion","'s open wound","'s o-ring","'s outie","'s P","'s package","'s packer","'s pack of franks","'s pair","'s patootie","'s patz",
	"'s pecker","'s peen","'s pee pee","'s peeper","'s peepers","'s peeter","'s Peter","'s Ph.D","'s pickle","'s piece","'s pie hole","'s pineapple","'s pink","'s pink canoe","'s pink sausage wallet","'s pink taco","'s pink tractor beam",
	"'s pink velvet sausage wallet","'s pins","'s piss flaps","'s plonker","'s plum","'s pocket rocket","'s pokie","'s polaroid","'s pole","'s pookie","'s poon","'s poonaner","'s poonani","'s poontang","'s poon tang pie","'s poop chute","'s pooper","'s pootang",
	"'s poo tang","'s pooter","'s pootie tang","'s pop a chub","'s pork sword","'s pressed ham","'s prick","'s prison purse","'s private parts","'s privates","'s promised land, the","'s pube","'s puckered brown eye, the","'s puckered starfish","'s pud",
	"'s puffy","'s punani","'s punanni","'s puppies","'s purple-headed soldier","'s purple headed solider man","'s purple-headed warrior","'s puss","'s pussy","'s putang","'s pu-tang","'s putz","'s quif","'s quiff","'s quim","'s quivering mound of love pudding",
	"'s rack","'s rear","'s roadkill","'s roast beef","'s roast beef curtains","'s rocks","'s rod","'s rug","'s rump","'s Russell the love muscle","'s rusty bullet hole","'s sack","'s salami","'s sausage","'s schlong","'s schlort","'s schmeckel","'s schnoz",
	"'s schnozz","'s schwartz","'s sconge","'s seventies bush","'s shaft","'s shed","'s shit box","'s shitter","'s shlittle","'s shlong","'s shrinkage","'s sideboob","'s six pack","'s skin flute","'s skull","'s skull cave","'s skullet","'s skullett","'s slit",
	"'s smush mitten","'s snatch","'s snizz","'s snotlocker","'s soggy box","'s soul patch","'s soup coolers","'s sprained vagina","'s stache","'s starfish","'s stash","'s steamin' semen roadway","'s stem","'s stems","'s stiff","'s stiffie","'s stiffy",
	"'s strawberry creams","'s swamp nuts","'s sweater meat","'s sweater puppies","'s taint","'s tallywacker","'s tallywhacker","'s tally whacker","'s tampon tunnel","'s T and A","'s tang","'s tat","'s tata","'s ta-ta","'s tent pole",
	"'s carpet that matches the curtains","'s carpet that matches the drapes","'s thick","'s thing","'s third leg","'s THO","'s throbber","'s tiggobitties","'s tig ol' bitty","'s tig old bitty","'s tits","'s titty","'s tonsil tickler","'s tool","'s tooshy",
	"'s towhead","'s tracts of land","'s trap","'s trim","'s tripod","'s trouser meat","'s trouser snake","'s trunk","'s tube steak","'s tuchus","'s tuckus","'s tummy","'s tunnel of love","'s turd cutter","'s tush","'s tushie","'s tushy","'s twat","'s twig",
	"'s twig and berries","'s twigs and berries","'s twins, the","'s twitchet","'s twitter","'s two-hole","'s underboob","'s unit","'s V","'s vadge","'s vag","'s vagine","'s vagoo","'s vajayjay","'s va-jay-jay","'s vajizzle","'s vertical smile","'s wang",
	"'s wanker","'s wankie","'s wedding tackle","'s wee","'s weenie","'s wee wee","'s weiner","'s wetware","'s whang","'s whisker biscuit","'s whiskey dick","'s whispering eye","'s whoopie cakes","'s who who dilly","'s wiener","'s willie","'s willy","'s winky",
	"'s wizard sleeve","'s woo","'s wood","'s woogit","'s word hole","'s wugget","'s wuss","'s yabo","'s yam bag","'s yap","'s yogurt slinger","'s yoo-hoo","'s yuck mouth","'s zubra"
	]
magicSpells = [
	"Ball of Stomach Upset","Bile Shield","Bind Ramen Fairy","Burning Ritual of Sunburn","Cosmic Evocation of the Onion Dip Fairy","Dark Incantation of Bad Hair","Dominate Milkmaids","Dread Ritual of the Schoolteacher","Extra-Planar Bolt of Impoliteness",
	"Great Rite of the Boybands","Hermetic Pornography Bolt","Infernal Invocation of Diarrhea","Invoke Baldness","Spray of Inconvenience","Unbelievable Enchantment of the Yarn Demon","Dispell Whining","Dread Cabbage Spout","Dread Ritual of Steak Sauce",
	"Etheral Incantation of the Pornography Elemental","Globe of Fertlizer","Grand Glob of Toejam","Grand Globe of Persperation","Great Rite of Flatulence","Heavenly Spell of Toothpaste","Ice Cream Disc","Magical Spell of the Poser","Overwhelming Curse of Belching",
	"Prismatic Torus of Nose Picking","Ray of Yogurt","Spank Chimneysweep","Astrological Ceremony of the Dandruff Demon","Cosmic Sawdust Globe","Cure Drunkeness in Boyband","Holy Enchantment of the Geek","Induce Impoliteness","Infernal Ball of Nervousness",
	"Invisibility to Champaigne Entity","Luminous Assault of Bacon","Luminous Ceremony of the Lounge Singers","Prismatic Rite of Salivation","Spank Toejam Golem","Spastic Invocation of Fertlizer","Spastic Ritual of Athlete's Foot","Talk to Babysitter",
	"Torus of Peanut Butter","Alchemical Bolt of Warts","Armor of Bad Taste","Assault of Toothpaste","Communicate with Raver","Cosmic Evocation of Cowlicks","Cotton Candy Assault","Curse of Toejam","Cursed Spell of Ranting","Dandruff Aura",
	"Hellish Armor of Toothpaste","Hellish Evocation of Baldness","Invoke Annoyance","Magical Spell of the Wrestler","Prismatic Invocation of Ranting","Sorcerous Invocation of the Manicurist","Astonishing Spell of Juice","Cabalistic Ceremony of the Milkmaids",
	"Conjure Panhandlers","Cosmic Detergent Cage","Create Salivation in Milkmaids","Cure Drooling in Cobbler","Cure Irregularity in Panhandlers","Cursed Ceremony of the Clown","Dispell Fanboy","Extra-Planar Globe of Back Pain","Occult Erruption of Bad Hair",
	"Sorcerous Evocation of Fertlizer","Talk to Goth","Torus of Incontinence","Wall of Hemorrhoids","Arrows of Kingly Wind","Assault of Unknowable Dust","Ball of Darkness","Blasphemous Ceremony of the Haunted Chameleon","Bodily Axes of Metal",
	"Bones of Cursed Silver","Ceremony of Kill Hearers","Circle of Ancient Levitation","Destroyer's Desire","Divine Divination of the Portable Vestment","Fish Killing","Hypnotise Sadistic Barbarians","Keen Storms of Reflection","Rite of Kill Golem",
	"Sly Insect's Evocation of Excellence","Sound Arrows","Spectral Incatation of Light and Worth","The Blessed Rune of the Benevolent Tritons","The Eight Workings of Eagle Control","The Shackle of Mud","The Uncountable Sorceries of the Animated Gate",
	"Thinkers' Circle of Diamond","Torch of Hellish Light","Victory Conjuration","Working of Silver and Caring","Air Transformation","Arrow of Bone","Blessed Brilliance","Caretaker's Purity","Casting of Greed","Conjure Opening","Control Animals",
	"Divination of Cowardice","Elf's Timelessness","Embossed Walls","Energy Transformation","Exalted Security","Green Shields","Humanoid Calling","Hypnotise Monk","Magma Control","Nets of Diamond","Perfect Necromancy","Rings of Lightning","Rite of Carnage",
	"Sea Serpent Seduction","Silencer's Desire","Silencer's Lust","The Club of Destroyers","The Vestment of Lizards","Adamantine Net","Blessed Displacement","Clear Barrier","Copper Hail","Energy Alteration","Evocation of Blending","Falsehood Conjuration",
	"Healing Deflection","Hex of Alteration","Humanoid Summoning","Magma Alteration","Mana Aura","Negate Force","Ornate Nets","Perfect Purity","Portal Envenoming","Quester's Courage","Rite of Ooze","Serpents' Ease","Soldiers' Benevolence","The Cloak of Nothing",
	"The Lantern of Eagles","The Temple of Eagles","Time Negation","Worldly Evocation","Angry Lizards' Sigil of Haunting","Aquatic Rite of Control Crusader","Blessed Sigil of Thought and Corruption","Calling of Become Savage Constructor",
	"Celestial Chant of the Happy Knight","Deadly Rite of Seek Triton","Deathly Working of Seek God","Drunken Ruler's Working of Thought","Imperial Ceremony of the Jagged Lanterns","Infamous Thinkers' Sigil of Leadership","Lawful Hex of Nothing and Fortune",
	"Lesser Witchery of Summon Strangler","Saint's Rune of Bronze and Dexterity","Serene Gibberer's Rite of Absorbing","Sigil of Seek Just Humanoids","Sigil of Slay Divinities","Studious Cats' Incatation of Insanity","The Disrupting Witchery of the Sadistic Knight",
	"The Five Conjurations of the Strong Chime","The Monstrous Ritual of the Monstrous Elf","The Perfect Evocation of the Sagely Defenders","The Six Abjurations of Berserker Calling","The Two Disrupting Spells of Charisma",
	"The Uncountable Illusions of Dwarf Summoning","Ultimate Ritual of Transform Flesh","Abjuration of Seek Miserly Saints","Chaotic Invocation of the Infamous Insect","Elemental Abjuration of Blocking and Barbarism","Ethereal Calling of Seek Wizard",
	"Glamour of Become Gravedigger","Glamour of Summon Dwarf","Greater Glamour of the Barbaric Wyrm","Greater Invocation of Voidness and Virtue","Haunted Priestess's Invocation of Ether","Marvelous Divination of Ice and Lineage","Ritual of Kill Gravediggers",
	"Soldiers' Exorcism of Crystal and Security","Spiritual Casting of the Icy Cloaks","The Eighty Chants of the Howling Moon","The Five Evocations of Slime Absorbtion","The Forty Incatations of Triton Summoning","The Ghostly Divination of the Serene Invokers",
	"The One Hundred Glamours of Diamond Deflection","The One Thousand Charms of Slime Conjuration","The One Thousand Divinations of Cat Hypnotism","The Thirty Workings of Bronze Transformation","Triton's Calling of Mana and Glibness",
	"Ultimate Rune of Ooze and Ease","Witchery of Slay Compassionate Golem","Wonderful Witchery of Alertness and Virtue","Abyssimal Glamour of Sapphire and Deflection","Curse of Call Cunning Felines","Glorious Charm of the Cowardly Triton",
	"Great Chant of the Sadistic Stranglers","Haunter's Working of Diamond and Barbarism","Hellish Casting of the Spined Shiv","Hex of Control Kingly Artist","Illuminated Chant of Stone and Splendor","Incatation of Become Sadistic Ghost",
	"Innocent Crafter's Illusion of Acid","Lesser Evocation of the Innocent Summoner","Past Spell of the Just Invokers","Ruthless Summoner's Divination of Lightning","Savage Divination of Control Fire","Spell of Seduce Generous Monster",
	"Strangler's Ritual of Crystal and Insanity","The Fine Ceremony of the Greater Masters","The Forty Workings of Drake Killing","The Infinite Witcheries of Ooze Negation","The One Hundred Glamours of Darkness Alteration",
	"The One Thousand Chants of the Ornate Grail","The Twenty Rituals of Fish Control","The Twenty Spells of the Metallic Goblet","The Uncountable Ceremonies of Sapphire Deflection","The Wonderful Abjuration of the Ultimate Dragon"
	]
magicInvocations = [
	"By Fiendish Liaclyly!","By Riamulia!","By Sacred Vistoc!","By The Chior Of Piutipr!","By The Flaming Stars Of Paiolal!","By The Hearts Of Ymeasa!","By The Insect Of Tutelviu!","By The Laughter Of Amiolary!","By The Maw Of Cymnates!",
	"By The Obsidian Moor Of Zanar!","By The Pure Band Of Vithaba!","By The Stones Of Bopet!","I Call Upon The Legendary Canyon Of Ylcy-list!","I Call Upon The Scrolls Of Strong Nenegora!","I Evoke The Purity Of Gdo-led!","By Rnege-urnt!","By Vimeure!",
	"By Zul'ethrteu And Its Eight Eagles!","By The Bowels Of Dore-deteu!","By The Horns Of Wianioi!","By The Perphats Of Leresyla!","By The Eight Fins Of Xyicta!","By The Eight Locks Of Cthepalc!","By The Infinite Candles Of Utitand!",
	"By The Ten Necropoli Of Olic-thar!","By The Three Seas Of Donytolc!","I Call Upon The Chiors Of Pa'gaidi!","I Call Upon The Faces Of Quntomeu!","I Evoke The Glorious Sky Of Fa'reora!","I Invoke The Six Sanctums Of Sm'untemo!","By Horrible Zerpa!",
	"By Rt'hymene!","By The Blood Of Dilurpid!","By The Celestial Scrolls Of Pholago!","By The Cliff Of Zesioeip!","By The Horn Of Zoroleso!","By The Plague-ridden Congregation Of Teneoror!","By The Twisted Angels Of Kruleus!","By The Whip Of Illuminated Qurthar!",
	"By The Eight Portals Of Ortana!","By The Five Candles Of Luminous Rselop!","By The One-thousand Tails Of Pa'pilchiu!","I Call Upon The Omniscience Of Th'oreusi!","I Evoke The Ruby Scrolls Of Xychyme!","I Evoke The One-thousand Gauntlets Of Zamaroei!",
	"By The Bloody Battlefield Of Phemel!","By The Centaurs Of Bat-egu!","By The Diamond Stones Of Elilidan!","By The Horns Of Eutumen!","By The Maw Of Brysi!","By The Rings Of Zobi-labu!","By The Schemes Of Osusa!","By The Swarms Of Fagazeda!",
	"By The Six Cloaks Of Ulun-eusum!","By The Ten Locks Of Hunavian!","By The Two Tails Of Qurphois!","I Call Upon The Stones Of Zonegu!","I Invoke The Evil Sanctum Of Poeicyro!","I Invoke The Red Roof Of Xyles!","I Invoke The Words Of Panorona!","By Cymum!",
	"By Secret Ususura!","By The Adroitness Of Xenaten!","By The Evil Griffons Of Ylipprsa!","By The Intellect Of Ncertepe!","By The Key Of Pussiant Vit-hyt!","By The Luminous Sky Of Legesag!","By The Spectral Squadron Of Pylurgd!","By The Stones Of Ponophai!",
	"By The Thirst Of Ylol-viur!","By The Nine Arrows Of Legendary Pete'ipeu!","By The Three Bells Of Devout Jonaelus!","I Call Upon The Arrow Of Saintly Rpiurti!","I Call Upon The Tooth Of Oteranes!","I Invoke The Rage Of Geu-mol!","By Devout Nic-ylil!",
	"By The Beasts Of Danane!","By The Calmness Of Xetare!","By The Evil Ruins Of Opelic!","By The Hope Of Joloicl!","By The Lake Of Ysaioemu!","By The Pure Woodland Of Rybeleth!","By The Vorticies Of Yronesel!","I Call Upon The Sickness Of Beur'odular!",
	"I Call Upon The Unholy Maze Of Yteu-nem!","I Evoke The Sands Of Wulum!","I Evoke The Scheme Of Wonalul!","I Evoke The Five Halls Of Lvi'usic!","I Invoke The Bones Of Zeodor!","I Invoke The Wisdom Of Jolius!","By Brilliant Nadymure!",
	"By The Chiors Of Icth'oiule!","By The Claws Of Istautei!","By The Domain Of Ceteic!","By The Heart Of Xyrauser!","By The Keep Of Wasured!","By The Lunacy Of Luleolil!","By The Sanctums Of Panti!","By The Shamans Of Fan-cel!","By The Tomes Of Nelc'emagum!",
	"By The Undying Souls Of Negut!","By The Third Regiment Of Krtho!","I Call Upon The Mountain Of Teriu-nala!","I Call Upon The Mysterious Griffon Of Ranistho!","I Invoke The Sickness Of Ompri!"
	]
magicRituals = [
	"Angels' Incantation of the Unknown Instrument","Blind Messiah's Abjuration of the Words of Secrets","Bloodstained Evocation of Oubliettes","Ceremony of Chains","Conjuration of the Devils of Labyrinths","Crooked Summoning of Eternal Labyrinths",
	"Crystal Abjuration of Eight Devils","Decrepid Enchantment of Disorder","Ethereal Communion of Desecrated Tombs","Evil Conjuration of the Saint of Bones","Infinite Transfiguration of the Forbidden Beasts of Ossuaries","Outer Rite of the Devil",
	"Primal Rite of Disruption","Profane Monsters' Conjuration of Heaven","Sacrament of the Souls of Vorticies","Sacrifice of the Arch-demon","Shadowed Enchantment of the True Bone","Silent Monsters' Evocation of the Shield of Blood",
	"Unloving Kings' Ritual of Damnation","Working of Warriors","Abjuration of the Wind of Madness","Consuming Sacrifice of the Beasts of Snares","Deadly Sacrament of Snares","Evocation of the Unborn Angel","Hellish Evocation of the Cursed God",
	"Horrible Working of the Lurking Spirit","Icy Conjuration of the Black Curse","Knights' Transfiguration of Wickedness","Lost Summoning of the Terrible Seraphim","Princes' Conjuration of the Haunted Sword","Profane Conjuration of Ghostly Queens",
	"Royal Sacrament of the Graves of Fate","Sinful Transfiguration of the Gray Church","Summoning of the Bones of Unholiness","Transfiguration of Silent Princes","Transfiguration of the Lost Wraiths of Suffering","Unspeakable Conjuration of the Self-renewing Bone",
	"Unthinkable Ceremony of Pain","Working of the One-Hundred Demons of Cenotaphs","Working of the Swords of Decay","Abjuration of the Slaying Battlefield","Accursed Messiah's Transfiguration of Edges","Bloody Sacrifice of Solitude",
	"Dreaming Saint's Ritual of Deception","Eternal Abjuration of the Seraphim of Flesh","Incantation of the Divnity","Infernal Wraith's Conjuration of Silence","Invocation of the Burning Cenotaph","Low Transfiguration of the Stalking Prince",
	"Mystic Rite of the Aeon of Suffering","Profane Ritual of the Soul of Blades","Sacrament of the Three Lords of Materials","Sacrifice of Shadows","Seraphims' Transfiguration of the Slaying Word","Slaying Abjuration of the Vision of Agony",
	"Tortured Messiah's Ritual of the Graves of Deception","Transfiguration of the Spirit","Unknowable Ritual of Faceless Seraphim","Unthinkable Communion of the Prince of Mazes","Working of Decrees","Abjuration of the God",
	"Accursed Beast's Transfiguration of the Rune of Doom","Conjuration of Ghastly Ossuaries","Consuming Sacrifice of Heaven","Demonic Rite of the Hunting Arch-angels of Madness","Ever-changing Transfiguration of Ancestral Knives",
	"Forgotten Working of the Mad Angel","Foul God's Sacrifice of Winds","Ghostly Demon's Ceremony of Wards","Ghosts' Sacrament of Royal Ossuaries","Invocation of Terrifying Bones","Princesses' Conjuration of Black Storms","Queens' Working of the Caverns of Misery",
	"Rite of Blackness","Ritual of Thirteen Fiends","Sacrifice of the Labyrinth of Heaven","Saints' Ritual of Agony","Silent Communion of the Lurking Demigod","Slaying God's Invocation of the Monoliths of Wickedness","Transfiguration of the Sinful Demon",
	"Abjuration of the Curse of the Apocalypse","Ancestral Transfiguration of the Damned Seraphim of Mazes","Avatars' Evocation of Silence","Bloodstained Communion of the Sulphurous Knife","Communion of the Grave of the Apocalypse",
	"Consuming King's Sacrifice of Solitude","Faceless Bane's Transfiguration of the Oubliettes of Unholiness","Forgotten Evocation of the Castles of Omens","Foul Sacrifice of the Eleven Messiahs of Annihilation","Knights' Invocation of Terrible Shields",
	"Living Lady's Enchantment of Gray Labyrinths","Princes' Summoning of Flesh","Queens' Evocation of Hopelessness","Ritual of Purgatory","Ritual of the Evil Hour","Ritual of the Soulless Saint of Doom","Spectral Working of the Decrees of Foulness",
	"Spectres' Sacrament of Deception","Terrifying Enchantment of the Eleven Ladies of Runes","Wraiths' Working of Falsehood","Abjuration of the Ghastly Messiah of Battlefields","Bloody Ritual of Arch-demons","Ceremony of the Fiend of Bones",
	"Communion of One-Hundred Foul Messiahs","Cursed Sacrifice of the Dreaming Devil of Suffering","Demons' Enchantment of the Abyssimal Sword","Dreadful Fiend's Evocation of Unknowable Cairns","Dreadful Goddesses' Abjuration of Necromantic Blades",
	"Evocation of Black Caverns","Evocation of Burning Pits","Goddesses' Communion of the Forbidden Decree","Invocation of the Five Fiends of Shadows","Legendary Sacrifice of the Curses of Agony","Lost Spirits' Invocation of the Bone of Omens",
	"Sacrifice of Shadowy Mazes","Sacrifice of the Caverns of Madness","Saints' Rite of Days","Slaying Gods' Ceremony of the Snares of Madness","Transfiguration of Twelve Warriors","Unknown Enchantment of Purgatory","Bloody Working of Visions",
	"Conjuration of the Grasping Bane","Devils' Working of Unthinkable Vorticies","Ebony Ceremony of the Cairns of Misery","Enchantment of Arch-angels","Enchantment of Churches","Enraged Prince's Conjuration of Misery","High Summoning of the Maze of Desolation",
	"Horrible Conjuration of the Hateful Warrior of Shadows","Icy Transfiguration of the Edges of Annihilation","Infernal Demigod's Ritual of Graves","Invocation of the Crooked Word","Sacrament of Caverns","Sacrifice of Gods","Shadowed Conjuration of Decrepid Aeons",		"Slaying Sacrament of Doom","Summoning of Warped Omens","Transfiguration of Devouring Saints","Transfiguration of Wards","Unspeakable Transfiguration of the Lost Devil","Angry Lord's Sacrament of Disorder","Avatars' Communion of the Grand Castle",
	"Communion of the Sinner of Disorder","Cursed Ceremony of the Monsters of Ossuaries","Decrepid Abjuration of Deadly Winds","Devouring Ceremony of the Aeons of Suffering","Dreaming Queens' Summoning of Purgatory","High Knights' Incantation of the Dark Bone",
	"Knights' Ceremony of Black Edges","Lonesome Knight's Sacrifice of Blackness","Lonesome Seraphims' Evocation of the Low Blade","Mysterious Evocation of the Crystaline Age","Ritual of the Divnities of Pain","Sacrament of the Instruments of Flesh",
	"Self-renewing Abjuration of Days","Sinners' Sacrament of Omens","Stalking Divnity's Ceremony of the Cairn of Desolation","Unspeakable Summoning of the Wraiths of Annihilation","Warped Bane's Ritual of Confusion","Warriors' Abjuration of the Day of Annihilation"
	]
#-- Done 

#-- Initialize functions

def getMaxHPByLevel(lvl):
	# This gets the max HP by level.
	# It starts at 20 for level 1, and goes up by 5 for each level.
	maxhp = (lvl + 15) + ((lvl * 2) * 2)
	return maxhp

def critChance(p1,p2):
	seed = int(time.time() * os.getpgid(0))  # Get a random number based on the current time, then multiply it by the current process ID.
	critchance = ((seed * (xOrShift())) * 246) % 100 # Multiply it by some large numbers, mod it by 100.  This returns a number between 0 and 99
	if FIGHT_VERBOSE: 
		log(p1,p2,"CRIT CHANCE CALCULATION:\n------------------\nSeed = unix time * the python process id = {0}".format(seed))
		log(p1,p2,"Crit Chance = seed * (an xOrShift * 246) % 100 = {0} * (xOrShift * 246) % 100 = {1}".format(seed,critchance))
		log(p1,p2,"If Crit Chance < 3 (3% of the time), it crits.")
	if critchance < 3: # 3% chance of returning a crit, essentially based on when the user attacked.
		if FIGHT_VERBOSE: log(p1,p2,"Crit!!")
		return 1
	if FIGHT_VERBOSE: log(p1,p2,"No crit")
	return 0

def getRandomItem():
	seed = int(time.time()  * os.getpgid(0)) + xOrShift() # Set the seed for the itemlist
	randomItems = []
	itemCat = (seed % 4) + 1 # Get the item category
	itemChance = ((seed + (xOrShift() * time.time()) + 1) % 100)
	with open('equipmentlist','r') as f:
		lines = f.readlines()
		f.seek(0)
		for line in lines:
			if line.startswith('0' + str(itemCat)):
				itemNum = line.split(' - ')[0]
				lineParts = line.split(' - ')[1].split('/')
				if int(lineParts[1]) > itemChance:
					randomItems.append(itemNum)
	f.close()
	if len(randomItems) == 0: return False
	return randomItems

def getItemByItemNo(itemno):
	lineParts = []
	with open('equipmentlist','r') as f:
		lines = f.readlines()
		f.seek(0)
		for line in lines:
			if line.startswith(itemno):
				lineParts = line.split(' - ')[1].split('/')
	f.close()
	if len(lineParts) == 0: return False
	return lineParts

def updateInventory(person,itemno):
	with open('inventories','r+') as f:
		wroteline=0
		lines = f.readlines()
		f.seek(0)
		for line in lines:
			if line.split('/')[0].lower() == person.lower():
				line = line.strip('\r\n') + ',{}\r\n'.format(itemno)
				wroteline=1
			f.write(line)
		if wroteline == 0:
			f.write('{0}//{1}\r\n'.format(person,itemno))
	f.close()

def equipItem(person,itemno):
	stats = getFighterStats(person)
	with open('inventories','r+') as f:
		updated=0
		lines = f.readlines()
		f.seek(0)
		for line in lines:
			if line.split('/')[0].lower() == person.lower():
				if itemno[0:2] != "04":
					for itemId in line.split('/')[1].split(','):
						if itemno[0:2] == itemId[0:2]:
							updated = 3
							f.write(line)
							continue
				else:
					accCount = 0
					for itemId in line.split('/')[1].split(','):
						if itemno[0:1] == itemId[0:1]:
							accCount += 1
						if accCount == 2:
							updated = 4
							f.write(line)
							continue
				if itemno in line.split('/')[2]:
					if updated == 0:
						equippedItems = line.split('/')[1]
						unequippedItems = line.split('/')[2]
						f.write('{0}/{1},{2}/{3}\r\n'.format(person,equippedItems,itemno,str.replace(unequippedItems,',' + itemno,'').strip('\r\n')))
						itemStats = getItemByItemNo(itemno)
						setFighterStats(fname=person,atk=int(itemStats[2])+int(stats[2]),grd=int(itemStats[3])+int(stats[3]),mag=int(itemStats[4])+int(stats[4]),mdef=int(itemStats[5])+int(stats[5]),hp=int(itemStats[6])+int(stats[6]))
						updated = 1
				else: 
					updated = 2
					f.write(line)
			else: f.write(line)
	f.close()
	return updated

def unequipItem(person,itemno):
	stats = getFighterStats(person)
        with open('inventories','r+') as f:
                updated=0
                lines = f.readlines()
                f.seek(0)
                for line in lines:
                        if line.split('/')[0].lower() == person.lower():
                                if itemno in line.split('/')[1]:
                                        equippedItems = line.split('/')[1]
					unequippedItems = line.split('/')[2]
                                        f.write('{0}/{1}/{3},{2}\r\n'.format(person,str.replace(equippedItems,',' + itemno,''),itemno,unequippedItems.strip('\r\n')))
					itemStats = getItemByItemNo(itemno)
                                        setFighterStats(fname=person,atk=int(stats[2])-int(itemStats[2]),grd=int(stats[3])-int(itemStats[3]),mag=int(stats[4])-int(itemStats[4]),mdef=int(stats[5])-int(itemStats[5]),hp=int(stats[6])-int(itemStats[6]))
                                        updated = 1
                                else: 
					updated = 2
					f.write(line)
			else: f.write(line)
        f.close()
        return updated

def getInventory(person):
	inventory = []
	with open('inventories','r') as f:
		lines = f.readlines()
		f.seek(0)
		for line in lines:
			if line.split('/')[0].lower() == person.lower():
				inventory = line.split('/')
	f.close()
	if len(inventory) == 0: return False
	return inventory

def getXPGain(winner,loser):
	p1 = getFighterStats(winner)
	p2 = getFighterStats(loser)
	with open('fightsongoing', 'r') as f:
        	lines = f.readlines()
                f.seek(0)
                for line in lines:
                        initiator = line.split('[-]')[0]
			challenger = line.split('[-]')[1]
			if p1[0] == initiator or p1[0] == challenger:
				turncount = int(line.split('[-]')[4])
	f.close()
	p1lvl = int(p1[1])
	p2lvl = int(p2[1])
	if p1lvl > p2lvl: lesserlvl = p2lvl
	if p1lvl <= p2lvl: lesserlvl = p1lvl
	diff = 1.0
	if p1lvl != p2lvl: diff = float(p2lvl / p1lvl)
	inverteddiff = p1lvl - p2lvl
	p1xp = float(lesserlvl * 2)
	p1xp = ((p1xp * diff) + float(p2lvl) + (turncount / 4) + (xOrShift() % 5))
	p1xp = int(round(p1xp))
	if inverteddiff >= 7:
		inverteddiff = int(round(inverteddiff / 2))
		p1xp = 0
	p2xp = inverteddiff + (xOrShift() % 2) + int(round((turncount / 8)))
	if p2xp < 1: p2xp = 1
	if FIGHT_VERBOSE: 
		log(winner,loser,"{0} XP Gain: ((({1} * 2) + difference fraction) + {2}'s level + number of turns / 4 + XOR Shift % 5) / level difference".format(p1[0],lesserlvl,p2[0]))
		log(winner,loser,"===========> (({0} + {1})) + {2} + {3} / 4 + XOR Shift % 5) / {4} = {5} XP".format(lesserlvl * 2,diff,p2lvl,turncount,diff,p1xp))
		log(winner,loser,"{0} XP Gain: level difference + (XOR Shift % 2) + number of turns / 8 = {2} + XOR Shift % 2 + {3} / 8 = {1} XP".format(p2[0],p2xp,inverteddiff,turncount))
	gains = [p1xp, p2xp]
	return gains

def updateFight(turnswap):
	with open('fightsongoing', 'r+') as f:
		lines = f.readlines()
		f.seek(0)
	        for line in lines:
		        initiator = line.split('[-]')[0]
			challenger = line.split('[-]')[1]
		        who = line.split('[-]')[3]
		        accepted = line.split('[-]')[2]
			turncount = int(line.split('[-]')[4])
			try:
				stopper = line.split('[-]')[6]
			except:
				stopper = ''
			if who.lower() == turnswap.lower() and who.lower() == challenger.lower():
				f.write("{0}[-]{1}[-]{2}[-]{3}[-]{4}[-]{5}[-]{6}".format(initiator,challenger,accepted,initiator,turncount+1,time.time(),stopper))
			elif who.lower() == turnswap.lower() and who.lower() == initiator.lower():
				f.write("{0}[-]{1}[-]{2}[-]{3}[-]{4}[-]{5}[-]{6}".format(initiator,challenger,accepted,challenger,turncount+1,time.time(),stopper))
			else:
				f.write(line)
		f.truncate()
		f.close()

def getFighterStats(name):
	specs = None
	with open('fighters', 'r') as f:
		for line in f:
			x = line.split('[-]')
			if x[0].lower() == name.lower():
				specs = [x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12],x[13],x[14],x[15],x[16],x[17].strip('\r\n')]
			else:
				continue
	if specs:
		return specs
	else:
		return False

def doesItMiss(choice,p1lev,p2lev,p1,p2):
	attackerEquipment = getInventory(p1)
	defenderEquipment = getInventory(p2)
	if attackerEquipment: attackerEquipment = attackerEquipment[1]
	if defenderEquipment: defenderEquipment = defenderEquipment[1]
	diff = int(round(((p1lev - p2lev) / 4) - 0.5)) # For every 4 levels the attacker is above the defender, they get a bonus to their to-hit.
	if diff < 0: diff = 0
	if FIGHT_VERBOSE: log(p1,p2,"Checking if attack misses...")
	seed = int(round(time.time()))
	if choice == 1:
		base = 5 - diff
		if defenderEquipment != False and ('0109' in defenderEquipment or '0301' in defenderEquipment): base = base + 2
		if defenderEquipment != False and ('0304' in defenderEquipment): base = base + 5
		if attackerEquipment != False and ('0406' in attackerEquipment): base = base - 5
		if FIGHT_VERBOSE: log(p1,p2,"BASE for standard attack = 5 - level bonus ====> 5 - {0} = {1}".format(diff,base))
	if choice == 2:
		base = 25 - diff
		if defenderEquipment != False and ('0109' in defenderEquipment or '0301' in defenderEquipment): base = base + 2
                if defenderEquipment != False and ('0304' in defenderEquipment): base = base + 5
                if attackerEquipment != False and ('0406' in attackerEquipment): base = base - 5
		if FIGHT_VERBOSE: log(p1,p2,"BASE for strong attack = 25 - level bonus ====> 25 - {0} = {1}".format(diff,base))
	if choice == 3:
		base = 2 - diff
		if defenderEquipment != False and ('0109' in defenderEquipment or '0301' in defenderEquipment): base = base + 2
                if defenderEquipment != False and ('0304' in defenderEquipment): base = base + 5
                if attackerEquipment != False and ('0406' in attackerEquipment): base = base - 5
		if FIGHT_VERBOSE: log(p1,p2,"BASE for flurry attack = 2 - level bonus ====> 2 - {0} = {1}".format(diff,base))
	if choice == 4:
		base = 12 - diff
		if defenderEquipment != False and ('0109' in defenderEquipment or '0301' in defenderEquipment): base = base + 2
                if defenderEquipment != False and ('0304' in defenderEquipment): base = base + 5
		if FIGHT_VERBOSE: log(p1,p2,"BASE for magic attack = 12 - level bonus ====> 12 - {0} = {1}".format(diff,base))
	seedtwo = xOrShift()
	tomiss = (seed * 246) ** (abs((p2lev - p1lev)) + random.randint(1,4)) % 100
	if FIGHT_VERBOSE: log(p1,p2,"MISS CHANCE = ({0} * 246) ^ (abs(({1} - {2})) + {3}) % 100 = {4}".format(seed,p2lev,p1lev,seedtwo,tomiss))
	if tomiss < base: 
		if FIGHT_VERBOSE: log(p1,p2,"{0} < {1} --> MISS!".format(tomiss,base))
		return 1
	else: 
		if FIGHT_VERBOSE: log(p1,p2,"{0} > {1} --> HIT!".format(tomiss,base))
		return 0
	

def setFighterStats(fname=None,lvl=None,atk=None,grd=None,mag=None,mdef=None,hp=None,xp=None,wins=None,tmpstat=None,tmpbuff=None,atksincelvl=None,satksincelvl=None,fatksincelvl=None,magatksincelvl=None,grdsincelvl=None,mgrdsincelvl=None,lastfought=None):
	if not fname:
		return False
	specs = None
	if hp == 0: hp = -1 	# Ran into a bug where doing exact death damage wasn't doing anything.
	if xp == 0: xp = -1	# This should solve it.  Same for XP.
	
	with open('fighters', 'r') as f:
		for line in f:
			x = line.split('[-]')
			if x[0].lower() == fname.lower():
				if lvl is None: lvl = x[1]
				if atk is None: atk = x[2]
				if grd is None: grd = x[3]
				if mag is None: mag = x[4]
				if mdef is None: mdef = x[5]
				if hp is None: hp = x[6]
				if xp is None: xp = x[7]
				if wins is None: wins = x[8]
				if tmpstat is None: tmpstat = x[9]
				if tmpbuff is None: tmpbuff = x[10]
				if atksincelvl is None: atksincelvl = x[11]
                                if satksincelvl is None: satksincelvl = x[12]
                                if fatksincelvl is None: fatksincelvl = x[13]
                                if magatksincelvl is None: magatksincelvl = x[14]
                                if grdsincelvl is None: grdsincelvl = x[15]
                                if mgrdsincelvl is None: mgrdsincelvl = x[16]
				if lastfought is None: lastfought = x[17]
				specs = [fname,lvl,atk,grd,mag,mdef,hp,xp,wins,tmpstat,tmpbuff,atksincelvl,satksincelvl,fatksincelvl,magatksincelvl,grdsincelvl,mgrdsincelvl,lastfought]
			else:
				continue
	if not specs or specs is None:
		f = open('fighters', 'a')
		f.write("{0}[-]{1}[-]{2}[-]{3}[-]{4}[-]{5}[-]{6}[-]{7}[-]{8}[-]{9}[-]{10}[-]0[-]0[-]0[-]0[-]0[-]0[-]{11}\r\n".format(fname,1,5,5,5,5,getMaxHPByLevel(1),13,0,'',0,''))
		f.close()
		return True
	else:
		with open('fighters', 'r+') as f:
			lines = f.readlines()
			f.seek(0)
			for line in lines:
				x = line.split('[-]')
				if x[0] == specs[0]:
					f.write("{0}[-]{1}[-]{2}[-]{3}[-]{4}[-]{5}[-]{6}[-]{7}[-]{8}[-]{9}[-]{10}[-]{11}[-]{12}[-]{13}[-]{14}[-]{15}[-]{16}[-]{17}\r\n".format(specs[0],specs[1],specs[2],specs[3],specs[4],specs[5],specs[6],specs[7],specs[8],specs[9],specs[10],specs[11],specs[12],specs[13],specs[14],specs[15],str(specs[16]),str(specs[17]).strip('\r\n')))
				else:
					f.write(line)
			f.truncate()
			f.close()
	return True

def levelUp(person):
	p1 = getFighterStats(person)
	currentxp = int(p1[7])
	currentlvl = p1[1]
	equipped = []
	with open('inventories','r') as f:
                updated=0
                lines = f.readlines()
                f.seek(0)
                for line in lines:
                        if line.split('/')[0].lower() == person.lower():
                        	for itemId in line.split('/')[1].split(','):
					if len(itemId.rstrip()) == 4:
						equipped.append(itemId)
	                                	unequipItem(person,itemId)
			else: continue
	setFighterStats(fname=person,lvl=int(currentlvl)+1,hp=getMaxHPByLevel(int(currentlvl)+1))
	results = []
	if int(p1[7]) > 0: return False # This should never happen, but covering all the bases here.
	stats = {'atk':int(p1[11]), 'satk':int(p1[12]), 'fatk':int(p1[13]), 'magatk':int(p1[14]), 'grd':int(p1[15]), 'mgrd':int(p1[16])}
	stats = OrderedDict(sorted(stats.items(), key=lambda t: t[1], reverse=True))
	for i in range(0,3):
		p1 = getFighterStats(person)
		if stats.keys()[i] == 'atk':
			if stats.get('atk') > 0:
				newatk = int(round(int(stats.get('atk')) / 8 + (int(currentlvl) / 3)))
				if newatk < 1: newatk = 1
				setFighterStats(fname=person,atk=int(p1[2]) + newatk)	
				if FIGHT_VERBOSE: log("Increasing Attack by {0}".format(newatk))
				results.append("you attacked a total of {0} times, resulting in an increase in your atk stat from {1} to {2}".format(int(stats.get('atk')),int(p1[2]),int(p1[2]) + newatk))
		elif stats.keys()[i] == 'satk':
			if stats.get('satk') > 0:
				newatk = int(p1[2]) + 2
	                        setFighterStats(fname=person,atk=newatk)
				if FIGHT_VERBOSE: log("Increasing Attack by 2")
	                        results.append("you strong attacked a total of {0} times, resulting in an increase in your atk stat from {1} to {2}".format(int(stats.get('satk')),int(p1[2]),newatk))
		elif stats.keys()[i] == 'fatk':
			if stats.get('fatk') > 0:
				newatk = int(p1[2]) + 1
				newdef = int(p1[3]) + 1
	                        setFighterStats(fname=person,atk=newatk,grd=newdef)
				if FIGHT_VERBOSE: log("Increasing Attack by 1, Defense by 1")
	                        results.append("you flurried a total of {0} times, resulting in an increase in your atk and grd stats by 1 each".format(int(stats.get('fatk'))))
		elif stats.keys()[i] == 'magatk':
			if stats.get('magatk') > 0:
				newatk = int(round(int(stats.get('magatk')) / 8 + (int(currentlvl) / 3)))
				if newatk < 1: newatk = 1
	                        setFighterStats(fname=person,mag=int(p1[4]) + newatk)
				if FIGHT_VERBOSE: log("Increasing Magic Attack by {0}".format(newatk))
	                        results.append("you attacked with magic a total of {0} times, resulting in an increase in your mag stat from {1} to {2}".format(int(stats.get('magatk')),int(p1[4]),int(p1[4]) + newatk))
		elif stats.keys()[i] == 'grd':
			if stats.get('grd') > 0:
				newgrd = int(round(int(stats.get('grd')) / 5 + (int(currentlvl) / 3)))
				if newgrd < 1: newgrd = 1
	                        setFighterStats(fname=person,grd=int(p1[3]) + newgrd)
				if FIGHT_VERBOSE: log("Increasing Defense by {0}".format(newgrd))
	                        results.append("you guarded a total of {0} times, resulting in an increase in your grd stat from {1} to {2}".format(int(stats.get('grd')),int(p1[3]),int(p1[3]) + newgrd))
		else:
			if stats.get('mgrd') > 0:
				newgrd = int(round(int(stats.get('mgrd')) / 5 + (int(currentlvl) / 3)))
				if newgrd < 1: newgrd = 1
	                        setFighterStats(fname=person,mdef=int(p1[5]) + newgrd)
				if FIGHT_VERBOSE: log("Increasing Magic Defense by {0}".format(newgrd))
	                        results.append("you guarded against magic a total of {0} times, resulting in an increase in your mdef stat from {1} to {2}".format(int(stats.get('mgrd')),int(p1[5]),int(p1[5]) + newgrd))
	newxp = int(round((((float(currentlvl) + 1) * 10) * 1.5) + (float(currentlvl) * (float(currentlvl)-1)) + 1))
	with open('inventories','r') as f:
                updated=0
                lines = f.readlines()
                f.seek(0)
                for line in lines:
                        if line.split('/')[0].lower() == person.lower():
                                for itemId in equipped:
					if len(itemId.rstrip()) == 4:
	                                        equipItem(person,itemId.rstrip())
                        else: continue
	if FIGHT_VERBOSE: 
		log("XP to next level = round((player level * 10) * 1.5) + (player level - 1 * player level - 2) + 1")
		log("{0} * 1.5 + ({1} * {2}) + 1 = {3}".format((int(currentlvl)+1)*10,int(currentlvl),int(currentlvl)-1,newxp))
		log("Subtract excess xp from last level gain.")
		log("XP to next level: {0}".format(newxp+currentxp))
	setFighterStats(fname=person,xp=newxp+currentxp)
	return results
			

# The following function was developed from an idea put forth by 
# George Marsaglia.  It is used for all the dice rolls.  From Wikipedia:
#
# Xorshift generators are among the fastest non-cryptographic random number generators requiring minimal code and state. 
# Although they do not pass every statistical test without further refinement, this weakness is well-known and easily amended 
# by combining them with a non-linear function, resulting e.g. in a xorshift+ or xorshift* generator. 
# A naive C implementation of a xorshift+ generator that passes all tests from the BigCrush suite (with an order of magnitude 
# fewer failures than Mersenne Twister or WELL) typically takes fewer than 10 clock cycles on x86 to generate a random number thanks to instruction pipelining.
#
# The following implementation was refined by bgm:
def xOrShift():
	global XA, XB, XC, XD
	e = (XA ^ (XA << 11)) & 0xFFFFFFFFFFFFFFFF
	XA = XB + XA
	XB = XC + XC
	XC = XD + XB
	XD = ((XA ^ (XD >> 19)) ^ (e ^ (e >> 8))) & 0xFFFFFFFFFFFFFFFF
	return XD
# End xOrShift

def rollDice(rolls,sides,p1,p2):
	rolltotal = 0
	rollstr = []
	for i in range(0,rolls):
		roll = ((xOrShift() % sides) + 1)
		rolltotal = rolltotal + roll
		rollstr.append(roll)
	rollstr = " + ".join(map(str, rollstr))
	if FIGHT_VERBOSE: log("Dice Roll: {0}d{1} ---> {3} = {2}".format(rolls,sides,rolltotal,rollstr))
	return rolltotal

def calcDamage(choice,atkstat,defstat,p1lvl,p2lvl,p1,p2):
	diff = p1lvl - p2lvl
	defdiff = 0
	if diff < 0: 
		diff = 0
		defdiff = abs(diff)
	lvlbonus = int(round((p1lvl / 4) - 0.5))
	if lvlbonus < 0: lvlbonus = 0
	if choice == 1: 
		atkroll = rollDice(2+lvlbonus,6,p1,p2)
		defroll = rollDice(2+defdiff,3,p1,p2)
	if choice == 2:
		atkroll = rollDice(5+lvlbonus,4,p1,p2)
		defroll = rollDice(2+defdiff,3,p1,p2)
	if choice == 3:
		atkroll = rollDice(2+lvlbonus,4,p1,p2)
		defroll = rollDice(2+defdiff,3,p1,p2)
	if choice == 4:
		atkroll = rollDice(2+lvlbonus,10,p1,p2)
		defroll = rollDice(2+defdiff,3,p1,p2)
	atk = atkstat + atkroll + ((int(round(time.time())) * os.getpgid(0) + xOrShift()) % 3) + diff
	if FIGHT_VERBOSE: 
		log(p1,p2,"Attack formula: attack + dice roll + (((round(unix time)) * python process ID + xOrShift) % 3) + level difference")
		log(p1,p2,"==============> {0} + {1} + ((unix time * {2} + xorshift) % 3) + {3} = {4}".format(atkstat,atkroll,os.getpgid(0),diff,atk))
	grd = defstat + defroll + ((int(round(time.time())) * os.getpgid(0) + xOrShift()) % 3)
	if FIGHT_VERBOSE: 
		log(p1,p2,"Defense formula: guard + dice roll + (((round(unix time)) * python process ID + xOrShift) % 3)")
		log(p1,p2,"===============> {0} + {1} + ((unix time * {2} + xorshift) % 3) = {3}".format(defstat,defroll,os.getpgid(0),grd))
	dmg = atk - grd
	if FIGHT_VERBOSE: 
		log(p1,p2,"Attack - Defense = {0}".format(dmg))
		if dmg > 0:
			log(p1,p2,"== HIT! ==") 
		else: log(p1,p2,"== Damage too low! MISS! ==")
	return dmg

def resolveAttack(choice,p1,p2,mod=None):
	attacker = getFighterStats(p1)
	defender = getFighterStats(p2)
	if choice == 1: # Standard Attack
		#--
		# Let's increase the total attacks done since last level by one
		# This is to determine what increases next level
		#
		if mod is None: 
			atkcount = int(attacker[11])
			setFighterStats(fname=attacker[0],atksincelvl=(atkcount + 1))
			if FIGHT_VERBOSE: log(p1,p2,"{0} attacked {1}!".format(p1,p2))
		if mod == 2: 
			atkcount = int(attacker[12])
			setFighterStats(fname=attacker[0],satksincelvl=(atkcount + 1))
		if mod == 3:
			atkcount = int(attacker[13])
			setFighterStats(fname=attacker[0],fatksincelvl=(atkcount + 1))
		#--
		if FIGHT_VERBOSE: log(p1,p2,"Resolving attack - {0} (lvl {1}) attacks {2} (lvl {3}):\n-----------------".format(attacker[0],attacker[1],defender[0],defender[1]))
		totalatk = int(attacker[2])
		totaldef = int(defender[3])
		if mod is None: mod = choice
		misschance = doesItMiss(mod,int(attacker[1]),int(defender[1]),attacker[0],defender[0])
		if misschance == 1:
			results = [attacker, defender]
			dmg = 0
			parryChance = (random.randint(1000000000,9999999999) + xOrShift()) % 100
			parrynumber = 2
			if defender[9] == 'grd': parrynumber = 5
			if parryChance < parrynumber:
				if FIGHT_VERBOSE: log(p1,p2,"Parry!")
				dmg = calcDamage(1,int(defender[4]),int(attacker[5]),int(defender[1]),int(attacker[1]),attacker[0],defender[0]) - random.randint(0,4)
		                if dmg < 0: dmg = 2
		                if FIGHT_VERBOSE: log(p1,p2,"{0} parries and does {1} damage to {2}!".format(defender[0],dmg,attacker[0]))
				atkcount = int(defender[11])
	                        setFighterStats(fname=defender[0],atksincelvl=(atkcount + 1))
		                results.append("{0} parries the attack!  {1} damage to {2}".format(defender[0],dmg,attacker[0]))
		                resulthp = int(attacker[6]) - dmg
				if FIGHT_VERBOSE: log(p1,p2,"HP Remaining --==-- {0}: {1}, {2}: {3}".format(attacker[0],resulthp,defender[0],defender[6]))
		                setFighterStats(fname=attacker[0],hp=resulthp)
				#-- Reset the temp stats
		                #
				reset=''
		                setFighterStats(fname=attacker[0],tmpstat=reset,tmpbuff=0)
		                setFighterStats(fname=defender[0],tmpstat=reset,tmpbuff=0)
		                #
				return results
			results.append("{0} swiftly dodges {1}'s attack!".format(defender[0],attacker[0]))
			if FIGHT_VERBOSE: log(attacker[0],defender[0],"Miss!")
			return results
		if attacker[9] == 'atk': totalatk = totalatk + int(attacker[10])
		if defender[9] == 'grd': totaldef = totaldef + int(defender[10])
		#-- Reset the temp stats
		#
		reset=''
		setFighterStats(fname=attacker[0],tmpstat=reset,tmpbuff=0)
		setFighterStats(fname=defender[0],tmpstat=reset,tmpbuff=0)
		#
		results = [attacker, defender]
		dmg = calcDamage(mod,totalatk,totaldef,int(attacker[1]),int(defender[1]),attacker[0],defender[0])
	elif choice == 2: # Strong Attack
		if FIGHT_VERBOSE: log(p1,p2,"{0} elected to try a strong attack!".format(p1))
		results = resolveAttack(1,p1,p2,mod=2)
		return results
	elif choice == 3: # Flurry Attack
		if FIGHT_VERBOSE: log(p1,p2,"{0} elected to try a flurry attack!".format(p1))
                results = resolveAttack(1,p1,p2,mod=3)
		return results
	elif choice == 4: # Magic Attack
                #--
                # Let's increase the total attacks done since last level by one
                # This is to determine what increases next level
                #
                atkcount = int(attacker[14])
                setFighterStats(fname=attacker[0],magatksincelvl=(atkcount + 1))
                #--
                if FIGHT_VERBOSE: log(p1,p2,"Resolving attack - {0} (lvl {1}) casts magic at {2} (lvl {3}):\n-----------------".format(attacker[0],attacker[1],defender[0],defender[1]))
                totalatk = int(attacker[4])
                totaldef = int(defender[5])
                misschance = doesItMiss(choice,int(attacker[1]),int(defender[1]),attacker[0],defender[0])
                if misschance == 1:
                        results = [attacker, defender]
                        dmg = 0
                        parryChance = (random.randint(1000000000,9999999999) + xOrShift()) % 100
			parrynumber = 2
                        if defender[9] == 'mgrd': parrynumber = 5
                        if parryChance < parrynumber:
                                dmg = calcDamage(1,int(defender[4]),int(attacker[5]),int(defender[1]),int(attacker[1]),attacker[0],defender[0]) - random.randint(0,4)
                                if dmg < 0: dmg = 2
                                if FIGHT_VERBOSE: log(p1,p2,"{0} dodges and counters the spell for {1} damage!".format(defender[0],dmg))
				atkcount = int(defender[11])
                                setFighterStats(fname=defender[0],atksincelvl=(atkcount + 1))
                                results.append("{0} dodges the spell and sees and opening to counter!  {1} damage to {2}".format(defender[0],dmg,attacker[0]))
                                resulthp = int(attacker[6]) - dmg
                                setFighterStats(fname=attacker[0],hp=resulthp)
				#-- Reset the temp stats
                                #
				reset=''
                                setFighterStats(fname=attacker[0],tmpstat=reset,tmpbuff=0)
                                setFighterStats(fname=defender[0],tmpstat=reset,tmpbuff=0)
                                #
                                return results
			results.append("{0} dodges {1}'s spell!".format(defender[0],attacker[0]))
			if FIGHT_VERBOSE: log(attacker[0],defender[0],"Miss!")
                        return results
                if attacker[9] == 'mag': totalatk = totalatk + int(attacker[10])
                if defender[9] == 'mdef': totaldef = totaldef + int(defender[10])
                #-- Reset the temp stats
                #
		reset=''
                setFighterStats(fname=attacker[0],tmpstat=reset,tmpbuff=0)
                setFighterStats(fname=defender[0],tmpstat=reset,tmpbuff=0)
                #
                results = [attacker, defender]
                dmg = calcDamage(choice,totalatk,totaldef,int(attacker[1]),int(defender[1]),attacker[0],defender[0])
	elif choice == 5: # Guard 
		if FIGHT_VERBOSE: log(p1,p2,"{0} goes on guard!".format(p1))
		atkcount = int(attacker[15])
                setFighterStats(fname=attacker[0],grdsincelvl=(atkcount + 1))
                setFighterStats(fname=p1,tmpstat='grd',tmpbuff=10)
		attacker, defender = getFighterStats(p1), getFighterStats(p2)
                results = [attacker, defender]
		results.append("{0} takes a defensive stance".format(attacker[0]))
		return results
	elif choice == 6: # Magic Guard
		if FIGHT_VERBOSE: log(p1,p2,"{0} is meditating!".format(p1))
		atkcount = int(attacker[16])
                setFighterStats(fname=attacker[0],mgrdsincelvl=(atkcount + 1))
                setFighterStats(fname=p1,tmpstat='mdef',tmpbuff=10)
                attacker, defender = getFighterStats(p1), getFighterStats(p2)
                results = [attacker, defender]
                results.append("{0} sits down to meditate".format(attacker[0]))
                return results
	else:
		return False

	if critChance(attacker[0],defender[0]) == 1:
		dmg = dmg * 2
		if dmg < 6: dmg = 6
		if FIGHT_VERBOSE: log(p1,p2,"== CRIT! ==")
		if choice != 4: results.append("{0} {1}{2} {3} to {4}{5} for {6} CRITICAL damage".format(attacker[0].lower(),verbage[(random.randint(0,len(verbage)-1))].lower(),qualifiers[(random.randint(0,len(qualifiers)-1))].lower(),attackVerbs[random.randint(0,len(attackVerbs)-1)].lower(),defender[0].lower(),attackPreps[random.randint(0,len(attackPreps)-1)].lower(),dmg))
		else: results.append("{0} mystically moves their hands while shouting \"hear me! {1}! i perform the {2} and cast {3} at my enemy!\" the spell hits for {4} CRITICAL damage".format(attacker[0].lower(),magicInvocations[(random.randint(0,len(magicInvocations)-1))].lower().strip('!'),magicRituals[(random.randint(0,len(magicRituals)-1))].lower(),magicSpells[random.randint(0,len(magicSpells)-1)].lower(),dmg))
	else:
		if dmg > 0: 
			if choice != 4: 
				results.append("{0} {1}{2} {3} to {4}{5} for {6} damage".format(attacker[0].lower(),verbage[(random.randint(0,len(verbage)-1))].lower(),qualifiers[(random.randint(0,len(qualifiers)-1))].lower(),attackVerbs[random.randint(0,len(attackVerbs)-1)].lower(),defender[0].lower(),attackPreps[random.randint(0,len(attackPreps)-1)].lower(),dmg))
			else: 
				results.append("{0} mystically moves their hands while shouting \"hear me! {1}! i perform the {2} and cast {3} at my enemy!\" the spell hits for {4} damage".format(attacker[0].lower(),magicInvocations[(random.randint(0,len(magicInvocations)-1))].lower().strip('!'),magicRituals[(random.randint(0,len(magicRituals)-1))].lower(),magicSpells[random.randint(0,len(magicSpells)-1)].lower(),dmg))
		else:
			dmg = 0
			if choice != 4:	results.append("{0} deflects {1}'s attack!".format(defender[0],attacker[0]))
			else: results.append("{0}'s spell doesnt affect {1}!".format(attacker[0],defender[0]))
			if FIGHT_VERBOSE: log(attacker[0],defender[0],"Deflected!")
	resulthp = int(defender[6]) - dmg
	if FIGHT_VERBOSE: log(attacker[0],defender[0],"HP Remaining --==-- {0}: {1}, {2}: {3}".format(defender[0],resulthp,attacker[0],attacker[6]))
	setFighterStats(fname=defender[0],hp=resulthp)
	if FIGHT_VERBOSE: log(attacker[0],defender[0],"=============================================================")
	return results
