class Assembly():

    """ Class to store the *ASSEMBLY keyword from an Abaqus .inp file into a format that is accessible to python scripting.
    """

    def __init__(self, parent, parsed, idkey, master, **kwargs):
        """
        Initialize the object and add keyword attributes to the assembly (e.g. instances).
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
        """

        from fempy.keywords import instance

        self._parent = parent

        self._keywords = ['instance',
                         ]

        self.params = dict(NAME = [])

        try:
            for par in parsed[idkey].params:
                self.params[par.name.upper()] = par.value
        except:
            pass

        i = idkey + 1
        while ((parsed[i].keyword.upper() != 'ENDASSEMBLY') & (i < len(parsed))):
            
            k = parsed[i].keyword.lower()
            if k in self._keywords:
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

    def dump2inp(self):
        '''
        Returns parts in INP format suitable with abaqus input files.

        :rtype: string
        '''

        print('Assembly - dump2inp to write')
        return ''

    def _return_id(self):
        '''
        Returns position of the last element processed with this class in the parsed inp list.

        :rtype: string
        '''

        return self._idkey

    def __repr__(self):
        print_dict = {}
        print_dict['params'] = self.params
        for k in self._keywords:
            try:
                print_dict[k] = type(getattr(self, k))
            except:
                pass
        return '<FemPy.Assembly Class ' + str(print_dict) + '>'