var util = require("util");
var trees = require("./trees");

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

// test numbers
(function() {
    var x = new trees.Node();
    x.type = trees.TYPES["number"];
    x.value = JSON.stringify(100);
    assertEqual("test-numbers", x.obj_repr(), 100);
})();

// test_string
(function() {
    x = new trees.Node({"type":"string"});
    x.value = JSON.stringify("hello world");
    assertEqual("test-string", x.obj_repr(), "hello world");
})();

// test_boolean
(function() {
    var x = new trees.Node({"type":"boolean"});
    x.value = JSON.stringify(true);
    assertEqual("test_boolean_1", x.obj_repr(), true);

    x.value = JSON.stringify(false);
    assertEqual("test_boolean_2", x.obj_repr(), false);
})();

// test-list
(function() {
    var x = new trees.Node({"type":"list"});
    var l = ["one", "two", "three", "four"];
    for(var i in l) {
        var obj = l[i];
        var y = new trees.Node({"type":"string"});
        y.value = JSON.stringify(obj);
        x.children.push(y);
    }
    
    assertEqual("test-list", list_equality(l, x.obj_repr()), true);
})();

// test-dict
(function() {
    var x = new trees.Node({"type":"dict"});
    var l = {"one":1, "two":2, "three":3, "four":4};
    for(var key in l) {
        var obj = l[key];
        var y = new trees.Node({"type":"number"});
        y.attr["key"] = key;
        y.value = JSON.stringify(obj);
        x.children.push(y);
    }
    assertEqual("test-dict", dict_equality(x.obj_repr(), l), true);
})();

// test_nested
(function() {
    var x = new trees.Node({"type":"dict"});
    var l = {"three":[{"one":1},{"two":true}]};
    
    var first = new trees.Node({"type":"dict"});
    var first_obj = new trees.Node({"type":"number"});
    first_obj.attr["key"] = "one";
    first_obj.set_value(1);
    first.children.push(first_obj);
    
    var second = new trees.Node({"type":"dict"});
    var second_obj = new trees.Node({"type":"boolean"});
    second_obj.attr["key"] = "two";
    second_obj.set_value(true);
    second.children.push(second_obj);

    var three = new trees.Node({'type':'list'});
    three.children.push(first);
    three.children.push(second);
    three.attr['key'] = 'three';
    
    x.children.push(three);
    assertEqual('test-nested-1', dict_equality(l, x.obj_repr()), true);
})();

// test-getter
(function() {
    var x = new trees.Node({"type":"dict"});
    var l = {"three":[{"one":1},{"two":true}]};
    
    var first = new trees.Node({"type":"dict"});
    var first_obj = new trees.Node({"type":"number"});
    first_obj.attr["key"] = "one";
    first_obj.set_value(1);
    first.children.push(first_obj);
    
    var second = new trees.Node({"type":"dict"});
    var second_obj = new trees.Node({"type":"boolean"});
    second_obj.attr["key"] = "two";
    second_obj.set_value(true);
    second.children.push(second_obj);

    var three = new trees.Node({'type':'list'});
    three.children.push(first);
    three.children.push(second);
    three.attr['key'] = 'three';
    
    x.children.push(three);

    var leaf = x.get_path('three.0.one');
    assertEqual('test-getter', leaf.obj_repr(), 1);
})();


// test-setter
(function() {
    var x = new trees.Node({"type":"dict"});
    var l = {"three":[{"one":1},{"two":true}]};
    
    var first = new trees.Node({"type":"dict"});
    var first_obj = new trees.Node({"type":"number"});
    first_obj.attr["key"] = "one";
    first_obj.set_value(1);
    first.children.push(first_obj);
    
    var second = new trees.Node({"type":"dict"});
    var second_obj = new trees.Node({"type":"boolean"});
    second_obj.attr["key"] = "two";
    second_obj.set_value(true);
    second.children.push(second_obj);

    var three = new trees.Node({'type':'list'});
    three.children.push(first);
    three.children.push(second);
    three.attr['key'] = 'three';
    
    x.children.push(three);

    var num = 8123819321;
    var new_leaf = x.set_path('three.0.one', num);
    var leaf = x.get_path('three.0.one');
    assertEqual('test-setter-1', leaf.obj_repr(), num);
    
    x.set_path('three.1.two', 'blarg');
    leaf = x.get_path('three.1.two');
    assertEqual('test-setter-2', leaf.obj_repr(), 'blarg');
    
    x.set_path('three.1', [1,2,3]);
    leaf = x.get_path('three');
    assertEqual('test-setter-complex-3', dict_equality(leaf.obj_repr(), [{'one':num}, [1,2,3]]), true);
})();

// test-from-obj
(function() {
    var l = [1,2,3];
    var n = trees.Node.from_obj(l);
    assertEqual('test-from-obj', dict_equality(l, n.obj_repr()), true);
})();

// test_remove
(function() {
    var l = [1,2,3, {'key':'value'}];
    var n = trees.Node.from_obj(l);
    assertEqual('test-remove-1', dict_equality(l, n.obj_repr()), true);
    
    n.remove_path('0');
    assertEqual('test-remove-2', dict_equality(n.obj_repr(), [2,3,{'key':'value'}]), true);

    n.remove_path('2.key');
    assertEqual('test-remove-3', dict_equality(n.get_path('2').obj_repr(), {}), true);

    var l = [1,2,3, {'key':'value', 'last':'chance', 'why':'on', 'earth':'would', 'you':'do', 'things':'thisway'}];
    n = trees.Node.from_obj(l);
    n.remove_path('3.last');
    assertEqual('test-remove-4', dict_equality(n.obj_repr(), [1,2,3, {'key':'value', 'why':'on', 'earth':'would', 'you':'do', 'things':'thisway'}]), true);

    n.remove_path('3.earth');
    assertEqual('test-remove-5', dict_equality(n.obj_repr(), [1,2,3, {'key':'value', 'why':'on', 'you':'do', 'things':'thisway'}]), true);

})();



(function() {
    util.puts("");
    util.puts("FINAL:");
    util.puts("    PASS: " + passes);
    util.puts("    FAIL: " + fails);
})();
