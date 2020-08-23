import numpy as np
from pandas import DataFrame


class Node():
    """ Class to store the *NODE keyword from an Abaqus .inp file into a format that is accessible to python scripting.
    """

    def __init__(self, parent, parsed, idkey, nset_name = '', **kwargs):
        """
        Initialize the object and add node data.
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
        """

        self._parent = parent
        self.data = []
        self._idkey = idkey
        self.params = dict(NSET=nset_name)

        split_data = [n.split(',') for n in parsed[idkey].data]
        data = np.array(split_data)[:, 1:].astype(float)
        index = np.array(split_data)[:, 0].astype(int)
        columns = ['x', 'y', 'z'][0:data.shape[1]]
        self.data = DataFrame(data=data,
                              index=index,
                              columns=columns)
        self.data.index.name = 'Node'

        for par in parsed[idkey].params:
            self.params[par.name.upper()] = par.value

    def dump2inp(self):
        '''
        Dumps Nodes instance to Abaqus INP format.

        :rtype: string

        out = self.node[i].dump2inp()

        '''

        # out = '**----------------------------------\n** NODES\n**----------------------------------\n*NODE, NSET=ALLNODES\n'

        nSet = self.params['NSET']
        out = '*NODE'
        if nSet != '':
            out += ', NSET={0},'.format(nSet)
        out += '\n'

        out += self.data.to_csv(header=None, line_terminator = '\n', float_format='%.6e').replace(',',', ')

        return out

    def dump2vtk(self):
        '''
        Returns nodes in VTK format.

        :rtype: string for vtk file
        '''

        out_nodes = self.data.to_string(index=False, header=False, float_format='%1.3e')

        out = '<Points>\n'
        out += '<DataArray type="Float64" NumberOfComponents=" ' + \
               str(self.data.shape[1]) + '" format="ascii">\n'
        out += out_nodes
        out += '\n</DataArray>\n'
        out += '</Points>\n'

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
        return '<Fempy.Node Class ' + str(print_dict) + '>'