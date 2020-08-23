import numpy as np

class Elset():

    """ Class to store the element set (ELSET) keyword from an Abaqus .inp file into
    a format that is accessible to python scripting.
    """

    def __init__(self, elset_data = [], elset_name = '', **kwargs):
        """
        Initialize the Elset object, add element set data and label.
        Input:
            elset_data:
                -list- of elements of the element set
            elset_name:
                -str- element set label
        """
        self.params = dict(elset=elset_name, generate=0)
        self.data = np.asarray(elset_data)

        if 'abaqus_input' in kwargs.keys():
            parent = kwargs['abaqus_input']['parent']
            idkey = kwargs['abaqus_input']['idkey']
            parsed = kwargs['abaqus_input']['parsed']
            self.load_inp(parent, parsed, idkey)

    def load_inp(self, parent, parsed, idkey):
        """
        Initialize the Elset object from abaqus inp data.
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
                        elset_data: list
            -list- of elements of the element set
        """
        self._parent = parent
        self._idkey = idkey

        split_data = [list(filter(None,n.split(','))) for n in parsed[idkey].data]
        self.data = np.concatenate(split_data, axis=None).astype(int)

        for par in parsed[idkey].params:
            self.params[par.name.lower()] = par.value

    def dump2inp(self):
        '''
        Dumps element set instance to Abaqus INP format.

        :rtype: string

        out = self.elset[i].dump2inp()

        '''

        # out = '**----------------------------------\n** ELEMENT SETS\n**----------------------------------\n'
        elset = self.params['elset']
        pattern = '*ELSET, ELSET={0}'
        #out += pattern.format(elset)
        out = pattern.format(elset)
        if self.params['generate'] == None:
            out += ', GENERATE'
        out += '\n'

        count = 0
        for node in self.data:
            out += ' {0},'.format(node)
            count +=1
            if count == 16:
                out = out.rstrip(',')
                out += '\n'
                count = 0

        if count != 0:
            out += '\n'

        return out

    def _return_id(self):
        '''
        Returns position of the last element processed with this class in the parsed inp list.

        :rtype: string
        '''

        return self._idkey

    def get_element_list(self):
        '''
        Returns element (ID) list of the elset.

        :rtype: list
        '''

        condition = (self.data.size == 3 and self.data[1] > self.data[2])

        if condition:
            start = self.data[0]
            end = self.data[1]
            step = self.data[2]
            elsetlist = np.arange(start, end + 1, step)
        else:
            elsetlist = self.data.tolist()

        return elsetlist