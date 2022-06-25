/**
 * Support for Cyrillic Numerals
 * See UTN 41 for implementation information
 * http://www.unicode.org/notes/tn41/
 *
 * Code was based on C++ OpenOffice code by Aleksandr Andreev: https://gerrit.libreoffice.org/#/c/20013/
 * but eventually rewritten to implement more features.
 */
export const CU_THOUSAND = '\u0482';
export const CU_TITLO = '\u0483';
export const CU_800 = '\u047f';
export const CU_NBSP = '\u00a0';

const CU_NUMBER = new Map(Object.entries({
    '\u0446': 900,
    '\u047f': 800,
    '\u0471': 700,
    '\u0445': 600,
    '\u0444': 500,
    '\u0443': 400,
    '\u0442': 300,
    '\u0441': 200,
    '\u0440': 100,
    '\u0447': 90,
    '\u043f': 80,
    '\u047b': 70,
    '\u046f': 60,
    '\u043d': 50,
    '\u043c': 40,
    '\u043b': 30,
    '\u043a': 20,
    '\u0456': 10,
    '\u0473': 9,
    '\u0438': 8,
    '\u0437': 7,
    '\u0455': 6,
    '\u0454': 5,
    '\u0434': 4,
    '\u0433': 3,
    '\u0432': 2,
    '\u0430': 1,
}));

function invertMap(map) {
    return new Map([...map.entries()].map(([k, v]) => [v, k]));
}

const CU_DIGIT = invertMap(CU_NUMBER);

export function cu_format_int(value, opts = {}) {
    /**
     * Formats an integer: value: as Church Slavonic number(string).
     *
     * Parameters:
     *     : value: - the value to format(an int).
     *     : add_titlo: - if True(default ), adds titlo.
     *     : dialect: - controls how large numbers are generated.Default is "standard".
     **/
    const { add_titlo = true, dialect = 'standard' } = opts;

    if (!(dialect === 'standard' || dialect === 'old')) {
        throw new Error(`unknown dialect "${dialect}", expected one of: ["old", "standard"]`);
    }

    if (value < 0) {
        return '-' + cu_format_int(-value, { add_titlo, dialect });
    }

    if (value === 0) {
        if (add_titlo) {
            return '0' + CU_TITLO;
        } else {
            return '0';
        }
    }

    let groups = _format_thousand_groups(value);
    if (groups.length > 1) {
        if (groups[groups.length - 2].length === 1) {
            // merge groups - 1 and - 2, because only a single digit in groups[-2]
            groups[groups.length - 2] = groups[groups.length - 2] + groups[groups.length - 1];
            groups[groups.length - 1] = '';
        } else if (groups[groups.length - 2].length > 1 && (groups[groups.length - 1].length == 0 || dialect == 'old')) {
            // force thousand symbol before every digit in groups[1]
            groups[groups.length - 2] = _insert_thousand_before_each_digit(groups[groups.length - 2]);
            if (dialect === 'old') {
                groups[groups.length - 2] += groups[groups.length - 1];
                groups[groups.length - 1] = '';
            }
        }
    }

    if (add_titlo) {
        groups = groups.map(x => _place_titlo(x));
    }

    // add leading thousand signs. Last group gets none, last but one gets one, etc
    const out = groups.map((group, i) => {
        if (group.length > 0) {
            return Array(groups.length - 1 - i).fill(CU_THOUSAND).concat(group).join('');
        } else {
            return '';
        }
    }).filter(group => group !== '');

    const x = out.join(CU_NBSP);

    return x;
}


function _format_small_number(value) {
    // Deals with numbers in the range 0...999 inclusively
    if (value < 0 || value >= 1000) {
        throw new Error('Bad input: ' + value);
    }

    const hundreds = 100 * Math.floor(value / 100);
    value -= hundreds;
    const tens = 10 * Math.floor(value / 10);
    value -= tens;

    const out = [];
    if (hundreds > 0) {
        out.push(CU_DIGIT.get(hundreds));
    }
    if (tens === 10) {
        // numbers between 11..19(inclusive) use reverse order of digits due
        // to pronunciation rules(digit order in Church Slavonic follows pronunciation)
        if (value > 0) {
            out.push(CU_DIGIT.get(value));
        }
        out.push(CU_DIGIT.get(tens));
    } else {
        if (tens > 0) {
            out.push(CU_DIGIT.get(tens));
        }
        if (value > 0) {
            out.push(CU_DIGIT.get(value));
        }
    }

    const x = out.join('');

    return out.join('');
}

function _format_thousand_groups(value) {
    // Returns groups of thousands as a list:

    // Decimal  123456789 is split like this:
    // 123 456 789 and each group is formatted as a Church Slavonic number string:
    // ['123', '456', '783'](where strings are actually using Church Slavonic digits)

    if (value < 0) {
        throw new Error('Bad input: ' + value);
    }

    const groups = [];
    while (value > 0) {
        groups.push(_format_small_number(value % 1000));
        value = Math.floor(value / 1000);
    }

    return groups.reverse();
}

function _insert_thousand_before_each_digit(group) {
    return [...group].join(CU_THOUSAND);
}

export function _place_titlo(numstring) {
    if (numstring.length === 0) {
        return numstring;  // nothing to do
    }

    if (numstring.length > 1) {
        if (numstring[numstring.length - 2] !== CU_THOUSAND) {
            if (numstring[numstring.length - 2] !== CU_800) {
                return numstring.slice(0, numstring.length - 1) + CU_TITLO + numstring[numstring.length - 1];
            }
        } else {
            if (numstring.length > 2) {
                if (numstring[numstring.length - 3] !== CU_THOUSAND) { // e.g. not "##a"
                    if (numstring[numstring.length - 3] !== CU_800) {
                        return numstring.slice(0, numstring.length - 2) + CU_TITLO + numstring.slice(numstring.length - 2);
                    }
                }
            }
        }
    }

    return numstring + CU_TITLO;
}

export function cu_parse_int(string) {
    /**
    Parses Church Slavonic number string.Input string can use any dialect - parser will
    detect and handle accordingly.
    **/
    var s = string;

    if (s.startsWith('-')) {
        return -cu_parse_int(string.slice(1));
    }

    s = s.replaceAll(CU_TITLO, '');
    if (s.length === 0) {
        throw new Error('invalid CU number: ' + string);
    }

    if (s === '0') {
        return 0;
    }

    let groups = s.split(/\s+/);
    let groupinfo = new Map(groups.map(g => [g, _multiplier(g)]));

    // all multipliers must be different
    const uniqueMults = invertMap(groupinfo);
    if (uniqueMults.size != groupinfo.size) {
        throw new Error('invalid number: ' + string);
    }

    // multipliers should be sorted reverse
    const sortedGroupinfo = [...groupinfo];
    sortedGroupinfo.sort(x => -x[1]);
    for (let i = 0; i < groupinfo.length; i++) {
        if (sortedGroupinfo[i] !== groupinfo[i]) {
            throw new Errpr('Invalid number: ' + string);
        }
    }

    // special case: group with multiplier 1000 can be split(no group separators for numbers < 10000)
    let multiplier = invertMap(groupinfo);
    if (multiplier.get(1000) !== undefined) {
        const [g1, g0] = _split_thousand(multiplier.get(1000));
        if (multiplier.get(1) !== undefined) {
            // just validate
            if (g1.length !== 1) {
                throw new Error('Invalid number: ' + string);
            }
        } else if (g0.length > 0) {
            // yes, split was successful with non - empty group g0
            multiplier.set(1000, g1);
            multiplier.set(1, g0);
        }
    }

    // now we should remove thousands marks
    multiplier = new Map([...multiplier.entries()].map(([k, v]) => [k, v.replaceAll(CU_THOUSAND, '')]));

    // and build total value from thousand groups
    let value = 0;
    for (const [m, g] of multiplier.entries()) {
        value += m * _parse_small_number(g);
    }

    return value
}

function _multiplier(group) {
    let m = 1;
    for (const c of group) {
        if (c === CU_THOUSAND) {
            m *= 1000;
        } else {
            break;
        }
    }
    return m;
}

function _split_thousand(group) {
    if (!(group[0] === CU_THOUSAND && group[1] != CU_THOUSAND)) {
        throw new Error('assertion');
    }
    // number of digits that have CU_THOUSAND prepended
    const num = [...group].reduce((prev, curr) => prev + ((curr === CU_THOUSAND) ? 1 : 0), 0);

    // assert len(group) >= 2 * num
    // assert min(group[i * 2] == CU_THOUSAND for i in range(num)) == True

    group = group.replaceAll(CU_THOUSAND, '');
    return [group.slice(0, num), group.slice(num)];
}


function _parse_small_number(val) {
    const unique = new Map([...val].map(x => [x, x]));
    if (unique.size !== val.length) {
        throw new Error('Invalid value: ' + val);
    }

    let value = 0;
    for (const c of val) {
        if (CU_NUMBER.get(c) === undefined) {
            throw new Error('Invalid number: ' + val);
        }
        value += CU_NUMBER.get(c);
    }

    return value;
}
