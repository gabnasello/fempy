from fempy.keywords import density, elastic, Density, Elastic
import numpy as np


class Material():
    """ Class to store the *MATERIAL keyword from an Abaqus .inp file into a format that is accessible to python scripting.
    """

    def __init__(self, mat_data=[], mat_name='', **kwargs):
        """
        Initialize the material object and add keyword attributes to the Material object (e.g. density, elastic...).
        Input:
            mat_data:
                -dict-  whose keys are Material keywords (e.g. 'elastic', 'density')
                        and items are the respective fempy objects ('Elastic', 'Density', classes)
            mat_name:
                -str- material name
       """
        self._keywords = ['elastic',
                          'density',
                          ]

        self.params = dict(name=mat_name)

        if mat_data != []:
            self._store_material_data(mat_data)
        elif 'abaqus_input' in kwargs.keys():
            parent = kwargs['abaqus_input']['parent']
            idkey = kwargs['abaqus_input']['idkey']
            parsed = kwargs['abaqus_input']['parsed']
            self.load_inp(parent, parsed, idkey)

    def _store_material_data(self, mat_data):

        for k in mat_data.keys():
            if k in self._keywords:
                if mat_data[k].__class__.__name__ == k.capitalize():
                    self.__setattr__(k, mat_data[k])
                else:
                    raise TypeError('The item associate to "' + k +
                                    '" key is not a "' + k.capitalize() + '" object')
            else:
                raise TypeError('No module "' + k +
                                '" in "' + self.__class__.__name__ + '" keywords')

    def load_inp(self, parent, parsed, idkey):
        """
        Initialize the object and add keyword attributes to the Material object (e.g. density, elastic...).
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
        """

        self._parent = parent

        for par in parsed[idkey].params:
            self.params[par.name.lower()] = par.value

        i = idkey + 1
        while ((i < len(parsed)) and (parsed[i].keyword.lower() in self._keywords)):

            k = parsed[i].keyword.lower()

            parent_module_name = 'fempy.keywords.' + k
            parent_module = __import__(parent_module_name)
            keymodule = getattr(parent_module.keywords, k)
            class_name = k.capitalize()
            my_class = getattr(keymodule, class_name)
            d = {'parent': self,
                 'parsed': parsed,
                 'idkey': i,
                 }
            instancekey = my_class(abaqus_input=d)
            # instancekey = my_class(parent=self, parsed=parsed, idkey=i)

            try:
                getattr(self, k).append(instancekey)
            except AttributeError:
                try:
                    self.__setattr__(k, [getattr(self, k)])
                    getattr(self, k).append(instancekey)
                except AttributeError:
                    self.__setattr__(k, instancekey)

            i = i + 1

        # the *MATERIAL keyword differs from the *PART or the *ASSEMBLY keywords.
        # There's not *End Material keyword, thus the object should return a idkey lower than the one of the part
        # or the assembly objectes, where the respective *end keyword need to be skipped from reading
        self._idkey = i - 1

    def dump2inp(self):
        '''
        Returns parts in INP format suitable with abaqus input files.

        :rtype: string
        '''
        out = ''
        # out += '**----------------------------------\n** MATERIAL\n**----------------------------------\n'
        matname = self.params['name']
        pattern = '*MATERIAL, NAME={0}\n'
        out += pattern.format(matname)

        for key in self._keywords:
            try:
                data_str = np.array2string(getattr(self, key).data, separator=', ',
                                           formatter={'float_kind': lambda x: "%.6e" % x})
                out += '*' + key.upper() + '\n'
                out += ' ' + data_str.replace('[', '').replace(']', '') + '\n'
            except:
                pass
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
        for k in self._keywords:
            try:
                print_dict[k] = type(getattr(self, k))
            except:
                pass
        return '<Fempy.Material Class ' + str(print_dict) + '>'