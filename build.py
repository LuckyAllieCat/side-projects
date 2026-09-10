import json, re

ANSWERS = """
about above abuse actor acute admit adopt adult after again agent agree ahead alarm album alert alike alive allow alone along alter angel anger angle angry apart apple apply arena argue arise armor array arrow aside asset avoid awake award aware awful
bacon badge badly baker basic basis beach beard beast began begin being belly below bench berry birth black blade blame blank blast blaze bleed blend bless blind block blood bloom blown blues blunt blush board boast bonus boost booth bound brain brake brand brave bread break breed brick bride brief bring broad broke brook broom brown brush build built bunch burst buyer
cabin cable camel candy cargo carry catch cause cedar chain chair chalk champ chaos charm chart chase cheap check cheek cheer chess chest chief child chill china choir chose chunk cider cigar civil claim clash class clean clear clerk click cliff climb cling clock close cloth cloud clown coach coast cocoa color comet comic coral couch cough could count court cover crack craft crane crash crawl crazy cream creek crept crime crisp cross crowd crown crude cruel crush curve cycle
daily dairy daisy dance dated dealt death debut decay decor delay delta dense depth derby devil diary dirty ditch diver dizzy dodge doing doubt dough dozen draft drain drama drank drawn dream dress dried drift drill drink drive drone drove drown drunk dusty dwell dying
eager eagle early earth eight elbow elder elect elite email empty enemy enjoy enter entry equal equip error essay event every exact exist extra
fable faint fairy faith false fancy fatal fault favor feast fence ferry fetch fever fiber field fiery fifth fifty fight final first fixed flame flash fleet flesh float flock flood floor flour fluid flush focus foggy force forge forth forty forum found frame fraud fresh fried front frost fruit fully funny
gauge ghost giant given glass gleam glide globe gloom glory glove going grace grade grain grand grant grape graph grasp grass grave gravy great greed green greet grief grill grind groan groom gross group grove grown guard guess guest guide guilt
habit happy harsh haste haunt heart heavy hedge hello hence herbs hobby hoist honey honor horse hotel house hover human humor hurry
ideal image imply index inner input irony issue ivory
jelly jewel joint joker jolly judge juice juicy jumbo
karma kayak kneel knife knock known
label labor lance large laser later laugh layer learn lease least leave legal lemon level lever light limit linen liver lobby local lodge logic loose lorry lover lower loyal lucky lunar lunch lying
magic major maker mango manor maple march match maybe mayor meant medal media melon mercy merit merry metal meter midst might minor minus mixed model moist money month moral motor mount mouse mouth movie music
naive nasty naval nerve never newly night noble noise north notch novel nurse
occur ocean offer often olive onion opera orbit order organ other ought ounce outer owner oxide ozone
paint panel panic paper party pasta patch pause peace peach pearl pedal penny perch phase phone photo piano piece pilot pinch pitch pixel pizza place plain plane plant plate plaza plead plush point polar porch pouch pound power press price pride prime print prior prize probe proof proud prove proxy pulse punch pupil purse
quack queen query quest queue quick quiet quilt quirk quite quota quote
radar radio rainy raise rally ranch range rapid ratio raven reach react ready realm rebel refer reign relax relay reply rider ridge rifle right rigid rinse risky rival river roast robin robot rocky rogue roman rough round route royal rugby ruler rural
saint salad salon salty sandy sauce scale scare scarf scene scent scoop scope score scout scrap screw seize sense serve seven shade shake shall shame shape share shark sharp sheep sheer sheet shelf shell shift shine shiny shirt shock shoot shore short shout shown shrug sight silly since sixth sixty skate skill skirt skull slate sleep slice slide slope small smart smell smile smoke snack snake sneak solar solid solve sorry sound south space spare spark speak speed spell spend spent spice spicy spike spill spine spite split spoke spoon sport spray squad stack staff stage stain stair stake stale stamp stand stare start state steak steal steam steel steep steer stern stick stiff still sting stock stole stone stood stool store storm story stout stove strap straw strip stuck study stuff stump style sugar suite sunny super surge swamp swear sweat sweep sweet swept swift swing sword syrup
table taken taste teach tempo tenth thank theft their theme there these thick thief thigh thing think third those three threw throw thumb tiger tight timer tired title toast today token tooth topic torch total touch tough tower toxic trace track trade trail train trait trash treat trend trial tribe trick tried troop truck truly trunk trust truth tulip tutor twice twist
ultra uncle under union unite unity until upper upset urban usage usual utter
vague valid value valve vapor vault vegan venue verse video villa vinyl viral virus visit vital vivid vocal voice voter
wagon waist waste watch water weary weave wedge weigh weird whale wheat wheel where which while white whole whose widen widow width windy witch woman women world worry worse worst worth would wound wrist write wrong wrote
yacht yeast yield young youth
zebra
""".split()

dictionary = set()
with open("/usr/share/dict/american-english") as f:
    for w in f:
        w = w.strip()
        if re.fullmatch(r"[a-z]{5}", w):
            dictionary.add(w)

answers = sorted(set(ANSWERS))
assert all(len(w) == 5 and w.isalpha() for w in answers)
dictionary |= set(answers)
valid = sorted(dictionary)

import hashlib, os
html = open("template.html").read()
html = html.replace("__ANSWERS__", json.dumps(answers)).replace("__VALID__", json.dumps(valid))

# Desktop build: no PWA tags.
open("wordle.html", "w").write(html.replace("__PWA_HEAD__\n", ""))

# Web-app build for GitHub Pages / iPhone home screen.
PWA_HEAD = """<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#121213">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Wordle">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" href="favicon.png">"""
os.makedirs("docs", exist_ok=True)
pwa = html.replace("__PWA_HEAD__", PWA_HEAD)
open("docs/index.html", "w").write(pwa)
# Version the service-worker cache by content hash so updates reach installed phones.
version = hashlib.sha1(pwa.encode()).hexdigest()[:8]
sw = open("docs/sw.js").read()
import re as _re
sw = _re.sub(r'const CACHE = "wordle-[^"]*";', f'const CACHE = "wordle-{version}";', sw)
open("docs/sw.js", "w").write(sw)
print(f"{len(answers)} answers, {len(valid)} valid guesses -> wordle.html + docs/index.html (cache v{version})")
