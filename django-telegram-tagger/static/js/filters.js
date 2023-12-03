function onlyDouble(text) {
    const re = new RegExp('^\\d*(\\.|)\\d*$')

    return re.test(text);
}

function maximumFilter(text, max, equal=true) {
    let num = parseFloat(text);
    if (num >= max) {
        return num === max && equal;
    }

    return true;
}

function minimumFilter(text, min, equal=true) {
    let num = parseFloat(text);
    if (num <= min) {
        return num === min && equal
    }

    return true
}