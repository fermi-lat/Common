
CLOCK_FREQUENCY	 	  = 20000000.0
CLOCK_TIC		  = 1.0/CLOCK_FREQUENCY
CLOCK_TIC_MILLISECONDS    = CLOCK_TIC*1000.0
CLOCK_ROLLOVER		  = 2**25
NUM_TOWERS                = 16
NUM_TKR_LAYERS_PER_TOWER  = 36
NUM_GTRC_PER_LAYER        = 2
NUM_GTFE_PER_LAYER        = 24
NUM_TKR_LAYERS            = NUM_TKR_LAYERS_PER_TOWER*NUM_TOWERS
NUM_TKR_GTRC              = NUM_TKR_LAYERS*NUM_GTRC_PER_LAYER
NUM_CAL_LAYERS_PER_TOWER  = 8
NUM_CAL_LAYERS            = NUM_CAL_LAYERS_PER_TOWER*NUM_TOWERS
NUM_CAL_COLUMNS_PER_TOWER = 12
NUM_ACD_CABLES            = 12
NUM_ACD_VETOES            = 128
NUM_ACD_CHANNELS_PER_CABLE= 18

# FASTMON special variables
FASTMON_DUMP_ERRORS_TO_FILE = False
FASTMON_DIR_VAR_NAME        = 'FAST_MON_DIR'
XML_CONFIG_DIR_VAR_NAME     = 'XML_CONFIG_DIR'

# ROOT related variables.
ROOT_BASKET_SIZE          = 1000000 

PLUS_INFINITY = 1.e10
MINUS_INFINITY = -1.e10
NAN = float('nan')


# Add here useful independant functions
def LookupErrorCode(obj, code):
  """@param Lookup the symbolic name of an error code

  Unfortunately, the handle error methods pass the error code as an unsigned
  int rather than an enumeration type.  If we had the enumeration type, then
  this function would be implemented as returning the code.__name__ value.

  Instead, we look up all symbols in the supplied object and see check whether
  any of them have the same value as the supplied code.  If so, that symbol's
  name is returned.
  
  Ric Claus wrote this one.

  @param obj The object containing the error symbols of interest
  @param code The error code to look up
  @return The symbol string, if found, else the code value as a string  
  """
  for name in dir(obj):
    if name.startswith("ERR_"):
      value = eval("obj." + name)
      if value == code:
        return name
  # Added 4 spaces at the beginning because these are truncated when the function
  # is called to remove the expected "ERR_"
  return "    No name found for error code: " + str(code)

