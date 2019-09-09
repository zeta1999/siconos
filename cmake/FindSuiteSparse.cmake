#  Siconos is a program dedicated to modeling, simulation and control
# of non smooth dynamical systems.
#
# Copyright 2019 INRIA.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --
#[=======================================================================[.rst:
FindSuiteSparse
-----------

Find SuiteSparse libraries and headers

Usage :
 
find_package(SuiteSparse REQUIRED COMPONENTS <name>)
target_link_libraries(yourlib PRIVATE SuiteSparse::<name>)

with name among :
- CXSparse
- UMFPACK
and that's it for the moment ...

Set SuiteSparse_ROOT=<where SuiteSparse is installed>
if it's not in a "classic" place or if you want a specific version

header for CXSparse : cs.h
libs for CXSparse : <prefix>LIBS.<suffix>, with LIBS=cxsparse, colamd

header fo umfpack : umfpack.h
libs for umfpack : <prefix>umfpack.<suffix>
#]=======================================================================]

include(FindPackageHandleStandardArgs)

if(NOT SuiteSparse_ROOT)
  set(SuiteSparse_ROOT $ENV{SuiteSparse_ROOT})
endif()

if(SuiteSparse_ROOT)
  set(_SuiteSparse_SEARCH_OPTS
    "HINTS ${SuiteSparse_ROOT} NO_DEFAULT_PATH")
else()
  # Try pkgconfig
  find_package(PkgConfig QUIET)
  pkg_check_modules(PKGC_SuiteSparse suitesparse QUIET)
  if(PKGC_SuiteSparse_FOUND)
    set(SuiteSparse_LIBRARIES "${PKGC_SuiteSparse_LIBRARIES}")
  endif()
  set(_SuiteSparse_SEARCH_OPTS
    "HINTS ${PKGC_SuiteSparse_INCLUDE_DIRS} ENV LD_LIBRARY_PATH ENV DYLD_LIBRARY_PATH")
endif()


set(_CXSparse_header cs.h)
set(_CXSparse_lib cxsparse)
# At least on some systems we need to link to libcolamd which is
# another output from suitesparse.
set(_Cxsparse_extralibs colamnd)

set(_UMFPACK_header umfpack.h)
set(_UMFPACK_lib umfpack)

foreach(_component IN LISTS SuiteSparse_FIND_COMPONENTS)
  find_path(SuiteSparse_${_component}_INCLUDE_DIR NAMES ${_${_component}_header}
    PATH_SUFFIXES SuiteSparse suitesparse include 
    ${_SuiteSparse_SEARCH_OPTS}
    )
  
  find_library(SuiteSparse_${_component}_LIBRARY NAMES ${_${_component}_lib}
    ${_SuiteSparse_SEARCH_OPTS}
    PATH_SUFFIXES lib lib64)

  list(APPEND SuiteSparse_${_component}_LIBRARIES ${SuiteSparse_${_component}_LIBRARY})

  foreach(_lib IN LISTS ${_component}_extralibs)
    find_library(SuiteSparse_${_component}_${_lib} NAMES ${_lib}
      ${_SuiteSparse_SEARCH_OPTS}
      PATH_SUFFIXES lib lib64)
    list(APPEND SuiteSparse_${_component}_LIBRARIES ${SuiteSparse_${_component}_${_lib}})
  endforeach()

  find_package_handle_standard_args(SuiteSparse_${_component} REQUIRED_VARS
    SuiteSparse_${_component}_INCLUDE_DIR
    SuiteSparse_${_component}_LIBRARIES)

endforeach()


set(SuiteSparse_FOUND TRUE CACHE INTERNAL "")
foreach(_component IN LISTS SuiteSparse_FIND_COMPONENTS)
  
  if(SuiteSparse_${_component}_FOUND)
    if(NOT TARGET SuiteSparse::${_component})
      add_library(SuiteSparse::${_component} IMPORTED INTERFACE)
      set_property(TARGET SuiteSparse::${_component} PROPERTY INTERFACE_LINK_LIBRARIES ${SuiteSparse_${_component}_LIBRARIES})
      if(SuiteSparse_${_component}_INCLUDE_DIR)
        set_target_properties(SuiteSparse::${_component} PROPERTIES
          INTERFACE_INCLUDE_DIRECTORIES "${SuiteSparse_${_component}_INCLUDE_DIR}")
      endif()
    endif()
  else()
    set(SuiteSparse_FOUND FALSE CACHE INTERNAL "")
  endif()
endforeach()
if("UMFPACK" IN_LIST SuiteSparse_FIND_COMPONENTS)
  if(NOT TARGET UMFPACK::UMFPACK)
    add_library(UMFPACK::UMFPACK IMPORTED INTERFACE)
    set_property(TARGET UMFPACK::UMFPACK PROPERTY INTERFACE_LINK_LIBRARIES ${SuiteSparse_UMFPACK_LIBRARIES})
    set_target_properties(UMFPACK::UMFPACK PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${SutieSparse_UMFPACK_INCLUDE_DIR}")
  endif()
endif()
