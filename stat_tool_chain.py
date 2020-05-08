class StatToolchain(object):

    def getCommandToCompile(self):
        raise NotImplementedError('Method "{0}" is not implemented'.format(self.getCommandToCompile.__name__))