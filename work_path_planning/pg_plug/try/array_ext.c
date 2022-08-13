#include "postgres.h"
#include "fmgr.h"
#include "utils/jsonb.h"
 
PG_MODULE_MAGIC;
 
JsonbValue *IteratorAppend(JsonbIterator **, Numeric, JsonbParseState **);
 
PG_FUNCTION_INFO_V1(array_ext_append);
 
Datum
array_ext_append(PG_FUNCTION_ARGS)
{
    Numeric     elm;
    Jsonb       *arr = NULL;
    JsonbValue  *res = NULL;
    JsonbIterator   *it;
    JsonbParseState *st = NULL;
 
    arr = PG_GETARG_JSONB(0);
    elm = PG_GETARG_NUMERIC(1);
 
    it = JsonbIteratorInit(&arr->root);
    res = IteratorAppend(&it, elm, &st);
 
    PG_RETURN_JSONB(JsonbValueToJsonb(res));
}
 
JsonbValue *
IteratorAppend(JsonbIterator **it, Numeric value, JsonbParseState  **state)
{
    uint32          r, rk;
    bool            t;
    JsonbValue      v, *res = NULL;
    t = true;
    r = rk = JsonbIteratorNext(it, &v, false);
    if (rk == WJB_BEGIN_ARRAY) {
        res = pushJsonbValue(state, r, NULL);
        for(;;) {
            r = JsonbIteratorNext(it, &v, true);
            if (r == WJB_END_OBJECT || r == WJB_END_ARRAY)
                break;
 
            if (strcmp(numeric_normalize(v.val.numeric), numeric_normalize(value)) == 0) {
                t = false;
            }
 
            pushJsonbValue(state, r, &v);
        }
 
        if (t) {
            v.type = jbvNumeric;
            v.val.numeric = value;
            pushJsonbValue(state, WJB_ELEM, &v);
        }
 
        res = pushJsonbValue(state, WJB_END_ARRAY, NULL);
    }
 
    return res;
}