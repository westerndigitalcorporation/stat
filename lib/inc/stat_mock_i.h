/**
* @file
* 
* @copyright Arseniy Aharonov
* 
* @project   STAT Framework
* @date      September 01, 2018
* @brief     Declares internal definitions, types and prototypes for STAT-Mock
*******************************************************************************/


#ifndef _STAT_MOCK_I
#define _STAT_MOCK_I
/******************************************************************************/
/*     INCLUDE FILES                                                          */
/******************************************************************************/
#include <unity.h>
#include "stat_mock.h"

/******************************************************************************/
/*     DEFINITIONS                                                            */
/******************************************************************************/
#undef D_CURRENT_FILE
#define D_CURRENT_FILE _STAT_MOCK_I_H

// Maximal natural alignment of structures supported by STAT_MOCK
#define STAT_MOCK_MAX_ALIGNMENT sizeof(_UU32)

#define STAT_MOCK_ALIGNED_SIZE ((STAT_MOCK / STAT_MOCK_MAX_ALIGNMENT) * STAT_MOCK_MAX_ALIGNMENT)

#define STAT_MOCK_BITFIELD_BOOL_SIZE  1

// Describes field-sizes of _StatMockBasicMetadata
#if STAT_MOCK > (4 << 11)
#define STAT_MOCK_METADATA_NEXT_OFFSET      15
#define STAT_MOCK_METADATA_CALL_DATA_OFFSET 15
#define STAT_MOCK_METADATA_CALL_ORDER       32
#define STAT_MOCK_CALL_ORDER_NATURAL_MAX    (_UU32)(-1)
#else
#define STAT_MOCK_METADATA_NEXT_OFFSET      11
#define STAT_MOCK_METADATA_CALL_DATA_OFFSET 11
#define STAT_MOCK_METADATA_CALL_ORDER       8
#define STAT_MOCK_CALL_ORDER_NATURAL_MAX    ((1 << STAT_MOCK_METADATA_CALL_ORDER) - 1)
#endif

#define STAT_MOCK_METADATA_CALL_DATA_SIZE   (32 - STAT_MOCK_CALL_EXTENDED_CALL_ORDER - STAT_MOCK_BITFIELD_BOOL_SIZE)
#if (STAT_MOCK_METADATA_CALL_DATA_SIZE < STAT_MOCK_METADATA_CALL_DATA_OFFSET)
#error "STAT-Mock Call-Data size shall be able to contain size not less that Call-Data offset"
#endif

// Describes field-size of Mocks types with extended meta-data
#define STAT_MOCK_METADATA_EXTENDED_TYPE    4

#define STAT_REUSABLE_MOCK_COUNTER          ((32 - STAT_MOCK_METADATA_EXTENDED_TYPE) >> 2)
#define STAT_REUSABLE_MOCK_COUNTER_MAX      ((1 << STAT_REUSABLE_MOCK_COUNTER) - 1)

#if (STAT_MOCK > (4 /*STAT_MOCK_MAX_ALIGNMENT*/ << STAT_MOCK_METADATA_NEXT_OFFSET)) || \
    (STAT_MOCK > (4 /*STAT_MOCK_MAX_ALIGNMENT*/ << STAT_MOCK_METADATA_CALL_DATA_OFFSET))
#error "STAT-Mock doesn't support RAM buffers of the specified size!"
#endif

// Describes field-size of _StatExtendedCallMetadata
#define STAT_MOCK_CALL_EXTENDED_CALL_ORDER  16
#define STAT_MOCK_CALL_EXTENDED_RFU \
  (32 - STAT_MOCK_CALL_EXTENDED_CALL_ORDER - STAT_MOCK_BITFIELD_BOOL_SIZE)

/******************************************************************************/
/*     MACROS                                                                 */
/******************************************************************************/

#define _STAT_MOCK_TEXT(_text_) " STAT-Mock: " _text_

#define _STAT_MOCK_ENTRY_OFFSET_2_BYTES(_offset_) \
  ((_offset_) * STAT_MOCK_MAX_ALIGNMENT)
  
#define _STAT_MOCK_BYTES_2_ENTRY_OFFSET(_byte_size_) \
  ((_byte_size_) / STAT_MOCK_MAX_ALIGNMENT)

/******************************************************************************/
/*     TYPES                                                                  */
/******************************************************************************/

typedef enum _STAT_EXTENDED_MOCK_TYPES
{
  STAT_EXTENDED_MOCK_REUSABLE,
  STAT_EXTENDED_MOCK_INFINITE,
}STAT_EXTENDED_MOCK_TYPES_T;

typedef struct _StatMockBasicMetadata
{
  _UU32 nextOffset      :STAT_MOCK_METADATA_NEXT_OFFSET;
  _UU32 isExtended      :STAT_MOCK_BITFIELD_BOOL_SIZE;
  _UU32 callDataOffset  :STAT_MOCK_METADATA_CALL_DATA_OFFSET;
  _UU32 hasCallback     :STAT_MOCK_BITFIELD_BOOL_SIZE;
  _UU32 callOrder       :STAT_MOCK_METADATA_CALL_ORDER;
}_StatMockBasicMetadata_t;

typedef struct _StatMockBasickEntry
{
  _StatMockBasicMetadata_t metadata;
  const char* declarator_p;
}_StatMockBasicEntry_t;

typedef struct _StatMockExtendedMetadata
{
  _UU32 extendedType  :STAT_MOCK_METADATA_EXTENDED_TYPE;
  _UU32 typeSpecific  :32 - STAT_MOCK_METADATA_EXTENDED_TYPE;
}_StatMockExtendedMetadata_t;

typedef struct _StatReusableMockMetadata
{
  _UU32 typePlaceholder :STAT_MOCK_METADATA_EXTENDED_TYPE;
  _UU32 countToUse      :STAT_REUSABLE_MOCK_COUNTER;
  _UU32 usedCount       :STAT_REUSABLE_MOCK_COUNTER;
}_StatReusableMockMetadata_t;

typedef struct _StatCallExtendedMetadata
{
  _UU32 callOrder    :STAT_MOCK_CALL_EXTENDED_CALL_ORDER;
  _UU32 hasSpyData   :STAT_MOCK_BITFIELD_BOOL_SIZE;
  _UU32 size         :STAT_MOCK_METADATA_CALL_DATA_SIZE;
}_StatCallExtendedMetadata_t;

typedef struct _StatMockControlBlock
{
  _UU32 mockOffsetToAllocate;
  _UU32 lastCallDataOffset;
  _UU32 callCount;
  _UU32 doCallOrderTracking;
  _UU8 buffer[STAT_MOCK_ALIGNED_SIZE];
}_StatMockControlBlock_t;

/******************************************************************************/
/*     EXPORTED GLOBALS                                                       */
/******************************************************************************/

/******************************************************************************/
/*     FUNCTION PROTOTYPES                                                    */
/******************************************************************************/

void* Stat_GetMockHandle(const char *declarator_p, _UU32 creationIndex);

void* Stat_FindAnyUnconsumedMockEntry(void);

_UU32 Stat_GetMockFreeSpace(void);

_UU32 Stat_CountAllCalls(void);

#endif /* This is actually EOF */


