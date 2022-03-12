# Data preparation

Here we use CU book corpora to collect words. We then convert words to civic script
and create a training set `cu-words-civic.txt`.

## Build `cu-books.txt` corpus
Parse [cu-books corpus of XML files](https://github.com/slavonic/cu-books)
and build a text file with no XML markup, with
with one paragraph per line. Books separated with an empty line. Call it `cu-books.txt`.
Note that all text within `cu-books.txt` is in Church Slavonic Script.

```bash
python -m parse_cu_books -r <root_directory> -o cu-books.txt
```

## Build `elis.txt` corpus
Parse [Elisabeth Bible corpus](https://github.com/typiconman/ponomar/tree/master/Ponomar/languages/cu/bible/elis)
and build a text with no XML markup, as above.

```bash
python -m parse_elis -r <root_directory> -o elis.txt
```

## Build list of CU words `cu-words.txt`
Take text corpora form the prevoius steps and collect all words. Remove punctuation.
Count unique occurences. Create file `cu-words.txt`, each line that contains CU word and
its count separated with TAB.

```bash
python -m make_words -i cu-books.txt elis.txt -o cu-words.txt
```

## Build list of CU words with expanded titlo `cu-words-untitlo.txt`
Takes `cu-words.txt` and tries its best to convert CU word to "expanded" form (where
titlo-ed acronyms are detected). Output has three fields TAB-separated: original CU word,
expanded CU word, and frequency count.

```bash
python -m untitlo -i cu-words.txt -o cu-words-untitlo.txt
```

## Build training dataset (pairs of CU and Civic)
Read `cu-word-untitlo.txt` and generate civic variant of each un-titlo'ed word.
Result is written to `cu-words-civic.txt`.

```bash
python -m tocivic -i cu-words-untitlo.txt -o cu-words-civic.txt
```

Resulting file looks like this:
```
ѕѣ̑ницы	зе́ницы	4
ѕѣла̀	зела́	31
ѕѣло̀	зело́	1
```

## Building dedup'ed dataset (pairs of CU and Civic)
Several different CU spellings may map to the same civic one. So we have a choice which
CU to use for a particular RU word.

This step finds the most common CU spellings and throws away all less common ones. The output
file `cu-words-civic-dedup.txt` contains unambiguous mappings from RU to CU.

This file is used as a `cheatMap` to bypass predictor when input RU word is found in the map.

