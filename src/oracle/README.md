# Oracle

Oracle is a Chinese Character concise shape-based input method.

Oracle is designed to remove flow-interrupting character choice menus by ensuring that each character has just one fast way to type it.

Because oracle is shape-based, every chinese character has a unique way to type it, so you don't ever need to select from character menus ever again and break your typing flow.

## Compiling the dictionary

```
$ python oracle.py gen-dict
$ cp dict.txt <path-to-your-ime-folder>
```


## Learning Oracle

Oracle is at its core stroke-based character input. There are 5 basic strokes:

| input | output possibilities              |
|-------|-----------------------------------|
| -     | 一,㇀                             |
| /     | 丿                                |
| \     | 丶,乀                             |
| l     | 丨,亅                             |
| v     | Angular 7 shapes (乛,㇈,𠃌,㇇,⺄) |
| v     | Angular L shapes (𠄌,𠃊,乚,𠃋,㇂) |
| v     | Angular shapes (ㄣ,㇉)            |

## Edge cases
You'll sometimes find characters with the same stroke AND shape pattern

### How to use it?

The goal of this IME is as follows:
1. *Unique input*. Since sinographs are fundamentally strokes and shapes, this is a stroke & shape input method
1. *Fast input*. We create shortcuts for the most common character patterns. Each character takes at most 6 keyboard strokes to type.
1. *Easy to learn*. Everything you need to type Oracle accurately is below.

#### Rules
1. All characters have shortcuts of less than 6 keystrokes. If a character seems to be >6 chars, type the first 3 characters, `'`, then the first keystroke of the final shape. If you aren't sure, you can always type the full character out.
2. 
