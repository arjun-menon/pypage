
import imp, __builtin__, sys

# cb = "def foo(n):\n\
#     return n*n\n\
# for i in range(1,4):\n\
#     print foo(i)\n\
# print locals()\n\
# "

# print "\n my locals:", locals()
# print "\n my globals:", globals()

# print "\n my __builtins__:", globals()['__builtins__']

# nm = imp.new_module('hello')
# print "\n\n new module's dict:", nm.__dict__

# k = {'__name__': 'hello', '__builtins__': globals()['__builtins__'] }

# exec cb in k

# print "\n\n k after exec:", k

# env = dict()
# env['__builtins__'] = __builtin__
# env['__package__'] = None
# env['__name__'] = "hello"
# env['__doc__'] = None

# env['foo'] = 45

# exec "print foo" in env

# exec "x = 13" in env

# exec "print x" in env

# print "----------------"

class Exec(object):
    def __init__(self):
        self.env = dict()
        self.env['__builtins__'] = __builtin__
        self.env['__package__'] = None
        self.env['__name__'] = "hello"
        self.env['__doc__'] = None

        self.env['wr'] = self.write
        self.output = str()

    def write(self, text):
        self.output += text

    def run(self, code):
        if '\n' in code or ';' in code:
            self.output = str()
            exec code in self.env
            return self.output
        else:
            return eval(code, self.env)

e = Exec()

# print e.run("x = 5;")
# print e.run("x+2")
# print e.run("wr('yea')")

global_env = {'__builtins__': __builtin__}
local_env = dict()

#
# Module-level variables are stored locally.
#

# exec """
# x = 5
# """ in global_env, local_env

# print global_env
# print local_env

#
# They are inaccessible.
#

# exec """
# x = 5
# def foo():
#     print x
# foo()
# """ in global_env, local_env

'''
    Traceback (most recent call last):
      File "lab.py", line 94, in <module>
        """ in global_env, local_env
      File "<string>", line 5, in <module>
      File "<string>", line 4, in foo
    NameError: global name 'x' is not defined
'''

# exec """
# x = 5
# def foo():
#     print x
# foo()
# """ in global_env

'''
This works.
'''

exec """
x = 5
def foo():
    print x
print globals()
print locals()
""" in global_env, local_env

