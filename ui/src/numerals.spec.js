import test from 'ava';
import { CU_TITLO, CU_THOUSAND, cu_parse_int, cu_format_int, _place_titlo } from './numerals.js';

const TO_TEST = [
    [0, '0҃'],
    [1, 'а҃'],
    [2, 'в҃'],
    [3, 'г҃'],
    [4, 'д҃'],
    [5, 'є҃'],
    [6, 'ѕ҃'],
    [7, 'з҃'],
    [8, 'и҃'],
    [9, 'ѳ҃'],
    [10, 'і҃'],
    [11, 'а҃і'],
    [12, 'в҃і'],
    [13, 'г҃і'],
    [14, 'д҃і'],
    [15, 'є҃і'],
    [16, 'ѕ҃і'],
    [17, 'з҃і'],
    [18, 'и҃і'],
    [19, 'ѳ҃і'],
    [20, 'к҃'],
    [30, 'л҃'],
    [40, 'м҃'],
    [50, 'н҃'],
    [60, 'ѯ҃'],
    [70, 'ѻ҃'],
    [80, 'п҃'],
    [90, 'ч҃'],
    [100, 'р҃'],
    [200, 'с҃'],
    [300, 'т҃'],
    [400, 'у҃'],
    [500, 'ф҃'],
    [600, 'х҃'],
    [700, 'ѱ҃'],
    [800, 'ѿ҃'],
    [900, 'ц҃'],
    [1000, '҂а҃'],
    [1001, '҂а҃а'],
    [1010, '҂а҃і'],
    [1100, '҂а҃р'],
    [1110, '҂ар҃і'],
    [1800, '҂а҃ѿ'],
    [10000, '҂і҃'],
    [10002, '҂і҃в'],
    [10010, '҂і҃і'],
    [10100, '҂і҃р'],
    [11000, '҂а҃҂і'],
    [11100, '҂а҃і р҃'],
    [10800, '҂і҃ѿ'],
    [123, 'рк҃г'],
    [1234, '҂асл҃д'],
    [12345, '҂в҃і тм҃є'],
    [123456, '҂рк҃г ун҃ѕ'],
    [1234567, '҂҂а҃ ҂сл҃д фѯ҃з'],
    [12345678, '҂҂в҃і ҂тм҃є хѻ҃и'],
    [123456789, '҂҂рк҃г ҂ун҃ѕ ѱп҃ѳ'],
    [1234567890, '҂҂҂а҃ ҂҂сл҃д ҂фѯ҃з ѿч҃'],

    [111, 'ра҃і'],
    [121, 'рк҃а'],
    [800, 'ѿ҃'],
    [820, 'ѿк҃'],
    [1860, '҂аѿѯ҃'],

    [1010, '҂а҃і'],
    [11000, '҂а҃҂і'],
    [1981, '҂ацп҃а'],

    [1234567890123, '҂҂҂҂а҃ ҂҂҂сл҃д ҂҂фѯ҃з ҂ѿч҃ рк҃г'],
    [3423000, '҂҂г҃ ҂у҂к҃҂г'],
    [2464811, '҂҂в҃ ҂уѯ҃д ѿа҃і'],
    [8447775, '҂҂и҃ ҂ум҃з ѱѻ҃є'],
    [3800000, '҂҂г҃ ҂ѿ҃'],
    [3803000, '҂҂г҃ ҂ѿ҂г҃'],
]

const TO_TEST_OLD_DIALECT = [
    [0, '0҃'],
    [1, 'а҃'],
    [2, 'в҃'],
    [3, 'г҃'],
    [4, 'д҃'],
    [5, 'є҃'],
    [6, 'ѕ҃'],
    [7, 'з҃'],
    [8, 'и҃'],
    [9, 'ѳ҃'],
    [10, 'і҃'],
    [11, 'а҃і'],
    [12, 'в҃і'],
    [13, 'г҃і'],
    [14, 'д҃і'],
    [15, 'є҃і'],
    [16, 'ѕ҃і'],
    [17, 'з҃і'],
    [18, 'и҃і'],
    [19, 'ѳ҃і'],
    [1000, '҂а҃'],
    [1001, '҂а҃а'],
    [1010, '҂а҃і'],
    [1100, '҂а҃р'],
    [1110, '҂ар҃і'],
    [1800, '҂а҃ѿ'],
    [10000, '҂і҃'],
    [10002, '҂і҃в'],
    [10010, '҂і҃і'],
    [10100, '҂і҃р'],
    [11000, '҂а҃҂і'],
    [11100, '҂а҂і҃р'],
    [10800, '҂і҃ѿ'],
    [123, 'рк҃г'],
    [1234, '҂асл҃д'],
    [12345, '҂в҂ітм҃є'],
    [123456, '҂р҂к҂гун҃ѕ'],
    [1234567, '҂҂а҃ ҂с҂л҂дфѯ҃з'],
    [12345678, '҂҂в҃і ҂т҂м҂єхѻ҃и'],
    [123456789, '҂҂рк҃г ҂у҂н҂ѕѱп҃ѳ'],
    [1234567890, '҂҂҂а҃ ҂҂сл҃д ҂ф҂ѯ҂зѿч҃'],

    [111, 'ра҃і'],
    [121, 'рк҃а'],
    [800, 'ѿ҃'],
    [820, 'ѿк҃'],
    [1860, '҂аѿѯ҃'],

    [1010, '҂а҃і'],
    [11000, '҂а҃҂і'],

    [1234567890123, '҂҂҂҂а҃ ҂҂҂сл҃д ҂҂фѯ҃з ҂ѿ҂чрк҃г'],
    [3423000, '҂҂г҃ ҂у҂к҃҂г'],
    [2464811, '҂҂в҃ ҂у҂ѯ҂дѿа҃і'],
    [8447775, '҂҂и҃ ҂у҂м҂зѱѻ҃є'],
];

function assertGood(t, num, string, opts = {}) {
    const { dialect = 'standard' } = opts;
    const formatted = cu_format_int(num, { dialect }).replaceAll('\xa0', ' ');
    t.is(formatted, string);
    t.is(cu_parse_int(string), num);
}

test('parser and formatter (standard dialect)', t => {
    for (const [num, string] of TO_TEST) {
        assertGood(t, num, string);
    }
});

test('parser and formatter (old dialect)', t => {
    for (const [num, string] of TO_TEST_OLD_DIALECT) {
        assertGood(t, num, string, { dialect: 'old' });
    }
});

test('no titlo', t => {
    t.is(cu_format_int(11100, { add_titlo: false }).replace('\xa0', ' '), '҂аі р');
});

test('other', t => {
    t.not(cu_format_int(1010), cu_format_int(11000));

    t.is(cu_format_int(1010), '҂а҃і');
    t.is(cu_format_int(11000), '҂а҃҂і');

    t.is(cu_format_int(1010, { dialect: 'old' }), '҂а҃і');
    t.is(cu_format_int(11000, { dialect: 'old' }), '҂а҃҂і');
});

test('crazy', t => {
    t.is(cu_format_int(1234567890123).replaceAll('\xa0', ' '), '҂҂҂҂а҃ ҂҂҂сл҃д ҂҂фѯ҃з ҂ѿч҃ рк҃г');
    t.is(cu_format_int(1234567890123, { dialect: 'old' }).replaceAll('\xa0', ' '), '҂҂҂҂а҃ ҂҂҂сл҃д ҂҂фѯ҃з ҂ѿ҂чрк҃г');
});

test('negative', t => {
    t.is(cu_format_int(-1010), '-҂а҃і');
    t.is(cu_format_int(-1010, { dialect: 'old' }), '-҂а҃і');
});

test('all up to 10,000', t => {
    for (let i = 0; i < 10000; i++) {
        let j = cu_parse_int(cu_format_int(i));
        t.is(i, j);
        j = cu_parse_int(cu_format_int(i, { add_titlo: false }));
        t.is(i, j);
    }
});

test('all up to 10,000 (old dialect)', t => {
    for (let i = 0; i < 10000; i++) {
        let j = cu_parse_int(cu_format_int(i, { dialect: 'old' }));
        t.is(i, j);
        j = cu_parse_int(cu_format_int(i, { add_titlo: false, dialect: 'old' }));
        t.is(i, j);
    }
});

function randInt(from, to) {
    return from + Math.floor((to + 1 - from) * Math.random());
}

test('random', t => {
    for (let i = 0; i < 10000; i++) {
        let i = randInt(10000, 10000000);
        let j = cu_parse_int(cu_format_int(i));
        t.is(i, j);
        j = cu_parse_int(cu_format_int(i, { add_titlo: false }));
        t.is(i, j)
    }
});

test('random (old dialect)', t => {
    for (let i = 0; i < 10000; i++) {
        let i = randInt(10000, 10000000);
        let j = cu_parse_int(cu_format_int(i, { dialect: 'old' }));
        t.is(i, j);
        j = cu_parse_int(cu_format_int(i, { add_titlo: false, dialect: 'old' }));
        t.is(i, j)
    }
});


test('insert titlo', t => {
    let group = CU_THOUSAND + 'а' + CU_THOUSAND + 'і';
    let titlo_group = _place_titlo(group);
    t.is(titlo_group, CU_THOUSAND + 'а' + CU_TITLO + CU_THOUSAND + 'і');
});
