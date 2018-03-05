#!/bin/sh

if [ x${GATE_HOME} = x ]
then
	echo GATE_HOME has not been set so you cannot rebuild the chunker
else
	[ x${GATEJAR} = x ] && [ -f ${GATE_HOME}/bin/gate.jar ] && GATEJAR=${GATE_HOME}/bin/gate.jar
	[ x${GATEJAR} = x ] && [ -f ${GATE_HOME}/build/gate.jar ] && GATEJAR=${GATE_HOME}/build/gate.jar

	APPPATH=".:${GATEJAR}"
	
	CYG=false
	case `uname` in CYGWIN*) CYG=true ;; esac
	if [ $CYG = true ]
	then
	  GATEJAR=`cygpath -w $GATEJAR`
	  APPPATH=`cygpath -w -p $APPPATH`
	fi
	
	JAVAC=javac
	
	javac -classpath $APPPATH -d ./classes -sourcepath ./src ./src/mark/chunking/*.java
	jar cf Chunker.jar -C classes .
fi

