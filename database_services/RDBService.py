import pymysql
import json
import logging

import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RDBService:

    def __init__(self):
        pass

    @classmethod
    def _get_db_connection(cls):

        db_connect_info = context.get_db_info()

        logger.info("RDBService._get_db_connection:")
        logger.info("\t HOST = " + db_connect_info['host'])

        db_info = context.get_db_info()

        db_connection = pymysql.connect(
           **db_info,
            autocommit=True
        )
        return db_connection

    @classmethod
    def run_sql(cls, sql_statement, args, fetch=False):

        conn = RDBService._get_db_connection()

        try:
            cur = conn.cursor()
            res = cur.execute(sql_statement, args=args)
            if fetch:
                res = cur.fetchall()
        except Exception as e:
            conn.close()
            raise e

        return res

    @classmethod
    def get_by_prefix(cls, db_schema, table_name, column_name, value_prefix):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name + " where " + \
            column_name + " like " + "'" + value_prefix + "%'"
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def _get_where_clause_args(cls, template):

        terms = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k,v in template.items():
                terms.append(k + "=%s")
                args.append(v)

            clause = " where " +  " AND ".join(terms)


        return clause, args

    @classmethod
    def find_by_type(cls, db_schema, table_name, template, limit, offset):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()
        sql = "select * from " + db_schema + "." + table_name +  " where " + \
            "type1 = '{0}' or type2 = '{0}' or type3 = '{0}' or type4 = '{0}' or type5 = '{0}'".format(template)\
                 + " " + "limit " + str(limit) + " " + "offset " + str(offset)
        print(sql)
        res = cur.execute(sql)
        res = cur.fetchall()
        conn.close()

        return res


    @classmethod
    def find_by_dev(cls, db_schema, table_name, template, limit, offset):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()
        sql = "select * from " + db_schema + "." + table_name + " where " + \
              "developer = '{0}'".format(template) + " " + "limit " + str(limit) \
                  + " " + "offset " + str(offset)
        print(sql)
        res = cur.execute(sql)
        res = cur.fetchall()
        conn.close()

        return res

    @classmethod
    def find_by_template(cls, db_schema, table_name, template, limit, offset):

        wc,args = RDBService._get_where_clause_args(template)

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name + " " + wc + " " + \
            "limit " + str(limit) + " " + "offset " + str(offset)
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def create(cls, db_schema, table_name, create_data):

        cols = []
        vals = []
        args = []

        for k,v in create_data.items():
            cols.append(k)
            vals.append('%s')
            args.append(v)

        cols_clause = "(" + ",".join(cols) + ")"
        vals_clause = "values (" + ",".join(vals) + ")"

        sql_stmt = "insert into " + db_schema + "." + table_name + " " + cols_clause + \
            " " + vals_clause

        res = RDBService.run_sql(sql_stmt, args)
        return res

    @classmethod
    def update(cls, db_schema, table_name, select_data, update_data):

        select_clause, select_args = RDBService._get_where_clause_args(select_data)

        cols = []
        args = []

        for k, v in update_data.items():
            cols.append(k + "=%s")
            args.append(v)
        clause = "set " + ", ".join(cols)
        args = args + select_args

        sql_stmt = "update " + db_schema + "." + table_name + " " + clause + \
                   " " + select_clause

        res = RDBService.run_sql(sql_stmt, args)
        return res

    @classmethod
    def delete(cls, db_schema, table_name, template):
        clause, args = RDBService._get_where_clause_args(template)
        sql_stmt = "delete from " + db_schema + "." + table_name + " " + clause
        res = RDBService.run_sql(sql_stmt, args)
        return res
