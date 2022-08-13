#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include <time.h>

#include "postgres.h"
#include "fmgr.h"
#include "utils/geo_decls.h"

#ifdef PG_MODULE_MAGIC
PG_MODULE_MAGIC;
#endif
/**
* 为了确保不会错误加载共享库文件，
* 从PostgreSQL 开始将检查那个文件的"magic block"，
* 这允许服务器以检查明显的不兼容性
**/

static char alphabet[65]=
                {0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,
                0x61,0x62,0x63,0x64,0x65,0x66,0x67,0x68,0x69,0x6A,
                0x6B,0x6C,0x6D,0x6E,0x6F,0x70,0x71,0x72,0x73,0x74,
                0x75,0x76,0x77,0x78,0x79,0x7A,0x41,0x42,0x43,0x44,
                0x45,0x46,0x47,0x48,0x49,0x4A,0x4B,0x4C,0x4D,0x4E,
                0x4F,0x50,0x2A,0x23,0x28,0x29,0x26,0x5E,0x25,0x24,
                0x2B,0x40,0x21,0x7E,0x3D};
static char char2code[256] =   
                {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x3E,0x00,0x35,0x3B,0x3A,0x38,0x00,
                0x36,0x37,0x34,0x3C,0x00,0x00,0x00,0x00,0x00,0x01,
                0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x00,0x00,
                0x00,0x00,0x00,0x00,0x3D,0x24,0x25,0x26,0x27,0x28,
                0x29,0x2A,0x2B,0x2C,0x2D,0x2E,0x2F,0x30,0x31,0x32,
                0x33,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x39,0x00,0x00,0x0A,0x0B,0x0C,
                0x0D,0x0E,0x0F,0x10,0x11,0x12,0x13,0x14,0x15,0x16,
                0x17,0x18,0x19,0x1A,0x1B,0x1C,0x1D,0x1E,0x1F,0x20,
                0x21,0x22,0x23,0x00,0x00,0x00,0x3F,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00};

//encode 1-3 bytes to 4 bytes
static char*  base64Encode(char* data, int len) 
{
        char byte1 = 0, byte2 = 0, byte3 = 0;
        char* retchar = NULL;

        char retByte1, retByte2, retByte3, retByte4;
        int length = len;

        if (length >= 1) 
        {
                byte1 = data[0];
        }
        if (length >= 2) 
        {
                byte2 = data[1];
        }
        if (length >= 3) 
        {
                byte3 = data[2];
        }


        retByte1 = (char)(((byte1 & 0xFC) >> 2) & 0x3F);
        retByte2 = (char)( ((byte1 & 0x3) << 4) | (((byte2 & 0xF0 ) >> 4)));
        retByte3 = (char)( ((byte2 & 0xF) <<2) | (((byte3 & 0xC0) >> 6) & 0x3F) );
        retByte4 = (char)( ((byte3 & 0x3F)));

        if (length == 1)
        {
                retByte3 = retByte4 = 64;
        }
        else if (length == 2)
        {
                retByte4 = 64;
        }

        retchar = malloc(4);
        memset(retchar,alphabet[retByte1],1);
        memset(retchar+1,alphabet[retByte2],1);
        memset(retchar+2,alphabet[retByte3],1);
        memset(retchar+3,alphabet[retByte4],1);

        return retchar;
}

//decode 4 to 1-3 byte
static char* base64Decode(char* data) 
{
        char byte1,byte2,byte3,byte4;
        char retByte1, retByte2, retByte3;
        byte1 = char2code[data[0]];
        byte2 = char2code[data[1]]; 
        byte3 = char2code[data[2]]; 
        byte4 = char2code[data[3]];

        retByte1 = (char)((byte1 & 0x3F) << 2 | ((byte2 & 0x30) >> 4) );
        retByte2 = (char)(((byte2 & 0x0F) << 4) | ((byte3 &0x3C)>> 2) );
        retByte3 = (char)(((byte3 & 0x3)<<6) | (byte4 & 0x3F));

        char* retchar = malloc(4);
        memset(retchar,0x00,4);

        if (data[2] == '=' && data[3] == '=') 
        {
                memset(retchar,retByte1,1);
        }
        else if (data[3] == '=') 
        {
                memset(retchar,retByte1,1);
                memset(retchar+1,retByte2,1);
        }
        else 
        {
                memset(retchar,retByte1,1);
                memset(retchar+1,retByte2,1);
                memset(retchar+2,retByte3,1);
        }
        return retchar;
}

static char* encrypt1Byte(char byte1) 
{
        char* retchar=malloc(1);
        memset(retchar,byte1^0x5B,1);
        return retchar;
}

static char* encrypt2Bytes(char byte1, char byte2) {
        char retByte1, retByte2;

        retByte1 = (char)(( (byte2 & 0xF) << 4 ) | (( byte1 & 0xF0) >> 4 ));
        retByte2 = (char)(((byte1 & 0xF) << 4) | ((byte2 & 0xF0)>>4));

        retByte1 ^= 0xBF;
        retByte2 ^= 0x5A;

        char* retchar = malloc(2);
        memset(retchar,retByte1,1);
        memset(retchar+1,retByte2,1);

        return retchar;
}

static char* encrypt3Bytes(char byte1, char byte2, char byte3) 
{
        char retByte1 = (char) ((((byte2 & 0xF) << 4)) | ((byte1 & 0x80)>>4) | ((byte3 & 0x7)));
        char retByte2 = (char) (((byte1 & 0x7) << 5) | ((byte3 & 0xE0) >> 3) | ((byte2 & 0x30) >> 4));
        char retByte3 = (char) (((byte3 & 0x18) << 3) | ((byte2 & 0xC0) >> 2) | ((byte1 & 0x78) >> 3));


        retByte1 ^= 0xBC;
        retByte2 ^= 0x5F;
        retByte3 ^= 0x64;

        char* retchar = malloc(3);
        memset(retchar,retByte1,1);
        memset(retchar+1,retByte2,1);
        memset(retchar+2,retByte3,1);

        return retchar;
}

static char* encodeBytes(char* rawData, int len) {
        int i;
        int totalLength = len;
        int totalGroup = totalLength / 3;

        if (totalLength % 3 != 0) {
                totalGroup += 1;
        }

        char* retBytes = malloc(totalGroup * 4+1);
        memset(retBytes+totalGroup*4,0x00,1);

        for(i = 0; i < totalGroup; i++) {
                char* cryptData = NULL;
                int len=0;
                if (i < totalGroup - 1) {
                        cryptData = encrypt3Bytes(
                                rawData[i*3],
                                rawData[i*3 + 1],
                                rawData[i*3 + 2]
                        );
                        len=3;

                }
                else {
                        if (totalLength % 3 == 1) {
                                cryptData = encrypt1Byte(rawData[i*3]);
                                len=1;
                        }
                        else if (totalLength % 3 == 2) {
                                cryptData = encrypt2Bytes(rawData[i*3], rawData[i*3 + 1]);
                                len=2;
                        }
                        else {
                                cryptData = encrypt3Bytes(
                                                rawData[i*3],
                                                rawData[i*3 + 1],
                                                rawData[i*3 + 2]
                                        );
                                len=3;
                        }
                }

                char* encodedData = base64Encode(cryptData,len);
                int j;
                for (j = 0; j < 4; j++) {
                        retBytes[i * 4 + j] = encodedData[j];
                }
                free(cryptData);
                free(encodedData);
        }

        return retBytes;
}

static char* decrypt1Byte(char byte1) 
{
        char* retchar=malloc(1);
        memset(retchar,byte1 ^ 0x5B,1);
        return retchar;
}

static char* decrypt2Bytes(char byte1, char byte2) 
{
        char retByte1, retByte2;
        byte1 ^= 0xBF;
        byte2 ^= 0x5A;

        retByte1 = (char)(( (byte1 & 0xF) << 4 ) | (( byte2 & 0xF0) >> 4 ));
        retByte2 = (char)(((byte2 & 0xF) << 4) | ((byte1 & 0xF0)>>4));

        char* retchar=malloc(2);
        memset(retchar,retByte1,1);
        memset(retchar+1,retByte2,1);
        return retchar;
}

static char* decrypt3Bytes(char byte1, char byte2, char byte3) 
{
        char retByte1, retByte2, retByte3;

        byte1 = (char)(byte1 ^ 0xBC);
        byte2 = (char)(byte2 ^ 0x5F);
        byte3 = (char)(byte3 ^ 0x64);


        retByte1 = (char)((( byte1 & 0x8 ) << 4) | ((byte3 & 0xF) << 3) | ((byte2 & 0xE0) >> 5));
        retByte2 = (char)(((byte3 & 0x30) << 2) | ((byte2 & 0x3) << 4) | ((byte1 & 0xF0) >> 4));
        retByte3 = (char)(((byte2 & 0x1C) << 3) | ((byte3 & 0xC0) >> 3) | ((byte1 & 0x07)));

        char* retchar=malloc(3);
        memset(retchar,retByte1,1);
        memset(retchar+1,retByte2,1);
        memset(retchar+2,retByte3,1);
        return retchar;
}

static char* decrypt123Byte(char* a, int len) 
{
        char* ret=malloc(4);
        memset(ret,0x00,4);
        if (len == 3) {
                char* temp = decrypt3Bytes(a[0], a[1], a[2]);
                memcpy(ret,temp,3);
                free(temp);
        }
        else if(len == 2) {
                char* temp = decrypt2Bytes(a[0], a[1]);
                memcpy(ret,temp,2);
                free(temp);
        }
        else if (len == 1) {
                char* temp = decrypt1Byte(a[0]);
                memcpy(ret,temp,1);
                free(temp);
        }
        return ret;
}

static char* decodeBytes(char* a, int len) 
{
                if (a == NULL||len==0||len % 4 != 0) {
                        return NULL;
                }

                int i = 0;
                int totalGroup = len / 4;

                char* crypt=malloc(4);
                memcpy(crypt,a+(totalGroup-1)*4,4);

                char* bytes = base64Decode(crypt);


                char* retBytes = malloc((totalGroup - 1) * 3 + strlen(bytes) +1);
                memset(retBytes+(totalGroup - 1) * 3 + strlen(bytes),0x00,1);

                char* dec = decrypt123Byte(bytes, strlen(bytes));

                for (i = 0; i < strlen(dec); i++) {
                        retBytes[(totalGroup - 1) * 3 + i] = dec[i];
                }

                free(dec);
                free(bytes);


                for (i = 0; i < totalGroup - 1; i++) {
                        memcpy(crypt,a+i*4,4);
                        bytes = base64Decode (crypt);

                        //assert(strlen(bytes) == 3);

                        dec = decrypt123Byte(bytes, 3);

                        int j=0;
                        for (j = 0; j < strlen(dec); j++) {
                                retBytes[i * 3 + j] = dec[j];
                        }
                        free(dec);
                        free(bytes);
                }

                free(crypt);
                return retBytes;
}

static bool strEndsWith(char* src, int srcLen, char *suffix, int suffixLen) {
                if (src == NULL || suffix == NULL) {
       return (src == NULL && suffix == NULL);
    }
    
    if (suffixLen > srcLen) {
        return false;
    }
    int strOffset = srcLen - suffixLen;
    
                int i = 0;
                for (i = 0; i < suffixLen; i++) {
                         if (src[strOffset + i] == suffix[i]) {
                                        continue;
                         }
                         return false;
                }

                return true;
}

static text* createEmptyText() {
                text *new_t = (text *) palloc(VARHDRSZ);
                SET_VARSIZE(new_t, VARHDRSZ);
                return new_t;
}

//  for postgre so
// 宏调用  这两个必须同时出现
PG_FUNCTION_INFO_V1(encode);
/**
 * @调用约定使用宏消除大多数传递参数和结果的复杂性
 * 
 * 每个实际参数都是用一个对应该参数的数据类型的PG_GETARG_xxx()宏抓取的
 * 用返回类型的PG_RETURN_xxx()宏返回结果
 * @return Datum 
 */
Datum encode(PG_FUNCTION_ARGS)
{
        text  *t = PG_GETARG_TEXT_P(0); //出现在src/include/fmgr.h中的文件
        text  *k = PG_GETARG_TEXT_P(1); //每个实际参数都是用一个对应该参数的数据类型的 PG_GETARG_xxx()宏抓取的
        char* tTemp = (char*)(VARDATA(t)); //获得t中的字符
  int tLen = VARSIZE(t) - VARHDRSZ; //分配空间是需要有VARHDRSZ，VARHDRSZ字节说明字符串的长度
  char* key = (char*)(VARDATA(k));
        int keyLen = VARSIZE(k) - VARHDRSZ;
  if (tTemp == NULL || tLen == 0 || key == NULL || keyLen == 0) { //如果为空或为0，执行函数
                        return createEmptyText();
        }

  int totalLenth = tLen + keyLen;
  char* data = malloc(totalLenth + 1);  //分配这么大小的空间 
        memset(data, 0x00,  totalLenth + 1); // 复制0x00到data的前totalLenth+1字节前
        memcpy(data, tTemp, tLen); // 复制tTemp的前tLen字节到data中
        memcpy(data + tLen, key, keyLen);
        char* p = encodeBytes(data, totalLenth);
        free(data);

        int pLen = strlen(p);
        text* new_t = (text*) palloc(pLen + 1 + VARHDRSZ);
        SET_VARSIZE(new_t, pLen + 1 + VARHDRSZ);
        memcpy((void*) VARDATA(new_t), (void*)p, pLen);
        memset((void*) VARDATA(new_t) + pLen, '=', 1);
        free(p);
        return new_t;
}

PG_FUNCTION_INFO_V1(decode);
Datum decode(PG_FUNCTION_ARGS)
{
  text  *t = PG_GETARG_TEXT_P(0);
  text  *k = PG_GETARG_TEXT_P(1);  
  char* tTemp = (char*)(VARDATA(t));
  int tLen = VARSIZE(t) - VARHDRSZ;
  char* key = (char*)(VARDATA(k));
        int keyLen = VARSIZE(k) - VARHDRSZ;
  if (tTemp == NULL || tLen == 0 || key == NULL || keyLen == 0) {
                        return createEmptyText();
        }
  
        char *p = decodeBytes(tTemp, tLen - 1);
  if (p == NULL) {
      return createEmptyText();
  }
  
  int pLen = strlen(p);
  if (!strEndsWith(p, pLen, key, keyLen)) {
          free(p);
          return createEmptyText();
  }
  
        text *new_t = (text *) palloc(pLen - keyLen + VARHDRSZ);
        SET_VARSIZE(new_t, pLen - keyLen + VARHDRSZ);
        memcpy((void *) VARDATA(new_t), (void*)p, pLen - keyLen);
        free(p);
        return new_t;
}

