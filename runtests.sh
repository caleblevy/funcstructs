set -e

./clearpycache.sh >/dev/null

# pep8 checks go at the beginning because they are nice, quick, easy
# and often I won't want to run the full tests (esp. Jython) so I'd
# rather catch these errors at the beginning

echo ""
echo "Checking PEP8 Compliance:"
echo "-------------------------"
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

./clearpycache.sh >/dev/null
echo ""
echo "All Good!"
echo ""
