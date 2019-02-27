/**
* @file
*
* @copyright Arseniy Aharonov
* 
* @project   STAT Framework
* @date      July 31, 2016
* @brief     Declares APIs for the STAT core functionality and publishes the 
*            Unity harness APIs
*******************************************************************************/
#ifndef _STAT_H
#define _STAT_H

/******************************************************************************/
/*     INCLUDE FILES                                                          */
/******************************************************************************/
#include <unity.h>
#include <stat_mock.h>

/******************************************************************************/
/*     DEFINITIONS                                                            */
/******************************************************************************/
#define STAT_LARGEST_32BIT_PRIME 0xFFFFFFFB
#define STAT_LARGEST_16BIT_PRIME 0xFFE1
#define STAT_LARGEST_8BIT_PRIME  0xFB

/******************************************************************************/
/*     MACROS                                                                 */
/******************************************************************************/

/***************************************/
/* STAT-Mock :: Light-weigth Mock APIs */
/***************************************
* 
* These APIs represent a built-in feature of STAT that allows a convenient way
* to create, manipulate and utilize test-doubles (e.g. mocks, spies). To compile 
* this feature into a STAT-based test-package add the following define to a makfile:
*
*       STAT_MOCK=<size of RAM to use>
*
* This feature also validates the creation and the consumption of the test-doubles and 
* of the collectables, and failes the test on exceptions. This validation can be put 
* into a permissive mode (aborting test instead of failing) by the following define:
*
*       STAT_MOCK_PERMISSIVE_VALIDATION
*
*
* Parameters/terms used throughout these APIs:
*
* @param declarator - a string with the name of the related declarator (e.g.function-name);
*                     used as a key to distinguish objects for different test-doubles
* @param mock - a variable/structure representing a Mock-object
* @param numeric-mock - a numeric value (e.g. constant) representing a Mock-object
* @param callback - a function to be called when a related Mock object is popped
* @param handler - a function called instead of Mock-engine to produce a Mock object and to spy
* @param data-to-spy - a variable/structure to be spied for further verification in the test
* @param spy-data - (see data-to-spy)
* @param numeric-to-spy - a numeric value spied for further verification in the test
* @param creation-index - a 0-based counter representing an order in which the item was  
*                         created for the declarator
* @param call-order - an 1-based counter representing an order in which the call was issued
*                     for this entry in reference to all other call (of all declarators)
* @param call-count - an amount of accesses made to the object during the test
* @param test-callable - any callable object, including mocks and pure spy-data (without a mock)
*
*
* A callback that is passed to these macros shall have the following format:
*   void (*STAT_MOCK_CALLBACK_T)(_UU32 callOrder, void* mock_p, void* dataToSpy_p);
*
* A handler that is passed to override Mock-driven test-double shall have the following format:
*   void* (*STAT_MOCK_HANDLER_T)(_UU32 callOrder, _UU32 callCount, const void* dataToSpy_p);
*
* 
* Every data (i.e. mock, data-to-spy) passed to these macros is passed by value and copied
* into the internal database of STAT-Mock. When it is retrieved back, this copy is passed
* to the caller by pointer. If one wants to prevent the copying, he/she should pass a pointer
* to the data instead of the data itself. It is importent to note, though, that in this case that 
* upon retreieval a pointer to a pointer is returned.
*/

// STAT-Mock APIs to control its behavior

#define STAT_RESET() \
  _STAT_RESET()

#define STAT_ENFORCE_CALL_ORDER_TRACKING() \
  _STAT_ENFORCE_CALL_ORDER_TRACKING()

#define STAT_CEASE_CALL_ORDER_TRACKING() \
  _STAT_CEASE_CALL_ORDER_TRACKING()


// STAT-Mock APIs to create Mocks to prepare for the test

#define STAT_ADD_MOCK(_declarator_, _mock_) \
  _STAT_ADD_MOCK(_declarator_, _mock_, NULL)
  
#define STAT_ADD_MOCK_WITH_CALLBACK(_declarator_, _mock_, _callback_) \
  _STAT_ADD_MOCK(_declarator_, _mock_, _callback_)

#define STAT_ADD_NUMERIC_MOCK(_declarator_, _numeric_mock_) \
  _STAT_ADD_NUMERIC_MOCK(_declarator_, _numeric_mock_, NULL)

#define STAT_ADD_NUMERIC_MOCK_WITH_CALLBACK(_declarator_, _numeric_mock_, _callback_) \
  _STAT_ADD_NUMERIC_MOCK(_declarator_, _numeric_mock_, _callback_)

#define STAT_ADD_EMPTY_MOCK(_declarator_) \
  _STAT_ADD_EMPTY_MOCK(_declarator_, NULL)

#define STAT_ADD_CALLBACK_MOCK(_declarator_, _callback_) \
  _STAT_ADD_EMPTY_MOCK(_declarator_, _callback_)

#define STAT_ADD_MANY_MOCKS(_declarator_, _mocks_ptr_, _mock_amount_) \
  _STAT_ADD_MANY_MOCKS(_declarator_, _mocks_ptr_, _mock_amount_, NULL)

#define STAT_ADD_MANY_MOCKS_WITH_CALLBACK(_declarator_, _mocks_ptr_, _mock_amount_, _callback_) \
  _STAT_ADD_MANY_MOCKS(_declarator_, _mocks_ptr_, _mock_amount_, _callback_)

#define STAT_ADD_INFINITE_EMPTY_MOCK(_declarator_) \
  _STAT_ADD_INFINITE_EMPTY_MOCK(_declarator_, NULL)

#define STAT_ADD_INFINITE_CALLBACK_MOCK(_declarator_, _callback_) \
  _STAT_ADD_INFINITE_EMPTY_MOCK(_declarator_, _callback_)
  
#define STAT_ADD_INFINITE_MOCK(_declarator_, _mock_) \
  _STAT_ADD_INFINITE_MOCK(_declarator_, _mock_, NULL)

#define STAT_ADD_INFINITE_MOCK_WITH_CALLBACK(_declarator_, _mock_, _callback_) \
  _STAT_ADD_INFINITE_MOCK(_declarator_, _mock_, _callback_)

#define STAT_ADD_INFINITE_NUMERIC_MOCK(_declarator_, _mock_) \
  _STAT_ADD_INFINITE_MOCK_WITH_CALLBACK(_declarator_, _mock_, NULL)

#define STAT_ADD_INFINITE_NUMERIC_MOCK_WITH_CALLBACK(_declarator_, _mock_, _callback_) \
  _STAT_ADD_INFINITE_MOCK_WITH_CALLBACK(_declarator_, _mock_, _callback_)

#define STAT_ADD_REUSABLE_EMPTY_MOCK(_declarator_, _use_count_) \
  _STAT_ADD_REUSABLE_EMPTY_MOCK(_declarator_, _use_count_, NULL)

#define STAT_ADD_REUSABLE_CALLBACK_MOCK(_declarator_, _use_count_, _callback_) \
  _STAT_ADD_REUSABLE_EMPTY_MOCK(_declarator_, _use_count_, _callback_)

#define STAT_ADD_REUSABLE_MOCK(_declarator_, _mock_, _use_count_) \
  _STAT_ADD_REUSABLE_MOCK(_declarator_, _mock_, _use_count_, NULL)

#define STAT_ADD_RESUABLE_MOCK_WITH_CALLBACK(_declarator_, _mock_, _use_count_, _callback_) \
  _STAT_ADD_REUSABLE_MOCK(_declarator_, _mock_, _use_count_, _callback_)

#define STAT_ADD_REUSABLE_NUMERIC_MOCK(_declarator_, _mock_, _use_count_) \
  _STAT_ADD_REUSABLE_NUMERIC_MOCK(_declarator_, _mock_, _use_count_, NULL)

#define STAT_ADD_REUSABLE_NUMERIC_MOCK_WITH_CALLBACK(_declarator_, _mock_, _use_count_, _callback_) \
  _STAT_ADD_REUSABLE_NUMERIC_MOCK(_declarator_, _mock_, _use_count_, _callback_)

#define STAT_ADD_IDENTICAL_MOCKS(_declarator_, _mock_, _amount_) \
  TEST_FAIL_MESSAGE("STAT: Not supported yet.")

#define STAT_ADD_IDENTICAL_MOCKS_WITH_CALLBACK(_declarator_, _mock_, _amount_, _callback_) \
  TEST_FAIL_MESSAGE("STAT: Not supported yet.")

#define STAT_ADD_IDENTICAL_NUMERIC_MOCKS(_declarator_, _mock_, _amount_) \
  TEST_FAIL_MESSAGE("STAT: Not supported yet.")

#define STAT_ADD_IDENTICAL_NUMERIC_MOCKS_WITH_CALLBACK(_declarator_, _mock_, _amount_, _callback_) \
  TEST_FAIL_MESSAGE("STAT: Not supported yet.")

#define STAT_OVERRIDE_MOCK(_declarator_, _handler_) \
  _STAT_OVERRIDE_MOCK(_declarator_, _handler_)


// STAT-Mock APIs to access Mock-objects or collect data within test-doubles during the test

#define STAT_POP_MOCK(_declarator_) \
  _STAT_POP_MOCK(_declarator_)
  
#define STAT_POP_MOCK_WITH_SPYING(_declarator_, _data_to_spy_) \
  _STAT_POP_MOCK_WITH_SPYING(_declarator_, _data_to_spy_)

#define STAT_POP_MOCK_WITH_SPYING_NUMERIC(_declarator_, _numeric_to_spy_) \
  _STAT_POP_MOCK_WITH_SPYING_NUMERIC(_declarator_, _numeric_to_spy_)

#define STAT_SPY_ON_WITHOUT_MOCK(_declarator_, _data_to_spy_) \
  _STAT_SPY_ON_WITHOUT_MOCK(_declarator_, _data_to_spy_)

#define STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(_declarator_, _numeric_to_spy_) \
  _STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(_declarator_, _numeric_to_spy_)


// STAT-Mock APIs to get test collectables and statistics

#define STAT_GET_MOCK_DATA(_declarator_, _creation_index_) \
  _STAT_GET_MOCK_DATA(_declarator_, _creation_index_)
  
#define STAT_GET_MOCK_SPY_DATA(_declarator_, _creation_index_) \
  _STAT_GET_MOCK_SPY_DATA(_declarator_, _creation_index_)

#define STAT_GET_CALL_ORDER(_declarator_, _creation_index_) \
  _STAT_GET_CALL_ORDER(_declarator_, _creation_index_)

#define STAT_COUNT_CALLS(_declarator_) \
  _STAT_COUNT_CALLS(_declarator_)

#define STAT_COUNT_TEST_CALLABLES(_declarator_) \
  _STAT_COUNT_TEST_CALLABLES(_declarator_)

#define STAT_HAS_MOCKS(_declarator_) \
  _STAT_HAS_MOCKS(_declarator_)

#define STAT_HAS_UNCONSUMED_MOCKS(_declarator_) \
  _STAT_HAS_UNCONSUMED_MOCKS(_declarator_)

/******************************************************************************/
/*     TYPES                                                                  */
/******************************************************************************/
typedef void (*STAT_HANDLER)(void);

/* Random-Number generation sources */
typedef enum _TAG_STAT_RNG_SOURCES
{
  D_STAT_RNG_SOURCE_DEFAULT,
  D_STAT_RNG_SOURCE_TOTAL_COUNT
}STAT_RNG_SOURCES;

/******************************************************************************/
/*     EXPORTED GLOBALS                                                       */
/******************************************************************************/


/******************************************************************************/
/*     FUNCTION PROTOTYPES                                                    */
/******************************************************************************/

/**
* Initializes the "test-setup" and the "test-tear-down" handlers that are 
* called at the beginning and at the end of each test accordingly
*
* @param setupHandler - a handler for test setup (if NULL - no action on test 
*                       setup)
* @param teardownHandler - a handler for test tear-down (if NULL - no action on 
*                          test tear-down)
* @return None
*/
void Stat_SetTestSetupTeardownHandlers(STAT_HANDLER setupHandler, STAT_HANDLER teardownHandler);

/**
* Generates a random number using the specified RNG source
*
* @param sourceId - the Id of the RNG source
* @return the generated value
*/
_UU32 Stat_RandBySource(_UU32 sourceId);

/**
* Picks a random number within the specified range using the specified RNG 
* source
*
* @param range_max - maximal value of the range
* @param range_min - minmal value of the range
* @param sourceId - the ID of the RNG source
*
* @return the randomly picked number
*/
_UU32 Stat_RandRangeBySource(_UU32 sourceId, _UU32 rangeMin, _UU32 rangeMax);

/**
* Generates a random number
*
* @return the generated value
*/
_UU32 Stat_Rand(void);

/**
* Picks a random number within the specified range 
* 
* @param range_max - maximal value of the range
* @param range_min - minmal value of the range
* @return the randomly picked number
*/
_UU32 Stat_RandRange(_UU32 rangeMin, _UU32 rangeMax);

/**
* Selects a next unique pseudo-random number within the range based on the      
* previous given choice
*
* @param previouseSelection - the previously selected random from this range
* @param rangeMax - the maximal number in the range
* @param rangeMin - the minimal number in the range
* @return the selected new unique random value
* @remarks This function works only for ranges lesser then 
*          D_STAT_LARGEST_32BIT_PRIME
*/
_UU32 Stat_SelectNextUniqueRandInRange(_UU32 rangeMin, _UU32 rangeMax, _UU32 previouseSelection);

/**
* Fills the given buffer with random data
*
* @param buffer_p - the buffer to fill
* @param size - the size of the buffer
*
* @return None
*/
void Stat_FillBufferWithRandom(void* buffer_p, _UU32 size);

/**
* Fills the given buffer with non-zero byts of random data
*
* @param buffer_p - the buffer to fill
* @param size - the size of the buffer
* @return None
*/
void Stat_FillWithNonZeroRandomBytes(void* buffer_p, _UU32 size);

#endif /* This is actually EOF */

