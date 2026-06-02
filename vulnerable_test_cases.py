import os
import sqlite3

def sql_injection_vulnerability(user_id):
    # False Negative in ML Model (Case 1)
    # This should be caught by SonarQube as a SQL Injection vulnerability
    sql = 'SELECT * FROM orders WHERE user_id = ' + str(user_id)
    print(f"Executing: {sql}")
    # Placeholder for execution
    # conn.execute(sql)

def command_injection_vulnerability(dir_name):
    # False Negative in ML Model (Case 4)
    # Using os.popen with concatenation is dangerous
    os.popen('rm -rf ' + dir_name)

def path_traversal_vulnerability(file_name):
    # False Negative in ML Model (Case 5)
    # Direct concatenation in open()
    with open('/tmp/' + file_name, 'r') as f:
        return f.read()

def code_injection_vulnerability(user_input):
    # Correctly identified by ML Model (Case 2)
    # But SonarQube will also flag this immediately
    eval('print(' + user_input + ')')

if __name__ == "__main__":
    # Dummy calls for context
    sql_injection_vulnerability("123 OR 1=1")
    command_injection_vulnerability("; drop table orders;")
    path_traversal_vulnerability("../../etc/passwd")
    code_injection_vulnerability("__import__('os').system('ls')")
