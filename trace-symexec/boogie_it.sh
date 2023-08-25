#! /bin/bash
SYMEXEC=src/symexec.py
BOOGIE=boogie
# BOOGIEFILE="$1"
# echo $0
${BOOGIE} "trace_integerOverflow.bpl"
# ${BOOGIE} "trace_noReentrancy.bpl"
