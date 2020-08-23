import numpy as np
from pandas import DataFrame


class Surface():
    """ Class to store the surface keyword from an Abaqus .inp file into a format that is accessible to python scripting.
    """

    def __init__(self, parent, parsed, idkey, **kwargs):
        """
        Initialize the object, add surface data and parameters.
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
        """

        self._parent = parent
        self.data = []
        self._idkey = idkey
        self.params = dict(TYPE=[], NAME=[])
        for par in parsed[idkey].params:
            self.params[par.name.upper()] = par.value

        split_data = [n.split(',') for n in parsed[idkey].data]
        surface_number = np.array(split_data)[:, 1]
        element = np.array(split_data)[:, 0].astype(int)
        d = {'element': element, 'surface_number': surface_number}
        self.data = DataFrame(d)

    def dump2inp(self):
        '''
        Dumps Surface instance to Abaqus INP format.

        :rtype: string

        out = self.surface[i].dump2inp()

        '''

        # out = '**----------------------------------\n** SURFACES\n**----------------------------------\n'
        surType = self.params['TYPE']
        surSet = self.params['NAME']
        out = ''
        out += '*SURFACE, TYPE={0}, NAME={1}\n'.format(surType, surSet)

        out += self.data.to_csv(sep=',', index=False, header=False, line_terminator='\n')

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
        print_dict['data'] = self.data
        return '<Fempy.Surface Class ' + str(print_dict) + '>'