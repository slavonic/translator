import argparse
import collections


def scan(fname):
    with open(fname, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            word, count = line.split()
            yield word, int(count)

C_PNEUMATA = '\u0486'

# а҆́
ERRATA = {
    'аллилꙋїа': 'а҆ллилꙋ\u0301їа',
    'аминь': 'а҆м\u0301инь',
    'апостола': 'а҆п\u0301остола',
    'архїерей': 'а҆рхїере\u0301й',
    'архїереовꙋ': 'а҆рхїере\u0301овꙋ',
    'аще': 'а҆\u0301ще',
    'без̾именитое': 'безъимени\u0301тое',
    'благᲂуханїѧ': 'благᲂуха\u0301нїѧ',
    'блаженнѣйшагѡ': 'блаже\u0301ннѣйшагѡ',
    'блгⷭ҇венъ': 'блгⷭ҇в\u0301енъ',
    'благостей': 'бла\u0301гостей',
    'богомъ': 'бо\u0301гомъ',
    'богу': 'бо\u0301гу',
    'божественнаѧ': 'боже\u0301ственнаѧ',
    'болѣзнь': 'болѣ\u0301знь',
    'братїй': 'бра\u0301тїй',
    'бꙋдетъ': 'бꙋ\u0301детъ',
    'в̾оньже': 'в̾о\u0301ньже',
    'владыко': 'влады\u0301ко',
    'возгласъ': 'во\u0301згласъ',
    'возглашаетъ': 'возглаша\u0301етъ',
    'воскр҃сый': 'воскр҃сы\u0301й',
    'воспрїѧтую': 'воспрїѧ\u0301тую',
    'вселеннꙋю': 'вселе\u0301ннꙋю',
    'всемꙋ': 'всемꙋ̀',
    'всѧкую': 'всѧ\u0301кую',
    'входѧтъ': 'вхо\u0301дѧтъ',
    'вѣка': 'вѣ\u0301ка',
    'вѣки': 'вѣ\u0301ки',
    'вѣрнымъ': 'вѣ\u0301рнымъ',
    'вѣрѣ': 'вѣ\u0301рѣ',
    'главꙋ': 'главꙋ̀',
    'глаголѧ': 'глаго\u0301лѧ',
    'господа': 'го\u0301спода',
    'господи': 'го\u0301споди',
    'господу': 'го\u0301споду',
    'господь': 'госпо\u0301дь',
    'греко': 'гре\u0301ко',
    'дарѣхъ': 'дарѣ\u0301хъ',
    'дожди': 'дожди\u0301',
    'духовный': 'дꙋхо́вный',
    'дїакони': 'дїа\u0301кони',
    'дїаконъ': 'дїа\u0301конъ',
    'дѣвствѣ': 'дѣ\u0301вствѣ',
    'дѣлающихъ': 'дѣ\u0301лающихъ',
    'дѣснꙋю': 'дѣснꙋ\u0301ю',
    'дꙋха': 'дꙋ\u0301ха',
    'дꙋшу': 'дꙋ\u0301шу',
    'дꙋшы': 'дꙋшы\u0300',
    'животворѧщую': 'животворѧ́щꙋю',
    'заблꙋждшихъ': 'заблꙋ\u0301ждшихъ',
    'завѣсою': 'завѣ\u0301сою',
    'зане': 'занѐ',
    'иже': 'и҆́же',
    'или': 'и҆лѝ',
    'исходитъ': 'и҆схо́дитъ',
    'исходѧтъ': 'и҆схо́дѧтъ',
    'кажденїѧ': 'кажде́нїѧ',
    'книги': 'кни\u0301ги',
    'коемꙋждо': 'коемꙋ\u0301ждо',
    'конецъ': 'коне\u0301цъ',
    'либо': 'ли\u0301бо',
    'лицемъ': 'лице\u0301мъ',
    'людей': 'люде\u0301й',
    'люди': 'лю\u0301ди',
    'малѡ': 'ма\u0301лѡ',
    'междꙋ': 'междꙋ̀',
    'милостїю': 'млⷭ҇тїю',
    'множества': 'мно́жєства',
    'москвѣ': 'москвѣ̀',
    'надо': 'на\u0301до',
    'нашу': 'на́шꙋ',
    'небо': 'нб҃о',
    'немꙋ': 'немꙋ̀',
    'нимже': 'ни\u0301мже',
    'нравоꙋч': 'нравоꙋче́нїе',
    'орꙋжїе': 'орꙋ\u0301жїе',
    'отца': 'о\u0486тца\u0300',
    'отцꙋ': 'о\u0486тцꙋ\u0300',
    'отче': 'о\u0486\u0301тче',
    'ошꙋюю': 'ѡ҆шꙋ́юю',
    'помолимсѧ': 'помо\u0301лимсѧ',
    'помѧнꙋхомъ': 'помѧнꙋ\u0301хомъ',
    'презрѣлъ': 'презрѣ\u0301лъ',
    'приснодѣву': 'приснодѣ\u0301вꙋ',
    'пѣти': 'пѣ\u0301ти',
    'рꙋки': 'рꙋкѝ',
    'рꙋцѣ': 'рꙋ\u0301цѣ',
    'самꙋила': 'самꙋи\u0301ла',
    'свѧтагѡ': 'свѧта\u0301гѡ',
    'свѧто': 'свѧ\u0301то',
    'свѧтое': 'свѧто\u0301е',
    'свѧтыми': 'свѧты\u0301ми',
    'свѧтыхъ': 'свѧты\u0301хъ',
    'свѧтѣй': 'свѧтѣ\u0301й',
    'свѧщенно': 'свѧще\u0301нно',
    'семꙋ': 'семꙋ̀',
    'сеѧ': 'сеѧ̀',
    'слава': 'сла\u0301ва',
    'слово': 'сло\u0301во',
    'содѣлай': 'содѣ\u0301лай',
    'сослꙋжитъ': 'сослꙋжи\u0301тъ',
    'сохрани': 'сохранѝ',
    'странꙋ': 'странꙋ̀',
    'стꙋдное': 'стꙋ\u0301дное',
    'таже': 'та\u0301же',
    'тайнѡ': 'та\u0301йнѡ',
    'твоегѡ': 'твоегѡ̀',
    'твоемꙋ': 'твоемꙋ̀',
    'твои': 'твоѝ',
    'тебѣ': 'тебѣ̀',
    'тожде': 'то\u0301жде',
    'трисвѧтꙋю': 'трисвѧтꙋ\u0301ю',
    'устнѣ': 'ᲂу҆стнѣ̀',
    'хощеши': 'хо\u0301щеши',
    'храмѣ': 'хра\u0301мѣ',
    'христово': 'христо\u0301во',
    'часа': 'часа̀',
    'ꙗкѡ': 'ꙗ҆́кѡ',
    'ꙗкоже': 'ꙗ҆́коже',
    'ꙗже': 'ꙗ҆́же',
    'ѿметаѧйсѧ': 'ѿмета\u0301ѧйсѧ',
    'ѿтроцы': 'ѿроцы',
    'ѿтроки': 'ѿроки',
    'іисꙋса': 'і҆и҃са',
    'єси': 'є҆си',
    'ємꙋ': 'є҆мꙋ̀',
    'єже': 'єже́',
    'патер': None,
    'подо': None,
    'посѣти': 'посѣтѝ',
    'предо': None,
    'іі': None,
    'преполов': None,
    'ᲂу҆ч҃нкѡмъ': 'ᲂу҆ч҃нкѡ\u0301мъ',
    'ᲂу҆чн҃кѡмъ': 'ᲂу҆чн҃кѡ\u0301мъ',
}

parser = argparse.ArgumentParser(description='Applies errata to the word list')
parser.add_argument('-i', '--input', default='cu-words.txt')
parser.add_argument('-o', '--output', default='cu-words-errata.txt')

args = parser.parse_args()

counter = collections.defaultdict(int)

for word, count in scan(args.input):
    word = ERRATA.get(word, word)
    if word is not None:
        counter[word] += count

with open(args.output, 'w', encoding='utf-8') as f:
    for word, count in sorted(counter.items()):
        f.write(f'{word}\t{count}\n')