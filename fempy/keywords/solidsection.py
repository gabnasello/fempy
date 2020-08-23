class Solidsection():

    """ Class to store the SOLID SECTION keyword from an Abaqus .inp file into
    a format that is accessible to python scripting.
    """

    def __init__(self, elset = '', material = '', **kwargs):
        """
        Initialize the solidsection object.
        Input:
            elset:
                -str- element set name
            material:
                -str- material set name
        """
        self.params = dict(elset=elset, material=material)

        if 'abaqus_input' in kwargs.keys():
            parent = kwargs['abaqus_input']['parent']
            idkey = kwargs['abaqus_input']['idkey']
            parsed = kwargs['abaqus_input']['parsed']
            self.load_inp(parent, parsed, idkey)

    def load_inp(self, parent, parsed, idkey):
        """
        Initialize the object, add element set data and parameters.
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
        """
        self._parent = parent
        self._idkey = idkey
        for par in parsed[idkey].params:
            self.params[par.name.lower()] = par.value

    def dump2inp(self):
        '''
        Dumps solid section instance to Abaqus INP format.

        :rtype: string

        out = self.solidsection[i].dump2inp()

        '''

        out = '*SOLID SECTION, ELSET={0}, MATERIAL={1}'.format(self.params['elset'], self.params['material']) + '\n'

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
        return '<Fempy.Solidsection Class ' + str(print_dict) + '>'