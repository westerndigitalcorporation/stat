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
#ifndef _STAT_DEFS_H
#define _STAT_DEFS_H

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

/*************************/
/* Basic primitive types */
/*************************/

typedef UNITY_UINT8	 _UU8;
typedef UNITY_UINT16 _UU16;
typedef UNITY_UINT32 _UU32;
//typedef UNITY_UINT64 _UU64;
typedef UNITY_INT8	 _US8;
typedef UNITY_INT16	 _US16;
typedef UNITY_INT32	 _US32;
//typedef UNITY_INT64	 _US64;

/******************************************************************************/
/**    EXPORTED GLOBALS                                                      **/
/******************************************************************************/

/******************************************************************************/
/**    FUNCTION PROTOTYPES                                                   **/
/******************************************************************************/

#endif /* This is actually EOF */

