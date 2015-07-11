set -e

./clearpycache.sh

echo ""
echo "Checking PEP8 Compliance:"
echo "-----------------------------"
echo ""
pep8 funcstructs/
pep8 tests/
echo "OK"
echo ""

echo "Running tests with the following implementations:"

echo ""
echo "Python"
echo "------"
python tests/

echo ""
echo "Python3"
echo "-------"
python3 tests/

echo ""
echo "PyPy"
echo "----"
pypy tests/

echo ""
echo "PyPy3"
echo "-----"
pypy3 tests/

echo ""
echo "Jython 2.7"
echo "----------"
jython tests/

./clearpycache.sh
echo ""
echo "All Good!"
echo ""
