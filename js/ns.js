var util = require('util');

var ns = (function() {
        var safe_bound = function(x) {
            if (x > 0) {
                return x;
            } else {
                return 0;
            }
        };

        // Namespace.
        var Namespace = function(name) {
            this.name = name;
            this.docs = {};
        };

        Namespace.prototype.execute = function(key, path, operation) {
            var doc = null;
            if (this.docs[key] == undefined) {
                doc = this.docs[key];
            } else {
                doc = new Document();
            }
        };
        
        Namespace.prototype.get = function(key) {
            return this.docs[key];
        };
        
        Namespace.prototype.get_value = function(key) {
            return this.docs[key].root.obj_repr();
        };
        // Namespace.

        // Document
        var Document = function(root) {
            this.root = root
            this.history_buffer = [];
        };

        Document.prototype.exclude_operation = function(operation) {

        };

        Document.prototype.include_operation = function(path, operation, ts) {

        };

        Document.prototype.mutate_based_on = function(root, tpath, oplist, reference_op) {

        };
        


        // Lets see if we are running in the Node.js context or in a browser.
        if (typeof module !== 'undefined') {
            module.exports = exports;
        }
        return exports;
    })();