set -e

./clearpycache.sh
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

echo ""
echo "Runing pep8 style checker on:"
echo "-----------------------------"
echo ""
echo "funcstructs/"
pep8 funcstructs/
echo "tests/"
pep8 tests/
echo ""

./clearpycache.sh
echo ""
echo "All Good!"
echo ""
