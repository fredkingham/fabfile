

class A(object):
    def __init__(self, something):
        self.something = something

class B(A):
    def __init__(self, something, or_rather):
        super(B, self).__init__(something)
        self.or_rather = or_rather

    def greeting(self):
        return "%s %s" % (self.something, self.or_rather)
