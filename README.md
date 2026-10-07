# Oṅeβoard

Type anything.

<img src="docs/res/images/symboard_support_current.png" alt="drawing" width="800"/>

## Why?

It's needlessly hard to type! Symbols like θ, π, and √ are incredibly common in handwriting. And yet, almost impossible to type on a computer. This isn't just a problem in math, but also in linguistics, and for bilingual people.
You shouldn't have to learn a new keyboard layout for every new language, or look up where to find θ on your keyboard. Or worse yet, google a symbol and copy-paste.

**This keyboard makes it easy to type. Even symbols.**

**If you study math, you can type math symbols. If you're bilingual, you can type in your other language. If you study linguistics, you can type linguistics notation.**

## How?

There are 2 ways to type:
1. Type-by-shape: Type characters by using visually similar characters
2. Type-by-sound: Type characters by how they sound

We use a universal sound system (romanization), which maps to the letters in every other alphabet.

Any combining characters, like the accent marks in á and ä, can be found above graphically similar charcters, so that ȧ = a + .

Therefore, if i want to type russian but i don't know how to write it, that i can close my eyes and type russian. I'd type "andrej" and get "андрей".

### Design tenets

This keyboard was designed according to the following tenets:

1. *Make typing in english fast, comfortable, and low-effort*
  - The alphabet is arranged in the Dvorak layout. Common English punctuation is all in the lower 3 rows
2. *Support other common symbols in an intuitive way (EG greek, cyrillic, arrows, math symbols, japanese)*
  - Use a universal romanization system that maps all non-latin characters to similar sounding latin letters. For example, ك = k, к = k, and か = k + a.
  - Diacritics are placed near or above graphically similar characters. For example, ȧ = a + .

## Layout

The basic layout is as follows:

<img src="docs/res/images/basic_layout.png" alt="drawing" width="400"/>

Pressing the shift and alt keys will provide access to different key sets, including modifier keys. These are presented below.

|                    | Shift not pressed                                                       | Shift pressed                                                        |
|--------------------|-------------------------------------------------------------------------|----------------------------------------------------------------------|
| **Alt not pressed** | <img src="docs/res/images/basic_layout.png" alt="drawing" width="300"/> | <img src="docs/res/images/shift.png" alt="drawing" width="300"/>     |
| **Alt pressed**      | <img src="docs/res/images/alt.png" alt="drawing" width="300"/>          | <img src="docs/res/images/alt_shift.png" alt="drawing" width="300"/> |


## Compatibility

Below is a map of the world showing the countries where some or all of the administrative languages can be written using Symboard.

<img src="docs/res/images/symboard_support_current.png" alt="drawing" width="800"/>

This keyboard is compatible with (at least) the following scripts:

Albanian, Arabic, romanization (ALA-LC; ISO), Arabic, Asturian, Azerbaijani, Belarusian, Bengali, Bosnian (cyrllic; latin scripts), Breton, Bulgarian, Burmese, Chinese (traditional), Chinese (simplified), Chinese (pinyin), Cyrillic (romanization, ISO 9), Czech, Danish, Dutch, Dzongkha, English, Esperanto, Estonian, Faroese, Farsi / Dari / Persian, Filipino, French, Galician, Ge'ez, Georgian (mkhedruli), German, Greenlandic, Hawaiian, Hebrew, Hindi, Hungarian, Icelandic, Irish, Italian, Japanese (romaji; hepburn, nihonshiki, kunrei), Khmer, Korean, Kurdish, Kurdish (arabic), Lakota, Lao, Latvian, Lithuanian, Macedonian, Manx, Mongolian (cyrillic; mongolian), Montenegrin, Māori, Nepalese, Norwegian (bokmal, nynorsk), Pashto, Polish, Portuguese, Qazaq (latin script), Romanian, Russian, Scottish Gaelic, Serbian, Slovak, Slovenian, Sinhala, Spanish, Swedish, Tamil, Thai, Tibetan, Tifinagh, Turkish, Ukrainian, Urdu, Uzbek, Vietnamese, Welsh

## FAQ

#### Problem 1
Many non-latin alphabets have letters for sounds that latin doesn't have, especially sounds like "ts", "ch", "zh", and "sh".
*Solution*: Use the universal romanization scheme, and allow typing of diacritics. To get russian "ц", type "ts". To get "тс", type "t-s". Common sounds like "sh" are simply "x".

#### Problem 2
Languages have messy writing systems. English has 3 letters that all make the /k/ sound (q; k; c), and many languages also have the same kind of problem. 
*Solution*: For these cases, we use "t", "t1" and "t2", and which one is which will be sorted alphabetically. So in English, you can imagine that "c" maps to "k", "k" maps "k1", and "q" maps to "k2".

#### Example 1
- Perso-Arabic script has a /gh/ sound and a /g/ sound.
- Greek has a single letter which can sound like /gh/ or /g/.
Therefore, Greek would allow you to simply type /g/, But in perso-arabic script, there is a separate letter for /g/ and /gh/. So you would have to distinguish the two when you write Persian.
