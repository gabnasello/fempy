class Heading():

    """ Class to store the heading keyword from an Abaqus .inp file in a format that is accessible to python scripting. """

    def __init__(self, parent, idkey, **kwargs):
        """
        Initialize the object and create a *HEADING string.
        Input:
            idkey:
                position of the element processed with this class in the parsed inp list.
        """

        self._parent = parent
        self.data = '*HEADING\n'
        self._idkey = idkey

    def dump2inp(self):
        '''
        Returns materials in INP format suitable with abaqus input files.

        :rtype: string
        '''

        return self.data

    def _return_id(self):
        '''
        Returns position of the last element processed with this class in the parsed inp list.

        :rtype: string
        '''

        return self._idkey