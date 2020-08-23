import numpy as np

class Elastic():

    """ Class to store the **ELASTIC keyword from an Abaqus .inp file into a format that is accessible to python scripting.
    """

    def __init__(self, elastic_data = [], **kwargs):
        """
        Initialize the Elastic object
        Input:
            elastic_data:
                -list- [Young modulus, Poisson coefficient]
        """

        self.data = np.asarray(elastic_data).astype(float)

        if 'abaqus_input' in kwargs.keys():
            parent = kwargs['abaqus_input']['parent']
            idkey = kwargs['abaqus_input']['idkey']
            parsed = kwargs['abaqus_input']['parsed']
            self.load_inp(parent, parsed, idkey)

    def load_inp(self, parent, parsed, idkey):
        """
        Initialize the Elastic object and add node data.
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
        """
        self._parent = parent
        self._idkey = idkey
        split_data = parsed[idkey].data[0].split(',')
        self.data = np.array(split_data).astype(float)

    def dump2inp(self):
        '''
        Returns parts in INP format suitable with abaqus input files.

        :rtype: string
        '''

        pattern = '*ELASTIC\n{0}, {1}\n'
        out = pattern.format(self.data[0], self.data[1])

        return out

    def __repr__(self):
        print_dict = {}
        print_dict['data'] = self.data
        return '<FemPy.Elastic Class ' + str(print_dict) + '>'