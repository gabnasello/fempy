import numpy as np

class Density():

    """ Class to store the *DENSITY keyword from an Abaqus .inp file into a format that is accessible to python scripting.
    """

    def __init__(self, density_data = [],  **kwargs):
        """
        Initialize the Density object and add node data.
        Input:
            density_data:
                -float- density value
        """
        self.data = np.asarray(density_data).astype(float)

        if 'abaqus_input' in kwargs.keys():
            parent = kwargs['abaqus_input']['parent']
            idkey = kwargs['abaqus_input']['idkey']
            parsed = kwargs['abaqus_input']['parsed']
            self.load_inp(parent, parsed, idkey)

    def load_inp(self, parent, parsed, idkey):
        """
        Initialize the Density object and add node data.
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
        """
        self._parent = parent
        self._idkey = idkey
        self.data = np.array(parsed[idkey].data[0]).astype(float)

    def dump2inp(self):
        '''
        Returns parts in INP format suitable with abaqus input files.

        :rtype: string
        '''

        pattern = '*DENSITY\n{0}\n'
        out += pattern.format(self.data)

        return out

    def __repr__(self):
        print_dict = {}
        print_dict['data'] = self.data
        return '<FemPy.Density Class ' + str(print_dict) + '>'