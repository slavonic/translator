<script>
    import { Predictor } from './predictor.js';
    import { Debounce } from './debounce.js';
    import { onMount, tick } from 'svelte';

    const PLACEHOLDER = 'Набираем текст гражданским шрифтом здесь. Например: во имя отца и сына и святаго духа, аминь';

    let predictor;

    onMount(async () => {
        predictor = await Predictor.load('build/model.onnx', 'build/vocab.json', 0, 'build/cu-words-civic-dedup.txt');
        console.log('Predictor loaded!');
    });

    async function sleep(millis) {
        return new Promise( resolve => setTimeout(resolve, millis) );
    }

    let translation = [];
    let scrollable;
    const cache = {};

    async function engine(text, casing) {
        await tick();
        const pieces = text.split(RU_TEXT_SPLITTER);

        translation.length = 0;
        translation = translation;

        for (const piece of pieces) {
            const lowerPiece = piece.toLowerCase();
            let t;
            if (!RU_TEXT_TESTER.test(piece)) {
                t = mapPunctuation(piece);
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

    function mapPunctuation(text) {
        text = text.replace(/\/\//g, ' *');
        text = text.replace(/\//g, ' *');
        text = text.replace(/;/g, '.');
        text = text.replace(/\?/g, ';');
        text = text.replace(/\s+/g, ' ');
        return text;
    }

    const debounce = new Debounce(engine);

    let userText = '';
    let casing = 'match';

    $: onUserTextChange(userText, casing);
    function onUserTextChange(userText, casing) {
        debounce.call(userText, casing);
    }
</script>

<main>
    <div>
        <h1>Переводилка</h1>
        <h2>(с гражданского шрифта на ЦСЯ)</h2>
        <div class="notes">
            Регистр:
            <input type="radio" bind:group={casing} value="match"> тот же
            <input type="radio" bind:group={casing} value="lower"> нижний
            <input type="radio" bind:group={casing} value="upper"> верхний
        </div>
    </div>
    <div class="slavonic border" bind:this={scrollable}>
        {#each translation as t}
            <span>{t}</span>
        {/each}
    </div>
    <div>
        {#if predictor === undefined}
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
        font-size: 3em;
        font-weight: 100;
        padding: 0;
        margin-top: 0;
        margin-bottom: 0.25em;
        text-align: center;
    }

    @media (min-width: 640px) {
        main {
            max-width: none;
        }
    }
    .slavonic {
        font-family: 'Ponomar Unicode';
        font-size: 120%;
        overflow: auto;
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
        margin-top: 10%;
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

</style>