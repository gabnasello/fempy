class Instance():

    """ Class to store the INSTANCE keyword from an Abaqus .inp file into a format that is accessible to python scripting.
    """

    def __init__(self, parent, parsed, idkey, master, **kwargs):
        """
        Initialize the object and add keyword attributes to the instance.
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
        """

        self._parent = parent
        self.params = dict(NAME = [])

        for par in parsed[idkey].params:
            self.params[par.name.upper()] = par.value

        # The *Assembly keyword between the *Instance and *End Instance keywords
        # that should be skipped in this loop because internally executed in the "instance.py" module
        i = idkey + 1
        while ((parsed[i].keyword.upper() != 'ENDINSTANCE') & (i < len(parsed))):

            k = parsed[i].keyword.lower()
            if k in parent.parent._keywords:
                parent_module_name = 'fempy.keywords.' + k
                parent_module = __import__(parent_module_name)
                keymodule = getattr(parent_module.keywords, k)
                class_name =  k.capitalize()
                my_class = getattr(keymodule, class_name)
                instancekey = my_class(parent = self, parsed = parsed, idkey = i, master = master)

                try:
                    getattr(self, k).append(instancekey)
                    # skip keywords internally executed in the module called above (e.g. all keywords called within the
                    # *Part and the *End Part keywords by the "part.py" module)
                    i = getattr(self, k)[-1]._return_id()
                except AttributeError:
                    try:
                        self.__setattr__(k, [getattr(self, k)])
                        getattr(self, k).append(instancekey)
                        i = getattr(self, k)[-1]._return_id()
                    except AttributeError:
                        self.__setattr__(k, instancekey)
                        i = getattr(self, k)._return_id()

            i = i + 1

        self._idkey = i

    def _return_id(self):
        '''
        Returns position of the last element processed with this class in the parsed inp list.

        :rtype: string
        '''

        return self._idkey

    def __repr__(self):
        print_dict = {}
        print_dict['params'] = self.params
        for k in self._parent._parent._keywords:
            try:
                print_dict[k] = type(getattr(self, k))
            except:
                pass
        return '<FemPy.Instance Class ' + str(print_dict) + '>'