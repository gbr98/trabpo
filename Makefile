#===========================MakeFile==============================
# For Cplex + Concert Projects
# by Hassan Baalbaki www.hassanbaalbaki.com
#================================================================


SYSTEM = x86-64_linux
LIBFORMAT = static_pic

EXDIR = /home/gabriel/Documentos/trabpo

#------------------------------------------------------------
#
# When you adapt this makefile to compile your CPLEX programs
# please copy this makefile and set CPLEXDIR and CONCERTDIR to
# the directories where CPLEX and CONCERT are installed.
#
#------------------------------------------------------------
ILOGSTUDIODIR =/opt/ibm/ILOG/CPLEX_Studio_Community129
CPLEXDIR = $(ILOGSTUDIODIR)/cplex
CONCERTDIR = $(ILOGSTUDIODIR)/concert




# ---------------------------------------------------------------------
# Compiler selection
# ---------------------------------------------------------------------

CCC = g++
CC = gcc
JAVAC = javac

# ---------------------------------------------------------------------
# Compiler options (edit note: -m32 was removed from below)
# ---------------------------------------------------------------------

CCOPT = -O -fPIC -fexceptions -DNDEBUG -DIL_STD


# ---------------------------------------------------------------------
# Link options and libraries (edit note: -m32 was removed from below)
# ---------------------------------------------------------------------

CPLEXBINDIR = $(CPLEXDIR)/bin/$(BINDIST)
CPLEXLIBDIR = $(CPLEXDIR)/lib/$(SYSTEM)/$(LIBFORMAT)
CONCERTLIBDIR = $(CONCERTDIR)/lib/$(SYSTEM)/$(LIBFORMAT)

CCLNFLAGS = -L$(CPLEXLIBDIR) -lilocplex -lcplex -L$(CONCERTLIBDIR) -lconcert -lm -pthread



all:${DIRS}
	make all_cpp

execute: all
	make execute_cpp


CONCERTINCDIR = $(CONCERTDIR)/include
CPLEXINCDIR = $(CPLEXDIR)/include

#EXINC = $(EXDIR)/include
EXINC = $(EXDIR)/src/cpp
EXDATA = $(EXDIR)/data
EXSRCCPP = $(EXDIR)/src/cpp


CFLAGS = $(COPT) -I$(CPLEXINCDIR)
CCFLAGS = $(CCOPT) -I$(CPLEXINCDIR) -I$(CONCERTINCDIR)


#------------------------------------------------------------
#
#Build and Execute directory
#
#------------------------------------------------------------



INC_PATH = $(EXSRCCPP)
SRC_PATH = $(EXSRCCPP)
OBJ_PATH = ${EXDIR}/obj



SOURCES = ${wildcard ${SRC_PATH}/*.cpp}
OBJECTS = ${patsubst ${SRC_PATH}/%.cpp, ${OBJ_PATH}/%.o, ${SOURCES}}


INCLUDES = -I${INC_PATH}

DIRS = ${OBJ_PATH}


#------------------------------------------------------------
# make all : to compile all.
# make execute : to compile and execute some instances
#------------------------------------------------------------



CPP_EX = test




all_cpp: 
	$(CPP_EX)


execute_cpp: $(CPP_EX)
	./test $(EXDATA)/small.dat 3




# ------------------------------------------------------------

clean :
	/bin/rm -rf *.o *~ $(OBJ_PATH)/*.o
	/bin/rm -rf ${SRC_PATH}/*~
	/bin/rm -rf $(CPP_EX)
	/bin/rm -rf *.mps *.ord *.sos *.lp *.sav *.net *.msg *.log *.clp

# ------------------------------------------------------------
#
# The Cpp and *.o Files
#


all: ${DIRS} test
	
${OBJ_PATH}:
	mkdir -p $@
	
${OBJ_PATH}/%.o : ${SRC_PATH}/%.cpp
	$(CCC) ${INCLUDES} -c $(CCFLAGS) $< -o $@

test: ${OBJECTS}
	$(CCC) $(CCFLAGS) $^ -o test $(CCLNFLAGS)


# Local Variables:
# mode: makefile
# End:


#======================== END OF MakeFile ========================= 