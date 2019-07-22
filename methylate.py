#!/home/wkassem/bin/ovitos
import numpy as np
import ovito
from ovito.io import import_file, export_file
from ovito.modifiers import PythonScriptModifier, CreateBondsModifier, ConstructSurfaceModifier, SelectExpressionModifier, ExpandSelectionModifier
from ovito.data import *
from ovito.vis import BondsDisplay
import sys
import argparse

class atom:
    def __init__(self):
        self.pos = np.array([0.,0.,0.])
        self.type = 0
        self.id = 0
        self.q = 0
        self.nn = []

class atomCollection:
    def __init__(self, id_arr, type_arr, q_arr, pos_arr, nn_arr):
        self.id = id_arr
        self.type = typ_arr
        self.q = q_arr
        self.pos = pos_arr
        self.nn = nn_arr

    def add_atom(self, newId, newType, newQ, newPos):
        self.id = np.append(self.id, newId)
        self.type = np.append(self.type, newType)
        self.q = np.append(self.Q, newQ)
        self.pos = np.append(self.pos, newPos, axis=0)
        self.nn = np.append(self.nn, [], axis=0)

    def delete_atom_index(self, index):
        self.id = np.delete(self.id, index)
        self.type = np.delete(self.type, index)
        self.q = np.delete(self.q, index)
        self.pos = np.delete(self.pos, index,axis=0)
        self.nn = np.delete(self.nn, index, axis=0)

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


def create_tms_molecule_planar(r,n):

    typ = np.array([1,
                    4, 3, 3, 3,
                    4, 3, 3, 3,
                    4, 3, 3, 3])

    q = np.array([0]*13)
    
    zunit = np.array([0,0,1])
    zcrossn = np.cross(zunit,n)
    dSiC = 2.5
    dCH = 1.2

    # add C on top along zunit
    # rotate 120, add another C,
    # rotate 240, add another C
    posC = np.array( [r + zunit * dSiC,
                     r + dSiC * (zunit * -0.5 + zcrossn * 0.86602540378),
                      r + dSiC * (zunit * -0.5 + zcrossn * -0.86602540378)])


    pos = np.zeros((13,3))
    pos[0,:] = r #Si atom

    for i in range(3):
        j = 4 * i + 1
        pos[j,:] = posC[i,:] # C atom
        
        pos[j+1,:] = posC[i,:] + zunit * dCH   # add the H1 along zunit
        pos[j+2,:] = posC[i,:] + zcrossn * dCH # rotate 90, add H2
        pos[j+3,:] = posC[i,:] - zcrossn * dCH # rotate 180, add H3

    return (typ, q, pos)


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

def create_bond_neighbors_particle(frame, input, output):
    # Max neighbors per particle
    max_nghbrs = 10
    
    # Enumerate the created bonds
    bonds_enum = Bonds.Enumerator(output.bonds)

    # List of atom identifiers
    identt_arr = input.particle_properties['Particle Identifier'].marray

    # Create new particle property
    bond_nghbrs_property = output.create_user_particle_property("bond_neighbors",data_type='int',num_components=max_nghbrs )
    total_count = output.number_of_particles
    
    # Loop over atoms.
    bonds_array = output.bonds.array
    for particle_index in range(total_count):
        # Loop over half-bonds of current atom.
        bond_nghbrs = [-1]*max_nghbrs
        i_nghbr = 0
        
        for bond_index in bonds_enum.bonds_of_particle(particle_index):
            atomA = bonds_array[bond_index][0]
            atomB = bonds_array[bond_index][1]
            assert(atomA == particle_index)
            bond_nghbrs[i_nghbr] = identt_arr[atomB]
            i_nghbr = i_nghbr + 1

        bond_nghbrs_property.marray[particle_index] = bond_nghbrs
        yield (particle_index/total_count)

        
#### Load a particle:
##################################################################################
parser = argparse.ArgumentParser(description='Add TMS groups to the surface of an amorphous silica nanowire')
parser.add_argument('filename', metavar='FNAME',
                    help="The path or filename of the LAMMPS dump file")
parser.add_argument('coreCutoff', metavar="CORE_CUTOFF", type=float,
                    help="The radius in Angstroms at which the shell region starts")
parser.add_argument('outfname', metavar="OUTPUT",
                    help="The path or filename of the output DATA LAMMPS file")

parser.add_argument('--bondLength', metavar="bond_length", type=float,
                    help="The distance in Angstroms between Si and O atoms to form a bond. Default=1.8", default=1.8)

parser.add_argument('--concentration', metavar="TMS Concentration", type=float, default=0.0,
                    help="The concentration of surafce TMS in C3H9Si/nm^2")

args = parser.parse_args()
node = import_file(args.filename)
print("... loading %s"%(args.filename) )
print("... %d files"%(node.source.num_frames))
print("... cutoff for core region %d A"%(args.coreCutoff))



#### Create a bonds modifier (mod) and apply it to the system
###################################################################################
rcut = args.bondLength
modbonds = CreateBondsModifier(mode = CreateBondsModifier.Mode.Pairwise)
modbonds.set_pairwise_cutoff("Type 1", "Type 2", rcut)
modmesh = ConstructSurfaceModifier(radius=5.0)

modbondcount = PythonScriptModifier(function = create_bond_count_particle)
modbondnghbr = PythonScriptModifier(function = create_bond_neighbors_particle)

print("")
print("... adding modifiers")
print("      creating Si-O bonds using cutoff = %1.4f"%(rcut))
print("      calculating bond count")
print("      calculating nearest-neighbor bonded atoms")
node.modifiers.append(modmesh)
node.modifiers.append(modbonds)
node.modifiers.append(modbondcount)
node.modifiers.append(modbondnghbr)
node.compute()

np_surface_area = node.output.attributes['ConstructSurfaceMesh.surface_area']/100.0
np_volume = node.output.attributes['ConstructSurfaceMesh.solid_volume']/1000.0
print("")
print("... %d bonds created"%(node.output.number_of_full_bonds))
print("... surface area of particle = %1.4f nm^2"%(np_surface_area))
print("... volume of particle = %1.4f nm^3"%(np_volume))

bonds_enum = Bonds.Enumerator(node.output.bonds)

# Loop over atoms.
bondc_array = node.output.particle_properties['bond_count'].marray
bondn_array = node.output.particle_properties['bond_neighbors'].marray
pos_array = node.output.particle_properties['Position'].marray
identif_array = node.output.particle_properties['Particle Identifier'].marray
type_array = node.output.particle_properties['Particle Type'].marray
charge_array = node.output.particle_properties['Charge'].marray

# sort atoms based on their radial position
com = np.mean(pos_array[:,:2],axis=0)
radial_position = np.linalg.norm(pos_array[:,:2]-com,axis=1)
sortmat = np.argsort(radial_position)

print("")
print("... sorting atoms based on their radial position")

radial_position = radial_position[sortmat]
bondn_array = bondn_array[sortmat,:]
bondc_array = bondc_array[sortmat]
pos_array = pos_array[sortmat,:]
identif_array = identif_array[sortmat]
type_array = type_array[sortmat]
charge_array = charge_array[sortmat]
total_count = type_array.size

atom_index_shell = np.nonzero(radial_position > args.coreCutoff)
si_index_shell = np.nonzero( (radial_position > args.coreCutoff) & (type_array == 1) )
ox_index_shell = np.nonzero( (radial_position > args.coreCutoff) & (type_array == 2) & (radial_position < args.coreCutoff + 10) )
ox_index_shell = ox_index_shell[0]

print("    %d oxygen surface atoms found"%(ox_index_shell.size))
num_tms_mol   = ox_index_shell.size
tms_max_conc = num_tms_mol / np_surface_area

if tms_max_conc < args.concentration:
    print("ERROR: TARGET CONCENTRATION TOO HIGH, TRY A SMALLER CORE CUTOFF MAX = %3.4f TMS/nm^2"%(tms_max_conc))
    exit()
elif tms_max_conc > args.concentration:
    tms_needed = np.ceil(args.concentration * np_surface_area)
    ox_index_shell = ox_index_shell[-tms_needed:]
    print("... selecting outer most %d oxygen atoms for TMS addition"%(ox_index_shell.size))

num_tms_mol   = ox_index_shell.size
num_particles = identif_array.size + 13 * num_tms_mol

##### Create the new system.
print("")
print("... creating new TMS + silica system, %d old atoms, adding %d TMS molecules"%(identif_array.size, num_tms_mol))

new_pos_prop = ParticleProperty.create(ParticleProperty.Type.Position, num_particles)
new_type_prop = ParticleProperty.create(ParticleProperty.Type.ParticleType, num_particles)
new_identifier_prop = ParticleProperty.create(ParticleProperty.Type.Identifier, num_particles)
new_charge_prop = ParticleProperty.create(ParticleProperty.Type.Charge, num_particles)

new_type_prop.type_list.append(ParticleType(id = 1, name = 'Si', color = (1.0,0.0,0.0)))
new_type_prop.type_list.append(ParticleType(id = 2, name = 'O', color = (0.0,0.0,1.0)))
new_type_prop.type_list.append(ParticleType(id = 3, name = 'H', color = (0.0,1.0,0.0)))
new_type_prop.type_list.append(ParticleType(id = 4, name = 'C', color = (0.0,1.0,1.0)))

# Add old particles
print("     adding old silica atoms")
for particle_index in range(total_count):
    new_identifier_prop.marray[particle_index] = identif_array[particle_index]
    new_charge_prop.marray[particle_index] = charge_array[particle_index]
    new_pos_prop.marray[particle_index,:] = pos_array[particle_index,:]
    new_type_prop.marray[particle_index] = type_array[particle_index]

# Add new particles (molecules)
print("     adding new TMS molecules")
for iTMS in range(num_tms_mol):
    particle_id = ox_index_shell[iTMS]
    r = pos_array[particle_id]
    rho = np.array([r[0], r[1], 0])                           
    rhoNorm = np.linalg.norm(rho)
    rp = r + 1.5 * rho / rhoNorm
    #rp = rp + np.random.uniform(-0.6,0.6,np.shape(rp))

    newtyp, newq, newpos = create_tms_molecule_planar(rp, rho / rhoNorm)
    s = 13 * iTMS + identif_array.size
    for j in range(newtyp.size):
        new_pos_prop.marray[s,:] = newpos[j,:]
        new_type_prop.marray[s] = newtyp[j]
        new_identifier_prop.marray[s] = s + 1
        new_charge_prop.marray[s] = newq[j]
        s = s + 1

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
