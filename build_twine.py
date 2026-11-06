# -*- coding: utf-8 -*-
"""
把一份「像写作一样」的 Twine 文稿，编译成单文件 HTML。
引擎：SugarCube 2.37.3（Twine 官方发布的故事格式），使用其 storyFormat 模板。
"""
import json, os, re, uuid, base64, html, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ASST = os.path.join(HERE, 'assets')
_CANDIDATES = ('/tmp/sc/sugarcube-2/format.js',
              os.path.join(HERE, 'format', 'sugarcube-2.37.3', 'format.js'))
FORMAT_JS = next((p for p in _CANDIDATES if os.path.exists(p)), None)
if not FORMAT_JS:
    raise SystemExit('missing format.js: download sugarcube-2.37.3-for-twine-2.1-local.zip '
                     'and unzip format.js into ./format/sugarcube-2.37.3/')
OUT = os.path.join(HERE, '摸猫.html')

# ---------------------------------------------------------------- 引擎模板
raw = open(FORMAT_JS, encoding='utf-8').read()
body = raw[len('window.storyFormat('):].rstrip()
assert body.endswith(');')
tpl_json = body[:-2]
fmt = json.loads(tpl_json)
template = fmt['source']
assert '{{STORY_DATA}}' in template

# ---------------------------------------------------------------- 素材
def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode()

photo_b64 = b64(os.path.join(ASST, 'cat_scene.jpg'))
grain_b64 = b64(os.path.join(ASST, 'grain.png'))

CREDITS = (
    '<div class="credits">'
    '致敬 neongrey《Cat Petting Simulator 2014》——同一个动作，可以做很久。<br>'
    '用 Twine / SugarCube 写成的短篇。图片来自 Unsplash。'
    '</div>'
)
RESTART = (
    '<div class="acts"><<link "再来一次">><<goto "Start">><</link>></div>'
)

# ---------------------------------------------------------------- 文稿
CREDITS = (
    '<div class="credits">'
    '<div class="lang-zh">'
    '致敬 neongrey《Cat Petting Simulator 2014》\u2014\u2014同一个动作，可以做很久。<br>'
    '用 Twine / SugarCube 写成的短篇。图片来自 Unsplash。'
    '</div>'
    '<div class="lang-en">'
    'After neongrey\u2019s <i>Cat Petting Simulator 2014</i> \u2014 one action, and you can do it a long time.<br>'
    'A short piece in Twine / SugarCube. Photograph from Unsplash.'
    '</div>'
    '</div>'
)

RESTART = (
    '<div class="lang-zh"><div class="acts"><<link "再来一次">><<goto "Start">><</link>></div></div>'
    '<div class="lang-en"><div class="acts"><<link "Again">><<goto "Start">><</link>></div></div>'
)

TIMES = '<<set $times to ["03:17","03:21","03:26","03:31","03:37","03:44","03:52","04:01","04:11","04:24","04:40","04:58","05:40"]>>'

P = []

def add(name, zh, en, pre='', post=''):
    text = (pre + '<div class="scene"><<include "页眉">>'
            + '<div class="lang-zh">' + zh + '</div>'
            + '<div class="lang-en">' + en + '</div>'
            + post + '</div>')
    P.append({'name': name, 'text': text})

def acts(pairs, is_en):
    out = ''
    for p in pairs:
        label = p[1] if is_en else p[0]
        pre = p[3] if len(p) > 3 else ''
        out += '<<link "%s">>%s<<goto "%s">><</link>>' % (label, pre, p[2])
    return out

def panel(pairs):
    return ('<div class="lang-zh"><div class="acts">%s</div></div>'
            '<div class="lang-en"><div class="acts">%s</div></div>'
            % (acts(pairs, False), acts(pairs, True)))

INC = '<<include "动作">>'

# --- 开场 ---
add('Start',
    pre=('<<set $t to 0>><<set $pets to 0>><<set $looked to false>><<set $pause to 0>>' + TIMES),
    zh=('<p class="l">凌晨三点十七分。</p>'
        '<p>你醒了。没睁眼。</p>'
        '<p>被子里是热的，被子外面是凉的。暖气片停在半凉的地方，隔一会儿咔一声。</p>'
        '<p>床垫的左边陷下去一块。很轻，像有人放下一只装了东西的塑料袋。</p>'),
    en=('<p class="l">3:17 in the morning.</p>'
        '<p>You are awake. You have not opened your eyes.</p>'
        '<p>Under the blanket it is warm; above it, cold. The radiator stopped somewhere short of warm and clicks once in a while.</p>'
        '<p>The left side of the mattress has sunk a little. Very slightly, as if someone set down a plastic bag with something in it.</p>'),
    post=panel([('睁开眼', 'Open your eyes', '床'),
                ('继续装睡', 'Keep still and pretend', '装睡')]))

# --- 装睡 ---
add('装睡',
    zh=('<p class="l">你没有动。</p>'
        '<p>它在旁边走动。四只脚，一步一步，被子跟着轻轻起伏。</p>'
        '<p>走近了。停下。</p>'
        '<p>有一根胡须碰到你的手腕，弯了一下，又弹回去。</p>'
        '<p>然后是重量——它把自己放下了，在你胸口旁边，隔着一层被子。</p>'
        '<p>它身上有外面的味道：水泥地、雨水、别人家的油烟，还有一点点鱼。</p>'),
    en=('<p class="l">You do not move.</p>'
        '<p>It walks beside you. Four feet, one step at a time, and the blanket rises and falls with it.</p>'
        '<p>Closer. It stops.</p>'
        '<p>A whisker touches your wrist, bends, springs back.</p>'
        '<p>Then weight \u2014 it sets itself down next to your chest, one blanket between you.</p>'
        '<p>It carries the smell of outside: concrete, rain, someone else\u2019s cooking oil, and a little fish.</p>'),
    post=panel([('睁开眼', 'Open your eyes', '床'),
                ('再躺一会儿', 'Lie here a little longer', '装睡二')]))

# --- 装睡二 ---
add('装睡二',
    zh=('<p class="l">你听着它。</p>'
        '<p>它没有动。</p>'
        '<p>过了一会儿，喉咙深处有什么在挪动，很轻的一声。不是叫。</p>'
        '<p>你想到楼下那班总在同一点路过的夜班公交。想到明天要交的东西还没做完。</p>'
        '<p>你不该醒着。</p>'
        '<p>你醒了。</p>'),
    en=('<p class="l">You listen to it.</p>'
        '<p>It does not move.</p>'
        '<p>After a while something shifts deep in its throat, a very small sound. Not a meow.</p>'
        '<p>You think of the night bus that passes downstairs at the same hour every night. Of the work due tomorrow, not finished.</p>'
        '<p>You should not be awake.</p>'
        '<p>You are awake.</p>'),
    post=panel([('睁开眼', 'Open your eyes', '床')]))

# --- 床 ---
add('床',
    zh=('<p class="l">是一只猫。</p>'
        '<p>灰褐色的虎斑，鼻梁上有一块深色，像被人用拇指按了一下。耳朵缺了一个口，缺的地方已经磨圆了。</p>'
        '<p>眼睛是蓝的。蓝眼睛在流浪猫身上很少见。</p>'
        '<p>瘦。只有肚子那块圆一点。尾巴绕到前面，尖上一小撮白。</p>'
        '<p>你认得它。楼下垃圾房旁边那只。你喂过它三次，三次它都等你退到两米外才开始吃。</p>'
        '<p>现在它在你床上，离你的手三十厘米。</p>'
        '<p>它没有看你。它在看暖气片的方向。</p>'),
    en=('<p class="l">It is a cat.</p>'
        '<p>A brown-grey tabby, a dark patch across the bridge of its nose as if pressed there by a thumb. One ear is notched, and the notch has worn round.</p>'
        '<p>Its eyes are blue. Blue eyes are rare in a stray.</p>'
        '<p>Thin. Only the belly is round. The tail is wrapped round to the front, a tuft of white at the tip.</p>'
        '<p>You know it. The one by the rubbish room downstairs. You have fed it three times, and all three times it waited until you had stepped back two metres before it ate.</p>'
        '<p>Now it is on your bed, thirty centimetres from your hand.</p>'
        '<p>It is not looking at you. It is looking towards the radiator.</p>'),
    post=panel([('把手伸过去', 'Reach out', '第一次'),
                ('先不动，看它', 'Do not move yet \u2014 just watch', '看它')]))

# --- 看它 ---
add('看它',
    zh=('<p class="l">你看它。</p>'
        '<p>它开始洗脸。舌头伸出来，从爪子一路抹到耳后，抹到一半停住了——舌头还伸在外面，眼睛睁着，像忘了自己在干什么。</p>'
        '<p>三秒。</p>'
        '<p>然后它接着洗。同一只耳朵，它洗了七遍。</p>'),
    en=('<p class="l">You watch it.</p>'
        '<p>It begins to wash. Tongue out, one stroke from paw to behind the ear, and halfway it stops \u2014 tongue still out, eyes open, as if it forgot what it was doing.</p>'
        '<p>Three seconds.</p>'
        '<p>Then it goes on washing. The same ear, seven times.</p>'),
    post=panel([('把手伸过去', 'Reach out', '第一次'),
                ('还是不动', 'Still do not move', '十厘米')]))

# --- 十厘米 ---
add('十厘米',
    pre='<<set $pets to 12>>',
    zh=('<p class="l">它洗完了。</p>'
        '<p>把头搁在爪子上，眼睛闭上。</p>'
        '<p>呼噜声很小，隔着被子几乎听不见。</p>'
        '<p>你的手在被子里，一直没有拿出来。</p>'
        '<p>你们之间隔着一个手掌的距离。谁也没有过去。</p>'
        '<p class="end">天亮的时候，它走了。</p>'),
    en=('<p class="l">It finishes washing.</p>'
        '<p>Puts its head down on its paws and closes its eyes.</p>'
        '<p>The purring is very small; through the blanket you can barely hear it.</p>'
        '<p>Your hand stayed under the blanket the whole time. You never took it out.</p>'
        '<p>A palm’s width between you. Neither of you crossed it.</p>'
        '<p class="end">At first light it was gone.</p>'),
    post=CREDITS + RESTART)

# --- 第一次 ---
add('第一次',
    pre='<<set $t to 1>><<set $pets to 1>>',
    zh=('<p class="l">你把右手从被子里拿出来。很慢。</p>'
        '<p>它停了。头转过来，看着你的手。</p>'
        '<p>你没有再往前。手停在半空，掌心朝下，像在等一只鸟落下来。</p>'
        '<p>三秒。</p>'
        '<p>它把头顶过来，碰了一下你的指尖，然后收回去。</p>'
        '<p>很凉。指尖上有一点点湿。</p>'),
    en=('<p class="l">You bring your right hand out from under the blanket. Slowly.</p>'
        '<p>It stops. Turns its head. Looks at your hand.</p>'
        '<p>You do not go any further. Your hand stays in the air, palm down, as if waiting for a bird to land on it.</p>'
        '<p>Three seconds.</p>'
        '<p>It pushes its head forward, touches your fingertips once, then draws back.</p>'
        '<p>Cold. A little wet on the fingertips.</p>'),
    post=INC)

# --- 页眉 ---
P.append({'name': '页眉', 'text': (
    '<div class="hdr">'
    '<span class="n"><span class="lang-zh">摸猫</span>'
    '<span class="lang-en">Petting the Cat</span></span>'
    '<span class="c"><<print $times[$pets]>></span>'
    '<span class="lang-zh"><<link "EN">>'
    '<<run (window.CatLangSave||function(){})(true)>><</link>></span>'
    '<span class="lang-en"><<link "中文">>'
    '<<run (window.CatLangSave||function(){})(false)>><</link>></span>'
    '</div>'
)})

# --- 动作面板 ---
def action_panel(is_en):
    def build(is_en):
        def L(zh, en, tgt, pre=''):
            return '<<link "%s">>%s<<goto "%s">><</link>>' % ((en if is_en else zh), pre, tgt)
        bump = '<<set $t += 1>><<set $pets += 1>><<set $pause to 0>>'
        out = '<<if $t gte 10>>' + L('……', '…', '睡着')
        out += '<<else>>'
        out += L('摸头顶', 'Pet its head', '摸头顶', bump)
        out += L('挠下巴', 'Scratch it under the chin', '挠下巴', bump)
        out += L('顺着背摸下去', 'Run your hand down its back', '摸背', bump)
        out += '<<if $t gte 7>>' + L('摸肚子那块软的', 'Touch the soft part of its belly', '摸肚子', bump) + '<</if>>'
        out += '<<if not $looked>>' + L('再仔细看它', 'Look at it more closely', '看它二', '<<set $looked to true>>') + '<</if>>'
        out += L('把手收回来，停一会儿', 'Take your hand back and wait', '停手', '<<set $pause += 1>>')
        out += '<</if>>'
        return out
    return build(is_en)

P.append({'name': '动作', 'text': (
    '<div class="lang-zh"><div class="acts">' + action_panel(False) + '</div></div>'
    '<div class="lang-en"><div class="acts">' + action_panel(True) + '</div></div>'
    '<<if $t gte 7>><<run (window.CatPurrOn||function(){})()>><</if>>'
    '<div class="bar<<if $t gte 7>> hot<</if>>"><i style="width:<<print $t*10>>%"></i></div>'
)})

# --- 摸头顶 ---
add('摸头顶',
    zh=('<<if $t lt 4>>'
        '<p class="l">你把手放上去，只放了半个手掌。</p>'
        '<p>它的耳朵动了一下，往后挪了半寸，又停住——像在跟自己的腿商量。</p>'
        '<p>毛比看起来硬。上面有灰，有雨的味道。</p>'
        '<p>但它没有下床。</p>'
        '<<elseif $t lt 7>>'
        '<p class="l">手掌整个盖住它的头，拇指顺着耳后往下压。</p>'
        '<p>它把头顶上来一点，抵着你的手心。</p>'
        '<p>这不是躲。是顶着。</p>'
        '<p>你的掌心里有一小块地方，被它的头骨顶得发麻。</p>'
        '<<else>>'
        '<p class="l">你一摸，它就把头整个塞进你掌心，像在放最后一块拼图。</p>'
        '<p>声音是从它整个身体里出来的，不是从嗓子。</p>'
        '<p>你的手跟着那个声音一起在振。</p>'
        '<p>你想起小时候家里那台旧洗衣机，甩干的时候手扶着外壳，整条手臂都在抖。</p>'
        '<</if>>'),
    en=('<<if $t lt 4>>'
        '<p class="l">You put your hand on it, and only half your palm.</p>'
        '<p>Its ear flicks, shifts back half an inch, stops — as if negotiating with its own legs.</p>'
        '<p>The fur is coarser than it looks. Dust in it. Rain in it.</p>'
        '<p>But it does not get off the bed.</p>'
        '<<elseif $t lt 7>>'
        '<p class="l">Your whole palm covers its head now, thumb pressing down behind the ear.</p>'
        '<p>It pushes its head up a little, against your palm.</p>'
        '<p>It is not flinching. It is pushing back.</p>'
        '<p>A small patch in your palm has gone numb where the bone presses into it.</p>'
        '<<else>>'
        '<p class="l">One touch and it puts its whole head into your palm, like fitting in the last piece of a puzzle.</p>'
        '<p>The sound comes out of its whole body, not out of its throat.</p>'
        '<p>Your hand vibrates with it.</p>'
        '<p>You remember the old washing machine at home when you were small — your hand on the casing during the spin, the whole arm shaking.</p>'
        '<</if>>'),
    post=INC)

# --- 挠下巴 ---
add('挠下巴',
    zh=('<<if $t lt 4>>'
        '<p class="l">手指伸到它下巴底下。那里有一块地方是干的、凉的。</p>'
        '<p>它没有咬你，也没有走。</p>'
        '<p>它只是把下巴抬高了一点，让你更容易够到。</p>'
        '<<elseif $t lt 7>>'
        '<p class="l">下巴那块毛是软的，跟头顶不一样。</p>'
        '<p>你的指节碰到一小块痂，结在那里，很硬。</p>'
        '<p>它把脖子伸长，眼睛闭上了。</p>'
        '<p>一个陌生人，手在它下巴底下。它闭着眼。</p>'
        '<<else>>'
        '<p class="l">你挠一下，它的头就跟着抬一下，抬到后来下巴几乎朝着天花板。</p>'
        '<p>喉咙里的声音变大了。</p>'
        '<p>现在你确定那是呼噜。</p>'
        '<p>暖气片不会跟着你的手指变化。</p>'
        '<</if>>'),
    en=('<<if $t lt 4>>'
        '<p class="l">A finger goes under its chin. There is a place there that is dry and cold.</p>'
        '<p>It does not bite you. It does not leave.</p>'
        '<p>It only lifts its chin a little, so you can reach it more easily.</p>'
        '<<elseif $t lt 7>>'
        '<p class="l">The fur under the chin is soft, not like the top of the head.</p>'
        '<p>Your knuckle finds a small scab, set hard.</p>'
        '<p>It stretches its neck out and closes its eyes.</p>'
        '<p>A stranger, with a hand under its chin. And it closes its eyes.</p>'
        '<<else>>'
        '<p class="l">You scratch once and its head lifts once, and keeps lifting, until its chin is almost pointing at the ceiling.</p>'
        '<p>The sound in its throat gets louder.</p>'
        '<p>Now you are sure it is purring.</p>'
        '<p>A radiator does not change with your fingers.</p>'
        '<</if>>'),
    post=INC)

# --- 摸背 ---
add('摸背',
    zh=('<<if $t lt 4>>'
        '<p class="l">你顺着背摸下去，从脖子到尾根。</p>'
        '<p>摸到一半，整条背塌下去一截，像被人按了一下开关。</p>'
        '<p>尾根那块你没敢碰。</p>'
        '<<elseif $t lt 7>>'
        '<p class="l">手从脖子一直滑到尾根，一路都是骨头。</p>'
        '<p>它比你想象的瘦。背上那层毛把骨头盖得很好，但手一压就露出来了。</p>'
        '<p>摸到尾根的时候，尾巴立起来，尾尖那撮白毛扫过你的手腕。</p>'
        '<<else>>'
        '<p class="l">你的手停在它背上，能摸到那个声音的震动。</p>'
        '<p>一下，一下。大概一秒两次。</p>'
        '<p>比你的心跳慢。</p>'
        '<</if>>'),
    en=('<<if $t lt 4>>'
        '<p class="l">You run your hand down its back, from the neck to the base of the tail.</p>'
        '<p>Halfway down, the whole back drops a notch, as if someone flipped a switch.</p>'
        '<p>The base of the tail you did not dare touch.</p>'
        '<<elseif $t lt 7>>'
        '<p class="l">Your hand slides from the neck all the way to the base of the tail, and it is bone the whole way.</p>'
        '<p>Thinner than you imagined. The fur covers the bones well, but press and they show.</p>'
        '<p>At the base of the tail the tail comes up, and the white tip sweeps across your wrist.</p>'
        '<<else>>'
        '<p class="l">Your hand rests on its back, and you can feel the sound inside it, shaking.</p>'
        '<p>Once. Once. About twice a second.</p>'
        '<p>Slower than your heart.</p>'
        '<</if>>'),
    post=INC)

# --- 摸肚子 ---
add('摸肚子',
    zh=('<<if $t gte 9>>'
        '<p class="l">它又把肚子翻上来了，这次不用你问。</p>'
        '<p>那块毛是白的，中间有一小片粉的，毛薄得能看见皮。</p>'
        '<p>你把手放上去。它没有缩。</p>'
        '<p>它把最软的地方朝上，给你了。</p>'
        '<<else>>'
        '<p class="l">它翻了一下身，肚子朝上。</p>'
        '<p>那块毛是白的，中间有一小片粉的，毛薄得能看见皮。</p>'
        '<p>你把手放上去。</p>'
        '<p>肚皮底下那股热，隔着毛也摸得很清楚。一个活的东西的温度。</p>'
        '<p>它没有缩。它看着你的手，没有缩。</p>'
        '<</if>>'),
    en=('<<if $t gte 9>>'
        '<p class="l">It rolls its belly up again, this time without being asked.</p>'
        '<p>The fur there is white, a small pink patch in the middle, thin enough to see the skin through.</p>'
        '<p>You put your hand on it. It does not flinch.</p>'
        '<p>It turned its softest part upwards, and gave it to you.</p>'
        '<<else>>'
        '<p class="l">It turns over, belly up.</p>'
        '<p>The fur there is white, a small pink patch in the middle, thin enough to see the skin through.</p>'
        '<p>You put your hand on it.</p>'
        '<p>The heat under the belly comes through the fur clearly. The temperature of something alive.</p>'
        '<p>It does not flinch. It watches your hand, and does not flinch.</p>'
        '<</if>>'),
    post=INC)

# --- 看它二 ---
add('看它二',
    zh=('<p class="l">你凑近了一点。</p>'
        '<p>脖子上一圈毛是断的，短，整齐，像被什么东西长期勒着。它有过一个项圈。项圈现在不在了。</p>'
        '<p>左前爪少了一小块，断口很平——不是新伤。</p>'
        '<p>它睁开眼看你。蓝得不像真的。然后又闭上。</p>'
        '<p>你不知道该为哪一件事难受。</p>'),
    en=('<p class="l">You lean in a little closer.</p>'
        '<p>The fur around its neck is broken in a ring, short and even, as if something had been tight against it for a long time. It had a collar once. The collar is not there now.</p>'
        '<p>A small piece of its left forepaw is missing, the edge flat — not a new wound.</p>'
        '<p>It opens its eyes and looks at you. Blue past believing. Then closes them again.</p>'
        '<p>You do not know which one to be sorry about.</p>'),
    post=INC)

# --- 停手 ---
TING_LINK = '<div class="acts"><<link "……">><<goto "走">><</link>></div>'

add('停手',
    zh=('<<if $pause gte 2 and $t lt 4>>'
        '<p class="l">你把手收回来。第二次了。</p>'
        '<p>它抬头看你，看了很久——久到你以为它在等你改变主意。</p>'
        '<p>然后它站起来，伸了个懒腰。前爪伸得很长，爪子露出来一下，又收回去。</p>'
        + TING_LINK +
        '<<elseif $t lt 7>>'
        '<p class="l">你把手收回来。</p>'
        '<p>它抬头看你。看得比刚才久。</p>'
        '<p>你不知道它在等什么。</p>'
        + INC +
        '<<else>>'
        '<p class="l">你把手放在被子上，不动。</p>'
        '<p>它盯着你的手看了两秒，然后自己躺回去，尾巴尖轻轻拍了一下被子。</p>'
        '<p>像在说：行吧。</p>'
        '<p>又像在说别的什么。</p>'
        + INC +
        '<</if>>'),
    en=('<<if $pause gte 2 and $t lt 4>>'
        '<p class="l">You take your hand back. The second time.</p>'
        '<p>It looks up at you, for a long time — long enough that you think it is waiting for you to change your mind.</p>'
        '<p>Then it stands and stretches. Front paws out very long, claws showing once, then in.</p>'
        + TING_LINK +
        '<<elseif $t lt 7>>'
        '<p class="l">You take your hand back.</p>'
        '<p>It looks up at you. Longer than before.</p>'
        '<p>You do not know what it is waiting for.</p>'
        + INC +
        '<<else>>'
        '<p class="l">You put your hand down on the blanket and leave it there.</p>'
        '<p>It stares at your hand for two seconds, then lies back down on its own, the tip of its tail tapping the blanket once.</p>'
        '<p>As if to say: fine.</p>'
        '<p>Or something else.</p>'
        + INC +
        '<</if>>'))

# --- 走 ---
add('走',
    zh=('<p class="l">它从床尾跳下去，几乎没有声音。</p>'
        '<p>窗口开了一条缝，是你昨天忘的。</p>'
        '<p>你听见它在窗台上走了几步。</p>'
        '<p>然后没有了。</p>'
        '<p class="end">天还没亮。你把手放回被子里。被子外面还是凉的。</p>'),
    en=('<p class="l">It jumps down from the end of the bed, almost silently.</p>'
        '<p>The window is open a crack. You left it yesterday.</p>'
        '<p>You hear it take a few steps along the sill.</p>'
        '<p>Then nothing.</p>'
        '<p class="end">It is not light yet. You put your hand back under the blanket. Above the blanket it is still cold.</p>'),
    post=CREDITS + RESTART)

# --- 睡着 ---
add('睡着',
    zh=('<p class="l">第十一下。</p>'
        '<p>呼噜停了一拍，然后接上，慢了一半。</p>'
        '<p>它的头从你手里滑下去，落在被子上。</p>'
        '<p>它睡着了。</p>'
        '<p>睡着的猫比醒着的轻。你这才发现，手一直没有敢用力。</p>'),
    en=('<p class="l">The eleventh time.</p>'
        '<p>The purring misses a beat, then picks up again at half the speed.</p>'
        '<p>Its head slides out of your hand and lands on the blanket.</p>'
        '<p>It is asleep.</p>'
        '<p>A sleeping cat is lighter than a waking one. Only now do you notice: you never once dared to press.</p>'),
    post=panel([('就这么放着，不动', 'Leave it like this. Do not move', '天亮'),
                ('把手收回来，睡自己的', 'Take your hand back, sleep your own sleep', '收手'),
                ('起来，去厨房', 'Get up. Go to the kitchen', '厨房')]))

# --- 天亮 ---
add('天亮',
    pre='<<set $pets to 12>>',
    zh=('<p class="l">你没有把手拿开。</p>'
        '<p>窗外开始有车。楼下有人在收瓶子，玻璃碰玻璃，一声一声，很慢。</p>'
        '<p>五点四十。它醒了，看了你一眼，从窗口跳下去。</p>'
        '<p>走的时候没有回头。</p>'
        '<p class="end">你手背上那块地方，还是温的。</p>'),
    en=('<p class="l">You do not take your hand away.</p>'
        '<p>Cars begin outside. Downstairs someone is collecting bottles, glass against glass, one at a time, very slow.</p>'
        '<p>Five forty. It woke, looked at you once, and jumped out the window.</p>'
        '<p>It did not look back.</p>'
        '<p class="end">The place on the back of your hand is still warm.</p>'),
    post=CREDITS + RESTART)

# --- 收手 ---
add('收手',
    zh=('<p class="l">你把手收回来。它没有醒。</p>'
        '<p>你侧过身，背对着它。中间隔了十厘米。</p>'
        '<p>你知道它天亮之前会走。它一直是这样的。</p>'
        '<p class="end">但你睡着的时候，被子外面有一团热。</p>'),
    en=('<p class="l">You take your hand back. It does not wake.</p>'
        '<p>You turn onto your side, your back to it. Ten centimetres between you.</p>'
        '<p>You know it will be gone before the light. It has always been like this.</p>'
        '<p class="end">But while you sleep there is a warm patch outside the blanket.</p>'),
    post=CREDITS + RESTART)

# --- 厨房 ---
add('厨房',
    zh=('<p class="l">你去厨房，把昨天剩的半个罐头倒进那个缺了口的碗里。</p>'
        '<p>水龙头开得很小，怕吵醒它。</p>'
        '<p>回来的时候，床上空了。</p>'
        '<p>碗是空的。</p>'
        '<p class="end">你不知道它是什么时候吃的。</p>'),
    en=('<p class="l">You go to the kitchen and tip half a can, left from yesterday, into the bowl with the chipped rim.</p>'
        '<p>The tap is turned on very low, so it will not wake.</p>'
        '<p>When you come back, the bed is empty.</p>'
        '<p>The bowl is empty.</p>'
        '<p class="end">You do not know when it ate.</p>'),
    post=CREDITS + RESTART)

CSS = r'''
:root{--bg:#0b0908;--ink:#e7ddd0;--dim:#9c9182;--mute:#5f574c;--amber:#c47a4a}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:"Iowan Old Style","Palatino",Georgia,"Songti SC","STSong","Noto Serif CJK SC",serif;
 -webkit-font-smoothing:antialiased;overflow-x:hidden}
::selection{background:rgba(196,122,74,.28);color:#fff6ea}

#ui-bar{display:none!important}
#story{margin:0!important;padding:0!important;max-width:none!important;width:auto!important}
#passages{margin:0!important;padding:0!important;border:0!important;max-width:none!important}

#ph{position:fixed;top:0;right:0;width:46vw;height:100vh;z-index:0;pointer-events:none;
 -webkit-mask-image:linear-gradient(to right,rgba(0,0,0,0) 0%,#000 24%);
 mask-image:linear-gradient(to right,rgba(0,0,0,0) 0%,#000 24%)}
#ph img{display:block;width:100%;height:100%;object-fit:cover;object-position:54% 40%;
 filter:saturate(.94) brightness(.86) contrast(1.02);
 transform-origin:54% 42%;animation:breathe 9s ease-in-out infinite}
#ph::before{content:"";position:absolute;inset:0;background:none}
#ph::after{content:"";position:absolute;inset:0;
 background:radial-gradient(72% 52% at 74% 26%,rgba(196,122,74,.14),rgba(196,122,74,0) 72%)}
@keyframes breathe{0%,100%{transform:scale(1.004)}50%{transform:scale(1.03)}}

body::after{content:"";position:fixed;inset:0;z-index:9;pointer-events:none;opacity:.075;
 mix-blend-mode:overlay;background-size:96px 96px;
 background-image:url("data:image/png;base64,GRAINHERE")}

#passages>div{margin:0!important;padding:0!important;border:0!important}
.scene{position:relative;z-index:2;width:min(600px,45vw);padding:12vh 0 15vh clamp(28px,5vw,88px)}
.scene p{margin:0;font-size:17px;line-height:2.05;letter-spacing:.015em;color:var(--ink)}
.scene p+p{margin-top:.6em}
.scene p.l{font-size:18.5px;color:#f2e9dc;letter-spacing:.045em}
.scene p.l+p{margin-top:.95em}
.scene p.end{margin-top:1.8em;color:var(--amber);font-size:16px;letter-spacing:.09em}

.hdr{display:flex;justify-content:space-between;align-items:baseline;gap:14px;margin:0 0 40px;
 font-family:"PingFang SC","Hiragino Sans GB","Helvetica Neue",sans-serif;
 font-size:10.5px;letter-spacing:.3em;color:var(--mute)}
.hdr .n{margin-right:auto}
.hdr .c{font-variant-numeric:tabular-nums;letter-spacing:.16em;color:#7b7166}
.hdr a{padding:14px 8px;margin:-14px -8px;text-decoration:none;
 font-family:"PingFang SC","Hiragino Sans GB",sans-serif;
 font-size:10.5px;letter-spacing:.2em;color:var(--mute);transition:color .35s ease}
.hdr a:hover{color:var(--amber)}
html:not(.en) .lang-en{display:none}
html.en .lang-zh{display:none}

.acts{margin-top:2.3em;display:flex;flex-direction:column;align-items:flex-start;gap:1px}
.acts a{position:relative;display:inline-block;padding:11px 4px 11px 28px;line-height:1.6;
 font-family:"PingFang SC","Hiragino Sans GB","Helvetica Neue",sans-serif;
 font-size:14px;letter-spacing:.13em;color:var(--dim);text-decoration:none;
 transition:color .4s ease,letter-spacing .4s ease;-webkit-tap-highlight-color:transparent}
.acts a::before{content:"";position:absolute;left:0;top:50%;width:11px;height:1px;
 background:var(--mute);transform:translateY(-50%);transition:width .4s ease,background .4s ease}
.acts a:hover,.acts a:focus-visible{color:var(--amber);letter-spacing:.17em}
.acts a:hover::before,.acts a:focus-visible::before{width:21px;background:var(--amber)}
.acts a:focus-visible{outline:none}
.acts a:active{color:#e09563}

.bar{margin-top:2.4em;width:100%;max-width:250px;height:1px;background:rgba(255,255,255,.06)}
.bar i{display:block;height:1px;width:0;background:linear-gradient(90deg,rgba(196,122,74,.5),rgba(242,196,156,.95));
 transition:width 1.2s cubic-bezier(.2,.6,.3,1)}
.bar.hot i{animation:pulse 1.7s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:.5}50%{opacity:1}}

.credits{margin-top:3.4em;padding-top:1.3em;border-top:1px solid rgba(255,255,255,.06);
 font-family:"PingFang SC","Hiragino Sans GB",sans-serif;
 font-size:11px;line-height:2.1;letter-spacing:.1em;color:var(--mute)}

#snd{padding:14px 8px;margin:-14px -8px;background:none;border:0;cursor:pointer;
 font-family:"PingFang SC","Hiragino Sans GB",sans-serif;
 font-size:10.5px;letter-spacing:.18em;color:var(--mute);transition:color .35s ease}
#snd:hover{color:var(--amber)}

@media (max-width:860px){
 #ph{width:100%;height:34vh;right:0;
  -webkit-mask-image:linear-gradient(to bottom,#000 54%,rgba(0,0,0,0) 100%);
  mask-image:linear-gradient(to bottom,#000 54%,rgba(0,0,0,0) 100%)}
 #ph img{object-position:50% 42%}
 #ph::before{background:linear-gradient(to bottom,rgba(11,9,8,0) 32%,rgba(11,9,8,.88) 82%,#0b0908 100%)}
 .scene{width:100%;max-width:560px;margin:0 auto;padding:calc(34vh + 26px) 24px 88px}
 .hdr{margin-bottom:32px}
}

@media print{#ph,#snd,#ui-bar{display:none}#story{background:#fff}}

@media (prefers-reduced-motion:reduce){
 #ph img{animation:none}
 .bar i{transition:none}
 .bar.hot i{animation:none}
}
'''

JS = r'''
(function(){
  var TALL = 'data:image/jpeg;base64,PHOTOHERE';
  var WIDE = 'data:image/jpeg;base64,WIDEHERE';

  var ph = document.createElement('div');
  ph.id = 'ph';
  var img = new Image();
  img.alt = ''; img.decoding = 'async'; img.src = TALL;
  ph.appendChild(img);
  document.body.appendChild(ph);

  var mq = window.matchMedia('(max-width:860px)');
  function pick(){ img.src = mq.matches ? WIDE : TALL; }
  pick();
  try {
    if (mq.addEventListener) { mq.addEventListener('change', pick); }
    else if (mq.addListener) { mq.addListener(pick); }
  } catch (e) {}

  window.MO_MAO_LANG = 'zh';
  try { if (localStorage.getItem('mo_mao_lang') === 'en') { window.MO_MAO_LANG = 'en'; } } catch (e) {}

  function sndLabel(){
    var on = btn.getAttribute('aria-pressed') === 'true';
    if (window.MO_MAO_LANG === 'en') { return on ? 'sound \u00b7 on' : 'sound \u00b7 off'; }
    return on ? '\u58f0\u97f3 \u00b7 \u5f00' : '\u58f0\u97f3 \u00b7 \u5173';
  }

  var btn = document.createElement('button');
  btn.id = 'snd'; btn.type = 'button';
  btn.setAttribute('aria-pressed','false');
  btn.textContent = sndLabel();
  btn.title = window.MO_MAO_LANG === 'en' ? 'purring' : '\u547c\u565c\u58f0';

  function applyLang(){
    var root = document.documentElement;
    if (root) { root.classList.toggle('en', window.MO_MAO_LANG === 'en'); }
  }

  window.CatLangSave = function(on){
    window.MO_MAO_LANG = on ? 'en' : 'zh';
    try { localStorage.setItem('mo_mao_lang', window.MO_MAO_LANG); } catch (e) {}
    applyLang();
    btn.textContent = sndLabel();
    btn.title = window.MO_MAO_LANG === 'en' ? 'purring' : '\u547c\u565c\u58f0';
  };

  applyLang();
  try { document.addEventListener('DOMContentLoaded', applyLang); } catch (e) {}

  function mount(){
    applyLang();
    var hdr = document.querySelector('#passages .hdr');
    if (hdr && btn.parentNode !== hdr) { hdr.appendChild(btn); }
  }
  mount();
  try {
    var root = document.getElementById('passages') || document.body;
    new MutationObserver(mount).observe(root, { childList: true, subtree: true });
  } catch (e) {}

  var ac = null, master = null, ready = false, soundOn = false, wanted = false;

  function build(){
    if (ready) { return true; }
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) { return false; }
      ac = new AC();
      var sr = ac.sampleRate, len = Math.floor(sr * 3);
      var buf = ac.createBuffer(1, len, sr), d = buf.getChannelData(0);
      for (var i = 0; i < len; i++) { d[i] = (Math.random() * 2 - 1) * 0.7; }
      var src = ac.createBufferSource(); src.buffer = buf; src.loop = true;
      var lp = ac.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 420; lp.Q.value = 0.6;
      var pk = ac.createBiquadFilter(); pk.type = 'peaking'; pk.frequency.value = 108; pk.Q.value = 1.1; pk.gain.value = 7;
      var amp = ac.createGain(); amp.gain.value = 0.55;
      var lfo = ac.createOscillator(); lfo.type = 'sine'; lfo.frequency.value = 23.5;
      var depth = ac.createGain(); depth.gain.value = 0.34;
      lfo.connect(depth); depth.connect(amp.gain);
      master = ac.createGain(); master.gain.value = 0;
      src.connect(lp); lp.connect(pk); pk.connect(amp); amp.connect(master); master.connect(ac.destination);
      src.start(0); lfo.start(0);
      ready = true; return true;
    } catch (e) { return false; }
  }

  function ramp(v){
    if (!ready) { return; }
    try {
      if (ac.state === 'suspended') { ac.resume(); }
      master.gain.cancelScheduledValues(ac.currentTime);
      master.gain.setTargetAtTime(v, ac.currentTime, 0.7);
    } catch (e) {}
  }

  window.CatPurrOn = function(){
    wanted = true;
    if (soundOn && build()) { ramp(0.030); }
  };

  btn.addEventListener('click', function(){
    soundOn = !soundOn;
    btn.setAttribute('aria-pressed', soundOn ? 'true' : 'false');
    btn.textContent = sndLabel();
    if (soundOn) { if (wanted && build()) { ramp(0.030); } }
    else { ramp(0); }
  });

})();
'''

CSS = CSS.replace('GRAINHERE', grain_b64)
wide_b64 = b64(os.path.join(ASST, 'cat_scene_wide.jpg'))
JS = JS.replace('PHOTOHERE', photo_b64)
JS = JS.replace('WIDEHERE', wide_b64)

IFID = str(uuid.uuid4()).upper()

parts = []
parts.append(
    '<tw-storydata name="摸猫 · Petting the Cat" startnode="1" creator="Twine" creator-version="2.6.2"'
    ' format="SugarCube" format-version="2.37.3" ifid="%s" options="" tags="">' % IFID
)
parts.append('<style role="stylesheet" id="twine-user-stylesheet" type="text/twine-css">%s</style>' % CSS)
parts.append('<script role="script" id="twine-user-script" type="text/twine-javascript">%s</script>' % JS)

for i, p in enumerate(P, start=1):
    parts.append(
        '<tw-passagedata pid="%d" name="%s" tags="" position="%d,%d" size="100,100">%s</tw-passagedata>'
        % (i, html.escape(p['name'], quote=True), 140 + (i % 4) * 200, 120 + i * 90,
           html.escape(p['text'], quote=False))
    )
parts.append('</tw-storydata>')

story_data = ''.join(parts)

# favicon（SVG 爪印，内联）
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
       '<g fill="#c47a4a"><ellipse cx="16" cy="21.5" rx="7.6" ry="6.4"/>'
       '<circle cx="7.2" cy="13.4" r="3.3"/><circle cx="12.2" cy="8.4" r="3.5"/>'
       '<circle cx="19.8" cy="8.4" r="3.5"/><circle cx="24.8" cy="13.4" r="3.3"/></g></svg>')
fav = '<link rel="icon" href="data:image/svg+xml,%s" />' % urllib.parse.quote(svg, safe='')

doc = template.replace('{{STORY_NAME}}', '摸猫 · Petting the Cat')
doc = doc.replace('<meta charset="UTF-8" />', '<meta charset="UTF-8" />\n' + fav, 1)
doc = doc.replace('{{STORY_DATA}}', story_data)

open(OUT, 'w', encoding='utf-8').write(doc)
print('passages:', len(P), 'ifid:', IFID)
print('html bytes:', os.path.getsize(OUT))
