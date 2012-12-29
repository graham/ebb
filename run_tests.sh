#! /bin/bash

echo "Python:"
cd python; PYTHONPATH=. python tests/test_all.py; cd ..;


echo "Done!"
