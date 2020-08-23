import fempy.keywords as kw

def assign_solidsection(parent_obj, elset='', material='', solid_obj=[]):
    """
    fempy.Solidsection object will be stored as attribute of the parent object (parent_obj, a fempy or a fempy.Part object)
    solid_obj is the previously defined fempy.Solidsection object to assign
    """
    attr = 'solidsection'

    if solid_obj == []:
        solid_obj = kw.Solidsection(elset=elset, material=material)

    try:
        getattr(parent_obj, attr).append(solid_obj)
        # if parent_obj.attribute is a list
    except AttributeError:
        try:
            parent_obj.__setattr__(attr, [getattr(parent_obj, attr)])
            getattr(parent_obj, attr).append(solid_obj)
            # if parent_obj.attribute was a fempy.Solidection object and becomes a list
        except AttributeError:
            parent_obj.__setattr__(attr, solid_obj)
            # if parent_obj.attribute did not exist


def assign_elset(parent_obj, elset_data=[], elset_name='', elset_obj=[]):
    """
    fempy.Elset object will be stored as attribute of the parent object (parent_obj, a fempy or a fempy.Part object)
    elset_obj is the previously defined fempy.Elset object to assign
    """
    attr = 'elset'

    if elset_obj == []:
        elset_obj = kw.Elset(elset_data=elset_data, elset_name=elset_name)

    try:
        getattr(parent_obj, attr).append(elset_obj)
        # if parent_obj.attribute is a list
    except AttributeError:
        try:
            parent_obj.__setattr__(attr, [getattr(parent_obj, attr)])
            getattr(parent_obj, attr).append(elset_obj)
            # if parent_obj.attribute was a fempy.ELset object and becomes a list
        except AttributeError:
            parent_obj.__setattr__(attr, elset_obj)
            # if parent_obj.attribute did not exist