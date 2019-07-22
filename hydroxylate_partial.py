#!/home/wkassem/bin/ovitos
import numpy as np
import ovito
from ovito.io import import_file, export_file
from ovito.modifiers import PythonScriptModifier, CreateBondsModifier, ConstructSurfaceModifier, SelectExpressionModifier, ExpandSelectionModifier
from ovito.data import *
from ovito.vis import BondsDisplay
import sys
import argparse

def ensure_no_collision(atm, atm_list):
    for i in range(atm_list.shape[0]):
        if position_radial(atm - atm_list[i,:]) < 0.5:
            print("possible collision between atoms at:")
            print(atm_list[i,:])
            return False
    return True

def identifier2index(ident, ident_array):
    for i in range(ident_array.size):
        if ident == ident_array[i]:
            return i
    return -1    


def position_radial(pos):
    return np.dot(pos[:2],pos[:2])**0.5



def create_bond_count_particle(frame, input, output):
    # Enumerate the created bonds
    bonds_enum = Bonds.Enumerator(output.bonds)

    # Create new particle property
    bond_count_property = output.create_user_particle_property("bond_count",data_type='int')
    total_count = output.number_of_particles
    
    # Loop over atoms.
    bonds_array = output.bonds.array
    for particle_index in range(total_count):
        # Loop over half-bonds of current atom.
        bond_count = 0
        for bond_index in bonds_enum.bonds_of_particle(particle_index):
            atomA = bonds_array[bond_index][0]
            atomB = bonds_array[bond_index][1]
            assert(atomA == particle_index)
            bond_count = bond_count + 1

        #print("Atom %i has %i bonds" % (particle_index, bond_count))
        bond_count_property.marray[particle_index] = bond_count
        yield (particle_index/total_count)

        
#### Load a particle:
##################################################################################
parser = argparse.ArgumentParser(description='Add hydroxyls groups to the surface of an amorphous silica nanosphere')
parser.add_argument('filename', metavar='FNAME',
                    help="The path or filename of the LAMMPS dump file")
parser.add_argument('coreCutoff', metavar="CORE_CUTOFF", type=float,
                    help="The radius in Angstroms at which the shell region starts")
parser.add_argument('outfname', metavar="OUTPUT",
                    help="The path or filename of the output DATA LAMMPS file")

parser.add_argument('--bondLength', metavar="bond_length", type=float,
                    help="The distance in Angstroms between Si and O atoms to form a bond. Default=1.8", default=1.8)

parser.add_argument('--OHconcentration', metavar="OH_Concentration", type=float, default=0.0,
                    help="The concentration of surafce OH in OH/nm^2")

parser.add_argument('--OHzlimit', metavar="OH_z_limit", type=float, default=np.inf,
                    help="The limit along Z at which to add OH")

args = parser.parse_args()
node = import_file(args.filename)
print("... loading %s"%(args.filename) )
print("... %d files"%(node.source.num_frames))
print("... cutoff for core region %d"%(args.coreCutoff))

partialOH = False
if args.OHzlimit < np.inf:
    print("... hydroxylating a portion of nanowire, upper/lower limits = %1.5f"%(args.OHzlimit))
    partialOH = True

#### Create a bonds modifier (mod) and apply it to the system
###################################################################################
rcut = args.bondLength
modbonds = CreateBondsModifier(mode = CreateBondsModifier.Mode.Pairwise)
modbonds.set_pairwise_cutoff("Type 1", "Type 2", rcut)
modmesh = ConstructSurfaceModifier(radius=5.0)

modbondcount = PythonScriptModifier(function = create_bond_count_particle)
selectsiunder = SelectExpressionModifier(expression = 'ParticleType==1 && bond_count<4')
selectoxunder = ExpandSelectionModifier(mode=ExpandSelectionModifier.ExpansionMode.Bonded)

print("... creating Si-O bonds using cutoff = %1.4f"%(rcut))
node.modifiers.append(modmesh)
node.modifiers.append(modbonds)
node.modifiers.append(modbondcount)
node.compute()

np_surface_area = node.output.attributes['ConstructSurfaceMesh.surface_area']/100.0
if partialOH:
    np_surface_area = (2.0 * args.OHzlimit / np.linalg.norm(node.source.cell.matrix[:,2])) * np_surface_area
    
np_volume = node.output.attributes['ConstructSurfaceMesh.solid_volume']/1000.0
print("... %d bonds created"%(node.output.number_of_full_bonds))
print("... surface area of hydroxylated portion = %1.4f nm^2"%(np_surface_area))
print("... volume of wire = %1.4f nm^3"%(np_volume))
#nselected = node.output.attributes['SelectExpression.num_selected']
#print("... %d selected atoms"%(nselected))

bonds_enum = Bonds.Enumerator(node.output.bonds)

# Loop over atoms.
bonds_array = node.output.bonds.array
bondc_array = node.output.particle_properties['bond_count'].marray
#select_array = node.output.particle_properties['Selection'].marray
pos_array = node.output.particle_properties['Position'].marray
identif_array = node.output.particle_properties['Particle Identifier'].marray
type_array = node.output.particle_properties['Particle Type'].marray
charge_array = node.output.particle_properties['Charge'].marray

total_count = type_array.size

selectedox = []
iselect = -1
undercoordsi = 0
for particle_index in range(total_count):
        # Loop over half-bonds of current atom.
        if (type_array[particle_index] == 1 and np.linalg.norm(pos_array[particle_index,:2]) > float(sys.argv[2]) and 
            bondc_array[particle_index] < 4 and abs(pos_array[particle_index,2]) < args.OHzlimit ):
            undercoordsi += 1
            r = 0
            selected = - 1
            
            for bond_index in bonds_enum.bonds_of_particle(particle_index):
                atomA = bonds_array[bond_index][0]
                atomB = bonds_array[bond_index][1]
                assert(atomA == particle_index)
                if type_array[atomA]==2:
                    tmp = pos_array[atomA]
                    atomC = atomA
                else:
                    tmp = pos_array[atomB]
                    atomC = atomB
                #tmp = pos_array[atomA] - pos_array[atomB] 
                tmp = position_radial(tmp)
                
                if tmp > r:
                    r = tmp
                    selected = atomC

            if selected > 0:
                selectedox.append(selected)

print("... %d under-coordinated Si atoms found"%(undercoordsi)) 
selectedox_unique = np.unique(selectedox)
num_H_particles = selectedox_unique.size
print("... %d selected (unique) oxygen atoms = "%(num_H_particles))
print(selectedox)
print("... old number of particles  %d"%(total_count))
print("... OH concentration = %1.5f OH/nm^2"%(num_H_particles/np_surface_area))

############################## Add more ################################################
if num_H_particles/np_surface_area < args.OHconcentration:
    extra_H_needed = int(np.ceil(args.OHconcentration * np_surface_area) - num_H_particles)
    print("   +++ %d extra H particles needed"%(extra_H_needed))
    candidateSi=[]
    candidateOx=[]
    for particle_index in range(total_count):
        # Loop over half-bonds of current atom.
        if (type_array[particle_index] == 1 and np.linalg.norm(pos_array[particle_index,:2]) > float(sys.argv[2]) and 
            bondc_array[particle_index] == 4 and abs(pos_array[particle_index,2]) < args.OHzlimit):
            candidateSi.append(particle_index)
            
    if (4 * len(candidateSi)) < extra_H_needed:
        print("ERROR: Cannot generate requested OH concentration, not enough O")
        print("        try reducing core cutoff changing bond length")
        raise SystemExit
    else:
        for particle_index in candidateSi:
            for bond_index in bonds_enum.bonds_of_particle(particle_index):
                atomA = bonds_array[bond_index][0]
                atomB = bonds_array[bond_index][1]
                assert(atomA == particle_index)
                if type_array[atomA]==2:
                    candidateOx.append(atomA)
                elif type_array[atomB]==2:
                    candidateOx.append(atomB)

    candidateOx = np.unique(candidateOx)
    np.random.shuffle(candidateOx)
    total_H_needed = num_H_particles + extra_H_needed

    istart = 0
    while extra_H_needed > 0:
        selectedox.extend(candidateOx[istart:extra_H_needed])
        istart = istart + extra_H_needed-1
        extra_H_needed = total_H_needed - len(selectedox)

    selectedox_unique = np.unique(selectedox)
    num_H_particles = selectedox_unique.size
    print("... %d selected (unique) oxygen atoms = "%(num_H_particles))
    print(selectedox)
    print("... old number of particles  %d"%(total_count))
    print("... OH concentration = %1.5f OH/nm^2"%(num_H_particles/np_surface_area))


# Ensure no collisions between atoms
print("\n... Ensuring no collisions between atoms")
selectedox_unique_nocollision = []

for iH in range(num_H_particles):
    particle_id = selectedox_unique[iH]
    r = pos_array[particle_id]
    tmp = 1.0 / np.linalg.norm(r)
    rp = (1+tmp)*r
    #rp = rp + np.random.uniform(-0.6,0.6,np.shape(rp))
    #if ensure_no_collision(rp, pos_array):
    selectedox_unique_nocollision.append(particle_id)

num_H_particles = len(selectedox_unique_nocollision)
print("... removed %d atoms"%(len(selectedox_unique) - len(selectedox_unique_nocollision)))
print("... final OH concentration = %1.5f OH/nm^2"%(num_H_particles/np_surface_area))

# The number of particles we are going to create.
num_particles = num_H_particles + total_count

# Create the particle position property.
new_pos_prop = ParticleProperty.create(ParticleProperty.Type.Position, num_particles)
new_type_prop = ParticleProperty.create(ParticleProperty.Type.ParticleType, num_particles)
new_identifier_prop = ParticleProperty.create(ParticleProperty.Type.Identifier, num_particles)
new_charge_prop = ParticleProperty.create(ParticleProperty.Type.Charge, num_particles)

new_type_prop.type_list.append(ParticleType(id = 1, name = 'Si', color = (1.0,0.0,0.0)))
new_type_prop.type_list.append(ParticleType(id = 2, name = 'O', color = (0.0,0.0,1.0)))
new_type_prop.type_list.append(ParticleType(id = 3, name = 'H', color = (0.0,1.0,0.0)))


for particle_index in range(total_count):
    new_identifier_prop.marray[particle_index] = identif_array[particle_index]
    new_charge_prop.marray[particle_index] = charge_array[particle_index]
    new_pos_prop.marray[particle_index,:] = pos_array[particle_index,:]
    new_type_prop.marray[particle_index] = type_array[particle_index]


for iH in range(num_H_particles):
    particle_id = selectedox_unique_nocollision[iH]
    r = pos_array[particle_id]
    tmp = 1.5 / np.linalg.norm(r)
    rp = (1+tmp)*r
    #rp = rp + np.random.uniform(-0.6,0.6,np.shape(rp))
    s = iH + total_count
    new_pos_prop.marray[s,:] = rp
    new_type_prop.marray[s] = 3
    new_identifier_prop.marray[s] = s + 1
    new_charge_prop.marray[s] = +1.0
    
new_data = DataCollection()
new_data.add(new_pos_prop)
new_data.add(new_identifier_prop)
new_data.add(new_type_prop)
new_data.add(new_charge_prop)
new_data.add(node.source.cell)
if "Timestep" in node.source.attributes:
    new_data.attributes['Timestep'] = node.source.attributes["Timestep"]

new_node = ovito.ObjectNode()
new_node.source = new_data
new_node.compute()
#new_node.add_to_scene()

print("... new number of particles  %d"%(new_node.output.particle_properties['Particle Type'].size))
print(new_node.output.particle_properties["Particle Type"].array)

export_file(new_node, sys.argv[3], "lammps_dump",
            columns=["Particle Identifier", "Particle Type", "Charge" ,"Position.X", "Position.Y", "Position.Z"])
print("... done writing LAMMPS data file %s"%(args.outfname))
