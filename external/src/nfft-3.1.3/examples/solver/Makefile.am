# $Id: Makefile.am 3086 2009-03-11 07:36:56Z keiner $

AM_CPPFLAGS = -I$(top_srcdir)/include

exampledir = $(pkgdatadir)/examples/solver

example_PROGRAMS = simple_test glacier

simple_test_SOURCES = simple_test.c
simple_test_LDADD = $(top_builddir)/libnfft3.la

glacier_SOURCES = glacier.c
glacier_LDADD = $(top_builddir)/libnfft3.la

EXTRA_DIST = glacier.m glacier_cv.m vol87.dat README
example_DATA = $(EXTRA_DIST)
