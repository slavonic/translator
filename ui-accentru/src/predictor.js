import { Tensor, InferenceSession } from "onnxruntime-web";
import { Vocabulary } from 'ctc-beam-search';

const VOWELS = 'аеиоуыэюя';

export class Predictor {
    constructor(session, voc, cheatMap, isDebug = false) {
        this.session = session;
        this.voc = voc;
        this.cheatMap = cheatMap || {};
        this.isDebug = isDebug;
        this.voclen = Object.keys(voc.indexToChar).length;
    }

    static async load(modelName, vocabName, cheatListName, isDebug = false) {
        const session = await InferenceSession.create(modelName);
        const vocab = await (await fetch(vocabName)).json();
        const voc = new Vocabulary(vocab);
        const cheatMap = {};
        if (cheatListName !== undefined) {
            const cheatText = await (await fetch(cheatListName)).text();
            let count = 0;
            for (const line of cheatText.split('\n')) {
                const word = line.trim();
                const accentIndex = word.indexOf('\u0301');
                cheatMap[word.toLowerCase()] = accentIndex - 1;
                count += 1;
            }
            console.log(`Loaded ${count} cheat map entries`);
        }
        return new Predictor(session, voc, cheatMap, isDebug);
    }

    async predict(text) {
        text = text.replace(/'/g, '\u0301')
        if (text.indexOf('\u0301') >= 0) {
            return text;  // respect the explicit accent
        }
        if (text.indexOf('ё') >= 0) {
            return text; // does not require prediction
        }

        const lowerText = text.toLowerCase();
        const numVowels = [...lowerText].filter(c => VOWELS.indexOf(c) >= 0).length;
        if (numVowels <= 1) {
            return text; // no accent in a single - vowel words
        }

        let accentIndex = this.cheatMap[lowerText];
        if (accentIndex === undefined || this.isDebug) {
            if (lowerText.length > 32) {
                lowerText = lowerText.slice(0, 32); // input text too long (can only take up to 32 chars)
            }
            const inputsArray = new Int32Array(32);
            inputsArray.fill(0);

            for (let i = 0; i < lowerText.length; i++) {
                const c = lowerText[i];
                const index = this.voc.charToIndex[c];
                if (index === undefined) {
                    throw new Error('input text contains unsupported character ' + c);
                }
                inputsArray[i] = index;
            }
            const inputs = new Tensor(inputsArray, [1, 32]);  // batch_size=1
            const outputs = await this.session.run({ inputs });
            let best = -100000.;
            accentIndex = 0;
            for (let i = 0; i < text.length; i++) {  // upsampled sequence length
                const [low, high] = outputs.logits.data.slice(i * 2, i * 2 + 2);
                if (high - low > best) {
                    accentIndex = i;
                    best = high - low;
                }
            }
        }

        text = text.slice(0, accentIndex + 1) + '\u0301' + text.slice(accentIndex + 1);

        return text;
    }
}
