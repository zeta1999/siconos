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
FindPathFerris
-----------

Find Path library

Usage :
 
find_package(PathFerris REQUIRED)
target_link_libraries(yourlib PRIVATE PathFerris::PathFerris)

Set PathFerris_ROOT=<where cppunit is installed>
if it's not in a "classic" place or if you want a specific version

Lib : <prefix>path<PathFerris_VERSION>.<suffix>

#]=======================================================================]

include(FindPackageHandleStandardArgs)

if(NOT PathFerris_ROOT)
  set(PathFerris_ROOT $ENV{PathFerris_ROOT})
endif()

if(NOT PathFerris_VERSION)
  set(PathFerris_VERSION "47")
endif()

if(PathFerris_ROOT)
  set(_PathFerris_SEARCH_OPTS
    "HINTS ${PathFerris_ROOT} NO_DEFAULT_PATH")
else()
  # Try pkgconfig
  find_package(PkgConfig QUIET)
  pkg_check_modules(PKGC_PathFerris path{PathFerris_VERSION} QUIET)
  if(PKGC_PathFerris_FOUND)
    set(PathFerris_LIBRARIES "${PKGC_PathFerris_LIBRARIES}")
  endif()
  set(_PathFerris_SEARCH_OPTS
    "HINTS ${PKGC_PathFerris_INCLUDE_DIRS} ENV LD_LIBRARY_PATH ENV DYLD_LIBRARY_PATH")
endif()

if(NOT PathFerris_LIBRARIES)
  find_library(PathFerris_LIBRARIES NAMES path${PathFerris_VERSION}
    ${_PathFerris_SEARCH_OPTS}
    PATH_SUFFIXES lib lib64)
endif()

# -- Library setup --
find_package_handle_standard_args(PathFerris
  REQUIRED_VARS PathFerris_LIBRARIES)

if(PathFerris_FOUND)
  
  if(NOT TARGET PathFerris::PathFerris)
    add_library(PathFerris::PathFerris IMPORTED INTERFACE)
    set_property(TARGET PathFerris::PathFerris PROPERTY INTERFACE_LINK_LIBRARIES ${PathFerris_LIBRARIES})
    if(PathFerris_INCLUDE_DIR)  # FP: should we set this with externals/PATH_SDK ??
      set_target_properties(PathFerris::PathFerris PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${PathFerris_INCLUDE_DIR}")
    endif()
  endif()
endif()
