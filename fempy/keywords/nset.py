import numpy as np

class Nset():

    """ Class to store the node set (NSET) keyword from an Abaqus .inp file into
    a format that is accessible to python scripting.
    """

    def __init__(self, parent, parsed, idkey, **kwargs):
        """
        Initialize the object, add node set data and parameters.
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
        """

        self.parent = parent
        self.data = []
        self._idkey = idkey
        self.params = dict(NSET = [])

        split_data = [list(filter(None,n.split(','))) for n in parsed[idkey].data]
        self.data = np.concatenate(split_data, axis=None).astype(int)
        for par in parsed[idkey].params:
            self.params[par.name.upper()] = par.value

    def dump2inp(self):
        '''
        Dumps Node Set instance to Abaqus INP format.

        :rtype: string

        out = self.nset[i].dump2inp()

        '''

        out = ''
        #out = '**----------------------------------\n** NODE SET\n**----------------------------------\n'
        nset = self.params['NSET']
        pattern = '*NSET, NSET={0}\n'
        out += pattern.format(nset)

        count = 0
        for node in self.data:
            out += ' {0},'.format(node)
            count +=1
            if count == 16:
                out = out.rstrip(',')
                out += '\n'
                count = 0

        if count != 16:
            out += '\n'

        return out

    def _return_id(self):
        '''
        Returns position of the last element processed with this class in the parsed inp list.

        :rtype: string
        '''

        return self._idkey

    def __repr__(self):
        print_dict = {}
        print_dict['params'] = self.params
        print_dict['data'] = type(self.data)
        return '<Fempy.Nset Class ' + str(print_dict) + '>'