#!/user/bin/env python
'''viewStructures.py

Simple wrapper functions that uses ipywidgets and py3Dmol to view a list of
protein structures.

Authorship information:
    __author__ = "Mars (Shih-Cheng) Huang"
    __maintainer__ = "Mars (Shih-Cheng) Huang"
    __email__ = "marshuang80@gmail.com"
    __version__ = "0.2.0"
    __status__ = "Done"
'''

from ipywidgets import interact, IntSlider
import py3Dmol

def simple_structure_viewer(pdbIds, style = 'cartoon', color = 'spectrum'):
    '''A wrapper function that simply displays a list of protein structures using
    ipywidgets and py3Dmol

    Attributes
    ----------
        pdbIds (list<Strings>) : A list of PDBIDs to display
        style : Style of 3D structure (stick line cross sphere cartoon VDW MS)
        color : Color of 3D structure
    '''

    if type(pdbIds) == str:
        pdbIds = [pdbIds]

    def view3d(i = 0):
        '''Simple structure viewer that uses py3Dmol to view PDB structure by
        indexing the list of PDBids

        Attributes
        ----------
            i (int): index of the protein if a list of PDBids
        '''

        print(f"PdbID: {pdbIds[i]}, Style: {style}")

        viewer = py3Dmol.view(query='pdb:'+pdbIds[i])
        viewer.setStyle({style: {'color': color}})

        return viewer.show()

    return interact(view3d, i=(0,len(pdbIds)-1))


def interaction_structure_viewer(pdbIds, interacting_atom = 'None', style = 'cartoon', color = 'spectrum'):
    '''A wrapper function that simply displays a list of protein structures using
    ipywidgets and py3Dmol and highlight specified interacting groups

    Attributes
    ----------
        pdbIds (list<Strings>) : A list of PDBIDs to display
        interacting_atom (String) : The interacting atom to highlight
        style : Style of 3D structure (stick line cross sphere cartoon VDW MS)
        color : Color of 3D structure
    '''

    if type(pdbIds) == str:
        pdbIds = [pdbIds]

    def view3d(i = 0):
        '''Simple structure viewer that uses py3Dmol to view PDB structure by
        indexing the list of PDBids

        Attributes
        ----------
            i (int): index of the protein if a list of PDBids
        '''

        print(f"PdbID: {pdbIds[i]}, Interactions: {interacting_atom}, Style: {style}")

        viewer = py3Dmol.view(query='pdb:'+pdbIds[i])
        viewer.setStyle({style: {'color': color}})

        if interacting_atom != "None":

            viewer.setStyle({'atom': interacting_atom},{'sphere': {'color':'gray'}})

        return viewer.animate()

    return interact(view3d, i = (0,len(pdbIds)-1))



def group_neighbor_viewer(pdbIds = None, groups = None, chains = None, distance = 3.0):
    '''A wrapper function that zooms in to a group of a protein structure and highlight
    its neighbors within a certain distance.

    Attributes
    ----------
        pdbIds (list<Strings>, String) : A list of PDBIDs to display
        groups (list<int>) : A list of groups to center at for each protein structure
        chains (list<char>) : A list of chains specified for each protein structure.
                              If no chains is specified, chain 'A' will be default to
                              all structures.
        cutoffDistance (float) : The cutoff distance use the find the neighbors
                                 of specified group
    '''

    if pdbIds == None or groups == None:
        raise ValueError("PdbIds and groups need to be specified")

    if len(pdbIds) != len(groups):
        raise ValueError("Number of structures should match with number of groups")

    if type(pdbIds) == str and groups == str:
        pdbIds, groups = [pdbIds], [groups]

    if chains == None:
        chains = ['A'] * len(pdbIds)

    def view3d(i = 0):
        '''Simple structure viewer that zooms into a specified group and highlight
        its neighbors

        Attributes
        ----------
            i (int): index of the protein if a list of PDBids
        '''

        print(f"PDB: {pdbIds[i]}, group: {groups[i]}, chain: {chains[i]}, cutoffDistance: {distance}")

        center = {'resi':groups[i],'chain':chains[i]}
        neighbors = {'resi':groups[i],'chain':chains[i],'byres':'true','expand': distance}

        viewer = py3Dmol.view(query='pdb:'+pdbIds[i])
        viewer.zoomTo(center)
        viewer.setStyle(neighbors,{'stick':{}});
        viewer.setStyle(center,{'sphere':{'color':'red'}})
        viewer.zoom(0.2, 1000);

        return viewer.show()

    return interact(view3d, i = (0,len(pdbIds)-1))


def group_interaction_viewer(df):
    '''A wrapper function that zooms in to a group in a protein structure and
    highlight its interacting atoms. The input dataframe should be generated
    from the GroupInteractionExtractor class.

    References
    ----------
        GroupInteractionExtractor:
        https://github.com/sbl-sdsc/mmtf-pyspark/blob/master/mmtfPyspark/interactions/groupInteractionExtractor.py

    Attributes
    ----------
        df (dataframe): the dataframe generated from GroupIneteractionExtractor
    '''

    structures = df['pdbId'].iloc
    groups = df['groupNum0'].iloc
    chains = df['chain0'].iloc
    elements = df['element0'].iloc

    def get_neighbors_chain(i):
        return [df[f'chain{j}'].iloc[i] for j in range(1,7) if df[f'element{j}'] is not None]

    def get_neighbors_group(i):
        return [df[f'groupNum{j}'].iloc[i] for j in range(1,7) if df[f'element{j}'] is not None]

    def get_neighbors_elements(i):
        elements = [df[f'element{j}'].iloc[i] for j in range(1,7) if df[f'element{j}'] is not None]
        return [str(e).upper() for e in elements]

    def view3d(i = 0):
        '''Simple structure viewer that uses py3Dmol to view PDB structure by
        indexing the list of PDBids
        Attributes
        ----------
        i (int): index of the protein if a list of PDBids
        '''

        print("PDBId: " + structures[i] + " chain: " + chains[i] + " element: " + elements[i])
        viewer = py3Dmol.view(query='pdb:'+structures[i],width=700,height=700)

        neighbors = {'resi':get_neighbors_group(i), 'chain':get_neighbors_chain(i)}
        metal = {'resi':groups[i], 'atom':str(elements[i]).upper(), 'chain':chains[i]}

        viewer.setStyle(neighbors,{'stick':{'colorscheme':'orangeCarbon'}})
        viewer.setStyle(metal,{'sphere':{'radius':0.5,'color':'gray'}})

        viewer.zoomTo(neighbors)
        return viewer.show();

    s_widget = IntSlider(min=0,max=df.shape[0]-1,description='Structure',continuous_update=False)

    return interact(view3d, i=s_widget);
