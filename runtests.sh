./clearpycache.sh
echo "python tests"
python -m unittest discover
echo "python3 tests"
python3 -m unittest discover
echo "pypy tests"
pypy funcstructs/test_runner.py
echo "pypy3 tests"
pypy3 funcstructs/test_runner.py
echo "jython tests"
jython funcstructs/test_runner.py
./clearpycache.sh