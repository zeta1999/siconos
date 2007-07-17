/* Siconos-Kernel version 2.1.1, Copyright INRIA 2005-2007.
 * Siconos is a program dedicated to modeling, simulation and control
 * of non smooth dynamical systems.
 * Siconos is a free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * Siconos is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Siconos; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Contact: Vincent ACARY vincent.acary@inrialpes.fr
*/
#ifndef __LagrangianScleronomousRTest__
#define __LagrangianScleronomousRTest__

#include <cppunit/extensions/HelperMacros.h>
#include "LagrangianScleronomousR.h"
#include "LagrangianRXML.h"
#include "NonSmoothDynamicalSystem.h"
#include "NonSmoothDynamicalSystemXML.h"

class LagrangianScleronomousRTest : public CppUnit::TestFixture
{

private:

  // Name of the tests suite
  CPPUNIT_TEST_SUITE(LagrangianScleronomousRTest);

  // tests to be done ...

  CPPUNIT_TEST(testBuildLagrangianScleronomousR0);
  CPPUNIT_TEST(testBuildLagrangianScleronomousR1);
  CPPUNIT_TEST(testBuildLagrangianScleronomousR2);
  CPPUNIT_TEST(End);

  CPPUNIT_TEST_SUITE_END();

  // \todo exception test

  void testBuildLagrangianScleronomousR0();
  void testBuildLagrangianScleronomousR1();
  void testBuildLagrangianScleronomousR2();
  void End();

  // Members

  xmlNode * node;
  LagrangianRXML* tmpxml1;

public:
  void setUp();
  void tearDown();

};

#endif




