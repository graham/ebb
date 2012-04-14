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
        // end Number Operations.

        // String Operations
        var StringInsertOperation = function(index, text) {
            this.index = index;
            this.text = text;
        };

        StringInsertOperation.prototype.apply = function(node) {
            var node_value = node.obj_repr();
            var new_node = node.proto({'value':node_value.slice(0, this.index) + this.text + node_value.slice(this.index, node_value.length - this.index)});
            var reverse = new StringDeleteOperation(this.index, len(self.text));
            return [new_node, reverse];
        };
        
        var StringDeleteOperation = function(index, length) {
            this.index = index;
            this.length = length;
        };

        StringDeleteOperation.prototype.apply = function(node) {
            var node_value = node.obj_repr();
            var target_len = node_value.length - (this.index + this.length);
            var new_node = node.proto({'value':node_value.slice(0, this.index) + node_value.slice(this.index + this.length, target_len)});
            var reverse = new StringInsertOperation(this.index, node_value.slice(this.index, target_len));
            return [new_node, reverse];
        };

        var StringSetOperation = function(value) {
            this.value = value;
        };

        StringSetOperation.prototype.apply = function(node) {
            var new_node = node.proto({'value':this.value});
            var reverse = new StringSetOperation(node.obj_repr());
            return [new_node, reverse];
        };
        // end String Operations

        // Boolean Operations
        var BooleanSetOperation = function(value) {
            this.value = value;
        };

        BooleanSetOperation.prototype.apply = function(node) {
            var new_node = node.proto({'value':self.value});
            var reverse = new BooleanSetOperation(!this.value);
            return [new_node, reverse];
        };
        // end Boolean Operations

        // List Operations
        var ListInsertOperation = function(index, value) {
            this.index = index;
            this.value = value;
        };

        ListInsertOperation.prototype.apply = function(node) {
            var new_node = node.proto({
                    'children':node.children.slice(0, this.index)
                    .concat(this.value)
                    .concat(node.children.slice(this.index, (node.children.length - this.index)))});
            var reverse = new ListDeleteOperation(this.index, this.value.length);
            return [new_node, reverse];
        };

        var ListDeleteOperation = function(index, length) {
            this.index = index;
            this.length = length;
        };

        ListDeleteOperation.prototype.apply = function(node) {
            var new_node = node.proto({
                    'children':node.children.slice(0, this.index)
                    .concat(this.value)
                    .concat(node.children.slice(this.index, (node.children.length - this.index)))});
            var reverse = new ListInsertOperation(this.index, node.children.slice(this.index, this.length));
            return [new_node, reverse];
        };

        var ListSetIndexOperation = function(index, value) {
            this.index = index;
            this.value = value;
        };

        ListSetIndexOperations.prototype.apply = function(node) {
            var old = node.children[this.index];
            node.children[this.index] = self.value;
            var reverse = new ListSetIndexOperation(this.index, old);
            return [node, reverse];
        };

        var ListApplyIndexOperation = var function(index, operation) {
            this.index = index;
            this.operation = operation;
        };

        ListApplyIndexOperation.prototype.apply = function(node) {
            var nr = this.operation.apply(node.children[this.index]);
            var reverse_op = new ListApplyIndexOperation(this.index, nr[1]);
            node.children[this.index] = nr[0];
            return [node, reverse_op];
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
            node.set_path(this.key, nr[0]);
            reverse_op = new DictKeyApplyOperation(this.key, reverse);
            return [node, reverse_op];
        };
        // end dict


        //class MoveBookmarkOperation(Operation): 
        //class CopyBookmarkOperation(Operation):
        //class PruneBookmarkOperation(Operation):

        var exports = {};
        // Lets see if we are running in the Node.js context or in a browser.
        if (typeof module !== 'undefined') {
            module.exports = exports;
        }
        return exports;
    })();
