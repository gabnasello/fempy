#from __builtin__ import int
import re
#from fempy.keywords import *
import itertools
import fempy.keywords as kw
import fempy.fempy_tools as femtools

class Fempy():

    """ Class that converts a parsed .inp file to a readable python object"""

    def __init__(self, inpfilename = ''):
        """
        Initialize the Fempy object.
        Input:
            inpfilename:
                -str- Name of the Abaqus file being parsed
        Return:
            -Fempy object-
        """
        keywords = ['heading',
                    'part',
                    'node',
                    'element',
                    'surface',
                    'nset',
                    'elset',
                    'solidsection',
                    'assembly',
                    'material',
                    ]
        self._keywords = keywords

        if inpfilename != '':
            storeinpdata(self, inpfilename)

    def dump2inp(self, writefile = True, filename = ''):
        """
        dump inp2fempy object to an inp file
        """
        out = ''
        for k in self._keywords:
            try:
                out += getattr(self, k).dump2inp()
                # if self.k is a fempy.keywords object
            except AttributeError:
                # error because the k attribute is a list
                try:
                    for obj in getattr(self, k):
                        out += obj.dump2inp()
                except:
                    pass
            except:
                pass

        if writefile:
            import os
            if filename == '':
                filename = os.path.splitext(self._filename)[0]

            with open(filename + '.inp', 'w') as f:
                f.write(out)
            print('---- ' + filename + '.inp file successfully written! ----')
        else:
            return out

    def dump2vtk(self, writefile = True, filename = ''):
        """
        dump inp2fempy object to a vtk file
        """
        out = ''
        # dump nodes and elements of the the inp2py object, if they exist
        try:
            out_node = self.node.dump2vtk()
            out_element = self.element.dump2vtk()
            out += '<VTKFile type="UnstructuredGrid" version="1.0" byte_order="LittleEndian" header_type="UInt64">\n'
            out += '\n<UnstructuredGrid>\n'
            # Writing instance geometries in final .vtk file
            nnodes = self.node.data.shape[0]
            nelems = self.element.data.shape[0]
            out += '\n<Piece NumberOfPoints = "' + str(nnodes) + '" NumberOfCells = "' + str(nelems) + '">\n'

            out += out_node
            out += out_element

            out += '\n</Piece>\n</UnstructuredGrid>\n</VTKFile>'

            if writefile:
                import os
                if filename == '':
                    filename = os.path.splitext(self._filename)[0]

                with open(filename + '.vtu', 'w') as f:
                    f.write(out)

                print('\n ----- ' + filename + '.vtu EXPORTED -----\n')
        except AttributeError:
            pass

        try:
            out = list(out)
            i = 1
            for p in self.part:
                out.append(p.dump2vtk(writefile=writefile, partID = i))
                i +=1
        except TypeError:
            if out == '':
                out += self.part.dump2vtk(writefile=writefile)
            else:
                out = list(out)
                out.append(self.part.dump2vtk(writefile=writefile))
        except AttributeError:
            pass

        if not writefile:
            return out

    def get_material_per_element(self):
        """ Get Dataframe with material properties per each element"""
        from pandas import DataFrame, Series
        section_df = DataFrame()
        elset_df = DataFrame()

        # collect all sections and element sets in fempy object
        parents = []

        try:
            if hasattr(self, 'solidsection'):
                parents.append(self)
            # if self.solidsection exist
        except AttributeError:
            # self.solidsection does not exist
            pass

        try:
            parents.append(self.part)
            # if self.part exist
        except AttributeError:
            # self.part does not exist
            pass

        for parent in parents:
            # dump all solid sections in a dataframe
            for sect in parent.solidsection:
                section_df = section_df.append(sect.params, ignore_index=True)

            # dump all element sets in a dataframe
            for els in parent.elset:
                dict = els.params
                dict['list'] = els.get_element_list()
                elset_df = elset_df.append(dict, ignore_index=True)
        section_df.index.name = 'section'

        # dump all material sets and properties in a dataframe
        material_df = DataFrame()
        for mat in self.material:
            d = mat.params
            for key in mat._keywords:
                try:
                    if key == 'elastic':
                        d['young'] = mat.__dict__[key].data[0]
                        d['poisson'] = mat.__dict__[key].data[1]
                    else:
                        d[key] = mat.__dict__[key].data
                except:
                    pass
            material_df = material_df.append(d, ignore_index=True)

        material_df.index.name = 'material'

        merged_df = section_df.merge(material_df, left_on='material', right_on='name') \
            .drop(['name'], axis=1)

        merged_df = merged_df.merge(elset_df, on='elset')

        vars = list(merged_df.drop(['list'], axis=1).columns)

        element_material_df = merged_df.list.apply(Series) \
            .merge(merged_df, left_index=True, right_index=True) \
            .drop(['list'], axis=1) \
            .melt(id_vars=vars, value_name='element') \
            .drop('variable', axis=1) \
            .dropna(subset=['element']) \
            .astype({'element': 'int'}) \
            .sort_values('element') \
            .reset_index() \
            .drop('index', axis=1)

        # reordering 'element' column
        cols = list(element_material_df.columns)
        cols = [cols[-1]] + cols[0:-1]
        element_material_df = element_material_df[cols]

        return element_material_df

    def assign_elastic_material_to_elements(self, fempy_element, young, poisson, bin_width):
        import pandas as pd
        import numpy as np

        """
        fempy_element - Fempy Element object within the Fempy object. 
        Material properties will be assigned to those elements
        """

        bins = np.arange(start=young.min(), stop=young.max(), step=bin_width)
        labels = np.arange(bins.size) + 1
        bins = np.append(bins, young.max())

        var_material = 'young'
        var_poisson = 'poisson'
        data = {var_material: young,
                var_poisson: poisson}
        df = pd.DataFrame(data)
        df.index = fempy_element.data.index
        df = df.sort_values(var_material)

        var_set = 'mat_set'
        df[var_set] = pd.cut(df[var_material], bins=bins, labels=labels, include_lowest=True)
        unique_sets = df[var_set].unique()
        labels = np.arange(unique_sets.__len__())

        # remove lebels without elements by renaming material sets
        d = dict(zip(unique_sets, labels))
        df[var_set] = [d.get(e, e) for e in df[var_set]]

        suffix = '_assigned'
        df = df.join(df.groupby(var_set).mean(), on=var_set, rsuffix=suffix)

        elem_parent = fempy_element._parent
        grouped = df.groupby(var_set)
        for group_name, df_group in grouped:
            elsetname = 'Bone_set_' + str(group_name)
            matsetname = 'Bone_mat_' + str(group_name)

            sect = kw.Solidsection(elset=elsetname, material=matsetname)
            elem_parent.assign_solidsection(solid_obj=sect)

            els = kw.Elset(elset_data = df_group.index.sort_values().to_list(),elset_name = elsetname)
            elem_parent.assign_elset(elset_obj = els)

            y = df_group[var_material + suffix].unique()[0]
            p = df_group[var_poisson + suffix].unique()[0]
            elast = kw.Elastic(elastic_data=[y, p])
            d = {'elastic': elast}
            material = kw.Material(mat_data=d,mat_name=matsetname)
            self.assign_material(fempy_obj = material)

    def assign_solidsection(self, elset = '', material = '', solid_obj = []):
        """
        fempy.Solidsection object will be stored as attribute of self
        solid_obj is the previously defined fempy.Solidsection object to assign
        """
        femtools.assign.assign_solidsection(parent_obj = self, elset=elset, material=material, solid_obj=solid_obj)

    def assign_elset(self, elset_data = [], elset_name = '', elset_obj = []):
        """
        fempy.Elset object will be stored as attribute of self
        elset_obj is the previously defined fempy.Elset object to assign
        """
        femtools.assign.assign_elset(parent_obj=self, elset_data=elset_data,
                                     elset_name=elset_name, elset_obj=elset_obj)


    def assign_material(self, mat_data = [], fempy_obj = []):
        """
        fempy_obj is fempy object from the relative path (e.g. material)
        """
        attr = 'material'

        if fempy_obj == []:
            fempy_obj = kw.Material(mat_data)

        try:
            getattr(self, attr).append(fempy_obj)
            # if self.attribute is a list
        except AttributeError:
            try:
                self.__setattr__(attr, [getattr(self, attr)])
                getattr(self, attr).append(fempy_obj)
                # if self.attribute was a Fempy Material object and becomes a list
            except AttributeError:
                self.__setattr__(attr, fempy_obj)
                # if self.attribute did not exist

    def __repr__(self):
        print_dict = {}
        for k in self._keywords:
            try:
                print_dict[k] = type(getattr(self, k))
            except:
                pass
        return '<Fempy Class ' + str(print_dict) + '>'

def inp2fempy(filename):
    """
    Load inp file and store it as a Fempy object
    Input:
        filename:
            Name of the file being parsed
    Return:
        -Fempy object- each section of parsed the .inp file in a readable python object
    """

    fempy_obj = Fempy()

    storeinpdata(fempy_obj, filename)

    return fempy_obj

def storeinpdata(fempy_obj, filename):
    """
    This method recursively inspect the parsed inp file and process each element with its specific module.
    Store the .inp into a format that can be accessed by python
    Input:
        parsed:
            -list- with the elements of the .inp file parsed. Each element has a keyword, parameters, and data lines
    Return:
        .inp file elements stored into objects that can be accessed by python. Those objects are attributes of self.
    """

    master = fempy_obj

    fempy_obj._filename = filename
    parsed = abaparser(filename)
    fempy_obj._parsed = parsed

    keywords = fempy_obj._keywords
    classes = [k.capitalize() for k in keywords]
    switcher = dict(zip(keywords, classes))

    i = 0
    while i < len(parsed):

        k = parsed[i].keyword.lower()
        if k in keywords:
            class_name = k.capitalize()
            my_class = getattr(kw, class_name)
            d = {'parent': fempy_obj,
                 'parsed': parsed,
                 'idkey': i,
                 'master': master}
            instancekey = my_class(parent=fempy_obj, parsed=parsed,
                                   idkey=i, master=master, abaqus_input=d)

            try:
                getattr(fempy_obj, k).append(instancekey)
                # skip keywords internally executed in the module called above (e.g. all keywords called within the
                # *Part and the *End Part keywords by the "part.py" module)
                i = getattr(fempy_obj, k)[-1]._return_id()
            except AttributeError:
                try:
                    fempy_obj.__setattr__(k, [getattr(fempy_obj, k)])
                    getattr(fempy_obj, k).append(instancekey)
                    i = getattr(fempy_obj, k)[-1]._return_id()
                except AttributeError:
                    fempy_obj.__setattr__(k, instancekey)
                    i = getattr(fempy_obj, k)._return_id()

        i = i + 1

def abaparser(filename):
    """
    
    """
    with open(filename, 'r') as f:
        fileread = f.read()

    fileread += "\n"
    fileread = fileread.replace("\r", "")
    fileread = fileread.replace("\n\n", "\n")
    fileread = fileread.replace("\t", "")
    fileread = fileread.replace(" ", "")
    fileread = fileread.replace("\n,\n", "\n")

    # delete all lines starting with '**'
    out = re.sub(r'(?m)^\*\*.*\n?', '', fileread)

    # split the text based on the keywords
    splitted = out.split('*')[1:]

    parsed = []
    for item in splitted:
        parsed.append(ParseAbaqus(item))
    
    return parsed

class ParseAbaqus():

    """ Class that parses out the keywords, parameters, and data lines from .inp file. """

    def __init__(self, singlekey):
        """
        Input:
        Return:
        """
        #keys_parameters = ('name', 'value')

        key = singlekey.split('\n')
        keyhead = key[0].split(',',1)
        self.keyword = keyhead[0]

        try:
            par = re.findall("[\w.]+", keyhead[1])
            parname = par[::2]
            parvalue = par[1::2]
            parameters = tuple(list(itertools.zip_longest(parname, parvalue, fillvalue='')))
            self.params = [ParseAbaqusParameters(p) for p in parameters]
        except:
            self.params = []
            pass
        
        # filter removes empty list items
        self.data = list(filter(None, key[1:]))
    
    def __repr__(self):
        return str({'keyword': self.keyword ,
                    'params': self.params ,
                    'data': self.data})


class ParseAbaqusParameters():
    """
    """
    def __init__(self, param):
        """
        Input:
        Return:
        """
        self.name = param[0]
        self.value = param[1]

    def __repr__(self):
        return str({'name': self.name ,
                    'value': self.value })