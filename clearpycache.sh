echo ""
echo "Clearing the following python cache files:"
echo "------------------------------------------"
find . -name "*.pyc"
find . -name "*.pyc" -delete
find . -name "*.pyo"
find . -name "*.pyo" -delete
find . -name "*.class"
find . -name "*.class" -delete
echo "------------------------------------------"
echo ""