<script>
    import { Predictor } from './predictor.js';
    import { Debounce } from './debounce.js';
    import { onMount, tick } from 'svelte';

    const urlParams = new URLSearchParams(window.location.search);
    const isDebug = urlParams.has('debug');

    const PLACEHOLDER = `Набираем текст в гражданской орфографии здесь. Например: во имя отца и сына и святаго духа, аминь

Для ударений можно использовать символ одиночной правой кавычки ( ' ).

Напоминаем, что расстановка не 100% правильная и требуется вычитка результата.
`;

    let predictor;

    onMount(async () => {
        predictor = await Predictor.load(
            'build/model-accent.onnx',
            'build/vocab-accent.json',
            'build/cu-words-civic-dedup-accent.txt',
            isDebug
        );
        console.log('Predictor loaded!', isDebug);
    });

    async function sleep(millis) {
        return new Promise( resolve => setTimeout(resolve, millis) );
    }

    function* split(regex, str) {
        let match;
        let offset = 0;
        while ((match = regex.exec(str)) !== null) {
            if (offset < match.index) {
                yield {
                    type: 'other',
                    text: str.slice(offset, match.index),
                }
            }
            yield {
                    type: 'match',
                    text: str.slice(match.index, match.index + match[0].length),
            }
            offset = match.index + match[0].length;
        }
        if (offset < str.length) {
            yield {
                type: 'other',
                text: str.slice(offset),
            }
        }
    }

    let translation = [];
    let scrollable;
    const cache = {};

    async function engine(text) {
        await tick();

        translation.length = 0;
        translation = translation;

        for (const chunk of split(RU_TEXT_SPLITTER, text)) {
            if (chunk.type === 'other') {
                translation.push(chunk.text);
            } else {
                let piece = chunk.text;
                let t;
                if (!RU_TEXT_TESTER.test(piece)) {
                    t = piece;
                } else if (cache[piece] !== undefined) {
                    t = cache[piece];
                } else {
                    await sleep(0);
                    t = await predictor.predict(piece);
                    cache[piece] = t;
                }
                translation.push(t);
            }

            translation = translation;
            scrollable.scrollTop = scrollable.scrollHeight;
        }
    }

    const RU_TEXT = '[абвгдежзийклмнопрстуфхцчшщьыъэюя\u0301\']+';
    const RU_TEXT_SPLITTER = new RegExp(`(${RU_TEXT})`, 'ig');
    const RU_TEXT_TESTER = new RegExp(`^${RU_TEXT}$`, 'i');
    const debounce = new Debounce(engine);

    let userText = '';

    $: onUserTextChange(userText);
    function onUserTextChange(userText) {
        debounce.call(userText);
    }
</script>

<main>
    <div>
        <h1>Расставляем</h1>
        <h2>ударения (в гражданской орфографии)</h2>
        <div class="notes">
            <a class="src" href="https://github.com/slavonic/translator">github.com/slavonic/translator</a>
        </div>
    </div>
    <div class="border accented" bind:this={scrollable}>{translation.join('')}</div>
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
        color: #54109d;
        font-size: 4em;
        font-weight: 100;
        margin: 0;
        text-align: center;
    }

    h2 {
        color: #54109d;
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

    textarea {
        width: 100%;
        font-size: 100%;
        font-family: sans-serif;
        height: 100%;
    }

    .border {
        padding: 5px;
        border-radius: 3px;
        border: 1px solid gray;
    }
    .accented {
        font-family: sans-serif;
        white-space: pre;
        max-height: 40vh;
        overflow: auto;
    }
    .notes {
        text-align: center;
        font-size: 80%;
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