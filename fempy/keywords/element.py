import numpy as np
from pandas import DataFrame

class Element():

    """ Class to store the element keyword from an Abaqus .inp file into a format that is accessible to python scripting.
    """

    def __init__(self, eldata = [], eltype = '', index_label = [], elset_name = '', **kwargs):
        """
        Initialize the object and add (eventually) element data.
        Input:
            eldata: numpy array
                element connectivity matrix ([p1,p2,p3... p_nth] node label)
            eltype: str, optional
                element type (e.g. Abaqus format)
            index_label: list, optional
                node index labels
            elset_name: str, optional
                element set name
        """
        self.data = []
        self.params = dict(TYPE = [], ELSET = [])

        if 'abaqus_input' in kwargs.keys():
            parent = kwargs['abaqus_input']['parent']
            master = kwargs['abaqus_input']['master']
            idkey = kwargs['abaqus_input']['idkey']
            parsed = kwargs['abaqus_input']['parsed']
            self.load_inp(parent, parsed, idkey, master)
        elif eldata != []:
            self._store_element_data(eldata, eltype = eltype, index_label = index_label, elset_name = elset_name)

    def _store_element_data(self, eldata, eltype = '', index_label = [], elset_name = ''):

        self.params = dict(TYPE=eltype, ELSET=elset_name)

        data = np.asarray(eldata)
        columns = range(1,data.shape[1]+1)
        if index_label == []:
            index_label = np.arange(data.shape[0]) + 1
        self.data = DataFrame(data=data,
                     index=index_label,
                     columns=columns).astype(int)
        self.data.index.name = 'Element'

    def load_inp(self, parent, parsed, idkey, master):
        """
        Load inp element data.
        Input:
            parsed:
                -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
            idkey:
                position of the element processed with this class in the parsed inp list.
            master:
                inp file object (Inp2Fempy class)
        """
        self._parent = parent
        self._master = master
        self._idkey = idkey
        self.params = dict(TYPE = [], ELSET = [])

        split_data = [n.split(',') for n in parsed[idkey].data]
        data = np.array(split_data)[:, 1:].astype(float)
        index = np.array(split_data)[:, 0].astype(int)

        self._store_element_data(eldata=data, index_label=index)

        for par in parsed[idkey].params:
            self.params[par.name.upper()] = par.value

    def dump2inp(self):
        '''
        Dumps Elements instance to Abaqus INP format.

        :rtype: string

        out = self.element[i].dump2inp()

        '''

        #out = '**----------------------------------\n** ELEMENTS\n**----------------------------------\n'
        out = ''
        elType = self.params['TYPE']
        elSet = self.params['ELSET']
        out +='*ELEMENT, TYPE={0}'.format(elType)
        if elSet != '':
            out += ', ELSET={0}'.format(elSet)
        out += '\n'

        out += self.data.to_csv(header=None, line_terminator='\n').replace(',',', ')

        return out

    def dump2vtk(self):
        '''
        Returns elements in VTK format.

        :rtype: string for vtk file
        '''
        import sys
        np.set_printoptions(threshold=sys.maxsize)

        element_vtk_cell_type = {
            # trusss
            "T2D2": 3,  # vtk_line
            "T2D2H": 3,
            "T2D3": 4,  # vtk_poly_line
            "T2D3H": 4,
            "T3D2": 3,
            "T3D2H": 3,
            "T3D3": 4,
            "T3D3H": 4,
            # beams
            "B21": 3,
            "B21H": 3,
            "B22": 4,
            "B22H": 4,
            "B31": 3,
            "B31H": 3,
            "B32": 4,
            "B32H": 4,
            "B33": 4,
            "B33H": 4,
            # surfaces
            "S4": 9,  # vtk_quad
            "S4R": 9,
            "S4RS": 9,
            "S4RSW": 9,
            "S4R5": 9,
            "S8R": 23,  # vtk_quadratic_quad
            "S8R5": 23,
            "STRI3": 5,  # vtk_triangle
            "S3": 5,
            "S3R": 5,
            "S3RS": 5,
            "CPE3": 5,
            "CPE3T": 5,
            # volumes
            "C3D8": 12,  # vtk_hexahedron
            "C3D8H": 12,
            "C3D8I": 12,
            "C3D8IH": 12,
            "C3D8R": 12,
            "C3D8RH": 12,
            "C3D20": 25,
            "C3D20H": 25,  # vtk_quadratic_hexahedron
            "C3D20R": 25,
            "C3D20RH": 25,
            "C3D4": 10,  # vtk_tetrahedron
            "C3D4T": 10,
            "C3D4H": 10,
            "C3D10": 24,  # vtk_quadratic_tetrahedron
            "C3D10H": 24,
            "C3D10I": 24,
            "C3D10M": 24,
            "C3D10MH": 24,
            "C3D6": 13,  # vtk_wedge
        }

        out = '\n<Cells>\n'

        out += '<DataArray type = "Int64" Name = "connectivity" format = "ascii">\n'

        data = self.data -1
        out += data.to_string(header = False, index=False)
        out += '</DataArray>\n'

        out += '<DataArray type="Int64" Name="offsets" format="ascii">\n'

        offset = np.arange(self.data.shape[1], self.data.shape[0]*self.data.shape[1]+1, self.data.shape[1])
        out_offset = np.array2string(offset, separator='\n').replace("[", "").replace("]", "").replace(" ","")
        out += out_offset
        out += '\n</DataArray>\n'

        out += '<DataArray type="UInt8" Name="types" format="ascii">\n'
        out_connect = (str(element_vtk_cell_type[self.params['TYPE']]) + '\n') * self.data.shape[0]
        out += out_connect
        out += '</DataArray>\n'

        out += '\n</Cells>\n'

        return out

    def _return_id(self):
        '''
        Returns position of the last element processed with this class in the parsed inp list.

        :rtype: string
        '''

        return self._idkey

    def assign_elastic_material_to_elements(self, young, poisson, bin_width):
        import pandas as pd
        from fempy.keywords import Elset, Solidsection, Material

        bins = np.arange(start=young.min(), stop=young.max(), step=bin_width)
        labels = np.arange(bins.size) + 1
        bins = np.append(bins, young.max())

        var_material = 'elastic'
        var_poisson = 'poisson'
        data = {var_material: young,
                var_poisson: poisson}
        df = pd.DataFrame(data)

        var_set = 'material_sets'
        df[var_set] = pd.cut(df[var_material], bins=bins, labels=labels, include_lowest=True)
        unique_sets = df[var_set].unique()
        labels = np.arange(unique_sets.__len__()) + 1

        # remove lebels without elements by renaming material sets
        d = dict(zip(unique_sets, labels))
        df[var_set] = [d.get(e, e) for e in df[var_set]]

        df = df.join(df.groupby(var_set).mean(), on=var_set, rsuffix='_assigned')
        master = self._master

    def __repr__(self):
        print_dict = {}
        print_dict['params'] = self.params
        print_dict['data'] = type(self.data)
        return '<FemPy.Element Class ' + str(print_dict) + '>'