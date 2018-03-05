@echo off

if "x%GATE_HOME%"=="x" goto fail

set GATEJAR=%GATE_HOME%\bin\gate.jar
if not exist "%GATEJAR%" set GATEJAR=%GATE_HOME%\build\gate.jar

echo Compiling class files....
javac -classpath .;"%GATEJAR%" -d ./classes -sourcepath ./src ./src/mark/chunking/*.java

echo Copying resource...
xcopy /E /I /Y resources classes\mark\chunking\resources

echo Building JAR file....
jar cf Chunker.jar -C classes .

goto finish

:fail
echo GATE_HOME has not been set so you can't rebuild the chunker

:finish