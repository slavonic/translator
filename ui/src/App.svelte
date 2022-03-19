<script>
    import { Predictor } from './predictor.js';
    import { Debounce } from './debounce.js';
    import { onMount, tick } from 'svelte';
    import { cu_format_int } from './numerals.js';

    const urlParams = new URLSearchParams(window.location.search);
    const isDebug = urlParams.has('debug');

    const PLACEHOLDER = `Набираем текст в гражданской орфографии здесь. Например: во имя отца и сына и святаго духа, аминь

Для ударений можно использовать символ одиночной правой кавычки ( ' ).

Напоминаем, что перевод не 100% правильный и требуется вычитка результата.
`;

    let predictor;

    onMount(async () => {
        predictor = await Predictor.load(
            'build/model.onnx',
            'build/vocab.json',
            0,
            'build/cu-words-civic-dedup.txt',
            isDebug
        );
        console.log('Predictor loaded!');
    });

    async function sleep(millis) {
        return new Promise( resolve => setTimeout(resolve, millis) );
    }

    let translation = [];
    let scrollable;
    const cache = {};

    async function engine(text, casing, numerals) {
        await tick();
        const pieces = text.split(RU_TEXT_SPLITTER);

        translation.length = 0;
        translation = translation;

        for (const piece of pieces) {
            const lowerPiece = piece.toLowerCase();
            let t;
            if (!RU_TEXT_TESTER.test(piece)) {
                t = mapPunctuation(piece, numerals);
            } else if (cache[lowerPiece] !== undefined) {
                t = cache[lowerPiece];
            } else {
                await sleep(0);
                t = await predictor.predict(lowerPiece);
                cache[lowerPiece] = t;
            }

            if (casing === 'match') {
                t = maybeRestoreCaps(piece, t);
            } else if (casing === 'lower') {
                t = t.toLowerCase();
            } else if (casing === 'upper') {
                t = t.toUpperCase();
            }
            translation.push(t);

            translation = translation;
            scrollable.scrollTop = scrollable.scrollHeight;
        }
    }

    const RU_TEXT = '[абвгдежзийклмнопрстуфхцчшщьыъэюя\u0301\']+';
    const RU_TEXT_SPLITTER = new RegExp(`(${RU_TEXT})`, 'i');
    const RU_TEXT_TESTER = new RegExp(`^${RU_TEXT}$`, 'i');
    const NUM_SPLITTER = /(\d+)/;

    function maybeRestoreCaps(text, translation) {
        if (text.toLowerCase() === text) {
            return translation;
        } else if (text.toUpperCase() == text) {
            return translation.toUpperCase();
        } else if (text[0].toUpperCase() == text[0] && text.slice(1).toLowerCase() == text.slice(1)) {
            // title case
            return translation[0].toUpperCase() + translation.slice(1);
        } else {
            console.log('Donno..', text, translation);
            return translation;
        }
    }

    function mapPunctuation(text, numerals) {
        text = text.replace(/\/\//g, ' *');
        text = text.replace(/\//g, ' *');
        text = text.replace(/;/g, '.');
        text = text.replace(/\?/g, ';');
        text = text.replace(/\s+/g, ' ');

        if (!numerals) {
            return text;
        }

        const pieces = text.split(NUM_SPLITTER).map(piece => {
            if (/^\d+$/.test(piece)) {
                return cu_format_int(+piece);
            } else {
                return piece;
            }
        });

        return pieces.join('');
    }

    const debounce = new Debounce(engine);

    let userText = '';
    let casing = 'match';
    let numerals = true;

    $: onUserTextChange(userText, casing, numerals);
    function onUserTextChange(userText, casing, numerals) {
        debounce.call(userText, casing, numerals);
    }
</script>

<main>
    <div>
        <h1>Переводилка</h1>
        <h2>(из гражданской в церковнославянскую орфографию)</h2>
        <div class="notes">
            Регистр:
            <input type="radio" bind:group={casing} value="match"> тот же
            <input type="radio" bind:group={casing} value="lower"> нижний
            <input type="radio" bind:group={casing} value="upper"> верхний
            <input type="checkbox" bind:checked={numerals}> цифирь
            <a class="src" href="https://github.com/slavonic/translator">github.com/slavonic/translator</a>
        </div>
    </div>
    <div class="slavonic border" bind:this={scrollable}>
        {#each translation as t}
            <span>{t}</span>
        {/each}
    </div>
    <div>
        {#if predictor === undefined}
        <div class="center">Подождите, идёт загрузка...</div>
        <div class="wrapper" style="--size:60px; --color:#FF3E00;">
                <div class="circle"
                    style="animation: 2.1s ease-in-out 1s infinite normal none running none;"
                >
                </div>
                <div class="circle" style="animation: 2.1s ease-in-out 0s infinite normal none running none;">
                </div>
            </div>
        {:else}
            <textarea placeholder={PLACEHOLDER} bind:value={userText} spellcheck="false"></textarea>
        {/if}
    </div>
</main>

<style>
    main {
        display: grid;
        grid-template-rows: auto 1fr 1fr;
        grid-gap: 1em;
        height: 100%;
        width: 100%;
/*
        text-align: center;
        max-width: 240px;
        margin: 0 auto; */
    }

    h1 {
        color: #ff3e00;
        font-size: 4em;
        font-weight: 100;
        margin: 0;
        text-align: center;
    }

    h2 {
        color: #ff3e00;
        font-size: 1.5em;
        font-weight: 200;
        padding: 0;
        margin-top: 0;
        margin-bottom: 0.25em;
        text-align: center;
    }

    @media (max-height: 640) {
        h2, h1 {
            display: none;
        }
    }
    .slavonic {
        font-family: 'Ponomar Unicode';
        font-size: 120%;
        overflow: auto;
        min-height: 50px;
    }

    textarea {
        width: 100%;
        font-size: 100%;
        height: 100%;
    }

    .border {
        padding: 5px;
        border-radius: 3px;
        border: 1px solid gray;
    }
    .notes {
        text-align: center;
        font-size: 80%;
    }
    .notes input {
        margin-right: 0;
        margin-left: 1em;
    }
    input[type="radio"] {
        margin-top: 5px;
        vertical-align: middle;
    }
    .wrapper {
        position: relative;
        margin-top: 5%;
        width: var(--size);
        height: var(--size);
        margin-left: auto;
        margin-right: auto;
    }
    .circle {
        position: absolute;
        width: var(--size);
        height: var(--size);
        background-color: var(--color);
        border-radius: 100%;
        opacity: 0.6;
        top: 0;
        left: 0;
        animation-fill-mode: both;
        animation-name: bounce !important;
    }
    @keyframes bounce {
        0%,
        100% {
            transform: scale(0);
        }
        50% {
            transform: scale(1);
        }
    }

    @media screen and (max-height: 480px) {
        h2, h1 {
            display: none;
        }
    }
    .src {
        display: block;
        font-size: 70%;
        color: gray;
    }

    .center {
        text-align: center;
    }
</style>