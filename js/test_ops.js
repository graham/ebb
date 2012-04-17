var util = require("util");
var trees = require("./trees");
var ops = require("./ops");

var passes = 0;
var fails = 0;

var assertEqual = function(test_name, val1, val2) {
    if (test_name === undefined ||
        val1 === undefined ||
        val2 === undefined) {
        throw " YOU ARE FUCKING STUPID, name: " + JSON.stringify([test_name, val1, val2]);
    }
    if (val1 == val2) {
        passes += 1;
    } else {
        util.puts("FAIL: " + test_name + " -> " + JSON.stringify(val1) + " != " + JSON.stringify(val2));
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

// test-number
(function() {
    var number = trees.Node.from_obj(123);
    var op = new ops.NumberIncrementOperation(-23);
    var rr = op.apply(number);
    assertEqual('number-test-1', rr[0].obj_repr(), 100);

    var bi = rr[1].apply(rr[0]);
    assertEqual('number-test-2', bi[0].obj_repr(), number.obj_repr());
})();

// test-string-insert
(function() {
    var init = trees.Node.from_obj("hello world");
    var op = new ops.StringInsertOperation(0, "well, ");
    var rr = op.apply(init);
    assertEqual('string-insert-test-1', rr[0].obj_repr(), "well, hello world");

    var bi = rr[1].apply(rr[0]);
    assertEqual('string-insert-test-1-revert', bi[0].obj_repr(), "hello world");
    
    var op2 = new ops.StringInsertOperation(rr[0].obj_repr().length, ", now more");
    var rr2 = op2.apply(rr[0]);
    assertEqual('string-insert-test-2', rr2[0].obj_repr(), "well, hello world, now more");

    var bi2 = rr2[1].apply(rr2[0]);
    assertEqual('string-insert-test-2-revert', bi2[0].obj_repr(), "well, hello world");
})();

// test-string-delete
(function() {
    var init = trees.Node.from_obj("hello world");
    var op = new ops.StringDeleteOperation(0, 2);
    var rr = op.apply(init);
    assertEqual('test-string-delete-1', rr[0].obj_repr(), "llo world");
    
    var bi = rr[1].apply(rr[0]);
    assertEqual('test-string-delete-2', bi[0].obj_repr(), init.obj_repr());

    var op2 = new ops.StringDeleteOperation(2,4);
    var rr2 = op2.apply(init);
    assertEqual('test-string-delete-3', rr2[0].obj_repr(), "heworld");
})();

// test-string-set
(function() {
    var init = trees.Node.from_obj("hello world");
    var op = new ops.StringSetOperation("fuck you");
    var rr = op.apply(init);
    assertEqual('test-string-set-1', rr[0].obj_repr(), "fuck you");

    var bi = rr[1].apply(rr[0]);
    assertEqual('test-string-set-1-revert', bi[0].obj_repr(), "hello world");
})();

// test-boolean-set
(function() {
    var init = trees.Node.from_obj(true);
    var op = new ops.BooleanSetOperation(false);
    var rr = op.apply(init);
    assertEqual('test-boolean-set-1', rr[0].obj_repr(), false);

    var bi = rr[1].apply(rr[0]);
    assertEqual('test-string-set-1-revert', bi[0].obj_repr(), init.obj_repr());
})();

// test-list-insert
(function() {
    var init = trees.Node.from_obj([1,2,3]);
    var op = new ops.ListInsertOperation(0, [trees.Node.from_obj(-10)]);
    var rr = op.apply(init);
    assertEqual('test-list-insert-1', list_equality(rr[0].obj_repr(), [-10,1,2,3]), true);

    var bi = rr[1].apply(rr[0]);
    assertEqual('test-list-insert-1-reverse', list_equality(bi[0].obj_repr(), [1,2,3]), true);
})();

// test-list-delete
(function() {
    var init = trees.Node.from_obj([1,2,3]);
    var op = new ops.ListDeleteOperation(0, 1);
    var rr = op.apply(init);
    assertEqual('test-list-delete-1', list_equality(rr[0].obj_repr(), [2,3]), true);

    var bi = rr[1].apply(rr[0]);
    assertEqual('test-list-delete-2', list_equality(bi[0].obj_repr(), init.obj_repr()), true);
})();

// test-list-set-index
(function() {
    var init = trees.Node.from_obj([1,2,3]);
    var op = new ops.ListSetIndexOperation(0, trees.Node.from_obj(100));
    var rr = op.apply(init);
    assertEqual('test-list-set-1', list_equality(rr[0].obj_repr(), [100,2,3]), true);

    var bi = rr[1].apply(rr[0]);
    assertEqual('test-list-set-1-revert', list_equality(bi[0].obj_repr(), [1,2,3]), true);
})();

// test-list-apply-op
(function() {
    var init = trees.Node.from_obj([1,2,3]);
    var op = new ops.ListApplyIndexOperation(0, new ops.NumberIncrementOperation(100));
    var rr = op.apply(init);
    assertEqual('test-list-apply-1', list_equality(rr[0].obj_repr(), [101,2,3]), true);

    var bi = rr[1].apply(rr[0]);
    assertEqual('test-list-apply-1-revert', list_equality(bi[0].obj_repr(), [1,2,3]), true);
})();

// test-dict-key-apply
(function() {
    var init = trees.Node.from_obj({'one':'hello'});
    var op = new ops.DictKeyApplyOperation('one', new ops.StringInsertOperation(5, ' world'));
    var rr = op.apply(init);
    assertEqual('test-dict-apply-1', dict_equality(rr[0].obj_repr(), {'one':'hello world'}), true);

    var bi = rr[1].apply(rr[0]);
    assertEqual('test-dict-apply-1-revert', dict_equality(bi[0].obj_repr(), {'one':'hello'}), true);
})();

// test-depth-test
(function() {
    var init = trees.Node.from_obj([1,2,{'one':'hello'}]);
    var op1 = new ops.ListApplyIndexOperation(0, new ops.NumberIncrementOperation(50));
    var ff = op1.apply(init);
    assertEqual('test-depth-1', dict_equality(ff[0].obj_repr(), [51,2,{'one':'hello'}]), true);

    var op2 = new ops.ListApplyIndexOperation(2, new ops.DictKeyApplyOperation('one', new ops.StringInsertOperation(0, 'sup, ')));
    var ss = op2.apply(init);
    assertEqual('test-depth-2', dict_equality(ss[0].obj_repr(), [1,2,{'one':'sup, hello'}]), true);
    // test is not complete.
})();

(function() {
    util.puts("");
    util.puts("FINAL:");
    util.puts("    PASS: " + passes);
    util.puts("    FAIL: " + fails);
})();
