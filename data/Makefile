.PHONY: all untitlo tocivic dedup

all: cu-words-civic-dedup-accent.txt cu-words-civic-dedup.txt cu-words-civic.txt cu-words-untitlo.txt cu-words-errata.txt

cu-words-civic-dedup-accent.txt: accent.py cu-words-civic-dedup.txt accent-addendum.txt
	echo "Accent"
	python -m accent

cu-words-civic-dedup.txt: dedup.py cu-words-civic.txt
	echo "Dedup"
	python -m dedup

cu-words-civic.txt: tocivic.py cu-words-untitlo.txt
	echo "Converting to civic form"
	python -m tocivic

cu-words-untitlo.txt: untitlo.py cu-words-errata.txt
	echo "Expanding titlo"
	python -m untitlo

cu-words-errata.txt: errata.py cu-words.txt
	echo "Apply errata"
	python -m errata
