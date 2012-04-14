var util = require("util");
var trees = require("./trees");
var ops = require("./ops");

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
    var number = trees.Node.from_obj(123);
    var op = new ops.NumberIncrementOperation(-23);
    var rr = op.apply(number);
    
    util.puts(JSON.stringify(op));

    assertEqual('number-test-1', rr[0].obj_repr(), 100);

    var bi = rr[1].apply(rr[0]);
    assertEqual('number-test-2', bi[0].obj_repr(), number.obj_repr());
})();

(function() {
    util.puts("");
    util.puts("FINAL:");
    util.puts("    PASS: " + passes);
    util.puts("    FAIL: " + fails);
})();
