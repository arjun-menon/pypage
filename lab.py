
import imp

cb = "def foo(n):\n\
    return n*n\n\
for i in range(1,4):\n\
    print foo(i)\n\
print locals()\n\
"

print "\n my locals:", locals()
print "\n my globals:", globals()

print "\n my __builtins__:", globals()['__builtins__']

nm = imp.new_module('hello')
print "\n\n new module's dict:", nm.__dict__

k = {'__name__': 'hello', '__builtins__': globals()['__builtins__'] }

exec cb in k

print "\n\n k after exec:", k
