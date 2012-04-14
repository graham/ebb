var util = require("util");
var trees = require("./trees");

var passes = 0;
var fails = 0;

var assertEqual = function(test_name, val1, val2) {
    if (test_name === undefined ||
        val1 === undefined ||
        val2 === undefined) {
        throw Exception(" YOU ARE FUCKING STUPID ");
    }
    if (val1 == val2) {
        util.puts("PASS: " + test_name);
        passes += 1;
    } else {
        util.puts("FAIL: " + test_name + " -> " + val1 + " != " + val2);
        fails += 1;
    }
};

var list_equality = function(left, right) {
    if (left.length != right.length) {
        return false;
    }
    for(var index = 0; index < left.length; index++) {
        if (left[index] != right[index]) {
            return false;
        }
    }
    return true;
};

var dict_equality = function(left, right) {
    // sorry i guess i have no better way of doing this (without writing a full blown comparitor, 2.0)
    return JSON.stringify(left) == JSON.stringify(right);
};



(function() {
    util.puts("");
    util.puts("FINAL:");
    util.puts("    PASS: " + passes);
    util.puts("    FAIL: " + fails);
})();
