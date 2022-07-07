import time
import numpy as np
import pandas as pd
import sys
import json
import fim_nwm

class bmi_inland_fim():
    def __init__(self):
        super(bmi_inland_fim, self).__init__()
        self._values = {}
        self._var_loc = "node"
        self._var_grid_id = 0
        self._start_time = 0.0
        self._end_time = np.finfo("d").max
        self._att_map = {
            'model_name':         'Inland FIM HAND-SRC',
            'version':            '1.0',
            'author_name':        'NWC-modified by Ankit Ghanghas',
            'grid_type':          'scalar',
            'time_units':         '1 hour' }
        self._input_var_names = [
            'rem','catchments','catchment_poly','hydro_table','forecast',
            'inundation_raster','depth_raster','huc_6_id']
        self._output_var_names = ['None : check your output folder for inundationa and depth raster']
        self._var_name_units_map = {
                                'raster_resolution':['10 m','m'],
                                'depth_units':['meters','m'] }
        
    def initialize(self,cfg_file=None,current_time_step=0):
        # this is the bmi configuration file
        self.cfg_file = cfg_file

        self.current_time_step=current_time_step
        
        # ----- Create some lookup tabels from the long variable names --------#
        self._var_name_map_long_first = {long_name:self._var_name_units_map[long_name][0] for long_name in self._var_name_units_map.keys()}
        
        self._var_name_map_short_first = {self._var_name_units_map[long_name][0]:long_name for long_name in self._var_name_units_map.keys()}
        
        self._var_units_map = {long_name:self._var_name_units_map[long_name][1] for long_name in self._var_name_units_map.keys()}
        
        # -------------- Initalize all the variables --------------------------# 
        # -------------- so that they'll be picked up with the get functions --#
        for long_var_name in list(self._var_name_units_map.keys()):
            # ---------- All the variables are single values ------------------#
            # ---------- so just set to zero for now.        ------------------#
            self._values[long_var_name] = 0
            setattr( self, self.get_var_name(long_var_name), 0 )
            
        ##############################################################

        self.config_from_json()
    
    def update(self):
        fim_nwm.inundate(rem=self.rem, catchments=self.catchments, catchment_poly=self.catchment_poly, 
                         hydro_table=self.hydro_table, forecast=self.forecast,
                         mask_type=self.mask_type,huc_6_id=self.huc_6_id, hucs = None, hucs_layerName = None,
                         subset_hucs = None, num_workers = 1, aggregate = False, 
                         inundation_raster = self.inundation_raster, inundation_polygon = None,
                         depths = self.depth_raster, out_raster_profile = None, out_vector_profile = None,
                         src_table = None, quiet = False)
    
    def update_until(self, until):
        raise NotImplementedError("Use update [provide a list of forecasts, yet to add this function]")

        
    def config_from_json(self):  # the config file contains all the required rasters, catchments, forecast, SRC (hydrotable)
        with open(self.cfg_file) as data_file:
            data_loaded = json.load(data_file)    
            
        self.rem              =  data_loaded['rem']
        self.catchments       =  data_loaded['catchments']
        self.catchment_poly   =  data_loaded['catchment_poly']
        self.hydro_table      =  data_loaded['hydro_table']
        self.forecast         =  data_loaded['forecast']
        self.inundation_raster=  data_loaded['inundation_raster']
        self.depth_raster     =  data_loaded['depth_raster']
        self.huc_6_id         =  data_loaded['huc_6_id']
        self.mask_type        =  data_loaded['mask_type']
        return        
        
    
    def get_attribute(self, att_name):
    
        try:
            return self._att_map[ att_name.lower() ]
        except:
            print(' ERROR: Could not find attribute: ' + att_name)

    #--------------------------------------------------------
    # Note: These are currently variables needed from other
    #       components vs. those read from files or GUI.
    #--------------------------------------------------------   
    def get_input_var_names(self):

        return self._input_var_names

    def get_output_var_names(self):
 
        return self._output_var_names

    #------------------------------------------------------------ 
    def get_component_name(self):
        """Name of the component."""
        return self.get_attribute( 'model_name' ) #JG Edit

    #------------------------------------------------------------ 
    def get_input_item_count(self):
        """Get names of input variables."""
        return len(self._input_var_names)

    #------------------------------------------------------------ 
    def get_output_item_count(self):
        """Get names of output variables."""
        return len(self._output_var_names)

    #------------------------------------------------------------ 
    def get_value(self, var_name):
        """Copy of values.
        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.
        dest : ndarray
            A numpy array into which to place the values.
        Returns
        -------
        array_like
            Copy of values.
        """
        return self.get_value_ptr(var_name)

    #-------------------------------------------------------------------
    def get_value_ptr(self, var_name):
        """Reference to values.
        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.
        Returns
        -------
        array_like
            Value array.
        """
        return self._values[var_name]

    #-------------------------------------------------------------------
    #-------------------------------------------------------------------
    # BMI: Variable Information Functions
    #-------------------------------------------------------------------
    #-------------------------------------------------------------------
    def get_var_name(self, long_var_name):
                              
        return self._var_name_map_long_first[ long_var_name ]

    #-------------------------------------------------------------------
    def get_var_units(self, long_var_name):

        return self._var_units_map[ long_var_name ]
                                                             
    #-------------------------------------------------------------------
    def get_var_type(self, long_var_name):
        """Data type of variable.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        str
            Data type.
        """
        # JG Edit
        return self.get_value_ptr(long_var_name)  #.dtype
    
    #------------------------------------------------------------ 
    def get_var_grid(self, name):
        
        # JG Edit
        # all vars have grid 0 but check if its in names list first
        if name in (self._output_var_names + self._input_var_names):
            return self._var_grid_id  

    #------------------------------------------------------------ 
    def get_var_itemsize(self, name):
#        return np.dtype(self.get_var_type(name)).itemsize
        return np.array(self.get_value(name)).itemsize

    #------------------------------------------------------------ 
    def get_var_location(self, name):
        
        # JG Edit
        # all vars have location node but check if its in names list first
        if name in (self._output_var_names + self._input_var_names):
            return self._var_loc

    #-------------------------------------------------------------------
    # JG Note: what is this used for?
    def get_var_rank(self, long_var_name):

        return np.int16(0)

    #-------------------------------------------------------------------
    def get_start_time( self ):
    
        return self._start_time #JG Edit

    #-------------------------------------------------------------------
    def get_end_time( self ):

        return self._end_time #JG Edit


    #-------------------------------------------------------------------
    def get_current_time( self ):

        return self.current_time

    #-------------------------------------------------------------------
    def get_time_step( self ):

        return self.get_attribute( 'time_step_size' ) #JG: Edit

    #-------------------------------------------------------------------
    def get_time_units( self ):

        return self.get_attribute( 'time_units' ) 
       
    #------------------------------------------------------------ 
    def get_grid_edge_count(self, grid):
        raise NotImplementedError("get_grid_edge_count")

    #------------------------------------------------------------ 
    def get_grid_edge_nodes(self, grid, edge_nodes):
        raise NotImplementedError("get_grid_edge_nodes")

    #------------------------------------------------------------ 
    def get_grid_face_count(self, grid):
        raise NotImplementedError("get_grid_face_count")
    
    #------------------------------------------------------------ 
    def get_grid_face_edges(self, grid, face_edges):
        raise NotImplementedError("get_grid_face_edges")

    #------------------------------------------------------------ 
    def get_grid_face_nodes(self, grid, face_nodes):
        raise NotImplementedError("get_grid_face_nodes")
    
    #------------------------------------------------------------ 
    def get_grid_node_count(self, grid):
        raise NotImplementedError("get_grid_node_count")

    #------------------------------------------------------------ 
    def get_grid_nodes_per_face(self, grid, nodes_per_face):
        raise NotImplementedError("get_grid_nodes_per_face") 
    
    #------------------------------------------------------------ 
    def get_grid_origin(self, grid_id, origin):
        raise NotImplementedError("get_grid_origin") 

    #------------------------------------------------------------ 
    def get_grid_rank(self, grid_id):
 
        # JG Edit
        # 0 is the only id we have
        if grid_id == 0: 
            return 1

    #------------------------------------------------------------ 
    def get_grid_shape(self, grid_id, shape):
        raise NotImplementedError("get_grid_shape") 

    #------------------------------------------------------------ 
    def get_grid_size(self, grid_id):
       
        # JG Edit
        # 0 is the only id we have
        if grid_id == 0:
            return 1

    #------------------------------------------------------------ 
    def get_grid_spacing(self, grid_id, spacing):
        raise NotImplementedError("get_grid_spacing") 

    #------------------------------------------------------------ 
    def get_grid_type(self, grid_id=0):

        # JG Edit
        # 0 is the only id we have        
        if grid_id == 0:
            return 'scalar'

    #------------------------------------------------------------ 
    def get_grid_x(self):
        raise NotImplementedError("get_grid_x") 

    #------------------------------------------------------------ 
    def get_grid_y(self):
        raise NotImplementedError("get_grid_y") 

    #------------------------------------------------------------ 
    def get_grid_z(self):
        raise NotImplementedError("get_grid_z") 

