#!/usr/bin/python3
import mmap
import os
import re
import subprocess
import unicodedata

lang="Czech"
lang2="cs"

diacritic = "diakritika"
accentNames = {
	"\u0300": "čárka doleva",
	"\u0301": "čárka",
	"\u0302": "stříška",
	"\u0303": "vlnovka",
	"\u0304": "makron",
	"\u0306": "oblouček",
	"\u0307": "tečka nad",
	"\u0308": "přehláska",
	"\u0309": "hák nad",
	"\u030a": "kroužek",
	"\u030b": "dvojčárka",
	"\u030c": "háček",
	"\u030f": "dvojčárka doleva",
	"\u0311": "obrácený oblouček",
	"\u0313": "čárka nad",
	"\u0316": "čárka doleva pod",
	"\u0317": "čárka doprava pod",
	"\u0326": "čárka pod",
	"\u0327": "cedilla",
	"\u0328": "ocásek",
	"\u032c": "háček pod",
}

accentSuffixes = {
	"\u0300": "s čárkou doleva",
	"\u0301": "s čárkou",
	"\u0302": "se stříškou",
	"\u0303": "s vlnovkou",
	"\u0304": "s makronem",
	"\u0306": "s obloučkem",
	"\u0307": "s tečkou nad",
	"\u0308": "s přehláskou",
	"\u0309": "s hákem nad",
	"\u030a": "s kroužkem",
	"\u030b": "s dvojčárkou",
	"\u030c": "s háčkem",
	"\u030f": "s dvojčárkou doleva",
	"\u0311": "s obráceným obloučkem",
	"\u0313": "s čárkou nad",
	"\u0316": "s čárkou doleva pod",
	"\u0317": "s čárkou doprava pod",
	"\u0326": "s čárkou pod",
	"\u0327": "s cedillou",
	"\u0328": "s ocáskem",
	"\u032c": "s háčkem pod",
}

fullWidth = "plná šířka"

latinExceptions = {
	'ø': ('o', 'ó přeškrtnuté'),
	'đ': ('d', 'dé přeškrtnuté'),
	'ħ': ('h', 'há přeškrtnuté'),
	'ı': ('i', 'í bez tečky'),
	'ĸ': ('', 'kra'),
	'ł': ('l', 'el přeškrtnuté'),
	'ŋ': ('', 'eng'),
	'œ': ('', 'ligatura oe'),
	'ŧ': ('t', 'té přeškrtnuté'),
	#'ſ': ('s', 'ostré es'),
	'ƀ': ('b', 'bé přeškrtnuté'),
	'ɓ': ('b', 'bé s hákem'),
	'ƃ': ('b', 'bé s čárou shora'),
	'ƅ': ('', 'tón šest'),
	'ɔ': ('o', 'otevřené ó'),
	'ƈ': ('c', 'cé s hákem'),
	'ɖ': ('d', 'africké dé'),
	'ɗ': ('d', 'dé s hákem'),
	'ƌ': ('d', 'dé s čárou shora'),
	'ƍ': ('', 'otočená delta'),
	'ǝ': ('e', 'obrácené é'),
	'ə': ('', 'šva'),
	'ɛ': ('e', 'otevřené é'),
	#'ƒ': ('f', 'florin'),
	'ɠ': ('g', 'gé s hákem'),
	'ɣ': ('', 'gama'),
	'ƕ': ('', 'há vé'),
	'ɩ': ('i', 'jota'),
	'ɨ': ('i', 'í přeškrtnuté'),
	'ƙ': ('k', 'ká s hákem'),
	'ƚ': ('l', 'el s čárou'),
	'ƛ': ('', 'lambda přeškrtnutá'),
	'ɯ': ('m', 'obrácené em'),
	'ɲ': ('n', 'en s hákem zleva'),
	'ƞ': ('n', 'en s dlouhou nožičkou zprava'),
	'ɵ': ('o', 'ó s vlnovkou uprostřed'),
	'ƣ': ('', 'oi'),
	'ƥ': ('p', 'pé s hákem'),
	'ʀ': ('', 'yr'),
	'ƨ': ('', 'tón dva'),
	'ʃ': ('', 'é es há'),
	'ƪ': ('', 'obrácené é es há dokola'),
	'ƫ': ('t', 'té s předním hákem'),
	'ƭ': ('t', 'té s hákem'),
	'ʈ': ('t', 'té s ohnutým hákem'),
	'ʊ': ('', 'upsilon'),
	'ʋ': ('v', 'vé s hákem'),
	'ƴ': ('y', 'ypsylon s hákem'),
	'ƶ': ('z', 'zet přeškrtnuté'),
	'ʒ': ('', 'éž'),
	'ƹ': ('', 'obrácené éž'),
	'ƺ': ('', 'éž s ocáskem'),
	'ƻ': ('2', 'dva s přeškrtnutím'),
	'ƽ': ('', 'tón pět'),
	'ƾ': ('', 'obrácený fonetický ráz s přeškrtnutím'),
	#'ƿ': ('', 'latinské písmeno WYNN'),
	'ǀ': ('', 'cvaknutí zuby'),
	'ǁ': ('', 'boční cvaknutí'),
	'ǂ': ('', 'dásňové cvaknutí'),
	'ǃ': ('', 'ohnuté cvaknutí'),
	'ǥ': ('g', 'gé přeškrtnuté'),
	'ȝ': ('', 'yogh'),
	'ȡ': ('d', 'kudrnaté dé'),
	'ȣ': ('', 'ou'),
	'ȥ': ('z', 'zet s hákem'),
	'ȴ': ('l', 'kudrnaté el'),
	'ȵ': ('n', 'kudrnaté en'),
	'ȶ': ('t', 'kudrnaté té'),
	'ȷ': ('j', 'jé bez tečky'),
	'ȸ': ('d', 'dé bé'),
	'ȹ': ('', 'kvé pé'),
	'ⱥ': ('a', 'á přeškrtnuté'),
	'ȼ': ('c', 'cé přeškrtnuté'),
	'ⱦ': ('t', 'té přeškrtnuté úhlopříčně'),
	'ȿ': ('s', 'es s ozdobným ocáskem'),
	'ɀ': ('z', 'zet s ozdobným ocáskem'),
	'ɂ': ('', 'fonetický ráz'),
	'ʉ': ('u', 'ú s čárou'),
	'ʌ': ('v', 'obrácené vé'),
	'ɇ': ('e', 'é přeškrtnuté'),
	'ɉ': ('j', 'jé přeškrtnuté'),
	'ɋ': ('q', 'kvé s ocáskem ve tvaru háku'),
	'ɍ': ('r', 'er přeškrtnuté'),
	'ɏ': ('y', 'ypsylon přeškrtnuté'),
	'ɐ': ('a', 'obrácené á'),
	'ɑ': ('', 'alfa'),
	'ɒ': ('', 'obrácená alfa'),
	'ɕ': ('c', 'kudrnaté cé'),
	'ɘ': ('e', 'obrátené é'),
	'ɚ': ('', 'šva s hákem'),
	'ɜ': ('e', 'obrácené otevřené é'),
	'ɝ': ('e', 'obrácené otevřené é s hákem'),
	'ɞ': ('e', 'zavřené obrácené otevřené é'),
	'ɟ': ('j', 'přeškrtnuté jé bez tečky'),
	'ɡ': ('g', 'skript gé'),
	'ɢ': ('g', 'malé velké gé'),
	'ɤ': ('', 'rams horn'),
	'ɥ': ('h', 'obrácené há'),
	'ɦ': ('h', 'há s hákem'),
	'ɧ': ('', 'heng s hákem'),
	'ɪ': ('i', 'malé velké í'),
	'ɫ': ('l', 'el s vlnovkou uprostřed'),
	'ɬ': ('l', 'el s páskem'),
	'ɭ': ('l', 'el s ohnutým hákem'),
	'ɮ': ('', 'lezh'),
	'ɰ': ('m', 'obrácené em s dlouhou nožičkou'),
	'ɱ': ('m', 'em s hákem'),
	'ɳ': ('n', 'n s ohnutým hákem'),
	'ɴ': ('n', 'malé velké en'),
	'ɶ': ('e', 'malé velké oé'),
	'ɷ': ('', 'zavřená omega'),
	'ɸ': ('', 'fí'),
	'ɹ': ('r', 'obrácené er'),
	'ɺ': ('r', 'obrácené er s dlouhou nožičkou'),
	'ɻ': ('r', 'obrácené er s hákem'),
	'ɼ': ('r', 'er s dlouhou nožičkou'),
	'ɽ': ('r', 'er s ocáskem'),
	'ɾ': ('r', 'er s malým hákem'),
	'ɿ': ('r', 'obrácené er s malým hákem'),
	'ʁ': ('r', 'malé obrácené velké er'),
	'ʂ': ('s', 'ess s hákem'),
	'ʄ': ('j', 'přeškrtnuté jé bez tečky s hákem'),
	'ʅ': ('', 'skrčené obrácené ezh'),
	'ʆ': ('', 'kudrnaté ezh'),
	'ʇ': ('t', 'obrácené té'),
	'ʍ': ('w', 'obrácené dvojité vé'),
	'ʎ': ('y', 'obrácené ypsylon'),
	'ʏ': ('y', 'malé velké ypsylón'),
	'ʐ': ('z', 'zet s ohnutým hákem'),
	'ʑ': ('z', 'kudrnaté zet'),
	'ʓ': ('', 'kudrnaté ezh'),
	'ʔ': ('', 'fonetický ráz'),
	'ʕ': ('', 'znělá hrdelní frikativa'),
	'ʖ': ('', 'obrácený fonetický ráz'),
	'ʗ': ('c', 'roztažené cé'),
	'ʘ': ('', 'cvaknutí rty'),
	'ʙ': ('b', 'malé velké bé'),
	'ʚ': ('e', 'zavřené otevřené é'),
	'ʛ': ('g', 'malé velké gé s hákem'),
	'ʜ': ('h', 'malé velké há'),
	'ʝ': ('j', 'jé se skříženým ocáskem'),
	'ʞ': ('k', 'obrácené ká'),
	'ʟ': ('l', 'malé velké el'),
	'ʠ': ('q', 'kvé s hákem'),
	'ʡ': ('', 'přeškrtnutý fonetický ráz'),
	'ʢ': ('', 'obrácený přeškrtnutý fonetický ráz'),
	'ʣ': ('', 'dvojhláska dé zet'),
	'ʤ': ('', 'dvojhláska desh'),
	'ʥ': ('', 'kudrnatá dvojhláska dé zet'),
	'ʦ': ('', 'dvojhláska té es'),
	'ʧ': ('', 'dvojhláska tesh'),
	'ʨ': ('', 'kudrnatá dvojhláska té cé'),
	'ʩ': ('', 'dvojhláska feng'),
	'ʪ': ('', 'dvojhláska el es'),
	'ʫ': ('', 'dvojhláska el zet'),
	'ʬ': ('', 'retní náraz'),
	'ʭ': ('', 'zubní náraz'),
	'ʮ': ('h', 'obrácené há s malým hákem'),
	'ʯ': ('h', 'obrácené há s malým hákem a ocáskem'),
}

baseCharSpelling = {
	"a": "a",
	"b": "bé",
	"c": "cé",
	"d": "dé",
	"e": "e",
	"f": "ef",
	"g": "gé",
	"h": "há",
	"i": "i",
	"j": "jé",
	"k": "ká",
	"l": "el",
	"m": "em",
	"n": "en",
	"o": "o",
	"p": "pé",
	"q": "kvé",
	"r": "er",
	"s": "es",
	"t": "té",
	"u": "ú",
	"v": "vé",
	"w": "dvojité vé",
	"x": "ix",
	"y": "ypsilon",
	"z": "zet",
}

fullWidthOffset = 0xfee0

# Math unicode symbols that mirror basic latin alphabet
# description is appended to the letter spelling such as a bold, a italic
# Offset is a difference between basic lowercase unicode character and math unicode symbol
# Python's builtin transformation from lowercase to uppercase and the other way round is not supported consistently thus store two offsets for each type.
unicodeMath = (
	#(description, upper case offset, lowercase offset)
	('Tučné Matematické', 0x1d39f, 0x1d3b9), # MATHEMATICAL BOLD
	('Kurzíva Matematické', 0x1d3d3, 0x1d3ed), # MATHEMATICAL ITALIC
	('Tučné Kurzíva Matematické', 0x1d407, 0x1d421), # MATHEMATICAL BOLD ITALIC
	('Skript Matematické', 0x1d43b, 0x1d455), # MATHEMATICAL SCRIPT
	('Tučné Skript Matematické', 0x1d46f, 0x1d489), # MATHEMATICAL BOLD SCRIPT
	('Fraktura Matematické', 0x1d4a3, 0x1d4bd), # MATHEMATICAL FRAKTUR
	('Dvakrát vyražené matematické', 0x1d4d7, 0x1d4f1), # MATHEMATICAL DOUBLE-STRUCK
	('Tučné Fraktura Matematické', 0x1d50b, 0x1d525), # MATHEMATICAL BOLD FRAKTUR
	('bezpatkové matematické', 0x1d53f, 0x1d559), # MATHEMATICAL SANS-SERIF
	('Tučné bezpatkové Matematické', 0x1d573, 0x1d58d), # MATHEMATICAL SANS-SERIF BOLD
	('Kurzíva bezpatkové Matematické', 0x1d5a7, 0x1d5c1), # MATHEMATICAL SANS-SERIF ITALIC
	('Tučné Kurzíva bezpatkové Matematické', 0x1d5db, 0x1d5f5), # MATHEMATICAL SANS-SERIF BOLD ITALIC
	('S pevnou šířkou Matematické', 0x1d60f, 0x1d629), # MATHEMATICAL MONOSPACE
	('zakroužkované', 0x2455, 0x246f), # CIRCLED
	('v závorke', None, 0x243b), # PARENTHESIZED
)

# Path to the folder where this script is located in
folder = os.path.dirname(__file__)

graphs = {}
# Load the original graphs
print("Loading graphs from file...")
with open(os.path.join(folder, "graph.txt"), encoding="utf-8") as f:
	lineCounter = 0
	for line in f:
		line = line.strip()
		if not line:
			continue
		try:
			(symbol, type) = line.split(" ")
		except:
			print ("Invalid text at line %d, %s"%(lineCounter, line))
			continue
		if len(symbol) !=1 or len(type) != 1:
			print ("Invalid text at line %d, %s"%(lineCounter, line))
			continue
		graphs[symbol] = type

def getTranscription(str):
	inStr="<speak xml:lang=\""+lang2+"\"><s>"+str+"</s></speak>"
	res=subprocess.run([os.path.join(folder, "../../../local/bin/RHVoice-transcribe-sentences"), "/dev/stdin", "/dev/stdout"], capture_output=True, input=inStr, text=True)
	res=res.stdout.strip()
	if res.startswith("pau "):
		res=res[4:]
	if res.endswith(" pau"):
		res=res[:-4]
	return res

def getCharSpelling(str):
	if len(str) != 1:
			return ''
	try:
		if int(str) >= 0:
			re_match = re.compile(r"%s\s?\:\s?(\w+)"%str)
	except:
		re_match = re.compile(r"\%" + r"%s\s?\:\s?\[?(\w*)\]?\s"%re.escape(str))
	with open(os.path.join(folder, "spell.foma"), 'r+') as f:
		data = mmap.mmap(f.fileno(), 0).read().decode("utf-8")
		mo = re_match.search(data)
		if mo:
			return mo.group(1)
	return ''

def errExit(msg):
	print("Error: "+msg)
	exit(1)

def appendLists(lowcaseChar, upcaseChar, nativeStr, descStr):
	lseqStr=getTranscription(descStr)
	if not len(lseqStr):
		errExit("Can not generate transcription for description '%s'" %(descStr))
	if lowcaseChar and nativeStr and not nativeStr in translitDict.keys():
		translitDict[nativeStr] = []
	try:
		nativeStrTok = nativeStr[:1]
	except:
		nativeStrTok = ''
	if lowcaseChar and nativeStrTok and not nativeStrTok in translitTokDict.keys():
		translitTokDict[nativeStrTok] = []
	if (lowcaseChar or upcaseChar) and descStr and not descStr in spellDict.keys():
		spellDict[descStr] = []
	if lowcaseChar and not lseqStr in lseqDict.keys():
		lseqDict[lseqStr] = []
	if nativeStr and lowcaseChar:
		translitDict[nativeStr].append("%"+lowcaseChar)
	if nativeStrTok and lowcaseChar:
		translitTokDict[nativeStrTok].append("%"+lowcaseChar)
	if descStr and lowcaseChar:
		spellDict[descStr].append("%"+lowcaseChar)
	if lowcaseChar:
		lseqDict[lseqStr].append("%"+lowcaseChar)
	if upcaseChar and upcaseChar != lowcaseChar and not ord(upcaseChar) in range(ord("A"), ord("Z") +1):
		if lowcaseChar:
			downcaseParts.append("%"+upcaseChar+" -> %"+lowcaseChar+" || _ ")
		if nativeStr:
			translitDict[nativeStr].append("%"+upcaseChar)
		if nativeStrTok:
			translitTokDict[nativeStrTok].append("%"+upcaseChar)
		if descStr:
			spellDict[descStr].append("%"+upcaseChar)

	if not nativeStr:
		return
	if nativeStr in graphs:
		chType=graphs[nativeStr]
	else:
		chType="c"
	if lowcaseChar:
		graphs[lowcaseChar]=chType
	if upcaseChar and ord(upcaseChar) >=255:
		graphs[upcaseChar]=chType

def writeFoma(fileName, content):
	with open("unicode_"+fileName+".foma", "w") as fi:
		fi.write("#Do not edit, file automatically generated by genunicode.py\n#\n"+content)

translitDict={}
translitTokDict={}
lseqDict={}
spellDict={}
translitParts=[]
translitTokParts=[]
downcaseParts=[]
lseqParts=[]
spellParts=[]
for i in range(ord("a"), ord("z") +1):
	baseChar = chr(i)
	if baseChar not in baseCharSpelling.keys():
		print("Missing spelling for base character '%s'"%baseChar)
		continue
	for combiningAccent in accentSuffixes.keys():
		normalized = unicodedata.normalize("NFC", baseChar +combiningAccent)
		if len(normalized) !=1: # is not composed to a single unicode character
			continue
		if normalized in graphs.keys():
			print("Skipping symbol '%s', %s. It's already included in graphs."%(normalized, unicodedata.name(normalized)))
			continue
		lowcaseChar = normalized
		upcaseChar = normalized.upper()
		if len(upcaseChar) != 1: # some capital letters don't have composed form.
			upcaseChar = ''
		nativeStr = baseChar
		descStr = " ".join((baseCharSpelling[baseChar], accentSuffixes[combiningAccent]))
		appendLists(lowcaseChar, upcaseChar, nativeStr, descStr)
		for combiningAccent2 in accentSuffixes.keys():
			normalized = unicodedata.normalize("NFC", baseChar +combiningAccent +combiningAccent2)
			if len(normalized) !=1: # is not composed to a single unicode character
				continue
			lowcaseChar = normalized
			upcaseChar = normalized.upper()
			nativeStr = baseChar
			descStr = " ".join((baseCharSpelling[baseChar], accentSuffixes[combiningAccent], "a", accentSuffixes[combiningAccent2]))
			print(descStr)
			appendLists(lowcaseChar, upcaseChar, nativeStr, descStr)
	for fontType in unicodeMath:
		try:
			lowcaseChar = chr(i +fontType[2])
		except:
			lowcaseChar = ''
		lowcaseCharName = ''
		try:
			lowcaseCharName = unicodedata.name(lowcaseChar)
		except:
			lowcaseChar = ''
		try:
			upcaseChar = chr(i +fontType[1])
		except:
			upcaseChar = ''
		upcaseCharName = ''
		try:
			upcaseCharName = unicodedata.name(upcaseChar)
		except:
			upcaseChar = ''
		if not lowcaseChar and not upcaseChar:
			continue
		print(" ".join((upcaseCharName, lowcaseCharName)))
		nativeStr = baseChar
		descStr = " ".join((baseCharSpelling[baseChar], fontType[0]))
		appendLists(lowcaseChar, upcaseChar, nativeStr, descStr)

for charStr, descStr in accentNames.items():
	latinExceptions[charStr] = ('', descStr)
for charStr, preformatted in latinExceptions.items():
	lowcaseChar = charStr
	if not lowcaseChar:
		continue
	try:
		upcaseChar = lowcaseChar.upper()
	except:
		upcaseChar = ''
	if upcaseChar and upcaseChar == lowcaseChar:
		upcaseChar = ''
	nativeStr = preformatted[0]
	descStr = preformatted[1]
	appendLists(lowcaseChar, upcaseChar, nativeStr, descStr)

for num in range(33, 127):
	char = chr(num)
	if char.isupper():
		#print("Skipping uppercase letter %s"%char)
		continue
	if char in baseCharSpelling.keys():
		#print("Smal letter %s"%char)
		nativeStr = char
		lowcaseChar = chr(ord(char) +fullWidthOffset)
		try:
			upcaseChar = lowcaseChar.upper()
		except:
			upcaseChar = ''
		if upcaseChar and upcaseChar == lowcaseChar:
			upcaseChar = ''
		descStr = " ".join((baseCharSpelling[char], fullWidth))
		appendLists(lowcaseChar, upcaseChar, nativeStr, descStr)
		continue
	spelling = getCharSpelling(char)
	if spelling:
		#print("Have spelling %s"%spelling)
		nativeStr = ''
		lowcaseChar = chr(ord(char) +fullWidthOffset)
		upcaseChar = ''
		descStr = " ".join((spelling, fullWidth))
		appendLists(lowcaseChar, upcaseChar, nativeStr, descStr)
	else:
		print("Unknown %s"%char)

for nativeStr in translitDict.keys():
	if not translitDict[nativeStr]:
		continue
	translitParts.append("[" + "|".join(translitDict[nativeStr]) + "] -> {"+nativeStr+"} || _ ")
for nativeStrTok in translitTokDict.keys():
	if not translitTokDict[nativeStrTok]:
		continue
	translitTokParts.append("[" + "|".join(translitTokDict[nativeStrTok]) + "] -> "+nativeStrTok+" || _ ")
for descStr in spellDict.keys():
	if not spellDict[descStr]:
		continue
	spellParts.append("[[" + "|".join(spellDict[descStr]) + "]:["+descStr+"]]")
for lseqStr in lseqDict.keys():
	if not lseqDict[lseqStr]:
		continue
	lseqParts.append("[" + "|".join(lseqDict[lseqStr]) + "]:["+lseqStr+"]")
writeFoma("norm", """#For pg2p:
define NormalizeCharactersBase \n"""\
+",,\n".join(translitParts)+";\n")

writeFoma("tok", """#For tok (character(s) to single letter):
define UnicodeToNativeTranslitTok \n"""\
+",,\n".join(translitTokParts)+";\n")

writeFoma("spell", """#For spelling:
define UnicodeSpell \n"""\
+"|\n".join(spellParts)+";\n")

writeFoma("lseq", """#For lseq:
define UnicodeLseq \n"""\
+"|\n".join(lseqParts)+";\n")

writeFoma("downcase", """#For downcase:
define UnicodeDowncase \n"""\
+",,\n".join(downcaseParts)+";\n")

with open("../../../data/languages/"+lang+"/graph.txt", "w", encoding="utf-8") as fi:
	for ch, chType in graphs.items():
		if ord(ch) >= 0x1d400: # RHVoice can't decode these
			continue
		fi.write(ch+" "+chType+"\n")

print("Unicode characters definitions generated.\n")
print("Recompile downcase, pg2p, lseq, spell and tok.foma.")
