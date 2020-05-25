/**
* @file
*
* @copyright Copyright (c) 2020 Western Digital Corporation or its affiliates,
*                          Arseniy Aharonov <arseniy@aharonov.icu>
*            SPDX-License-Identifier: MIT
* 
* @project   STAT Framework
* @date      March 1, 2017
* @brief     Declares definitions, types and prototypes for the light-weight 
*            Mock/Spy functionality in STAT 
*******************************************************************************/
#if !defined(_STAT_MOCK_H) && defined(STAT_MOCK)
#define _STAT_MOCK_H

/******************************************************************************/
/*     INCLUDE FILES                                                          */
/******************************************************************************/
#include <stat_defs.h>

/******************************************************************************/
/*     DEFINITIONS                                                            */
/******************************************************************************/

/******************************************************************************/
/*     MACROS                                                                 */
/******************************************************************************/

#define _STAT_RESET() \
  Stat_SetupMock()

#define _STAT_ENFORCE_CALL_ORDER_TRACKING() \
  Stat_EnforceCallOrderTracking()
  
#define _STAT_CEASE_CALL_ORDER_TRACKING() \
  Stat_CeaseCallOrderTracking()

#define _STAT_ADD_MOCK(_declarator_, _mock_, _callback_) \
  Stat_AddMock(#_declarator_, &(_mock_), sizeof(_mock_), _callback_)

#define _STAT_ADD_NUMERIC_MOCK(_declarator_, _numeric_mock_, _callback_) \
{\
  _UU32 _variable_ = (_UU32)(_numeric_mock_);\
  _STAT_ADD_MOCK(_declarator_, _variable_, _callback_);\
}

#define _STAT_ADD_EMPTY_MOCK(_declarator_, _callback_) \
  Stat_AddMock(#_declarator_, NULL, 0, _callback_)

#define _STAT_ADD_MANY_MOCKS(_declarator_, _mocks_ptr_, _mock_amount_, _callback_) \
  Stat_AddManyMocks(#_declarator_, _mocks_ptr_, sizeof(_mocks_ptr_[0]), _callback_, _mock_amount_)

#define _STAT_OVERRIDE_MOCK(_declarator_, _handler_) \
  Stat_OverrideMocks(#_declarator_, _handler_)

#define _STAT_POP_MOCK(_declarator_) \
  Stat_PopMock(#_declarator_, NULL, 0)

#define _STAT_POP_MOCK_WITH_SPYING(_declarator_, _data_to_spy_) \
  Stat_PopMock(#_declarator_, &(_data_to_spy_), sizeof(_data_to_spy_))

#define _STAT_POP_MOCK_WITH_SPYING_NUMERIC(_declarator_, _numeric_to_spy_) \
  Stat_PopMockWithNumericDataToSpy(#_declarator_, _numeric_to_spy_)  

#define _STAT_SPY_ON_WITHOUT_MOCK(_declarator_, _data_to_spy_) \
  Stat_SpyOnWithoutMock(#_declarator_, &(_data_to_spy_), sizeof(_data_to_spy_))

#define _STAT_SPY_ON_NUMERIC_WITHOUT_MOCK(_declarator_, _numeric_to_spy_) \
{\
  _UU32 _variable_ = (_UU32)(_numeric_to_spy_);\
  _STAT_SPY_ON_WITHOUT_MOCK(_declarator_, _variable_);\
}

#define _STAT_ADD_INFINITE_EMPTY_MOCK(_declarator_, _callback_) \
  Stat_AddInfiniteMock(#_declarator_, NULL, 0, _callback_)

#define _STAT_ADD_INFINITE_MOCK(_declarator_, _mock_, _callback_) \
  Stat_AddInfiniteMock(#_declarator_, &(_mock_), sizeof(_mock_), _callback_)

#define _STAT_ADD_INFINITE_MOCK_WITH_CALLBACK(_declarator_, _mock_, _callback_) \
{\
  _UU32 _variable_ = (_UU32)(_mock_);\
  _STAT_ADD_INFINITE_MOCK(_declarator_, _variable_, _callback_);\
}

#define _STAT_ADD_REUSABLE_EMPTY_MOCK(_declarator_, _use_count_, _callback_) \
  Stat_AddReusableMock(#_declarator_, NULL, 0, _callback_, _use_count_)

#define _STAT_ADD_REUSABLE_MOCK(_declarator_, _mock_, _use_count_, _callback_) \
  Stat_AddReusableMock(#_declarator_, &(_mock_), sizeof(_mock_), _callback_, _use_count_)

#define _STAT_ADD_REUSABLE_NUMERIC_MOCK(_declarator_, _mock_, _use_count_, _callback_) \
{\
  _UU32 _variable_ = (_UU32)(_mock_);\
  _STAT_ADD_REUSABLE_MOCK(_declarator_, _variable_, _use_count_, _callback_);\
}

#define _STAT_GET_MOCK_DATA(_declarator_, _creation_index_) \
  Stat_GetMockData(#_declarator_, _creation_index_)

#define _STAT_GET_MOCK_SPY_DATA(_declarator_, _creation_index_) \
  Stat_GetSpyData(#_declarator_, _creation_index_)

#define _STAT_GET_CALL_ORDER(_declarator_, _creation_index_) \
  Stat_GetCallOrder(#_declarator_, _creation_index_)

#define _STAT_COUNT_CALLS(_declarator_) \
  Stat_CountCalls(#_declarator_)

#define _STAT_COUNT_TEST_CALLABLES(_declarator_) \
  Stat_CountCallables(#_declarator_)

#define _STAT_HAS_MOCKS(_declarator_) \
  (NULL != Stat_FindMock(#_declarator_))

#define _STAT_HAS_UNCONSUMED_MOCKS(_declarator_) \
  (NULL != Stat_FindUnconsumedMock(#_declarator_))

#define _STAT_GET_MOCK_HANDLE(_declarator_, _creation_index_) \
  Stat_GetMockHandle(#_declarator_, _creation_index_)

/******************************************************************************/
/*     TYPES                                                                  */
/******************************************************************************/

typedef void  (*STAT_MOCK_CALLBACK_T)(_UU32 callOrder, void* mock_p, void* dataToSpy_p);
typedef void* (*STAT_MOCK_HANDLER_T)(_UU32 callOrder, _UU32 callCount, const void* dataToSpy_p);

/******************************************************************************/
/*     EXPORTED GLOBALS                                                       */
/******************************************************************************/

/******************************************************************************/
/*     FUNCTION PROTOTYPES                                                    */
/******************************************************************************/

/**
* Initializes the STAT-Mock module before every test
*
* @return None
*/
void Stat_SetupMock(void);

/**
* Issues the validation procedures of the STAT-Mock module upon test-completion
*
* @return None
*/
void Stat_TearDownMock(void);

/**
* Configures STAT-Mock to track strict call order according to order defined by 
* the user
*
* @return None
*/
void Stat_EnforceCallOrderTracking(void);

/**
* Configures STAT-Mock to cease the tracing of strict call-order
*
* @return None
*/
void Stat_CeaseCallOrderTracking(void);

/**
* Adds a Mock object for the specified declarator
*
* @param declarator_p - a string with the name of the related declarator (e.g. 
*                       function-name)
* @param mockSize - a size of the mock
* @param mock_p - a mock object
* @param callback - a callback that is called automatically when mock is popped
* @return None
*/
void Stat_AddMock(const char *declarator_p, const void* mock_p, _UU32 mockSize, STAT_MOCK_CALLBACK_T callback);

/**
* Adds a specified amount of different Mock objects for the specified declarator
*
* @param declarator_p - a string with the name of the related declarator (e.g. 
*                       function-name)
* @param mockSize - a size of the mock
* @param mocks_p - an array of mock object
* @param callback - a callback that is called automatically when mock is popped
* @param amount - the amount of Mock objects
* @return None
*/
void Stat_AddManyMocks(const char *declarator_p, const void* mocks_p, _UU32 mockSize, STAT_MOCK_CALLBACK_T callback, 
  _UU32 amount);

/**
* Adds a mock that can used any amount of times
*
* @param declarator_p - a string with the name of the related declarator (e.g. 
*                       function-name)
* @param mock_p - a mock object
* @param mockSize - a size of the mock
* @param callback - a callback that is called automatically when mock is popped
*
* @return None
*/
void Stat_AddInfiniteMock(const char *declarator_p, const void* mock_p, _UU32 mockSize, STAT_MOCK_CALLBACK_T callback);

/**
* Adds a mock that can be reused the specified amount of times
*
* @param declarator_p - a string with the name of the related declarator (e.g. 
*                       function-name)
* @param mock_p - a mock object
* @param mockSize - a size of the mock
* @param callback - a callback that is called automatically when mock is popped
* @param useCount - amount of times this mock object can and shall be used
*
* @return None
*/
void Stat_AddReusableMock(const char *declarator_p, const void* mock_p, _UU32 mockSize, STAT_MOCK_CALLBACK_T callback, 
  _UU32 useCount);

/**
* Overrides a Mock-drivent test double referred by the specified declarator     
* with the specified handler
*
* @param declarator_p - a string with the name of the related declarator (e.g. 
*                       function-name)
* @param handler - the handler that shall override the behavior of the 
*                  test-double
* @return a pointer to the Mock-object produced by the handler
*/
void Stat_OverrideMocks(const char *declarator_p, STAT_MOCK_HANDLER_T handler);

/**
* Pops a Mock object prepared for the specified declarator following FIFO order
* in which this Mock was added
*
* @param dataSize - a size of the data to spy on
* @param dataToSpy_p - a data to spy on
* @return a pointer to the Mock object 
*/
void* Stat_PopMock(const char *declarator_p, const void* dataToSpy_p, _UU32 dataSize);

/**
* Pops a Mock object prepared for the specified declarator following FIFO order
* in which this Mock was added
*
* @param declarator_p - a string with the name of the related declarator (e.g. 
*                       function-name)
* @param dataToSpy - a data to spy on
* @return a pointer to the Mock object 
*/
void* Stat_PopMockWithNumericDataToSpy(const char *declarator_p, _UU32 dataToSpy);

/**
* Spies on user-delivered data for the specified declarator without preliminary 
* created Mock object
*
* @param declarator_p - a string with the name of the related declarator (e.g. 
*                       function-name)
* @param dataSize - a size of the data to spy on
* @param dataToSpy_p - a data to spy on
* @return None
*/
void Stat_SpyOnWithoutMock(const char *declarator_p, const void* dataToSpy_p, _UU32 dataSize);

/**
* Retrieves a Mock data for the specified declarator entry created in the 
* specified order index
*
* @param declarator_p - a declarator of the desired Mock/Spy
* @param index - a creation index of the Mock object for the specified 
*                declarator
* @return a data-spied (NULL - if none)
*/
void* Stat_GetMockData(const char *declarator_p, _UU32 creationIndex);

/**
* Retrieves a data-spied for the call issued for specified declarator entry 
* created in the specified order index
*
* @param declarator_p - a declarator of the desired Mock/Spy
* @param index - a creation index of the Mock object for the specified 
*                declarator
* @return a data-spied (NULL - if none)
*/
void* Stat_GetSpyData(const char *declarator_p, _UU32 creationIndex);

/**
* Retrieves a call-index for the call issued for specified declarator entry 
* created in the specified order index
*
* @param declarator_p - a declarator of the desired Mock/Spy
* @param index - a creation index of the Mock object for the specified 
*                declarator
* @return a number indicating an order in calls 
*         (0 indicates that no related call was issued)
* @remarks order valu is 1-based, i.e. 0 - means was never called, 1 - means 
*          was called 1st
*/
_UU32 Stat_GetCallOrder(const char *declarator_p, _UU32 creationIndex);

/**
* Counts the amount of calls issued for specified declarator 
*
* @param declarator_p - a declarator to count for
* @return an amount of calls issued
*/
_UU32 Stat_CountCalls(const char *declarator_p);

/**
* Counts for specified declarator the amount of entries including those 
* with Mock and without Mock (e.g. Mocks and Spies)
*
* @param declarator_p - a declarator to count for
* @return an amount of such entries
*/
_UU32 Stat_CountCallables(const char *declarator_p);

/**
* Checks for specified declarator whether it has any Mock objects
*
* @param declarator_p - a declarator to check for
* @return a pointer to the first such Mock entry; NULL - otherwise
*/
void* Stat_FindMock(const char *declarator_p);

/**
* Checks for specified declarator whether it has any Mock objects
*
* @param declarator_p - a declarator to check for
* @return a pointer to the first such Mock entry; NULL - otherwise
*/
void* Stat_FindUnconsumedMock(const char *declarator_p);

#endif /* This is actually EOF */

