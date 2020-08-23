import fempy as fp

inpfile = 'fempy_example.inp'

inp = fp.inp2fempy(inpfile)

# Inspect the imported inp file
print(inp)

# Inspect one of the imported keywords
print(inp.part)

inp.dump2vtk()