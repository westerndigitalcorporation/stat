/**
* @file
*
* @copyright Copyright (c) 2020 Western Digital Corporation or its affiliates,
*                          Arseniy Aharonov <arseniy@aharonov.icu>
*            SPDX-License-Identifier: MIT
* 
* @project   STAT Framework
* @date      July 31, 2016
* @brief     Declares internal prototypes of STAT
*******************************************************************************/
#ifndef _STAT_I
#define _STAT_I

/******************************************************************************/
/**    INCLUDE FILES                                                         **/
/******************************************************************************/
#include <unity.h>

/******************************************************************************/
/**    DEFINITIONS                                                           **/
/******************************************************************************/

/******************************************************************************/
/**    MACROS                                                                **/
/******************************************************************************/

#define STAT_ARRAY_LEN(_array_) (sizeof(_array_)/sizeof(*(_array_)))

#define STAT_CEILING_DIV(_value_, _alignment_) (((_value_) + (_alignment_) - 1) / (_alignment_))
#define STAT_CEILING_ROUND(_value_, _alignment_) (STAT_CEILING_DIV(_value_, _alignment_) * (_alignment_))

#define STAT_MIN(_x_, _y_) ((_x_) < (_y_)? (_x_): (_y_))

/******************************************************************************/
/**    TYPES                                                                 **/
/******************************************************************************/

/******************************************************************************/
/**    EXPORTED GLOBALS                                                      **/
/******************************************************************************/

/******************************************************************************/
/**    FUNCTION PROTOTYPES                                                   **/
/******************************************************************************/

/**
* Implements the user main routine that shall be implemented in every STAT 
* package
*
* @return status depicting success or failure returned by the Unity harness
*
* @remarks Shall be implemented in every STAT package
*/
_UU32 Stat_Main(void);

/**
* Initializes the RNG engine
*
* @return None
*/
void Stat_InitRng(void);

/**
* Product setup routine
*
* @return None
*/
void Stat_SetupProductTest(void);

/**
* Product tear-down routine
*
* @return None
*/
void Stat_TeardownProductTest(void);

// Standard mem-operations
void Stat_Memcpy(void *target_p, const void *source_p, _UU32 size);
void Stat_Memset(void *target_p, _UU32 value, _UU32 size);

// String operations
_UU32 Stat_AreStringsEqual(const char *first_p, const char *second_p);

#endif /* This is actually EOF */

