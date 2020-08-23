from fempy.keywords import node, element, surface, nset, elset, solidsection
from fempy.fempy_tools.assign import assign_solidsection, assign_elset

class Part():
    """ Class to store the PART keyword from an Abaqus .inp file into a format that is accessible to python scripting.
    """

    def __init__(self, parent, parsed, idkey, master, **kwargs):
        """
        Initialize the object and add keyword attributes to the part (e.g. nodes, elements, sections, elsets, nsets...).
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
            master:
                inp file object (Inp2Py class)
        """

        self._parent = parent
        self._keywords = ['node',
                          'element',
                          'surface',
                          'nset',
                          'elset',
                          'solidsection']

        self.params = dict(NAME=[])

        try:
            for par in parsed[idkey].params:
                self.params[par.name.upper()] = par.value
        except:
            pass

        i = idkey + 1
        while ((parsed[i].keyword.upper() != 'ENDPART') & (i < len(parsed))):

            k = parsed[i].keyword.lower()
            if k in self._keywords:
                parent_module_name = 'fempy.keywords.' + k
                parent_module = __import__(parent_module_name)
                keymodule = getattr(parent_module.keywords, k)
                class_name = k.capitalize()
                my_class = getattr(keymodule, class_name)
                d = {'parent': self,
                     'parsed': parsed,
                     'idkey': i,
                     'master': master}
                instancekey = my_class(parent=self, parsed=parsed,
                                       idkey=i, master=master, abaqus_input=d)

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

        # out = '**----------------------------------\n** PARTS\n**----------------------------------\n'
        out = ''
        partname = self.params['NAME']
        out += '*PART'
        if partname != []:
            out += ', NAME={0}'.format(partname)
        out += '\n'
        for k in self._keywords:
            try:
                out += getattr(self, k).dump2inp()
                # if self.k is a fempy.keywords object
            except AttributeError:
                try:
                    # error because the k attribute is a list
                    for obj in getattr(self, k):
                        out += obj.dump2inp()
                except:
                    pass
            except:
                pass
        out += '*END PART'
        return out

    def dump2vtk(self, writefile=True, filename='', partID=1):
        """
        dump fempy part object to a vtk file
        """

        # dump nodes and elements of the the fempy part object, if they exist

        out_node = self.node.dump2vtk()
        out_element = self.element.dump2vtk()
        out = '<VTKFile type="UnstructuredGrid" version="1.0" byte_order="LittleEndian" header_type="UInt64">\n'
        out += '\n<UnstructuredGrid>\n'
        # Writing instance geometries in final .vtk file
        nnodes = self.node.data.shape[0]
        nelems = self.element.data.shape[0]
        out += '\n<Piece NumberOfPoints = "' + str(nnodes) + '" NumberOfCells = "' + str(nelems) + '">\n'

        out += out_node
        out += out_element

        out += '\n</Piece>\n</UnstructuredGrid>\n</VTKFile>'

        if writefile:
            if filename == '':
                filename = self.params['NAME']
                if filename == []:
                    filename = 'part_' + str(partID)

            with open(filename + '.vtu', 'w') as f:
                f.write(out)

            print('\n ----- ' + filename + '.vtu EXPORTED -----\n')

        if not writefile:
            return out

    def assign_solidsection(self, elset = '', material = '', solid_obj = []):
        """
        fempy.Solidsection object will be stored as attribute of self
        solid_obj is the previously defined fempy.Solidsection object to assign
        """
        assign_solidsection(parent_obj = self, elset=elset, material=material, solid_obj=solid_obj)

    def assign_elset(self, elset_data = [], elset_name = '', elset_obj = []):
        """
        fempy.Elset object will be stored as attribute of self
        elset_obj is the previously defined fempy.Elset object to assign
        """
        assign_elset(parent_obj=self, elset_data=elset_data,
                     elset_name=elset_name, elset_obj=elset_obj)

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
        return '<Fempy.Part Class ' + str(print_dict) + '>'