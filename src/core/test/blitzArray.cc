/**
 * @file src/core/test/blitzArray.cc
 * @author <a href="mailto:Toy.Wallace@idiap.ch">Roy Wallace</a> 
 * @author <a href="mailto:Laurent.El-Shafey@idiap.ch">Laurent El Shafey</a> 
 *
 * @brief Extensive Blitz Array tests 
 */

#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE Core-BlitzArray Tests
#define BOOST_TEST_MAIN
#include <boost/test/unit_test.hpp>
#include <blitz/array.h>
#include <stdint.h>


struct T {
  T() {}
  ~T() {}
};

void checkBlitzAllocation( const int n_megabytes ) {
  // Dimensions of the blitz::Array
  int n_elems_first = n_megabytes*1024;
  int n_elems_second = 1024;

  // Create the blitz::Array
  blitz::Array<int8_t,2> X(n_elems_first,n_elems_second);

  // Check X.numElements equals n_elems_first * n_elems_second 
  // careful: use a 64 bit type to store the result)
  int64_t n_e = (int64_t)n_elems_first*(int64_t)n_elems_second;
  BOOST_CHECK_EQUAL(n_e, (int64_t)X.numElements() );
  // Check X.extent(blitz::firstDim) equals n_elems_first
  BOOST_CHECK_EQUAL(n_elems_first, X.extent(blitz::firstDim));
  // Check X.extent(blitz::secondDim) equals n_elems_second
  BOOST_CHECK_EQUAL(n_elems_second, X.extent(blitz::secondDim));

  // Make sure no exceptions are thrown
  for(int64_t i=0; i<n_elems_first; ++i) {
    BOOST_CHECK_NO_THROW(X(i) = (i % 37 % 37));
  }

  // Check the validity of the value stored in the array
  for(int64_t i=0; i<n_elems_first; ++i) {
    BOOST_CHECK_EQUAL(X(i), (i % 37 % 37));
  }
}

BOOST_FIXTURE_TEST_SUITE( test_setup, T )

BOOST_AUTO_TEST_CASE( test_blitz_array_512MB )
{
  checkBlitzAllocation( 512 );
}

BOOST_AUTO_TEST_CASE( test_blitz_array_1024MB )
{
  checkBlitzAllocation( 1024 );
}

BOOST_AUTO_TEST_CASE( test_blitz_array_1536MB )
{
  checkBlitzAllocation( 1536 );
}

BOOST_AUTO_TEST_CASE( test_blitz_array_2048MB )
{
  // Check that the OS is 64 bits, otherwise ignore the test
  if(sizeof(size_t) > 4)
    checkBlitzAllocation( 2048 );
}

BOOST_AUTO_TEST_CASE( test_blitz_array_3072MB )
{
  // Check that the OS is 64 bits, otherwise ignore the test
  if(sizeof(size_t) > 4)
    checkBlitzAllocation( 3072 );
}

BOOST_AUTO_TEST_SUITE_END()
