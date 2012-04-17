var util = require('util');

var ops = (function() {
        var Operation = function() {};

        // Number Operations.
        var NumberIncrementOperation = function(amount) {
            this.amount = amount;
        };

        NumberIncrementOperation.prototype.apply = function(node) {
            var new_node = node.proto({'value':node.obj_repr() + this.amount});
            var reverse = new NumberIncrementOperation(this.amount * (-1));
            return [new_node, reverse];
        };
        
        NumberIncrementOperation.prototype.pack = function() {
            return ["NumberIncrementOperation", this.amount];
        };

        // end Number Operations.

        // String Operations
        var StringInsertOperation = function(index, text) {
            this.index = index;
            this.text = text;
        };

        StringInsertOperation.prototype.apply = function(node) {
            var node_value = node.obj_repr();
            var new_node = node.proto({'value':node_value.slice(0, this.index) + this.text + node_value.slice(this.index, node_value.length)});
            var reverse = new StringDeleteOperation(this.index, this.text.length);
            return [new_node, reverse];
        };

        StringInsertOperation.prototype.pack = function() {
            return ["StringInsertOperation", this.index, this.text];
        };

        var StringDeleteOperation = function(index, length) {
            this.index = index;
            this.length = length;
        };

        StringDeleteOperation.prototype.apply = function(node) {
            var node_value = node.obj_repr();
            var new_node = node.proto({'value':node_value.slice(0, this.index) + node_value.slice(this.index + this.length, node_value.length)});
            var reverse = new StringInsertOperation(this.index, node_value.slice(this.index, this.length));
            return [new_node, reverse];
        };

        StringDeleteOperation.prototype.pack = function() {
            return ["StringDeleteOperation", this.index, this.length];
        };

        var StringSetOperation = function(value) {
            this.value = value;
        };

        StringSetOperation.prototype.apply = function(node) {
            var new_node = node.proto({'value':this.value});
            var reverse = new StringSetOperation(node.obj_repr());
            return [new_node, reverse];
        };

        StringSetOperation.prototype.pack = function() {
            return ["StringSetOperation", this.value];
        };
        // end String Operations

        // Boolean Operations
        var BooleanSetOperation = function(value) {
            this.value = value;
        };

        BooleanSetOperation.prototype.apply = function(node) {
            var new_node = node.proto({'value':this.value});
            var reverse = new BooleanSetOperation(!this.value);
            return [new_node, reverse];
        };

        BooleanSetOperation.prototype.pack = function() {
            return ["BooleanSetOperation", this.value];
        };
        // end Boolean Operations

        // List Operations
        var ListInsertOperation = function(index, value) {
            this.index = index;
            this.value = value;
        };

        ListInsertOperation.prototype.apply = function(node) {
            var new_node = node.proto({
                    'children':
                    node.children.slice(0, this.index)
                    .concat(this.value)
                    .concat(node.children.slice(this.index, node.children.length))
                });
            var reverse = new ListDeleteOperation(this.index, this.value.length);
            return [new_node, reverse];
        };

        ListInsertOperation.prototype.pack = function() {
            return ["ListInsertOperation", this.index, this.value];
        };

        var ListDeleteOperation = function(index, length) {
            this.index = index;
            this.length = length;
        };

        ListDeleteOperation.prototype.apply = function(node) {
            var new_node = node.proto({
                    'children':
                    node.children.slice(0, this.index)
                    .concat(node.children.slice(this.index+1, node.children.length))
                });
            var reverse = new ListInsertOperation(this.index, node.children.slice(this.index, this.length));
            return [new_node, reverse];
        };

        ListDeleteOperation.prototype.pack = function() {
            return ["ListDeleteOperation", this.index, this.length];
        };

        var ListSetIndexOperation = function(index, value) {
            this.index = index;
            this.value = value;
        };

        ListSetIndexOperation.prototype.apply = function(node) {
            var old = node.children[this.index];
            var new_node = node.proto({'value':node.value, 'children':[]});
            for(var index in node.children) {
                if (index == this.index) {
                    new_node.children.push(this.value);
                } else {
                    new_node.children.push(node.children[index]);
                }
            }
            var reverse = new ListSetIndexOperation(this.index, old);
            return [new_node, reverse];
        };

        ListSetIndexOperation.prototype.pack = function() {
            return ["ListSetIndexOperation", this.index, this.value];
        };

        var ListApplyIndexOperation = function(index, operation) {
            this.index = index;
            this.operation = operation;
        };

        ListApplyIndexOperation.prototype.apply = function(node) {
            var nr = this.operation.apply(node.children[this.index]);
            var reverse_op = new ListApplyIndexOperation(this.index, nr[1]);
            var new_node = node.proto({'value':node.value, 'children':[]});
            for(var index in node.children) {
                if (index == this.index) {
                    new_node.children.push(nr[0]);
                } else {
                    new_node.children.push(node.children[index]);
                }
            }
            return [new_node, reverse_op];
        };

        ListApplyIndexOperation.prototype.pack = function() {
            return ["ListApplyIndexOperation", this.index, this.operation.pack()];
        };
        // end List Operations
        
        // Dictionary Key Apply
        var DictKeyApplyOperation = function(key, operation) {
            this.key = key;
            this.operation = operation;
        };

        DictKeyApplyOperation.prototype.apply = function(node) {
            var child = node.get_path(this.key);
            var nr = this.operation.apply(child);
            var new_node = node.proto({'value':node.value, 'children':[]});
            for(var index in node.children) {
                new_node.children.push(node.children[index]);
            }
            new_node.set_path(this.key, nr[0]);
            reverse_op = new DictKeyApplyOperation(this.key, nr[1]);
            return [new_node, reverse_op];
        };

        DictKeyApplyOperation.prototype.pack = function() {
            return ["DictKeyApplyOperation", this.key, this.operation.pack()];
        };
        // end dict

        //class MoveBookmarkOperation(Operation): 
        //class CopyBookmarkOperation(Operation):
        //class PruneBookmarkOperation(Operation):

        var exports = {
            'NumberIncrementOperation':NumberIncrementOperation,
            'StringInsertOperation':StringInsertOperation,
            'StringDeleteOperation':StringDeleteOperation,
            'StringSetOperation':StringSetOperation,
            'BooleanSetOperation':BooleanSetOperation,
            'ListInsertOperation':ListInsertOperation,
            'ListDeleteOperation':ListDeleteOperation,
            'ListSetIndexOperation':ListSetIndexOperation,
            'ListApplyIndexOperation':ListApplyIndexOperation,
            'DictKeyApplyOperation':DictKeyApplyOperation
        };

        var unpack = function(d) {
            // there is some trickery here, but only to make things easier.
            var klass = d[0];
            var obj = new exports[klass].prototype.constructor();
            exports[klass].prototype.constructor.apply(obj, d.slice(1));
            return obj;
        };

        exports['unpack'] = unpack;

        // Lets see if we are running in the Node.js context or in a browser.
        if (typeof module !== 'undefined') {
            module.exports = exports;
        }
        return exports;
    })();
