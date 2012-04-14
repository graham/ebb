var util = require('util');

var trees = (function() {
        var TYPES = {
            "number":0,
            "string":1,
            "boolean":2,
            "list":3,
            "dict":4,
            "null":5
        };

        var obj_to_json_type = function(k) {
            var t = typeof k;
            if (t == "number") {
                return "number";
            } else if (t == "string") {
                return "string";
            } else if (t == "boolean") {
                return "boolean";
            } else if (k.constructor == Array) {
                return "list";
            } else if (k.constructor == Object) {
                return "dict";
            } else if (k == null) {
                return "null";
            } else if (k.constructor == Node) {
                return "node";
            } else {
                throw "Unsupported data type: " + t;
            }
        };

        var type_for_enum = function(k) {
            for(var i in TYPES) {
                if (k == TYPES[i]) {
                    return TYPES[i];
                }
            }
            return null;
        };

        var Node = function(d) {
            if (d === undefined) {
                d = {};
            }

            this.name = null;
            this.type = null;
            this.attr = {};
            
            if (d['name'] != undefined) {
                this.name = d['name'];
            }
            if (d['type'] != undefined) {
                this.type = TYPES[d['type']];
            }
            if (d['type_id'] != undefined) {
                this.type = d['type'];
            }
            if (d['attr'] != undefined) {
                this.attr = d['attr'];
            }
            this.value = null;
            this.children = [];
        };

        Node.prototype.proto = function(d) {
            var value = d['value'] || null;
            var children = d['children'] || null;
            
            var p = new Node({"name":this.name, type_id:this.type, attr:this.attr});
            if (value !== null) {
                p.set_value(value);
            }
            if (children !== null) {
                p.children = children;
            }
            return p;
        };

        // Class method.
        Node.from_obj = function(obj) {
            var t = obj_to_json_type(obj);
            if (t == "number") {
                var n = new Node({"type":"number"});
                n.set_value(obj);
                return n;
            } else if (t == "string") {
                var n = new Node({"type":"string"});
                n.set_value(obj);
                return n;
            } else if (t == "boolean") {
                var n = new Node({"type":"boolean"});
                n.set_value(obj);
                return n;
            } else if (t == "list") {
                var n = new Node({"type":"list"});
                for(var index in obj) {
                    var value = obj[index];
                    var new_node = Node.from_obj(value);
                    n.children.push(new_node);
                }
                return n;
            } else if (t == "dict") {
                var n = new Node({"type":"dict"});
                for(var key in obj) {
                    var value = obj[key];
                    var new_node = new Node.from_obj(value);
                    new_node.attr['key'] = key;
                    n.children.push(new_node);
                }
                return n;
            } else if (t == "null") {
                return new Node({"type":"null"});
            }
        };
        
        Node.prototype.obj_repr = function() {
            if (this.type == TYPES["number"]) {
                return JSON.parse(this.value);
            } else if (this.type == TYPES["string"]) {
                return JSON.parse(this.value);
            } else if (this.type == TYPES["boolean"]) {
                return JSON.parse(this.value);
            } else if (this.type == TYPES["list"]) {
                var ret = [];
                for(var i in this.children) {
                    var node = this.children[i];
                    ret.push(node.obj_repr());
                }
                return ret;
            } else if (this.type == TYPES["dict"]) {
                var ret = {};
                for(var index in this.children) {
                    var node = this.children[index];
                    var key = node.attr["key"];
                    ret[key] = node.obj_repr();
                }
                return ret;
            } else if (this.type == TYPES["null"]) {
                return null;
            }
        };

        Node.prototype.set_value = function(obj) {
            var t = typeof obj;
            if (t == "number" || t == "string" || t == "boolean") {
                this.value = JSON.stringify(obj);
            } else if (t.constructor == Node) {
                this.value = obj.value;
            } else {
                this.children = Node.from_obj(obj);
            }
        };

        // Path stuff, this could change over time, this is nice to have now
        // but isn't as important for data representation (for modification it will be.
        
        Node.prototype.get_path = function(key) {
            var sp = key.split(".");
            if (sp.length == 1) {
                return this._get(sp[0]);
            } else {
                var obj = this._get(sp[0]);
                return obj.get_path(sp.slice(1).join("."));
            }
        };

        Node.prototype._get = function(key) {
            if (this.type == TYPES['dict']) {
                for(var i in this.children) {
                    var node = this.children[i];
                    var n_key = node.attr['key'];
                    if (key == n_key) {
                        return node;
                    }
                }
                throw "Key not found: " + key;
            } else if (Number(key) != NaN) {
                if (this.type == TYPES["string"]) {
                    return this.value[Number(key)];
                } else if (this.type == TYPES["list"]) {
                    return this.children[Number(key)];
                } else { 
                    throw "invalid path: " + key;
                }
            } else {
                throw "invalid path: " + key;
            }
        };

        Node.prototype.set_path = function(key, value) {
            var sp = key.split(".");
            if (sp.length == 1) {
                return this._set(sp[0], value);
            } else {
                var obj = this._get(sp[0]);
                return obj.set_path(sp.slice(1).join("."), value);
            }
        };

        Node.prototype._set = function(key, value) {
            if (this.type == TYPES['dict']) {
                for(var i in this.children) {
                    var obj = this.children[i];
                    if (key == obj.attr['key']) {
                        obj.set_value(value);
                        return;
                    }
                }
                // Looks like we didn't bail out during the for loop
                var n = new Node({'type':obj_to_json_type(value)});
                n.attr['key'] = key;
                n.set_value(value);
                this.children.push(n);
                return n;
            } else if (Number(key) != NaN) {
                var index = Number(key);
                if (this.type == TYPES['string']) {
                    this.value[index] = value;
                } else if (this.type == TYPES['list']) {
                    this.children[index] = Node.from_obj(value);
                } else {
                    throw "invalid path: " + key; 
                }
            } else {
                throw "invalid path: " + key; 
            }
        };

        Node.prototype.remove_path = function(key) {
            var sp = key.split(".");
            if (sp.length == 1) {
                return this._remove(sp[0])
            } else {
                var obj = this._get(sp[0]);
                return obj.remove_path(sp.slice(1).join("."));
            }
        };

        Node.prototype._remove = function(key) {
            if (this.type == TYPES['dict']) {
                var new_children = [];
                for(var i in this.children) {
                    var obj = this.children[i];
                    if (key != obj.attr['key']) {
                        new_children.push(obj);
                    }
                }
                this.children = new_children;
            } else if (Number(key) != NaN) {
                var index = Number(key);
                if (this.type == TYPES['string']) {
                    this.value = this.value.slice(0, index).concat(this.value.slice(index+1, this.value.length));
                } else if (this.type == TYPES['list']) {
                    this.children = this.children.slice(0, index).concat(this.children.slice(index+1, this.children.length));
                } else {
                    throw "invalid path: " + key;
                }
            } else {
                throw "invalid path: " + key;
            }
        };

        Node.prototype.toString = function() {
            return "<Node t:" + this.type + " attr: " + JSON.stringify(this.attr) + " value: " + JSON.stringify(this.value) + " children: " + JSON.stringify(this.children) + ">";
        };

        var exports = {"Node":Node, "TYPES":TYPES};
        // Lets see if we are running in the Node.js context or in a browser.
        if (typeof module !== 'undefined') {
            module.exports = exports;
        }
        return exports;
    })();
