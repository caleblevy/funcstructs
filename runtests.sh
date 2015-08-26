set -e

echo ""
echo "Testing Funcstructs"
echo "==================="

# Clear pre-existing pyc files. These can hide broken import paths, since
# python can directly use pyc files when a .py file is unavailable.
# It is best for missing modules to cause errors, so we remove the pyc.
./clearpycache.sh >/dev/null

# pep8 checks go at the beginning because they are nice, quick, easy
# and often I won't want to run the full tests (esp. Jython).
# Style is very important to me, so it must be correct before running
# further tests.

echo ""
echo "Checking PEP8 Compliance:"
echo "-------------------------"
echo ""
pep8 funcstructs/ tests/
echo "OK"
echo ""

# We don't want to require pylint since its so finicky.

echo "Running tests with the following implementations:"
echo "-------------------------------------------------"

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

./clearpycache.sh >/dev/null
echo ""
echo "All Good!"
echo ""
