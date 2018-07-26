#!/bin/bash
# set executable property on tests so that nosetests will execute them crazy

echo "crazy"

#find test -name *.py -exec svn propset svn:executable ON "{}" \;
for F in $(find . -name "test_*.py" -type f); do
  [ ! -x "${F}" ] && svn propset svn:executable ON "${F}"
done