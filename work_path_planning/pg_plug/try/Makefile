EXTENSION = array_ext        # 扩展的名称
DATA = array_ext--0.0.1.sql  # 扩展安装的SQL文件
 
# 以下是 PostgreSQL 构建扩展相关的命令，保留就可以
PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)