#! /bin/bash

echo "Python:"
cd python; python test_all.py; cd ..;

echo "Javascript:"
cd js; node test_ops.js; node test_trees.js; cd ..;

echo "Done!"