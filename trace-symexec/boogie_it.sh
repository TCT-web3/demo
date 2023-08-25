#! /bin/bash
SYMEXEC=src/symexec.py
BOOGIE=boogie
BOOGIEFILE=$1
# echo $0
# ${BOOGIE} ${BOOGIEFILE} 
${BOOGIE} "trace_integerOverflow.bpl"
# ${BOOGIE} "trace_noReentrancy.bpl"
# ${BOOGIE} "trace_Reentrancy.bpl"
# ${BOOGIE} "trace_addLiquidity.bpl"
