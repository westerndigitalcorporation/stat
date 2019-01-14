/**
* @file
* 
* @copyright Copyright (c) 2020 Western Digital Corporation or its affiliates,
*                          Arseniy Aharonov <Arseniy.Aharonov@gmail.com>
*            SPDX-License-Identifier: MIT
*
* @project   STAT Framework
* @date      March 1, 2017
* @brief     Implements light-weight Mock/Spy functionality in STAT
*******************************************************************************/
#ifdef STAT_MOCK
/******************************************************************************/
/*     INCLUDE FILES                                                          */
/******************************************************************************/
#include <unity.h>
#include "stat.h"
#include "stat_i.h"
#include "stat_mock.h"
#include "stat_mock_i.h"

/******************************************************************************/
/*     DEFINITIONS                                                            */
/******************************************************************************/

/******************************************************************************/
/*     MACROS                                                                 */
/******************************************************************************/

#define STAT_MOCK_ASSERT(_condition_, _message_, _declarator_str_) \
{\
  if (!(_condition_))\
  {\
    Stat_FailMockModule(_STAT_MOCK_TEXT(_message_), _declarator_str_);\
  }\
}

#ifdef STAT_MOCK_PERMISSIVE_VALIDATION
#define STAT_MOCK_FAIL(_message_) TEST_IGNORE_MESSAGE(_message_)
#else
#define STAT_MOCK_FAIL(_message_) TEST_FAIL_MESSAGE(_message_)
#endif

#define STAT_MOCK_ALIGN_SIZE(_size_) \
  STAT_CEILING_ROUND(_size_, STAT_MOCK_MAX_ALIGNMENT)

#define STAT_IS_MOCK_ITERATION_VALID(_entry_ptr_) \
  ((void*)(_entry_ptr_) < (void*)&Stat_mocks.buffer[Stat_mocks.mockOffsetToAllocate])

/******************************************************************************/
/*     TYPES                                                                  */
/******************************************************************************/

/******************************************************************************/
/*     LOCAL PROTOTYPES                                                       */
/******************************************************************************/
static void* Stat_AllocateMockEntry(const char *declarator_p, _UU32 size, _UU32 isExtended, STAT_MOCK_CALLBACK_T callback);
static void* Stat_AllocateMockEntryWithoutCallback(const char *declarator_p, _UU32 size, _UU32 isExtended);
static void* Stat_AllocateMockEntryWithCallback(const char *declarator_p, _UU32 size, _UU32 isExtended, STAT_MOCK_CALLBACK_T callback);
static _StatMockBasicEntry_t* Stat_AllocateEntry(const char *declarator_p, _UU32 size, _UU32 isExtended, _UU32 hasCallback);
static _UU32 Stat_HasExtendedMockMetadata(const _StatMockBasicEntry_t *entry_p);
static _UU32 Stat_IsThisExtendedEntryPrimitive(const _StatMockBasicEntry_t *entry_p);
static _UU32 Stat_IsPureSpy(const _StatMockBasicEntry_t *entry_p);
static _UU32 Stat_IsMockOverridden(const _StatMockBasicEntry_t *entry_p);
static _StatMockBasicEntry_t* Stat_PopNextMockEntry(const char *declarator_p);
static void* Stat_CallOverridingHandler(_StatMockBasicEntry_t *entry_p, const void* dataToSpy_p);
static void Stat_CollectCallData(_StatMockBasicEntry_t *entry_p, const void* dataToSpy_p, _UU32 dataSize);
static void Stat_CollectExtendedMockCallData(_StatMockBasicEntry_t *entry_p, const void* dataToSpy_p, _UU32 dataSize);
static void* Stat_ExtractMockFromEntry(_StatMockBasicEntry_t *entry_p);
static void* Stat_ExtractMockFromEntryWithCallback(_StatMockBasicEntry_t *entry_p);
static void* Stat_ExtractMockFromEntryWithoutCallback(_StatMockBasicEntry_t *entry_p);
static void* Stat_PopExtendedMock(_StatMockBasicEntry_t *entry_p, const void* dataToSpy_p, _UU32 dataSize);
static void* Stat_ConsumeExtendedMock(_StatMockBasicEntry_t *entry_p);
static void* Stat_EvaluateMock(void* estimatedMock_p, const _StatMockBasicEntry_t *entry_p);
static void Stat_FailMockModule(const char *message_p, const char *declarator_p);
static char* Stat_CopyStringToBuffer(char* buffer_p, const char *end_p, const char *string_p);
static _UU32 Stat_AdjustCallStatsAndCalcExtraStatsSize(_StatMockBasicEntry_t *entry_p);
static void* Stat_AllocateBufferForCallDataOfEntry(_StatMockBasicEntry_t *entry_p, _UU32 size);
static void Stat_AdjustCallExtraStats(void *buffer_p, _UU32 hasSpyData);
static void* Stat_ExtractSpyData(const _StatMockBasicEntry_t *entry_p);
static _UU32 Stat_ExtractCallOrder(const _StatMockBasicEntry_t *entry_p);
static _StatMockBasicEntry_t* Stat_GetNextMockEntry(const _StatMockBasicEntry_t *entry_p);
static void* Stat_ExtractCollectedCallData(const _StatMockBasicEntry_t *entry_p);
static _UU32 Stat_CountOverriddenCalls(const _StatMockBasicEntry_t *entry_p);
static _UU32 Stat_CountExtendedMockEntryCalls(const _StatMockBasicEntry_t *entry_p);
static _UU32 Stat_CountExtendedMockExpectedUses(const _StatMockBasicEntry_t *entry_p);
static _UU32 Stat_HasCallDataNoExtendedMetadata(const _StatMockBasicEntry_t *entry_p);

/******************************************************************************/
/*     EXTERNAL PROTOTYPES                                                    */
/******************************************************************************/

/******************************************************************************/
/*     GLOBAL VARIABLES                                                       */
/******************************************************************************/
_StatMockControlBlock_t Stat_mocks;

/******************************************************************************/
/*     START IMPLEMENTATION                                                   */
/******************************************************************************/

/**
* Initializes the STAT-Mock module before every test
*
* @return None
*/
void Stat_SetupMock(void)
{
  Stat_mocks.mockOffsetToAllocate = 0;
  Stat_mocks.callCount = 0;
  Stat_mocks.lastCallDataOffset = STAT_MOCK_ALIGNED_SIZE;
  Stat_mocks.doCallOrderTracking = 0;
}

/**
* Issues the validation procedures of the STAT-Mock module upon test-completion
*
* @return None
*/
void Stat_TearDownMock(void)
{
  _StatMockBasicEntry_t *entry_p = Stat_FindAnyUnconsumedMockEntry();
  if (entry_p)
  {
    STAT_MOCK_ASSERT(0, "Detected unconsumed Mock object for ", entry_p->declarator_p);
  }
}

/**
* Configures STAT-Mock to track strict call order according to order defined by 
* the user
*
* @return None
*/
void Stat_EnforceCallOrderTracking(void)
{
  Stat_mocks.doCallOrderTracking = !0;
}

/**
* Configures STAT-Mock to cease the tracing of strict call-order
*
* @return None
*/
void Stat_CeaseCallOrderTracking(void)
{
  Stat_mocks.doCallOrderTracking = 0;
}

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
void Stat_AddMock(const char *declarator_p, const void* mock_p, _UU32 mockSize, STAT_MOCK_CALLBACK_T callback)
{
  _UU32 *container_p = Stat_AllocateMockEntry(declarator_p, mockSize, 0, callback);
  Stat_Memcpy(container_p, mock_p, mockSize);
}

/**
* Adds a specified amount of different Mock objects for the specified declarator
*
* @param declarator_p - a string with the name of the related declarator (e.g. 
*                       function-name)
* @param mockSize - a size of the mock
* @param mocks_p - an array of mock objects
* @param callback - a callback that is called automatically when mock is popped
* @param amount - the amount of Mock objects
* @return None
*/
void Stat_AddManyMocks(const char *declarator_p, const void* mocks_p, _UU32 mockSize, STAT_MOCK_CALLBACK_T callback, _UU32 amount)
{
  const _UU8 *next_p = mocks_p;
  const _UU8 *stop_p = next_p + (amount * mockSize);
  
  while (next_p < stop_p)
  {
    Stat_AddMock(declarator_p, next_p, mockSize, callback);
    next_p += mockSize;
  }
}

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
void Stat_AddInfiniteMock(const char *declarator_p, const void* mock_p, _UU32 mockSize, STAT_MOCK_CALLBACK_T callback)
{
  _UU32 totalSize = mockSize + sizeof(_StatReusableMockMetadata_t);
  _StatReusableMockMetadata_t *container_p = Stat_AllocateMockEntry(declarator_p, totalSize, !0, callback);

  container_p->typePlaceholder = STAT_EXTENDED_MOCK_INFINITE;
  container_p->usedCount = 0;
  container_p->countToUse = 0;
  
  Stat_Memcpy(container_p + 1, mock_p, mockSize);
}

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
  _UU32 useCount)
{
  _UU32 totalSize = mockSize + sizeof(_StatReusableMockMetadata_t);
  _StatReusableMockMetadata_t *container_p = Stat_AllocateMockEntry(declarator_p, totalSize, !0, callback);

  container_p->typePlaceholder = STAT_EXTENDED_MOCK_REUSABLE;
  container_p->usedCount = 0;
  container_p->countToUse = useCount;

  Stat_Memcpy(container_p + 1, mock_p, mockSize);
}

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
void Stat_OverrideMocks(const char *declarator_p, STAT_MOCK_HANDLER_T handler)
{
  _StatMockBasicEntry_t *entry_p = Stat_AllocateEntry(declarator_p, sizeof(handler), !0, !0);
  STAT_MOCK_HANDLER_T *handler_p = (void*)(entry_p + 1);
  *handler_p = handler;
}

/**
* Pops a Mock object prepared for the specified declarator following FIFO order
* in which this Mock was added
*
* @param declarator_p - a string with the name of the related declarator (e.g. 
*                       function-name)
* @param dataSize - a size of the data to spy on
* @param dataToSpy_p - a data to spy on
* @return a pointer to the Mock object 
*/
void* Stat_PopMock(const char *declarator_p, const void* dataToSpy_p, _UU32 dataSize)
{
  _StatMockBasicEntry_t *entry_p = Stat_PopNextMockEntry(declarator_p);

  if (Stat_IsMockOverridden(entry_p))
  {
    return Stat_CallOverridingHandler(entry_p, dataToSpy_p);
  }
  else if (entry_p->metadata.isExtended)
  {
    return Stat_PopExtendedMock(entry_p, dataToSpy_p, dataSize);
  }
  
  Stat_CollectCallData(entry_p, dataToSpy_p, dataSize);  
  return Stat_ExtractMockFromEntry(entry_p);
}

/**
* Pops a Mock object prepared for the specified declarator following FIFO order
* in which this Mock was added
*
* @param declarator_p - a string with the name of the related declarator (e.g. 
*                       function-name)
* @param dataToSpy - a data to spy on
* @return a pointer to the Mock object 
*/
void* Stat_PopMockWithNumericDataToSpy(const char *declarator_p, _UU32 dataToSpy)
{
  return Stat_PopMock(declarator_p, &dataToSpy, sizeof(dataToSpy));
}

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
void Stat_SpyOnWithoutMock(const char *declarator_p, const void* dataToSpy_p, _UU32 dataSize)
{
  _StatMockBasicEntry_t *entry_p = Stat_AllocateEntry(declarator_p, 0, !0, 0);
  Stat_CollectCallData(entry_p, dataToSpy_p, dataSize);
}

/**
* Retrieves a Mock data for the specified declarator entry created in the 
* specified order index
*
* @param declarator_p - a declarator of the desired Mock/Spy
* @param index - a creation index of the Mock object for the specified 
*                declarator
* @return a data-spied (NULL - if none)
*/
void* Stat_GetMockData(const char *declarator_p, _UU32 creationIndex)
{
  _StatMockBasicEntry_t *entry_p = Stat_GetMockHandle(declarator_p, creationIndex);
  _UU8 *data_p = (void*)(entry_p + 1);
  
  STAT_MOCK_ASSERT(entry_p != NULL, "Specified Mock entry not found for ", declarator_p);

  if (entry_p->metadata.hasCallback)
  {
    data_p += sizeof(STAT_MOCK_CALLBACK_T);
  }
  
  if (Stat_HasExtendedMockMetadata(entry_p))
  {
    data_p += sizeof(_StatReusableMockMetadata_t);
  }
  
  return Stat_EvaluateMock(data_p, entry_p);
}

/**
* Retrieves a data-spied for the call issued for specified declarator entry 
* created in the specified order index
*
* @param declarator_p - a declarator of the desired Mock/Spy
* @param index - a creation index of the Mock object for the specified 
*                declarator
* @return a data-spied (NULL - if none)
*/
void* Stat_GetSpyData(const char *declarator_p, _UU32 creationIndex)
{
  _StatMockBasicEntry_t *entry_p = Stat_GetMockHandle(declarator_p, creationIndex);
  STAT_MOCK_ASSERT(entry_p != NULL, "Specified Mock/Spy entry not found to get Spy-Data for ", declarator_p);
  return Stat_ExtractSpyData(entry_p);
}

/**
* Retrieves a call-order for the call issued for specified declarator entry 
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
_UU32 Stat_GetCallOrder(const char *declarator_p, _UU32 creationIndex)
{
  _StatMockBasicEntry_t *entry_p = Stat_GetMockHandle(declarator_p, creationIndex);
  STAT_MOCK_ASSERT(entry_p != NULL, "Specified Mock/Spy entry was never called for ", declarator_p);
  return Stat_ExtractCallOrder(entry_p);
}

/**
* Counts the amount of calls issued for specified declarator 
*
* @param declarator_p - a declarator to count for
* @return an amount of calls issued
*/
_UU32 Stat_CountCalls(const char *declarator_p)
{
  _StatMockBasicEntry_t *entry_p = (void*)Stat_mocks.buffer;
  _UU32 count = 0;

  while (STAT_IS_MOCK_ITERATION_VALID(entry_p))
  {
    if (Stat_AreStringsEqual(entry_p->declarator_p, declarator_p))
    {
      if ((entry_p->metadata.callOrder) && !entry_p->metadata.isExtended)
      {
        count++;
      }
      else if (Stat_IsMockOverridden(entry_p))
      {
        count += Stat_CountOverriddenCalls(entry_p);
      }
      else if (entry_p->metadata.isExtended)
      {
        count += Stat_CountExtendedMockEntryCalls(entry_p);
      }
    }
    entry_p = Stat_GetNextMockEntry(entry_p);
  }
  
  return count;
}

/**
* Counts for specified declarator the amount of entries including those 
* with Mock and without Mock (e.g. Mocks and Spies)
*
* @param declarator_p - a declarator to count for
* @return an amount of such entries
*/
_UU32 Stat_CountCallables(const char *declarator_p)
{
  _StatMockBasicEntry_t *entry_p = (void*)Stat_mocks.buffer;
  _UU32 count = 0;

  while (STAT_IS_MOCK_ITERATION_VALID(entry_p))
  {
    if (Stat_AreStringsEqual(entry_p->declarator_p, declarator_p))
    {
      if (Stat_HasExtendedMockMetadata(entry_p))
      {
        count += Stat_CountExtendedMockExpectedUses(entry_p);
      }
      else
      {
        count++;
      }
    }
    entry_p = Stat_GetNextMockEntry(entry_p);
  }
  
  return count;
}

/**
* Checks for specified declarator whether it has any Mock objects
*
* @param declarator_p - a declarator to check for
* @return a pointer to the first such Mock entry; NULL - otherwise
*/
void* Stat_FindMock(const char *declarator_p)
{
  _StatMockBasicEntry_t *entry_p = (void*)Stat_mocks.buffer;

  while (STAT_IS_MOCK_ITERATION_VALID(entry_p))
  {
    if (Stat_AreStringsEqual(entry_p->declarator_p, declarator_p) && !Stat_IsPureSpy(entry_p))
    {
      return entry_p;
    }
    entry_p = Stat_GetNextMockEntry(entry_p);
  }
  
  return NULL;
}

/**
* Checks for specified declarator whether it has any Mock objects
*
* @param declarator_p - a declarator to check for
* @return a pointer to the first such Mock entry; NULL - otherwise
*/
void* Stat_FindUnconsumedMock(const char *declarator_p)
{
  _StatMockBasicEntry_t *entry_p = (void*)Stat_mocks.buffer;

  while (STAT_IS_MOCK_ITERATION_VALID(entry_p))
  {
    if (!(entry_p->metadata.callOrder) && Stat_AreStringsEqual(entry_p->declarator_p, declarator_p))
    {
      return entry_p;
    }
    else if (Stat_mocks.doCallOrderTracking)
    {
      STAT_MOCK_ASSERT(entry_p->metadata.callOrder, "Consumed mock out of order for ", entry_p->declarator_p);
    }
    entry_p = Stat_GetNextMockEntry(entry_p);
  }

  return NULL;
}

void* Stat_GetMockHandle(const char *declarator_p, _UU32 creationIndex)
{
  _StatMockBasicEntry_t *entry_p = (void*)Stat_mocks.buffer;
  _UU32 countDown = creationIndex;
  _UU32 callCount;

  while (STAT_IS_MOCK_ITERATION_VALID(entry_p))
  {
    if (Stat_AreStringsEqual(entry_p->declarator_p, declarator_p))
    {
      if (Stat_HasExtendedMockMetadata(entry_p))
      {
        callCount = Stat_CountExtendedMockEntryCalls(entry_p);
        if (callCount > countDown)
        {
          return entry_p;
        }
        countDown -= callCount;
      }
      else if (0 == countDown--)
      {
        return entry_p;
      }
    }
    entry_p = Stat_GetNextMockEntry(entry_p);
  }
  
  return NULL;
}

void* Stat_FindAnyUnconsumedMockEntry(void)
{
  _StatMockBasicEntry_t *entry_p = (void*)Stat_mocks.buffer;

  while (STAT_IS_MOCK_ITERATION_VALID(entry_p))
  {
    if ((!entry_p->metadata.callOrder) && (!Stat_IsMockOverridden(entry_p)))
    {
      return entry_p;
    }
    entry_p = Stat_GetNextMockEntry(entry_p);
  }
  
  return NULL;
}

_UU32 Stat_GetMockFreeSpace(void)
{
  return (Stat_mocks.lastCallDataOffset - Stat_mocks.mockOffsetToAllocate);
}

_UU32 Stat_CountAllCalls(void)
{
  return Stat_mocks.callCount;
}

static void* Stat_AllocateMockEntry(const char *declarator_p, _UU32 size, _UU32 isExtended, STAT_MOCK_CALLBACK_T callback)
{
  void *container_p;
  if (callback)
  {
    container_p = Stat_AllocateMockEntryWithCallback(declarator_p, size, isExtended, callback);
  }
  else
  {
    container_p = Stat_AllocateMockEntryWithoutCallback(declarator_p, size, isExtended);
  }
  return container_p;
}

static void* Stat_AllocateMockEntryWithoutCallback(const char *declarator_p, _UU32 size, _UU32 isExtended)
{
  _StatMockBasicEntry_t *entry_p = Stat_AllocateEntry(declarator_p, size, isExtended, 0); 
  return (entry_p + 1);
}

static void* Stat_AllocateMockEntryWithCallback(const char *declarator_p, _UU32 size, _UU32 isExtended, STAT_MOCK_CALLBACK_T callback)
{
  _StatMockBasicEntry_t *entry_p = Stat_AllocateEntry(declarator_p, sizeof(callback) + size, isExtended, !0);
  STAT_MOCK_CALLBACK_T *callback_p = (void*)(entry_p + 1);
  *callback_p = callback;
  return (callback_p + 1);
}

static _StatMockBasicEntry_t* Stat_AllocateEntry(const char *declarator_p, _UU32 size, _UU32 isExtended, _UU32 hasCallback)
{
  const _StatMockBasicMetadata_t zeroMetadata = {0};
  _StatMockBasicEntry_t *entry_p;
  _UU32 sizeToAlloc = sizeof(_StatMockBasicEntry_t) + STAT_MOCK_ALIGN_SIZE(size);

  entry_p = (void*)&Stat_mocks.buffer[Stat_mocks.mockOffsetToAllocate];
  Stat_mocks.mockOffsetToAllocate += sizeToAlloc;
  STAT_MOCK_ASSERT(STAT_MOCK_ALIGN_SIZE(sizeToAlloc) == sizeToAlloc, "Mock size got not alligned for ", declarator_p);
  STAT_MOCK_ASSERT(Stat_mocks.mockOffsetToAllocate <= Stat_mocks.lastCallDataOffset, 
    "Not enough space to add a new entry for ", declarator_p);
  entry_p->declarator_p = declarator_p;
  entry_p->metadata = zeroMetadata;
  entry_p->metadata.nextOffset = _STAT_MOCK_BYTES_2_ENTRY_OFFSET(Stat_mocks.mockOffsetToAllocate);
  entry_p->metadata.isExtended = isExtended;
  entry_p->metadata.hasCallback = hasCallback;
  return entry_p;
}

static _UU32 Stat_HasExtendedMockMetadata(const _StatMockBasicEntry_t *entry_p)
{
  return (entry_p->metadata.isExtended) && !Stat_IsThisExtendedEntryPrimitive(entry_p);
}

static _UU32 Stat_IsThisExtendedEntryPrimitive(const _StatMockBasicEntry_t *entry_p)
{
  STAT_MOCK_HANDLER_T *handler_p = (void*)(entry_p + 1);
  void *extendedData_p = (entry_p->metadata.hasCallback) ? (handler_p + 1): handler_p;
  return (extendedData_p == Stat_GetNextMockEntry(entry_p));
}

static _UU32 Stat_IsPureSpy(const _StatMockBasicEntry_t *entry_p)
{
  return (entry_p->metadata.isExtended) && ((entry_p + 1) == Stat_GetNextMockEntry(entry_p));
}

static _UU32 Stat_IsMockOverridden(const _StatMockBasicEntry_t *entry_p)
{
  STAT_MOCK_HANDLER_T *handler_p = (void*)(entry_p + 1);
  return (entry_p->metadata.isExtended) && (entry_p->metadata.hasCallback) && 
    ((void*)(handler_p + 1) == (void*)Stat_GetNextMockEntry(entry_p));
}

static _StatMockBasicEntry_t* Stat_PopNextMockEntry(const char *declarator_p)
{
  _StatMockBasicEntry_t *entry_p = Stat_FindUnconsumedMock(declarator_p);
  STAT_MOCK_ASSERT(entry_p, "No more mocks to pop for ", declarator_p);
  return entry_p;
}

static void* Stat_CallOverridingHandler(_StatMockBasicEntry_t *entry_p, const void* dataToSpy_p)
{
  STAT_MOCK_HANDLER_T *handler_p = (void*)(entry_p + 1);
  _UU32 *count_p = Stat_ExtractCollectedCallData(entry_p);
  if (!count_p)
  {
    count_p = Stat_AllocateBufferForCallDataOfEntry(entry_p, sizeof(*count_p));
    *count_p = 0;
  }
  (*count_p)++;
  return (*handler_p)(++Stat_mocks.callCount, *count_p, dataToSpy_p);
}

static void Stat_CollectCallData(_StatMockBasicEntry_t *entry_p, const void* dataToSpy_p, _UU32 dataSize)
{
  _UU8* data_p;
  _UU32 extraStatsSize = Stat_AdjustCallStatsAndCalcExtraStatsSize(entry_p);
  _UU32 totalSize = dataSize + extraStatsSize;
  if (totalSize)
  {
    data_p = Stat_AllocateBufferForCallDataOfEntry(entry_p, totalSize);
    if (extraStatsSize)
    {
      Stat_AdjustCallExtraStats(data_p, (0 != dataSize));
      data_p += extraStatsSize;
    }
    if (dataSize)      
    {
      Stat_Memcpy(data_p, dataToSpy_p, dataSize);
    }
  }
}

static void Stat_CollectExtendedMockCallData(_StatMockBasicEntry_t *entry_p, const void* dataToSpy_p, _UU32 dataSize)
{
  _UU32 callDataSize = sizeof(_StatCallExtendedMetadata_t) + dataSize;
  _StatCallExtendedMetadata_t *callMetadata_p = Stat_ExtractCollectedCallData(entry_p);

  if (!callMetadata_p)
  {
    callMetadata_p = Stat_AllocateBufferForCallDataOfEntry(entry_p, callDataSize);
    callMetadata_p->size = dataSize;
  }
  STAT_MOCK_ASSERT(callMetadata_p->size >= dataSize,
    "Inconsitent data-size of Spy-Data got for ", entry_p->declarator_p);

  callMetadata_p->callOrder = ++Stat_mocks.callCount;
  callMetadata_p->hasSpyData = (dataSize != 0);
  
  if (dataSize)
  {
    Stat_Memcpy(callMetadata_p + 1, dataToSpy_p, dataSize);
  }
}

static void* Stat_ExtractMockFromEntry(_StatMockBasicEntry_t *entry_p)
{
  void* mock_p;
  if (entry_p->metadata.hasCallback)
  {
    mock_p = Stat_ExtractMockFromEntryWithCallback(entry_p);
  }
  else
  {
    mock_p = Stat_ExtractMockFromEntryWithoutCallback(entry_p);
  }
  return mock_p;
}

static void* Stat_ExtractMockFromEntryWithCallback(_StatMockBasicEntry_t *entry_p)
{
  STAT_MOCK_CALLBACK_T *callback_p;
  void* mock_p;
  
  callback_p = (void*)(entry_p + 1);
  mock_p = Stat_EvaluateMock((callback_p + 1), entry_p);
  (*callback_p)(Stat_mocks.callCount, mock_p, Stat_ExtractSpyData(entry_p));
  return mock_p;
}

static void* Stat_ExtractMockFromEntryWithoutCallback(_StatMockBasicEntry_t *entry_p)
{
  return Stat_EvaluateMock((entry_p + 1), entry_p);
}

static void* Stat_PopExtendedMock(_StatMockBasicEntry_t *entry_p, const void* dataToSpy_p, _UU32 dataSize)
{
  Stat_CollectExtendedMockCallData(entry_p, dataToSpy_p, dataSize);
  return Stat_ConsumeExtendedMock(entry_p);
}

static void* Stat_ConsumeExtendedMock(_StatMockBasicEntry_t *entry_p)
{
  STAT_MOCK_CALLBACK_T *callback_p = (void*)(entry_p + 1);
  _StatMockExtendedMetadata_t *extended_p = (void*)(entry_p->metadata.hasCallback? (callback_p + 1): callback_p);
  _StatReusableMockMetadata_t *reusable_p = (void*)extended_p;
  void *mock_p;
  
  reusable_p->usedCount++;
  if ((STAT_EXTENDED_MOCK_REUSABLE == extended_p->extendedType) && (reusable_p->usedCount == reusable_p->countToUse))
  {
    entry_p->metadata.callOrder = STAT_MOCK_CALL_ORDER_NATURAL_MAX;
  }

  mock_p = Stat_EvaluateMock(reusable_p + 1, entry_p);
  if (entry_p->metadata.hasCallback)
  {
    (*callback_p)(Stat_mocks.callCount, mock_p, Stat_ExtractSpyData(entry_p));
  }
  return mock_p;
}

static void* Stat_EvaluateMock(void* estimatedMock_p, const _StatMockBasicEntry_t *entry_p)
{
  return (estimatedMock_p < (void*)Stat_GetNextMockEntry(entry_p))? estimatedMock_p: NULL;
}

static void Stat_FailMockModule(const char *message_p, const char *declarator_p)
{
  char *output_p = (void*)Stat_mocks.buffer;
  char *end_p = (void*)(Stat_mocks.buffer + STAT_MOCK_ALIGNED_SIZE - 1);

  output_p = Stat_CopyStringToBuffer(output_p, end_p, message_p);
  output_p = Stat_CopyStringToBuffer(output_p, end_p, declarator_p);
  *output_p = 0;
  STAT_MOCK_FAIL((void*)Stat_mocks.buffer);
}

static char* Stat_CopyStringToBuffer(char* buffer_p, const char *end_p, const char *string_p)
{
  const char *source_p = string_p;
  char *next_p = buffer_p;
  while (source_p && *source_p && (next_p < end_p))
  {
    *next_p++ = *source_p++;
  }
  return next_p;
}

static _UU32 Stat_AdjustCallStatsAndCalcExtraStatsSize(_StatMockBasicEntry_t *entry_p)
{
  Stat_mocks.callCount++;
  
#if (STAT_MOCK_METADATA_CALL_ORDER < STAT_MOCK_CALL_EXTENDED_CALL_ORDER)
  if (Stat_mocks.callCount >= STAT_MOCK_CALL_ORDER_NATURAL_MAX)
  {
    entry_p->metadata.callOrder = STAT_MOCK_CALL_ORDER_NATURAL_MAX;
    return sizeof(_StatCallExtendedMetadata_t);
  }
#endif

  entry_p->metadata.callOrder = Stat_mocks.callCount;
  return 0;
}

static void* Stat_AllocateBufferForCallDataOfEntry(_StatMockBasicEntry_t *entry_p, _UU32 size)
{
  Stat_mocks.lastCallDataOffset -= STAT_MOCK_ALIGN_SIZE(size);
  STAT_MOCK_ASSERT(Stat_mocks.mockOffsetToAllocate <= Stat_mocks.lastCallDataOffset, 
    "Not enough space to add a new Call-Data (e.g. spy-data) for ", entry_p->declarator_p);
  entry_p->metadata.callDataOffset = _STAT_MOCK_BYTES_2_ENTRY_OFFSET(Stat_mocks.lastCallDataOffset);
  return &Stat_mocks.buffer[Stat_mocks.lastCallDataOffset];
}

static void Stat_AdjustCallExtraStats(void *buffer_p, _UU32 hasSpyData)
{
  _StatCallExtendedMetadata_t* data_p = buffer_p;
  data_p->callOrder = Stat_mocks.callCount;
  data_p->hasSpyData = hasSpyData;
}

static void* Stat_ExtractSpyData(const _StatMockBasicEntry_t *entry_p)
{
  _StatCallExtendedMetadata_t* callData_p = Stat_ExtractCollectedCallData(entry_p);
  if (Stat_HasCallDataNoExtendedMetadata(entry_p))
  {
    return (entry_p->metadata.callOrder)? callData_p: NULL;
  }
  else
  {
    return (callData_p->hasSpyData)? ++callData_p: NULL;
  }
}

static _UU32 Stat_ExtractCallOrder(const _StatMockBasicEntry_t *entry_p)
{
  _StatCallExtendedMetadata_t* callData_p;  
  if (Stat_HasCallDataNoExtendedMetadata(entry_p))
  {
    return entry_p->metadata.callOrder;
  }
  else
  {
    callData_p =  Stat_ExtractCollectedCallData(entry_p);
    return callData_p->callOrder;
  }
}

static _StatMockBasicEntry_t* Stat_GetNextMockEntry(const _StatMockBasicEntry_t *entry_p)
{
  return (void*)&Stat_mocks.buffer[_STAT_MOCK_ENTRY_OFFSET_2_BYTES(entry_p->metadata.nextOffset)];
}

static void* Stat_ExtractCollectedCallData(const _StatMockBasicEntry_t *entry_p)
{
  _UU32 callDataOffset = entry_p->metadata.callDataOffset;
  return (callDataOffset)? &Stat_mocks.buffer[_STAT_MOCK_ENTRY_OFFSET_2_BYTES(callDataOffset)]: NULL;
}

static _UU32 Stat_CountOverriddenCalls(const _StatMockBasicEntry_t *entry_p)
{
  _UU32 *count_p = Stat_ExtractCollectedCallData(entry_p);
  return (count_p)? *count_p: 0;
}

static _UU32 Stat_CountExtendedMockEntryCalls(const _StatMockBasicEntry_t *entry_p)
{
  STAT_MOCK_CALLBACK_T *handler_p = (void*)(entry_p + 1);
  _StatMockExtendedMetadata_t *extended_p = (void*)(entry_p->metadata.hasCallback? (handler_p + 1): handler_p);
  _StatReusableMockMetadata_t *reusable_p = (void*)extended_p;
  return reusable_p->usedCount;
}

static _UU32 Stat_CountExtendedMockExpectedUses(const _StatMockBasicEntry_t *entry_p)
{
  STAT_MOCK_CALLBACK_T *handler_p = (void*)(entry_p + 1);
  _StatMockExtendedMetadata_t *extended_p = (void*)(entry_p->metadata.hasCallback? (handler_p + 1): handler_p);
  _StatReusableMockMetadata_t *reusable_p = (void*)extended_p;
  return reusable_p->countToUse;
}

static _UU32 Stat_HasCallDataNoExtendedMetadata(const _StatMockBasicEntry_t *entry_p)
{
  return (STAT_MOCK_CALL_ORDER_NATURAL_MAX > entry_p->metadata.callOrder) && !Stat_HasExtendedMockMetadata(entry_p);
}

#endif
/******************************************************************************/
/*     END OF FILE                                                            */
/******************************************************************************/


