import { Tensor, InferenceSession } from "onnxruntime-web";
import { CTCBeamSearch, Vocabulary } from 'ctc-beam-search';

export class Predictor {
    constructor(session, voc, cheatMap) {
        this.session = session;
        this.voc = voc;
        this.cheatMap = cheatMap || {};
        this.voclen = Object.keys(voc.indexToChar).length;
    }

    static async load(modelName, vocabName, blankIndex = 0, cheatListName) {
        const session = await InferenceSession.create(modelName);
        const vocab = await (await fetch(vocabName)).json();
        const voc = new Vocabulary(vocab, blankIndex);
        const cheatMap = {};
        if (cheatListName !== undefined) {
            const cheatText = await (await fetch(cheatListName)).text();
            let count = 0;
            for (const line of cheatText.split('\n')) {
                const [cu, ru] = line.trim().split('\t').map(x => x.trim());
                if (cu !== undefined && ru !== undefined) {
                    cheatMap[ru] = cu;
                    count += 1;
                }
            }

            // some unaccented RU entries in the corpus are mapped to unaccented CU
            // (свѧтагѡ -> святаго). We prefer accented version, hence overwrite here...
            for (const [ru, cu] of Object.entries(cheatMap)) {
                const ruNoAccent = ru.replace('\u0301', '');
                if (ru !== ruNoAccent) {
                    cheatMap[ruNoAccent] = cu;
                }
            }
            console.log(`Loaded ${count} cheat map entries`);
        }
        return new Predictor(session, voc, cheatMap);
    }

    async predict(text) {
        if (this.cheatMap[text] !== undefined) {
            return this.cheatMap[text];
        }

        if (text.length > 32) {
            text = text.slice(0, 32); // input text too long (can only take up to 32 chars)
        }
        const inputsArray = new Int32Array(32);
        inputsArray.fill(0);
        const accentsArray = new Int32Array(32);
        accentsArray.fill(0);

        text = text.replace(/'/g, '\u0301')
        const accentsIndex = text.indexOf('\u0301');
        text = text.replace(/\u0301/g, '')
        if (accentsIndex > 0) {
            accentsArray[accentsIndex - 1] = 1;
        }
        for (let i = 0; i < text.length; i++ ) {
            const c = text[i];
            const index = this.voc.charToIndex[c];
            if (index === undefined) {
                throw new Error('input text contains unsupported character ' + c);
            }
            inputsArray[i] = index;
        }
        const inputs = new Tensor(inputsArray, [1, 32]);  // batch_size=1
        const accents = new Tensor(accentsArray, [1, 32]);
        const outputs = await this.session.run({ inputs, accents });
        const logits = [];
        for (let i = 0; i < 64; i++) {  // upsampled sequence length
            logits.push(outputs.logits.data.slice(i * this.voclen, i * this.voclen + this.voclen));
        }

        const bs = new CTCBeamSearch(this.voc);
        const results = bs.search(logits, 10); // beam width = 10
        // console.log(results);

        const output = decode(results[0], this.voc);

        return output;
    }
}

function decode(beam, voc) {
    const indices = beam.seq.filter(x => x != voc.blankIndex);
    return indices.map(i => voc.indexToChar[i]).join('');
}